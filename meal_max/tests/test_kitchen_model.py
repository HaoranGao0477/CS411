import pytest
import sqlite3
from meal_max.models.kitchen_model import (
    create_meal, clear_meals, delete_meal, get_leaderboard, 
    get_meal_by_id, get_meal_by_name, update_meal_stats, Meal
)

@pytest.fixture
def sample_meal():
    """Fixture to provide a sample meal."""
    return Meal(id=1, meal="Meal 1", cuisine="Cuisine 1", price=99, difficulty="MED")

@pytest.fixture
def db_connection(mocker):
    """Mock the database connection for testing purposes."""
    mock_conn = mocker.patch("meal_max.utils.sql_utils.get_db_connection")
    mock_conn.return_value.__enter__.return_value.cursor.return_value.fetchall.return_value = []
    return mock_conn

##################################################
# Meal Creation Tests
##################################################

def test_create_meal_valid(db_connection):
    """Test creating a valid meal."""
    create_meal("Meal 1", "Cuisine 1", 99, "MED")
    db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_once_with(
        "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)", 
        ("Meal 1", "Cuisine 1", 99, "MED")
    )

def test_create_meal_invalid_price(db_connection):
    """Test creating a meal with an invalid negative price."""
    with pytest.raises(ValueError, match="Invalid price: -99. Price must be a positive number."):
        create_meal("Meal 2", "Cuisine 2", -99, "MED")

def test_create_meal_invalid_difficulty(db_connection):
    """Test creating a meal with an invalid difficulty."""
    with pytest.raises(ValueError, match="Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal("Meal 3", "Cuisine 3", 99, "EASY")

def test_create_duplicate_meal(db_connection, mocker):
    """Test creating a duplicate meal."""
    mocker.patch("meal_max.utils.sql_utils.get_db_connection").return_value.__enter__.return_value.cursor.return_value.execute.side_effect = sqlite3.IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Meal 1' already exists"):
        create_meal("Meal 1", "Cuisine 1", 99, "MED")

##################################################
# Meal Deletion Tests
##################################################

def test_delete_meal_valid(db_connection):
    """Test deleting a meal by ID."""
    delete_meal(1)
    db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_any_call(
        "UPDATE meals SET deleted = TRUE WHERE id = ?", (1,)
    )

def test_delete_nonexistent_meal(db_connection):
    """Test deleting a meal that does not exist."""
    db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)

##################################################
# Meal Retrieval Tests
##################################################

def test_get_meal_by_id_existing(db_connection, sample_meal):
    """Test retrieving an existing meal by ID."""
    db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (
        sample_meal.id, sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty, False
    )
    meal = get_meal_by_id(1)
    assert meal.id == sample_meal.id
    assert meal.meal == sample_meal.meal
    assert meal.cuisine == sample_meal.cuisine
    assert meal.price == sample_meal.price
    assert meal.difficulty == sample_meal.difficulty

def test_get_meal_by_id_deleted(db_connection):
    """Test retrieving a meal by ID that is deleted."""
    db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (1, "Meal 1", "Cuisine 1", 99, "MED", True)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_get_meal_by_name_existing(db_connection, sample_meal):
    """Test retrieving an existing meal by name."""
    db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (
        sample_meal.id, sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty, False
    )
    meal = get_meal_by_name("Meal 1")
    assert meal.id == sample_meal.id
    assert meal.meal == sample_meal.meal
    assert meal.cuisine == sample_meal.cuisine
    assert meal.price == sample_meal.price
    assert meal.difficulty == sample_meal.difficulty

##################################################
# Leaderboard Tests
##################################################

def test_get_leaderboard_sorted_by_wins(db_connection):
    """Test retrieving leaderboard sorted by wins."""
    db_connection.return_value.__enter__.return_value.cursor.return_value.fetchall.return_value = [
        (1, "Meal 1", "Cuisine 1", 99, "MED", 10, 7, 0.7)
    ]
    leaderboard = get_leaderboard(sort_by="wins")
    assert leaderboard[0]['meal'] == "Meal 1"
    assert leaderboard[0]['wins'] == 7

def test_get_leaderboard_invalid_sort(db_connection):
    """Test leaderboard retrieval with an invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard(sort_by="invalid")

##################################################
# Meal Stats Update Tests
##################################################

def test_update_meal_stats_win(db_connection):
    """Test updating a meal's stats with a win."""
    update_meal_stats(1, "win")
    db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,)
    )

def test_update_meal_stats_loss(db_connection):
    """Test updating a meal's stats with a loss."""
    update_meal_stats(1, "loss")
    db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1 WHERE id = ?", (1,)
    )

def test_update_meal_stats_invalid_result(db_connection):
    """Test updating meal stats with an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_meal_stats(1, "draw")

##################################################
# Utility Tests
##################################################

def test_clear_meals(db_connection):
    """Test clearing all meals in the database."""
    clear_meals()
    db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_once()

