Usage
=====

.. note::
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Prerequisites
-------------

.. note::
   Jargon in this guide (for example :term:`Encoder`, :term:`Decoder`,
   :term:`@type`, :term:`@context`, and :term:`RType`) links to the
   :doc:`glossary` the first time it appears.

- Python 3.6+ with the ``omero-py`` client libraries installed (``pip install
  omero-py``).
- ``omero-marshal`` installed (``pip install omero-marshal``). If you work on
  the upstream code, use ``pip install -e .`` in that repository instead.
- An OMERO model object to encode (for example one fetched via BlitzGateway or
  constructed in a test).

Encoding to JSON-ready dictionaries
-----------------------------------

The library does not ship a custom ``dumps`` helper. Instead you pick the
:term:`Encoder` for the object type and pass the object to ``encode``. The
result is a plain dictionary you can feed to ``json.dumps``. Encoding always
moves **from** an OMERO model object **to** a JSON-safe dictionary::

    import json
    from omero_marshal import get_encoder
    from omero.model import ImageI

    image = ImageI(1)  # or pull from BlitzGateway
    encoder = get_encoder(ImageI)
    payload = encoder.encode(image)          # includes @context by default
    json_payload = json.dumps(payload)       # safe to serialise

Decoding back into OMERO model objects
--------------------------------------

Use the ``@type`` field in the payload to pick the matching :term:`Decoder`.
Decoding always moves **from** a JSON-derived dictionary **to** an OMERO model
object::

    import json
    from omero_marshal import get_decoder

    data = json.loads(json_payload)
    decoder = get_decoder(data["@type"])
    round_tripped = decoder.decode(data)

You can now attach ``round_tripped`` to other OMERO graph operations or update
its fields before saving it via the OMERO API.

Controlling the JSON-LD context
-------------------------------

``encode(..., include_context=None)`` adds the :term:`@context` by default.
Pass ``include_context=False`` when nesting objects to avoid repeating it::

    project_encoder = get_encoder(ProjectI)
    project_json = project_encoder.encode(project, include_context=True)
    # contained datasets/images will omit their own @context

What the payload looks like
---------------------------

- :term:`@type` always refers to the schema URI (for example ``"ROI"`` or
  ``"omero:Permissions"``). Use it for decoding.
- :term:`@context` maps the default vocabulary to the OME schema namespace and
  introduces the ``omero`` prefix for OMERO-specific types.
- :term:`@id` is populated when the source object exposes an ``id`` attribute
  with a value.
- Values stored as OMERO :term:`RType` wrappers are unwrapped for you.
- Unit-bearing values are expanded into ``{"@type": "...", "Unit": "...",
  "Symbol": "...", "Value": ...}``, which keeps :term:`Unit` metadata attached.

See :doc:`examples` for fuller payload snapshots (Image, ROI, Plate, and
Permissions).

Round-tripping tips
-------------------

- The encoders respect ``isLoaded()`` checks on linked data to avoid pulling
  unloaded collections accidentally. Load what you need on the OMERO side
  before encoding (e.g. annotation links or pixels channels).
- Shape transforms differ across schema versions. When reading transforms from
  older payloads you may see SVG matrices encoded as strings.
- ``omero:details`` (owner, group, permissions, external info) are included
  when present; drop or replace them before re-uploading if your workflow
  should not change security settings.
