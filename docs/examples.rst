Examples
========

Install:

.. code-block:: shell

   $ pip install suffix-tree

Import the library:

.. code-block:: python

   >>> from suffix_tree import Tree

Initialize a tree and then add sequences of symbols:

.. code-block:: python

   >>> tree = Tree()
   >>> tree.add(1, "xabxac")
   >>> tree.add(2, "awyawxawxz")

Or initialize from a dictionary of sequences in one step:

.. code-block:: python

   >>> tree = Tree({1: "xabxac", 2: "awyawxawxz"})

Query if a sequence exists in the tree:

.. code-block:: python

   >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
   >>> tree.find("abx")
   True
   >>> tree.find("awx")
   True
   >>> tree.find("abc")
   False

Query if a sequence exists in a sequence:

.. code-block:: python

   >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
   >>> tree.find_id("A", "abx")
   True
   >>> tree.find_id("B", "abx")
   False
   >>> tree.find_id("B", "awx")
   True

Enumerate all hits:

.. code-block:: python

   >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
   >>> for id_, path in tree.find_all("xa"):
   ...     print(id_, ":", str(path))
   ...
   A : x a b x a c $
   A : x a c $
   B : x a w x z $
   >>> tree.find_all("abc")
   []

Sequences can contain all kinds of hashable objects:

.. code-block:: python

   >>> tree = Tree()
   >>> b = True
   >>> i = 10
   >>> s = "hello, world"
   >>> t = (1, 2, 3)
   >>> f = frozenset(t)
   >>> tree.add(1, [b, i, f, s, t])
   >>> tree.add(2, [t, s, f, i, b])
   >>> tree.find([b, i, f, s, t])
   True
   >>> tree.find([s, f, i])
   True
   >>> tree.find([i, s])
   False


Find common substrings:

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

Find maximal repeats:

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
