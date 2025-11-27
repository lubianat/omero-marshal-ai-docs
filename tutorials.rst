Tutorials
=========

.. note::
   Jargon in these tutorials (e.g. :term:`Encoder`, :term:`Decoder`,
   :term:`@context`, :term:`@type`) links to the :doc:`glossary` on first
   mention.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Encode and decode an Image
--------------------------

1. Fetch or construct an ``ImageI`` (via BlitzGateway or tests).
2. Pick the :term:`Encoder` using ``get_encoder(ImageI)`` and call
   ``encode(image)``.
3. Serialize with ``json.dumps`` to send across the wire or store.
4. On the other side, load JSON, inspect ``@type``, call ``get_decoder(...)``,
   and rebuild the object.

.. code-block:: text

   OMERO ImageI --> Encoder --> dict --> JSON --> Decoder --> OMERO ImageI

.. code-block:: python

   import json
   from omero_marshal import get_encoder, get_decoder
   from omero.model import ImageI

   image = ImageI(1)
   payload = get_encoder(ImageI).encode(image)
   json_payload = json.dumps(payload)

   data = json.loads(json_payload)
   image_copy = get_decoder(data["@type"]).decode(data)

Round-trip an ROI with shapes
-----------------------------

ROIs carry nested shapes and annotations. Load what you need first to ensure
the encoder walks the links::

    from omero.gateway import BlitzGateway
    from omero_marshal import get_encoder, get_decoder

    conn = BlitzGateway("user", "pass", host="omero.host")
    roi = conn.getObject("Roi", 1)
    roi = roi._obj  # unwrap the underlying model object
    roi.loadShapes()  # ensure shapes are loaded

    encoded = get_encoder(roi.__class__).encode(roi)
    decoded = get_decoder(encoded["@type"]).decode(encoded)

Key notes:

- Shape transforms differ by schema version (2015-01 uses SVG strings,
  2016-06 uses matrix fields); the correct decoder is selected via ``@type``.
- Annotation links are included only when loaded; call ``loadAnnotations`` if
  you need them.

Serve metadata over HTTP
------------------------

You can expose marshalled payloads via a lightweight service boundary without
shipping the full OMERO model. Example with a minimal Flask-style handler::

    import json
    from omero_marshal import get_encoder
    from omero.model import ImageI

    def handle_request(image_id):
        image = ImageI(image_id)  # in real code, fetch from OMERO
        encoded = get_encoder(ImageI).encode(image, include_context=True)
        return json.dumps(encoded), 200, {"Content-Type": "application/json"}

On the consumer side, decode with ``get_decoder`` to regain a real OMERO model
object, or read the JSON directly if you only need metadata.

Nested export of Project/Dataset/Image
--------------------------------------

When exporting containers, include ``@context`` at the top level only to keep
payloads compact::

    project_encoder = get_encoder(ProjectI)
    project_json = project_encoder.encode(project, include_context=True)
    # datasets/images inside will omit their own @context

This is useful for static metadata snapshots, UI previews, or feeding task
queues for downstream processing.

Encode an SPW hierarchy
-----------------------

High-content screening data often needs to move between services. To encode a
screen with plates and wells:

.. code-block:: python

    from omero_marshal import get_encoder
    from omero.model import ScreenI

    screen = ScreenI(1)  # populate via OMERO, ensuring plates/wells are loaded
    payload = get_encoder(ScreenI).encode(screen, include_context=True)

Flow:

.. code-block:: text

   Screen -> Plate(s) -> Well(s) -> WellSample(s) -> Image
     |         |           |             |
     |         |           |             +-- encoded if loaded
     |         |           +-- colour/status encoded (RGBA int, status string)
     |         +-- well origins, naming conventions, dimensions encoded
     +-- protocol/reagent info encoded

Keep ``@context`` because multiple namespaces (OME vs OMERO) appear in SPW
structures.

Validate a round-trip
---------------------

When fidelity matters (e.g. wavelengths, units, colours), assert after
decoding::

    import json
    from omero_marshal import get_encoder, get_decoder
    from omero.model import ChannelI
    from omero.rtypes import rint

    channel = ChannelI(1)
    channel.red = rint(255); channel.green = rint(0); channel.blue = rint(128)
    payload = get_encoder(ChannelI).encode(channel)
    data = json.loads(json.dumps(payload))
    restored = get_decoder(data["@type"]).decode(data)

    assert restored.getRed().getValue() == 255
    r, g, b, a = get_decoder(data["@type"]).int_to_rgba(data["Color"])
    assert (r, g, b) == (255, 0, 128)

Use this pattern in tests or notebooks to catch regressions when tweaking
codecs or schema handling.
