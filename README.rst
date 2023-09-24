===========================
 A Generalized Suffix Tree
===========================

.. |py39| image:: docs/_images/badge-py39.svg

.. |py310| image:: docs/_images/badge-py310.svg

.. |py311| image:: docs/_images/badge-py311.svg

.. |py312| image:: docs/_images/badge-py312.svg

.. |pypy39| image:: docs/_images/badge-pypy39.svg

.. |coverage| image:: docs/_images/badge-coverage.svg

|py39| |py310| |py311| |py312| |pypy39| |coverage|

A Generalized Suffix Tree for any Python sequence, with Lowest Common Ancestor
retrieval.

.. code-block:: shell

   pip install suffix-tree

.. code-block:: python

   >>> from suffix_tree import Tree

   >>> tree = Tree({"A": "xabxac"})
   >>> tree.find("abx")
   True
   >>> tree.find("abc")
   False


This suffix tree:

- works with any Python sequence, not just strings, if the items are hashable,
- is a generalized suffix tree for sets of sequences,
- is implemented in pure Python,
- builds the tree in time proportional to the length of the input,
- does constant-time Lowest Common Ancestor retrieval.

Being implemented in Python this tree is not very fast nor memory efficient.  The
building of the tree takes time proportional to the length of the string of symbols.
The query time is proportional to the length of the query string.

To get the best performance turn the python optimizer on: python -O.

Documentation: https://cceh.github.io/suffix-tree/

PyPi: https://pypi.org/project/suffix-tree/


Usage examples:
===============

.. code-block:: python

   >>> from suffix_tree import Tree
   >>> tree = Tree()
   >>> tree.add(1, "xabxac")
   >>> tree.add(2, "awyawxawxz")
   >>> tree.find("abx")
   True
   >>> tree.find("awx")
   True
   >>> tree.find("abc")
   False

.. code-block:: python

   >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
   >>> tree.find_id("A", "abx")
   True
   >>> tree.find_id("B", "abx")
   False
   >>> tree.find_id("B", "awx")
   True

.. code-block:: python

   >>> tree = Tree(
   ...     {
   ...         "A": "sandollar",
   ...         "B": "sandlot",
   ...         "C": "handler",
   ...         "D": "grand",
   ...         "E": "pantry",
   ...     }
   ... )
   >>> for k, length, path in tree.common_substrings():
   ...     print(k, length, path)
   ...
   2 4 s a n d
   3 3 a n d
   4 3 a n d
   5 2 a n

.. code-block:: python

   >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
   >>> for C, path in sorted(tree.maximal_repeats()):
   ...     print(C, path)
   ...
   1 a w
   1 a w x
   2 a
   2 x
   2 x a
