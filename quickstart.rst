Quickstart
==========

Goal: encode an OMERO object to JSON and decode it back in under five minutes.

.. note::
   Key terms link to the :doc:`glossary` (e.g. :term:`Encoder`, :term:`Decoder`,
   :term:`@context`, :term:`@type`).

.. warning::
   This quickstart is an unofficial, AI-generated guide. Confirm behaviour
   against the upstream ``omero-marshal`` library and its tests.

1. Install dependencies
-----------------------

.. code-block:: bash

   pip install omero-marshal                # library under test
   pip install -r docs/requirements.txt     # to build these docs (optional)

2. Grab an OMERO object
-----------------------

Use BlitzGateway or the raw model classes. Here we construct a minimal image:

.. code-block:: python

   from omero.model import ImageI
   image = ImageI(1)
   image.setName("demo")

3. Encode to a JSON-safe dict
-----------------------------

.. code-block:: python

   from omero_marshal import get_encoder
   payload = get_encoder(ImageI).encode(image)   # includes @context/@type

4. Serialise to JSON (optional)
-------------------------------

.. code-block:: python

   import json
   json_payload = json.dumps(payload)

5. Decode back to an OMERO model object
---------------------------------------

.. code-block:: python

   from omero_marshal import get_decoder
   data = json.loads(json_payload)
   restored = get_decoder(data["@type"]).decode(data)
   assert restored.getName().getValue() == "demo"

6. Round-trip checklist
-----------------------

- ``@type`` present and matches the schema URI.
- ``@context`` included at the top level (unless intentionally omitted).
- Critical fields (IDs, units, colours) survived the round-trip.

Next steps
----------

- See :doc:`tutorials` for ROI, SPW, and HTTP service patterns.
- Browse :doc:`examples` for full payload snapshots.
- Consult :doc:`developer` when adding codecs or extending behaviour.
