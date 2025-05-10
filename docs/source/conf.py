# Configuration file for the Sphinx documentation builder.
import os
import sys
from datetime import datetime

# Добавляем путь к проекту для autodoc
sys.path.insert(0, os.path.abspath('../../links_generator'))

os.environ['GENERATING_DOCS'] = '1'
# -- Project information -----------------------------------------------------
project = 'links_generator'
copyright = f'{datetime.now().year}, mrandrew30'
author = 'mrandrew30'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

# Настройки для autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_mock_imports = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Язык документации
language = 'ru'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
}

# Отключаем автоматическое создание заголовков
autosummary_generate = False

# Изменяем заголовки
rst_prolog = """
.. role:: python(code)
   :language: python
"""
