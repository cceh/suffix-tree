.. _performance:

Performance
===========

Both McCreight's and Ukkonen's algorithms build the suffix tree in `\mathcal O(\lvert
S\rvert)` time, with `\lvert S\rvert` being the length of the input sequence.  This may
not be strictly true for this implementation, especially for large alphabets, since the
library uses Python dictionaries to store symbols and those dictionaries are not linear.



Python 3.10.7
-------------

.. image:: _images/graph_time_complexity.png
   :width: 100%

PyPy 7.3.9
----------

.. image:: _images/graph_time_complexity_pypy38.png
   :width: 100%
