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


class PlantShuffle(Toggle):
    """
    Shuffle plant items.

    Bomb Spores and Moon Seeds are locked at the beginning of the game,
    and receiving the item unlocks the plant with infinite uses.
    """

    display_name = "Shuffle Plant Items"

    default = True


class DarkRoomLogic(Toggle):
    """
    Put Dark Rooms in logic without FireFly Lantern.

    false: Dark Rooms require FireFly Lantern to access
    true: Dark Rooms can be accessed without FireFly Lantern
    """

    display_name = "Dark Room Logic"

    default = False


@dataclass
class SFAOptions(PerGameCommonOptions):
    """Star Fox Adventures options class."""

    shop_locations: ShopLocations
    plant_shuffle: PlantShuffle
    dark_rooms: DarkRoomLogic


option_groups = [
    OptionGroup(
        "Logic Options",
        [ShopLocations],
    ),
]
