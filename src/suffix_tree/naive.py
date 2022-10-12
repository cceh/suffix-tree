r"""A naive tree builder.

This builder uses a naive algorithm to build a suffix tree in `\mathcal{O}(n^2)` time.

This implementation closely follows the description in [Gusfield1997]_ §5.4 page 93.
"""

from .util import Id, IterSymbols, debug
from .node import Leaf, Internal
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using a naive algorithm."""

    name = "Naive"

    def debug_dot(self, start: int):
        """Write a debug graph."""
        self.root.debug_dot(f"/tmp/suffix_tree_naive_{str(self.id)}_{start}.dot")

    def build(self, root: Internal, id_: Id, S: IterSymbols) -> None:
        """Add a sequence to the tree.

        :param node.Internal root: the root node of the tree
        :param Id id_: the id of the sequence
        :param Symbols S: the sequence to insert
        """
        self.root = root
        self.id = id_

        S = list(S)
        end = len(S)

        node: Internal
        for start in range(end):
            if self.progress and start % self.progress_tick == 0:
                self.progress(start)

            # find longest path from root
            node, matched_len, child = root.find_path(S, start, end)  # type: ignore

            if child is not None:
                # the path ended in the middle of an edge
                node = node.split_edge(matched_len, child)

            assert matched_len == node.depth, f"Add String {matched_len}/{node.depth}"
            assert matched_len < (end - start)

            new_leaf = Leaf(node, self.id, S, start, end)

            assert S[start + matched_len] not in node.children  # do not overwrite

            node.children[S[start + matched_len]] = new_leaf

            if __debug__ and util.DEBUG:
                debug(
                    "Adding %s to node %s as [%s]",
                    str(new_leaf),
                    str(node),
                    S[start + matched_len],
                )
            if __debug__ and util.DEBUG_DOT:
                self.debug_dot(start)
