""" Test the find ()  method. """

# pylint: disable=missing-docstring

import unittest

from suffix_tree import Tree

class TestFind (unittest.TestCase):

    def test_find_1 (self):
        tree = Tree ({ 'A' : 'xabxac' })      # Gusfield1997 Figure 5.1 Page  91
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

    def test_find_2 (self):
        tree = Tree ({ 'A' : 'awyawxawxz' })    # Gusfield1997 Figure 5.2 Page  92
        self.assertTrue  (tree.find ('awx'))
        self.assertTrue  (tree.find ('awy'))
        self.assertFalse (tree.find ('awz'))

    def test_find_3 (self):
        tree = Tree ({ 'A' : 'xyxaxaxa' })      # Gusfield1997 Figure 7.1 Page 129
        self.assertTrue  (tree.find ('xyxaxaxa'))
        self.assertTrue  (tree.find ('xax'))
        self.assertTrue  (tree.find ('axa'))
        self.assertFalse (tree.find ('ay'))

    def test_find_4 (self):
        tree = Tree ({
            'A' : ('232 020b 092 093 039 061 102 135 098 099 '
                   '039 040 039 040 044 141 140 098').split (),
            'B' : '097 098 039 040 041 129 043'.split (),
            'C' : ('097 098 039 040 020a 022 023 097 095 094 098 '
                   '043 044 112 039 020b 039 098').split (),
        })
        self.assertTrue  (tree.find ('039 040 041'.split ()))
        self.assertTrue  (tree.find ('039 040 039 040'.split ()))
        self.assertTrue  (tree.find ('020a 022 023'.split ()))
        self.assertFalse (tree.find ('039 040 042'.split ()))

    def test_find_5 (self):
        tree = Tree ({ 'A' : 'aaaaa' })
        a = tree.find_all ('a')
        self.assertEqual (len (a), 5)

if __name__ == '__main__':
    unittest.main ()
