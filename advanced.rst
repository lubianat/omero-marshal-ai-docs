Advanced Topics
===============

.. note::
   Key terms such as :term:`Marshalling`, :term:`Codec`, :term:`Unit`,
   :term:`RType`, and :term:`@context` link to the :doc:`glossary`.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Performance and payload size
----------------------------

- **Load only what you need**: Encoders respect ``isLoaded()`` and collection
  sizes. Fetch or load links explicitly (annotations, pixels, shapes, SPW
  children) instead of calling ``.load()`` indiscriminately.
- **Trim contexts on nested objects**: Use ``include_context=False`` when
  nesting many objects; keep the top-level context only.
- **Avoid giant ROIs**: For images with thousands of shapes, consider slicing
  ROIs or filtering shapes by channel/Z/T before encoding.

Schema-aware pipelines
----------------------

- **Mixed schema archives**: If you store long-lived JSON snapshots, always
  keep ``@context`` and ``@type`` so consumers can decode with the matching
  schema. Avoid rewriting snapshots across schema versions.
- **Forward compatibility**: When adding codecs for new OMERO/OME releases,
  keep older codecs intact and register new ones under the new schema URIs.
  Downstream consumers can branch on ``@type``.

Transforms and geometry
-----------------------

- **2015-01** uses SVG strings parsed by the legacy ``AffineTransformI`` shim;
  malformed strings are skipped silently. Validate transforms upstream if they
  matter to your workflow.
- **2016-06** stores numeric matrix fields and omits empty transforms
  altogether. When you need identity transforms preserved, ensure coefficients
  are set explicitly.

Units and numeric fidelity
--------------------------

- Encoders emit units as structured dicts; decoders rebuild the correct OMERO
  unit class. Keep unit metadata intact when post-processing JSON so round
  trips stay lossless.
- Unsupported unit classes raise exceptions during encoding; add explicit
  handling when introducing new unit types.

Permissions and security
------------------------

- ``omero:details`` includes owner, group, permissions, and external info.
  Strip or rewrite them if your consumer should not inherit access control
  settings.
- ``PermissionsDecoder`` reconstructs restrictions from booleans; ensure your
  JSON source is trusted or validate before decoding.

Error handling patterns
-----------------------

- ``get_encoder`` / ``get_decoder`` return ``None`` and log a warning for
  unknown types. Check for ``None`` and fail loudly in upstream code.
- Invalid OMERO versions raise during import when computing
  ``SCHEMA_VERSION``; catch and surface early in CLI tools or services.

Validation checklist for consumers
----------------------------------

- Ensure ``@context`` is present on top-level payloads crossing boundaries.
- Assert ``@type`` matches the expected schema URI before decoding.
- Verify critical numeric fields (units, wavelengths, colours) after decoding.
- If applying permissions, confirm the source is trusted or strip
  ``omero:details`` first.
- Confirm expected links are loaded/encoded (annotations, shapes, channels)
  before assuming they exist.

Measuring and profiling
-----------------------

- Time encoding/decoding for large ROIs or SPW graphs; consider batching or
  filtering if latency is high.
- Profile with ``cProfile`` to locate hotspots (often channel/shape traversal
  when many links are loaded).
- Keep payload sizes in mind: thousands of shapes or channels can balloon JSON
  size; gzip over the wire helps.

Contract invariants
-------------------

- ``@type`` must always be present and schema-qualified; do not rewrite it.
- Units must carry ``Unit`` and ``Value``; dropping either makes decoding
  ambiguous.
- Colours stay in signed 32-bit RGBA format; changing representation breaks
  round-trips.
- ``omero:details`` should only contain owner/group/permissions/externalInfo;
  avoid custom fields there—add annotations instead.
- These docs are an unofficial companion; confirm invariants against upstream
  ``omero-marshal`` and OMERO schema releases when upgrading.

Testing your codecs
-------------------

- Mirror the style in ``tests/unit``: build minimal OMERO objects, encode,
  compare dictionaries, decode, and assert on fields.
- Include both loaded and unloaded variants to verify lazy-loading behaviour.
- Add regression tests for round-tripping colours, units, and transforms,
  which are the most error-prone fields.

End-to-end flow (expanded)
--------------------------

.. code-block:: text

   OMERO fetch (BlitzGateway / API)
          |
          |  optional: load links (pixels, shapes, annotations)
          v
   Encoder (class -> encoder lookup)
          |
          |  attaches @context, @type, @id, details; unwraps RTypes; encodes units
          v
   JSON-LD dict --> json.dumps / HTTP / queue / file
          |
          |  consumer reads @type
          v
   Decoder (type -> decoder lookup)
          |
          |  rebuilds OMERO model, wraps units, sets details/links
          v
   OMERO model object ready for further graph operations or persistence

Visual map of major object graphs
---------------------------------

.. code-block:: text

   Project -> Dataset -> Image -> Pixels -> Channel -> LogicalChannel
                                   |
                                   +-> ROI -> Shape(s)

   Screen -> Plate -> Well -> WellSample -> Image

   Details -> Owner / Group / Permissions / ExternalInfo

   Annotations -> (Boolean | Comment | Double | Long | Tag | Term | Timestamp | XML
                   | Map | File[OriginalFile])
