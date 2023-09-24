"""The base class for all builders."""

from typing import Callable, Optional

from .node import Internal
from .util import Id, IterSymbols


class Builder:
    """The base class for all builders."""

    name = "Builder"

    def __init__(self):
        self.root: Internal
        self.id: Id
        self.progress: Optional[Callable[[int], None]] = None
        self.progress_tick = 1

    def build(self, root: Internal, id_: Id, S: IterSymbols) -> None:
        """Add the sequence to the tree."""
        raise NotImplementedError()

    def set_progress_function(
        self, tick: int, callback: Optional[Callable[[int], None]] = None
    ):
        """Set a progress indicator callback function.

        You should not change the tree in this callback.

        :param int tick:          call the callback every tick rounds
        :param Callable callback: The function is called with the index of the current
                                  round as parameter.
        """
        self.progress_tick = tick
        self.progress = callback
