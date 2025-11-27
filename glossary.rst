Glossary
========

.. note::
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

.. glossary::

    Marshalling
        The process of turning in-memory objects into a transport-friendly
        representation and later reversing that step. In this repository, the
        transport is a JSON-serialisable Python dictionary that preserves type
        information, context, and links so the object graph can be rebuilt
        safely.

        Common reasons to marshal include caching metadata for analysis,
        exporting objects to services that only accept JSON, and persisting
        results offline without tying them to a live OMERO session.

        Example: encode an ``ImageI`` to JSON for a notebook pipeline, tweak a
        few fields, and decode it back before saving through the OMERO API.

        See also: :doc:`quickstart` for a minimal walkthrough.

    Codec
        A pair of functions (an encoder and decoder) that know how to marshal
        one specific model type. Each codec handles that type’s field-level
        quirks: loaded vs unloaded links, unit conversions, and schema
        differences between 2015-01 and 2016-06.

        Codecs are discovered dynamically from
        ``omero_marshal/encode/encoders`` and
        ``omero_marshal/decode/decoders``. Adding a new codec is usually
        symmetrical: implement both directions, register them, and rely on the
        shared ``MarshallingCtx`` for nested lookups.

        Example: the ROI codec marshals shapes, annotations, and permissions
        when those links are loaded, keeping measurements tied to the correct
        image.

        See also: :ref:`developer:create-a-new-codec-step-by-step` and
        :ref:`architecture:dynamic-registry`.

    Encoder / Decoder
        Encoders expose ``encode(obj, include_context=True)`` and return a
        dictionary with ``@type`` (and usually ``@context``). They unwrap OMERO
        ``RType`` values, attach ``@id`` when present, include details, and
        defer to sibling codecs for nested objects.

        Decoders accept that dictionary, locate the target OMERO class, and
        rebuild it. They also take care of unit reconstruction and restoring
        permissions, external info, and links. They aim to make round-trips
        lossless for the supported fields.

        In short: **encoding** flows from an in-memory OMERO model object to a
        plain Python dictionary suitable for JSON serialisation; **decoding**
        flows in the opposite direction, from such a dictionary back to an
        OMERO model object.

        Example: ``get_encoder(ImageI).encode(image)`` emits a dictionary with
        ``@type``; ``get_decoder(payload["@type"]).decode(payload)`` rebuilds
        the ``ImageI`` instance.

        See also: :ref:`usage:encoding-to-json-ready-dictionaries` and
        :ref:`usage:decoding-back-into-omero-model-objects`.

    ``@context``
        The JSON-LD context mapping the default vocabulary to the OME schema
        namespace and introducing the ``omero`` prefix for OMERO-specific
        types. Including it makes the payload self-describing and easy to
        interpret without hard-coded prefixes.

        When objects are nested, the context can be omitted on inner items to
        save space; the top-level context still defines how keys should be read
        downstream.

        Example: ``"@context": {"@vocab": "http://www.openmicroscopy.org/Schemas/OME/2016-06#", "omero": "http://www.openmicroscopy.org/Schemas/OME/2016-06#"}``
        tells consumers which namespace to apply to keys. Swap the schema URI
        if you encode against a different OME version (for example 2015-01).

        See also: :ref:`usage:controlling-the-json-ld-context`.

    ``@type``
        The schema-qualified identifier for the encoded object, e.g.
        ``"http://www.openmicroscopy.org/Schemas/OME/2016-06#Image"`` or
        ``"omero:Permissions"``. It disambiguates similarly named types across
        schemas and is the lookup key for decoders.

        Maintaining the full URI is important when supporting multiple OME
        schema versions; it ensures consumers pick the right interpretation and
        prevents silent drift when the schema evolves.

        Example: ``"http://www.openmicroscopy.org/Schemas/OME/2016-06#ROI"``
        signals that the payload describes an ROI and should be decoded with
        that codec.

        See also: :ref:`architecture:dynamic-registry`.

    ``@id``
        The OMERO database identifier emitted when available on the source
        object. It preserves entity identity across the wire so updates,
        links, and permission checks continue to target the correct row.

        If an object is transient or has no server-side id, ``@id`` is simply
        omitted. Callers can still attach it later after persisting the object.

        Example: encoding ``ImageI(42)`` yields ``"@id": 42``; encoding a new
        unsaved image omits ``@id``.

        See also: :ref:`usage:round-tripping-tips`.

    RType
        OMERO’s wrapped primitive types (``rlong``, ``rstring``, ``rdouble``,
        and friends). They provide nullability, type hints, and lazy-loading
        semantics on the server side.

        Encoders unwrap these into plain Python values so JSON consumers do not
        need OMERO runtime helpers. When decoding, the library rewraps values
        using OMERO field metadata so the reconstructed object behaves like any
        other OMERO model instance.

        Example: ``rstring("channel-1")`` becomes ``"channel-1"`` in JSON and
        is restored as an ``rstring`` on decode.

        See also: :ref:`usage:what-the-payload-looks-like`.

    Unit
        Length and Time values represented as instances of the OMERO unit
        classes (for example ``LengthI`` with ``UnitsLength.MICROMETER``).
        Units travel with both a numeric value and symbolic metadata, which is
        essential for downstream calculations and comparisons.

        Encoders expand units into dictionaries with ``@type``, ``Unit``, and
        ``Value`` (plus ``Symbol`` where available) to avoid losing the unit
        system. Decoders rebuild the typed unit instances, keeping subsequent
        arithmetic consistent with OMERO expectations.

        Example: ``LengthI(1.2, UnitsLength.MICROMETER)`` encodes to
        ``{"@type": "Length", "Unit": "MICROMETER", "Value": 1.2}`` (with an
        optional ``"Symbol"`` field) and decodes back to a typed ``LengthI``.

        See also: :ref:`usage:what-the-payload-looks-like`.

    ROI
        Region of Interest. An OMERO container for one or more shapes linked to
        a single image, used to mark objects, measurements, or analysis
        results. ROIs can carry annotations and inherit details like ownership
        and permissions.

        The marshalled form captures the ROI’s name, description, shapes, and
        annotations only if those links are loaded, so you control how much of
        the ROI graph crosses the wire.

        Example: a rectangle and ellipse drawn on an image are marshalled with
        their positions and linked annotations so they can be inspected in a
        downstream notebook.

        See also: :ref:`tutorials:round-trip-an-roi-with-shapes`.

    SPW
        Screen/Plate/Well data model used in high-content screening workflows.
        Screens contain plates; plates contain wells; wells can hold multiple
        well samples that point to images.

        Marshal support preserves this hierarchy and includes well colour/status
        fields when they are present on the source object, keeping plate maps
        meaningful outside OMERO (for example in QC dashboards or notebook
        visualisations).

        Example: encode a plate with well statuses to drive a QC heatmap
        without querying an OMERO server.

        See also: :ref:`tutorials:encode-an-spw-hierarchy`.

    LogicalChannel
        The rich metadata attached to an image channel: fluorophore identity,
        excitation/emission wavelengths, acquisition mode, illumination,
        photometric interpretation, ND filter settings, and pinhole size.

        Logical channel data is nested within channels and included when the
        linked enumerations are loaded on the source object. It is critical for
        downstream analysis that relies on spectral separation, scaling, or
        display defaults.

        Example: marshalling an image channel includes the excitation and
        emission wavelengths so spectral plots can be regenerated later.

        See also: :ref:`usage:what-the-payload-looks-like` for where these
        values appear.
