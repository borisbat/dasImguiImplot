# -*- coding: utf-8 -*-
#
# dasImguiImplot documentation build configuration file.
#
# Vendored from dasImgui/doc/source/conf.py (itself vendored from daslang).
# HTML-only deploy. Diff and reconcile against dasImgui / daslang upstream when
# the daslang Sphinx domain evolves.

import sys
import os
import time

# Make the vendored `daslang` Sphinx domain importable.
sys.path.insert(0, os.path.abspath('.'))

extensions = ['daslang', 'tutorial_video', 'sphinx.ext.intersphinx']

# Resolve cross-refs to daslang core (JsonValue, float2, ...) against the
# published daslang documentation. Sphinx fetches objects.inv at build time.
intersphinx_mapping = {
    'daslang': ('https://daslang.io/doc/', None),
}
intersphinx_disabled_reftypes = []

templates_path = ['_templates']

suppress_warnings = ['toctree.not_included']

source_suffix = '.rst'

master_doc = 'index'

project = u'dasImguiImplot documentation'
copyright = '2026-%s, Gaijin Entertainment' % time.strftime('%Y')
author = u'Boris Batkin'

version = u'0.16'
release = u'0.16'

language = 'en'

# Intermediate files used by implot2rst — not standalone documentation pages.
exclude_patterns = ['stdlib/generated/detail', 'stdlib/handmade']

pygments_style = 'sphinx'
highlight_language = 'none'

todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'style_nav_header_background': '#0d0c0a',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'titles_only': False,
}
html_logo = '_static/forge-logo.svg'
html_favicon = 'daslang-favicon.svg'
html_static_path = ['_static']
# sphinx_rtd_theme reads this and adds an "Edit on GitHub" link to every page header.
html_context = {
    'display_github': True,
    'github_user': 'borisbat',
    'github_repo': 'dasImguiImplot',
    'github_version': 'master',
    'conf_py_path': '/doc/source/',
}
# Forge dark retoken — matches daslang.io/doc/ visually. Vendored from
# dasImgui's doc/source/_static/custom.css; reconcile against upstream when
# the daslang docs theme evolves.
html_css_files = ['custom.css', 'custom-patch.css']

html_js_files = ['sidebar.js']

htmlhelp_basename = 'dasimguiimplot_doc'
