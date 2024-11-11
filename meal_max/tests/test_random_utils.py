import pytest
import requests
from unittest.mock import patch, Mock
from meal_max.utils.random_utils import get_random
from meal_max.models.kitchen_model import get_random_meal
from meal_max.models.battle_model import BattleModel, Meal

# Constants for testing
RANDOM_NUMBER = 42
NUM_MEALS = 100
NUM_BATTLES = 50

# Mock for random.org response
@pytest.fixture
def mock_random_org(mocker):
    """Fixture to mock a successful response from random.org."""
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_NUMBER}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

# Tests for get_random function in random_utils for Kitchen and Battle models
def test_get_random(mock_random_org):
    """Test retrieving a random number from random.org."""
    result = get_random(NUM_MEALS)
    assert result == RANDOM_NUMBER, f"Expected random number {RANDOM_NUMBER}, but got {result}"
    requests.get.assert_called_once_with(
        f"https://www.random.org/integers/?num=1&min=1&max={NUM_MEALS}&col=1&base=10&format=plain&rnd=new",
        timeout=5
    )

def test_get_random_request_failure(mocker):
    """Test handling of a request failure from random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random(NUM_MEALS)

def test_get_random_timeout(mocker):
    """Test handling of a timeout from random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random(NUM_MEALS)

def test_get_random_invalid_response(mock_random_org):
    """Test handling of an invalid response (non-digit) from random.org."""
    mock_random_org.text = "invalid_response"
    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random(NUM_MEALS)

# Mocking models that depend on get_random
@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=15.0, difficulty="MED")

@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal="Meal 2", cuisine="Cuisine 2", price=12.0, difficulty="LOW")

@pytest.fixture
def battle_model():
    return BattleModel()

# Test Kitchen Model get_random_meal function
@patch("meal_max.utils.random_utils.get_random", return_value=RANDOM_NUMBER)
@patch("meal_max.models.kitchen_model.get_all_meals")
def test_get_random_meal(mock_get_all_meals, mock_get_random):
    """Test retrieving a random meal from the Kitchen model."""
    mock_get_all_meals.return_value = [
        {"id": 1, "meal": "Meal 1", "cuisine": "Cuisine 1", "price": 10.0, "difficulty": "MED"},
        {"id": 2, "meal": "Meal 2", "cuisine": "Cuisine 2", "price": 20.0, "difficulty": "LOW"},
        {"id": 3, "meal": "Meal 3", "cuisine": "Cuisine 3", "price": 15.0, "difficulty": "HIGH"},
    ]

    random_meal = get_random_meal()
    assert random_meal.meal in ["Meal 1", "Meal 2", "Meal 3"]
    mock_get_random.assert_called_once_with(3)

# Test Battle Model battle function with random selection
@patch("meal_max.utils.random_utils.get_random", return_value=0.5)
def test_battle_model_battle(battle_model, sample_meal1, sample_meal2, mock_get_random):
    """Test the battle functionality in the Battle model."""
    # Prepare the battle model with two meals
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    winner = battle_model.battle()
    assert winner in ["Meal 1", "Meal 2"], f"Unexpected winner {winner}"
    mock_get_random.assert_called_once()

@patch("meal_max.utils.random_utils.get_random", return_value=0.3)
def test_battle_model_winner_selection(battle_model, sample_meal1, sample_meal2, mock_get_random):
    """Test winner selection in the Battle model based on random threshold."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    score_1 = battle_model.get_battle_score(sample_meal1)
    score_2 = battle_model.get_battle_score(sample_meal2)
    delta = abs(score_1 - score_2) / 100

    winner = battle_model.battle()
    if delta > 0.3:
        assert winner == (sample_meal1.meal if score_1 > score_2 else sample_meal2.meal)
    else:
        assert winner == (sample_meal2.meal if score_2 > score_1 else sample_meal1.meal)
    mock_get_random.assert_called_once()