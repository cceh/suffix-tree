.. _builders:

Builders
========

Which builder should I choose?

tl;dr: McCreight's

McCreight's builder is the fastest in this implementation.

Ukkonen's builder has no real advantage over McCreight's except if your symbols come
from a source that is slow relative to your CPU.  In that case Ukkonen's will do one
round after each character has arrived and have the tree always ready.

The naive builder is present only for educational purposes.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   builder/mccreight
   builder/ukkonen
   builder/naive
   builder/builder
