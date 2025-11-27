Codecs by Object Type
=====================

This section summarises what each encoder/decoder pair includes. Field names
match the JSON keys; OMERO fields are noted in parentheses when different.

.. note::
   Jargon such as :term:`ROI`, :term:`SPW`, :term:`LogicalChannel`, and
   :term:`Unit` links to the :doc:`glossary` on first mention.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Quick inclusion rules
---------------------

- **Loaded only**: linked collections (datasets, images, channels, shapes,
  annotations, wells) are encoded only when loaded.
- **Details**: included when present; unloaded owners/groups emit only
  ``@id``/``@type``.
- **Units**: emitted as structured dicts with ``@type``/``Unit``/``Symbol``/
  ``Value``.
- **Colours**: encoded as signed 32-bit RGBA integers.
- **Transforms**: SVG strings in 2015-01; matrix coefficients in 2016-06.

Containers and images
---------------------

- **Project / Dataset / Image** (``omero_marshal/encode/encoders/project.py`` ,
  ``dataset.py``, ``image.py``)

  - Name and Description are always included when present.
  - Child links are only serialised if the corresponding links are loaded:
    datasets under projects, images under datasets.
  - Images include acquisition date, archive flag, series index, partial flag,
    and description/name. If ``format`` is loaded it is encoded inline. Primary
    pixels are included only when loaded and present.

Pixels and channels
-------------------

- **Pixels** (``pixels.py``)

  - Captures physical sizes (Length with units), pixel sizes ``SizeX/Y/Z/C/T``,
    ``SignificantBits``, SHA1, methodology, time/wave increments, and the
    ``DimensionOrder`` and ``PixelsType`` enumerations when loaded.
  - Channels are nested only when loaded. The encoder trusts the channel order
    already set on the ``Pixels`` object.

- **Channel** and **:term:`LogicalChannel`** fields (``channel.py``)

  - Colour is encoded via RGBA integer; lookup tables are passed through.
  - Logical channel metadata includes excitation/emission wavelengths (with
    units), fluor, name, ND filter, pinhole size, Pockel cell setting, samples
    per pixel, contrast method, illumination, acquisition mode, and
    photometric interpretation when the linked enumerations are loaded.

Annotations
-----------

- **Base Annotation** (``annotation.py``) emits Description and Namespace.
  Annotatable objects (datasets, images, ROIs, shapes, screens, plates, wells)
  include linked annotations if the annotation links are loaded.
- **Boolean / Comment / Double / Long / Tag / Term / Timestamp / XML
  annotations** map their value fields to ``Value`` or ``Text`` keys as
  appropriate.
- **MapAnnotation** stores ``Value`` as a list of ``[key, value]`` pairs.
- **FileAnnotation** bundles an ``OriginalFile`` (path, size, timestamps,
  hash/hash algorithm, mimetype, name).

Regions of interest and shapes
------------------------------

- **:term:`ROI`** (``roi.py``) keeps ``Name``, ``Description``, and the set of shapes
  when shape links are loaded. Annotation links on the ROI are included as
  well.
- **Shape base** (``shape.py``) records fill/stroke colours, stroke width,
  dash pattern, text, indices (TheZ, TheT, TheC), font properties, visibility
  (2015-01 only), and stroke line cap (2015-01 only).
  - Transform handling differs by schema: 2015-01 encodes SVG transform
    strings via the legacy ``AffineTransformI`` shim; 2016-06 uses matrix
    coefficients when any are set.
- **Specific shapes** add coordinates:
  - Point (``x/y`` or ``cx/cy`` depending on schema)
  - Ellipse (``x/y/radiusX/radiusY`` or ``cx/cy/rx/ry``)
  - Rectangle, Mask (``x/y/width/height``)
  - Line adds ``X1/Y1/X2/Y2`` plus ``MarkerStart/MarkerEnd`` in 2016-06
  - Polyline/Polygon include ``Points`` and optional markers (2016-06 only)
  - Label stores ``x/y`` and shares the other shape styling fields.

Screens, plates, and wells
--------------------------

These map to the :term:`SPW` (screen/plate/well) model used in high-content
screening.

- **Screen** (``screen.py``) captures protocol description/identifier, reagent
  set description/identifier, type, name, description, and linked plates when
  plate links are loaded.
- **Plate** (``plate.py``) includes name/description, row/column naming
  conventions, column/row counts, default sample (field index), external
  identifier, status, well origin (Length with units), and linked wells when
  loaded.
- **Well** (``well.py``) stores row/column, external description/identifier,
  type, colour (RGBA integer), status, and linked well samples when loaded.
- **PlateAcquisition** (``plateacquisition.py``) carries name, description,
  maximum field count, start/end timestamps.
- **WellSample** (``wellsample.py``) records timepoint, position (Length with
  units), linked image, and parent plate acquisition id when present.

People, permissions, and external info
--------------------------------------

- **Experimenter** and **ExperimenterGroup** include identifying fields only
  when the object is loaded; unloaded references keep just ``@id``/``@type``.
- **Details** (``details.py``) attaches owner, group, permissions, and
  external info without adding an ``@context`` to avoid repetition.
- **Permissions** (``permissions.py``) exposes both the string representation
  and the boolean convenience flags (``canAnnotate``, ``canDelete``,
  ``isWorldRead``, etc.). Decoding rehydrates restrictions from those flags.
- **ExternalInfo** holds entity id/type, LSID, and UUID for cross-system audit
  trails.

Enumerations
------------

Enumerated classes (dimension order, contrast method, acquisition mode,
illumination, checksum algorithm, format, pixel type, photometric
interpretation) all rely on the shared ``EnumEncoder``/``EnumDecoder`` to store
the ``value`` property when the enumeration is loaded.
