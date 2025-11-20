"""
Scene analysis functionality for Collect Smole Objects addon.

Provides statistical analysis of scene objects and threshold suggestions.
"""

import bpy
from . import core


def analyze_scene(context):
    """
    Analyze all mesh objects in the scene to gather volume statistics.

    Args:
        context: Blender context

    Returns:
        dict: Analysis results containing:
            - total_objects: int (total mesh objects in scene)
            - valid_objects: int (objects with valid volumes)
            - invalid_objects: int (objects that failed validation)
            - invalid_reasons: list of (obj_name, reason) tuples
            - min_volume: float
            - max_volume: float
            - mean_volume: float
            - median_volume: float
            - std_dev: float (standard deviation)
            - percentiles: dict {10: val, 20: val, ..., 90: val}
            - volumes: list of tuples (obj_name, volume) sorted by volume
    """
    results = {
        'total_objects': 0,
        'valid_objects': 0,
        'invalid_objects': 0,
        'invalid_reasons': [],
        'min_volume': 0.0,
        'max_volume': 0.0,
        'mean_volume': 0.0,
        'median_volume': 0.0,
        'std_dev': 0.0,
        'percentiles': {},
        'volumes': []
    }

    # Collect all mesh objects
    mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
    results['total_objects'] = len(mesh_objects)

    if results['total_objects'] == 0:
        return results

    # Calculate volume for each object
    valid_volumes = []

    for obj in mesh_objects:
        success, volume, error = core.calculate_object_volume(obj, context)

        if success:
            valid_volumes.append((obj.name, volume))
            results['valid_objects'] += 1
        else:
            results['invalid_objects'] += 1
            results['invalid_reasons'].append((obj.name, error))

    if results['valid_objects'] == 0:
        return results

    # Sort volumes
    valid_volumes.sort(key=lambda x: x[1])
    results['volumes'] = valid_volumes

    # Extract just the volume values for statistics
    volume_values = [vol for _, vol in valid_volumes]

    # Calculate basic statistics
    results['min_volume'] = volume_values[0]
    results['max_volume'] = volume_values[-1]
    results['mean_volume'] = sum(volume_values) / len(volume_values)

    # Calculate median
    n = len(volume_values)
    if n % 2 == 0:
        results['median_volume'] = (volume_values[n//2 - 1] + volume_values[n//2]) / 2
    else:
        results['median_volume'] = volume_values[n//2]

    # Calculate standard deviation
    mean = results['mean_volume']
    variance = sum((v - mean) ** 2 for v in volume_values) / len(volume_values)
    results['std_dev'] = variance ** 0.5

    # Calculate percentiles (10th, 20th, ..., 90th)
    results['percentiles'] = calculate_percentiles(volume_values, [10, 20, 25, 50, 75, 80, 90])

    return results


def calculate_percentiles(sorted_values, percentile_list):
    """
    Calculate percentiles from a sorted list of values.

    Args:
        sorted_values: List of numeric values (must be sorted)
        percentile_list: List of percentiles to calculate (e.g., [10, 25, 50, 75, 90])

    Returns:
        dict: {percentile: value}
    """
    if not sorted_values:
        return {}

    percentiles = {}
    n = len(sorted_values)

    for p in percentile_list:
        # Use linear interpolation method
        # Index = (percentile / 100) * (n - 1)
        idx = (p / 100.0) * (n - 1)
        lower_idx = int(idx)
        upper_idx = min(lower_idx + 1, n - 1)

        # Linear interpolation between the two nearest values
        lower_val = sorted_values[lower_idx]
        upper_val = sorted_values[upper_idx]
        fraction = idx - lower_idx

        percentiles[p] = lower_val + fraction * (upper_val - lower_val)

    return percentiles


def suggest_thresholds(analysis_results):
    """
    Suggest appropriate threshold values based on scene analysis.

    Args:
        analysis_results: Results from analyze_scene()

    Returns:
        dict: Suggested thresholds:
            - percentile_thresholds: dict {percentile: volume}
            - percentage_thresholds: dict {percentage: volume}
            - natural_gaps: list of (volume, gap_size) tuples
            - recommended: dict with specific recommendations
    """
    suggestions = {
        'percentile_thresholds': {},
        'percentage_thresholds': {},
        'natural_gaps': [],
        'recommended': {}
    }

    if analysis_results['valid_objects'] == 0:
        return suggestions

    # Percentile-based suggestions
    # These are useful for "collect the smallest X% of objects"
    suggestions['percentile_thresholds'] = {
        10: analysis_results['percentiles'].get(10, 0),
        20: analysis_results['percentiles'].get(20, 0),
        25: analysis_results['percentiles'].get(25, 0),
        50: analysis_results['percentiles'].get(50, 0),
        75: analysis_results['percentiles'].get(75, 0),
        80: analysis_results['percentiles'].get(80, 0),
    }

    # Percentage-based suggestions
    # These are useful for "collect objects smaller than X% of largest"
    max_vol = analysis_results['max_volume']
    mean_vol = analysis_results['mean_volume']

    suggestions['percentage_thresholds'] = {
        '1% of largest': max_vol * 0.01,
        '5% of largest': max_vol * 0.05,
        '10% of largest': max_vol * 0.10,
        '25% of largest': max_vol * 0.25,
        '10% of average': mean_vol * 0.10,
        '25% of average': mean_vol * 0.25,
        '50% of average': mean_vol * 0.50,
    }

    # Detect natural gaps in size distribution
    suggestions['natural_gaps'] = detect_natural_gaps(analysis_results['volumes'])

    # Provide specific recommendations based on distribution
    suggestions['recommended'] = generate_recommendations(analysis_results, suggestions)

    return suggestions


def detect_natural_gaps(volumes_list, min_gap_ratio=3.0):
    """
    Detect natural gaps in the volume distribution.

    A "gap" is a large jump between consecutive volumes.
    These often represent natural breakpoints (e.g., tiny screws vs actual parts).

    Args:
        volumes_list: List of (obj_name, volume) tuples (sorted)
        min_gap_ratio: Minimum ratio between consecutive values to consider a gap

    Returns:
        list: List of (threshold_volume, gap_ratio) tuples
    """
    if len(volumes_list) < 2:
        return []

    gaps = []

    for i in range(len(volumes_list) - 1):
        vol1 = volumes_list[i][1]
        vol2 = volumes_list[i + 1][1]

        # Avoid division by zero
        if vol1 <= 0:
            continue

        ratio = vol2 / vol1

        # If the next object is significantly larger, that's a gap
        if ratio >= min_gap_ratio:
            # Suggest threshold at the geometric mean of the gap
            threshold = (vol1 * vol2) ** 0.5
            gaps.append((threshold, ratio))

    # Sort by gap size (descending) and return top 5
    gaps.sort(key=lambda x: x[1], reverse=True)
    return gaps[:5]


def generate_recommendations(analysis_results, suggestions):
    """
    Generate specific recommendations based on the analysis.

    Args:
        analysis_results: Results from analyze_scene()
        suggestions: Results from suggest_thresholds()

    Returns:
        dict: Specific recommendations with reasoning
    """
    recommendations = {}

    total = analysis_results['total_objects']
    valid = analysis_results['valid_objects']

    if valid == 0:
        return recommendations

    # Recommendation 1: For CAD cleanup (automotive/product)
    # Typically want to remove smallest 50-80% of objects
    p80_threshold = suggestions['percentile_thresholds'].get(80, 0)
    recommendations['cad_cleanup'] = {
        'threshold': p80_threshold,
        'method': 'percentile',
        'value': 80,
        'reason': 'Collect smallest 80% - typical for CAD imports with many tiny hardware parts'
    }

    # Recommendation 2: Conservative approach
    # Only remove obvious outliers (smallest 20%)
    p20_threshold = suggestions['percentile_thresholds'].get(20, 0)
    recommendations['conservative'] = {
        'threshold': p20_threshold,
        'method': 'percentile',
        'value': 20,
        'reason': 'Collect smallest 20% - conservative approach for unknown data'
    }

    # Recommendation 3: Natural gap (if exists)
    if suggestions['natural_gaps']:
        gap_threshold, gap_ratio = suggestions['natural_gaps'][0]
        recommendations['natural_gap'] = {
            'threshold': gap_threshold,
            'method': 'gap_detection',
            'value': gap_ratio,
            'reason': f'Natural gap detected ({gap_ratio:.1f}x size jump) - likely breakpoint between part types'
        }

    # Recommendation 4: Percentage of largest
    # Good for relative scaling
    pct5_threshold = suggestions['percentage_thresholds']['5% of largest']
    recommendations['relative_small'] = {
        'threshold': pct5_threshold,
        'method': 'percentage',
        'value': 5,
        'reason': '5% of largest object - removes relatively tiny parts across any scale'
    }

    return recommendations


def calculate_impact(threshold_volume, context):
    """
    Calculate the impact of using a specific threshold.

    Args:
        threshold_volume: Volume threshold to test
        context: Blender context

    Returns:
        dict: Impact analysis:
            - affected_count: int (objects that would be collected)
            - affected_names: list of str (names of affected objects)
            - total_polygons: int (total polygons in affected objects)
            - percentage_of_scene: float (% of objects affected)
            - volume_range: tuple (min_vol, max_vol) of affected objects
    """
    impact = {
        'affected_count': 0,
        'affected_names': [],
        'total_polygons': 0,
        'percentage_of_scene': 0.0,
        'volume_range': (0.0, 0.0)
    }

    mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']

    if not mesh_objects:
        return impact

    affected_volumes = []

    for obj in mesh_objects:
        success, volume, error = core.calculate_object_volume(obj, context)

        if not success:
            continue

        if volume < threshold_volume:
            impact['affected_count'] += 1
            impact['affected_names'].append(obj.name)
            affected_volumes.append(volume)

            # Count polygons
            depsgraph = context.evaluated_depsgraph_get()
            try:
                mesh = obj.evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=False)
                if mesh:
                    impact['total_polygons'] += len(mesh.polygons)
                obj.evaluated_get(depsgraph).to_mesh_clear()
            except:
                pass

    # Calculate percentage
    impact['percentage_of_scene'] = (impact['affected_count'] / len(mesh_objects)) * 100

    # Volume range
    if affected_volumes:
        impact['volume_range'] = (min(affected_volumes), max(affected_volumes))

    return impact
