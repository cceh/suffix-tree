===========================
 A Generalized Suffix Tree
===========================

A Generalized Suffix Tree for any Python iterable, with Lowest Common Ancestor
retrieval.

.. code-block:: shell

   pip install suffix-tree

.. code-block:: python

   from suffix_tree import Tree

   >>> tree = Tree ({ 'A' : 'xabxac' })
   >>> tree.find ('abx')
   True
   >>> tree.find ('abc')
   False


This suffix tree:

- works with any Python iterable, not just strings, if the items are hashable,
- is a generalized suffix tree for sets of iterables,
- uses Ukkonen's algorithm to build the tree in linear time,
- does constant-time Lowest Common Ancestor retrieval,
- outputs the tree as GraphViz .dot file.

Three different builders have been implemented:

- one that follows Ukkonen's original paper ([Ukkonen1995]_),
- one that follows Gusfield's variant ([Gusfield1997]_),
- and one simple naive algorithm.


PyPi: https://pypi.org/project/suffix-tree/

.. [Ukkonen1995] Ukkonen, Esko.  On-line construction of suffix trees.  1995.
                 Algorithmica 14:249-60.  http://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf

.. [Gusfield1997] Gusfield, Dan.  Algorithms on strings, trees, and sequences.
                  1997.  Cambridge University Press.
