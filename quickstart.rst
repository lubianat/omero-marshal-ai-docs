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

Install the OMERO client libraries and ``omero-marshal``. Add the Sphinx bits
only if you plan to build these docs locally.

.. code-block:: bash

   pip install omero-py omero-marshal       # runtime libraries
   pip install -r requirements.txt          # docs build (optional)

2. Grab an OMERO object
-----------------------

Use BlitzGateway to fetch a live object or construct an in-memory model for
testing. This example keeps everything local:

.. code-block:: python

   from omero.model import ImageI
   image = ImageI(1)        # set an id if you want @id in the payload
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
   data = payload                       # use this if you skip JSON
   json_payload = json.dumps(payload)   # round-trip through a string if needed
   data = json.loads(json_payload)

5. Decode back to an OMERO model object
---------------------------------------

.. code-block:: python

   from omero_marshal import get_decoder
   restored = get_decoder(data["@type"]).decode(data)  # or pass `payload` directly
   assert restored.getName().getValue() == "demo"

6. Round-trip checklist
-----------------------

- ``@type`` present and using the full schema URI (for example ``...#Image``).
- ``@context`` included at the top level (unless intentionally omitted for nesting).
- ``@id`` present only when the source object had an id.
- Critical fields (IDs, units, colours) survived the round-trip.

Next steps
----------

- See :doc:`usage` for more options on encode/decode behaviour.
- See :doc:`tutorials` for ROI, SPW, and HTTP service patterns.
- Browse :doc:`examples` for full payload snapshots.
- Consult :doc:`developer` when adding codecs or extending behaviour.
- Need an offline copy? Grab the PDF/EPUB/HTML zip from the **Downloads**
  menu on the Read the Docs build.
