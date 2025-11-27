"""Sphinx configuration for the OMERO Marshal documentation.

The configuration is intentionally lightweight so it can build on Read the
Docs without pulling in the full OMERO stack. No package imports are needed.
"""

project = "OMERO Marshal (Unofficial AI Guide)"
author = "Open Microscopy Environment and contributors — AI-generated companion"
release = "0.9.1.dev0"
version = release

extensions = [
    "sphinx.ext.autosectionlabel",
]

# Prefix document path to section labels so cross-file links stay unique.
autosectionlabel_prefix_document = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
