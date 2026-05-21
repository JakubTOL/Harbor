from dataclasses import dataclass


@dataclass
class ExplorerState:
    """
    Dataclass representing the state of the explorer.

    Attributes:
        current_path (str): The path currently shown in the explorer.
    """
    current_path: str