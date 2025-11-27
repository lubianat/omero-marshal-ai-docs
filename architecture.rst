Architecture
============

.. note::
   First-time jargon (e.g. :term:`Marshalling`, :term:`Codec`, :term:`@type`,
   :term:`RType`, :term:`Unit`) links to the :doc:`glossary` for fuller
   context.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Dynamic registry
----------------

- Importing ``omero_marshal`` triggers a ``pkgutil`` walk of
  ``encode/encoders`` and ``decode/decoders``; modules are imported to pick up
  registrations.
- Each module exports an ``encoder`` or ``decoder`` tuple of
  ``(source_type, EncoderClass)`` or ``(schema_uri, DecoderClass)``. Tuples
  that are missing or misnamed will not be registered.
- ``get_encoder(<omero.model.Class>)`` and ``get_decoder(<@type string>)``
  look up entries in the in-memory registry and return ``None`` when absent.
  Codecs receive a shared ``MarshallingCtx`` so they can resolve nested objects
  recursively and reuse cached lookups.

Schema version resolution
-------------------------

- ``SCHEMA_VERSION`` is derived from ``omero_version`` at runtime.
- The version drives namespace URLs (``ROI``/``SA``/``SPW`` vs ``OME``) and
  selects which codec subclasses are registered. The library supports
  **2015-01** and **2016-06** only; anything newer must add new codecs.

Base encoder/decoder behaviour
------------------------------

- ``Encoder.encode`` constructs ``@type``, ``@context`` (unless explicitly
  suppressed), ``@id`` when available, and ``omero:details`` when the object
  has a loaded ``details`` field. The direction is always OMERO model object
  -> JSON-safe dictionary.
- ``Decoder.decode`` initialises the OMERO class, assigns the ``@id`` value,
  and hydrates ``omero:details`` using the nested decoder if present. The
  direction is always JSON-derived dictionary -> OMERO model object.
- ``set_if_not_none`` unwraps OMERO :term:`RType` objects automatically;
  :term:`Unit` values are encoded with ``encode_unit`` so numeric values keep
  their unit metadata.
- Unit decoding uses ``to_unit`` to rebuild instances of the specific OMERO
  unit class (e.g. ``LengthI``).

Units, colour, and transforms
-----------------------------

- **Units**: currently Length and Time are supported. Unrecognised unit classes
  raise an exception so that additions are explicit.
- **Colours**: ``rgba_to_int`` packs red/green/blue/alpha components into the
  signed 32-bit integer format OMERO expects; ``int_to_rgba`` reverses it.
- **Transforms**: Shape transforms depend on the schema version. For 2015-01 a
  legacy ``AffineTransformI`` shim parses SVG-style strings (``matrix(...)`` or
  ``translate(...)``). From 2016-06 onwards, the transform fields are stored
  directly when at least one coefficient is set.

Loading discipline
------------------

- Most codecs check ``isLoaded()``, ``is...Loaded()``, and collection sizes
  before traversing links. This keeps encoding side-effect free on partially
  loaded objects from BlitzGateway.
- Details, permissions, and external info are encoded only when present; if
  owners or groups are unloaded, only ``@id`` and ``@type`` are emitted to
  avoid forcing extra database lookups.

Flow of registration and use
----------------------------

.. code-block:: text

   import omero_marshal
          |
          | (pkgutil scans encoders/decoders)
          v
   Registry populated: Class -> Encoder, @type -> Decoder
          |
          | get_encoder(Class) / get_decoder(@type)
          v
   Encode/decode calls with shared MarshallingCtx

Adding new codecs
-----------------

- Create a module under ``omero_marshal/encode/encoders`` and define a class
  with a ``TYPE`` URI, an ``encode`` method, and an ``encoder`` tuple
  ``(<omero.model.Class>, <EncoderClass>)``.
- Mirror it under ``omero_marshal/decode/decoders`` with ``OMERO_CLASS``,
  ``decode``, and a ``decoder`` tuple ``(<TYPE string>, <DecoderClass>)``.
- Importing ``omero_marshal`` picks these up automatically via the package
  walker; tests under ``tests/unit`` show how to assert round-trips.

Error handling
--------------

- Unknown encoder/decoder lookups log a warning and return ``None``. Callers
  should validate the result before attempting to use it.
- Invalid or unsupported OMERO versions raise immediately during
  ``SCHEMA_VERSION`` resolution so build systems fail fast.
