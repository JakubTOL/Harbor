import os
import threading
from typing import Callable, Optional
from PySide6.QtCore import QObject, Signal


class SearchWorker(QObject):
    """
    Worker object that emits signals to communicate with the main thread.
    This solves the threading/Qt safety issues.
    """

    result_found = Signal(str)  # Emits file path when match found
    search_finished = Signal()  # Emits when search completes

    def __init__(self):
        """Initialize the search worker."""
        super().__init__()
        self.stop_search = False

    def search(self, root_path: str, query: str) -> None:
        """
        Search for files matching query in root_path.

        Args:
            root_path: Root directory to search in
            query: Search term (case-insensitive substring match)
        """
        self.stop_search = False
        query_lower = query.lower()

        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Check if search should be stopped
                if self.stop_search:
                    break

                # Search through filenames in current directory
                for filename in filenames:
                    if self.stop_search:
                        break

                    # Case-insensitive substring match
                    if query_lower in filename.lower():
                        full_path = os.path.join(dirpath, filename)
                        # Emit signal (thread-safe!)
                        self.result_found.emit(full_path)

        except (PermissionError, OSError):
            # Silently skip inaccessible directories
            pass
        finally:
            # Signal completion (thread-safe!)
            self.search_finished.emit()

    def stop(self) -> None:
        """Stop the current search operation."""
        self.stop_search = True


class SearchService:
    """
    Handles file system searching in background threads.
    Manages worker threads and their lifecycle.
    """

    def __init__(self):
        """Initialize the search service."""
        self.search_thread: Optional[threading.Thread] = None
        self.worker: Optional[SearchWorker] = None

    def search_files(
            self,
            root_path: str,
            query: str,
            on_result: Callable[[str], None],
            on_complete: Callable[[], None]
    ) -> None:
        """
        Search for files matching query in root_path asynchronously.

        Args:
            root_path: Root directory to search in
            query: Search term (case-insensitive substring match)
            on_result: Callback function called with each match (file path as string)
            on_complete: Callback function called when search completes
        """
        # Stop any existing search
        if self.worker:
            self.worker.stop()

        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join(timeout=2)

        # Create new worker
        self.worker = SearchWorker()

        # Connect signals to callbacks
        self.worker.result_found.connect(on_result)
        self.worker.search_finished.connect(on_complete)

        # Start search in background thread
        self.search_thread = threading.Thread(
            target=self.worker.search,
            args=(root_path, query),
            daemon=True
        )
        self.search_thread.start()

    def stop(self) -> None:
        """Stop the current search operation."""
        if self.worker:
            self.worker.stop()