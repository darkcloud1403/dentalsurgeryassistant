import os
import numpy as np
import pydicom
from skimage import measure
from stl import mesh  

import datetime


timestamp  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_STL = rf"C:\Users\Admin\output path\teeth_{timestamp}.stl"

DICOM_DIR   = r"input path"
HU_MIN = 1200
HU_MAX = 3000


def load_dicom_series(dicom_dir):
    slices = []
    for fname in sorted(os.listdir(dicom_dir)):
        if not fname.endswith(".dcm"):
            continue
        fpath = os.path.join(dicom_dir, fname)
        ds = pydicom.dcmread(fpath)
        slices.append(ds)

    
    slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))
    print(f"Loaded {len(slices)} DICOM slices")
    return slices


def build_volume(slices):

    pixel_arrays = []
    for s in slices:
        arr = s.pixel_array.astype(np.float32)

        slope     = float(getattr(s, 'RescaleSlope', 1))
        intercept = float(getattr(s, 'RescaleIntercept', 0))
        arr = arr * slope + intercept
        pixel_arrays.append(arr)

    volume = np.stack(pixel_arrays, axis=0)
    print(f"Volume shape: {volume.shape}")
    print(f"HU range in scan: {volume.min():.0f} to {volume.max():.0f}")
    return volume



def get_spacing(slices):

    ps = slices[0].PixelSpacing
    row_spacing = float(ps[0])
    col_spacing = float(ps[1])


    if len(slices) > 1:
        z0 = float(slices[0].ImagePositionPatient[2])
        z1 = float(slices[1].ImagePositionPatient[2])
        z_spacing = abs(z1 - z0)
    else:
        z_spacing = float(slices[0].SliceThickness)

    spacing = (z_spacing, row_spacing, col_spacing)
    print(f"Voxel spacing (Z, Y, X): {spacing}")
    return spacing


def volume_to_mesh(volume, spacing, hu_min, hu_max):

    mask = (volume >= hu_min) & (volume <= hu_max)

    verts, faces, normals, _ = measure.marching_cubes(
        mask,
        level=0.5,
        spacing=spacing
    )
    print(f"Mesh: {len(verts)} verts, {len(faces)} faces")
    return verts, faces



def save_stl(verts, faces, output_path):
    teeth_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            teeth_mesh.vectors[i][j] = verts[f[j]]

    teeth_mesh.save(output_path)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"Saved STL to: {output_path} ({size_mb:.2f} MB)")



def mesh_report(verts, faces, spacing):
    bbox_min = verts.min(axis=0)
    bbox_max = verts.max(axis=0)
    dims = bbox_max - bbox_min

    print("\n── Mesh Report ──────────────────")
    print(f"  Vertices  : {len(verts)}")
    print(f"  Faces     : {len(faces)}")
    print(f"  Bounding box (mm):")
    print(f"    X: {dims[2]:.1f} mm")
    print(f"    Y: {dims[1]:.1f} mm")
    print(f"    Z: {dims[0]:.1f} mm")
    print(f"  HU range used: {HU_MIN} – {HU_MAX}")
    print("─────────────────────────────────\n")



if __name__ == "__main__":
    print("=== DICOM → STL Pipeline ===\n")

    slices  = load_dicom_series(DICOM_DIR)
    volume  = build_volume(slices)
    spacing = get_spacing(slices)

    verts, faces = volume_to_mesh(volume, spacing, HU_MIN, HU_MAX)
    mesh_report(verts, faces, spacing)
    save_stl(verts, faces, OUTPUT_STL)

    print("Done.")
