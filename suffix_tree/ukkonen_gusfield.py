# -*- coding: utf-8 -*-
#

r"""Ukkonen's Algorithm according to Gusfield

Ukkonen's algorithm to build a suffix tree in linear time.

Credits: This implementation of Ukkonen's algorithm in Python closely follows
the description in [Gusfield1997]_ Chapter 6, 94ff.

See also: the implementation in C by Dan Gusfield et al.:
http://web.cs.ucdavis.edu/%7Egusfield/strmat.html

See also: Ukkonen's original paper:
http://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf

"""

from .util import Path, debug, debug_dot
from .node import Leaf
from . import builder

class Builder (builder.Builder):
    """Builds the suffix-tree using Ukkonen's Algorithm."""

    def debug_dot (self, i, j):
        """ Write a debug graph. """
        debug_dot (self.tree, '/tmp/suffix_tree_ukkonen_gusfield_%s_%d_%d' % (self.id, i, j))


    def suffix_link_dance (self, node, beta):
        """Go to the parent, follow the suffix link and do the skip/count trick."""

        if node.suffix_link is not None:
            # just follow the suffix link
            debug ("Followed node's own suffix link to node %s", str (node.suffix_link))
            return node.suffix_link

        if node.parent and node.parent.suffix_link:
            l = len (beta)
            # do the skip / count dance
            debug ("Starting suffix link dance from node %s", str (node))
            sv = node.parent.suffix_link
            debug ("The old node has len %d", len (node))
            debug ("The sv node has len %d",  len (sv))
            debug ("Skipping down to len %d", l)
            # use the skip/count trick to move down the tree.
            while True:
                child = sv.children[node.path[len (sv) + 1]]
                if len (child) >= l:
                    break
                sv = child
            debug ("Ended suffix link dance on node %s", str (sv))
            return sv

        # fallback to the naive method
        node, dummy_matched_len, dummy_child = self.tree.find_path (beta)
        debug ("Found node %s using naive method", str (node))
        return node

    def build (self):
        """Add a string to the tree """

        node = self.tree.root
        M = len (self.path)
        i = 0            # Ukkonen phase
        j = 0            # Ukkonen extension
        last_phase = -1  # for detection of repeated execution of extension

        while i <= M - 1:

            # Single phase algorithm: SPA
            #
            # Begin
            #
            # 1. Increment index :math:`e` to :math:`i + 1`. (By Trick 3 this
            #    correctly implements all implicit extensions 1 through
            #    :math:`j_i`.)
            #
            # 2. Explicitly compute successive extensions (using algorithm SEA)
            #    starting at :math:`j_i + 1` until reaching the first extension
            #    :math:`j^*` where rule 3 applies or until all extensions are done
            #    in this phase.  (By Trick 2, this correctly implements all the
            #    additional implicit extensions :math:`j^* + 1` through :math:`i +
            #    1`.)
            #
            # 3. Set :math:`j_{i + 1}` to :math:`j^* - 1`, to prepare for the next
            #    phase.
            #
            # End
            #
            # [...] phase :math:`i + 1` ends knowing where string :math:`S[j^*..i
            # + 1]` ends, so the repeated extension of :math:`j^*` in phase
            # :math:`i + 2` can execute the suffix extension rule for :math:`j^*`
            # without any up-walking, suffix traversals, or node skipping.
            #
            # -- [Gusfield1997]_, page 106

            Path.e = i + 1 # adjust the 'open ended' marker for leaf nodes
            Sip1 = self.path[i] # the character :math:`S(i + 1)`

            w = dict ()    # Queue for nodes :math:`w` eventually created by
                           # Rule2, see: SEA 4
            sw = None      # The node :math:`s(w)`

            debug ("\n\n=== Phase i=%d === extending [:%d] (%s) with %s",
                   i, i, str (self.path[:i]), Sip1)

            while j <= i:

                self.debug_dot (i, j)

                # Single extension algorithm: SEA
                #
                # Putting these pieces together, when implemented using suffix
                # links, extension :math:`j \gte 2` of phase :math:`i + 1` is:
                #
                # Begin
                #
                # 1. Find the first node :math:`v` at or above the end of
                #    :math:`S[j - 1..i]` that either has a suffix link from it
                #    or is the root.  This requires walking up at most one edge
                #    from the end of :math:`S[j - 1..i]` in the current tree.
                #    Let :math:`\gamma` (possibly empty) denote the string
                #    between :math:`v` end the end of :math:`S[j - 1..i]`.
                #
                # 2. If :math:`v` is not the root traverse the suffix link from
                #    :math:`v` to node :math:`s(v)` and then walk down from
                #    :math:`s(v)` following the path for string :math:`\gamma`.
                #    If :math:`v` is the root, then follow the path for
                #    :math:`S[j..i]` from the root (as in the naive algorithm).
                #
                # 3. Using the extension rules, ensure that the string
                #    :math:`S[j..i]S(i + 1)` is in the tree.
                #
                # 4. If a new internal node :math:`w` was created in extension
                #    :math:`j - 1` (by extension rule 2), then by Lemma 6.1.1,
                #    string :math:`\alpha` must end at node :math:`s(w)`, the
                #    end node for the suffix link from :math:`w`.  Create the
                #    suffix link :math:`(w, s(w))` from :math:`w` to
                #    :math:`s(w)`.
                #
                # End.
                #
                # Assuming the algorithm keeps a pointer to the current full
                # string :math:`S[1..i]`, the first extension of phase :math:`i
                # + 1` need not do any up or down walking.
                #
                # -- [Gusfield1997]_, page 100

                ############################################
                # Find the end of beta in the current tree #
                ############################################

                # node is positioned at the end of the last extension's beta.

                beta = Path (self.path.S, j, i) # the string :math:`S[j..i]` aka. as :math:`beta`
                l = len (beta)

                debug ("\n--- Extension j=%d l=%d --- [%d:%d] extending (%s) with %s",
                       j, l, j, i, str (beta), Sip1)
                debug ("Now at node %s", str (node))

                if i != last_phase:
                    # node is already at the right positon
                    last_phase = i
                    debug ("Re-executing extension %d from node %s", j, str (node))
                else:
                    # do the suffix link dance: SEA steps 1 and 2
                    node = self.suffix_link_dance (node, beta)

                # oldnode = node
                # node, matched_len, child = self.tree.find_path (beta)
                # assert node == oldnode, ("node is %s, should be = %s" %
                #                          (str (oldnode), str (node)))

                ##############################
                # Perform a suffix extension #
                ##############################

                # Let :math:`S[j..i] = \beta` be a suffix of :math:`S[1..i]`.
                # In extension :math:`j`, when the algorithm finds the end of
                # :math:`\beta` in the current tree, it extends :math:`\beta` to
                # be sure the suffix :math:`\beta S(i + 1)` is in the tree.  It
                # does this according to one of the following three rules:
                #
                # -- [Gusfield1997]_, page 96

                sw = node # target for suffix link

                # We matched :math:`\beta`. Try matching :math:`\beta S(i + 1)`.
                node, matched_len, child = node.find_path (Path (self.path.S, j, i + 1))

                assert matched_len >= l, (
                    r"Fatal: \beta not found in tree. l = %d, matched_len = %d" %
                    (l, matched_len))

                debug ("Performing suffix extension, l = %d, matched len = %d",
                       l, matched_len)

                # **Rule 1** In the current tree, path :math:`\beta` ends at a
                # leaf.  That is, the path from the root labeled :math:`\beta`
                # extends to the end of some leaf edge.  To update the tree,
                # character :math:`S(i + 1)` is added to the end of the label of
                # that leaf edge.

                #if node.is_leaf ():
                #    node.add (self.id, Path (self.path.S, j, Path.inf))
                #    debug ("*** Applied Rule 1 -- extended leaf %s", str (node))

                # **Rule 3** Some path from the end of string :math:`\beta`
                # starts with character :math:`S(i + 1)`.  In this case the
                # string :math:`\beta S(i + 1)`, is already in the current tree,
                # so (remembering that in an implicit suffix tree the end of a
                # suffix need not be explicitly marked) we do nothing.

                # N.B.  In a *generalized* suffix tree rule 3 must fix up leaf
                # nodes, because more than one string can end at a leaf.  We
                # test for rule 3 after rule 1, so rule 1 fixed up the node for
                # us.

                if matched_len > l:
                    # We did match :math:`\beta S(i + 1)`!
                    debug ("*** Applied Rule 3 -- did nothing while at node %s", str (node))
                    # Trick 2: End any phase the first time that extension rule
                    # 3 applies.
                    break # SPA step 3: begin next phase, same extension

                # **Rule 2** No path from the end of string :math:`\beta` starts
                # with character :math:`S(i + 1)`, but at least one labeled path
                # continues from the end of :math:`\beta`.
                #
                # In this case a new leaf edge starting from the end of
                # :math:`\beta` must be created and labeled with character
                # :math:`S(i + 1)`.  A new node will also have to be created
                # there if :math:`\beta` ends inside an edge.  The leaf at the
                # end of the new leaf edge is given the number :math:`j`.

                elif child is None and Sip1 not in node.children: # also catches root
                    leaf = Leaf (node, self.id, Path (self.path.S, j, Path.inf))
                    node.children[Sip1] = leaf
                    debug ("*** Applied Rule 2.1 -- added new leaf %s to node %s",
                           str (leaf), str (node))

                elif child is not None:
                    w[j] = sw = node = node.split_edge (matched_len, child)
                    debug ("Setting w to the new internal node %s", str (node))
                    leaf = Leaf (node, self.id, Path (self.path.S, j, Path.inf))
                    node.children[Sip1] = leaf
                    debug ("*** Applied Rule 2.2 -- added new leaf %s and split node %s",
                           str (leaf), str (node))
                else:
                    assert True, "can't happen"

                #######################
                # Create suffix links #
                #######################

                if w.get (j - 1) is not None:
                    debug ("Giving w %s a suffix_link to %s", str (w[j - 1]), str (sw))
                    w[j - 1].suffix_link = sw
                    del w[j - 1]

                ####################################
                # Continue with the next extension #
                ####################################

                assert l == len (node), "l = %s, len (node) = %d" % (l, len (node))

                j += 1

            i += 1

        self.fixup_e (M)
