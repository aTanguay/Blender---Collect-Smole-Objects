# Packaging Guide - Collect Smole Objects

## Overview

This addon is distributed in two formats to support different Blender versions:

1. **Modern Extension** (Blender 4.2+) - Uses `blender_manifest.toml`
2. **Legacy Addon** (Blender 2.80-4.1) - Uses `bl_info` dictionary

## Directory Structure

```
Blender---Collect-Smole-Objects/
├── collect_smole_objects/          # Modern extension source
│   ├── __init__.py                 # Main addon code
│   └── blender_manifest.toml       # Extension metadata
├── dev/                            # Development files
│   ├── Blender_CollectSmoleObjects_v01.py  # Legacy addon source
│   └── Dev_CollectSmoleObjects_v01.blend   # Test scene
├── release/                        # Built packages (generated)
│   ├── collect_smole_objects_v110_extension.zip
│   └── Blender_CollectSmoleObjects_v110_legacy.zip
├── package.py                      # Build script
└── package.sh                      # Convenience wrapper
```

## Building Packages

### Quick Build (Recommended)

Run the packaging script to create both formats:

```bash
python3 package.py
```

Or use the shell wrapper:

```bash
./package.sh
```

This will create both packages in the `release/` folder.

### Manual Build

If you need to build packages manually:

**Legacy Addon:**
```bash
cd dev/
zip ../release/Blender_CollectSmoleObjects_v110_legacy.zip Blender_CollectSmoleObjects_v01.py
```

**Modern Extension:**
```bash
cd collect_smole_objects/
zip -r ../release/collect_smole_objects_v110_extension.zip . -x "*.pyc" -x "__pycache__/*"
```

## Version Management

When updating the version number, update it in THREE places:

1. **blender_manifest.toml** (line 5-6):
   ```toml
   id = "collect_smole_objects"
   version = "1.1.0"
   ```

2. **collect_smole_objects/__init__.py** (commented bl_info for reference):
   ```python
   # "version": (1, 1, 0),
   ```

3. **dev/Blender_CollectSmoleObjects_v01.py** (bl_info):
   ```python
   bl_info = {
       "version": (1, 1, 0),
   ```

4. **package.py** (line 14):
   ```python
   VERSION = "1.1.0"
   ```

## Package Contents

### Legacy Addon Package
```
Blender_CollectSmoleObjects_v110_legacy.zip
└── Blender_CollectSmoleObjects_v01.py    # Single file addon
```

### Modern Extension Package
```
collect_smole_objects_v110_extension.zip
└── collect_smole_objects/
    ├── __init__.py                       # Main code
    └── blender_manifest.toml             # Metadata
```

## Testing Packages

### Test Legacy Addon (Blender 2.80-4.1)
1. Open Blender (version 2.80 to 4.1)
2. Edit > Preferences > Add-ons
3. Click "Install..." and select the legacy zip
4. Enable the addon
5. Test: 3D View > Select > Collect Smaller Objects

### Test Modern Extension (Blender 4.2+)
1. Open Blender (version 4.2+)
2. Edit > Preferences > Get Extensions
3. Click dropdown (⌄) > Install from Disk
4. Select the extension zip
5. Enable the extension
6. Test: 3D View > Select > Collect Smaller Objects

## Adding New Files (Future Development)

When refactoring for v2.0 with multiple modules:

1. **Create module files** in `collect_smole_objects/`:
   ```
   collect_smole_objects/
   ├── __init__.py
   ├── core.py              # New
   ├── analysis.py          # New
   ├── ui.py                # New
   ├── utils.py             # New
   └── blender_manifest.toml
   ```

2. **Update package.py** to include new files (already handles `*.py` files automatically)

3. **Legacy addon** may need to stay as single file or use alternative approach

## Metadata Fields

### blender_manifest.toml
Required fields:
- `schema_version`: Must be "1.0.0"
- `id`: Unique identifier (no spaces, lowercase)
- `version`: Semantic version (e.g., "1.1.0")
- `name`: Display name
- `tagline`: Short description
- `maintainer`: "Name <email or URL>"
- `type`: "add-on" or "theme"
- `blender_version_min`: Minimum Blender version
- `license`: SPDX identifier

Optional fields:
- `website`: Project URL
- `tags`: List of category tags
- `blender_version_max`: Maximum Blender version
- `copyright`: Copyright holders
- `permissions`: Network, files, clipboard, etc.

### bl_info (Legacy)
Required fields:
- `name`: Addon name
- `author`: Author name(s)
- `version`: Tuple (major, minor, patch)
- `blender`: Minimum version tuple
- `category`: Category for addon browser

Optional fields:
- `description`: Short description
- `location`: Where to find the addon
- `doc_url`: Documentation URL
- `tracker_url`: Bug tracker URL

## Build Automation

The `package.py` script:
- ✓ Creates both legacy and extension packages
- ✓ Uses ZIP compression
- ✓ Excludes `.pyc` and `__pycache__`
- ✓ Validates source files exist
- ✓ Reports file sizes
- ✓ Shows installation instructions

## Distribution Checklist

Before releasing a new version:

- [ ] Update version in all 4 locations
- [ ] Update changelog/release notes
- [ ] Test legacy addon in Blender 2.80+
- [ ] Test modern extension in Blender 4.2+
- [ ] Run `python3 package.py` to build packages
- [ ] Verify package contents with `unzip -l`
- [ ] Test installation from both packages
- [ ] Update README.md with new version numbers
- [ ] Commit changes to git
- [ ] Tag release: `git tag v1.1.0`
- [ ] Push packages to GitHub releases

## Troubleshooting

**Package script fails:**
- Ensure Python 3 is installed
- Check that source files exist in expected locations
- Verify file permissions

**Legacy addon won't install:**
- Ensure .py file is directly in zip root (not in subfolder)
- Check bl_info format is valid Python dict

**Extension won't install:**
- Ensure folder structure is correct (folder name must match `id` in manifest)
- Validate TOML syntax in manifest
- Check Blender version is 4.2+

**Addon doesn't appear in menu:**
- Verify addon is enabled in preferences
- Check for errors in Blender console (Window > Toggle System Console)
- Ensure register/unregister functions are working

## Future: Multi-File Extension

When we refactor for v2.0, the extension structure will expand:

```
collect_smole_objects/
├── __init__.py              # Registration and imports
├── core.py                  # Volume calculations, object processing
├── analysis.py              # Scene analysis, statistics
├── ui.py                    # Panels, operators
├── utils.py                 # Validation, helpers
├── blender_manifest.toml    # Metadata
└── README.md                # Optional: extension-specific docs
```

The package.py script is already designed to handle this - it includes all `.py` files automatically.

## Resources

- [Blender Extensions Documentation](https://docs.blender.org/manual/en/latest/advanced/extensions/)
- [Blender Add-on Tutorial](https://docs.blender.org/manual/en/latest/advanced/scripting/addon_tutorial.html)
- [TOML Specification](https://toml.io/)
- [Semantic Versioning](https://semver.org/)
