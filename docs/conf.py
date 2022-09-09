"""Sphinx configuration."""
project = "Elastica Pipelines"
author = "ElasticaDev"
copyright = "2022, ElasticaDev"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"

# Include Python intersphinx mapping to prevent failures when standard library types
# are reference
extensions += ["sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
