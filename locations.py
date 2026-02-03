from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from BaseClasses import Location

from .addresses import T2_ADDRESS
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
        region.locations.append(sfa_location)
        world.progress_locations.add(loc_name)
    print(f"Added locations: {[list(world.get_locations())]}")  # noqa: T201


def create_events(world: SFAWorld) -> None:
    """Create events for AP world."""
    sw_entrance = world.get_region(SFARegion.SW_ENTRANCE.value)
    sw_entrance.add_event(
        "EVENT - Opened SnowHorn Wastes",
        "EVENT - Opened SnowHorn Wastes",
        location_type=SFALocation,
        item_type=SFAItem,
        rule=lambda state: state.has("Tricky", world.player),
    )


def create_all_locations(world: SFAWorld) -> None:
    """Generate all locations for the world."""
    create_regular_locations(world)
    create_events(world)


LOCATION_UPGRADE: dict[str, SFAUpgradeLocationData] = {
    "Fire Blaster Upgrade": SFAUpgradeLocationData(
        1, 0x06FC, T2_ADDRESS, SFALocationType.MCUPGRADE, SFARegion.TH, 2, 0
    ),
    "Staff Booster Upgrade": SFAUpgradeLocationData(
        2, 0x0706, T2_ADDRESS, SFALocationType.MCUPGRADE, SFARegion.TH, 3, 1
    ),
}

LOCATION_SHOP: dict[str, SFAShopLocationData] = {
    "Buy Rock Candy": SFAShopLocationData(200, 0x035F, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 200, 10),
    "Buy Hi-Tech Display Device": SFAShopLocationData(
        201, 0x035E, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 201, 20
    ),
    "Buy Tricky Ball": SFAShopLocationData(202, 0x084C, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 202, 15),
    "Buy Bafomdad Holder": SFAShopLocationData(203, 0x09EE, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 203, 20),
    "Buy Firefly Lantern": SFAShopLocationData(204, 0x0717, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 204, 20),
    "Buy Snowhorn Artifact": SFAShopLocationData(205, 0x0060, T2_ADDRESS, SFALocationType.SHOP, SFARegion.TH, 205, 130),
    "Buy Map Cape Claw": SFAShopLocationData(210, 0x0841, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map Ocean Force Point": SFAShopLocationData(211, 0x083F, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 10),
    "Buy Map Krazoa Palace": SFAShopLocationData(212, 0x083D, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map Dragon Rock": SFAShopLocationData(213, 0x0839, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map ThornTail Hollow": SFAShopLocationData(214, 0x0837, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map Moon Pass": SFAShopLocationData(215, 0x0845, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map LightFoot Village": SFAShopLocationData(216, 0x0836, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map DarkIce Mines": SFAShopLocationData(217, 0x0833, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map CloudRunner Fortress": SFAShopLocationData(
        218, 0x0835, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5
    ),
    "Buy Map Walled City": SFAShopLocationData(219, 0x0840, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map SnowHorn Wastes": SFAShopLocationData(220, 0x0834, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 5),
    "Buy Map Volcano Force Point": SFAShopLocationData(
        221, 0x0832, T2_ADDRESS, SFALocationType.MAP, SFARegion.TH, 0, 10
    ),
}

LOCATION_ANY: dict[str, SFALocationData] = {
    "SW Magic Upgrade": SFALocationData(20, 0x0010, T2_ADDRESS, SFALocationType.FLAG, SFARegion.SW_WATERSPOUT),
    "SW Give Alpine Root 1": SFACountLocationData(
        21, 0x033, T2_ADDRESS, SFALocationType.COUNT, SFARegion.SW_WATERSPOUT, 1, 3
    ),
    "SW Give Alpine Root 2": SFACountLocationData(
        22, 0x033, T2_ADDRESS, SFALocationType.COUNT, SFARegion.SW_WATERSPOUT, 2, 3
    ),
    "SW Rescue Gate Keeper": SFALocationData(23, 0x0058, T2_ADDRESS, SFALocationType.FLAG, SFARegion.SW_ENTRANCE),
    "TH Dark Well Shroom 1": SFALocationData(24, 0x00A8, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM),
    "TH Dark Well Shroom 2": SFALocationData(25, 0x00A7, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM),
    "TH Dark Well Shroom 3": SFALocationData(26, 0x00A5, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM),
    "TH Dark Well Shroom 4": SFALocationData(27, 0x00A3, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM),
    "TH Dark Well Shroom 5": SFALocationData(28, 0x00A4, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM),
    "TH Dark Well Shroom 6": SFALocationData(29, 0x00A6, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH_WELL_BOTTOM),
    "TH Above Shop Magic Upgrade": SFALocationData(30, 0x00B1, T2_ADDRESS, SFALocationType.FLAG, SFARegion.TH),
}

# Last id = 138
LOCATION_FUEL_CELL: dict[str, SFALocationData] = {
    # ThornTail Hollow
    # Queen Cave Fuel Cell disapear on Act 2
    # "TH Queen Cave Fuel Cell": SFALocationData(100, 0x0945, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "TH Pillar Fuel Cell Left": SFALocationData(101, 0x0946, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Pillar Fuel Cell Right": SFALocationData(102, 0x0943, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Beside Warpstone Left": SFALocationData(103, 0x0947, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Beside Warpstone Right": SFALocationData(104, 0x0949, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Waterfall Cave 1": SFALocationData(105, 0x094E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Waterfall Cave 2": SFALocationData(106, 0x094C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Waterfall Cave 3": SFALocationData(107, 0x0950, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Waterfall Cave Back": SFALocationData(108, 0x0948, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH South Cave 1": SFALocationData(109, 0x0944, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH South Cave 2": SFALocationData(110, 0x0942, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH South Cave 3": SFALocationData(111, 0x0941, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Shop Booster Ledge 1": SFALocationData(112, 0x094F, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Shop Booster Ledge 2": SFALocationData(113, 0x094D, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH),
    "TH Well Booster Ledge 1": SFALocationData(128, 0x095D, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH_WELL),
    "TH Well Booster Ledge 2": SFALocationData(129, 0x095E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.TH_WELL),
    # Ice Mountain
    "IM Cheat Well Cave": SFALocationData(114, 0x0957, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    "IM Race Cave Front": SFALocationData(115, 0x0955, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    "IM Race Cave Back": SFALocationData(116, 0x0956, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    # SnowHorn Wastes
    "SW Ice Block Left": SFALocationData(117, 0x0958, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_WATERSPOUT),
    "SW Ice Block Right": SFALocationData(118, 0x0959, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_WATERSPOUT),
    "SW Cold Water Left": SFALocationData(119, 0x0952, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE),
    "SW Cold Water Right (also dig cave)": SFALocationData(
        120, 0x0953, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SW Dig Cave Left": SFALocationData(121, 0x0954, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE),
    "SW Transition Booster Left": SFALocationData(
        122, 0x095F, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SW Transition Booster Right": SFALocationData(
        123, 0x0960, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE
    ),
    "SW Gate After Tree 1": SFALocationData(133, 0x0967, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE),
    "SW Gate After Tree 2": SFALocationData(134, 0x0968, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE),
    "SW Gate River Cheat Well": SFALocationData(135, 0x0984, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE),
    "SW Gate River Ledge 1": SFALocationData(136, 0x095A, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE),
    "SW Gate River Ledge 2": SFALocationData(137, 0x095B, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE),
    "SW Gate River Ledge 3": SFALocationData(138, 0x095C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_GATE),
    # LightFoot Village
    "TH Cape Claw Entrance 1": SFALocationData(124, 0x094A, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV),
    "TH Cape Claw Entrance 2": SFALocationData(125, 0x094B, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV),
    # "LFV Entrance Booster Ledge 1": SFALocationData(126, 0x096B, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV),
    # "LFV Entrance Booster Ledge 2": SFALocationData(127, 0x096C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.LFV),
    # Moon Mountain Pass
    # "MMP Windy Path In": SFALocationData(130, 0x0985, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.MMP),
    # "MMP Windy Path Out": SFALocationData(131, 0x097E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.MMP),
    # "MMP Barrel Hill": SFALocationData(132, 0x0961, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.MMP),
}

# Last id = 307
LOCATION_DIG_SPOT: dict[str, SFALocationData] = {
    "SW Dig Alpine Root 1": SFALocationData(300, 0x002F, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT),
    "SW Dig Alpine Root 2": SFALocationData(301, 0x002E, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT),
    "SW Dig Water Spout Egg": SFALocationData(
        302, 0x003A, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT
    ),
    "SW Dig Entrance Bafomdad": SFALocationData(
        303, 0x086F, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_ENTRANCE
    ),
    "SW Gate Dig Cave": SFALocationData(307, 0x086E, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_GATE),
    "TH Dig Near Shop": SFALocationData(304, 0x0857, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.TH),
    "TH Dig Near Queen Cave": SFALocationData(305, 0x0856, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.TH),
    "TH Dig Cape Claw Entrance": SFALocationData(306, 0x0858, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.LFV),
}

LOCATION_EVENTS: dict[str, SFALocationData] = {
    "EVENT - Opened SnowHorn Wastes": SFALocationData(
        1000, 0x008E, T2_ADDRESS, SFALocationType.EVENT, SFARegion.SW_ENTRANCE
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
