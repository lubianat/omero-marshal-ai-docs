# OMERO Marshal AI Docs

Unofficial, AI-generated documentation that explains how `omero-marshal` turns OMERO model objects into JSON-friendly dictionaries and back again. The goal is to give engineering teams a concise companion to the upstream `omero-marshal` project by describing what each codec includes, what schema versions are supported, and how to extend the library safely.

## What this repository contains
- ReStructuredText sources under the project root (see `index.rst`) that mirror the structure of the upstream docs.
- Topical guides such as `quickstart.rst`, `usage.rst`, `codecs.rst`, and `developer.rst` covering common workflows, codec behaviour, and extension points.
- Terminology references in `glossary.rst` and practical examples in `examples.rst` and `use_cases.rst`.
- A narrative design note in `design_notes.rst` explaining how codecs are
  organized, what patterns are used, and how to extend them safely.

## How to build the docs locally
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies: `pip install -r requirements.txt`.
3. Build HTML: `sphinx-build -b html . _build/html`.
4. Open `_build/html/index.html` in your browser.

## Offline copies
Read the Docs is configured to publish downloadable formats (PDF, EPUB, and
HTML zip). Use the **Downloads** menu on the RTD build to fetch an offline copy
after each build completes.

## Changelog
See `CHANGELOG.md` for release summaries. This repository publishes
documentation-only releases; always verify behaviour against upstream
`omero-marshal`.

## Relationship to upstream
This repository is not affiliated with or endorsed by the OMERO or OME teams. Always check behaviour against the official [`omero-marshal`](https://github.com/ome/omero-marshal) codebase and tests before using these notes in production.

## License
This documentation is available under the terms of the MIT License (see `LICENSE`).
