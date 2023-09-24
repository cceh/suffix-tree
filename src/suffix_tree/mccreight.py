r"""A tree builder that uses McCreight's Algorithm.

This module implements McCreight's algorithm to build a suffix tree in linear time,
adapted to generalized suffix trees.

"""

from .util import Id, IterSymbols, debug
from .node import Node, Internal, Leaf
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using McCreight's Algorithm."""

    name = "McCreight"

    __slots__ = ["root"]

    def debug_dot(self, start: int) -> None:
        """Write a debug graph."""
        self.root.debug_dot(f"/tmp/suffix_tree_mccreight_{str(self.id)}_{start}.dot")

    def build(self, root: Internal, id_: Id, S: IterSymbols) -> None:
        r"""Add a sequence to the tree.

        :param node.Internal root: the root node of the tree
        :param Id id_: the id of the sequence
        :param Symbols S: the sequence to insert
        """
        self.root = root
        self.id = id_

        root.suffix_link = root
        root.parent = root

        S = list(S)
        end = len(S)
        head = root
        matched_len = 0

        for start in range(end):
            if self.progress and start % self.progress_tick == 0:
                self.progress(start)

            #
            # substep A
            #
            if __debug__ and util.DEBUG:
                debug(f"start of substep A with head {head} depth={head.depth}")

            c: Node = head.suffix_link or head.parent.suffix_link  # type: ignore

            #
            # substep B
            #
            if __debug__ and util.DEBUG:
                debug(f"start of substep B with c {c} depth={c.depth}")

            # Fast rescan along the path to the depth of matched_len - 1.

            if matched_len > 1:
                # We have to examine only the first symbol of each edge because we
                # already know there must be a path.
                depth = matched_len - 1
                while c.depth < depth:
                    assert isinstance(c, Internal)
                    c = c.children[head[c.depth + 1]]  # type: ignore
                if c.depth > depth:
                    # The path ended in the middle of an edge.
                    assert c.parent
                    c = c.parent.split_edge(depth, c)

                if __debug__ and util.DEBUG:
                    debug(f"rescanned to depth of {depth}")
                assert c.depth == depth

            if head.suffix_link is None:
                assert isinstance(c, Internal)
                head.suffix_link = c  # type: ignore

            #
            # substep C
            #
            if __debug__ and util.DEBUG:
                debug(f"start of substep C on c {c} depth={c.depth}")

            # Slow scan from d
            head, matched_len, child = c.find_path(S, start, end)  # type: ignore
            if __debug__ and util.DEBUG:
                debug(f"scanned to depth of {matched_len}")

            if child is not None:
                # the path ended in the middle of an edge
                head = head.split_edge(matched_len, child)

            if __debug__ and util.DEBUG:
                debug(f"new head is head {c} depth={head.depth}")

            # assert matched_len == head.depth, f"Add String {matched_len}/{head.depth}"
            # assert matched_len < (end - start), f"{matched_len} < {end}-{start}"
            # assert S[start + matched_len] not in head.children  # do not overwrite

            new_leaf = Leaf(head, self.id, S, start, end)
            head.children[S[start + matched_len]] = new_leaf

            if __debug__ and util.DEBUG:
                debug(
                    "Added %s to node %s as [%s]",
                    str(new_leaf),
                    str(head),
                    S[start + head.depth],
                )
            if __debug__ and util.DEBUG_DOT:
                self.debug_dot(start)
