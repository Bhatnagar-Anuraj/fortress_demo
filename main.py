"""
main.py -- Medieval Fortress Generator (Week 7: Data-Driven & Bulletproof)
===========================================================================
DIGM 131 - Week 7 | Author: Anuraj Bhatnagar

Assembles a complete fortress from configuration data using the
BUILDERS dispatcher pattern. Handles bad input gracefully.
"""

import os
import sys
import maya.cmds as cmds

try:
    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _THIS_DIR = cmds.workspace(query=True, rootDirectory=True)

if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import fortress_geometry as geo
import fortress_materials as mat


# ---------------------------------------------------------------------------
# Configuration Data
# ---------------------------------------------------------------------------
# Each dict is a "recipe" for one fortress element.
# "type" tells the dispatcher WHICH function to call.
# The rest are parameters for that function.
# Add a new element = add one dict. No code changes needed.

WALL_LENGTH = 16
WALL_HEIGHT = 5
HALF = WALL_LENGTH / 2.0

FORTRESS_CONFIG = [
    # Curtain walls (4 sides)
    {"type": "wall", "length": WALL_LENGTH, "height": WALL_HEIGHT,
     "position": (0, 0, HALF)},
    {"type": "wall", "length": WALL_LENGTH, "height": WALL_HEIGHT,
     "position": (0, 0, -HALF)},
    {"type": "wall", "length": WALL_LENGTH, "height": WALL_HEIGHT,
     "position": (HALF, 0, 0)},
    {"type": "wall", "length": WALL_LENGTH, "height": WALL_HEIGHT,
     "position": (-HALF, 0, 0)},

    # Corner towers
    {"type": "tower", "radius": 1.5, "height": 8,
     "position": (HALF, 0, HALF)},
    {"type": "tower", "radius": 1.5, "height": 8,
     "position": (-HALF, 0, HALF)},
    {"type": "tower", "radius": 1.5, "height": 8,
     "position": (HALF, 0, -HALF)},
    {"type": "tower", "radius": 1.5, "height": 8,
     "position": (-HALF, 0, -HALF)},

    # Central keep
    {"type": "keep", "width": 6, "floors": 3, "floor_height": 4,
     "position": (0, 0, 0)},

    # Gatehouse on the south wall
    {"type": "gatehouse", "position": (0, 0, -HALF)},
]

MATERIAL_PALETTE = {
    "walls":  ("castle_stone",  (0.55, 0.55, 0.50)),
    "towers": ("tower_stone",   (0.50, 0.48, 0.45)),
    "keep":   ("keep_dark",     (0.40, 0.38, 0.35)),
    "gate":   ("iron_gate",     (0.25, 0.22, 0.20)),
}

# Map element type names to the functions that build them.
# Functions are values -- you can store them in a dict and call them by key.
BUILDERS = {
    "wall":      geo.create_wall,
    "tower":     geo.create_tower,
    "keep":      geo.create_keep,
    "gatehouse": geo.create_gatehouse,
}

# Map element types to material keys for auto-assignment.
TYPE_MATERIALS = {
    "wall":      "walls",
    "tower":     "towers",
    "keep":      "keep",
    "gatehouse": "gate",
}


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def create_element(data):
    """Dispatch one config entry to the correct builder function.

    Looks up data["type"] in BUILDERS and calls the matching function
    with the remaining keys as ** keyword arguments.

    Args:
        data (dict): One entry from FORTRESS_CONFIG. Must have a "type" key.

    Returns:
        str or None: The created Maya node name, or None if failed.
    """
    element_type = data.get("type")

    # Check: does the entry have a type?
    if not element_type:
        cmds.warning("Config entry missing 'type' key -- skipping.")
        return None

    # Check: do we have a builder for this type?
    builder = BUILDERS.get(element_type)
    if not builder:
        cmds.warning("Unknown type '{}' -- skipping.".format(element_type))
        return None

    # Strip "type" before ** unpacking -- it's not a function parameter
    params = {k: v for k, v in data.items() if k != "type"}

    try:
        return builder(**params)
    except TypeError as error:
        cmds.warning("Bad params for '{}': {}".format(element_type, error))
        return None


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def build_fortress(config=None):
    """Build a complete fortress from configuration data.

    Args:
        config (list): List of config dicts. Defaults to FORTRESS_CONFIG.

    Returns:
        list: Names of all created Maya nodes.
    """
    if config is None:
        config = FORTRESS_CONFIG

    cmds.file(new=True, force=True)

    # Create materials
    shaders = {}
    for key, (name, color) in MATERIAL_PALETTE.items():
        shaders[key] = mat.create_material(name, color)

    # Ground plane
    ground = cmds.polyPlane(
        w=WALL_LENGTH * 2, h=WALL_LENGTH * 2,
        sx=1, sy=1, name="fortress_ground_#"
    )[0]

    results = [ground]

    # Process every entry in the config
    for entry in config:
        obj = create_element(entry)
        if obj:
            # Auto-assign material based on type
            mat_key = TYPE_MATERIALS.get(entry.get("type"))
            if mat_key and mat_key in shaders:
                mat.assign_material(obj, shaders[mat_key])
            results.append(obj)

    cmds.viewFit(allObjects=True)
    print("=== Fortress Complete ===")
    print("  {} elements from {} config entries.".format(
        len(results), len(config)))

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    build_fortress()

    # Bonus: test error handling with bad data
    print("\n--- Error handling tests ---")
    create_element({"type": "wall", "lenght": 16})    # Typo in key
    create_element({"length": 16, "height": 5})       # Missing type
    create_element({"type": "dragon", "size": 10})    # Unknown type
    create_element({"type": "wall", "length": -5})    # Negative value
    print("--- All tests passed (warnings, not crashes) ---")
