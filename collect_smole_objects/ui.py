"""
UI elements for Collect Smole Objects addon.

Defines operators, panels, properties, and menus.
"""

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, BoolProperty
from bpy.types import PropertyGroup
from . import core
from . import utils
from . import analysis


# Property group to store addon settings and state
class CollectSmoleObjectsProperties(PropertyGroup):
    """Properties for Collect Smole Objects addon."""

    # Threshold method selection
    threshold_method: EnumProperty(
        name="Method",
        description="Threshold calculation method",
        items=[
            ('REFERENCE', "Reference Object", "Use selected object as size reference"),
            ('PERCENTAGE_LARGEST', "% of Largest", "Percentage of largest object volume"),
            ('PERCENTAGE_AVERAGE', "% of Average", "Percentage of average object volume"),
            ('PERCENTILE', "Percentile", "Collect smallest X% of objects"),
            ('ABSOLUTE', "Absolute Volume", "Direct volume input in cubic units"),
        ],
        default='PERCENTILE'
    )

    # Method-specific values
    percentage_value: FloatProperty(
        name="Percentage",
        description="Percentage value (0-100)",
        default=5.0,
        min=0.01,
        max=100.0,
        precision=2,
        subtype='PERCENTAGE'
    )

    percentile_value: IntProperty(
        name="Percentile",
        description="Percentile value - collect smallest X% of objects",
        default=80,
        min=1,
        max=99,
        subtype='PERCENTAGE'
    )

    absolute_volume: FloatProperty(
        name="Volume",
        description="Absolute volume threshold in cubic units",
        default=0.001,
        min=0.0000001,
        max=1000000.0,
        precision=6,
        unit='VOLUME'
    )

    # Scene analysis results (stored for display)
    analysis_done: BoolProperty(
        name="Analysis Done",
        description="Scene has been analyzed",
        default=False
    )

    total_objects: IntProperty(default=0)
    valid_objects: IntProperty(default=0)
    min_volume: FloatProperty(default=0.0)
    max_volume: FloatProperty(default=0.0)
    mean_volume: FloatProperty(default=0.0)
    median_volume: FloatProperty(default=0.0)

    # Preview state
    preview_active: BoolProperty(
        name="Preview Active",
        description="Preview is currently active",
        default=False
    )

    preview_object_count: IntProperty(default=0)
    preview_polygon_count: IntProperty(default=0)
    preview_percentage: FloatProperty(default=0.0)


class OBJECT_OT_analyze_scene(bpy.types.Operator):
    """Analyze scene to gather statistics"""
    bl_idname = "object.collect_smole_analyze"
    bl_label = "Analyze Scene"
    bl_description = "Scan all mesh objects and calculate volume statistics"

    def execute(self, context):
        props = context.scene.collect_smole_props

        # Run scene analysis
        results = analysis.analyze_scene(context)

        if results['total_objects'] == 0:
            self.report({'WARNING'}, "No mesh objects found in scene.")
            return {'CANCELLED'}

        if results['valid_objects'] == 0:
            self.report({'ERROR'}, f"Scene has {results['total_objects']} mesh objects, but none have valid volumes.")
            return {'CANCELLED'}

        # Store results in properties
        props.total_objects = results['total_objects']
        props.valid_objects = results['valid_objects']
        props.min_volume = results['min_volume']
        props.max_volume = results['max_volume']
        props.mean_volume = results['mean_volume']
        props.median_volume = results['median_volume']
        props.analysis_done = True

        # Report success
        self.report({'INFO'},
                   f"Analysis complete: {results['valid_objects']} valid objects "
                   f"(volume range: {utils.format_volume(results['min_volume'])} - "
                   f"{utils.format_volume(results['max_volume'])})")

        # Log invalid objects if any
        if results['invalid_objects'] > 0:
            print("\n=== Collect Smole Objects: Scene Analysis ===")
            print(f"Invalid objects: {results['invalid_objects']}")
            for obj_name, reason in results['invalid_reasons']:
                print(f"  - {obj_name}: {reason}")
            print()

        return {'FINISHED'}


class OBJECT_OT_preview_collection(bpy.types.Operator):
    """Preview which objects will be collected without moving them"""
    bl_idname = "object.collect_smole_preview"
    bl_label = "Preview Collection"
    bl_description = "Select all objects that would be collected with current threshold"

    def execute(self, context):
        props = context.scene.collect_smole_props

        # Calculate threshold based on selected method
        threshold_result = None
        reference_obj = None

        if props.threshold_method == 'REFERENCE':
            # Validate selection
            success, error = utils.validate_selection(context)
            if not success:
                self.report({'WARNING'}, error)
                return {'CANCELLED'}

            reference_obj = context.selected_objects[0]

            # Validate it's a mesh
            success, error = utils.validate_object_is_mesh(reference_obj)
            if not success:
                self.report({'ERROR'}, error)
                return {'CANCELLED'}

            threshold_result = core.calculate_threshold_volume('reference', None, context, reference_obj)

        elif props.threshold_method == 'PERCENTAGE_LARGEST':
            threshold_result = core.calculate_threshold_volume('percentage_largest', props.percentage_value, context)

        elif props.threshold_method == 'PERCENTAGE_AVERAGE':
            threshold_result = core.calculate_threshold_volume('percentage_average', props.percentage_value, context)

        elif props.threshold_method == 'PERCENTILE':
            threshold_result = core.calculate_threshold_volume('percentile', props.percentile_value, context)

        elif props.threshold_method == 'ABSOLUTE':
            threshold_result = core.calculate_threshold_volume('absolute', props.absolute_volume, context)

        # Check if threshold calculation succeeded
        if not threshold_result or not threshold_result['success']:
            error_msg = threshold_result['error_message'] if threshold_result else "Unknown error"
            self.report({'ERROR'}, f"Failed to calculate threshold: {error_msg}")
            return {'CANCELLED'}

        threshold_volume = threshold_result['threshold_volume']

        # Clear current selection
        bpy.ops.object.select_all(action='DESELECT')

        # Select all objects that would be collected
        selected_count = 0
        polygon_count = 0

        for obj in bpy.data.objects:
            # Skip non-mesh objects
            if obj.type != 'MESH':
                continue

            # Skip reference object
            if obj == reference_obj:
                continue

            # Calculate volume
            success, volume, error = core.calculate_object_volume(obj, context)

            if not success:
                continue

            # Check if smaller than threshold
            if volume < threshold_volume:
                obj.select_set(True)
                selected_count += 1

                # Count polygons
                depsgraph = context.evaluated_depsgraph_get()
                try:
                    mesh = obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=False)
                    if mesh:
                        polygon_count += len(mesh.polygons)
                    obj.evaluated_get(depsgraph).to_mesh_clear()
                except:
                    pass

        # Calculate percentage
        mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
        percentage = (selected_count / len(mesh_objects) * 100) if mesh_objects else 0

        # Store preview state
        props.preview_active = True
        props.preview_object_count = selected_count
        props.preview_polygon_count = polygon_count
        props.preview_percentage = percentage

        # Report results
        self.report({'INFO'}, f"Preview: {selected_count} objects selected ({percentage:.1f}% of scene, {polygon_count:,} polygons)")

        return {'FINISHED'}


class OBJECT_OT_clear_preview(bpy.types.Operator):
    """Clear preview selection"""
    bl_idname = "object.collect_smole_clear_preview"
    bl_label = "Clear Preview"
    bl_description = "Deselect all objects and clear preview state"

    def execute(self, context):
        props = context.scene.collect_smole_props

        # Clear selection
        bpy.ops.object.select_all(action='DESELECT')

        # Clear preview state
        props.preview_active = False
        props.preview_object_count = 0
        props.preview_polygon_count = 0
        props.preview_percentage = 0.0

        self.report({'INFO'}, "Preview cleared")

        return {'FINISHED'}


class OBJECT_OT_collect_with_method(bpy.types.Operator):
    """Collect objects using selected threshold method"""
    bl_idname = "object.collect_smole_execute"
    bl_label = "Collect Objects"
    bl_description = "Collect objects smaller than threshold using selected method"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.collect_smole_props

        # Calculate threshold based on selected method
        threshold_result = None
        reference_obj = None

        if props.threshold_method == 'REFERENCE':
            # Validate selection
            success, error = utils.validate_selection(context)
            if not success:
                self.report({'WARNING'}, error)
                return {'CANCELLED'}

            reference_obj = context.selected_objects[0]

            # Validate it's a mesh
            success, error = utils.validate_object_is_mesh(reference_obj)
            if not success:
                self.report({'ERROR'}, error)
                return {'CANCELLED'}

            threshold_result = core.calculate_threshold_volume('reference', None, context, reference_obj)

        elif props.threshold_method == 'PERCENTAGE_LARGEST':
            threshold_result = core.calculate_threshold_volume('percentage_largest', props.percentage_value, context)

        elif props.threshold_method == 'PERCENTAGE_AVERAGE':
            threshold_result = core.calculate_threshold_volume('percentage_average', props.percentage_value, context)

        elif props.threshold_method == 'PERCENTILE':
            threshold_result = core.calculate_threshold_volume('percentile', props.percentile_value, context)

        elif props.threshold_method == 'ABSOLUTE':
            threshold_result = core.calculate_threshold_volume('absolute', props.absolute_volume, context)

        # Check if threshold calculation succeeded
        if not threshold_result or not threshold_result['success']:
            error_msg = threshold_result['error_message'] if threshold_result else "Unknown error"
            self.report({'ERROR'}, f"Failed to calculate threshold: {error_msg}")
            return {'CANCELLED'}

        threshold_volume = threshold_result['threshold_volume']

        # Collect objects using the threshold
        results = core.collect_smaller_objects(reference_obj, threshold_volume, context)

        # Check for critical errors
        if not results['success']:
            self.report({'ERROR'}, results['error_message'])
            return {'CANCELLED'}

        # Clear preview state (since we just executed the operation)
        props.preview_active = False
        props.preview_object_count = 0
        props.preview_polygon_count = 0
        props.preview_percentage = 0.0

        # Update view
        context.view_layer.update()

        # Report results to user
        collected = results['collected_count']
        skipped = results['skipped_count']

        # Build detailed message
        method_info = self._get_method_description(props.threshold_method, threshold_result)

        if collected > 0:
            msg = f"Collected {collected} object(s) using {method_info}."
            if skipped > 0:
                msg += f" Skipped {skipped} invalid object(s)."
            self.report({'INFO'}, msg)
        else:
            if skipped > 0:
                self.report({'WARNING'},
                           f"No objects collected. Skipped {skipped} invalid object(s).")
            else:
                self.report({'INFO'},
                           f"No objects smaller than threshold ({utils.format_volume(threshold_volume)}) found.")

        # Log skipped objects to console if any
        if skipped > 0 and results['skipped_objects']:
            print("\n=== Collect Smole Objects: Skipped Objects ===")
            for obj_name, reason in results['skipped_objects']:
                print(f"  - {obj_name}: {reason}")
            print(f"Total skipped: {skipped}\n")

        return {'FINISHED'}

    def _get_method_description(self, method, result):
        """Generate human-readable method description."""
        if method == 'REFERENCE':
            return f"reference object '{result['metadata']['reference_object']}'"
        elif method == 'PERCENTAGE_LARGEST':
            return f"{result['metadata']['percentage']}% of largest"
        elif method == 'PERCENTAGE_AVERAGE':
            return f"{result['metadata']['percentage']}% of average"
        elif method == 'PERCENTILE':
            return f"{result['metadata']['percentile']}th percentile"
        elif method == 'ABSOLUTE':
            return f"absolute threshold {utils.format_volume(result['metadata']['absolute_volume'])}"
        return method


class OBJECT_OT_collect_smaller_objects(bpy.types.Operator):
    """Collect objects smaller than selected object by volume (legacy operator for menu)"""
    bl_idname = "object.collect_smaller_objects"
    bl_label = "Collect Smaller Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the collect operation using reference object method."""

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


class VIEW3D_PT_collect_smole_objects(bpy.types.Panel):
    """Panel for Collect Smole Objects in 3D Viewport sidebar"""
    bl_label = "Collect Smole Objects"
    bl_idname = "VIEW3D_PT_collect_smole_objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Collect"

    def draw(self, context):
        layout = self.layout
        props = context.scene.collect_smole_props

        # Scene Analysis Section
        box = layout.box()
        box.label(text="Scene Analysis", icon='VIEWZOOM')

        row = box.row()
        row.operator("object.collect_smole_analyze", icon='PLAY')

        if props.analysis_done:
            col = box.column(align=True)
            col.label(text=f"Objects: {props.valid_objects} / {props.total_objects}", icon='OBJECT_DATA')
            col.label(text=f"Min: {utils.format_volume(props.min_volume)}")
            col.label(text=f"Max: {utils.format_volume(props.max_volume)}")
            col.label(text=f"Mean: {utils.format_volume(props.mean_volume)}")
            col.label(text=f"Median: {utils.format_volume(props.median_volume)}")

        # Threshold Method Section
        box = layout.box()
        box.label(text="Threshold Method", icon='SETTINGS')

        box.prop(props, "threshold_method", text="")

        # Dynamic controls based on selected method
        if props.threshold_method == 'REFERENCE':
            box.label(text="Select one mesh object", icon='INFO')

        elif props.threshold_method in ('PERCENTAGE_LARGEST', 'PERCENTAGE_AVERAGE'):
            box.prop(props, "percentage_value", slider=True)

        elif props.threshold_method == 'PERCENTILE':
            box.prop(props, "percentile_value", slider=True)
            if props.analysis_done:
                # Calculate preview info
                obj_count = int((props.percentile_value / 100.0) * props.valid_objects)
                box.label(text=f"≈ {obj_count} smallest objects", icon='OBJECT_DATA')

        elif props.threshold_method == 'ABSOLUTE':
            box.prop(props, "absolute_volume")

        # Preview Section
        box = layout.box()
        box.label(text="Preview", icon='HIDE_OFF')

        row = box.row(align=True)
        row.operator("object.collect_smole_preview", icon='VIEWZOOM')
        row.operator("object.collect_smole_clear_preview", text="Clear", icon='X')

        # Show preview statistics if active
        if props.preview_active:
            col = box.column(align=True)
            col.separator()
            col.label(text=f"Objects: {props.preview_object_count}", icon='OBJECT_DATA')
            col.label(text=f"Polygons: {props.preview_polygon_count:,}")
            col.label(text=f"Percentage: {props.preview_percentage:.1f}%")

        # Execute Section
        box = layout.box()
        box.label(text="Execute", icon='PLAY')

        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("object.collect_smole_execute", icon='CHECKMARK')


def menu_func(self, context):
    """Add operator to View3D Select menu (legacy support)."""
    self.layout.separator()
    self.layout.operator(OBJECT_OT_collect_smaller_objects.bl_idname)


# List of classes to register
classes = (
    CollectSmoleObjectsProperties,
    OBJECT_OT_analyze_scene,
    OBJECT_OT_preview_collection,
    OBJECT_OT_clear_preview,
    OBJECT_OT_collect_with_method,
    OBJECT_OT_collect_smaller_objects,
    VIEW3D_PT_collect_smole_objects,
)


def register():
    """Register UI classes and append to menu."""
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register property group
    bpy.types.Scene.collect_smole_props = bpy.props.PointerProperty(type=CollectSmoleObjectsProperties)

    # Add to Select menu (legacy support)
    bpy.types.VIEW3D_MT_select_object.append(menu_func)


def unregister():
    """Unregister UI classes and remove from menu."""
    # Remove from Select menu
    bpy.types.VIEW3D_MT_select_object.remove(menu_func)

    # Unregister property group
    del bpy.types.Scene.collect_smole_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
