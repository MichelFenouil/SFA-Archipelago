from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .addresses import PLAYER_CUR_HP, PLAYER_CUR_MP, PLAYER_MAX_HP, PLAYER_MAX_MP, T2_ADDRESS

if TYPE_CHECKING:
    from .world import SFAWorld


class SFAItem(Item):
    """Item class for Star Fox Adventures."""

    game: str = "Star Fox Adventures"


class SFAItemType(Enum):
    """This class defines constants for various types of items to know how to handle in game."""

    STAFF = auto()
    TRICKY = auto()
    INVENTORY = auto()
    PROGRESSIVE = auto()
    CONSUMABLE = auto()
    SHOP_PROGRESSION = auto()
    SHOP_USEFUL = auto()
    USEFUL = auto()
    FILLER = auto()
    PLANET = auto()


@dataclass
class SFAItemData:
    """Data class for items in Star Fox Adventures."""

    id: int
    bit_offset: int
    table_address: int
    type: SFAItemType
    ap_classification: ItemClassification

    @classmethod
    def get_by_id(cls, id: int) -> SFAItemData | None:
        """
        Return item for given id.

        :param cls: SFAItemData class
        :param id: Item id to search
        :return: SFAItemData for given id
        """
        for item in ALL_ITEMS_TABLE.values():
            if item.id == id:
                return item
        return None


@dataclass
class SFAStaffItemData(SFAItemData):
    """Data class for staff items."""

    mc_bitflag: int | None = None
    linked_location: int | None = None


@dataclass
class SFAProgressiveItemData(SFAItemData):
    """Data class for progressive items."""

    # offset, address, count
    progressive_data: list[tuple]


@dataclass
class SFACountItemData(SFAItemData):
    """Data class for count items."""

    max_count: int
    bit_size: int
    count_increment: int = 1
    start_amount: int = 0


@dataclass
class SFAQuestItemData(SFACountItemData):
    """Data class for quest items."""

    item_used_flag_offset: int = 0x0
    item_used_bit_size: int = 1


@dataclass
class SFAConsumableItemData(SFAItemData):
    """Data class for consumable items."""

    add_value: int
    bit_size: int
    max_read_address: int
    max_read_bit_size: int


def items_name_to_id_dict() -> dict[str, int]:
    """Name to id dict for Star Fox Adventures items."""
    return {name: data.id for name, data in ALL_ITEMS_TABLE.items()}


def get_random_filler_item_name(world: SFAWorld) -> str:
    """Generate filler items."""
    if world.random.randint(0, 99) < 20:
        return "Health Refill"
    if world.random.randint(0, 99) < 20:
        return "Magic Refill"
    return "Fuel Cell"


def create_item_classification(world: SFAWorld, name: str) -> SFAItem:
    """Create item with AP classification."""
    data = ALL_ITEMS_TABLE[name]
    return SFAItem(name, data.ap_classification, data.id, world.player)


def create_all_items(world: SFAWorld) -> None:
    """Generate all items for the world."""
    itempool: list[Item] = []

    for name, data in PROGRESSION_ITEMS.items():
        if name == "Staff" or name == "Bomb Plant" or name == "Dinosaur Planet" or name == "Victory":
            continue
        if isinstance(data, SFACountItemData):
            itempool.extend([world.create_item(name) for _ in range(data.max_count)])
        elif isinstance(data, SFAProgressiveItemData):
            itempool.extend([world.create_item(name) for _ in range(len(data.progressive_data))])
        else:
            itempool.append(world.create_item(name))

    # Add a few player upgrades
    itempool.append(world.create_item("MP Upgrade"))
    itempool.append(world.create_item("MP Upgrade"))
    itempool.append(world.create_item("HP Upgrade"))
    itempool.append(world.create_item("HP Upgrade"))

    # Fill with filler items
    needed_number_of_filler_items = len(world.multiworld.get_unfilled_locations(world.player)) - len(itempool)

    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    print(f"Added items: {itempool}")  # noqa: T201

    world.multiworld.itempool += itempool

    # Start with Staff and Bomb Plant for logic (might shuffle later)
    world.push_precollected(world.create_item("Staff"))
    world.push_precollected(world.create_item("Bomb Plant"))
    world.push_precollected(world.create_item("Dinosaur Planet"))


ITEM_STAFF: dict[str, SFAStaffItemData] = {
    "Staff": SFAStaffItemData(1, 0x0080, T2_ADDRESS, SFAItemType.STAFF, ItemClassification.progression),
    "Fire Blaster": SFAStaffItemData(2, 0x06FC, T2_ADDRESS, SFAItemType.STAFF, ItemClassification.progression),
    "Staff Booster": SFAStaffItemData(3, 0x0706, T2_ADDRESS, SFAItemType.STAFF, ItemClassification.progression),
}

ITEM_TRICKY: dict[str, SFAItemData] = {
    "Tricky (Progressive)": SFAProgressiveItemData(
        10,
        0x0,
        T2_ADDRESS,
        SFAItemType.TRICKY,
        ItemClassification.progression,
        [(0x0846, T2_ADDRESS, 1), (0x084B, T2_ADDRESS, 1)],
    ),
}

ITEM_PLANET: dict[str, SFAItemData] = {
    "Dinosaur Planet": SFAItemData(50, 0x0930, T2_ADDRESS, SFAItemType.PLANET, ItemClassification.progression),
    "DarkIce Mines": SFAItemData(51, 0x093D, T2_ADDRESS, SFAItemType.PLANET, ItemClassification.progression),
    # "CloudRunner Fortress": SFAItemData(52, 0x093E, T2_ADDRESS, SFAItemType.PLANET, ItemClassification.progression),
    # "Walled City": SFAItemData(53, 0x093F, T2_ADDRESS, SFAItemType.PLANET, ItemClassification.progression),
    # "Dragon Rock": SFAItemData(54, 0x0940, T2_ADDRESS, SFAItemType.PLANET, ItemClassification.progression),
}

ITEM_INVENTORY: dict[str, SFAItemData] = {
    "Scarab Bag (Progressive)": SFAProgressiveItemData(
        100,
        0x0,
        T2_ADDRESS,
        SFAItemType.PROGRESSIVE,
        ItemClassification.progression,
        [(0x035B, T2_ADDRESS, 1), (0x035C, T2_ADDRESS, 1), (0x035D, T2_ADDRESS, 1)],
    ),
    "Bomb Plant": SFAItemData(101, 0x0, T2_ADDRESS, SFAItemType.INVENTORY, ItemClassification.progression),
    "Alpine Root": SFAQuestItemData(
        102,
        0x0030,
        T2_ADDRESS,
        SFAItemType.INVENTORY,
        ItemClassification.progression,
        max_count=2,
        bit_size=3,
        item_used_flag_offset=0x0033,
        item_used_bit_size=3,
    ),
    "White GrubTub": SFAQuestItemData(
        103,
        0x00A9,
        T2_ADDRESS,
        SFAItemType.INVENTORY,
        ItemClassification.progression,
        max_count=6,
        bit_size=3,
        item_used_flag_offset=0x00AD,
        item_used_bit_size=3,
    ),
    "Gate Key": SFAItemData(104, 0x00B0, T2_ADDRESS, SFAItemType.INVENTORY, ItemClassification.progression),
    "Cog 1": SFAItemData(105, 0x036E, T2_ADDRESS, SFAItemType.INVENTORY, ItemClassification.progression),
    "DIM Alpine Root": SFAQuestItemData(
        106,
        0x037E,
        T2_ADDRESS,
        SFAItemType.INVENTORY,
        ItemClassification.progression,
        max_count=2,
        bit_size=3,
        item_used_flag_offset=0x036C,
    ),  # Problem if given 1, you will receive 1 again
    "Cog 2/3/4": SFAProgressiveItemData(
        107,
        0x0371,
        T2_ADDRESS,
        SFAItemType.INVENTORY,
        ItemClassification.progression,
        [(0x0371, T2_ADDRESS, 1), (0x0373, T2_ADDRESS, 1), (0x0375, T2_ADDRESS, 1)],
    ),
    "Dinosaur Horn": SFAItemData(110, 0x03A0, T2_ADDRESS, SFAItemType.INVENTORY, ItemClassification.progression),
    "Cell Silver Key": SFAItemData(111, 0x03DC, T2_ADDRESS, SFAItemType.INVENTORY, ItemClassification.progression),
    # "Fire Spellstone 1": SFAItemData(112, 0x039E, T2_ADDRESS, SFAItemType.INVENTORY, ItemClassification.progression),
}

ITEM_SHOP: dict[str, SFAItemData] = {
    "Rock Candy": SFAItemData(
        200,
        0x035F,
        T2_ADDRESS,
        SFAItemType.SHOP_PROGRESSION,
        ItemClassification.progression,
    ),
    "Hi-Tech Display Device": SFAItemData(201, 0x035E, T2_ADDRESS, SFAItemType.SHOP_USEFUL, ItemClassification.useful),
    "Tricky Ball": SFAItemData(202, 0x084C, T2_ADDRESS, SFAItemType.SHOP_USEFUL, ItemClassification.useful),
    "Bafomdad Holder": SFAItemData(203, 0x09EE, T2_ADDRESS, SFAItemType.SHOP_USEFUL, ItemClassification.useful),
    "Firefly Lantern": SFAItemData(
        204,
        0x0717,
        T2_ADDRESS,
        SFAItemType.SHOP_PROGRESSION,
        ItemClassification.progression,
    ),
    # Gives access to unimplemented area
    # "Snowhorn Artifact": SFAItemData(
    #     205,
    #     0x0060,
    #     T2_ADDRESS,
    #     SFAItemType.SHOP_PROGRESSION,
    #     ItemClassification.progression,
    # ),
}

PROGRESSION_ITEMS: dict[str, SFAItemData] = {
    **ITEM_STAFF,
    **ITEM_INVENTORY,
    **ITEM_SHOP,
    **ITEM_TRICKY,
    **ITEM_PLANET,
    "Victory": SFAItemData(2000, 0x0, 0x0, SFAItemType.FILLER, ItemClassification.progression),
}

USEFUL_ITEMS: dict[str, SFAItemData] = {
    "MP Upgrade": SFACountItemData(
        300,
        0x0,
        PLAYER_MAX_MP,
        SFAItemType.USEFUL,
        ItemClassification.useful,
        6,
        8,
        25,
        25,
    ),
    "HP Upgrade": SFACountItemData(
        301,
        0x0,
        PLAYER_MAX_HP,
        SFAItemType.USEFUL,
        ItemClassification.useful,
        6,
        8,
        4,
        12,
    ),
}

FILLER_ITEMS: dict[str, SFAItemData] = {
    "Fuel Cell": SFACountItemData(
        1001,
        0x0935,
        T2_ADDRESS,
        SFAItemType.FILLER,
        ItemClassification.filler,
        max_count=255,
        bit_size=8,
    ),
    "Health Refill": SFAConsumableItemData(
        1002,
        0x0,
        PLAYER_CUR_HP,
        SFAItemType.FILLER,
        ItemClassification.filler,
        add_value=4,
        bit_size=8,
        max_read_address=PLAYER_MAX_HP,
        max_read_bit_size=8,
    ),
    "Magic Refill": SFAConsumableItemData(
        1003,
        0x0,
        PLAYER_CUR_MP,
        SFAItemType.FILLER,
        ItemClassification.filler,
        add_value=25,
        bit_size=8,
        max_read_address=PLAYER_MAX_MP,
        max_read_bit_size=8,
    ),
}

ALL_ITEMS_TABLE: dict[str, SFAItemData] = {
    **PROGRESSION_ITEMS,
    **USEFUL_ITEMS,
    **FILLER_ITEMS,
}
