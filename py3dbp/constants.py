class RotationType:
    """Rotation type of an item."""

    RT_XYZ = 0
    RT_YXZ = 1
    RT_YZX = 2
    RT_ZYX = 3
    RT_ZXY = 4
    RT_XZY = 5

    ALL = [RT_XYZ, RT_YXZ, RT_YZX, RT_ZYX, RT_ZXY, RT_XZY]


class Axis:
    """Axis of an item."""

    X_AXIS = 0
    Y_AXIS = 1
    Z_AXIS = 2

    ALL = [X_AXIS, Y_AXIS, Z_AXIS]
