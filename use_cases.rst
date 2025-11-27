Use Cases and Patterns
======================

.. note::
   Terms like :term:`Marshalling`, :term:`Codec`, :term:`ROI`, :term:`SPW`,
   and :term:`LogicalChannel` link to the :doc:`glossary` on first mention.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Notebook exploration
--------------------

- Pull OMERO objects into a Jupyter notebook via BlitzGateway, marshal them,
  and store the JSON alongside derived results (plots, segmentation masks,
  measurements).
- Benefit: notebooks stay lightweight; collaborators without OMERO installed
  can still read the JSON for context.
- Tip: include ``@context`` at the top level so future readers know which
  schema version was used.

Microservices or message queues
-------------------------------

- Encode images, ROIs, or SPW structures to JSON and push them onto a queue
  (e.g. RabbitMQ, SQS) consumed by workers that do not import OMERO.
- Workers can decode if they need real OMERO model objects or read the JSON
  directly to drive processing (e.g. select channels, apply measurements).
- Flow diagram:

  .. code-block:: text

     OMERO object --> Encoder --> JSON payload --> queue --> worker
                                                   |-> Decoder (if needed)
      (attach @context, keep @type)     (gzip optional)    (route by @type)

Metadata snapshots and audits
-----------------------------

- Periodically export projects/datasets/images with ``@context`` for
  long-lived audit logs or reproducibility bundles.
- Advantage: the snapshot is stable even if OMERO server state changes; you
  can diff JSON dumps to track metadata drift.

UI previews
-----------

- Web or desktop clients can request encoded objects and render metadata
  without linking against the OMERO model APIs.
- Keeping ``@type`` intact allows the frontend to route payloads to specific
  UI components (e.g. channel viewer, ROI overlay) without guessing.

Custom ETL pipelines
--------------------

- Combine marshalled metadata with image derivatives in object storage.
- Use units and logical channel fields to drive downstream conversions (e.g.
  normalising wavelengths or pixel sizes before analysis).
- Store permissions and ownership from ``omero:details`` when provenance and
  access control need to be auditable.

Example integrations
--------------------

- **OMERO.web extensions** can request marshalled ROIs and annotations to
  overlay on tiled viewers without embedding the full Python model layer.
- **IDR-style public datasets** often expose metadata snapshots; including
  ``@context`` and ``@type`` keeps them decodable even when consumers are not
  running the same OMERO version.
- **Workflow runners** (e.g. Nextflow/Snakemake stages) can pass marshalled
  payloads between steps to keep channel selections, physical sizes, and
  permissions consistent across tooling stacks.
- **Data portals or catalogues** can index the JSON payloads directly,
  extracting selected fields (owners, tags, wavelengths) for search without
  needing the live OMERO server at query time.
- Always validate against upstream ``omero-marshal`` semantics before
  committing pipelines based solely on this unofficial guide.
