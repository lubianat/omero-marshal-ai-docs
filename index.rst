OMERO Marshal Documentation
===========================

Guides for bioinformaticians who need to turn OMERO model objects into
portable, JSON-friendly dictionaries and back again. The notes below focus on
how the codecs work, what gets included, and how to extend them safely.

.. warning::
   This is an **unofficial, AI-generated companion** to the upstream
   `omero-marshal <https://github.com/ome/omero-marshal>`_ project. Always
   validate behaviour against the upstream code and tests before relying on
   these docs in production.

.. note::
   Jargon is linked to the :doc:`glossary` the first time it appears (for
   example :term:`Marshalling` or :term:`Codec`) so you can jump straight to
   definitions without losing your place.

.. toctree::
   :maxdepth: 2

   quickstart
   overview
   usage
   tutorials
   architecture
   jsonld
   codecs
   advanced
   developer
   faq
   use_cases
   examples
   glossary
