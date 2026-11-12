"""Export single-mesh OBJ geometry and diffuse PNGs for the object clones."""
import math
import sys
from pathlib import Path

import bpy


def export_asset(source, output):
    bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = bpy.data.objects[source.stem]
    bpy.ops.object.join()
    obj = bpy.context.object
    mesh = obj.data
    materials = list(mesh.materials)
    if not 0 < len(materials) <= 16:
        raise ValueError("The diffuse atlas supports up to 16 palette colors")

    # Give each original material a padded 32-pixel square in a 128px atlas.
    side, tile = 128, 32
    pixels = [0.0] * (side * side * 4)
    for index, material in enumerate(materials):
        x0, y0 = (index % 4) * tile, (index // 4) * tile
        color = list(material.diffuse_color[:3]) + [1.0]
        for y in range(y0, y0 + tile):
            start = (y * side + x0) * 4
            pixels[start:start + tile * 4] = color * tile
    image = bpy.data.images.new(source.stem + "_Diffuse", width=side, height=side, alpha=True)
    image.pixels.foreach_set(pixels)
    image.filepath_raw = str(output / (source.stem + "_Diffuse.png"))
    image.file_format = "PNG"
    image.save()

    for layer in list(mesh.uv_layers):
        mesh.uv_layers.remove(layer)
    uv = mesh.uv_layers.new(name="UVMap")
    for face in mesh.polygons:
        index = face.material_index
        center_x = (index % 4) * tile + tile / 2
        center_y = (index // 4) * tile + tile / 2
        for step, loop in enumerate(face.loop_indices):
            angle = math.tau * step / face.loop_total
            uv.data[loop].uv = ((center_x + 8 * math.cos(angle)) / side,
                                (center_y + 8 * math.sin(angle)) / side)
    mesh.materials.clear()
    bpy.ops.wm.obj_export(filepath=str(output / (source.stem + ".obj")),
                          export_selected_objects=True, export_materials=False,
                          forward_axis="Y", up_axis="Z", export_triangulated_mesh=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:]
    source_dir, output_dir = (Path(arg).resolve() for arg in args)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in ("LifeJournal_Parcel", "LifeJournal_Planner"):
        export_asset(source_dir / (name + ".blend"), output_dir)
