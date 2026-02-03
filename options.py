from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions


class ShopLocations(Choice):
    """
    Choose which objects appear in the shop for locations.

    all_items: buy all items and maps
    no_map: only buy items
    nothing: nothing in the shop
    """

    display_name = "Remove Shop Maps"

    option_all_items = "all"
    option_no_map = "no_map"
    option_nothing = "nothing"

    default = "no_map"


@dataclass
class SFAOptions(PerGameCommonOptions):
    """Star Fox Adventures options class."""

    shop_locations: ShopLocations


option_groups = [
    OptionGroup(
        "Logic Options",
        [ShopLocations],
    ),
]
