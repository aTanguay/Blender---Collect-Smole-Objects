"""
Collect Smole Objects - Blender Extension
Modern extension format for Blender 4.2+

A Blender addon that collects and hides small objects by volume.
Perfect for cleaning up CAD imports with many tiny unwanted parts.

For legacy addon support (Blender 2.80+), see dev/Blender_CollectSmoleObjects_v01.py
"""

# Blender extension metadata is now in blender_manifest.toml (Blender 4.2+)
# No bl_info needed for modern extensions

import bpy

# Import addon modules
# Using importlib for proper reload support during development
if "bpy" in locals():
    import importlib
    if "utils" in locals():
        importlib.reload(utils)
    if "core" in locals():
        importlib.reload(core)
    if "analysis" in locals():
        importlib.reload(analysis)
    if "ui" in locals():
        importlib.reload(ui)

from . import utils
from . import core
from . import analysis
from . import ui


def register():
    """Register addon classes and UI elements."""
    ui.register()


def unregister():
    """Unregister addon classes and UI elements."""
    ui.unregister()


# Support running as script (for testing)
if __name__ == "__main__":
    register()
