Ukkonen Builder
---------------

Ukkonen's algorithm is very similar to McCreight's.

================  ========================  ===================
McCreight1976     Ukkonen1995               English
================  ========================  ===================
step              phase                     round
locus             implicit state            node + substring
locus node        explicit state            node
\                 branching state           internal node
\                 final state               leaf
arc               transition function       edge
suffix link       suffix function           suffix pointer
head              active point
contracted locus  canonical representation  parent node
scan                                        search
rescan            canonize                  fast-forward search
================  ========================  ===================

The differences are: In round `i` Ukkonen inserts character `t_i` into the tree while
McCreight inserts the whole suffix `t_i\dots t_n`.  Ukkonen's algorithm  does not need
to know the characters following `t_i`. It can build a tree from a Python generator and
be ready in constant time after the last character was generated.

McCreight's algorithm is easier to understand.  McCreight inserts one leaf and at most
one internal node per round.  It is not clear beforehand how many leafs and internal
nodes a round in Ukkonen's will insert: in Fig. 2 of Ukkonen's paper, the last round
creates 2 internal nodes and 3 new leaves, while both preceding rounds created nothing.

Some annotations to Ukkonen's paper follow:

Ukkonen identifies subsequences by two indices: `k` and `p`.  In a generalized suffix
tree these are not sufficient to uniquely identify a subsequence, we also need to know
to which sequence `k` and `p` are referring.  So instead of using the parameter pair
`(k,p)` we use three parameters: `(S,k,p)`. We also prefer to name them: ``S, start,
end``.

We also have two problems with indices:  The first is that Python indices start with 0
while Ukkonen's start with 1.  The second is that Python indices point to one beyond the
end while Ukkonen's point to the end.  In conclusion: Ukkonen's `1..2` becomes Python's
``[0:2]``.

Ukkonen treats the *suffix trie* as an automaton and thus uses *transition function* to
describe what a mere mortal would call an *edge*, and *explicit state* `s` to describe
what the rest of us would call a *node.*  Edges in a trie are labeled by one character
only.  A *branching state* is an internal node, a *final state* is a leaf node.  Every
node in the trie represents a substring and every leaf node represents a suffix.  The
converse is true.  The node representing the string `abc` is called `\overline{abc}`.

A *suffix tree* is a compressed suffix trie without those internal nodes that have only
one child.  Edges in a tree are labeled by more than one character.  As a consequence
those states in the trie that had their nodes removed become *implicit states* in the
tree.  Those that still retain their nodes are *explicit states*.  Explicit substrings
always end on a node, implicit ones end in the middle of an edge (but can be made
explict by splitting the edge).

States are represented by the triple: `(s,(k,p))`, which is a node and a substring
going out of the node.  There may be more than one such representation.  Remember that
we use ``node, S, start, end`` instead.

The *canonical representation* of a state is: the state itself and an empty substring if
explicit, the nearest node above the state and the shortest possible substring if
implicit.

The *transition function* `g'(s,(k,p)) = r` starts at node `s` and ends at the state
`r`, which may be a node or an implicit state (in the middle of an edge).

The *suffix function* `f(\bar x) = \bar y` is a link present at each internal node, that
points to another node that encodes the same suffix minus the first symbol.  Following
suffix links you get from: cacao -> acao -> cao -> ao -> a -> root -> aux.

An *open transition* is any edge going into a leaf.  A leaf's ``end`` grows
automatically whenever a new symbol is added to the tree.

The *boundary path* of a trie is the chain of suffix links starting at the deepest state
and ending at aux. In a tree the states on the boundary path may be implicit.  To follow
an implicit boundary path we use substep A and substep B from McCreight's algorithm.

The *active point* and *end point* are states on the boundary path.  Active point and
end point may be the same point.  The active point is the first state on the boundary
path that is not a leaf, the end point ist the first state that already has the
transition we trying to are add, and if we follow that transition we reach the next
active point.


.. seealso::

   [Ukkonen1995]_

   Ukkonen's suffix tree algorithm in plain English
   https://stackoverflow.com/questions/9452701/


.. automodule:: suffix_tree.ukkonen
