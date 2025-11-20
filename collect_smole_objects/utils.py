"""
Utility functions for Collect Smole Objects addon.

Provides validation, error checking, and helper functions.
"""

import bpy


def validate_scene_has_meshes(context):
    """
    Check if scene has any mesh objects.

    Returns:
        tuple: (bool success, str error_message)
    """
    mesh_count = sum(1 for obj in context.scene.objects if obj.type == 'MESH')

    if mesh_count == 0:
        return False, "Scene contains no mesh objects to process."

    return True, ""


def validate_selection(context):
    """
    Validate that exactly one object is selected.

    Returns:
        tuple: (bool success, str error_message)
    """
    selected_count = len(context.selected_objects)

    if selected_count == 0:
        return False, "No object selected. Please select one mesh object to use as reference."

    if selected_count > 1:
        return False, f"Please select exactly one object (you have {selected_count} selected)."

    return True, ""


def validate_object_is_mesh(obj):
    """
    Validate that an object is a mesh type.

    Args:
        obj: Blender object to validate

    Returns:
        tuple: (bool success, str error_message)
    """
    if obj.type != 'MESH':
        return False, f"Selected object '{obj.name}' is a {obj.type}, not a MESH. Please select a mesh object."

    return True, ""


def validate_mesh_not_empty(obj, context):
    """
    Validate that a mesh object has geometry.

    Args:
        obj: Blender mesh object
        context: Blender context

    Returns:
        tuple: (bool success, str error_message, evaluated_mesh or None)
    """
    depsgraph = context.evaluated_depsgraph_get()

    try:
        mesh = obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=False)

        if mesh is None:
            return False, f"Object '{obj.name}' has no mesh data.", None

        if len(mesh.vertices) == 0:
            obj.evaluated_get(depsgraph).to_mesh_clear()
            return False, f"Object '{obj.name}' has no vertices (empty mesh).", None

        return True, "", mesh

    except Exception as e:
        return False, f"Error evaluating mesh for '{obj.name}': {str(e)}", None


def validate_volume(volume, obj_name="object"):
    """
    Validate that a calculated volume is valid (positive, non-zero).

    Args:
        volume: Calculated volume value
        obj_name: Name of object for error message

    Returns:
        tuple: (bool success, str error_message)
    """
    if volume <= 0:
        if volume == 0:
            return False, f"Object '{obj_name}' has zero volume (possibly 2D/planar geometry)."
        else:
            return False, f"Object '{obj_name}' has invalid negative volume."

    return True, ""


def get_or_create_collection(collection_name, context, hide_viewport=True):
    """
    Get existing collection or create new one.

    Args:
        collection_name: Name of collection
        context: Blender context
        hide_viewport: Whether to hide collection in viewport (default True)

    Returns:
        bpy.types.Collection: The collection
    """
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]

    new_collection = bpy.data.collections.new(collection_name)
    context.scene.collection.children.link(new_collection)
    new_collection.hide_viewport = hide_viewport

    return new_collection


def move_object_to_collection(obj, target_collection):
    """
    Move an object to a target collection, removing from all others.

    Args:
        obj: Blender object to move
        target_collection: Target collection
    """
    # Unlink from all current collections
    for col in obj.users_collection:
        col.objects.unlink(obj)

    # Link to target collection
    target_collection.objects.link(obj)


def format_volume(volume):
    """
    Format volume for display with appropriate units.

    Args:
        volume: Volume value in cubic Blender units

    Returns:
        str: Formatted volume string
    """
    if volume < 0.000001:
        return f"{volume * 1e9:.4f} mm³"
    elif volume < 0.001:
        return f"{volume * 1e6:.4f} mm³"
    elif volume < 1.0:
        return f"{volume * 1000:.4f} cm³"
    else:
        return f"{volume:.4f} m³"
