import pytest
from unittest.mock import patch, MagicMock
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats


@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_combatant_1():
    return Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=99, difficulty="MED")

@pytest.fixture
def sample_combatant_2():
    return Meal(id=2, meal="Meal 2", cuisine="Cuisine 2", price=80, difficulty="LOW")


##################################################
# Battle Preparation Tests
##################################################

def test_prep_combatant(battle_model, sample_combatant_1):
    """Test adding a combatant to the combatants list."""
    battle_model.prep_combatant(sample_combatant_1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Meal 1"

def test_prep_combatant_list_full(battle_model, sample_combatant_1, sample_combatant_2):
    """Test adding a third combatant raises an error."""
    battle_model.prep_combatant(sample_combatant_1)
    battle_model.prep_combatant(sample_combatant_2)

    new_combatant = Meal(id=3, meal="Meal 3", cuisine="Cuisine 3", price=70, difficulty="HIGH")
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(new_combatant)


##################################################
# Combatants List Management Tests
##################################################

def test_clear_combatants(battle_model, sample_combatant_1, sample_combatant_2):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_combatant_1)
    battle_model.prep_combatant(sample_combatant_2)
    assert len(battle_model.combatants) == 2

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Expected combatants list to be empty"


##################################################
# Battle Execution Tests
##################################################

@patch("meal_max.models.battle_model.get_random", return_value=0.5)
@patch("meal_max.models.battle_model.update_meal_stats")
def test_battle_winner_determined(mock_update_stats, mock_random, battle_model, sample_combatant_1, sample_combatant_2):
    """Test the battle method to determine a winner."""
    battle_model.prep_combatant(sample_combatant_1)
    battle_model.prep_combatant(sample_combatant_2)

    winner = battle_model.battle()
    assert winner in ["Meal 1", "Meal 2"], "Expected winner to be either 'Meal 1' or 'Meal 2'"

    # Check that update_meal_stats was called for both winner and loser
    mock_update_stats.assert_any_call(sample_combatant_1.id, "win")
    mock_update_stats.assert_any_call(sample_combatant_2.id, "loss")


def test_battle_insufficient_combatants(battle_model, sample_combatant_1):
    """Test error when attempting to battle with less than two combatants."""
    battle_model.prep_combatant(sample_combatant_1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()


##################################################
# Battle Score Calculation Tests
##################################################

def test_get_battle_score(battle_model, sample_combatant_1):
    """Test calculating the battle score for a combatant."""
    score = battle_model.get_battle_score(sample_combatant_1)
    expected_score = (sample_combatant_1.price * len(sample_combatant_1.cuisine)) - 2  # MED difficulty modifier is 2
    assert score == expected_score, f"Expected score to be {expected_score} but got {score}"


##################################################
# Combatants Retrieval Tests
##################################################

def test_get_combatants(battle_model, sample_combatant_1, sample_combatant_2):
    """Test retrieving the current list of combatants."""
    battle_model.prep_combatant(sample_combatant_1)
    battle_model.prep_combatant(sample_combatant_2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Meal 1"
    assert combatants[1].meal == "Meal 2"