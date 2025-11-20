#!/usr/bin/env python3
"""
Package Collect Smole Objects addon for distribution.

Creates two package formats:
1. Legacy addon (Blender 2.80+) - single .py file in zip
2. Modern extension (Blender 4.2+) - folder with blender_manifest.toml
"""

import zipfile
import os
from pathlib import Path
import shutil

# Version info (should match bl_info and blender_manifest.toml)
VERSION = "1.1.0"

# Paths
SCRIPT_DIR = Path(__file__).parent
DEV_DIR = SCRIPT_DIR / "dev"
EXTENSION_DIR = SCRIPT_DIR / "collect_smole_objects"
RELEASE_DIR = SCRIPT_DIR / "release"

# Output filenames
LEGACY_FILENAME = f"Blender_CollectSmoleObjects_v{VERSION.replace('.', '')}_legacy.zip"
EXTENSION_FILENAME = f"collect_smole_objects_v{VERSION.replace('.', '')}_extension.zip"


def create_legacy_package():
    """Create legacy addon package (single .py file in zip)."""
    print(f"Creating legacy addon package: {LEGACY_FILENAME}")

    legacy_py = DEV_DIR / "Blender_CollectSmoleObjects_v01.py"
    output_zip = RELEASE_DIR / LEGACY_FILENAME

    if not legacy_py.exists():
        print(f"ERROR: Legacy addon file not found at {legacy_py}")
        return False

    # Create release directory if it doesn't exist
    RELEASE_DIR.mkdir(exist_ok=True)

    # Create zip with just the .py file
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(legacy_py, legacy_py.name)

    print(f"  ✓ Created: {output_zip}")
    print(f"  ✓ Size: {output_zip.stat().st_size:,} bytes")
    return True


def create_extension_package():
    """Create modern extension package (folder structure with manifest)."""
    print(f"Creating modern extension package: {EXTENSION_FILENAME}")

    init_py = EXTENSION_DIR / "__init__.py"
    manifest_toml = EXTENSION_DIR / "blender_manifest.toml"
    output_zip = RELEASE_DIR / EXTENSION_FILENAME

    if not init_py.exists():
        print(f"ERROR: Extension __init__.py not found at {init_py}")
        return False

    if not manifest_toml.exists():
        print(f"ERROR: Extension manifest not found at {manifest_toml}")
        return False

    # Create release directory if it doesn't exist
    RELEASE_DIR.mkdir(exist_ok=True)

    # Create zip with folder structure
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add all Python files (excluding __pycache__)
        for py_file in EXTENSION_DIR.glob("*.py"):
            arc_name = f"collect_smole_objects/{py_file.name}"
            zf.write(py_file, arc_name)

        # Add manifest
        arc_name = "collect_smole_objects/blender_manifest.toml"
        zf.write(manifest_toml, arc_name)

        # Future: Add additional modules when we refactor for v2.0
        # for module_file in EXTENSION_DIR.glob("**/*.py"):
        #     if "__pycache__" not in str(module_file):
        #         arc_name = module_file.relative_to(EXTENSION_DIR.parent)
        #         zf.write(module_file, arc_name)

    print(f"  ✓ Created: {output_zip}")
    print(f"  ✓ Size: {output_zip.stat().st_size:,} bytes")
    return True


def main():
    """Package both addon formats."""
    print("=" * 60)
    print("Collect Smole Objects - Packaging Script")
    print(f"Version: {VERSION}")
    print("=" * 60)
    print()

    success_count = 0

    # Create legacy package
    if create_legacy_package():
        success_count += 1
    print()

    # Create extension package
    if create_extension_package():
        success_count += 1
    print()

    # Summary
    print("=" * 60)
    if success_count == 2:
        print("✓ SUCCESS: Both packages created successfully!")
        print()
        print("Installation Instructions:")
        print()
        print("  Legacy Addon (Blender 2.80 - 4.1):")
        print(f"    Install: {LEGACY_FILENAME}")
        print("    Method: Preferences > Add-ons > Install (from disk)")
        print()
        print("  Modern Extension (Blender 4.2+):")
        print(f"    Install: {EXTENSION_FILENAME}")
        print("    Method: Preferences > Get Extensions > Install from Disk")
        print()
        print(f"  Both packages are in: {RELEASE_DIR}/")
    else:
        print("✗ ERROR: Some packages failed to create.")
        print("  Check error messages above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
