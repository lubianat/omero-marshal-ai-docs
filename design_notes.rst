Codec internals for developers
==============================

.. note::
   Developer-focused dive into how codecs are structured and the OOP patterns
   in play. Terms like :term:`Encoder`, :term:`Decoder`, :term:`@type`, and
   :term:`@context` link to the :doc:`glossary`. This is an unofficial
   companion; verify behaviour against the upstream ``omero-marshal`` code.
   For a reference-style overview, see :doc:`architecture`.

Core objects and schema mapping
-------------------------------

- **TYPE to schema**: each codec declares a ``TYPE`` like
  ``http://www.openmicroscopy.org/Schemas/OME/2016-06#Image`` so encoded
  payloads carry the schema version alongside the model name.
- **OMERO_CLASS mapping**: decoders declare an ``OMERO_CLASS`` (e.g.
  ``ImageI``) to instantiate when rebuilding objects.
- **Schema forks**: schema-specific subclasses (2015-01 vs 2016-06) sit side by
  side; a small bit of version logic decides which one registers.

Schema version selection
------------------------

- ``SCHEMA_VERSION`` is derived from the installed ``omero-py``/OMERO version.
- Modules usually guard registration with a simple ``if SCHEMA_VERSION >= ...``
  so only the matching codec tuple is exported.
- The ``@type`` URI embedded in payloads (e.g.
  ``.../2016-06#Channel`` vs ``.../2015-01#Channel``) is the decoder’s key to
  pick the correct class.

Registry and lookup flow
------------------------

- **Plugin registry**: on import, ``omero_marshal`` walks ``encode/encoders``
  and ``decode/decoders`` and registers any module exposing an ``encoder`` or
  ``decoder`` tuple. That keeps additions discoverable without editing a
  central map.
- **Strategies per model**: each OMERO model class gets its own encoder/decoder
  class pair. Picking a codec is a Strategy-style lookup via ``get_encoder`` /
  ``get_decoder`` keyed by model type or ``@type`` URI.
- **Shared context**: codecs receive a ``MarshallingCtx`` so nested lookups and
  caches are reused rather than re-created per call.

Import-to-call flow
-------------------

.. code-block:: text

   import omero_marshal
      |
      |-- pkgutil scans encode/encoders + decode/decoders
  |-- modules imported; each exposes encoder/decoder tuple
  v
   Registry populated: Class -> Encoder, @type URI -> Decoder
      |
      |-- get_encoder(ModelClass) / get_decoder(@type)
      v
   Encode/Decode call with shared MarshallingCtx (handles nesting + caches)

Key behaviours:

- Missing or misnamed ``encoder``/``decoder`` tuples are simply skipped—no
  registration, no errors. Good for avoiding import side effects, but easy to
  forget, so tests matter.
- Registry lookups return ``None`` when a codec is absent; callers should
  handle that (see :ref:`architecture:error-handling`).

How classes are laid out
------------------------

- The tree mirrors the OMERO model itself. Each file under
  ``omero_marshal/encode/encoders`` corresponds to a model type (Image, ROI,
  Channel, Plate, etc.). That module defines one or more encoder classes (one
  per schema when needed) and exposes an ``encoder = (<omero.model.Class>,
  <EncoderClass>)`` tuple.
- Decoders live in the matching path under ``decode/decoders`` and export
  ``decoder = (<schema_uri string>, <DecoderClass>)``.
- Because the registry is populated at import time, adding a new codec is
  mostly “drop in a module with the right tuple”. There is no central
  switchboard to edit, which keeps churn low when the model grows.

Patterns in play
----------------

- **Registry + Strategy**: the registry is a dynamic directory of available
  strategies. ``get_encoder``/``get_decoder`` simply look up the right strategy
  and hand back an object with a uniform interface (``encode`` / ``decode``).
- **Template Method**: the base classes own the framing—the ``@type``, optional
  ``@context``, ``@id``, and details handling—then call into subclass hooks to
  fill model-specific fields. That keeps payload shape consistent.
- **Composition for helpers**: instead of bolting utilities onto every
  subclass, helpers like ``encode_unit``/``to_unit`` and colour packing live in
  shared modules and are called where needed.
- **Schema-conditional registration**: when schemas diverge, both variants are
  implemented and only the matching one registers, avoiding version checks in
  hot code paths.

Template skeleton (tiny example)
--------------------------------

An encoder subclass relies on the base class to stamp in the scaffolding, then
adds its own fields:

.. code-block:: python

   class Image201606Encoder(Encoder):
       TYPE = "http://www.openmicroscopy.org/Schemas/OME/2016-06#Image"
       def encode(self, obj, include_context=None):
           v = super(Image201606Encoder, self).encode(obj, include_context)
           self.set_if_not_none(v, "Name", obj.getName())
           return v

The matching decoder mirrors that structure and rehydrates fields. Because the
base class already applies ``@id`` and details handling, subclasses stay small.

Base behaviour to know
----------------------

- ``Encoder`` applies ``@type`` and (by default) ``@context``, unwraps
  :term:`RType` values, includes ``@id`` when present, and can include
  ``omero:details`` when loaded.
- ``Decoder`` creates the OMERO class, re-applies ``@id`` and details, and
  delegates unit/colour helpers so numeric + unit metadata survive.
- ``MarshallingCtx`` is passed into nested codecs to keep lookups consistent and
  avoid re-resolving the same types.

Organizing principles (and why they help)
-----------------------------------------

- **Isolation by model type** keeps changes local. Tweaking an ROI field does
  not risk Image or Plate codecs.
- **Declarative registration** avoids forgetting to wire up a new codec. If the
  module imports, it registers.
- **Context reuse via ``MarshallingCtx``** reduces duplicated work when encoding
  nested graphs (e.g., Project -> Dataset -> Image).
- **Explicit schema handling** prevents silent drift when upstream schemas add
  fields; new subclasses make differences obvious.
- **Side-effect avoidance**: codecs rely on ``isLoaded()`` checks rather than
  loading links, so encoding remains a read-only operation on whatever graph
  the caller has prepared.

Trade-offs and guardrails
-------------------------

- **Import-time registration is silent**: you get flexibility but fewer guard
  rails. Add tests that assert your codec is present in ``ENCODERS`` /
  ``DECODERS`` after import.
- **Schema forks duplicate code**: keeping 2015-01 and 2016-06 side by side
  means small drifts can diverge. Pair changes with round-trip tests for both
  schemas.
- **Shared context caches**: great for speed, but avoid storing mutable state
  that depends on caller-specific flags inside codecs; keep them stateless.

If you extend the library
-------------------------

- Start from an existing encoder/decoder pair for a similar model; copy the
  structure and adapt fields.
- Keep base-class calls intact so ``@type``/``@context``/``@id`` stay standard.
- Write round-trip tests that assert both the encoded dict and the reconstructed
  OMERO object for the schema versions you support.
- Use the registry: ensure your module exports the ``encoder``/``decoder``
  tuples so it is picked up automatically.

Quick checklist
---------------

- [ ] Does your module expose ``encoder``/``decoder`` tuples with the right
  types/URIs?
- [ ] Are both schema variants covered (2015-01 and 2016-06) when applicable?
- [ ] Do round-trip tests exist for loaded and unloaded links?
- [ ] Does the payload keep ``@context`` only where needed (top-level, not
  nested)?

Where to read the code (upstream)
---------------------------------

- ``omero_marshal/encode/__init__.py``: base ``Encoder``, registry population,
  and helpers like ``set_if_not_none`` / unit handling.
- ``omero_marshal/decode/__init__.py``: base ``Decoder``, registry population,
  and helpers for assigning properties and rebuilding units.
- ``omero_marshal/encode/encoders`` and ``decode/decoders``: per-model
  subclasses and their registration tuples.
- ``omero_marshal/util`` (if present in your checkout): colour packing, unit
  helpers, and other shared functions used by codecs.
