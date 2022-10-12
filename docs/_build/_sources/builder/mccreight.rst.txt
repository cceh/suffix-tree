McCreight Builder
-----------------

.. |S|     replace:: `\bf S`
.. |i|     replace:: `i`
.. |i-1|   replace:: `i-1`
.. |Ti+1|  replace:: `T_{\imath+1}`
.. |Ti|    replace:: `T_{\imath}`
.. |Ti-1|  replace:: `T_{\imath-1}`
.. |Ti-2|  replace:: `T_{\imath-2}`
.. |suf|     replace:: `\suf{}`
.. |sufi|    replace:: `\suf{\imath}`
.. |sufi-1|  replace:: `\suf{\imath-1}`
.. |sufj|    replace:: `\suf{\jmath}`
.. |sufj-1|  replace:: `\suf{\jmath-1}`
.. |head|    replace:: `\head{}`
.. |headi|   replace:: `\head{\imath}`
.. |headi-1| replace:: `\head{\imath-1}`
.. |headi+1| replace:: `\head{\imath+1}`
.. |tail|    replace:: `\tail{}`
.. |taili|   replace:: `\tail{\imath}`
.. |taili-1| replace:: `\tail{\imath-1}`

.. |alpha| replace:: `\bs\alpha`
.. |beta|  replace:: `\bs\beta`
.. |gamma| replace:: `\bs\gamma`
.. |delta| replace:: `\bs\delta`
.. |rho|   replace:: `\bs\rho`
.. |chi|   replace:: `\bs\chi`
.. |x|     replace:: `\bf x`
.. |alphabeta|      replace:: `\bs{\alpha\beta}`
.. |alphabetagamma| replace:: `\bs{\alpha\beta\gamma}`
.. |chialpha|       replace:: `\bs{\chi\alpha}`
.. |chialphabeta|   replace:: `\bs{\chi\alpha\beta}`
.. |xdelta|         replace:: `\bf x\bs{\delta}`

The original and mathematically precise exposition (in blockquotes) is taken from the
excellent paper by McCreight [McCreight1976]_.  The comments are by me, trying to
understand the paper and translate it into language suited for mere mortals.

First McCreight defines:

    extension
        An extension of a string |alpha| is any string of which |alpha| is a prefix.

    locus
        The locus of a string is the node at the end of the path named by the string.
        The locus may not exist.

    extended locus
        The extended locus of a string |alpha| is the locus of the shortest extension of
        |alpha| whose locus is defined.  This may be the locus itself.

    contracted locus
        The contracted locus of a string |alpha| is the locus of the longest prefix of
        |alpha| whose locus is defined.  This may be the locus itself.

    |sufi|
        is the suffix of |S| beginning at character position |i| (beginning with
        1).

    |headi|
        |headi| is the longest prefix of |sufi| which is also a prefix of |sufj| for
        some `j < i`. Equivalently, |headi| is the longest prefix of |sufi| whose
        extended locus exists within the tree |Ti-1|.

    |taili|
        We define |taili| as `\suf{\imath}-\head{\imath}`.


The McCreight algorithm inserts all suffixes of |S| in order beginning with the longest.

In each step it inserts one suffix and creates one leaf node and at most one internal
node. For each internal node it will also create a suffix link in the next step.

To insert one suffix |suf|, we search the tree from the root until we get a mismatch. If
the mismatch happens on a node, we call that node the |head|. If the mismatch happens in
the middle of an edge, we split the edge and insert a new node, and call this new node
the |head|.  Then we append the |tail| to the |head|.  This procedure is slow because we
have to search starting from the root over and over again.

McCreight shows us how to warp from |headi-1| to |headi| in linear time using suffix
links and "rescanning". He demonstrates how suffix links can be set and exploited in
linear time:

    LEMMA 1. If |headi-1| can be written as |xdelta| for some character |x| and some
    (possibly empty) string |delta|, then |delta| is a prefix of |headi|.

    PROOF. By induction on |i|. Suppose `\head{\imath-1}=\bf x\bs{\delta}`.
    This means that there is a `j,\, j < i`, such that |xdelta| is a prefix both
    of |sufi-1| and of |sufj-1|. Thus |delta| is a prefix both of |sufi| and of |sufj|.
    Therefore by the definition of |head|, |delta| is a prefix of |headi|.
    `\quad\square`

Rephrasing that for mere mortals:

LEMMA 1:  If the locus of |headi-1| was not the root node, then in step |i| we
will find or create a node `c` that is on the path to |headi|.  Therefore in step
|i| it will be possible link to |headi-1| to `c` with a suffix link.

PROOF: at the end of step |i-1| the locus of |headi-1| can exists only if |sufi-1|
and some previous suffix |sufj-1| diverged at |xdelta|.  But then, in step |i|,
|sufi| must diverge with the previously inserted |sufj| at |delta|.

    To exploit this relationship, auxiliary links are added to our tree structure. From
    each nonterminal node which is the locus of |xdelta|, where |x| is a character and
    |delta| is a string, a suffix link is introduced pointing to the locus of |delta|.
    (Note that the locus of |delta| is never within the subtree rooted at the locus of
    |xdelta|.) […]  These links enable the algorithm in step |i| to do a short-cut
    search for the locus of |headi| beginning at the locus of |headi-1| which it has
    visited in the previous step.  The following semiformal presentation of the
    algorithm will prove by induction on |i| that

        `P1`: in tree |Ti| only the locus of |headi| could fail to have a valid
        suffix link, and that

        `P2`: in step |i| the algorithm visits the contracted locus of
        |headi| in |Ti-1|.

    Properties `P1` and `P2` clearly obtain if `i = 1`. Now suppose
    `i > 1`. In step |i| the algorithm does the following:

It follows a description of the algorithm:

Substep A. Let us write down |headi-1| as the concatenation of three strings
|chialphabeta|.  Let us also write down |headi| in the same way as |alphabetagamma|.

|chi| was the first character in |sufi-1| and is of no more importance when we insert
|sufi|.  |alpha| is that part of |sufi| we can short-circuit with a suffix link.  |beta|
is the next part of |sufi| which we can fast-forward by "rescanning".  |gamma| is the
third part of |sufi| for which we have to use slow "scanning". (And |taili| is the last
part of |sufi|.)

We go to the first ancestor-or-self of |headi-1| that has a suffix link.  (That would be
|chialpha|.)  We then follow the suffix link to the locus of |alpha| and call that node
`c`.  Goto substep B.

Note that if we set the suffix link of root to root itself we don't have to special case
an empty |alpha|.

    Substep A. First the algorithm identifies three strings |chi|, |alpha|, and |beta|,
    with the following properties:

      (1) |headi-1| can be represented as |chialphabeta|.

      (2) If the contracted locus of |headi-1| in |Ti-2| is not the root, it is the
          locus of |chialpha|. Otherwise |alpha| is empty.

      (3) |chi| is a string of at most one character which is empty only if |headi+1| is
          empty.

    Lemma 1 guarantees that |headi| may be represented as |alphabetagamma| for some
    (possibly empty) string |gamma|. The algorithm now chooses the appropriate case of
    the following two:

      - |alpha| empty: The algorithm calls the root node `c` and goes to substep
        B.  Note that `c` is defined as the locus of |alpha|.

      - |alpha| nonempty: By definition, the locus of |chialpha| must have existed in
        the tree |Ti-2|. By `P1` the suffix link of that (nonterminal) locus node
        must be defined in tree |Ti-1|, since the node itself must have been constructed
        before step |i-1|. By `P2` the algorithm visited that node in step
        |i-1|. The algorithm follows its suffix link to a nonterminal node
        called `c` and goes to substep B. Note that `c` is defined as the
        locus of |alpha|.

Substep B.  This is the second time-saving trick devised by McCreight.

From the node `c`, the locus of |alpha|, we search the locus of |alphabeta|.  We
save time by what McCreight calls "rescanning":  We already know that all characters in
|beta| must match so we need to examine only the first character of each edge (to decide
which edge to follow).

If we overshoot the length of |beta| we have to split the edge as usual.  When found or
created, we call that node `d`.  Goto Substep C.  Note that if |gamma| is not
empty the edge will already be split.

    Substep B.  This is called "rescanning," and is the key idea of algorithm M.  Since
    |alphabetagamma| is defined as |headi|, by the definition of |head| we know that the
    extended locus of |alphabeta| exists in the tree |Ti-1|.  This means that there is a
    sequence of arcs downward from node `c` (the locus of |alpha|) which spells
    out some extension of |beta|. To rescan |beta| the algorithm finds the child arc
    |rho| of `c` which begins with the first character of |beta| and leads to a
    node which we shall call `f`.  It compares the *lengths* of |beta| and |rho|.
    If |beta| is longer, then a recursive rescan of `\beta - \rho` is begun from
    node `f`.  If |beta| is the same length or shorter, then |beta| is a prefix of
    |rho|, the algorithm has found the extended locus of |alphabeta| and the rescan is
    complete.  It has been accomplished in time linear in the number of nodes
    encountered.  A new nonterminal node is constructed to be the locus of |alphabeta|
    if one does not already exist.  The algorithm calls `d` the locus of
    |alphabeta| and goes to substep C. (Note that substep B constructs a new node to be
    the locus of |alphabeta| only if |gamma| is empty.)

Substep C.  Back to the naive algorithm.

First we set the suffix link on |chialphabeta| to point to |alphabeta|.  Then from the
locus of |alphabeta| we scan the slow way to |alphabetagamma| comparing each character
until we get a mismatch.  If the mismatch happens on a node, we call that node |headi|.
If the mismatch happens in the middle of an edge, we split the edge and insert a new
node, and call the new node |headi|.  Then we append the unmatched rest |taili| to
|headi|.  Increment |i| and goto Substep A.

    Substep C. This is called "scanning." If the suffix link of the locus of
    |chialphabeta| is currently undefined, the algorithm first defines that link to
    point to node `d`. This and inductive hypothesis establish the truth of
    `P1` in |Ti|. Then the algorithm begins searching from node `d` deeper
    into the tree to find the extended locus of |alphabetagamma|. The major difference
    between scanning and rescanning is that in rescanning the length of |beta| is known
    beforehand (because it has already been scanned), while in scanning the length of
    |gamma| is not known beforehand. Thus the algorithm must travel downward into the
    tree in response to the characters of |taili| (of which |gamma| is a prefix) one by
    one from left to right. When the algorithm "falls out of the tree" (as constraint
    `S1` guarantees that it must), it has found the extended locus of
    |alphabetagamma|. The last node of |Ti-1| encountered in this downward trek of
    rescanning and scanning is the contracted locus of |headi| in |Ti-1| ; this
    establishes the truth of `P2`. A new nonterminal node is constructed to be the
    locus of |alphabetagamma| if one does not already exist.  Finally a new arc labeled
    |taili|, is constructed from the locus of |alphabetagamma| to a new terminal node.
    Step |i| is now finished.

..  seealso::

   [McCreight1976]_

   https://www.cs.helsinki.fi/u/tpkarkka/opetus/10s/spa/lectures.pdf


.. automodule:: suffix_tree.mccreight
