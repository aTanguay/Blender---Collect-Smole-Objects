import bpy
import bmesh

bl_info = {
    "name": "Move Smaller Mesh Objects",
    "author": "ChatGPT ft. Andy Tanguay",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > View Menu > Collect Small Objects",
    "description": "Moves mesh objects smaller than the selected object to the 'Littles' collection",
    "category": "Object",
}


def move_smaller_objects(self, context):
    if len(bpy.context.selected_objects) != 1:
        self.report({'WARNING'}, "Please select exactly one object to compare with others. Anything smaller will be collected.")
        return

    selected_obj = bpy.context.selected_objects[0]

    collection_name = 'Littles'
    if collection_name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        new_collection.hide_viewport = True
    else:
        new_collection = bpy.data.collections[collection_name]

    depsgraph = bpy.context.evaluated_depsgraph_get()
    temp_mesh_selected = selected_obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=False)
    temp_mesh_selected.transform(selected_obj.matrix_world)
    bm_selected = bmesh.new()
    bm_selected.from_mesh(temp_mesh_selected)
    selected_volume = bm_selected.calc_volume()
    bm_selected.free()
    selected_obj.evaluated_get(depsgraph).to_mesh_clear()

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

    bpy.context.view_layer.update()


class OBJECT_OT_move_smaller_objects(bpy.types.Operator):
    bl_idname = "object.move_smaller_objects"
    bl_label = "Collect Smaller Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        move_smaller_objects(self, context)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(OBJECT_OT_move_smaller_objects.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_move_smaller_objects)
    bpy.types.VIEW3D_MT_view.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_move_smaller_objects)
    bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()
