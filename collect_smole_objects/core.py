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


def process_percentage_method(percentage, base='largest', context=None, exclude_obj=None):
    """
    Calculate threshold as percentage of largest or average object.

    Args:
        percentage: Percentage value (e.g., 5 for 5%)
        base: 'largest' or 'average' (default 'largest')
        context: Blender context
        exclude_obj: Object to exclude from calculations (optional)

    Returns:
        dict: Results containing:
            - success: bool
            - threshold_volume: float
            - base_volume: float (the largest or average volume)
            - error_message: str
    """
    from . import analysis

    results = {
        'success': False,
        'threshold_volume': 0.0,
        'base_volume': 0.0,
        'error_message': ''
    }

    if percentage <= 0 or percentage > 100:
        results['error_message'] = f"Invalid percentage: {percentage}. Must be between 0 and 100."
        return results

    # Analyze scene to get volumes
    scene_analysis = analysis.analyze_scene(context)

    if scene_analysis['valid_objects'] == 0:
        results['error_message'] = "No valid mesh objects found in scene."
        return results

    # Calculate base volume
    if base == 'largest':
        base_volume = scene_analysis['max_volume']
    elif base == 'average':
        base_volume = scene_analysis['mean_volume']
    else:
        results['error_message'] = f"Invalid base '{base}'. Must be 'largest' or 'average'."
        return results

    # Calculate threshold
    threshold = base_volume * (percentage / 100.0)

    results['success'] = True
    results['threshold_volume'] = threshold
    results['base_volume'] = base_volume

    return results


def process_absolute_volume_method(volume_value):
    """
    Use direct volume input as threshold.

    Args:
        volume_value: Volume threshold in cubic units

    Returns:
        dict: Results containing:
            - success: bool
            - threshold_volume: float
            - error_message: str
    """
    results = {
        'success': False,
        'threshold_volume': 0.0,
        'error_message': ''
    }

    if volume_value <= 0:
        results['error_message'] = f"Invalid volume: {volume_value}. Must be positive."
        return results

    results['success'] = True
    results['threshold_volume'] = volume_value

    return results


def process_percentile_method(percentile, context=None):
    """
    Calculate threshold to collect smallest X% of objects.

    Args:
        percentile: Percentile value (e.g., 20 for smallest 20%)
        context: Blender context

    Returns:
        dict: Results containing:
            - success: bool
            - threshold_volume: float
            - objects_in_percentile: int (how many objects this represents)
            - error_message: str
    """
    from . import analysis

    results = {
        'success': False,
        'threshold_volume': 0.0,
        'objects_in_percentile': 0,
        'error_message': ''
    }

    if percentile <= 0 or percentile > 100:
        results['error_message'] = f"Invalid percentile: {percentile}. Must be between 0 and 100."
        return results

    # Analyze scene to get percentiles
    scene_analysis = analysis.analyze_scene(context)

    if scene_analysis['valid_objects'] == 0:
        results['error_message'] = "No valid mesh objects found in scene."
        return results

    # Get or calculate the percentile threshold
    if percentile in scene_analysis['percentiles']:
        threshold = scene_analysis['percentiles'][percentile]
    else:
        # Calculate it manually if not in standard percentiles
        volume_values = [vol for _, vol in scene_analysis['volumes']]
        percentile_dict = analysis.calculate_percentiles(volume_values, [percentile])
        threshold = percentile_dict.get(percentile, 0)

    # Calculate how many objects this represents
    objects_count = int((percentile / 100.0) * scene_analysis['valid_objects'])

    results['success'] = True
    results['threshold_volume'] = threshold
    results['objects_in_percentile'] = objects_count

    return results


def calculate_threshold_volume(method, value, context, reference_obj=None):
    """
    Unified threshold processor - converts any method to absolute volume.

    This is the main function that should be called by UI elements.
    It handles all threshold methods and returns a normalized result.

    Args:
        method: Threshold method string:
                'reference' - Use reference object volume
                'percentage_largest' - X% of largest object
                'percentage_average' - X% of average object
                'absolute' - Direct volume input
                'percentile' - Smallest X% of objects
        value: Method-specific value:
               - reference: reference object
               - percentage_*: percentage (0-100)
               - absolute: volume value
               - percentile: percentile (0-100)
        context: Blender context
        reference_obj: Reference object (for 'reference' method)

    Returns:
        dict: Unified results:
            - success: bool
            - method: str (echoed back)
            - threshold_volume: float
            - metadata: dict (method-specific additional info)
            - error_message: str
    """
    unified_result = {
        'success': False,
        'method': method,
        'threshold_volume': 0.0,
        'metadata': {},
        'error_message': ''
    }

    try:
        if method == 'reference':
            if reference_obj is None:
                unified_result['error_message'] = "Reference object required for 'reference' method."
                return unified_result

            success, volume, error = calculate_object_volume(reference_obj, context)
            if not success:
                unified_result['error_message'] = f"Reference object error: {error}"
                return unified_result

            unified_result['success'] = True
            unified_result['threshold_volume'] = volume
            unified_result['metadata']['reference_object'] = reference_obj.name
            unified_result['metadata']['reference_volume'] = volume

        elif method == 'percentage_largest':
            result = process_percentage_method(value, 'largest', context)
            unified_result['success'] = result['success']
            unified_result['threshold_volume'] = result['threshold_volume']
            unified_result['error_message'] = result['error_message']
            unified_result['metadata']['percentage'] = value
            unified_result['metadata']['base_volume'] = result.get('base_volume', 0)

        elif method == 'percentage_average':
            result = process_percentage_method(value, 'average', context)
            unified_result['success'] = result['success']
            unified_result['threshold_volume'] = result['threshold_volume']
            unified_result['error_message'] = result['error_message']
            unified_result['metadata']['percentage'] = value
            unified_result['metadata']['base_volume'] = result.get('base_volume', 0)

        elif method == 'absolute':
            result = process_absolute_volume_method(value)
            unified_result['success'] = result['success']
            unified_result['threshold_volume'] = result['threshold_volume']
            unified_result['error_message'] = result['error_message']
            unified_result['metadata']['absolute_volume'] = value

        elif method == 'percentile':
            result = process_percentile_method(value, context)
            unified_result['success'] = result['success']
            unified_result['threshold_volume'] = result['threshold_volume']
            unified_result['error_message'] = result['error_message']
            unified_result['metadata']['percentile'] = value
            unified_result['metadata']['objects_count'] = result.get('objects_in_percentile', 0)

        else:
            unified_result['error_message'] = f"Unknown threshold method: '{method}'. Valid methods: reference, percentage_largest, percentage_average, absolute, percentile"
            return unified_result

    except Exception as e:
        unified_result['success'] = False
        unified_result['error_message'] = f"Error calculating threshold: {str(e)}"

    return unified_result

