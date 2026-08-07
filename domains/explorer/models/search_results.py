from dataclasses import dataclass, field
from typing import List


@dataclass
class SearchResults:
    """
    Holds search results and status.

    Attributes:
        query: The search query string
        results: List of file paths matching the search
        is_searching: Whether a search is currently in progress
        error: Error message if search failed
    """
    query: str
    results: List[str] = field(default_factory=list)
    is_searching: bool = False
    error: str = ""

    def add_result(self, path: str) -> None:
        """
        Add a result if not already present.

        Args:
            path: File path to add
        """
        if path and path not in self.results:
            self.results.append(path)

    def clear(self) -> None:
        """
        Clear all results and reset state.
        """
        self.results.clear()
        self.is_searching = False
        self.error = ""