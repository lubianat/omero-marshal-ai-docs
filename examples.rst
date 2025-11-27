Payload Examples
================

.. note::
   Unofficial, AI-generated companion to the upstream ``omero-marshal`` docs.

Sometimes it is faster to learn by seeing complete payloads. The snippets
below illustrate what the encoders emit for common objects (assuming schema
2016-06). Fields omitted here were ``None`` or not loaded in the source object.

Image with primary pixels and channels
--------------------------------------

.. code-block:: json

    {
      "@context": {
        "@vocab": "http://www.openmicroscopy.org/Schemas/OME/2016-06#",
        "omero": "http://www.openmicroscopy.org/Schemas/OMERO/2016-06#"
      },
      "@type": "Image",
      "@id": 1,
      "AcquisitionDate": 1,
      "Description": "image_description_1",
      "Name": "image_name_1",
      "Pixels": {
        "@type": "Pixels",
        "@id": 1,
        "PhysicalSizeX": {
          "@type": "Length",
          "Unit": "MICROMETER",
          "Symbol": "um",
          "Value": 1.0
        },
        "SizeX": 1,
        "SizeY": 2,
        "SizeZ": 3,
        "SizeC": 4,
        "SizeT": 5,
        "Channels": [
          {
            "@type": "Channel",
            "@id": 1,
            "Color": -16711681,
            "omero:LogicalChannelId": 1,
            "Name": "GFP/488"
          }
        ],
        "Type": {
          "@type": "PixelType",
          "value": "bit"
        },
        "DimensionOrder": {
          "@type": "DimensionOrder",
          "value": "XYZCT"
        }
      }
    }

ROI with shapes and annotations
-------------------------------

.. code-block:: json

    {
      "@context": {
        "@vocab": "http://www.openmicroscopy.org/Schemas/OME/2016-06#",
        "omero": "http://www.openmicroscopy.org/Schemas/OMERO/2016-06#"
      },
      "@type": "ROI",
      "@id": 1,
      "Name": "the_name",
      "Description": "the_description",
      "Shapes": [
        {
          "@type": "Ellipse",
          "@id": 1,
          "x": 1.0,
          "y": 2.0,
          "radiusX": 3.0,
          "radiusY": 4.0,
          "FillColor": -1,
          "StrokeColor": -65536,
          "TheC": 1,
          "TheT": 2,
          "TheZ": 3
        }
      ],
      "Annotations": [
        {
          "@type": "MapAnnotation",
          "Namespace": "map_annotation",
          "Value": [
            ["a", "1"],
            ["b", "2"]
          ]
        }
      ]
    }

Plate and wells (SPW excerpt)
-----------------------------

.. code-block:: json

    {
      "@context": {
        "@vocab": "http://www.openmicroscopy.org/Schemas/OME/2016-06#",
        "omero": "http://www.openmicroscopy.org/Schemas/OMERO/2016-06#"
      },
      "@type": "Plate",
      "@id": 5,
      "Name": "plate_name_5",
      "Columns": 12,
      "Rows": 8,
      "WellOriginX": {
        "@type": "Length",
        "Unit": "REFERENCEFRAME",
        "Symbol": "reference frame",
        "Value": 0.1
      },
      "Wells": [
        {
          "@type": "Well",
          "@id": 7,
          "Column": 2,
          "Row": 1,
          "Color": -16777216,
          "omero:status": "the_status",
          "WellSamples": [
            {
              "@type": "WellSample",
              "@id": 9,
              "Image": {
                "@type": "Image",
                "@id": 1,
                "Name": "image_name_1"
              }
            }
          ]
        }
      ]
    }

Permissions block
-----------------

.. code-block:: json

    {
      "@type": "omero:Permissions",
      "perm": "rwrwrw",
      "canAnnotate": true,
      "canDelete": true,
      "canEdit": true,
      "canLink": true,
      "isGroupAnnotate": true,
      "isGroupRead": true,
      "isGroupWrite": true,
      "isUserRead": true,
      "isUserWrite": true,
      "isWorldRead": true,
      "isWorldWrite": true
    }

Details and external info
-------------------------

.. code-block:: json

    {
      "@type": "omero:Details",
      "owner": {
        "@type": "Experimenter",
        "@id": 1,
        "FirstName": "the_firstName",
        "LastName": "the_lastName"
      },
      "group": {
        "@type": "ExperimenterGroup",
        "@id": 1,
        "Name": "the_name"
      },
      "permissions": {
        "@type": "omero:Permissions",
        "perm": "rwrwrw"
      },
      "externalInfo": {
        "@type": "omero:ExternalInfo",
        "EntityId": 123,
        "EntityType": "test",
        "Lsid": "ABCDEF",
        "Uuid": "f90a1fd5-275c-4d14-82b3-87b5ef0f07de"
      }
    }

These snapshots align with the upstream unit tests; they are a quick reference
when eyeballing payloads or debugging round-trips. The exact outputs depend on
upstream ``omero-marshal`` and OMERO schema versions—verify against the
upstream repository when in doubt.
