r"""A naive tree builder.

This builder uses a naive algorithm to build a suffix tree using
:math:`\mathcal{O}(n^2)` time.

Credits: This implementation closely follows the description in [Gusfield1997]_
Chapter §5.4, page 93.
"""

from .util import Path, debug, debug_dot
from .node import Leaf
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using a naive algorithm."""

    name = "Naive"

    def debug_dot(self, i: int):
        """Write a debug graph."""
        debug_dot(self.tree, f"/tmp/suffix_tree_naive_{str(self.id)}_{i}")

    def build(self) -> None:
        """Add a string to the tree."""

        for i in range(0, self.path.end):
            if self.progress:
                self.progress(i)

            path = Path(self.path, i, self.path.end)

            # find longest path from root
            node, matched_len, child = self.tree.find_path(path)

            if child is not None:
                # the path ended in the middle of an edge
                node = node.split_edge(matched_len, child)

            assert matched_len == len(node), f"Add String {matched_len}/{len(node)}"

            assert matched_len < len(path)
            new_leaf = Leaf(node, self.id, Path(path, path.start, path.end))
            assert (
                path.S[path.start + matched_len] not in node.children
            )  # do not overwrite
            node.children[path.S[path.start + matched_len]] = new_leaf
            if __debug__ and util.DEBUG:
                debug(
                    "Adding %s to node %s as [%s]",
                    str(new_leaf),
                    str(node),
                    path.S[path.start + matched_len],
                )
            if __debug__ and util.DEBUG_DOT:
                self.debug_dot(i)
