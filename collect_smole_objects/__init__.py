# Collect Smole Objects - Blender Extension
# Modern extension format for Blender 4.2+
# For legacy addon support (Blender 2.80+), see dev/Blender_CollectSmoleObjects_v01.py

import bpy
import bmesh

# Note: bl_info is no longer needed in Blender 4.2+ extensions
# All metadata is now in blender_manifest.toml
# This bl_info is kept commented for reference only
#
# bl_info = {
#     "name": "Collect Smole Objects",
#     "author": "ChatGPT ft. Andy Tanguay",
#     "version": (1, 1, 0),
#     "blender": (4, 2, 0),
#     "location": "View3D > Select Menu > Collect Smaller Objects",
#     "description": "Collects and hides mesh objects smaller than the selected object by volume",
#     "category": "Object",
# }


def move_smaller_objects(self, context):
    """
    Move all mesh objects smaller than the selected object to 'Littles' collection.

    Uses BMesh volume calculation to accurately determine object size.
    """
    if len(bpy.context.selected_objects) != 1:
        self.report({'WARNING'}, "Please select exactly one object to compare with others. Anything smaller will be collected.")
        return

    selected_obj = bpy.context.selected_objects[0]

    # Validate selected object is a mesh
    if selected_obj.type != 'MESH':
        self.report({'ERROR'}, "Selected object must be a mesh object.")
        return

    collection_name = 'Littles'
    if collection_name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        new_collection.hide_viewport = True
    else:
        new_collection = bpy.data.collections[collection_name]

    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Calculate reference object volume
    temp_mesh_selected = selected_obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=False)
    temp_mesh_selected.transform(selected_obj.matrix_world)
    bm_selected = bmesh.new()
    bm_selected.from_mesh(temp_mesh_selected)
    selected_volume = bm_selected.calc_volume()
    bm_selected.free()
    selected_obj.evaluated_get(depsgraph).to_mesh_clear()

    # Check if reference volume is valid
    if selected_volume <= 0:
        self.report({'ERROR'}, "Selected object has invalid volume (zero or negative). Cannot use as reference.")
        return

    moved_count = 0

    # Process all mesh objects in scene
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != selected_obj:
            temp_mesh = obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=False)
            temp_mesh.transform(obj.matrix_world)

            bm = bmesh.new()
            bm.from_mesh(temp_mesh)
            volume = bm.calc_volume()
            bm.free()

            obj.evaluated_get(depsgraph).to_mesh_clear()

            if volume < selected_volume:
                for col in obj.users_collection:
                    col.objects.unlink(obj)
                new_collection.objects.link(obj)
                moved_count += 1

    bpy.context.view_layer.update()

    # Report results to user
    if moved_count > 0:
        self.report({'INFO'}, f"Collected {moved_count} object(s) to '{collection_name}' collection.")
    else:
        self.report({'INFO'}, "No objects smaller than selected object found.")


class OBJECT_OT_move_smaller_objects(bpy.types.Operator):
    """Collect objects smaller than selected object by volume"""
    bl_idname = "object.move_smaller_objects"
    bl_label = "Collect Smaller Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        move_smaller_objects(self, context)
        return {'FINISHED'}


def menu_func(self, context):
    """Add operator to View3D Select menu"""
    self.layout.separator()
    self.layout.operator(OBJECT_OT_move_smaller_objects.bl_idname)


def register():
    """Register addon classes and append to menu"""
    bpy.utils.register_class(OBJECT_OT_move_smaller_objects)
    bpy.types.VIEW3D_MT_select_object.append(menu_func)


def unregister():
    """Unregister addon classes and remove from menu"""
    bpy.utils.unregister_class(OBJECT_OT_move_smaller_objects)
    bpy.types.VIEW3D_MT_select_object.remove(menu_func)


if __name__ == "__main__":
    register()
