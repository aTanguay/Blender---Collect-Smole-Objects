# Development Tasks - Collect Smole Objects Addon

## Quick Reference
- **Current Version**: v1.1
- **Next Target Version**: v2.0
- **Last Updated**: 2025-11-20
- **Active Phase**: Phase 2c - Multiple Collection Tiers
- **Last Completed Phase**: Phase 2b - Preview System ✓

## Task Status Legend
- [ ] Not started
- [🔄] In progress
- [✓] Completed
- [⏸] Blocked/On hold
- [❌] Cancelled

---

## Phase 1a: Foundation & Error Handling

### Code Refactoring
- [✓] Create separate modules for better organization
  - [✓] `core.py` - Core volume calculation and object processing
  - [✓] `analysis.py` - Scene analysis and statistics (skeleton for Phase 1b)
  - [✓] `ui.py` - UI panels and operators
  - [✓] `utils.py` - Helper functions and validators
  - [✓] `__init__.py` - Main addon registration with reload support

### Enhanced Validation
- [✓] Add pre-flight validation system
  - [✓] Check if scene has any mesh objects
  - [✓] Validate selected object is a mesh type
  - [✓] Check for valid/non-empty geometry
  - [✓] Handle objects with modifiers properly (uses evaluated depsgraph)
  - [✓] Validate volume calculations don't return zero/negative

### Error Handling Improvements
- [✓] Implement comprehensive error messages
  - [✓] "No mesh objects in scene" handler
  - [✓] "Selected object is not a mesh" handler
  - [✓] "Empty mesh geometry" handler
  - [✓] "Volume calculation failed" handler
  - [✓] "No objects match threshold" handler

### Error Recovery
- [✓] Add graceful failure handling
  - [✓] Skip invalid objects rather than failing entire operation
  - [✓] Report skipped objects to user (with console logging)
  - [✓] Maintain scene state on failure (try/except with cleanup)

---

## Phase 1b: Scene Analysis System

### Volume Analysis Core
- [✓] Implement scene scanning functionality
  - [✓] Scan all mesh objects in scene
  - [✓] Calculate volumes for all objects
  - [✓] Store results in efficient data structure (dict with sorted volumes list)
  - [✓] Track invalid objects with error reasons

### Statistical Analysis
- [✓] Calculate scene statistics
  - [✓] Minimum volume
  - [✓] Maximum volume
  - [✓] Median volume
  - [✓] Mean (average) volume
  - [✓] Standard deviation
  - [✓] Percentile distributions (10th, 20th, 25th, 50th, 75th, 80th, 90th)

### Smart Suggestions
- [✓] Implement threshold suggestion system
  - [✓] Detect natural gaps in size distribution (3x+ ratio jumps)
  - [✓] Identify outliers via percentiles
  - [✓] Suggest percentile-based thresholds (20%, 80%, etc.)
  - [✓] Calculate suggested percentage thresholds (% of largest, % of average)

### Analysis Display
- [✓] Create analysis results data structure
  - [✓] Format statistics in structured dict
  - [✓] Generate recommendations with reasoning
  - [✓] Calculate estimated impact (object count, polygon count, percentage)

---

## Phase 1c: Multiple Threshold Methods

### Reference Object Method (Enhanced)
- [✓] Improve existing reference object method
  - [✓] Add better validation (comprehensive error handling)
  - [✓] Core method implemented (ready for UI in Phase 2a)
  - [✓] Returns metadata for display

### Percentage-Based Method
- [✓] Implement relative percentage threshold
  - [✓] "X% of largest object" mode (process_percentage_method)
  - [✓] "X% of average object" mode (process_percentage_method)
  - [✓] Validation (0-100% range)
  - [✓] Uses scene analysis for calculations
  - Note: UI sliders deferred to Phase 2a

### Absolute Volume Method
- [✓] Implement direct volume input
  - [✓] Volume input validation (process_absolute_volume_method)
  - [✓] Positive value validation
  - [✓] Simple pass-through to threshold
  - Note: Unit conversion and UI deferred to Phase 2a

### Percentile-Based Method
- [✓] Implement percentile threshold
  - [✓] "Collect smallest X%" mode (process_percentile_method)
  - [✓] Percentile validation (0-100%)
  - [✓] Uses scene analysis percentile calculations
  - [✓] Returns object count in percentile
  - Note: UI slider and preview deferred to Phase 2a

### Threshold Calculation Engine
- [✓] Create unified threshold processor
  - [✓] Unified interface for all methods (calculate_threshold_volume)
  - [✓] Converts all methods to absolute volume threshold
  - [✓] Returns normalized result dict
  - [✓] Includes method-specific metadata
  - [✓] Comprehensive error handling
  - [✓] 5 supported methods: reference, percentage_largest, percentage_average, absolute, percentile

---

## Phase 2a: UI Panel Development

### Panel Structure
- [✓] Create sidebar panel in 3D Viewport
  - [✓] Register panel in N-panel sidebar (VIEW3D_PT_collect_smole_objects)
  - [✓] Create "Collect" tab in N-panel
  - [✓] Design clean, intuitive layout with sections
  - [✓] Add panel icons and visual hierarchy (boxed sections)

### Method Selection UI
- [✓] Implement threshold method dropdown
  - [✓] Reference Object option
  - [✓] Percentage of Largest option
  - [✓] Percentage of Average option
  - [✓] Percentile option
  - [✓] Absolute Volume option
  - [✓] Dynamic UI based on selection

### Dynamic Controls
- [✓] Create method-specific controls
  - [✓] Reference: Info label ("Select one mesh object")
  - [✓] Percentage: Slider with precision (0.01-100%)
  - [✓] Absolute: Volume input with units (FloatProperty with VOLUME unit)
  - [✓] Percentile: Slider (1-99%) with object count preview

### Information Display Panel
- [✓] Add statistics display section
  - [✓] Show current scene stats (Objects: valid/total)
  - [✓] Display Min/Max/Mean/Median volumes with formatting
  - [✓] Percentile preview (object count for percentile method)
  - Note: Polygon count and full preview deferred to Phase 2b

### Action Buttons
- [✓] Implement main action buttons
  - [✓] "Analyze Scene" button (OBJECT_OT_analyze_scene)
  - [✓] "Collect Objects" button (OBJECT_OT_collect_with_method)
  - Note: Preview/Clear Preview buttons deferred to Phase 2b

### Property Management
- [✓] Create property group (CollectSmoleObjectsProperties)
  - [✓] threshold_method (EnumProperty)
  - [✓] percentage_value (FloatProperty)
  - [✓] percentile_value (IntProperty)
  - [✓] absolute_volume (FloatProperty)
  - [✓] Scene analysis results storage
  - [✓] Register/unregister properties properly

---

## Phase 2b: Preview System

### Visual Preview
- [✓] Implement object highlighting system
  - [✓] Use Blender selection system for preview
  - [✓] Clear preview state cleanly
  - [ ] Temporarily change object display color (deferred - selection is sufficient)
  - [ ] Use viewport overlays for preview (deferred)
  - [ ] Add wireframe/solid preview options (deferred)

### Selection Preview
- [✓] Create preview selection functionality
  - [✓] Select all objects that would be collected
  - [✓] Use Blender selection system
  - [✓] Allow inspection before execution
  - [✓] Add clear preview button

### Preview Statistics Display
- [✓] Display preview statistics in panel
  - [✓] Show object count
  - [✓] Show polygon count
  - [✓] Show percentage of scene
  - [✓] Preview/Clear Preview buttons

### Preview Object List (Deferred to Future Enhancement)
- [ ] Display affected objects list
  - [ ] Scrollable list in panel
  - [ ] Show object names and volumes
  - [ ] Click to focus/select object
  - [ ] Sort options (name, size, collection)

### Live Updates (Deferred to Future Enhancement)
- [ ] Implement real-time preview updates
  - [ ] Update preview as threshold changes
  - [ ] Throttle updates for performance
  - [ ] Show loading state during calculation
  - [ ] Cancel long-running previews

---

## Phase 2c: Multiple Collection Tiers

### Tier System Design
- [ ] Design multi-tier collection system
  - [ ] Define default tiers (Tiny, Small, Medium)
  - [ ] Create tier configuration structure
  - [ ] Allow custom tier names
  - [ ] Support 2-5 tiers

### Tier Calculation
- [ ] Implement tier threshold calculation
  - [ ] Automatic tier distribution
  - [ ] Manual tier boundary setting
  - [ ] Percentile-based tier division
  - [ ] Equal-count vs equal-range modes

### Collection Management
- [ ] Create tier collection handling
  - [ ] Generate multiple collections
  - [ ] Name collections appropriately
  - [ ] Set collection colors/visibility
  - [ ] Organize in hierarchy

### Tier UI
- [ ] Add tier controls to panel
  - [ ] Enable/disable tier mode
  - [ ] Tier count selector
  - [ ] Tier boundary editors
  - [ ] Preview objects per tier

---

## Phase 3: Advanced Features

### Name Pattern Exclusion
- [ ] Implement object name filtering
  - [ ] Wildcard pattern support
  - [ ] Regex pattern option
  - [ ] Multiple pattern rules
  - [ ] Test pattern matching

### Alternative Measurements
- [ ] Add bounding box measurement option
  - [ ] Calculate bounding box volumes
  - [ ] Add UI toggle for measurement method
  - [ ] Performance comparison

- [ ] Add longest dimension option
  - [ ] Calculate max dimension
  - [ ] Unit-based threshold
  - [ ] UI controls

- [ ] Add polygon count option
  - [ ] Count polygons per object
  - [ ] Polygon-based threshold
  - [ ] Performance optimization mode

### Preset System
- [ ] Create preset save/load system
  - [ ] Save current configuration
  - [ ] Load saved presets
  - [ ] Default presets (Automotive, Product, Architecture)
  - [ ] Preset management UI

### Performance Optimization
- [ ] Add progress tracking for large scenes
  - [ ] Progress bar UI
  - [ ] Cancel operation support
  - [ ] Time estimation
  - [ ] Batch processing optimization

### Occlusion Detection (Shell Extraction)
**Goal**: Detect and collect objects that are completely hidden inside assemblies (internal mechanics, hidden screws, etc.)

**Use Case**: Product renders where only the outer shell matters (Walkman with all internal mechanics)

- [ ] Research and prototype occlusion detection
  - [ ] Research Blender raycast API
  - [ ] Test performance with multi-directional raycasts
  - [ ] Prototype bounding box intersection tests
  - [ ] Evaluate render-based approaches

- [ ] Implement core occlusion analysis
  - [ ] Create multi-directional raycast system
  - [ ] Calculate occlusion percentage per object
  - [ ] Handle partially visible objects
  - [ ] Optimize for large object counts
  - [ ] Cache results for performance

- [ ] Add occlusion threshold method
  - [ ] Integrate with existing threshold system
  - [ ] "Collect objects X% occluded or more"
  - [ ] Sensitivity slider (0-100%)
  - [ ] Combine with volume filtering option

- [ ] UI integration
  - [ ] Add "Occlusion" threshold method to dropdown
  - [ ] Occlusion sensitivity slider
  - [ ] "Small OR Occluded" combined mode
  - [ ] Preview occluded objects
  - [ ] Statistics (% occluded, ray hits, etc.)

- [ ] Advanced occlusion features
  - [ ] Sample ray count control (performance vs accuracy)
  - [ ] Ignore transparent materials option
  - [ ] Directional occlusion (from specific viewpoint)
  - [ ] Export occlusion map for review

---

## Testing & Quality Assurance

### Unit Testing
- [ ] Create test suite structure
- [ ] Test volume calculation accuracy
- [ ] Test threshold methods
- [ ] Test statistical analysis
- [ ] Test error handling

### Integration Testing
- [ ] Test with small scenes (10-50 objects)
- [ ] Test with medium scenes (100-500 objects)
- [ ] Test with large scenes (1000+ objects)
- [ ] Test different object scales
- [ ] Test edge cases

### Edge Case Testing
- [ ] Empty meshes
- [ ] Objects with modifiers
- [ ] Linked/library objects
- [ ] Hidden objects
- [ ] Objects in hidden collections
- [ ] Non-manifold geometry
- [ ] Zero-volume objects

### User Testing
- [ ] Create test scenes for common use cases
  - [ ] Automotive CAD import
  - [ ] Product model (small scale)
  - [ ] Architectural model (large scale)
- [ ] Document test results
- [ ] Gather feedback
- [ ] Iterate based on findings

---

## Documentation

### Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add inline comments for complex logic
- [ ] Create API documentation
- [ ] Document class structures

### User Documentation
- [ ] Write user guide
  - [ ] Installation instructions
  - [ ] Basic usage tutorial
  - [ ] Advanced features guide
  - [ ] Troubleshooting section
- [ ] Create example workflows
- [ ] Add screenshots/videos
- [ ] Create FAQ section

### Developer Documentation
- [ ] Architecture overview
- [ ] Contributing guidelines
- [ ] Development setup guide
- [ ] Extension points documentation

---

## Release Preparation

### Version 2.0 Release
- [ ] Update version number in bl_info
- [ ] Create changelog
- [ ] Update README.md
- [ ] Create release notes
- [ ] Package addon for distribution
- [ ] Test installation process
- [ ] Tag release in git
- [ ] Create GitHub release

---

## Future Enhancements (Post v2.0)

### Advanced Features
- [ ] Camera frustum-based visibility culling
- [ ] ML-based object importance detection
- [ ] Export filtered collections separately
- [ ] Integration with other cleanup tools
- [ ] Batch processing multiple files
- [ ] Scripting API for automation

### Community Requests
- [ ] (Add items as requested by users)

---

## Notes & Decisions

### 2025-11-20 (Session 1)
- Initial planning completed
- Decided on phased approach
- Priority on error handling and usability
- Multi-tier collections moved to Phase 2c
- Advanced features deferred to Phase 3
- Created PLANNING.md, TASKS.md, CLAUDE.md
- Set up dual-format packaging (legacy + modern extension)
- **Phase 1a COMPLETED**: Full code refactoring into modules
  - Split into utils.py, core.py, ui.py, analysis.py
  - Comprehensive validation system implemented
  - Enhanced error handling with graceful recovery
  - Skip invalid objects instead of failing
  - Console logging for skipped objects
  - Proper cleanup in error paths
- **Phase 1b COMPLETED**: Scene analysis system
  - Full statistical analysis (min/max/mean/median/std dev)
  - Percentile calculations with linear interpolation
  - Natural gap detection (3x+ jumps in size)
  - Smart threshold suggestions (4 recommendation types)
  - Impact preview calculation (counts, polygons, percentages)
  - Structured results for future UI display
- **Phase 1c COMPLETED**: Multiple threshold methods
  - 5 threshold methods implemented (reference, percentage_largest, percentage_average, absolute, percentile)
  - Unified threshold processor (calculate_threshold_volume)
  - Each method returns normalized result with metadata
  - Comprehensive validation for all methods
  - Backend ready for UI integration in Phase 2a
- **Phase 2a COMPLETED**: UI Panel Development
  - Full sidebar panel in N-panel ("Collect" tab)
  - Method selection dropdown with 5 options
  - Dynamic controls that change per method
  - Scene analysis button with statistics display
  - Collect Objects button using selected method
  - Property group for UI state management
  - Clean Blender-style layout with sections
- **Phase 2b COMPLETED**: Preview System
  - Preview operator that selects objects that would be collected
  - Clear preview operator to reset selection
  - Preview statistics display (object count, polygon count, percentage)
  - Preview/Clear Preview buttons in UI panel
  - Preview state tracking in property group
  - Automatic preview clearing after collect operation
  - Uses Blender's native selection system for visual feedback

---

## Current Sprint Focus

**Completed:**
- ✓ Phase 1a: Foundation & Error Handling (COMPLETE)
- ✓ Phase 1b: Scene Analysis System (COMPLETE)
- ✓ Phase 1c: Multiple Threshold Methods (COMPLETE)
- ✓ Phase 2a: UI Panel Development (COMPLETE)
- ✓ Phase 2b: Preview System (COMPLETE)
- ✓ Project documentation (PLANNING.md, TASKS.md, CLAUDE.md)
- ✓ Dual-format packaging system
- ✓ Code refactoring into modules
- ✓ Complete backend API + functional UI with preview

**Active Tasks:**
- Ready to begin Phase 2c: Multiple Collection Tiers

**Next Up:**
- Phase 2c: Multiple collection tiers
  - Create tiered collections (Tiny, Small, Medium)
  - Automatic tier organization
  - Tier configuration UI
- Phase 3: Advanced features

**Blocked:**
- None currently

**Questions/Decisions Needed:**
- None currently
