import os
import json
import tempfile
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

def canonicalize_path(path: str) -> str:
    """
    Normalize a path for comparison and storage.
    """
    if not path:
        return ""

    try:
        return str(Path(path).expanduser().resolve(strict=False))
    except Exception:
        return str(Path(path).expanduser())

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
        Load favorites from disk, filtering invalid or duplicate entries.
        """
        try:
            with open(self.fav_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self.favorites = []
            return

        if not isinstance(raw_data, list):
            self.favorites = []
            return

        seen = set()
        valid_paths = []

        for item in raw_data:
            if not item or not isinstance(item, str):
                continue

            normalized = canonicalize_path(item)
            if not normalized or not os.path.isdir(normalized):
                continue

            key = normalized.lower()
            if key in seen:
                continue

            seen.add(key)
            valid_paths.append(normalized)

        self.favorites = valid_paths

    def save(self):
        """
        Persist favorites to disk using an atomic write to avoid corruption.
        """
        directory = os.path.dirname(self.fav_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                delete=False,
                encoding="utf-8",
                dir=directory or None
            ) as tmp:
                temp_path = tmp.name
                json.dump(self.favorites, tmp)

            os.replace(temp_path, self.fav_path)
        except Exception:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def add_favorite(self, path):
        """
        Add a directory path to the favorites list, if not already present.

        Args:
            path (str): The directory path to add.
        """
        normalized = canonicalize_path(path)
        if not normalized or not os.path.isdir(normalized):
            return

        existing_keys = {item.lower() for item in self.favorites}
        if normalized.lower() in existing_keys:
            return

        self.favorites.append(normalized)
        self.save()

    def remove_favorite(self, path):
        """
        Remove a directory path from the favorites list, if present.

        Args:
            path (str): The directory path to remove.
        """
        normalized = canonicalize_path(path)
        if not normalized:
            return

        self.favorites = [
            item for item in self.favorites
            if item.lower() != normalized.lower()
        ]
        self.save()

    def is_favorite(self, path):
        """
        Check if a directory is currently marked as a favorite.

        Args:
            path (str): The directory path to check.

        Returns:
            bool: True if the path is a favorite, False otherwise.
        """
        normalized = canonicalize_path(path)
        if not normalized:
            return False

        return any(item.lower() == normalized.lower() for item in self.favorites)


    def all(self):
        """
        Get the current favorites list.

        Returns:
            list: List of favorite directory paths.
        """
        return list(self.favorites)