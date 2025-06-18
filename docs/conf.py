# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
project = 'Fishing Line Material Properties Analysis'
copyright = '2025, Nanosystems Lab'
author = 'Nanosystems Lab'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    # 'sphinx_argparse',  # Temporarily commented out
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output ------------------------------------------------
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

# PyData Sphinx Theme configuration
html_theme_options = {
    # Header links
    "github_url": "https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis",
    "use_edit_page_button": True,
    
    # Navigation and TOC
    "show_toc_level": 2,
    "navbar_align": "left",
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    
    # Site navigation
    "external_links": [
        {
            "name": "Nanosystems Lab",
            "url": "https://github.com/nanosystemslab"
        }
    ],
    
    # Footer
    "footer_start": ["copyright"],
    "footer_end": ["sphinx-version"],
    
    # Search
    "search_bar_text": "Search the docs...",
    
    # Page elements
    "show_prev_next": True,
}

# Configure edit button
html_context = {
    "github_user": "nanosystemslab",
    "github_repo": "Fishing_Line_Material_Properties_Analysis",
    "github_version": "main",
    "doc_path": "docs/",
}

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# -- Options for intersphinx extension --------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# -- Options for Napoleon extension -----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
