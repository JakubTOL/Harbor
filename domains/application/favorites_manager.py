import os
import json
from pathlib import Path

def get_favorites_file_path():
    """
    Determine the appropriate path to store the favorites file, depending on the platform.

    Returns:
        str: Absolute path to the user's favorites.json configuration.
    """
    # Use user's config dir (cross-platform)
    if os.name == "nt":
        config_dir = os.path.join(os.environ.get("APPDATA", str(Path.home())), "Harbor")
    else:
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "Harbor")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "favorites.json")

class FavoritesManager:
    """
    Manager class for handling user favorites directories.
    Loads and saves favorites to persistent storage.
    """

    def __init__(self):
        """
        Initialize the FavoritesManager and load existing favorites.
        """
        self.favorites = []
        self.fav_path = get_favorites_file_path()
        self.load()

    def load(self):
        """
        Load favorites from disk, or start with an empty list if unavailable.
        """
        try:
            with open(self.fav_path, "r", encoding="utf-8") as f:
                self.favorites = json.load(f)
        except Exception:
            self.favorites = []

    def save(self):
        """
        Persist the favorites list to disk as a JSON file.
        """
        with open(self.fav_path, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f)

    def add_favorite(self, path):
        """
        Add a directory path to the favorites list, if not already present.

        Args:
            path (str): The directory path to add.
        """
        if path not in self.favorites:
            self.favorites.append(path)
            self.save()

    def remove_favorite(self, path):
        """
        Remove a directory path from the favorites list, if present.

        Args:
            path (str): The directory path to remove.
        """
        if path in self.favorites:
            self.favorites.remove(path)
            self.save()

    def is_favorite(self, path):
        """
        Check if a directory is currently marked as a favorite.

        Args:
            path (str): The directory path to check.

        Returns:
            bool: True if the path is a favorite, False otherwise.
        """
        return path in self.favorites

    def all(self):
        """
        Get the current favorites list.

        Returns:
            list: List of favorite directory paths.
        """
        return list(self.favorites)