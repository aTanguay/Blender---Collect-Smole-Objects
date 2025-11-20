# Occlusion Detection (Shell Extraction) - Technical Design

## Overview

This document describes the technical approach for implementing occlusion-based object filtering in the Collect Smole Objects addon. This feature addresses a common CAD workflow problem: product models often include complete internal mechanics that are never visible in renders.

**Problem Statement**: A Sony Walkman CAD file might contain 500 parts including batteries, circuit boards, springs, and internal screws. For a product render, you only need the outer shell and parts visible through openings.

**Solution**: Detect which objects are fully occluded (hidden inside other objects) using multi-directional raycast analysis, then collect them for hiding.

---

## Core Concept

### The Visibility Test

Imagine standing around an object from many different viewpoints and asking: "Can I see this object from here?"

- If the answer is **"No"** from every viewpoint → **Fully occluded** → Hide it
- If the answer is **"Yes"** from some viewpoints → **Partially visible** → Keep it
- If the answer is **"Yes"** from all viewpoints → **Fully visible** → Keep it

### Visual Example: Walkman Cross-Section

```
        Viewpoint 1 (top)
              |
              | ray
              ↓
    ═══════════════════  ← Shell (hit first)
    ║  🔩            ║
    ║    [Battery]   ║  ← Internal battery (ray never reaches)
    ║            🔩  ║
    ═══════════════════
              ↑
              | ray
              |
        Viewpoint 2 (bottom)
```

**Shell**: Rays hit it directly from all angles → **0% occluded** → KEEP

**Internal Battery**:
- Ray from top → hits shell first → blocked
- Ray from bottom → hits shell first → blocked
- Ray from all sides → hits shell first → blocked
- **Result**: 100% occluded → HIDE

**Button Recessed in Shell**:
- Rays from straight on → hit button directly
- Rays from steep angles → blocked by shell edge
- **Result**: 30% occluded → KEEP (user adjustable)

---

## Technical Implementation

### Step 1: Generate Viewpoint Sphere

Create evenly distributed points on a sphere around the entire scene. These represent "virtual camera positions" from which we'll test visibility.

#### Fibonacci Sphere Algorithm

```python
import math
from mathutils import Vector

def generate_viewpoint_sphere(center, radius, samples=100):
    """
    Generate evenly distributed points on a sphere using Fibonacci lattice.

    Args:
        center: Vector - Center of the sphere (typically scene center)
        radius: float - Radius of sphere (should encompass entire assembly)
        samples: int - Number of viewpoints (more = accurate but slower)

    Returns:
        List of Vector positions
    """
    points = []
    phi = math.pi * (3.0 - math.sqrt(5.0))  # Golden angle in radians

    for i in range(samples):
        # y goes from 1 to -1
        y = 1 - (i / float(samples - 1)) * 2

        # Radius at y
        radius_at_y = math.sqrt(1 - y * y)

        # Golden angle increment
        theta = phi * i

        x = math.cos(theta) * radius_at_y
        z = math.sin(theta) * radius_at_y

        # Scale to desired radius and offset by center
        point = center + Vector((x, y, z)) * radius
        points.append(point)

    return points
```

**Visualization of Fibonacci Sphere** (50 points):
```
        •  •  •  •  •       Top hemisphere
     •  •  •  •  •  •  •
   •  •  •  •  •  •  •  •
  •  •  •  •  •  •  •  •  •  Equator
   •  •  •  •  •  •  •  •
     •  •  •  •  •  •  •
        •  •  •  •  •       Bottom hemisphere
```

### Step 2: Calculate Scene Bounds

```python
def calculate_scene_bounds(objects):
    """
    Calculate bounding sphere that encompasses all objects.

    Args:
        objects: List of mesh objects to analyze

    Returns:
        (center: Vector, radius: float)
    """
    if not objects:
        return Vector((0, 0, 0)), 10.0

    # Find min/max bounds
    min_bound = Vector((float('inf'), float('inf'), float('inf')))
    max_bound = Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in objects:
        # Get world-space bounding box corners
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

        for corner in bbox_corners:
            min_bound.x = min(min_bound.x, corner.x)
            min_bound.y = min(min_bound.y, corner.y)
            min_bound.z = min(min_bound.z, corner.z)

            max_bound.x = max(max_bound.x, corner.x)
            max_bound.y = max(max_bound.y, corner.y)
            max_bound.z = max(max_bound.z, corner.z)

    # Calculate center and radius
    center = (min_bound + max_bound) / 2
    radius = (max_bound - min_bound).length / 2 * 1.5  # 1.5x for safety margin

    return center, radius
```

### Step 3: Test Object Occlusion

```python
import bpy
from mathutils import Vector

def test_object_occlusion(obj, viewpoints, context, threshold=0.95):
    """
    Test if an object is occluded from multiple viewpoints.

    Args:
        obj: bpy.types.Object - Object to test
        viewpoints: List[Vector] - Positions to cast rays from
        context: bpy.context - Blender context
        threshold: float - 0.0-1.0, percentage of rays that must be blocked

    Returns:
        dict: {
            'is_occluded': bool,
            'occlusion_percentage': float,
            'visible_rays': int,
            'blocked_rays': int,
            'total_rays': int
        }
    """
    depsgraph = context.evaluated_depsgraph_get()
    scene = context.scene

    # Get object center (or multiple test points for large objects)
    obj_center = obj.matrix_world.translation

    blocked_count = 0
    visible_count = 0
    total_rays = len(viewpoints)

    for viewpoint in viewpoints:
        # Calculate ray direction: from viewpoint toward object center
        ray_direction = (obj_center - viewpoint).normalized()
        ray_origin = viewpoint

        # Cast ray into scene
        result, location, normal, index, hit_obj, matrix = scene.ray_cast(
            depsgraph,
            ray_origin,
            ray_direction,
            distance=10000.0  # Maximum ray distance
        )

        if result:
            # Ray hit something
            if hit_obj == obj:
                # Ray hit our target object directly - VISIBLE
                visible_count += 1
            else:
                # Ray hit a different object first - BLOCKED
                blocked_count += 1
        else:
            # Ray didn't hit anything - object is visible from this angle
            visible_count += 1

    occlusion_percentage = blocked_count / total_rays if total_rays > 0 else 0.0
    is_occluded = occlusion_percentage >= threshold

    return {
        'is_occluded': is_occluded,
        'occlusion_percentage': occlusion_percentage,
        'visible_rays': visible_count,
        'blocked_rays': blocked_count,
        'total_rays': total_rays
    }
```

### Step 4: Batch Processing

```python
def analyze_scene_occlusion(objects, context, threshold=0.95, ray_samples=100):
    """
    Analyze all objects in scene for occlusion.

    Args:
        objects: List of mesh objects to analyze
        context: Blender context
        threshold: Occlusion percentage to consider "occluded"
        ray_samples: Number of rays to cast per object

    Returns:
        dict: {
            'occluded_objects': List[Object],
            'visible_objects': List[Object],
            'occlusion_data': Dict[Object, dict]  # Full results per object
        }
    """
    # Calculate scene bounds and generate viewpoints
    center, radius = calculate_scene_bounds(objects)
    viewpoints = generate_viewpoint_sphere(center, radius, ray_samples)

    occluded_objects = []
    visible_objects = []
    occlusion_data = {}

    # Test each object
    for obj in objects:
        result = test_object_occlusion(obj, viewpoints, context, threshold)
        occlusion_data[obj] = result

        if result['is_occluded']:
            occluded_objects.append(obj)
        else:
            visible_objects.append(obj)

    return {
        'occluded_objects': occluded_objects,
        'visible_objects': visible_objects,
        'occlusion_data': occlusion_data,
        'viewpoint_count': len(viewpoints)
    }
```

---

## Performance Optimization

### Challenge: Computational Complexity

For a scene with **N objects** and **R rays**:
- **Naive approach**: N × R raycasts
- **Example**: 200 objects × 200 rays = **40,000 raycasts**
- **Problem**: Can be slow for large scenes

### Solution: Multi-Stage Filtering Pipeline

#### Stage 1: Bounding Box Pre-Filter (Milliseconds)

Fast rejection test - if an object's bounding box is completely inside another object's bounding box, it's likely occluded.

```python
def bbox_contains_bbox(outer_obj, inner_obj):
    """
    Quick test: Is inner object's bbox completely inside outer object's bbox?
    """
    # Get world-space bounding boxes
    outer_bbox = [outer_obj.matrix_world @ Vector(corner) for corner in outer_obj.bound_box]
    inner_bbox = [inner_obj.matrix_world @ Vector(corner) for corner in inner_obj.bound_box]

    # Calculate min/max for both
    outer_min = Vector((min(c.x for c in outer_bbox),
                        min(c.y for c in outer_bbox),
                        min(c.z for c in outer_bbox)))
    outer_max = Vector((max(c.x for c in outer_bbox),
                        max(c.y for c in outer_bbox),
                        max(c.z for c in outer_bbox)))

    inner_min = Vector((min(c.x for c in inner_bbox),
                        min(c.y for c in inner_bbox),
                        min(c.z for c in inner_bbox)))
    inner_max = Vector((max(c.x for c in inner_bbox),
                        max(c.y for c in inner_bbox),
                        max(c.z for c in inner_bbox)))

    # Check if inner is completely inside outer
    return (inner_min.x >= outer_min.x and inner_max.x <= outer_max.x and
            inner_min.y >= outer_min.y and inner_max.y <= outer_max.y and
            inner_min.z >= outer_min.z and inner_max.z <= outer_max.z)

def fast_bbox_filter(objects):
    """
    Stage 1: Quick bounding box test.

    Returns:
        likely_occluded: Objects definitely worth testing
        definitely_visible: Objects that can't be occluded (too large)
    """
    likely_occluded = []
    definitely_visible = []

    for inner_obj in objects:
        is_contained = False

        for outer_obj in objects:
            if inner_obj == outer_obj:
                continue

            if bbox_contains_bbox(outer_obj, inner_obj):
                is_contained = True
                break

        if is_contained:
            likely_occluded.append(inner_obj)
        else:
            # Might still be occluded, needs raycast test
            pass

    return likely_occluded
```

#### Stage 2: Coarse Raycast Test (Seconds)

Test with fewer rays (20-50) to quickly categorize objects.

```python
def coarse_occlusion_test(objects, context, viewpoints_coarse):
    """
    Stage 2: Test with small number of rays for quick categorization.

    Returns:
        definitely_occluded: >90% blocked with coarse test
        definitely_visible: <30% blocked with coarse test
        uncertain: 30-90% blocked, needs fine test
    """
    definitely_occluded = []
    definitely_visible = []
    uncertain = []

    for obj in objects:
        result = test_object_occlusion(obj, viewpoints_coarse, context, threshold=0.9)

        if result['occlusion_percentage'] > 0.9:
            definitely_occluded.append(obj)
        elif result['occlusion_percentage'] < 0.3:
            definitely_visible.append(obj)
        else:
            uncertain.append(obj)

    return definitely_occluded, definitely_visible, uncertain
```

#### Stage 3: Fine Raycast Test (Only for Uncertain Objects)

```python
def fine_occlusion_test(uncertain_objects, context, viewpoints_fine, threshold):
    """
    Stage 3: Accurate test for uncertain objects only.
    """
    occluded = []
    visible = []

    for obj in uncertain_objects:
        result = test_object_occlusion(obj, viewpoints_fine, context, threshold)

        if result['is_occluded']:
            occluded.append(obj)
        else:
            visible.append(obj)

    return occluded, visible
```

#### Complete Optimized Pipeline

```python
def optimized_occlusion_analysis(objects, context, threshold=0.95):
    """
    Three-stage pipeline for efficient occlusion detection.
    """
    import time

    print(f"\n=== Occlusion Analysis: {len(objects)} objects ===")
    start_time = time.time()

    # Stage 1: Bounding box pre-filter
    print("Stage 1: Bounding box test...")
    likely_occluded = fast_bbox_filter(objects)
    print(f"  → {len(likely_occluded)} objects likely occluded")

    # Stage 2: Coarse raycast (20 rays)
    print("Stage 2: Coarse raycast test (20 rays)...")
    center, radius = calculate_scene_bounds(objects)
    viewpoints_coarse = generate_viewpoint_sphere(center, radius, samples=20)

    definitely_occluded, definitely_visible, uncertain = coarse_occlusion_test(
        objects, context, viewpoints_coarse
    )
    print(f"  → {len(definitely_occluded)} definitely occluded")
    print(f"  → {len(definitely_visible)} definitely visible")
    print(f"  → {len(uncertain)} uncertain (need fine test)")

    # Stage 3: Fine raycast (200 rays, only for uncertain objects)
    print(f"Stage 3: Fine raycast test (200 rays, {len(uncertain)} objects)...")
    viewpoints_fine = generate_viewpoint_sphere(center, radius, samples=200)

    occluded_uncertain, visible_uncertain = fine_occlusion_test(
        uncertain, context, viewpoints_fine, threshold
    )

    # Combine results
    all_occluded = definitely_occluded + occluded_uncertain
    all_visible = definitely_visible + visible_uncertain

    elapsed = time.time() - start_time
    print(f"\n✓ Analysis complete in {elapsed:.2f}s")
    print(f"  Final: {len(all_occluded)} occluded, {len(all_visible)} visible")

    return {
        'occluded_objects': all_occluded,
        'visible_objects': all_visible,
        'computation_time': elapsed
    }
```

### Additional Optimizations

#### Early Exit Strategy

```python
def test_object_occlusion_with_early_exit(obj, viewpoints, context, threshold=0.95, early_exit_count=5):
    """
    Stop testing as soon as object is confirmed visible.
    """
    blocked_count = 0
    visible_count = 0

    for i, viewpoint in enumerate(viewpoints):
        # ... perform raycast ...

        # Early exit: if we have enough visible rays, object is not occluded
        if visible_count >= early_exit_count:
            return {
                'is_occluded': False,
                'occlusion_percentage': blocked_count / (i + 1),
                'early_exit': True
            }

        # If we're past the point where threshold can be reached, exit early
        remaining_rays = len(viewpoints) - i - 1
        max_possible_blocked = blocked_count + remaining_rays
        if max_possible_blocked / len(viewpoints) < threshold:
            return {
                'is_occluded': False,
                'occlusion_percentage': blocked_count / (i + 1),
                'early_exit': True
            }

    # Full test completed
    return {
        'is_occluded': blocked_count / len(viewpoints) >= threshold,
        'occlusion_percentage': blocked_count / len(viewpoints),
        'early_exit': False
    }
```

#### Spatial Optimization: Hemisphere Testing

For objects you know are in a specific region (e.g., bottom half of assembly), only test rays from relevant hemisphere.

```python
def generate_hemisphere_viewpoints(center, radius, samples, direction='up'):
    """
    Generate viewpoints only on one hemisphere.
    Useful for objects known to be in specific region.
    """
    points = generate_viewpoint_sphere(center, radius, samples * 2)

    if direction == 'up':
        return [p for p in points if p.z > center.z]
    elif direction == 'down':
        return [p for p in points if p.z < center.z]
    # ... etc for other directions
```

---

## Handling Edge Cases

### Case 1: Large Objects with Partial Occlusion

**Problem**: A large door panel might have one edge hidden behind a wall.

**Solution**: Test multiple points on the object, not just center.

```python
def get_object_test_points(obj, num_points=5):
    """
    Get multiple test points distributed across object volume.
    """
    bbox = obj.bound_box
    center = obj.matrix_world.translation

    # Test center + points along major axes
    test_points = [center]

    # Add corner points
    for i in [0, 6]:  # Opposite bbox corners
        test_points.append(obj.matrix_world @ Vector(bbox[i]))

    # Add edge midpoints
    test_points.append(obj.matrix_world @ Vector((
        (bbox[0][0] + bbox[6][0]) / 2,
        (bbox[0][1] + bbox[6][1]) / 2,
        bbox[0][2]
    )))

    return test_points

def test_large_object_occlusion(obj, viewpoints, context, threshold=0.95):
    """
    Test large objects using multiple sample points.
    """
    test_points = get_object_test_points(obj)

    # Object is occluded only if ALL test points are occluded
    all_results = []

    for point in test_points:
        # Modify test_object_occlusion to accept custom test point
        result = test_point_occlusion(point, viewpoints, context, obj)
        all_results.append(result)

    # Aggregate: object is occluded if average occlusion > threshold
    avg_occlusion = sum(r['occlusion_percentage'] for r in all_results) / len(all_results)

    return {
        'is_occluded': avg_occlusion >= threshold,
        'occlusion_percentage': avg_occlusion,
        'test_points': len(test_points)
    }
```

### Case 2: Transparent/Glass Materials

**Problem**: A window might block rays but should allow visibility through it.

**Solution**: Material-aware raycasting (future enhancement).

```python
def is_material_transparent(material):
    """
    Check if material should be considered transparent for occlusion.
    """
    if not material:
        return False

    # Check for glass-like materials
    if material.use_nodes:
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_GLASS':
                return True
            if node.type == 'BSDF_TRANSPARENT':
                return True

    # Check legacy transparency
    if material.blend_method in {'BLEND', 'CLIP'}:
        return True

    return False

# When raycasting, optionally ignore hits on transparent materials
# (Requires custom ray filtering logic)
```

### Case 3: Objects in Recessed Areas

**Problem**: Buttons recessed in housing are partially occluded but should be visible.

**Solution**: User-adjustable sensitivity threshold.

```
Sensitivity Settings:
- 100%: Only fully hidden objects (0% visible from any angle)
- 95%: Mostly hidden (visible from <5% of angles) - RECOMMENDED
- 90%: Significantly hidden
- 75%: More than half hidden
```

---

## UI Integration

### Property Group Addition

```python
class CollectSmoleObjectsProperties(PropertyGroup):
    # ... existing properties ...

    # Occlusion detection properties
    occlusion_threshold: FloatProperty(
        name="Occlusion Threshold",
        description="Percentage of rays that must be blocked to consider object occluded",
        default=95.0,
        min=50.0,
        max=100.0,
        precision=1,
        subtype='PERCENTAGE'
    )

    occlusion_ray_samples: IntProperty(
        name="Ray Samples",
        description="Number of rays to cast (more = accurate but slower)",
        default=100,
        min=20,
        max=500
    )

    occlusion_combine_with_volume: BoolProperty(
        name="Combine with Volume",
        description="Collect objects that are small OR occluded",
        default=False
    )
```

### Panel UI Mockup

```python
def draw(self, context):
    layout = self.layout
    props = context.scene.collect_smole_props

    # ... existing sections ...

    # Threshold Method section
    if props.threshold_method == 'OCCLUSION':
        box = layout.box()
        box.label(text="Occlusion Detection", icon='HIDE_OFF')

        # Sensitivity slider
        col = box.column(align=True)
        col.label(text="Sensitivity:")
        col.prop(props, "occlusion_threshold", slider=True)

        # Interpretation helper
        threshold = props.occlusion_threshold
        if threshold >= 98:
            interpretation = "Only fully hidden objects"
        elif threshold >= 90:
            interpretation = "Mostly hidden objects (recommended)"
        elif threshold >= 75:
            interpretation = "Partially hidden objects"
        else:
            interpretation = "Even slightly hidden objects"

        col.label(text=f"  → {interpretation}", icon='INFO')

        # Ray samples (advanced)
        col.separator()
        col.prop(props, "occlusion_ray_samples")

        # Performance estimate
        est_time = props.occlusion_ray_samples * props.valid_objects / 1000
        col.label(text=f"Estimated time: ~{est_time:.1f}s", icon='TIME')

        # Combine mode
        box.separator()
        box.prop(props, "occlusion_combine_with_volume")

        if props.occlusion_combine_with_volume:
            box.label(text="Will collect objects that are:", icon='INFO')
            box.label(text="  • Below volume threshold, OR")
            box.label(text="  • Above occlusion threshold")
```

### Visual Panel Layout

```
┌─ Threshold Method ─────────────────────┐
│ Method: [Occlusion              ▼]     │
└─────────────────────────────────────────┘

┌─ Occlusion Detection ──────────────────┐
│ Sensitivity:                            │
│ [════════════════●═══] 95%             │
│  Conservative     →    Aggressive      │
│   → Mostly hidden objects (recommended) │
│                                         │
│ Ray Samples: [══════●═════] 100        │
│ Estimated time: ~2.3s                   │
│                                         │
│ ☐ Combine with Volume                  │
│   (Collect small OR occluded objects)  │
└─────────────────────────────────────────┘

┌─ Preview ──────────────────────────────┐
│ [Preview Occlusion]  [Clear]           │
│                                         │
│ 📊 Preview Statistics:                  │
│    Objects: 47 occluded                │
│    Avg occlusion: 98.3%                │
│    Computation time: 2.4s              │
└─────────────────────────────────────────┘
```

---

## Integration with Existing System

### Add as New Threshold Method

```python
# In core.py

def process_occlusion_method(threshold_percentage, ray_samples, context):
    """
    Process occlusion-based threshold.

    Args:
        threshold_percentage: 0-100, how occluded object must be
        ray_samples: Number of rays to cast
        context: Blender context

    Returns:
        dict with occlusion results
    """
    mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']

    if not mesh_objects:
        return {
            'success': False,
            'error_message': "No mesh objects in scene"
        }

    # Run optimized occlusion analysis
    results = optimized_occlusion_analysis(
        mesh_objects,
        context,
        threshold=threshold_percentage / 100.0
    )

    return {
        'success': True,
        'method': 'occlusion',
        'threshold_percentage': threshold_percentage,
        'ray_samples': ray_samples,
        'occluded_objects': results['occluded_objects'],
        'visible_objects': results['visible_objects'],
        'computation_time': results['computation_time']
    }

def calculate_threshold_volume(method, value, context, reference_obj=None):
    """
    Unified threshold processor - ADD OCCLUSION SUPPORT.
    """
    # ... existing methods ...

    elif method == 'occlusion':
        # Occlusion method returns objects directly, not a volume threshold
        threshold_percentage = value  # e.g., 95.0
        ray_samples = context.scene.collect_smole_props.occlusion_ray_samples

        result = process_occlusion_method(threshold_percentage, ray_samples, context)

        if not result['success']:
            return result

        return {
            'success': True,
            'method': 'occlusion',
            'threshold_volume': None,  # Not applicable for occlusion
            'occluded_objects': result['occluded_objects'],
            'metadata': {
                'threshold_percentage': threshold_percentage,
                'ray_samples': ray_samples,
                'object_count': len(result['occluded_objects']),
                'computation_time': result['computation_time']
            }
        }
```

### Modified Collection Logic

```python
# In core.py

def collect_occluded_objects(occluded_objects, context, collection_name="Occluded"):
    """
    Collect objects identified as occluded.
    Similar to collect_smaller_objects but for occlusion results.
    """
    # Get or create target collection
    if collection_name not in bpy.data.collections:
        target_collection = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(target_collection)
    else:
        target_collection = bpy.data.collections[collection_name]

    # Move objects to collection
    collected_count = 0

    for obj in occluded_objects:
        # Unlink from current collections
        for collection in obj.users_collection:
            collection.objects.unlink(obj)

        # Link to target collection
        target_collection.objects.link(obj)
        collected_count += 1

    return {
        'success': True,
        'collected_count': collected_count,
        'collection_name': collection_name
    }
```

### Combined Mode: Volume OR Occlusion

```python
def collect_small_or_occluded(volume_threshold, occlusion_results, context):
    """
    Collect objects that are EITHER small OR occluded.
    Ultimate CAD cleanup mode.
    """
    # Get small objects (existing logic)
    small_objects = []
    for obj in context.scene.objects:
        if obj.type != 'MESH':
            continue

        success, volume, error = calculate_object_volume(obj, context)
        if success and volume < volume_threshold:
            small_objects.append(obj)

    # Get occluded objects
    occluded_objects = occlusion_results['occluded_objects']

    # Combine (using set to avoid duplicates)
    combined_objects = list(set(small_objects + occluded_objects))

    # Collect all
    return collect_smaller_objects(
        reference_obj=None,
        threshold_volume=volume_threshold,
        context=context,
        collection_name="SmallOrOccluded",
        custom_object_list=combined_objects
    )
```

---

## Real-World Usage Examples

### Example 1: Sony Walkman Product Render

**Scenario**: 500-part Walkman assembly with complete internal mechanics

**Setup**:
1. Import CAD file (500 objects)
2. Open Collect Smole Objects panel
3. Click "Analyze Scene"
   - Statistics show: 500 objects, volume range 0.00001 to 0.5 m³
4. Select Method: **"Occlusion"**
5. Set Sensitivity: **95%** (recommended)
6. Ray Samples: **100** (balanced)
7. Click **"Preview Occlusion"**
   - Computation time: 4.2s
   - Preview shows 350 objects selected (internal mechanics)
   - External shell, buttons, and visible parts remain unselected
8. Verify preview looks correct
9. Click **"Collect Objects"**
   - 350 objects moved to "Occluded" collection
   - Collection hidden by default

**Result**:
- Visible objects: 150 (shell + external parts)
- Hidden objects: 350 (batteries, PCBs, internal screws, springs)
- Render-ready in seconds instead of hours of manual cleanup

### Example 2: Automotive Engine Bay

**Scenario**: Engine compartment with many hidden brackets and fasteners

**Setup**:
1. Analyze Scene: 1200 objects
2. Method: **"Occlusion"** + **"Combine with Volume"** enabled
3. Volume threshold: 0.001 m³ (catch small fasteners)
4. Occlusion threshold: 90% (catch hidden brackets)
5. Ray samples: 150 (high accuracy)
6. Preview → 800 objects selected
7. Collect Objects

**Result**:
- Collects small fasteners (volume-based)
- Collects hidden internal brackets (occlusion-based)
- Keeps visible engine components and external parts
- Perfect for exterior engine bay render

### Example 3: Architectural Interior

**Scenario**: Building model with furniture - want to hide objects inside closed cabinets

**Setup**:
1. Analyze Scene: 450 objects
2. Method: **"Occlusion"**
3. Sensitivity: **98%** (conservative - only fully hidden)
4. Ray samples: 200 (maximum accuracy)
5. Preview → 85 objects selected (dishes inside cabinets, items in drawers)
6. Collect Objects

**Result**:
- Cabinet exteriors remain visible
- Contents of closed cabinets hidden
- Reduces polygon count without affecting visible scene

---

## Performance Benchmarks (Estimated)

Based on the optimized three-stage pipeline:

| Scene Size | Objects | Ray Samples | Computation Time | Notes |
|------------|---------|-------------|------------------|-------|
| Small      | 50      | 100         | ~0.5s           | Almost instant |
| Medium     | 200     | 100         | ~2-3s           | Very usable |
| Large      | 500     | 100         | ~5-8s           | Acceptable |
| Very Large | 1000    | 100         | ~15-20s         | Progress bar recommended |
| Extreme    | 2000+   | 100         | ~40s+           | Consider batch mode |

**Optimization impact**:
- Without optimization: 200 objects × 100 rays = 20,000 raycasts
- With optimization: ~5,000-8,000 raycasts (60-75% reduction)

**Ray sample impact**:
- 20 rays: Fast but less accurate (~0.3s for 200 objects)
- 50 rays: Good balance (~1s for 200 objects)
- 100 rays: Recommended (~2-3s for 200 objects)
- 200 rays: High accuracy (~5-6s for 200 objects)
- 500 rays: Maximum accuracy (~12-15s for 200 objects)

---

## Future Enhancements

### 1. Camera-Based Occlusion
Instead of sphere viewpoints, use actual camera frustums:
- Detect occlusion relative to specific camera angle
- "Collect objects not visible from Camera 1"
- Perfect for single-angle product shots

### 2. Material-Aware Raycasting
- Ignore transparent materials (glass, windows)
- Weight occlusion by material opacity
- Handle refraction for more accurate results

### 3. Hierarchical Object Testing
- Test parent objects first
- If parent is occluded, skip testing children
- Significant speedup for grouped assemblies

### 4. GPU-Accelerated Raycasting
- Use Cycles/EEVEE rendering engine for parallel raycast
- Render depth passes from multiple angles
- Could be 10-100× faster than CPU raycasting

### 5. Occlusion Heatmap Visualization
- Color-code objects by occlusion percentage
- Red = fully occluded, Green = fully visible
- Help users understand and adjust threshold

### 6. Adaptive Ray Sampling
- Start with few rays, add more only where needed
- Machine learning to predict occlusion early
- Could reduce computation time by 50%

---

## Technical Challenges & Solutions

### Challenge 1: Ray Precision at Distance
**Problem**: Rays from very far viewpoints might miss small objects due to floating point precision.

**Solution**:
- Limit viewpoint sphere radius to 2-3× scene bounds
- Use double precision for critical calculations
- Add small offset to ray origin (0.001 units)

### Challenge 2: Objects with Holes
**Problem**: An object might have holes (like a mesh screen) that let visibility through.

**Solution**:
- Test multiple points distributed across object surface
- If >80% of surface points are occluded, mark object as occluded
- Option to treat non-manifold geometry specially

### Challenge 3: Thin Objects
**Problem**: Very thin objects (like paper, fabric) might be missed by rays.

**Solution**:
- Use object's evaluated mesh (with modifiers)
- Increase ray sampling for thin objects (detected via bbox aspect ratio)
- Option to thicken geometry slightly for testing

### Challenge 4: Performance on Low-End Hardware
**Problem**: 40,000+ raycasts might be too slow on older computers.

**Solution**:
- Provide performance presets: "Fast", "Balanced", "Accurate"
- Show estimated time before starting
- Allow cancellation mid-operation
- Option to process in background with progress bar

---

## Conclusion

Occlusion detection via multi-directional raycasting is a powerful, physically-accurate method for identifying hidden objects in CAD assemblies. Combined with the existing volume-based filtering, it provides a comprehensive solution for CAD cleanup workflows.

**Key Advantages**:
- ✅ Physically accurate (mimics real visibility)
- ✅ Works with any geometry
- ✅ User-adjustable sensitivity
- ✅ Optimizable for performance
- ✅ Integrates with existing system
- ✅ Provides visual preview

**Recommended Implementation Order**:
1. Phase 1: Basic occlusion detection (single-point, 100 rays)
2. Phase 2: Optimization pipeline (three-stage filtering)
3. Phase 3: UI integration and preview
4. Phase 4: Advanced features (multi-point, material-aware, etc.)

This feature would make the addon a complete solution for CAD import cleanup, handling both small objects and hidden objects in a single tool.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-20
**Status**: Technical Design - Ready for Implementation (Phase 3+)
