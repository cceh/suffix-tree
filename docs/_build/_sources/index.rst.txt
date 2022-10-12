suffix-tree Documentation
=========================

**suffix-tree** is a Generalized Suffix Tree for any Python sequence, with Lowest Common
Ancestor retrieval.  It:

- works with any Python sequence, not just strings, if the items are hashable,
- is a generalized suffix tree for sets of sequences,
- is implemented in pure Python,
- builds the tree in time proportional to the length of the input,
- does constant-time Lowest Common Ancestor retrieval.

Three different :ref:`builders <builders>` have been implemented:

- one that uses McCreight's `\mathcal O(\lvert S\rvert)` algorithm ([McCreight1976]_),
- one that uses Ukkonen's `\mathcal O(\lvert S\rvert)` algorithm ([Ukkonen1995]_),
- and one that uses a naive (non linear time) algorithm.

Being implemented in Python this tree is not very fast nor memory efficient.  The
building of the tree takes time proportional to the length of the string of symbols.
The query time is proportional to the length of the query string.  You can get a rough
idea of the performance under: :ref:`Performance <performance>`.

To get the best performance turn the python optimizer on with :program:`python -O`.

Install it from PyPi: https://pypi.org/project/suffix-tree/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   tree
   node
   lca
   builders
   util
   performance
   references


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
