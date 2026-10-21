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
        self.max_results = 200

    def search(self, root_path: str, query: str) -> None:
        """
        Search for files matching query in root_path.

        Args:
            root_path: Root directory to search in
            query: Search term (case-insensitive substring match)
        """
        self.stop_search = False
        query_lower = query.lower()
        matches = 0

        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                if self.stop_search:
                    break

                for filename in filenames:
                    if self.stop_search:
                        break

                    if matches >= self.max_results:
                        self.stop_search = True
                        break

                    if query_lower in filename.lower():
                        full_path = os.path.join(dirpath, filename)
                        self.result_found.emit(full_path)
                        matches += 1

        except (PermissionError, OSError):
            pass
        finally:
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

    def search_files(self, root_path, query, on_result, on_complete):
        if self.worker:
            self.worker.stop()

        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join(timeout=0.2)

        self.worker = SearchWorker()
        self.worker.result_found.connect(on_result)
        self.worker.search_finished.connect(on_complete)

        self.search_thread = threading.Thread(
            target=self.worker.search,
            args=(root_path, query),
            daemon=True,
        )
        self.search_thread.start()

    def stop(self) -> None:
        """Stop the current search operation."""
        if self.worker:
            self.worker.stop()