import requests
import time
from datetime import date
from pathlib import Path
from typing import Literal
from mcp.server.mcpserver import MCPServer

URL = "https://esb-level1.brown.edu/services/oit/sys/brown-dining/v1/menus"
Meal = Literal["Lunch", "Dinner", "All Day"]
MEALS = frozenset({"Lunch", "Dinner", "All Day"})
BEEF = {"beef", "steak", "cheeseburger"}
NOT_BEEF = ["turkey", "chicken", "mushroom", "tofu"]
FAVORITES_FILE = Path(__file__).parent / "favorites.txt"
mcp = MCPServer("brown-dining")
_cache = {"data": None, "fetched_at": 0}

def get_data():
    """download the menus from the URL"""
    if _cache["data"] is None or time.time() - _cache["fetched_at"] > 30 * 60:
        _cache["data"] = requests.get(URL, timeout=10).json()  # give up after 10s instead of hanging
        _cache["fetched_at"] = time.time()
    return _cache["data"]

def todays_dishes(day=None, meals: list[Meal] = MEALS):
    """all the dishes served on a day as a list of dictionaries"""
    day = day or date.today().isoformat()
    results = []
    for hall in get_data():
        for meal_day in hall["meals"].get(day, []):
            if meal_day["meal"] not in meals:
                continue
            for station in meal_day["menu"]["stations"]:
                for item in station["items"]:
                    if item["itemType"] == "ingredient":
                        continue
                    results.append({"hall": hall["name"], "meal": meal_day["meal"], "dish": item["item"]})
    return results

def is_beef(dish_name):
    """is the food beef?"""
    name = dish_name.lower()
    has_beef_word = any(word in name for word in BEEF)
    isnt_beef_word = any(word in name for word in NOT_BEEF)
    return has_beef_word and not isnt_beef_word

@mcp.tool()
def find_beef(day=None, meals: list[Meal] = MEALS):
    """Find beef dishes (beef, steak, cheeseburger) at Brown dining halls.

    day: date as YYYY-MM-DD, defaults to today. Menus exist for today through 6 days ahead.
    meals: which meals to search, defaults to all.
    Returns a list of {hall, meal, dish}. Empty list = no beef that day.
    """
    res = []
    dishes = todays_dishes(day, meals)
    for food in dishes:
        if is_beef(food["dish"]):
            res.append(food)
    return res

@mcp.tool()
def load_favorites():
    """List the user's saved favorite foods."""
    try:
        text = FAVORITES_FILE.read_text()
    except FileNotFoundError:
        return []
    return [line.strip().lower() for line in text.splitlines() if line.strip()]

def save_favorites(favorites):
    """write the list back to favorites.txt"""
    FAVORITES_FILE.write_text("\n".join(favorites) + "\n")

@mcp.tool()
def add_favorite(food):
    """Save a food to the user's favorites, e.g. "ramen". Returns the updated list."""
    food = food.strip().lower()
    favorites = load_favorites()
    if food and food not in favorites:
        favorites.append(food)
        save_favorites(favorites)
    return favorites

@mcp.tool()
def subtract_favorite(food):
    """Remove a food from the user's favorites. Returns the updated list."""
    food = food.strip().lower()
    favorites = load_favorites()
    if food in favorites:
        favorites.remove(food)
        save_favorites(favorites)
    return favorites

def is_favorite(dish_name, favorites):
    """is the food my favorite?"""
    name = dish_name.lower()
    return any(word in name for word in favorites)

@mcp.tool()
def find_favorite(day=None, meals: list[Meal] = MEALS):
    """Find dishes at Brown dining halls that match the user's saved favorite foods.

    day: date as YYYY-MM-DD, defaults to today.
    meals: which meals to search, defaults to all.
    Returns a list of {hall, meal, dish}. Empty list = no favorites that day.
    """
    favorites = load_favorites() 
    res = []
    dishes = todays_dishes(day, meals)
    for food in dishes:
        if is_favorite(food["dish"], favorites):
            res.append(food)
    return res

if __name__ == "__main__":
    mcp.run()