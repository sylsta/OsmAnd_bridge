# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'OsmAnd bridge'
copyright = '2022-2025, Sylvain Théry - CNRS - UMR 5281 ART-Dev'
author = 'Sylvain Théry - CNRS - UMR 5281 ART-Dev'
release = '2'

# # -- General configuration ---------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
#
# extensions = []
#
# templates_path = ['_templates']
# exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
#
#
#
# # -- Options for HTML output -------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
#
# # html_theme = 'alabaster'
# html_theme = 'sphinx_rtd_theme'
# # html_static_path = ['_static']
#
# # Reference figures
# numfig = True
#
#
# master_doc = 'index'


extensions = [
    "myst_parser",       # Pour le support Markdown
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

# Configuration MyST (Markdown)
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

# Internationalisation
locale_dirs = ["locale/"]
gettext_compact = False
language = "index.md"
languages = {
    "index.md": "English",
    "fr": "Français",
}

# Thème (optionnel, RTD utilise son thème par défaut)
html_theme = "sphinx_rtd_theme"
