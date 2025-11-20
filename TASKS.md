# Development Tasks - Collect Smole Objects Addon

## Quick Reference
- **Current Version**: v1.1
- **Next Target Version**: v2.0
- **Last Updated**: 2025-11-20
- **Active Phase**: Phase 2a - UI Panel Development
- **Last Completed Phase**: Phase 1c - Multiple Threshold Methods ✓

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
- [ ] Create sidebar panel in 3D Viewport
  - [ ] Register panel in N-panel sidebar
  - [ ] Create "Collect Objects" tab
  - [ ] Design clean, intuitive layout
  - [ ] Add panel icons and visual hierarchy

### Method Selection UI
- [ ] Implement threshold method dropdown
  - [ ] Reference Object option
  - [ ] Percentage option
  - [ ] Absolute Volume option
  - [ ] Percentile option
  - [ ] Dynamic UI based on selection

### Dynamic Controls
- [ ] Create method-specific controls
  - [ ] Reference: Object selector with info
  - [ ] Percentage: Slider + numeric input
  - [ ] Absolute: Volume input with units
  - [ ] Percentile: Slider (0-100%)

### Information Display Panel
- [ ] Add statistics display section
  - [ ] Show current scene stats
  - [ ] Display threshold preview info
  - [ ] Affected object count
  - [ ] Estimated polygon count reduction
  - [ ] Visual progress indicators

### Action Buttons
- [ ] Implement main action buttons
  - [ ] "Analyze Scene" button
  - [ ] "Preview Selection" button (Phase 2b)
  - [ ] "Execute Collection" button
  - [ ] "Clear Preview" button (Phase 2b)
  - [ ] "Reset" button

---

## Phase 2b: Preview System

### Visual Preview
- [ ] Implement object highlighting system
  - [ ] Temporarily change object display color
  - [ ] Use viewport overlays for preview
  - [ ] Add wireframe/solid preview options
  - [ ] Clear preview state cleanly

### Selection Preview
- [ ] Create preview selection functionality
  - [ ] Select all objects that would be collected
  - [ ] Use Blender selection system
  - [ ] Allow inspection before execution
  - [ ] Add "hide preview" option

### Preview Object List
- [ ] Display affected objects list
  - [ ] Scrollable list in panel
  - [ ] Show object names and volumes
  - [ ] Click to focus/select object
  - [ ] Sort options (name, size, collection)

### Live Updates
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

---

## Current Sprint Focus

**Completed:**
- ✓ Phase 1a: Foundation & Error Handling (COMPLETE)
- ✓ Phase 1b: Scene Analysis System (COMPLETE)
- ✓ Phase 1c: Multiple Threshold Methods (COMPLETE)
- ✓ Project documentation (PLANNING.md, TASKS.md, CLAUDE.md)
- ✓ Dual-format packaging system
- ✓ Code refactoring into modules
- ✓ Complete backend API for threshold processing

**Active Tasks:**
- Ready to begin Phase 2a: UI Panel Development

**Next Up:**
- Phase 2a: UI panel development
  - Create sidebar panel in N-panel
  - Method selection dropdown
  - Dynamic controls for each method
  - Statistics display
  - Action buttons (Analyze, Preview, Execute)
- Phase 2b: Preview system
- Phase 2c: Multiple collection tiers

**Blocked:**
- None currently

**Questions/Decisions Needed:**
- None currently
