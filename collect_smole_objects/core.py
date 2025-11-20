"""
Core functionality for Collect Smole Objects addon.

Handles volume calculations and object processing.
"""

import bpy
import bmesh
from . import utils


def calculate_object_volume(obj, context):
    """
    Calculate the volume of a mesh object using BMesh.

    Handles modifiers by using evaluated depsgraph.
    Transforms mesh to world space for accurate volume.

    Args:
        obj: Blender mesh object
        context: Blender context

    Returns:
        tuple: (bool success, float volume or 0, str error_message)
    """
    # Validate it's a mesh
    success, error = utils.validate_object_is_mesh(obj)
    if not success:
        return False, 0.0, error

    # Validate mesh has geometry
    success, error, mesh = utils.validate_mesh_not_empty(obj, context)
    if not success:
        return False, 0.0, error

    depsgraph = context.evaluated_depsgraph_get()

    try:
        # Transform to world space
        mesh.transform(obj.matrix_world)

        # Calculate volume using BMesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        volume = bm.calc_volume()
        bm.free()

        # Clean up temporary mesh
        obj.evaluated_get(depsgraph).to_mesh_clear()

        # Validate volume
        success, error = utils.validate_volume(volume, obj.name)
        if not success:
            return False, 0.0, error

        return True, volume, ""

    except Exception as e:
        # Clean up on error
        try:
            obj.evaluated_get(depsgraph).to_mesh_clear()
        except:
            pass

        return False, 0.0, f"Error calculating volume for '{obj.name}': {str(e)}"


def collect_smaller_objects(reference_obj, threshold_volume, context, collection_name="Littles"):
    """
    Collect all objects smaller than threshold volume into a collection.

    Args:
        reference_obj: Reference object (to exclude from collection)
        threshold_volume: Volume threshold (objects smaller than this will be collected)
        context: Blender context
        collection_name: Name of target collection (default "Littles")

    Returns:
        dict: Results containing:
            - success: bool
            - collected_count: int
            - skipped_count: int
            - skipped_objects: list of (obj_name, reason) tuples
            - error_message: str
    """
    results = {
        'success': True,
        'collected_count': 0,
        'skipped_count': 0,
        'skipped_objects': [],
        'error_message': ''
    }

    # Get or create target collection
    try:
        target_collection = utils.get_or_create_collection(collection_name, context)
    except Exception as e:
        results['success'] = False
        results['error_message'] = f"Failed to create collection '{collection_name}': {str(e)}"
        return results

    # Process all objects in scene
    for obj in bpy.data.objects:
        # Skip non-mesh objects
        if obj.type != 'MESH':
            continue

        # Skip reference object
        if obj == reference_obj:
            continue

        # Calculate volume
        success, volume, error = calculate_object_volume(obj, context)

        if not success:
            # Skip invalid objects, track them
            results['skipped_count'] += 1
            results['skipped_objects'].append((obj.name, error))
            continue

        # Check if smaller than threshold
        if volume < threshold_volume:
            try:
                utils.move_object_to_collection(obj, target_collection)
                results['collected_count'] += 1
            except Exception as e:
                results['skipped_count'] += 1
                results['skipped_objects'].append((obj.name, f"Failed to move: {str(e)}"))

    return results


def process_reference_object_method(selected_obj, context):
    """
    Process using reference object method (current v1.1 behavior).

    Args:
        selected_obj: Selected reference object
        context: Blender context

    Returns:
        dict: Results from collect_smaller_objects()
    """
    # Calculate reference volume
    success, ref_volume, error = calculate_object_volume(selected_obj, context)

    if not success:
        return {
            'success': False,
            'collected_count': 0,
            'skipped_count': 0,
            'skipped_objects': [],
            'error_message': f"Reference object error: {error}"
        }

    # Collect smaller objects
    results = collect_smaller_objects(selected_obj, ref_volume, context)

    return results
