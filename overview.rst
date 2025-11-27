Overview
========

.. note::
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

OMERO Marshal converts objects from the `OMERO <https://www.openmicroscopy.org/omero/>`_
data model into plain Python dictionaries that can be JSON encoded, then
recreates the objects from those dictionaries. This is the core
:term:`Marshalling` step, powered by paired :term:`Codecs <Codec>` for each
supported model class.

.. note::
   When a term such as :term:`Marshalling` or :term:`Codec` appears for the
   first time, follow the link to the :doc:`glossary` for a deeper definition.

It acts as a bridge between server-side model objects (``Project``, ``Image``,
``Well``, :term:`ROI` shapes, and annotations) and client-side tools that expect JSON,
such as web frontends, Jupyter notebooks, or lightweight microservices.

Why this matters for engineering teams
--------------------------------------

Image-analysis pipelines and data platforms often need to copy metadata out of
OMERO (for example to feed a downstream REST API, cache metadata alongside
image derivatives, or inspect provenance in notebooks) and later push curated
values back in. The codecs in this repository:

- normalise identifiers, schema URIs, and namespaces so data stays compatible
  with OME XML 2015-01 and 2016-06;
- handle units, permissions, and colour encoding so you do not have to hand
  roll conversions;
- avoid loading unloaded links on purpose, which keeps round-trips safe on
  objects fetched with partial fields;
- keep annotation links, ROI shapes, screen/plate/well structures, channels,
  and pixel metadata intact for downstream reuse.

Supported schema versions
-------------------------

The library inspects the installed ``omero_version`` and selects the matching
schema flavour at import time:

- **2015-01** for OMERO 5.1–5.2 style ROI namespaces (``ROI``/``SA``/``SPW``);
- **2016-06** for OMERO 5.3+ where everything sits under the ``OME`` namespace.

The selected version drives which encoder/decoder classes are registered and
which field names are emitted (for example ``cx``/``cy`` vs ``x``/``y`` on
points, or SVG string transforms vs matrix fields on affine transforms).

Compatibility matrix
--------------------

.. list-table::
   :header-rows: 1

   * - OMERO version range
     - Schema version
     - Namespace prefixes
     - Notes
   * - 5.1.x–5.2.x
     - 2015-01
     - ROI / SA / SPW (plus OME/OMERO)
     - Shapes use SVG transform strings; points/ellipses use ``cx``/``cy``.
   * - 5.3.x–<6.0 (tested up to 5.6.x)
     - 2016-06
     - OME (plus OMERO)
     - Shapes store matrix coefficients; points/ellipses use ``x``/``y``.
   * - newer
     - (unsupported)
     - —
     - Add codecs for new schemas; library raises on unknown versions.

Repository layout (high level)
------------------------------

- ``omero_marshal/encode/encoders`` and ``omero_marshal/decode/decoders`` hold
  paired codecs for each model class.
- ``omero_marshal/__init__.py`` wires the registry that maps classes and schema
  URIs to the codecs.
- ``tests/unit`` contains round-trip expectations that show exactly which
  fields are included for each object type.

If you want the shortest possible orientation, start with the examples in
:doc:`usage` and skim :doc:`codecs` for the object you care about.
