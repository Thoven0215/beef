import tempfile
from pathlib import Path
import menu_printer
from menu_printer import is_beef, is_favorite, load_favorites, add_favorite, subtract_favorite

# Real beef 
assert is_beef("Beef Burger") == True
assert is_beef("STEAK frites") == True

# Fake beef
assert is_beef("Turkey Steak") == False
assert is_beef("Mediterranean Tofu Steaks") == False

# Not beef
assert is_beef("Cheese Pizza") == False

# Favorites matching
assert is_favorite("Spicy Ramen Bowl", ["ramen"]) == True
assert is_favorite("PIZZA", ["pizza"]) == True
assert is_favorite("Salad", ["pizza"]) == False
assert is_favorite("Salad", []) == False

# Add/remove use a throwaway file so your real favorites.txt is untouched
menu_printer.FAVORITES_FILE = Path(tempfile.mkdtemp()) / "favorites.txt"
assert load_favorites() == []                       # no file yet
assert add_favorite("Ramen") == ["ramen"]           # lowercased
assert add_favorite("ramen") == ["ramen"]           # no duplicates
assert add_favorite("pizza") == ["ramen", "pizza"]
assert subtract_favorite("RAMEN") == ["pizza"]
assert subtract_favorite("sushi") == ["pizza"]      # removing a missing one is fine
assert load_favorites() == ["pizza"]                # really saved to the file

print("All tests passed!")
