""" Test the find ()  method. """

# pylint: disable=missing-docstring

import unittest
from parameterized import parameterized

from suffix_tree import Tree
from .tests import BUILDERS

class TestFind (unittest.TestCase):

    @parameterized.expand(BUILDERS)
    def test_find_1 (self, _, builder):
        # Gusfield1997 Figure 5.1 Page  91
        tree = Tree ({ 'A' : 'xabxac' }, builder = builder)
        self.assertTrue  (tree.find ('x'))
        self.assertTrue  (tree.find ('xa'))
        self.assertTrue  (tree.find ('xab'))
        self.assertTrue  (tree.find ('xabx'))
        self.assertTrue  (tree.find ('xabxa'))
        self.assertTrue  (tree.find ('xabxac'))

        self.assertTrue  (tree.find ('abxac'))
        self.assertTrue  (tree.find ('bxac'))
        self.assertTrue  (tree.find ('xac'))
        self.assertTrue  (tree.find ('ac'))
        self.assertTrue  (tree.find ('c'))

        self.assertFalse (tree.find ('d'))
        self.assertFalse (tree.find ('xx'))
        self.assertFalse (tree.find ('xabxaa'))

    @parameterized.expand(BUILDERS)
    def test_find_2 (self, _, builder):
        # Gusfield1997 Figure 5.2 Page  92
        tree = Tree ({ 'A' : 'awyawxawxz' }, builder = builder)
        self.assertTrue  (tree.find ('awx'))
        self.assertTrue  (tree.find ('awy'))
        self.assertFalse (tree.find ('awz'))

    @parameterized.expand(BUILDERS)
    def test_find_3 (self, _, builder):
        # Gusfield1997 Figure 7.1 Page 129
        tree = Tree ({ 'A' : 'xyxaxaxa' }, builder = builder)
        self.assertTrue  (tree.find ('xyxaxaxa'))
        self.assertTrue  (tree.find ('xax'))
        self.assertTrue  (tree.find ('axa'))
        self.assertFalse (tree.find ('ay'))

    @parameterized.expand(BUILDERS)
    def test_find_4 (self, _, builder):
        tree = Tree ({
            'A' : ('232 020b 092 093 039 061 102 135 098 099 '
                   '039 040 039 040 044 141 140 098').split (),
            'B' : '097 098 039 040 041 129 043'.split (),
            'C' : ('097 098 039 040 020a 022 023 097 095 094 098 '
                   '043 044 112 039 020b 039 098').split (),
        }, builder = builder)
        self.assertTrue  (tree.find ('039 040 041'.split ()))
        self.assertTrue  (tree.find ('039 040 039 040'.split ()))
        self.assertTrue  (tree.find ('020a 022 023'.split ()))
        self.assertTrue  (tree.find ('232 020b 092'.split ()))
        self.assertTrue  (tree.find ('097 098 039 040'.split ()))
        self.assertTrue  (tree.find ('141 140 098'.split ()))
        self.assertFalse (tree.find ('039 040 042'.split ()))

    @parameterized.expand(BUILDERS)
    def test_find_5 (self, _, builder):
        tree = Tree ({
            'A' : 'aaaaa',
            'B' : 'bbbb',
        }, builder = builder)
        self.assertEqual (len (tree.find_all ('a')), 5)
        self.assertEqual (len (tree.find_all ('b')), 4)

    @parameterized.expand(BUILDERS)
    def test_find_6 (self, _, builder):
        tree = Tree ({
            'A' : 'a',
            'B' : 'ab',
            'C' : 'abc',
            'D' : 'abcd',
            'E' : 'abcde',
        }, builder = builder)
        self.assertEqual (len (tree.find_all ('abcde')), 1)
        self.assertEqual (len (tree.find_all ('abcd')),  2)
        self.assertEqual (len (tree.find_all ('abc')),   3)
        self.assertEqual (len (tree.find_all ('ab')),    4)
        self.assertEqual (len (tree.find_all ('a')),     5)

    @parameterized.expand(BUILDERS)
    def test_find_7 (self, _, builder):
        tree = Tree ({
            'A' : 'abcde',
            'B' : 'bcde',
            'C' : 'cde',
            'D' : 'de',
            'E' : 'e',
        }, builder = builder)
        self.assertEqual (len (tree.find_all ('abcde')), 1)
        self.assertEqual (len (tree.find_all ('bcde')),  2)
        self.assertEqual (len (tree.find_all ('cde')),   3)
        self.assertEqual (len (tree.find_all ('de')),    4)
        self.assertEqual (len (tree.find_all ('e')),     5)

if __name__ == '__main__':
    unittest.main ()
