"""Build editable Life Journal prop models with Blender's Python runtime."""
import sys
from pathlib import Path
import math

import bpy


def material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    return mat


def box(name, dimensions, position, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Rounded edges", "BEVEL")
        mod.width, mod.segments = bevel, 2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def save(output, name):
    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = bpy.data.objects[name]
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / (name + ".blend")), compress=True)


def make_parcel(output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    kraft = material("Kraft cardboard", (0.49, 0.27, 0.12))
    tape = material("Packing tape", (0.72, 0.49, 0.26))
    paper = material("Shipping label", (0.93, 0.88, 0.73))
    ink = material("Label ink", (0.08, 0.09, 0.09))
    box("LifeJournal_Parcel", (0.42, 0.32, 0.23), (0, 0, 0.115), kraft, 0.008)
    box("Tape across lid", (0.418, 0.063, 0.002), (0, 0, 0.230), tape)
    box("Tape across seam", (0.065, 0.318, 0.003), (0, 0, 0.231), tape)
    for side in (-1, 1):
        box("Tape down side", (0.002, 0.063, 0.205), (side * 0.210, 0, 0.115), tape)
    box("Shipping label", (0.11, 0.074, 0.001), (0.105, 0.07, 0.233), paper, 0.0005)
    for index, width in enumerate((.003, .005, .002, .004, .002, .005, .003, .004)):
        box("Barcode stripe", (width, 0.025, 0.001),
            (0.075 + 0.008 * index, 0.059, 0.234), ink)
    save(output, "LifeJournal_Parcel")


def make_planner(output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mint = material("Pastel mint", (0.37, 0.77, 0.59))
    pages = material("Cream pages", (0.94, 0.88, 0.73))
    teal = material("Dark teal title", (0.024, 0.20, 0.20))
    accents = [material(name, rgb) for name, rgb in (
        ("Lavender", (.62, .43, .85)), ("Sky blue", (.26, .66, .93)),
        ("Coral", (.95, .38, .36)), ("Yellow", (.95, .74, .16)),
        ("Turquoise", (.12, .65, .59)),
    )]
    box("LifeJournal_Planner", (.184, .242, .006), (0, 0, .003), mint, .002)
    box("Pages", (.177, .233, .015), (0, 0, .0135), pages, .003)
    box("Front cover", (.184, .242, .006), (0, 0, .024), mint, .002)
    for index in range(10):
        bpy.ops.mesh.primitive_torus_add(
            major_segments=12, minor_segments=6, major_radius=.011,
            minor_radius=.0022, rotation=(math.pi / 2, 0, 0),
            location=(-.089, -.105 + .023 * index, .014))
        ring = bpy.context.object
        ring.name = "Spiral ring"
        ring.data.materials.append(accents[index % len(accents)])
    for index, mat in enumerate(accents):
        box("Planner tab", (.025, .025, .002), (.09, .083 - .035 * index, .017),
            mat, .0008)
    bpy.ops.object.text_add(location=(.010, .033, .0272))
    title = bpy.context.object
    title.name = "Life Journal title"
    title.data.body = "Life\nJournal"
    title.data.align_x = "CENTER"
    title.data.size = .032
    title.data.resolution_u = 4
    title.data.materials.append(teal)
    bpy.ops.object.convert(target="MESH")
    diamond = box("Diamond accent", (.028, .028, .001), (.01, -.061, .0278),
                  accents[3], .0004)
    diamond.rotation_euler.z = math.pi / 4
    save(output, "LifeJournal_Planner")


if __name__ == "__main__":
    output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    make_parcel(output)
    make_planner(output)
