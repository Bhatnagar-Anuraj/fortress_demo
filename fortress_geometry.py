"""
fortress_geometry.py -- Geometry builders for medieval fortress elements.
=========================================================================
DIGM 131 - Week 6 Demo | Author: Anuraj Bhatnagar

Each function creates one type of fortress element and returns
the Maya node name(s). No materials or scene logic here.

Usage:
    import fortress_geometry as geo
    geo.create_wall(length=16, height=5, position=(0, 0, 8))
    Make sure you have downloaded fortress_geometry
"""

import maya.cmds as cmds


def create_wall(length=10, height=5, thickness=0.5, position=(0, 0, 0)):
    """Create a curtain wall segment.

    Args:
        length (float):    Wall length. Default 10.
        height (float):    Wall height. Default 5.
        thickness (float): Wall thickness. Default 0.5.
        position (tuple):  (x, y, z) center of the wall base.

    Returns:
        str: Name of the wall transform node.
    """
    wall = cmds.polyCube(
        w=length, h=height, d=thickness,
        name="wall_#"
    )[0]
    cmds.move(
        position[0], position[1] + height / 2.0, position[2], wall
    )
    return wall


def create_merlons(length=10, wall_height=5, merlon_size=0.6,
                   spacing=1.8, position=(0, 0, 0), axis="x"):
    """Create a row of battlements (merlons) along the top of a wall.

    Args:
        length (float):      Length of the wall to cover. Default 10.
        wall_height (float): Height of the wall below. Default 5.
        merlon_size (float): Size of each merlon cube. Default 0.6.
        spacing (float):     Distance between merlons. Default 1.8.
        position (tuple):    (x, y, z) center of the wall base.
        axis (str):          "x" or "z" -- direction the wall runs.

    Returns:
        list: Names of all merlon transform nodes.
    """
    merlons = []
    count = int(length / spacing)
    half = length / 2.0
    merlon_y = position[1] + wall_height + merlon_size / 2.0

    for i in range(count):
        offset = -half + spacing * 0.5 + i * spacing

        if axis == "x":
            mx, mz = position[0] + offset, position[2]
        else:
            mx, mz = position[0], position[2] + offset

        merlon = cmds.polyCube(
            w=merlon_size, h=merlon_size, d=merlon_size,
            name="merlon_#"
        )[0]
        cmds.move(mx, merlon_y, mz, merlon)
        merlons.append(merlon)

    return merlons


def create_tower(radius=1.5, height=8, position=(0, 0, 0)):
    """Create a round tower with a conical roof.

    Args:
        radius (float):   Tower radius. Default 1.5.
        height (float):   Tower body height. Default 8.
        position (tuple): (x, y, z) base center.

    Returns:
        str: Name of the tower group.
    """
    body = cmds.polyCylinder(
        r=radius, h=height,
        name="tower_body_#"
    )[0]
    cmds.move(
        position[0], position[1] + height / 2.0, position[2], body
    )

    roof = cmds.polyCone(
        r=radius * 1.4, h=radius * 2.0,
        name="tower_roof_#"
    )[0]
    cmds.move(
        position[0], position[1] + height + radius * 0.8, position[2], roof
    )

    return cmds.group(body, roof, name="tower_#")


def create_keep(width=6, floors=3, floor_height=4, position=(0, 0, 0)):
    """Create a central keep (tall rectangular tower) with battlements.

    Args:
        width (float):        Keep width and depth. Default 6.
        floors (int):         Number of floors. Default 3.
        floor_height (float): Height per floor. Default 4.
        position (tuple):     (x, y, z) base center.

    Returns:
        str: Name of the keep group.
    """
    total_height = floor_height * floors

    body = cmds.polyCube(
        w=width, h=total_height, d=width,
        name="keep_body_#"
    )[0]
    cmds.move(
        position[0], position[1] + total_height / 2.0, position[2], body
    )

    # Battlements on top
    merlons = create_merlons(
        length=width, wall_height=total_height,
        position=position, axis="x"
    )

    parts = [body] + merlons
    return cmds.group(parts, name="keep_#")


def create_gatehouse(width=2.5, height=3.5, tower_radius=1.0,
                     tower_height=6.5, position=(0, 0, 0)):
    """Create a gatehouse with an opening and two flanking towers.

    Args:
        width (float):        Gate opening width. Default 2.5.
        height (float):       Gate opening height. Default 3.5.
        tower_radius (float): Flanking tower radius. Default 1.0.
        tower_height (float): Flanking tower height. Default 6.5.
        position (tuple):     (x, y, z) center of gate.

    Returns:
        str: Name of the gatehouse group.
    """
    parts = []

    # Gate opening marker
    gate = cmds.polyCube(
        w=width, h=height, d=0.8,
        name="gate_opening_#"
    )[0]
    cmds.move(
        position[0], position[1] + height / 2.0, position[2], gate
    )
    parts.append(gate)

    # Flanking towers
    for side in [1, -1]:
        tower = create_tower(
            radius=tower_radius,
            height=tower_height,
            position=(position[0] + side * width, position[1], position[2])
        )
        parts.append(tower)

    return cmds.group(parts, name="gatehouse_#")


# -------------------------------------------------------------------
if __name__ == "__main__":
    cmds.file(new=True, force=True)

    create_wall(length=12, height=5, position=(0, 0, 6))
    create_tower(radius=1.5, height=8, position=(6, 0, 6))
    create_keep(width=5, floors=3, position=(0, 0, 0))
    create_gatehouse(position=(0, 0, -6))

    cmds.viewFit(allObjects=True)
    print("fortress_geometry self-test complete!")
