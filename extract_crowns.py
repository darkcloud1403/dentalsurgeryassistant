
import trimesh
import numpy as np

from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_STL = rf"C:\Users\dental_pipeline\stl_files\crowns_{timestamp}.stl"

INPUT_STL  = r"C:\Users\Admin\Desktop\c"

Z_CUTOFF = 25

def main():
    print(f"Loading {INPUT_STL} ...")

    jaw = trimesh.load(INPUT_STL)

    if not isinstance(jaw, trimesh.Trimesh):
        jaw = trimesh.util.concatenate(
            list(jaw.geometry.values())
        )

    print(
        f"Mesh loaded — {len(jaw.vertices):,} vertices, {len(jaw.faces):,} faces"
    )

    print(f"Bounding box (min → max):")

    print(
        f"  X: {jaw.bounds[0][0]:.2f} → {jaw.bounds[1][0]:.2f}"
    )

    print(
        f"  Y: {jaw.bounds[0][1]:.2f} → {jaw.bounds[1][1]:.2f}"
    )

    print(
        f"  Z: {jaw.bounds[0][2]:.2f} → {jaw.bounds[1][2]:.2f}"
    )

    if Z_CUTOFF is None:
        print("\n⚠  Z_CUTOFF is not set.")
        print("Look at the Z range above.")
        print(
            "Crowns are near the TOP of the jaw (higher Z values)."
        )

        print(
            "Pick a Z value that sits at the gumline and set Z_CUTOFF in the script."
        )

        return

    print(
        f"\nCutting at Z = {Z_CUTOFF} (keeping everything above) ..."
    )

    crown = jaw.slice_plane(
        plane_origin=[0, 0, Z_CUTOFF],
        plane_normal=[0, 0, -1],
        cap=True
    )

    if crown is None or len(crown.faces) == 0:
        print(
            "❌ Result is empty. Try a lower Z_CUTOFF value."
        )

        return

    print(
        f"Crown mesh — {len(crown.vertices):,} vertices, {len(crown.faces):,} faces"
    )

    components = crown.split(only_watertight=False)

    if len(components) > 1:
        print(
            f"Found {len(components)} disconnected components — keeping largest ones ..."
        )

        max_faces = max(
            len(c.faces) for c in components
        )

        threshold = max_faces * 0.01

        kept = [
            c for c in components
            if len(c.faces) >= threshold
        ]

        crown = trimesh.util.concatenate(kept)

        print(
            f"Kept {len(kept)} components → {len(crown.faces):,} faces"
        )

    crown.export(OUTPUT_STL)

    print(f"\nSaved to {OUTPUT_STL}")

if __name__ == "__main__":
    main()
