# -*- coding: utf-8 -*-
#

""" Utilities for suffix tree. """

import functools
import logging
import subprocess
import sys

DEBUG     = 0
DEBUG_DOT = 0

@functools.total_ordering
class UniqueEndChar (object):
    """ A singleton object to signal end of sequence. """

    def __init__ (self, id_):
        self.id = id_

    def __str__ (self):
        return '$'

    def __lt__ (self, other):
        return False

min_debug_depth = -1
""" How deep we were in the stack when emitting the first debug message. """

def debug (msg, *args, **kwargs):
    """ Print a debug message to stderr. """

    if __debug__ and DEBUG:
        global min_debug_depth

        frame = sys._getframe (1)
        function_name = frame.f_code.co_name
        depth = 0
        while frame.f_back:
            frame = frame.f_back
            depth += 1
        if min_debug_depth == -1:
            min_debug_depth = depth
        depth -= min_debug_depth
        msg = ("%s%s: " % ('  ' * depth, function_name)) + msg
        logging.debug (msg, *args, **kwargs)


def debug_dot (tree, fn):
    """Write a dot and png file of the tree. """

    if __debug__ and DEBUG_DOT:
        dot = tree.to_dot ()
        debug ("writing dot: %s", fn)
        with open ('%s.dot' % fn, 'w') as tmp:
            tmp.write (dot)
        subprocess.check_output ("dot -Tpng %s.dot > %s.png" % (fn, fn), shell=True)


def is_debug ():
    """ Return True if debugging is on. """

    return __debug__ and DEBUG


class Pos (object):
    """ Represents a position in a string. """
    # pylint: disable=too-few-public-methods

    def __init__ (self, S, start = 0):
        assert 0 <= start <= len (S), "Pos: 0 <= %d <= %d" % (start, len (S))

        self.S     = S
        self.start = start

    def __str__ (self):
        return str (self.S[self.start])


class Path (object):
    """ A path in a suffix tree. """

    e = 0 # See: SPA, step 1.

    inf = -1 # the 'open ended' marker

    def __init__ (self, S, start = 0, end = None):
        if end is None:
            end = len (S)

        _end = end if end >= 0 else self.e
        assert 0 <= start <= _end <= len (S), "Path: 0 <= %d <= %d <= %d" % (start, end, len (S))

        self.S     = S
        self.start = start
        self._end  = end

    @property
    def end (self):
        """The end of the path.

        This is a calculated property because sometimes the end is 'open', which
        means that the end is automatically adjusted to be the end of the
        current phase.

        """
        return self._end if self._end != self.inf else self.e

    @end.setter
    def end (self, value):
        self._end = value

    @property
    def k (self):
        """The start of the path in Ukkonen's preferred notation"""

        return self.start

    @property
    def p (self):
        """The end of the path in Ukkonen's preferred notation"""

        return self.end - 1

    @property
    def i (self):
        """Another end of the path in Ukkonen's preferred notation"""

        return self.end - 1

    @classmethod
    def from_iterable (cls, iterable):
        """ Build a path froman iterable.

        Make the iterable immutable.
        """

        iterable = tuple (iterable)
        return Path (iterable, 0, len (iterable))

    def __str__ (self):
        return ' '.join (map (str, self.S[self.start:self.end]))

    def __len__ (self):
        return self.end - self.start

    def __lt__ (self, other):
        return self.S[self.start:self.end] < other.S[other.start:other.end]

    def __getitem__ (self, key):
        l = len (self)
        if isinstance (key, slice):
            start, stop, step = key.indices (l)
            if step != 1:
                raise TypeError
            return self.S[self.start + start:self.start + stop]
        if isinstance (key, int):
            if key < 0:
                key = len (self) + key
            if key >= l:
                raise IndexError ("key = %d, len () = %d" % (key, l))
            return self.S[self.start + key]
        raise TypeError ()

    def compare (self, path, offset = 0):
        """ Compare a path against another. """
        length = min (len (self), len (path)) - offset
        offset1 = self.start + offset
        offset2 = path.start + offset
        i = 0

        while i < length:
            if self.S[offset1 + i] != path.S[offset2 + i]:
                break
            i += 1
        debug ("Comparing %s == %s at offsets %d => common len: %d",
               str (self), str (path), offset, i)
        return i

    def ukko_str (self):
        """ Debug path in Ukkonen's notation """
        return 'k=%d p=%d k..p="%s"' % (self.k, self.p, self)
