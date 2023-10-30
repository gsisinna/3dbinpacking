import json
from decimal import Decimal

from .auxiliary_methods import intersect, set_to_decimal
from .constants import Axis, RotationType


DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]


class Item:
    """Item class to be packed into a pallet."""

    def __init__(self, name, x_dim, y_dim, z_dim, weight):
        self.name = name
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.z_dim = z_dim
        self.weight = weight
        self.rotation_type = 0
        self.position = START_POSITION
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.x_dim = set_to_decimal(self.x_dim, number_of_decimals)
        self.y_dim = set_to_decimal(self.y_dim, number_of_decimals)
        self.z_dim = set_to_decimal(self.z_dim, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return '%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)' % (
            self.name,
            self.x_dim,
            self.y_dim,
            self.z_dim,
            self.weight,
            self.position,
            self.rotation_type,
            self.get_volume(),
        )

    def get_volume(self):
        return set_to_decimal(
            self.x_dim * self.y_dim * self.z_dim, self.number_of_decimals
        )

    def get_dimension(self):
        if self.rotation_type == RotationType.RT_XYZ:  # 0
            dimension = [self.x_dim, self.y_dim, self.z_dim]
        elif self.rotation_type == RotationType.RT_YXZ:  # 1
            dimension = [self.y_dim, self.x_dim, self.z_dim]
        elif self.rotation_type == RotationType.RT_YZX:  # 2
            dimension = [self.y_dim, self.z_dim, self.x_dim]
        elif self.rotation_type == RotationType.RT_ZYX:  # 3
            dimension = [self.z_dim, self.y_dim, self.x_dim]
        elif self.rotation_type == RotationType.RT_ZXY:  # 4
            dimension = [self.z_dim, self.x_dim, self.y_dim]
        elif self.rotation_type == RotationType.RT_XZY:  # 5
            dimension = [self.x_dim, self.z_dim, self.y_dim]
        else:
            dimension = []

        return dimension


class Pallet:
    """Pallet class to be packed with items."""

    def __init__(self, name, x_dim, y_dim, z_dim, max_weight, x_spacing=0.0, y_spacing=0.002, z_spacing=0.0):
        self.name = name
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.z_dim = z_dim
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.z_spacing = z_spacing
        self.max_weight = max_weight
        self.items = []
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def format_numbers(self, number_of_decimals):
        self.y_dim = set_to_decimal(self.y_dim, number_of_decimals)
        self.z_dim = set_to_decimal(self.z_dim, number_of_decimals)
        self.x_dim = set_to_decimal(self.x_dim, number_of_decimals)
        self.x_spacing = set_to_decimal(self.x_spacing, number_of_decimals)
        self.y_spacing = set_to_decimal(self.y_spacing, number_of_decimals)
        self.z_spacing = set_to_decimal(self.z_spacing, number_of_decimals)
        self.max_weight = set_to_decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return '%s(%sx%sx%s, max_weight:%s) vol(%s)' % (
            self.name,
            self.x_dim,
            self.y_dim,
            self.z_dim,
            self.max_weight,
            self.get_volume(),
        )

    def get_volume(self):
        return set_to_decimal(
            self.x_dim * self.y_dim * self.z_dim, self.number_of_decimals
        )

    def get_total_weight(self):
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return set_to_decimal(total_weight, self.number_of_decimals)

    def put_item(self, item, pivot):
        fit = False
        valid_item_position = item.position
        item.position = pivot

        for i in range(0, len(RotationType.ALL)):
            item.rotation_type = i
            dimension = item.get_dimension()
            if (
                self.x_dim < pivot[0] + dimension[0] + self.x_spacing
                or self.y_dim < pivot[1] + dimension[1] + self.y_spacing
                or self.z_dim < pivot[2] + dimension[2] + self.z_spacing
            ):
                continue

            fit = True

            for current_item_in_pallet in self.items:
                # Check if item intersect with other items
                if intersect(current_item_in_pallet, item, self.x_spacing, self.y_spacing, self.z_spacing):
                    fit = False
                    break

            if fit:
                if self.get_total_weight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                self.items.append(item)

            if not fit:
                item.position = valid_item_position

            return fit

        if not fit:
            item.position = valid_item_position

        return fit


class Packer:
    """Packer class to pack items into pallets."""

    def __init__(self, x_spacing, y_spacing, z_spacing, x_offset=0.0, y_offset=0.0, z_offset=0.0):
        self.pallets = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.z_spacing = z_spacing
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset

    def add_pallet(self, pallet):
        return self.pallets.append(pallet)

    def add_item(self, item):
        self.total_items = len(self.items) + 1

        return self.items.append(item)

    def pack_to_pallet(self, pallet, item):
        fitted = False

        if not pallet.items:
            response = pallet.put_item(item, [Decimal(self.x_offset), Decimal(self.y_offset), Decimal(self.z_offset)])

            if not response:
                pallet.unfitted_items.append(item)

            return

        for axis in range(0, 3):
            items_in_pallet = pallet.items

            for ib in items_in_pallet:
                pivot = [0, 0, 0]
                x_dim, y_dim, z_dim = ib.get_dimension()
                if axis == Axis.X_AXIS:
                    pivot = [ib.position[0] + x_dim + pallet.x_spacing, ib.position[1], ib.position[2]]
                elif axis == Axis.Y_AXIS:
                    pivot = [ib.position[0], ib.position[1] + y_dim + pallet.y_spacing, ib.position[2]]
                elif axis == Axis.Z_AXIS:
                    pivot = [ib.position[0], ib.position[1], ib.position[2] + z_dim + pallet.z_spacing]

                if pallet.put_item(item, pivot):
                    fitted = True
                    break
            if fitted:
                break

        if not fitted:
            pallet.unfitted_items.append(item)

    def pack(
        self,
        bigger_first=False,
        distribute_items=False,
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS,
    ):
        for pallet in self.pallets:
            pallet.format_numbers(number_of_decimals)

        for item in self.items:
            item.format_numbers(number_of_decimals)

        self.pallets.sort(key=lambda pallet: pallet.get_volume(), reverse=bigger_first)
        self.items.sort(key=lambda item: item.get_volume(), reverse=bigger_first)

        for pallet in self.pallets:
            for item in self.items:
                self.pack_to_pallet(pallet, item)

            if distribute_items:
                for item in pallet.items:
                    self.items.remove(item)

    def export_json(self, file_path):
        """Export packing result to JSON file."""
        result = {'boxes': []}
        # Iterate over all the boxes in the pallets and add them to the result
        for pallet in self.pallets:
            for item in pallet.items:
                result['boxes'].append(
                    {
                        'label': item.name,
                        'x': round(float(item.position[0]), 3),
                        'y': round(float(item.position[1]), 3),
                        'z': round(float(item.position[2]), 3),
                        'x_dim': round(float(item.x_dim), 3),
                        'y_dim': round(float(item.y_dim), 3),
                        'z_dim': round(float(item.z_dim), 3),
                        'weight': round(float(item.weight), 3),
                        'rotation': item.rotation_type,
                    }
                )

        # Order the boxes by their x coordinate (increasing), then y coordinate (increasing), then z coordinate (increasing)
        result['boxes'] = sorted(
            result['boxes'], key=lambda k: (k['x'], k['y'], k['z'])
        )

        with open(file_path, 'w') as f:
            json.dump(result, f, indent=4)
