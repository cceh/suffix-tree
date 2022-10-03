"""The base class for all builders."""

from typing import Callable, Optional

from .node import Internal
from .util import Path, Id


class Builder:
    """Base class for all builders."""

    name = "Builder"

    def __init__(self, tree, id_: Id, path: Path):
        self.tree = tree
        self.id: Id = id_
        self.path: Path = path
        self.root: Internal = tree.root
        self.progress: Optional[Callable[[int], None]] = None

    def set_progress_function(self, progress: Callable[[int], None] = None):
        """Set a progress indicator function.

        The function gets called at regular intervals with the current phase as
        parameter.
        """
        self.progress = progress

    def build(self) -> None:
        """Add a string to the tree."""
        raise NotImplementedError
