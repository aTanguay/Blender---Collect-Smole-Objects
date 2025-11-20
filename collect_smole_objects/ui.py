"""
UI elements for Collect Smole Objects addon.

Defines operators, panels, and menus.
"""

import bpy
from . import core
from . import utils


class OBJECT_OT_collect_smaller_objects(bpy.types.Operator):
    """Collect objects smaller than selected object by volume"""
    bl_idname = "object.collect_smaller_objects"
    bl_label = "Collect Smaller Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the collect operation."""

        # Validate scene has meshes
        success, error = utils.validate_scene_has_meshes(context)
        if not success:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        # Validate selection
        success, error = utils.validate_selection(context)
        if not success:
            self.report({'WARNING'}, error)
            return {'CANCELLED'}

        selected_obj = context.selected_objects[0]

        # Validate selected object is a mesh
        success, error = utils.validate_object_is_mesh(selected_obj)
        if not success:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        # Process using reference object method
        results = core.process_reference_object_method(selected_obj, context)

        # Check for critical errors
        if not results['success']:
            self.report({'ERROR'}, results['error_message'])
            return {'CANCELLED'}

        # Update view
        context.view_layer.update()

        # Report results to user
        collected = results['collected_count']
        skipped = results['skipped_count']

        if collected > 0:
            if skipped > 0:
                self.report({'INFO'},
                           f"Collected {collected} object(s) to 'Littles' collection. "
                           f"Skipped {skipped} invalid object(s).")
            else:
                self.report({'INFO'},
                           f"Collected {collected} object(s) to 'Littles' collection.")
        else:
            if skipped > 0:
                self.report({'WARNING'},
                           f"No objects collected. Skipped {skipped} invalid object(s).")
            else:
                self.report({'INFO'},
                           "No objects smaller than selected object found.")

        # Log skipped objects to console if any
        if skipped > 0 and results['skipped_objects']:
            print("\n=== Collect Smole Objects: Skipped Objects ===")
            for obj_name, reason in results['skipped_objects']:
                print(f"  - {obj_name}: {reason}")
            print(f"Total skipped: {skipped}\n")

        return {'FINISHED'}


def menu_func(self, context):
    """Add operator to View3D Select menu."""
    self.layout.separator()
    self.layout.operator(OBJECT_OT_collect_smaller_objects.bl_idname)


# List of classes to register
classes = (
    OBJECT_OT_collect_smaller_objects,
)


def register():
    """Register UI classes and append to menu."""
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add to Select menu
    bpy.types.VIEW3D_MT_select_object.append(menu_func)


def unregister():
    """Unregister UI classes and remove from menu."""
    # Remove from Select menu
    bpy.types.VIEW3D_MT_select_object.remove(menu_func)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
