# Blender Collect Smole Objects - Improvement Planning

## Project Overview
A Blender addon for managing small objects in CAD data collections. Automatically collects and hides objects smaller than a threshold based on their volume. Particularly useful for automotive UDM models, product rendering, and complex CAD imports.

## Current State Analysis

### Existing Features
- Volume-based object comparison using BMesh
- Automatic collection creation ("Littles")
- Non-destructive object hiding
- Simple menu operator in View3D > Select menu

### Current Limitations
1. **Scale-dependent**: No way to set thresholds that work across different project scales (Walkman vs vehicle vs building)
2. **Limited feedback**: User doesn't know how many objects will be affected before running
3. **Minimal validation**: Only checks for exactly 1 selected object
4. **Trial-and-error workflow**: User must repeatedly select different reference objects to find the right threshold
5. **No scene analysis**: Doesn't help user understand the size distribution in their scene
6. **Single execution**: No preview or adjustment options
7. **No guidance**: User must carefully set up the scene without help

## Proposed Improvements

### Phase 1: Core Enhancements (High Priority)

#### 1.1 Smart Threshold Selection Methods
Replace single-method approach with multiple flexible options:

- **Reference Object** (current method - enhanced)
  - Keep existing functionality
  - Add validation and better error messages
  - Show what percentage of scene this represents

- **Percentage-based**
  - "Collect objects smaller than X% of the largest object"
  - "Collect objects smaller than X% of the average object volume"
  - Useful for relative scaling across different project types

- **Absolute Volume**
  - Direct volume input in cubic units (Blender units³)
  - Useful when user knows exact threshold needed
  - Should respect scene units

- **Percentile-based**
  - "Collect the smallest 20% of objects"
  - Great for initial exploration of unknown CAD data
  - Size-agnostic approach

#### 1.2 Scene Analysis & Statistics
Help users understand their scene before making decisions:

- **Volume Distribution Analysis**
  - Scan all mesh objects in scene
  - Calculate min/max/median/mean volumes
  - Show histogram or distribution info

- **Smart Threshold Suggestions**
  - Based on statistical analysis
  - Suggest natural "gaps" in size distribution
  - Flag outliers (extremely small objects)

- **Preview Information**
  - "X objects will be collected (Y total polygons)"
  - "This represents Z% of total scene objects"
  - Show volume range that will be affected

#### 1.3 Enhanced Error Handling
Make the addon more robust and user-friendly:

- **Pre-flight Checks**
  - Verify scene has mesh objects
  - Validate selected object is a mesh (not camera, light, empty, etc.)
  - Check for valid geometry (not empty mesh)
  - Handle scenes with modifiers correctly

- **Clear User Messages**
  - Specific error messages for each failure case
  - Helpful suggestions ("Try selecting a mesh object")
  - Success confirmation with statistics

- **Edge Case Handling**
  - Empty meshes
  - Non-manifold geometry
  - Objects with modifiers (use evaluated mesh)
  - Objects in hidden collections
  - Linked/library objects

### Phase 2: UI/UX Improvements (Medium Priority)

#### 2.1 Dedicated UI Panel
Replace simple menu item with full sidebar panel:

- **Location**: 3D Viewport > Sidebar (N panel) > "Collect Objects" tab
- **Controls**:
  - Threshold method dropdown (Reference/Percentage/Absolute/Percentile)
  - Dynamic controls based on selected method
  - Threshold value slider/input
  - "Analyze Scene" button
  - "Preview" button (highlight without moving)
  - "Execute" button (actually move objects)

- **Information Display**:
  - Current scene statistics
  - Objects that will be affected count
  - Total polygon count to be hidden
  - Suggested threshold values

#### 2.2 Preview System
Let users see before they commit:

- **Visual Preview**
  - Highlight objects that would be collected (change viewport color/wireframe)
  - Option to temporarily hide them to see effect
  - Clear preview mode before executing

- **Statistics Preview**
  - Live update as threshold changes
  - Show affected object list (scrollable)
  - Display volume ranges

#### 2.3 Multiple Collection Tiers
Instead of single "Littles" collection:

- **Tiered Collections**
  - "Tiny" (smallest X%)
  - "Small" (next Y%)
  - "Medium" (next Z%)
  - User-definable tier thresholds

- **Benefits**:
  - More granular control
  - Easy to show/hide different levels
  - Better scene organization

### Phase 3: Advanced Features (Lower Priority)

#### 3.1 Additional Filtering Options
More control over what gets collected:

- **Name Pattern Exclusion**
  - Exclude objects matching pattern (e.g., "*_hero", "*_keep")
  - Useful for protecting specific objects regardless of size
  - Regex or simple wildcard support

- **Collection-based Rules**
  - Only process objects in specific collections
  - Exclude objects already in certain collections
  - Useful for protecting organized areas

- **Material-based Filtering**
  - Exclude objects with specific materials
  - Useful for keeping small but important visible parts

#### 3.2 Alternative Measurement Methods
Different ways to define "small":

- **Bounding Box Volume**
  - Faster calculation than mesh volume
  - Option for users who prefer this method
  - Good for simple geometry

- **Longest Dimension**
  - Collect objects smaller than X units in any direction
  - Sometimes more intuitive than volume

- **Polygon Count**
  - Collect based on complexity rather than size
  - Useful for performance optimization

#### 3.3 Batch Operations & Presets
Save and reuse configurations:

- **Save/Load Presets**
  - Save threshold configurations
  - Quick presets: "Automotive", "Product Shot", "Architecture"
  - User can create custom presets

- **Batch Processing**
  - Run multiple threshold levels at once
  - Create all tier collections in one go
  - Useful for complex scenes

#### 3.4 Performance Optimizations
For very large scenes (1000+ objects):

- **Progress Indicator**
  - Show progress bar during processing
  - Allow cancellation mid-process
  - Estimate time remaining

- **Spatial Optimization**
  - Use bounding box pre-filter before volume calculation
  - Skip obviously large objects early
  - Cache volume calculations

## Implementation Strategy

### Development Phases
1. **Phase 1a**: Error handling and validation (foundation)
2. **Phase 1b**: Scene analysis system (data gathering)
3. **Phase 1c**: Multiple threshold methods (core flexibility)
4. **Phase 2a**: Basic UI panel (user interface)
5. **Phase 2b**: Preview system (user feedback)
6. **Phase 2c**: Multiple collection tiers (organization)
7. **Phase 3**: Advanced features (as needed)

### Technical Considerations

#### Code Structure
- Separate UI code from logic
- Create dedicated classes for analysis, threshold calculation, and collection management
- Maintain backward compatibility with simple menu operator

#### Testing Approach
- Test with small scenes (10-50 objects)
- Test with medium scenes (100-500 objects)
- Test with large scenes (1000+ objects)
- Test edge cases (empty meshes, modifiers, linked objects)
- Test different scales (tiny products to large buildings)

#### Documentation Needs
- User guide with screenshots
- Example workflows for common use cases
- API documentation for extensibility
- Troubleshooting section

## Use Case Examples

### Automotive UDM
- Import has 5000+ objects (bolts, springs, clips, main body panels)
- Use percentile method: "Collect smallest 80% of objects"
- Result: Major panels remain, tiny hardware hidden
- Polygon count reduced from 2M to 400K

### Product Rendering (Sony Walkman)
- Import has 200 objects (screws, internal components, case, buttons)
- Use percentage method: "Collect objects smaller than 5% of largest"
- Keep visible external parts, hide internal components
- Clear product shot with minimal cleanup

### Architectural Model
- Import has 1000+ objects (furniture, fixtures, structure)
- Use absolute volume: "Collect objects smaller than 0.001 m³"
- Hide small fixtures, keep structure and major furniture
- Optimized for rendering

## Success Metrics
- Reduce user trial-and-error iterations (currently 3-5, target: 1-2)
- Clear feedback before execution (currently none)
- Support projects across 3+ orders of magnitude in scale
- Reduce setup time from minutes to seconds

## Future Considerations

### Occlusion Detection (Shell Extraction)
**Problem**: CAD assemblies often include internal mechanics that are never visible in renders (screws, springs, internal components inside a closed shell).

**Use Case**: Sony Walkman with full mechanicals - you only want the outer shell and parts that peek through openings.

**Potential Approaches**:
1. **Raycast-based occlusion**
   - Cast rays from multiple directions toward each object
   - If 100% of rays hit other objects first, mark as occluded
   - Adjustable sensitivity (95% occluded vs 100%)

2. **Camera-based visibility**
   - Place cameras in sphere around assembly
   - Render depth passes or use ray visibility API
   - Objects never visible from any angle = internal

3. **Bounding box intersection analysis**
   - Fast pre-filter: if object is completely inside another object's bbox
   - Refine with actual mesh intersection tests

4. **Combined approach**
   - Use volume + occlusion together
   - "Collect small OR occluded objects"
   - Most flexible for CAD cleanup

**Technical Challenges**:
- Performance with 1000+ objects (raycast complexity)
- Handling partially visible objects (door mechanisms, vents)
- Dealing with transparent/glass materials
- User control over sensitivity

**UI Integration**:
- Add "Occlusion" threshold method
- "Collect Occluded Objects" button
- Preview shows what will be hidden
- Sensitivity slider (0-100% occlusion threshold)

### Other Future Ideas
- Integration with other cleanup tools
- Export filtered collections separately
- ML-based object importance detection
- Camera frustum-based visibility culling (view-dependent)
