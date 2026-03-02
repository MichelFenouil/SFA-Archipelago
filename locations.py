from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location

from .addresses import T0_ADDRESS, T2_ADDRESS
from .items import SFAItem
from .regions import SFARegion

if TYPE_CHECKING:
    from .world import SFAWorld


class SFALocation(Location):
    """Location class for Star Fox Adventures."""

    game: str = "Star Fox Adventures"


class SFALocationType(Enum):
    """This class defines constants for various types of locations in Star Fox Adventures."""

    MCUPGRADE = auto()
    FUELCELL = auto()
    DIGSPOT = auto()
    SHOP = auto()
    MAP = auto()
    FLAG = auto()
    COUNT = auto()
    EVENT = auto()


@dataclass
class SFALocationData:
    """Data class for locations in Star Fox Adventures."""

    id: int
    bit_offset: int
    table_address: int
    type: SFALocationType
    region: SFARegion


@dataclass
class SFAUpgradeLocationData(SFALocationData):
    """Data class for magic cave upgrade locations."""

    linked_item: int
    mc_bitflag: int


@dataclass
class SFAShopLocationData(SFALocationData):
    """Data class for shop locations."""

    linked_item: int
    cost: int


@dataclass
class SFALinkedLocationData(SFALocationData):
    """Data class for magic cave upgrade locations."""

    linked_item: int
    map_address: int
    map_bit_size: int
    map_value: int
    state: bool = True


@dataclass
class SFACountLocationData(SFALocationData):
    """Data class for count locations."""

    count: int
    bit_size: int


def locations_name_to_id_dict() -> dict[str, int]:
    """Name to id dict for Star Fox Adventures locations."""
    return {name: data.id for name, data in LOCATION_TABLE.items()}


def create_regular_locations(world: SFAWorld) -> None:
    """Create locations for AP world."""
    for loc_name, loc_data in LOCATION_TABLE.items():
        if world.options.shop_locations == "nothing" and loc_data in LOCATION_SHOP.values():
            continue
        if world.options.shop_locations == "no_map" and loc_data.type == SFALocationType.MAP:
            continue

        region = world.get_region(loc_data.region.value)
        sfa_location = SFALocation(world.player, loc_name, loc_data.id, region)
        if loc_name == "DIM: Defeat Boss Galdon":
            sfa_location.place_locked_item(SFAItem("Victory", ItemClassification.progression, 2000, world.player))
        region.locations.append(sfa_location)
        world.progress_locations.add(loc_name)
    print(f"Added locations: {[list(world.get_locations())]}")  # noqa: T201


def create_events(world: SFAWorld) -> None:
    """Create events for AP world."""
    # darkice_mines = world.get_region(SFARegion.DIM_BOTTOM.value)
    # darkice_mines.add_event(
    #     "Defeated Boss Galdon",
    #     "Victory",
    #     location_type=SFALocation,
    #     item_type=SFAItem,
    #     rule=lambda state: has_blaster(state, world.player) and state.has("Tricky (Progressive)", world.player, 2)
    # )


def create_all_locations(world: SFAWorld) -> None:
    """Generate all locations for the world."""
    create_regular_locations(world)
    create_events(world)


LOCATION_UPGRADE: dict[str, SFAUpgradeLocationData] = {
    "TTH: Fire Blaster Upgrade": SFAUpgradeLocationData(
        1, 0x06FC, T2_ADDRESS, SFALocationType.MCUPGRADE, SFARegion.TH, 2, 0
    ),
    "TTH Well: Staff Booster Upgrade": SFAUpgradeLocationData(
        2, 0x0706, T2_ADDRESS, SFALocationType.MCUPGRADE, SFARegion.TH, 3, 1
    ),
}

LOCATION_SHOP: dict[str, SFAShopLocationData] = {
    "TTH Store: Rock Candy": SFAShopLocationData(200, 0x035F, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 200, 10),
    "TTH Store: Hi-Tech Display Device": SFAShopLocationData(
        201, 0x035E, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 201, 20
    ),
    "TTH Store: Tricky Ball": SFAShopLocationData(202, 0x084C, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 202, 15),
    "TTH Store: BafomDad Holder": SFAShopLocationData(
        203, 0x09EE, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 203, 20
    ),
    "TTH Store: FireFly Lantern": SFAShopLocationData(
        204, 0x0717, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 204, 20
    ),
    "TTH Store: Snowhorn Artifact": SFAShopLocationData(
        205, 0x0060, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 205, 130
    ),
    "TTH Store: Map Cape Claw": SFAShopLocationData(210, 0x0841, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "TTH Store: Map Ocean Force Point": SFAShopLocationData(
        211, 0x083F, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 10
    ),
    "TTH Store: Map Krazoa Palace": SFAShopLocationData(
        212, 0x083D, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "TTH Store: Map Dragon Rock": SFAShopLocationData(213, 0x0839, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "TTH Store: Map ThornTail Hollow": SFAShopLocationData(
        214, 0x0837, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "TTH Store: Map Moon Pass": SFAShopLocationData(215, 0x0845, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "TTH Store: Map LightFoot Village": SFAShopLocationData(
        216, 0x0836, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "TTH Store: Map DarkIce Mines": SFAShopLocationData(
        217, 0x0833, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "TTH Store: Map CloudRunner Fortress": SFAShopLocationData(
        218, 0x0835, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "TTH Store: Map Walled City": SFAShopLocationData(219, 0x0840, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "TTH Store: Map SnowHorn Wastes": SFAShopLocationData(
        220, 0x0834, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "TTH Store: Map Volcano Force Point": SFAShopLocationData(
        221, 0x0832, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 10
    ),
}

LOCATION_ANY: dict[str, SFALocationData] = {
    "SHW: Magic Upgrade": SFALocationData(20, 0x0010, T2_ADDRESS, SFALocationType.FLAG, SFARegion.SW_WATERSPOUT),
    "SHW: Feed Alpine Root 1": SFACountLocationData(
        21, 0x0033, T2_ADDRESS, SFALocationType.COUNT, SFARegion.SW_WATERSPOUT, 1, 3
    ),
    "SHW: Feed Alpine Root 2": SFACountLocationData(
        22, 0x0033, T2_ADDRESS, SFALocationType.COUNT, SFARegion.SW_WATERSPOUT, 2, 3
    ),
    "SHW: Rescue GateKeeper": SFALocationData(23, 0x0058, T2_ADDRESS, SFALocationType.FLAG, SFARegion.SW_ENTRANCE),
    "TTH Well: White GrubTub 1": SFALocationData(
        24, 0x00A8, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM
    ),
    "TTH Well: White GrubTub 2": SFALocationData(
        25, 0x00A7, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM
    ),
    "TTH Well: White GrubTub 3": SFALocationData(
        26, 0x00A5, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM
    ),
    "TTH Well: White GrubTub 4": SFALocationData(
        27, 0x00A3, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM
    ),
    "TTH Well: White GrubTub 5": SFALocationData(
        28, 0x00A4, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM
    ),
    "TTH Well: White GrubTub 6": SFALocationData(
        29, 0x00A6, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM
    ),
    "TTH: Magic Upgrade Above Store": SFALocationData(30, 0x0011, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH),
    "TTH: Feed Queen White GrubTubs": SFACountLocationData(
        31, 0x00AD, T2_ADDRESS, SFALocationType.COUNT, SFARegion.TH, 6, 3
    ),
    "DIM: Release Entrance SnowHorn": SFALocationData(
        32, 0x0366, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_ENTRANCE
    ),
    "DIM: Rescue Injured SnowHorn": SFALocationData(
        33, 0x036B, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_ENTRANCE
    ),
    "DIM: Feed Injured SnowHorn": SFALocationData(34, 0x036D, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_ENTRANCE),
    "DIM: Enemy Gate Cog Chest": SFALocationData(35, 0x0370, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_FORT),
    "DIM: Hut Cog Chest": SFALocationData(36, 0x0372, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_FORT),
    "DIM: Ice Cog Chest": SFALocationData(37, 0x0374, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_FORT),
    "DIM: Fire Puzzle Reward": SFALocationData(38, 0x03BC, T2_ADDRESS, SFALocationType.FLAG, SFARegion.DIM_FORT),
    # "DIM: Get Silver Key": SFALinkedLocationData(
    #     39,
    #     0x03DC,
    #     T2_ADDRESS,
    #     SFALocationType.FLAG,
    #     SFARegion.DIM_BOTTOM,
    #     linked_item=111,
    #     map_address=0x803A3891,
    #     map_bit_size=4,
    #     map_value=0x40042,
    # ),
    "DIM: Defeat Boss Galdon": SFALocationData(40, 0x0120, T0_ADDRESS, SFALocationType.EVENT, SFARegion.DIM_BOTTOM),
}

# Last id = 138
LOCATION_FUEL_CELL: dict[str, SFALocationData] = {
    # ThornTail Hollow
    "TTH: Queen Cave Fuel Cell": SFALocationData(100, 0x0945, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH: Pillar Fuel Cell Left": SFALocationData(101, 0x0946, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH: Pillar Fuel Cell Right": SFALocationData(102, 0x0943, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH: Beside WarpStone Fuel Cell Left": SFALocationData(
        103, 0x0947, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: Beside WarpStone Fuel Cell Right": SFALocationData(
        104, 0x0949, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: Waterfall Cave Fuel Cell Center": SFALocationData(
        105, 0x094E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: Waterfall Cave Fuel Cell Left": SFALocationData(
        106, 0x094C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: Waterfall Cave Fuel Cell Right": SFALocationData(
        107, 0x0950, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: Waterfall Cave Fuel Cell Back": SFALocationData(
        108, 0x0948, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: South Cave Fuel Cell Center": SFALocationData(
        109, 0x0944, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH
    ),
    "TTH: South Cave Fuel Cell Right": SFALocationData(110, 0x0942, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH: South Cave Fuel Cell Left": SFALocationData(111, 0x0941, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH: Above Store Fuel Cell Left": SFALocationData(112, 0x094F, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH: Above Store Fuel Cell Right": SFALocationData(113, 0x094D, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TTH Well: Fuel Cell Left": SFALocationData(128, 0x095D, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH_WELL),
    "TTH Well: Fuel Cell Right": SFALocationData(129, 0x095E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH_WELL),
    # Ice Mountain
    "IM: Cheat Well Fuel Cell": SFALocationData(114, 0x0957, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    "IM: Race Cave Fuel Cell Front": SFALocationData(115, 0x0955, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    "IM: Race Cave Fuel Cell Back": SFALocationData(116, 0x0956, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    # SnowHorn Wastes
    "SHW: Ice Block Fuel Cell Left": SFALocationData(
        117, 0x0958, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_WATERSPOUT
    ),
    "SHW: Ice Block Fuel Cell Right": SFALocationData(
        118, 0x0959, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_WATERSPOUT
    ),
    "SHW: Water Platform Fuel Cell Left": SFALocationData(
        119, 0x0952, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SHW: Water Platform Fuel Cell Right": SFALocationData(
        120, 0x0953, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),  # Also Linked to dig cave fuel cell
    "SHW: Dig Cave Near Entrance Fuel Cell": SFALocationData(
        121, 0x0954, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SHW: Path to TTH Booster Fuel Cell Left": SFALocationData(
        122, 0x095F, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SHW: Path to TTH Booster Fuel Cell Right": SFALocationData(
        123, 0x0960, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SHW: GateKeeper Blast Tree Fuel Cell Left": SFALocationData(
        133, 0x0967, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE
    ),
    "SHW: GateKeeper Blast Tree Fuel Cell Right": SFALocationData(
        134, 0x0968, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE
    ),
    "SHW: GateKeeper River Cheat Well Fuel Cell": SFALocationData(
        135, 0x0984, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE
    ),
    "SHW: GateKeeper River Ledge Fuel Cell Center": SFALocationData(
        136, 0x095A, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE
    ),
    "SHW: GateKeeper River Ledge Fuel Cell Right": SFALocationData(
        137, 0x095B, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE
    ),
    "SHW: GateKeeper River Ledge Fuel Cell Left": SFALocationData(
        138, 0x095C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE
    ),
    # LightFoot Village
    "TTH: Entrance to LFV Fuel Cell Right": SFALocationData(
        124, 0x094A, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV
    ),
    "TTH: Entrance to LFV Fuel Cell Left": SFALocationData(
        125, 0x094B, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV
    ),
    # "LFV Entrance Booster Ledge 1": SFALocationData(126, 0x096B, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV),
    # "LFV Entrance Booster Ledge 2": SFALocationData(127, 0x096C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV),
    # Moon Mountain Pass
    # "MMP Windy Path In": SFALocationData(130, 0x0985, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.MMP),
    # "MMP Windy Path Out": SFALocationData(131, 0x097E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.MMP),
    # "MMP Barrel Hill": SFALocationData(132, 0x0961, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.MMP),
}

# Last id = 307
LOCATION_DIG_SPOT: dict[str, SFALocationData] = {
    "SHW: Dig Alpine Root near Campfire": SFALocationData(
        300, 0x002F, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT
    ),
    "SHW: Dig Alpine Root near Fallen Tree": SFALocationData(
        301, 0x002E, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT
    ),
    "SHW: Dig Egg near Water Spout": SFALocationData(
        302, 0x003A, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT
    ),
    "SHW: Dig BafomDad near Entrance": SFALocationData(
        303, 0x086F, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_ENTRANCE
    ),
    "SHW: Dig in GateKeeper Cave": SFALocationData(307, 0x086E, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_GATE),
    "TTH: Dig Near Store": SFALocationData(304, 0x0857, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.TH),
    "TTH: Dig Near Queen Cave": SFALocationData(305, 0x0856, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.TH),
    "TTH: Dig in Entrance to LFV": SFALocationData(306, 0x0858, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.LFV),
    "DIM: Dig Alpine Root in Entrance Hut": SFALocationData(
        308, 0x037C, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.DIM_ENTRANCE
    ),
    "DIM: Dig Alpine Root in Boulder Path": SFALocationData(
        309, 0x037D, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.DIM_ENTRANCE
    ),
}

NORMAL_TABLES: dict[str, SFALocationData] = {
    **LOCATION_ANY,
    **LOCATION_FUEL_CELL,
    **LOCATION_DIG_SPOT,
}

LOCATION_TABLE: dict[str, SFALocationData] = {
    **LOCATION_UPGRADE,
    **LOCATION_SHOP,
    **LOCATION_ANY,
    **LOCATION_FUEL_CELL,
    **LOCATION_DIG_SPOT,
}
