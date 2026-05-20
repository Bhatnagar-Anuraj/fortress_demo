"""
fortress_materials.py -- Material creation and assignment for fortress.
========================================================================
DIGM 131 - Week 7 | Author: Anuraj Bhatnagar

Usage:
    import fortress_materials as mat
    stone = mat.create_material("stone_gray", (0.55, 0.55, 0.50))
    mat.assign_material("wall_1", stone)
"""

import maya.cmds as cmds


def create_material(name, color=(0.5, 0.5, 0.5)):
    """Create a Lambert shader with the given name and RGB color.

    If a shader with this name already exists, return it
    without creating a duplicate.

    Args:
        name (str):    Name for the shader node.
        color (tuple): (R, G, B) floats, each 0.0 - 1.0.

    Returns:
        str: The name of the shader node.
    """
    if cmds.objExists(name):
        return name

    shader = cmds.shadingNode("lambert", asShader=True, name=name)
    sg = cmds.sets(
        renderable=True, noSurfaceShader=True,
        empty=True, name="{}_SG".format(name)
    )
    cmds.connectAttr(
        "{}.outColor".format(shader),
        "{}.surfaceShader".format(sg),
        force=True
    )
    cmds.setAttr("{}.color".format(shader), *color, type="double3")
    return shader


def assign_material(obj_name, shader_name):
    """Assign a shader to a Maya object or group.

    Args:
        obj_name (str):    Transform, shape, or group node.
        shader_name (str): Shader node name.
    """
    if not cmds.objExists(obj_name) or not cmds.objExists(shader_name):
        cmds.warning("assign_material: object or shader not found.")
        return

    sg_list = cmds.listConnections(
        "{}.outColor".format(shader_name), type="shadingEngine"
    )
    if not sg_list:
        return

    shapes = cmds.listRelatives(
        obj_name, allDescendents=True, shapes=True, fullPath=True
    ) or []
    targets = shapes if shapes else [obj_name]
    cmds.sets(targets, edit=True, forceElement=sg_list[0])


# -------------------------------------------------------------------
if __name__ == "__main__":
    cmds.file(new=True, force=True)

    cube = cmds.polyCube(name="test_cube")[0]
    stone = create_material("test_stone", (0.6, 0.58, 0.52))
    assign_material(cube, stone)

    cmds.viewFit(allObjects=True)
    print("fortress_materials self-test complete!")
