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

        Bioinformaticians often marshal OMERO model objects to decouple
        metadata from the live OMERO server: for caching, for notebook
        analysis, or to shuttle data into microservices that only speak JSON.
        Accurate marshalling lets you mix those systems without sacrificing
        provenance.

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

    Encoder / Decoder
        Encoders expose ``encode(obj, include_context=True)`` and return a
        dictionary with ``@type`` (and usually ``@context``). They unwrap OMERO
        ``RType`` values, attach ``@id`` when present, include details, and
        defer to sibling codecs for nested objects.

        Decoders accept that dictionary, locate the target OMERO class, and
        rebuild it. They also take care of unit reconstruction and restoring
        permissions, external info, and links. Together they guarantee that a
        round-trip is lossless for the supported fields.

        In short: **encoding** flows from an in-memory OMERO model object to a
        plain Python dictionary suitable for JSON serialisation; **decoding**
        flows in the opposite direction, from such a dictionary back to an
        OMERO model object.

    ``@context``
        The JSON-LD context mapping the default vocabulary to the OME schema
        namespace and introducing the ``omero`` prefix for OMERO-specific
        types. Including it makes the payload self-describing and easy to
        interpret without hard-coded prefixes.

        When objects are nested, the context can be omitted on inner items to
        save space; the top-level context still defines how keys should be read
        downstream.

    ``@type``
        The schema-qualified identifier for the encoded object, e.g.
        ``"http://www.openmicroscopy.org/Schemas/OME/2016-06#Image"`` or
        ``"omero:Permissions"``. It disambiguates similarly named types across
        schemas and is the lookup key for decoders.

        Maintaining the full URI is important when supporting multiple OME
        schema versions; it ensures consumers pick the right interpretation and
        prevents silent drift when the schema evolves.

    ``@id``
        The OMERO database identifier emitted when available on the source
        object. It preserves entity identity across the wire so updates,
        links, and permission checks continue to target the correct row.

        If an object is transient or has no server-side id, ``@id`` is simply
        omitted. Callers can still attach it later after persisting the object.

    RType
        OMERO’s wrapped primitive types (``rlong``, ``rstring``, ``rdouble``,
        and friends). They provide nullability, type hints, and lazy-loading
        semantics on the server side.

        Encoders unwrap these into plain Python values so JSON consumers do not
        need OMERO runtime helpers. When decoding, the library rewraps values
        using OMERO field metadata so the reconstructed object behaves like any
        other OMERO model instance.

    Unit
        Length and Time values represented as instances of the OMERO unit
        classes (for example ``LengthI`` with ``UnitsLength.MICROMETER``).
        Units travel with both a numeric value and symbolic metadata, which is
        essential for downstream calculations and comparisons.

        Encoders expand units into dictionaries with ``@type``, ``Unit``,
        ``Symbol``, and ``Value`` to avoid losing the unit system. Decoders
        rebuild the typed unit instances, keeping subsequent arithmetic
        consistent with OMERO expectations.

    ROI
        Region of Interest. An OMERO container for one or more shapes linked to
        a single image, used to mark objects, measurements, or analysis
        results. ROIs can carry annotations and inherit details like ownership
        and permissions.

        The marshalled form captures the ROI’s name, description, shapes, and
        annotations only if those links are loaded, so you control how much of
        the ROI graph crosses the wire.

    SPW
        Screen/Plate/Well data model used in high-content screening workflows.
        Screens contain plates; plates contain wells; wells can hold multiple
        well samples that point to images.

        Marshal support preserves this hierarchy and the well colour/status
        metadata so plate maps remain meaningful outside OMERO (for example in
        QC dashboards or notebook visualisations).

    LogicalChannel
        The rich metadata attached to an image channel: fluorophore identity,
        excitation/emission wavelengths, acquisition mode, illumination,
        photometric interpretation, ND filter settings, and pinhole size.

        Logical channel data is nested within channels and only included when
        the linked enumerations are loaded. It is critical for downstream
        analysis that relies on spectral separation, scaling, or display
        defaults.
