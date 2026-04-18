from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Toggle


class ShopLocations(Choice):
    """
    Choose which objects appear in the shop as locations.

    all_items: All shop items and maps are randomized
    no_map: Only the shop items are randomized, the maps are bought from the start
    nothing: Nothing in the shop is randomized, all items and maps are bought from the start
    """

    display_name = "Shop Locations"

    option_all_items = "all"
    option_no_map = "no_map"
    option_nothing = "nothing"

    default = "no_map"

class SeedShuffle(Toggle):
    """Toggle to shuffle seed items."""

    display_name = "Shuffle Seed Items"

    default = True


@dataclass
class SFAOptions(PerGameCommonOptions):
    """Star Fox Adventures options class."""

    shop_locations: ShopLocations
    seed_shuffle: SeedShuffle


option_groups = [
    OptionGroup(
        "Logic Options",
        [ShopLocations],
    ),
]
