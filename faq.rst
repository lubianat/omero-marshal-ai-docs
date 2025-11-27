FAQ
===

.. note::
   Terms like :term:`Marshalling`, :term:`Codec`, :term:`@context`, and
   :term:`@type` link to the :doc:`glossary`.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

How is this different from ``json.dumps`` on an OMERO object?
-------------------------------------------------------------

Directly dumping an OMERO object produces opaque Python internals and cannot
round-trip. The encoders here unwrap ``RType`` values, keep schema-qualified
``@type`` information, manage units, and respect loaded/unloaded links so the
decoder can safely reconstruct the OMERO model object.

What happens if I do not load linked data?
------------------------------------------

Encoders only traverse links that report ``isLoaded()`` and have a non-zero
size. Unloaded links are omitted entirely. This prevents accidental database
access and keeps payloads small. If you need annotations, pixels channels, or
shapes, load them explicitly before encoding.

Can I drop the ``@context``?
----------------------------

Yes—set ``include_context=False`` when encoding nested objects to avoid
repetition. Keep the context on top-level payloads that cross service
boundaries so consumers can resolve prefixes and schema versions correctly.

How do I add support for a new OMERO model class?
-------------------------------------------------

Create paired encoder/decoder modules under ``omero_marshal/encode/encoders``
and ``omero_marshal/decode/decoders``. Export ``encoder = (Class, EncoderClass)``
and ``decoder = ("<schema_uri>#Type", DecoderClass)``. On import,
``pkgutil`` picks them up automatically. Add round-trip tests mirroring
``tests/unit``.

How do I handle OMERO schema upgrades?
--------------------------------------

Add new codec subclasses with the new schema URIs; do not delete older ones.
The library selects which set to register based on ``omero_version`` at import
time. Persisted payloads remain decodable because ``@type`` is fully
qualified.

Why are colours encoded as integers?
------------------------------------

OMERO stores RGBA colours as signed 32-bit integers. ``rgba_to_int`` packs
red/green/blue/alpha channels into this format; ``int_to_rgba`` reverses it.
This keeps compatibility with OMERO display conventions and avoids loss of
alpha information.

What about unsupported units?
-----------------------------

Currently Length and Time units are handled. If you encounter another unit
class, the encoder raises to make the gap explicit. Extend ``encode_unit`` /
``to_unit`` to add support, and add tests to lock behaviour down.

Is it safe to decode untrusted JSON?
------------------------------------

Payloads are simple dictionaries; there is no code execution. Still, decoded
objects may carry permissions or IDs you might not want to apply. Validate or
sanitize fields (especially ``omero:details`` and ``@id``) before using them
in write operations.

What if ``@type`` is missing?
-----------------------------

``get_decoder`` relies on ``@type`` to find the right codec. If it is missing,
reject the payload or infer it from context only if you fully control the
source. Guessing types can misapply schema rules and lead to silent data loss.

Do I need multiple contexts inside one payload?
-----------------------------------------------

No. Include the ``@context`` once at the top of the payload and omit it from
nested objects to reduce size. All nested ``@type`` values remain resolvable
because they rely on the same vocabulary.

How large are typical payloads?
-------------------------------

- Projects/Datasets/Images without pixels or annotations are small (hundreds
  of bytes).
- Pixels with channels and logical channel metadata add a few kilobytes.
- ROIs with many shapes can grow quickly; consider batching or filtering by
  plane/channel if size becomes an issue.

How do I sanity-check a payload quickly?
----------------------------------------

- Verify ``@type`` and ``@context`` exist at the top level.
- Spot-check IDs and a couple of critical fields (e.g. ``SizeX`` on Pixels,
  ``Color`` on Channels, ``Unit`` on Length/Time).
- Run a quick decode/encode round-trip in a REPL; compare to expected examples
  in :doc:`examples`. Remember these docs are unofficial; upstream behaviour is
  the source of truth.

Troubleshooting
---------------

``get_decoder`` returns ``None``
   Check the payload includes ``@type`` and that the URI matches a registered
   codec. Missing or truncated URIs cannot be resolved. If you are using a new
   schema, add the codec first.

BlitzGateway connection fails (ICE/SSL errors)
   Verify host/port/secure settings (for IDR: ``host=idr.openmicroscopy.org``,
   ``port=4064``, ``secure=True``, user ``public``/``public``). Ensure
   ``omero-py`` is installed with a compatible Ice runtime and that outbound
   ports are allowed by your firewall.

Payloads miss units or colours
   Unloaded links or unsupported unit classes lead to missing fields. Load
   linked objects before encoding and extend ``encode_unit``/``to_unit`` if you
   add new unit types.

Contexts appear multiple times
   Pass ``include_context=False`` when encoding nested objects; keep a single
   context at the top level.
