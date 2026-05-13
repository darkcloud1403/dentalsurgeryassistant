
# Dental Surgical Assistance Pipeline

A research pipeline for processing CBCT/DICOM dental scans into 3D-visualized, analysis-ready tooth geometry. Built as part of a dental surgical assistance research internship.

---

## Motivation & Vision

Dental surgeries like implant placements, extractions, maxillofacial procedures rely heavily on the surgeon's spatial understanding of a patient's anatomy, typically from 2D X-rays or manually reviewed CBCT scans. There's a significant gap between the data available and how intuitively it can be used in the operating room.

The goal of this project is to close that gap.

**Immediate focus:** Build a robust pipeline that takes raw CBCT scan data and produces clean, analysis-ready 3D tooth geometry segmented, processed, and ready for visualization or further computation.

**Broader vision:** Use this pipeline as the foundation for a real-time dental surgical assistance system. The long-term direction includes:

- **AR overlay** — projecting patient-specific tooth and jaw geometry onto AR glasses worn by the surgeon during a procedure
- **Real-time guidance** — live positioning feedback, drill depth assistance, and implant alignment support during surgery
- **Intraoral processing** — integrating real-time camera or scan feeds for in-procedure anatomy tracking

The pipeline being built now DICOM ingestion, segmentation, 3D mesh extraction, crown isolation is the groundwork everything else will build on.

---

## Pipeline Overview

```
CBCT/DICOM Scan
      ↓
  InVesalius        (DICOM → STL: segmentation + HU thresholding)
      ↓
  Blender           (mesh cleanup, materials, rendering)
      ↓
  Python Scripts    (batch processing, geometry extraction, analysis)
      ↓
  Crown Extraction  (isolate crown geometry for surgical planning)
```

---

## Stage 1 — DICOM to STL (InVesalius)

CBCT scans of dental/maxillofacial regions are loaded as DICOM stacks. Bone geometry is isolated using Hounsfield Unit (HU) thresholding to separate hard tissue (teeth, jaw bone) from soft tissue. The segmented volume is then exported as an STL file.

InVesalius was selected over 3D Slicer after testing both tools InVesalius produced cleaner, less noisy meshes for dental CBCT datasets specifically.

**Early exploration:** Before adopting InVesalius, a fully custom Python pipeline was attempted using `pydicom` for DICOM loading, `scikit-image` marching cubes for mesh generation, and `numpy-stl` for STL export. While functional, the output meshes were too noisy for reliable downstream use, which led to switching to InVesalius as the primary conversion tool.

---

## Stage 2 — 3D Visualization (Blender)

The exported STL is imported into Blender for mesh cleanup, material assignment, and rendering.

Key work done in this stage:
- **Mesh cleanup** — fixing inverted normals, removing artifacts from the STL export
- **Materials** — Principled BSDF shader with Transmission Weight for enamel/glass-like appearance (note: Blender 4.0+ replaced the Glass BSDF node with Transmission Weight inside Principled BSDF)
- **Fluid simulation** — water-in-jaw animation for anatomical visualization
- **Rendering** — final scene setup, lighting, and camera positioning for presentation

---

## Stage 3 — Batch Processing

Automated Python scripts to process multiple STL files in bulk without manual intervention for each scan. This was built to handle the volume of patient scans in the dataset efficiently.

---

## Stage 4 — Crown Extraction

A trimesh-based Python script (`extract_crowns.py`) that isolates only the tooth crown region from a full jaw/skull STL by performing a plane slice at the gumline height (Z-axis cutoff).

The script:
- Loads the full jaw STL
- Prints bounding box info to help identify the correct Z cutoff
- Slices above the gumline plane, discarding roots and skull base
- Auto-removes small floating noise fragments post-slice
- Exports a timestamped crown-only STL

Dependencies:
```bash
pip install trimesh numpy shapely rtree mapbox-earcut
```

---

## Stack

| Tool | Purpose |
|---|---|
| [InVesalius](https://invesalius.github.io/) | DICOM → STL conversion and segmentation |
| [Blender](https://www.blender.org/) | 3D visualization, materials, rendering |
| [trimesh](https://trimesh.org/) | Mesh slicing and geometry extraction |
| [pydicom](https://pydicom.github.io/) | DICOM file loading |
| [scikit-image](https://scikit-image.org/) | Marching cubes, image processing |
| [numpy-stl](https://numpy-stl.readthedocs.io/) | STL mesh generation |
| [numpy](https://numpy.org/) | Numerical computation |

---

## Context

Built during a dental surgical assistance research internship. The internship involves working with real CBCT scan data from dental patients, building 3D modeling pipelines for maxillofacial geometry, and supporting surgical planning workflows.

---

*This repository is actively updated as the internship progresses.*
