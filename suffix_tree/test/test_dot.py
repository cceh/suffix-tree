""" Test the to_dot ()  method. """

# pylint: disable=missing-docstring

import unittest

from suffix_tree import Tree

class TestFind (unittest.TestCase):

    def test_to_dot (self):
        # tree = Tree ({ 'A' : 'aaaaa' })
        # tree = Tree ({ 'A' : 'ababcabcdabdeaef' })
        tree = Tree ({ 'A' : 'xabxac', 'B' : 'awyawxawxz' })
        dot = tree.to_dot ()
        with open ('/tmp/suffix_tree.dot', 'w') as tmp:
            tmp.write (dot)
        self.assertTrue (1 == 1) # just test that it doesn't bomb

if __name__ == '__main__':
    unittest.main ()
