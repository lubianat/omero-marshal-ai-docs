JSON-LD and Contexts
====================

.. note::
   Terms such as :term:`@context`, :term:`@type`, and :term:`Marshalling` link
   to the :doc:`glossary`.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Why JSON-LD is used
-------------------

- It makes payloads self-describing: keys resolve to a specific OME schema
  version, and the ``omero`` prefix cleanly separates OMERO extensions.
- It prevents silent drift when schemas evolve; a consumer can choose the
  right decoder based on the fully qualified :term:`@type`.
- Downstream tools that understand JSON-LD can treat the payload as linked
  data, but regular JSON consumers can still parse it as normal dictionaries.

The default context
-------------------

Encoders add this ``@context`` unless you set ``include_context=False``:

.. code-block:: json

    {
      "@context": {
        "@vocab": "http://www.openmicroscopy.org/Schemas/OME/2016-06#",
        "omero": "http://www.openmicroscopy.org/Schemas/OMERO/2016-06#"
      },
      "@type": "Image",
      "Name": "example"
    }

- ``@vocab`` sets the default namespace for unprefixed keys (e.g. ``Name``).
- ``omero`` introduces the prefix for OMERO-specific extensions
  (e.g. ``omero:Permissions``).
- ``@type`` identifies the schema-qualified type of the object.

When to keep or drop the context
--------------------------------

- Keep it on top-level payloads that cross service boundaries or get stored
  for later analysis; it makes the data self-contained.
- Drop it for nested objects inside the same payload to reduce repetition:
  ``encode(..., include_context=False)``.

Nested example (top-level only)
-------------------------------

.. code-block:: json

    {
      "@context": {
        "@vocab": "http://www.openmicroscopy.org/Schemas/OME/2016-06#",
        "omero": "http://www.openmicroscopy.org/Schemas/OMERO/2016-06#"
      },
      "@type": "Project",
      "Name": "Cell atlas",
      "Datasets": [
        {
          "@type": "Dataset",
          "@id": 1,
          "Name": "Plates batch A",
          "Images": [
            {
              "@type": "Image",
              "@id": 10,
              "Name": "plateA_field01"
            }
          ]
        }
      ]
    }

Only the outer ``Project`` carries ``@context``; nested datasets/images rely on
it implicitly. Decoders still succeed because ``@type`` is fully qualified by
the shared vocabulary.

Adapting contexts
-----------------

Most users can keep the defaults. If you do need to adapt the context (for
example to inline custom prefixes or to emit a different ``@vocab``), wrap the
encoded payload and modify ``@context`` before serialising. Be sure to keep
``@type`` untouched so decoders can still pick the right codec.

Working with JSON-LD tools
--------------------------

- You can feed the payload to JSON-LD processors (``pyld`` in Python) to
  perform compaction or expansion if your downstream stack benefits from it.
- Compaction using the emitted ``@context`` shortens URIs, while expansion
  turns ``@type`` and keys into full IRIs—useful for graph databases.
- Regardless of tooling, marshalled payloads remain valid plain JSON for
  consumers that ignore JSON-LD semantics.

Flow of JSON-LD-aware marshalling
---------------------------------

.. code-block:: text

   OMERO model object
        |  (encoder attaches @context, @type)
        v
   JSON-LD dictionary
        |  (json.dumps / HTTP / storage)
        v
   JSON-LD payload in transit
        |  (json.loads)
        v
   Decoder reads @type, rebuilds OMERO model object
         |
         +--> Optional: JSON-LD tooling compacts/expands keys while preserving links
