#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

clear_meals() {
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating the meal ($meal, $cuisine, $price, $difficulty) and adding it to the meal list..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":\"$price\", \"difficulty\":$difficulty}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal_by_id(){
    meal_id=$1

    echo "Deleting meal by ID ($meal_id)..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal deleted successfully by ID ($meal_id)."
    else
        echo "Failed to delete meal by ID ($meal_id)."
        exit 1
    fi
}

get_meal_by_id(){
    meal_id=$1

    echo "Getting meal by ID ($meal_id)..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-from-catalog-by-id/$song_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by ID ($meal_id)."
        if [ "$ECHO_JSON" = true ]; then
        echo "Meal JSON (ID $meal_id):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get meal by ID ($meal_id)."
        exit 1
    fi
}

get_meal_by_name(){
    meal_name=$1

    echo "Getting meal by name ($meal_name)..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-from-catalog-by-name/$meal_name")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "($meal_name) retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Meal JSON (name $meal_name):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get ($meal_name) by its name ."
        exit 1
    fi

}

get_random_meal() {
  echo "Getting a random meal from the combatant list..."
  response=$(curl -s -X GET "$BASE_URL/get-random-meal")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get a random meal."
    exit 1
  fi
}


############################################################
#
# Meal Battle Management
#
############################################################

prep_combatant(){
    combatant=$1
    cuisine=$2
    price=$3
    difficulty=$4

    echo "Adding ($combatant) to combatants list to battle..."
    response=$(curl -s -X GET "$BASE_URL/prep-combatant")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatant added to combatants list successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Combatabt JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to add combatant to combatants list."
        exit 1
    fi
}

get_combatants(){
    echo "Getting combatants that are in list to battle"

    response=$(curl -s -X GET "$BASE_URL/get-combatants")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Retrieved combatants list successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Combatabts JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get combatants list."
        exit 1
    fi
}

battle(){
    echo "Getting combatants to battle"

    response=$(curl -s -X GET "$BASE_URL/battle")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Battle occured successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Battle JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to battle."
        exit 1
    fi
}

clear_combatants(){
    echo "Battle over, clearing all the combatants..."
    response=$(curl -s -X POST "$BASE_URL/clear-combatants")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatants cleared successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Clear combatants JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to clear combatants."
        exit 1
    fi
}



######################################################
#
# Leaderboard
#
######################################################

get_leaderboard(){ 
    sort_by=$1
    echo "Getting leaderboard which is sorted by $sort_by..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard_sort=$sort_by")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Loaded leaderboard successfully."
        if [ "$ECHO_JSON" = true ]; then
        echo "Leaderboard JSON (sorted by $sort_by):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get leaderboard."
        exit 1
    fi
}

########################
#TESTS
#######################

# Health checks
check_health
check_db
########################## 
#SUCESSFUL CASES 
################################
# Create meals
create_meal "Lasagna Bolognese" "Italian" 66.6 "MED"
create_meal "Risotto alla Milanese" "Italian" 88.8 "High"
create_meal "Sushi" "Japanese" 11.1 "LOW"
create_meal "Ramen" "Japanese" 22.2 "LOW"
create_meal "Peking Duck" "Chinese" 99.9 "HIGH"

delete_meal_by_id 1
get_meal_by_id 2

get_random_meal

get_meal_by_name "Ramen"
get_meal_by_name "Sushi"

# Clear the meals
clear_meals

# Create meals
create_meal "Lasagna Bolognese" "Italian" 66.6 "MED"
create_meal "Risotto alla Milanese" "Italian" 88.8 "High"
create_meal "Sushi" "Japanese" 11.1 "LOW"
create_meal "Ramen" "Japanese" 22.2 "LOW"
create_meal "Peking Duck" "Chinese" 99.9 "HIGH"

#prep_combatant
prep_combatant "Lasagna Bolognese" "Italian" 66.6 "MED"
prep_combatant "Risotto alla Milanese" "Italian" 88.8 "High"

get_combatants

battle

get_leaderboard

# Clear the combatants
clear_combatants


echo "All tests passed successfully!"


################################
#Failed case
################################


#From prep_combatant above
prep_combatant "Sushi" "Japanese" 11.1 "LOW"
prep_combatant "Ramen" "Japanese" 22.2 "LOW"
prep_combatant "Peking Duck" "Chinese" 99.9 "HIGH"

echo "Tests failed!"

# Failed cases for kitchen model
create_meal "Lasagna Bolognese" "Italian" 66.6 "MED"
create_meal "Lasagna Bolognese" "Italian" 66.6 "MED"

delete_meal 1
delete_meal 1
