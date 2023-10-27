from decimal import Decimal

from .constants import Axis


def rect_intersect(item1, item2, x, y, x_spacing=0, y_spacing=0):
    """Check if two items intersect in the given axis."""
    d1 = item1.get_dimension()
    d2 = item2.get_dimension()

    dx = abs(item1.position[x] - item2.position[x]) - x_spacing
    dy = abs(item1.position[y] - item2.position[y]) - y_spacing

    return dx < (d1[x] + d2[x]) / 2 and dy < (d1[y] + d2[y]) / 2


def intersect(item1, item2, x_spacing=0, y_spacing=0, z_spacing=0):
    """Check if two items intersect."""
    return (
        rect_intersect(item1, item2, Axis.Y_AXIS, Axis.Z_AXIS, y_spacing, z_spacing)
        and rect_intersect(item1, item2, Axis.Z_AXIS, Axis.X_AXIS, z_spacing, x_spacing)
        and rect_intersect(item1, item2, Axis.Y_AXIS, Axis.X_AXIS, y_spacing, x_spacing)
    )


def get_limit_number_of_decimals(number_of_decimals):
    return Decimal('1.{}'.format('0' * number_of_decimals))


def set_to_decimal(value, number_of_decimals):
    number_of_decimals = get_limit_number_of_decimals(number_of_decimals)

    return Decimal(value).quantize(number_of_decimals)
