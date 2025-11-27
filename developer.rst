Developer Guide
===============

.. note::
   This guide assumes you are comfortable with :term:`Marshalling`,
   :term:`Codec` patterns, and the :doc:`architecture`.
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Create a new codec (step-by-step)
---------------------------------

1. **Pick schema URIs**: Identify the schema version and the fully qualified
   type (e.g. ``http://www.openmicroscopy.org/Schemas/OME/2016-06#NewType``).
2. **Encoder module** (``omero_marshal/encode/encoders/<name>.py``):

   .. code-block:: python

      from ... import SCHEMA_VERSION
      from .. import Encoder
      from omero.model import NewTypeI

      class NewType201606Encoder(Encoder):
          TYPE = "http://www.openmicroscopy.org/Schemas/OME/2016-06#NewType"
          def encode(self, obj, include_context=None):
              v = super(NewType201606Encoder, self).encode(obj, include_context)
              self.set_if_not_none(v, "Name", obj.name)
              return v

      encoder = (NewTypeI, NewType201606Encoder)

3. **Decoder module** (``omero_marshal/decode/decoders/<name>.py``):

   .. code-block:: python

      from ... import SCHEMA_VERSION
      from .. import Decoder
      from omero.model import NewTypeI

      class NewType201606Decoder(Decoder):
          TYPE = "http://www.openmicroscopy.org/Schemas/OME/2016-06#NewType"
          OMERO_CLASS = NewTypeI
          def decode(self, data):
              v = super(NewType201606Decoder, self).decode(data)
              self.set_property(v, "name", data.get("Name"))
              return v

      decoder = (NewType201606Decoder.TYPE, NewType201606Decoder)

4. **Handle schema forks**: If 2015-01 differs, add a sibling class with
   adjusted fields and a conditional ``encoder = (...)`` / ``decoder = (...)``
   based on ``SCHEMA_VERSION``.
5. **Tests**: Mirror ``tests/unit`` style—construct a minimal object, encode,
   assert dictionary equality, decode, assert field equivalence. Include
   unloaded variants.

Debugging registration
----------------------

- Import ``omero_marshal`` in a Python shell and inspect ``ENCODERS`` /
  ``DECODERS`` to confirm your codec appears.
- If ``get_encoder``/``get_decoder`` returns ``None``, check the ``encoder`` /
  ``decoder`` tuples are exported at module scope and the ``TYPE`` URI matches
  your schema.

Backward/forward compatibility tips
-----------------------------------

- **Do not delete older codecs**; add new classes for new schema versions and
  register based on ``SCHEMA_VERSION``.
- **Log clearly** for unsupported versions so CI fails fast when dependencies
  change.
- **Be explicit with units**: adding new unit types should raise until handled.

Marshalling map (reference)
---------------------------

.. code-block:: text

   Project
     └─ Dataset(s)
         └─ Image(s)
             └─ Pixels
                 └─ Channel(s)
                     └─ LogicalChannel
   ROI
     └─ Shape(s)
   Screen
     └─ Plate(s)
         └─ Well(s)
             └─ WellSample(s) -> Image
   Details
     ├─ Owner (Experimenter)
     ├─ Group (ExperimenterGroup)
     ├─ Permissions
     └─ ExternalInfo

Common pitfalls (and fixes)
---------------------------

- **Forgetting ``include_context=False`` on nested encodes**: leads to repeated
  contexts and larger payloads. Pass ``False`` when encoding children.
- **Using unloaded links**: you may get empty annotations/shapes; load the
  links explicitly before encoding.
- **Mismatched ``@type``**: ensure the decoder’s ``TYPE`` string exactly
  matches what the encoder emits; schema URIs differ between 2015-01 and
  2016-06.
- **Units not handled**: adding new unit classes without encoder support will
  raise. Extend ``encode_unit`` / ``to_unit`` and add tests.
- **Permissions leakage**: drop or scrub ``omero:details`` if consumers should
  not inherit ownership/permissions from the source object.

Contributor checklist
---------------------

- [ ] Added paired encoder/decoder with correct ``TYPE``/``OMERO_CLASS``.
- [ ] Included schema-conditional registration if applicable.
- [ ] Added unit tests for encode/decode (loaded and unloaded variants).
- [ ] Verified colours, units, transforms round-trip correctly where relevant.
- [ ] Documented new behaviour in the docs if it changes payload shape.

Docs and CI tips
----------------

- Build docs locally with ``sphinx-build -b html docs docs/_build/html``.
- Read the Docs is configured via ``.readthedocs.yaml`` and
  ``docs/requirements.txt``; pushes will trigger RTD builds if hooked up.
- Keep examples in sync with upstream ``tests/unit`` to avoid drift between
  docs and actual payloads.
