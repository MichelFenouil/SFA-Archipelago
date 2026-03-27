from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Self, Type

from loguru import logger

from BaseClasses import Item, ItemClassification
from worlds.apquest.game.game import Game

from .bit_helper import GameBit
from .addresses import PLAYER_CUR_HP, PLAYER_CUR_MP, PLAYER_MAX_HP, PLAYER_MAX_MP, T2_ADDRESS

if TYPE_CHECKING:
    from .world import SFAWorld


class SFAItem(Item):
    """Item class for Star Fox Adventures."""

    game: str = "Star Fox Adventures"


class SFAItemTags(Enum):
    """This class defines constants for various types of items to know how to handle in game."""

    SHOP = auto()
    PLANET = auto()
    STARTING_ITEM = auto()
    SKIP_ITEMPOOL = auto()


@dataclass
class SFAItemData:
    """Data class for items in Star Fox Adventures."""

    id: int
    name: str
    game_bit: GameBit
    ap_classification: ItemClassification
    tags: list[SFAItemTags] = []

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

    @classmethod
    def get_by_name(cls, name: str) -> SFAItemData:
        """
        Return item for given name.

        :param cls: SFAItemData class
        :param name: Item name to search
        :return: SFAItemData for given name
        """
        return ALL_ITEMS_TABLE.get(
            name, SFAItemData(0, "", GameBit(0x0, 0x0), ItemClassification.filler)
        )

    def get_value(self) -> bool:
        """Get bit value for item."""
        return self.game_bit.get_bit()

    def set_value(self, value: bool) -> None:
        """Set bit for item."""
        self.game_bit.set_bit(value)

@dataclass
class SFAProgressiveItemData(SFAItemData):
    """Data class for progressive items."""

    game_bit: None # pyright: ignore[reportIncompatibleVariableOverride]
    progressive_data: list[GameBit] = []

    def set_value(self, value: int) -> None:
        """Set bits ON until value."""
        for index, bit in enumerate(self.progressive_data):
            bit.set_bit(value > index)


@dataclass
class SFACountItemData(SFAItemData):
    """Data class for count items."""

    max_count: int = 1
    count_increment: int = 1
    start_amount: int = 0

    def set_value(self, value: int) -> None:
        if value > self.max_count:
            value = self.max_count
        value = self.start_amount + value * self.count_increment
        self.game_bit.set_value(value)


@dataclass
class SFAQuestItemData(SFAItemData):
    """Data class for quest items."""

    max_count: int = 1
    count_increment: int = 1
    start_amount: int = 0
    used_count_bits: list[GameBit] = []

    def set_value(self, value: int) -> None:
        if value > self.max_count:
            value = self.max_count
        used_count = 0
        for bit in self.used_count_bits:
            used_count += bit.get_value()
        value = self.start_amount + (value - used_count) * self.count_increment
        if value < 0:
            value = 0
        self.game_bit.set_value(value)

@dataclass
class SFAConsumableItemData(SFAItemData):
    """Data class for consumable items."""

    increment_amount: int = 1
    max_amount_bit: GameBit | None = None

    def set_value(self, value: int = 0) -> None:
        current_value = self.game_bit.get_value()
        value = current_value + self.increment_amount
        max_value = self.max_amount_bit.get_value() if isinstance(self.max_amount_bit, GameBit) else 0
        if value > max_value:
            value = max_value
        self.game_bit.set_value(value)


@dataclass
class SFAPlanetItemData(SFAItemData):
    """Data class for planet items."""
    # TODO: Change for general ALL FLAGS items
    gate_bit: GameBit = GameBit(0x0)


def items_name_to_id_dict() -> dict[str, int]:
    """Name to id dict for Star Fox Adventures items."""
    return {name: data.id for name, data in ALL_ITEMS_TABLE.items()}


def get_random_filler_item_name(world: SFAWorld) -> str:
    """Generate filler items."""
    # Add filler percent in class?
    if world.random.randint(0, 99) < 20:
        return "Health Refill"
    if world.random.randint(0, 99) < 20:
        return "Magic Refill"
    return "Fuel Cell"


def create_item_classification(world: SFAWorld, name: str) -> SFAItem:
    """Create item with AP classification."""
    data = SFAItemData.get_by_name(name)
    return SFAItem(name, data.ap_classification, data.id, world.player)


def create_all_items(world: SFAWorld) -> None:
    """Generate all items for the world."""
    itempool: list[Item] = []

    for name, data in PROGRESSION_ITEMS.items():
        if SFAItemTags.SKIP_ITEMPOOL in data.tags:
            continue
        elif SFAItemTags.STARTING_ITEM in data.tags:
            world.push_precollected(world.create_item(name))
        elif isinstance(data, SFACountItemData):
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

    world.multiworld.itempool += itempool


ITEM_STAFF: dict[str, SFAItemData] = {
    "Staff": SFAItemData(
        1, "Staff", GameBit(0x0080), ItemClassification.progression, [SFAItemTags.STARTING_ITEM]
    ),
    "Fire Blaster": SFAItemData(2, "Fire Blaster", GameBit(0x06FC), ItemClassification.progression, []),
    "Staff Booster": SFAItemData(3, "Staff Booster", GameBit(0x0706), ItemClassification.progression, []),
}

ITEM_TRICKY: dict[str, SFAProgressiveItemData] = {
    "Tricky (Progressive)": SFAProgressiveItemData(
        10,
        "Tricky (Progressive)",
        None,
        ItemClassification.progression,
        progressive_data=[GameBit(0x0846), GameBit(0x084B)],
    ),
}

ITEM_PLANET: dict[str, SFAItemData] = {
    "Dinosaur Planet Access": SFAItemData(
        50,
        "Dinosaur Planet Access",
        GameBit(0x0930),
        ItemClassification.progression,
        [SFAItemTags.STARTING_ITEM, SFAItemTags.PLANET],
    ),
    "DarkIce Mines Access": SFAPlanetItemData(
        51,
        "DarkIce Mines Access",
        GameBit(0x093D),
        ItemClassification.progression,
        [SFAItemTags.PLANET],
        gate_bit=GameBit(0x0931),
    ),
    # "CloudRunner Fortress": SFAItemData(52, 0x093E, SFAItemType.PLANET, ItemClassification.progression),
    # "Walled City": SFAItemData(53, 0x093F, SFAItemType.PLANET, ItemClassification.progression),
    # "Dragon Rock": SFAItemData(54, 0x0940, SFAItemType.PLANET, ItemClassification.progression),
}

ITEM_INVENTORY: dict[str, SFAItemData] = {
    "Scarab Bag (Progressive)": SFAProgressiveItemData(
        100,
        "Scarab Bag (Progressive)",
        None,
        ItemClassification.progression,
        progressive_data=[GameBit(0x035B), GameBit(0x035C), GameBit(0x035D)],
    ),
    "Bomb Plant": SFAItemData(
        101, "Bomb Plant", GameBit(0x0), ItemClassification.progression, [SFAItemTags.STARTING_ITEM]
    ),
    "SHW Alpine Root": SFAQuestItemData(
        102,
        "SHW Alpine Root",
        GameBit(0x0030, bit_size=3),
        ItemClassification.progression,
        max_count=2,
        used_count_bits=[GameBit(0x0033, bit_size=3)]
    ),
    "White GrubTub": SFAQuestItemData(
        103,
        "White GrubTub",
        GameBit(0x00A9, bit_size=3),
        ItemClassification.progression,
        max_count=6,
        used_count_bits=[GameBit(0x00AD, bit_size=3)]
    ),
    "Gate Key": SFAItemData(104, "Gate Key", GameBit(0x00B0), ItemClassification.progression),
    "Entrance Bridge Cog": SFAItemData(
        105, "Entrance Bridge Cog", GameBit(0x036E), ItemClassification.progression
    ),
    "DIM Alpine Root": SFAQuestItemData(
        106,
        "DIM Alpine Root",
        GameBit(0x037E, bit_size=3),
        ItemClassification.progression,
        max_count=2,
        used_count_bits=[GameBit(0x036C)] # TODO: Missing more flags
    ),
    "SharpClaw Fort Bridge Cogs": SFAProgressiveItemData(
        107,
        "SharpClaw Fort Bridge Cogs",
        None,
        ItemClassification.progression,
        progressive_data=[GameBit(0x0371), GameBit(0x0373), GameBit(0x0375)],
    ),
    "Dinosaur Horn": SFAItemData(110, "Dinosaur Horn", GameBit(0x03A0), ItemClassification.progression),
    # "Cell Silver Key": SFAItemData(111, 0x03DC, SFAItemType.INVENTORY, ItemClassification.progression),
    # "Fire Spellstone 1": SFAItemData(112, 0x039E, SFAItemType.INVENTORY, ItemClassification.progression),
}

ITEM_SHOP: dict[str, SFAItemData] = {
    "Rock Candy": SFAItemData(
        200,
        "Rock Candy",
        GameBit(0x035F),
        ItemClassification.progression,
        [SFAItemTags.SHOP],
    ),
    "Hi-Tech Display Device": SFAItemData(
        201, "Hi-Tech Display Device", GameBit(0x035E), ItemClassification.useful, [SFAItemTags.SHOP]
    ),
    "Tricky Ball": SFAItemData(
        202, "Tricky Ball", GameBit(0x084C), ItemClassification.useful, [SFAItemTags.SHOP]
    ),
    "BafomDad Holder": SFAItemData(
        203, "BafomDad Holder", GameBit(0x09EE), ItemClassification.useful, [SFAItemTags.SHOP]
    ),
    "FireFly Lantern": SFAItemData(
        204,
        "FireFly Lantern",
        GameBit(0x0717),
        ItemClassification.progression,
        [SFAItemTags.SHOP],
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
    "Victory": SFAItemData(2000, "Victory", GameBit(0x0, 0x0), ItemClassification.progression, [SFAItemTags.SKIP_ITEMPOOL]),
}

USEFUL_ITEMS: dict[str, SFAItemData] = {
    "MP Upgrade": SFACountItemData(
        300,
        "MP Upgrade",
        GameBit(0x0, PLAYER_MAX_MP, bit_size=8),
        ItemClassification.useful,
        max_count=6,
        count_increment=25,
        start_amount=25,
    ),
    "HP Upgrade": SFACountItemData(
        301,
        "HP Upgrade",
        GameBit(0x0, PLAYER_MAX_HP, bit_size=8),
        ItemClassification.useful,
        max_count=6,
        count_increment=4,
        start_amount=12,
    ),
}

FILLER_ITEMS: dict[str, SFAItemData] = {
    "Fuel Cell": SFACountItemData(
        1001,
        "Fuel Cell",
        GameBit(0x0935, bit_size=8),
        ItemClassification.filler,
        max_count=255,
    ),
    "Health Refill": SFAConsumableItemData(
        1002,
        "Health Refill",
        GameBit(0x0, PLAYER_CUR_HP, bit_size=8),
        ItemClassification.filler,
        increment_amount=4,
        max_amount_bit=GameBit(0x0, PLAYER_MAX_HP, bit_size=8)
    ),
    "Magic Refill": SFAConsumableItemData(
        1003,
        "Magic Refill",
        GameBit(0x0, PLAYER_CUR_MP, bit_size=8),
        ItemClassification.filler,
        increment_amount=25,
        max_amount_bit=GameBit(0x0, PLAYER_MAX_MP, bit_size=8)
    ),
}

ALL_ITEMS_TABLE: dict[str, SFAItemData] = {
    **PROGRESSION_ITEMS,
    **USEFUL_ITEMS,
    **FILLER_ITEMS,
}
