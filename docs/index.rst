suffix-tree Documentation
=========================

**suffix-tree** is a Generalized Suffix Tree for any Python sequence, with Lowest Common
Ancestor retrieval.  It:

- works with any Python sequence, not just strings, if the items are hashable,
- is a generalized suffix tree for sets of sequences,
- is implemented in pure Python,
- builds the tree in linear time with Ukkonen's algorithm,
- does constant-time Lowest Common Ancestor retrieval.

Three different builders have been implemented:

- one that follows Ukkonen's original paper ([Ukkonen1995]_),
- one that follows Gusfield's variant ([Gusfield1997]_),
- and one simple naive algorithm.

Being implemented in Python this tree is not very fast nor memory efficient.  The
building of the tree takes time proportional to the length of the string of symbols.
The query time is proportional to the length of the query string.  You can get a rough
idea of the performance under: :ref:`Performance <time-complexity>`.

To get the best performance run it with :program:`python -O`.

Install it from PyPi: https://pypi.org/project/suffix-tree/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   tree
   node
   lca
   builder
   util
   performance
   references


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
