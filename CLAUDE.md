# Claude Session Guide - Blender Collect Smole Objects

## Essential Start-Up Actions

**ALWAYS READ THESE FILES FIRST:**
1. **PLANNING.md** - Complete project vision, improvements, and design decisions
2. **TASKS.md** - Current implementation status and active work items

**THEN REVIEW:**
3. **README.md** - User-facing description and current functionality
4. Current addon code in `/dev/` or `/release/`

## Project Context

### What This Is
Blender addon that collects and hides small objects in CAD imports based on volume. Used for cleaning up automotive UDM models, product renders, and complex CAD data with unwanted tiny parts (screws, springs, etc.).

### Current State
- **Version**: 1.1 (released - basic functionality)
- **Status**: v2.0 development - Phase 1 COMPLETE, Phase 2a in progress
- **Current Features**:
  - v1.1: Single reference-object method (legacy addon + modern extension)
  - v2.0 Backend: Complete modular architecture with 5 threshold methods, scene analysis, validation
- **Target**: Full UI panel integration (Phase 2a), preview system (Phase 2b), multi-tier collections (Phase 2c)

### Key Problem Being Solved
Users struggle with scale-dependent workflows - a threshold that works for a Sony Walkman won't work for a car or building. The addon needs to be smarter and more flexible.

## Development Approach

### Before Making Changes
1. Check TASKS.md to see what's in progress
2. Review PLANNING.md for the reasoning behind decisions
3. Update TASKS.md when starting/completing tasks
4. Follow the phased implementation order

### Implementation Phases (In Order)
- **Phase 1a**: ✅ COMPLETE - Error handling and validation (foundation)
- **Phase 1b**: ✅ COMPLETE - Scene analysis and statistics
- **Phase 1c**: ✅ COMPLETE - Multiple threshold methods
- **Phase 2a**: 🚧 IN PROGRESS - UI panel development
- **Phase 2b**: 📋 PLANNED - Preview system
- **Phase 2c**: 📋 PLANNED - Multiple collection tiers
- **Phase 3**: 📋 PLANNED - Advanced features

### Code Organization
Current structure (refactored):
```
/collect_smole_objects/
  __init__.py          # Main registration with reload support
  core.py              # Volume calculations, threshold methods (395 lines)
  analysis.py          # Scene analysis, statistics, suggestions (354 lines)
  ui.py                # Operators, menus (current) → panels (Phase 2a)
  utils.py             # Validation, helpers (160 lines)
  blender_manifest.toml # Modern extension metadata
```

Legacy: Single file at `dev/Blender_CollectSmoleObjects_v01.py` (for Blender 2.80-4.1)

## Critical Technical Details

### Volume Calculation Method
- Uses BMesh for accurate mesh volume (not bounding box)
- Requires evaluated depsgraph for modifier support
- Must handle empty/invalid meshes gracefully

### Blender API Requirements
- Minimum Blender 2.80+ (uses evaluated_depsgraph_get)
- Operator registered in VIEW3D_MT_select_object menu
- Future: Panel in VIEW3D_PT_sidebar

### Testing Considerations
Must test across different scales:
- Small: Product models (Walkman, phone) ~0.001-0.1 m³
- Medium: Furniture, automotive ~0.1-10 m³
- Large: Architecture, vehicles ~10-1000 m³

## Common Tasks & Patterns

### When Implementing New Features
1. Add comprehensive error handling (Phase 1a priority)
2. Provide user feedback (warnings, confirmations, statistics)
3. Support undo (bl_options = {'REGISTER', 'UNDO'})
4. Test with edge cases (empty meshes, modifiers, hidden objects)
5. Update TASKS.md checkboxes

### When Fixing Bugs
1. Add validation to prevent recurrence
2. Improve error messages
3. Update documentation
4. Mark task complete in TASKS.md

### When Adding UI Elements
1. Keep consistent with Blender UI conventions
2. Provide tooltips (bl_description)
3. Group related controls
4. Show feedback/confirmation
5. Test with different Blender themes

## Git Workflow

### Branch Strategy
- Work on feature branches with `claude/` prefix
- Branch name includes session ID (auto-configured)
- Commit regularly with clear messages
- Push when tasks complete

### Commit Message Style
Follow existing convention (see git log):
```
Add scene analysis system

- Implement volume statistics calculation
- Add percentile distribution analysis
- Create threshold suggestion logic
```

## User Interaction Principles

### Error Messages Should
- Be specific about what went wrong
- Suggest how to fix the problem
- Use Blender's report system: `self.report({'WARNING'}, "message")`

### UI Should
- Show preview before execution
- Display statistics (object count, polygon impact)
- Provide threshold suggestions
- Allow adjustment without re-analysis

### Performance Should
- Handle 1000+ objects efficiently
- Show progress for long operations
- Cache analysis results when possible
- Allow cancellation

## Quick Reference

### Key Files
- `PLANNING.md` - Why and what
- `TASKS.md` - Progress tracking
- `README.md` - User documentation
- `dev/Blender_CollectSmoleObjects_v01.py` - Current implementation
- `LICENSE` - GNU GPL v3

### Important Blender APIs
- `bpy.data.objects` - All objects in file
- `bpy.context.selected_objects` - User selection
- `bmesh.calc_volume()` - Volume calculation
- `depsgraph.evaluated_get()` - Handle modifiers
- `bpy.data.collections` - Collection management

### Testing Quick Checks
- Does it handle no selection gracefully?
- Does it work with modified objects?
- Does it show user what will happen?
- Does it support undo?
- Are error messages helpful?

## Session Workflow

### Starting a Session
```
1. Read PLANNING.md for context
2. Read TASKS.md to see status
3. Identify current active phase
4. Check for blockers or questions
5. Begin implementation
```

### During Session
```
1. Update TASKS.md as you progress
2. Mark tasks [🔄] when started
3. Mark tasks [✓] when completed
4. Add notes to TASKS.md if needed
5. Commit frequently
```

### Ending a Session
```
1. Update TASKS.md with final status
2. Commit all changes
3. Push to feature branch
4. Update "Notes & Decisions" in TASKS.md if applicable
```

## Common Questions

**Q: Should I refactor the single file first?**
A: Only after Phase 1a validation is implemented. Refactor when adding Phase 1b.

**Q: How to handle backward compatibility?**
A: Keep simple menu operator alongside new panel. Users can use either.

**Q: What if a task isn't in TASKS.md?**
A: Add it under appropriate phase with [ ] checkbox, then implement.

**Q: How to prioritize between phases?**
A: Always complete current phase before moving to next. Don't skip ahead.

**Q: User requests feature from Phase 3?**
A: Note it in TASKS.md but explain foundation must be built first.

## Critical Reminders

- **Phase 1 Complete!** - Backend API fully functional
- **User feedback always** - No silent operations
- **Test edge cases** - Empty meshes, modifiers, scale extremes
- **Update docs** - TASKS.md and code comments
- **Commit often** - Small, focused commits
- **UI integration next** - Connect backend to Blender UI elements

## Phase 1 Accomplishments

### Phase 1a - Foundation & Error Handling ✅
- Modular architecture (utils, core, analysis, ui)
- Comprehensive validation system
- Graceful error recovery with skip logic
- Console logging for debugging

### Phase 1b - Scene Analysis System ✅
- Full statistical analysis (min/max/mean/median/std dev)
- Percentile calculations with linear interpolation
- Natural gap detection (3x+ size jumps)
- 4 smart threshold recommendations with reasoning
- Impact preview calculations

### Phase 1c - Multiple Threshold Methods ✅
- 5 threshold methods implemented
- Unified processor (calculate_threshold_volume)
- Method-specific metadata
- Full validation for all methods
- Backend API complete

### Phase 2a - UI Panel Development ✅
- Full sidebar panel in N-panel ("Collect" tab)
- Method selection dropdown with 5 options
- Dynamic controls that change per method
- Scene analysis button with statistics display
- Property group for UI state management
- Clean Blender-style layout with sections

### Phase 2b - Preview System ✅
- Preview operator that selects objects before collection
- Clear preview operator to reset selection
- Preview statistics display (object count, polygon count, percentage)
- Preview/Clear Preview buttons in UI panel
- Automatic preview clearing after collect operation

## Future Feature Ideas

### Occlusion Detection (Phase 3+)
User-requested feature for detecting hidden/internal objects in CAD assemblies:
- **Problem**: Product models (like Walkman) include internal mechanics never seen in renders
- **Goal**: Detect and collect fully occluded objects (objects hidden inside other objects)
- **Approach**: Multi-directional raycast analysis to determine visibility percentage
- **Integration**: New "Occlusion" threshold method with sensitivity slider
- **See**: PLANNING.md "Future Considerations" and TASKS.md "Phase 3" for detailed breakdown

---

**Last Updated**: 2025-11-20
**Current Phase**: Phase 2c - Multiple Collection Tiers
**Phase 2b Status**: ✅ COMPLETE (Preview system functional)
**Next Milestone**: Implement tiered collection system (Tiny/Small/Medium)
