""" Common stuff for tests. """

from suffix_tree import naive
from suffix_tree import ukkonen
from suffix_tree import ukkonen_gusfield

BUILDERS = [
    ['naive', naive.Builder],
    ['ukkonen', ukkonen.Builder],
    ['gusfield', ukkonen_gusfield.Builder]
]
