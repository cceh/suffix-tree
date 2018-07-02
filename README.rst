===========================
 A Generalized Suffix-Tree
===========================

This implementation:

- works with any python iterable, not just strings, if the items are hashable,
- values simplicity over speed,
- is a generalized suffix tree for sets of iterables ([Gusfield1997]_ §6.4),
- can convert the tree to .dot if the items convert to strings,

This implementation mostly follows [Gusfield1997]_ §6, with following differences:

- indices are 0-based (a Python convention),
- end indices point one element beyond the end (also a Python convention).

.. [Gusfield1997] Gusfield, Dan.  Algorithms on strings, trees, and sequences.
                  1997.  Cambridge University Press.
