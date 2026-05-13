import bpy
import math
import os


STL_FOLDER  = r"C:\Users\stl_files"
RENDER_FOLDER = r"C:\Users\renders"


os.makedirs(RENDER_FOLDER, exist_ok=True)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)


def import_stl(path):
    bpy.ops.wm.stl_import(filepath=path)
    obj = bpy.context.active_object
    obj.name = "Teeth"
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    bpy.ops.object.shade_smooth()
    return obj


def apply_tooth_material(obj):
    mat = bpy.data.materials.new(name="EnamelMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value         = (0.92, 0.89, 0.82, 1)
    bsdf.inputs["Roughness"].default_value          = 0.25
    bsdf.inputs["Specular IOR Level"].default_value = 0.5
    bsdf.inputs["Subsurface Weight"].default_value  = 0.15
    bsdf.inputs["Subsurface Radius"].default_value  = (0.8, 0.7, 0.6)
    bsdf.inputs["Subsurface Scale"].default_value   = 0.5
    obj.data.materials.append(mat)


def setup_lighting():
    bpy.ops.object.light_add(type='AREA', location=(2, -2, 4))
    key = bpy.context.active_object
    key.data.energy = 600
    key.data.size   = 3.0
    key.data.color  = (1.0, 0.97, 0.90)
    key.rotation_euler = (math.radians(45), 0, math.radians(30))

    bpy.ops.object.light_add(type='AREA', location=(-3, 1, 2))
    fill = bpy.context.active_object
    fill.data.energy = 150
    fill.data.size   = 4.0
    fill.data.color  = (0.85, 0.90, 1.0)

    bpy.ops.object.light_add(type='SPOT', location=(0, 4, 3))
    rim = bpy.context.active_object
    rim.data.energy    = 300
    rim.data.spot_size = math.radians(40)
    rim.data.color     = (1.0, 1.0, 1.0)
    rim.rotation_euler = (math.radians(-35), 0, math.radians(180))

    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value    = (0.95, 0.95, 0.95, 1)
    bg.inputs["Strength"].default_value = 0.3


def setup_camera(obj):
    bbox = [obj.matrix_world @ v.co for v in obj.data.vertices]
    xs   = [v.x for v in bbox]
    ys   = [v.y for v in bbox]
    zs   = [v.z for v in bbox]
    size = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
    dist = size * 2.0

    bpy.ops.object.camera_add(location=(dist*0.8, -dist*0.8, dist*0.5))
    cam = bpy.context.active_object
    cam.name = "DentalCam"
    cam.data.lens = 100
    bpy.context.scene.camera = cam

    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target     = obj
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis    = 'UP_Y'


def setup_render(output_path):
    scene = bpy.context.scene
    scene.render.engine                     = 'CYCLES'
    scene.cycles.samples                    = 256
    scene.render.resolution_x               = 1920
    scene.render.resolution_y               = 1080
    scene.render.filepath                   = output_path
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent           = True




def batch_render():
    stl_files = [
        f for f in os.listdir(STL_FOLDER)
        if f.endswith(".stl")
    ]

    if not stl_files:
        print("No STL files found in folder.")
        return

    print(f"Found {len(stl_files)} STL files\n")

    for i, filename in enumerate(stl_files):
        stl_path    = os.path.join(STL_FOLDER, filename)
        render_name = os.path.splitext(filename)[0] + "_render.png"
        render_path = os.path.join(RENDER_FOLDER, render_name)

        print(f"[{i+1}/{len(stl_files)}] Rendering: {filename}")

        clear_scene()
        obj = import_stl(stl_path)
        apply_tooth_material(obj)
        setup_lighting()
        setup_camera(obj)
        setup_render(render_path)

        bpy.ops.render.render(write_still=True)

        print(f"    Saved → {render_path}\n")

    print(f"Done! All renders saved to: {RENDER_FOLDER}")


batch_render()
