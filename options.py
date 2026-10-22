from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

## Goal Options


class GoalOption(Choice):
    """
    Choose the goal to complete the game.

    Collect: Collect all Spell Stones and Krazoa Spirits to complete the game.
    Place: Collect and place all the Spell Stones and Krazoa Spirits to complete the game.
    """

    display_name = "Goal"

    option_collect = "collect"
    option_place = "place"

    default = "collect"


class RequiredBoss(Range):
    """Required boss to defeat to complete the game."""

    display_name = "Required Boss"

    range_start = 0
    range_end = 2

    default = 2


class RequiredSpellStones(Range):
    """Required number of SpellStones to collect to complete the game."""

    display_name = "Required SpellStones"

    range_start = 0
    range_end = 2

    default = 2


class RequiredSpirits(Range):
    """Required number of Krazoa Spirits to collect to complete the game."""

    display_name = "Required Spirits"

    range_start = 0
    range_end = 2

    default = 2


## Logic Options


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
    and receiving the item unlocks the plant.
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


class LightfootEntrance(Choice):
    """
    Choose how to shuffle the entrance to LightFoot Village.

    vanilla: Gate can be opened out of logic with vanilla tree code, AP item will open the gate for logic
    always_open: Gate is always open, no code required
    ap_item: Gate stays closed and can only be opened with the AP item
    """

    display_name = "LightFoot Village Entrance"

    option_vanilla = "vanilla"
    option_always_open = "always_open"
    option_ap_item = "ap_item"

    default = "vanilla"


class LightfootQuests(Toggle):
    """Put LightFoot Village tests and side quests in logic."""

    display_name = "LightFoot Village Quests"

    default = False


## QoL Options


class InfiniteConsumables(Toggle):
    """
    Always have max consumables once unlocked (seeds, fireflies, etc.).

    Moon Seeds require Ground Quake to be collected without this option.
    """

    display_name = "Infinite Consumables"

    default = False


class InfiniteTrickyFood(Toggle):
    """Always have max Tricky food."""

    display_name = "Infinite Tricky Food"

    default = False


@dataclass
class SFAOptions(PerGameCommonOptions):
    """Star Fox Adventures options class."""

    goal_completion: GoalOption
    required_boss: RequiredBoss
    required_spellstones: RequiredSpellStones
    required_spirits: RequiredSpirits

    shop_locations: ShopLocations
    plant_shuffle: PlantShuffle
    dark_rooms: DarkRoomLogic
    lightfoot_entrance: LightfootEntrance
    lightfoot_quests: LightfootQuests

    infinite_consumables: InfiniteConsumables
    infinite_tricky_food: InfiniteTrickyFood


option_groups = [
    OptionGroup(
        "Goal Options",
        [GoalOption, RequiredBoss, RequiredSpellStones, RequiredSpirits],
    ),
    OptionGroup(
        "Logic Options",
        [ShopLocations, PlantShuffle, DarkRoomLogic, LightfootEntrance, LightfootQuests],
    ),
    OptionGroup(
        "Quality of Life Options",
        [InfiniteConsumables, InfiniteTrickyFood],
    ),
]
