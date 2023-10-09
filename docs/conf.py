# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from suffix_tree import _version

# -- Project information -----------------------------------------------------

project = "suffix-tree"
copyright = "2018-22, Marcello Perathoner"
author = "Marcello Perathoner"

# The full version, including alpha/beta/rc tags
release = _version.VERSION

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
]

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": True,
    "exclude-members": "__weakref__, debug_dot",
}

mathjax3_config = {
    "tex": {
        "macros": {
            "bs": [r"\boldsymbol"],
            "suf": [r"\mathrm{\bf suf}_{\mkern 1mu\bs{#1}}", 1],
            "head": [r"\mathrm{\bf head}_{\mkern 1mu\bs{#1}}", 1],
            "tail": [r"\mathrm{\bf tail}_{\mkern 1mu\bs{#1}}", 1],
        }
    }
}


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "display_version": False,
    "navigation_depth": 3,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "logo-cceh-white.svg"
html_favicon = "favicon-cceh-blue.png"
html_css_files = ["custom.css"]

default_role = "math"
modindex_common_prefix = ["suffix_tree."]
add_module_names = False
