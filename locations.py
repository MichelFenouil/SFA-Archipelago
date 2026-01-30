from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Literal

from BaseClasses import Location
from .regions import SFARegion
from .addresses import T0_ADDRESS, T1_ADDRESS, T2_ADDRESS
from .items import SFAItem

if TYPE_CHECKING:
    from .world import SFAWorld

class SFALocation(Location):
    game: str = "Star Fox Adventure"

class SFALocationType(Enum):
    """
    This class defines constants for various types of locations in Star Fox Adventure
    """

    MCUPGRADE = auto()
    FUELCELL = auto()
    DIGSPOT = auto()
    SHOP = auto()
    MAP = auto()
    FLAG = auto()
    COUNT = auto()

@dataclass
class SFALocationData():
    """
    This class represents the data for a location in Star Fox Adventure

    :param id: The unique identifier for the location.
    """
    id: int
    bit_offset: int
    table_address: int
    type: SFALocationType
    region: SFARegion

@dataclass
class SFAUpgradeLocationData(SFALocationData):
    linked_item: int
    mc_bitflag: int

@dataclass
class SFAShopLocationData(SFALocationData):
    linked_item: int
    cost: int

@dataclass
class SFACountLocationData(SFALocationData):
    count: int
    bit_size: int

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_TABLE[location_name].id for location_name in location_names}

def locations_name_to_id_dict():
    return {name: data.id for name, data in LOCATION_TABLE.items()}

def create_all_locations(world: SFAWorld) -> None:
    create_regular_locations(world)
    create_events(world)

def create_regular_locations(world: SFAWorld) -> None:
    for loc_name, loc_data in LOCATION_TABLE.items():
        if world.options.shop_locations == "nothing" and loc_data in LOCATION_SHOP.values():
            continue
        if world.options.shop_locations == "no_map" and loc_data.type == SFALocationType.MAP:
            continue

        region = world.get_region(loc_data.region.value)
        sfa_location = SFALocation(world.player, loc_name, loc_data.id, region)
        region.locations.append(sfa_location)
        world.progress_locations.add(loc_name)
    print(f"Added locations: {[_ for _ in world.get_locations()]}")

def create_events(world: SFAWorld) -> None:
    sw_entrance = world.get_region(SFARegion.SH_SW_TRANSITION.value)
    sw_entrance.add_event("EVENT - Opened SnowHorn Wastes", "EVENT - Opened SnowHorn Wastes", location_type=SFALocation, item_type=SFAItem)


LOCATION_UPGRADE: dict[str, SFAUpgradeLocationData] = {
    "Fireblaster Upgrade": SFAUpgradeLocationData(1, 0x06FC, T2_ADDRESS, SFALocationType.MCUPGRADE, SFARegion.SH, 2, 0)
}

LOCATION_SHOP: dict[str, SFAShopLocationData] = {
    "Buy Rock Candy": SFAShopLocationData(200, 0x035F, T2_ADDRESS, SFALocationType.SHOP, SFARegion.SH, 200, 10),
    "Buy Hi-Tech Display Device": SFAShopLocationData(201, 0x035E, T2_ADDRESS, SFALocationType.SHOP, SFARegion.SH, 201, 20),
    "Buy Tricky Ball": SFAShopLocationData(202, 0x084C, T2_ADDRESS, SFALocationType.SHOP, SFARegion.SH, 202, 15),
    "Buy Bafomdad Holder": SFAShopLocationData(203, 0x09EE, T2_ADDRESS, SFALocationType.SHOP, SFARegion.SH, 203, 20),
    "Buy Firefly Lantern": SFAShopLocationData(204, 0x0717, T2_ADDRESS, SFALocationType.SHOP, SFARegion.SH, 204, 20),
    "Buy Snowhorn Artifact": SFAShopLocationData(205, 0x0060, T2_ADDRESS, SFALocationType.SHOP, SFARegion.SH, 205, 130),

    "Buy Map Cape Claw": SFAShopLocationData(210, 0x0841, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map Ocean Force Point": SFAShopLocationData(211, 0x083F, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 10),
    "Buy Map Krazoa Palace": SFAShopLocationData(212, 0x083D, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map Dragon Rock": SFAShopLocationData(213, 0x0839, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map ThornTail Hollow": SFAShopLocationData(214, 0x0837, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map Moon Pass": SFAShopLocationData(215, 0x0845, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map LightFoot Village": SFAShopLocationData(216, 0x0836, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map DarkIce Mines": SFAShopLocationData(217, 0x0833, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map CloudRunner Fortress": SFAShopLocationData(218, 0x0835, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map Walled City": SFAShopLocationData(219, 0x0840, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map SnowHorn Wastes": SFAShopLocationData(220, 0x0834, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 5),
    "Buy Map Volcano Force Point": SFAShopLocationData(221, 0x0832, T2_ADDRESS, SFALocationType.MAP, SFARegion.SH, 0, 10),
}

LOCATION_ANY: dict[str, SFALocationData] = {
    "SW Magic Upgrade": SFALocationData(20, 0x0010, T2_ADDRESS, SFALocationType.FLAG, SFARegion.SW_WATERSPOUT),
    "SW Give Alpine Root 1": SFACountLocationData(21, 0x033, T2_ADDRESS, SFALocationType.COUNT, SFARegion.SW_WATERSPOUT, 1, 3),
}

# Max id = 123
LOCATION_FUEL_CELL: dict[str, SFALocationData] = {
    # ThornTail Hollow
    "SH Queen Cave Fuel Cell": SFALocationData(100, 0x0945, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Pillar Fuel Cell Left": SFALocationData(101, 0x0946, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Pillar Fuel Cell Right": SFALocationData(102, 0x0943, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Beside Warpstone Left": SFALocationData(103, 0x0947, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Beside Warpstone Right": SFALocationData(104, 0x0949, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Waterfall Cave 1": SFALocationData(105, 0x094E, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Waterfall Cave 2": SFALocationData(106, 0x094C, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Waterfall Cave 3": SFALocationData(107, 0x0950, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Waterfall Cave Back": SFALocationData(108, 0x0948, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH South Cave 1": SFALocationData(109, 0x0944, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH South Cave 2": SFALocationData(110, 0x0942, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH South Cave 3": SFALocationData(111, 0x0941, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Booster Ledge Left": SFALocationData(112, 0x094F, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),
    "SH Booster Ledge Right": SFALocationData(113, 0x094D, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH),

    #Ice Mountain
    "IM Cheat Well Cave": SFALocationData(114, 0x0957, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    "IM Race Cave Front": SFALocationData(115, 0x0955, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),
    "IM Race Cave Back": SFALocationData(116, 0x0956, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.IM),

    #SnowHorn Wastes
    "SW Ice Block Left": SFALocationData(117, 0x0958, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_WATERSPOUT),
    "SW Ice Block Right": SFALocationData(118, 0x0959, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_WATERSPOUT),
    "SW Cold Water Left": SFALocationData(119, 0x0952, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE),
    "SW Cold Water Right (also dig cave)": SFALocationData(120, 0x0953, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE),
    "SW Dig Cave Left": SFALocationData(121, 0x0954, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SW_ENTRANCE),
    "SW Transition Booster Left": SFALocationData(122, 0x095F, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH_SW_TRANSITION),
    "SW Transition Booster Right": SFALocationData(123, 0x0960, T2_ADDRESS, SFALocationType.FUELCELL, SFARegion.SH_SW_TRANSITION),
}

# Max id = 303
LOCATION_DIG_SPOT: dict[str, SFALocationData] = {
    "SW Dig Alpine Root 1": SFALocationData(300, 0x002F, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT),
    "SW Dig Alpine Root 2": SFALocationData(301, 0x002E, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT),
    "SW Dig Water Spout Egg": SFALocationData(302, 0x003A, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_WATERSPOUT),
    "SW Dig Entrance Bafomdad": SFALocationData(303, 0x086F, T2_ADDRESS, SFALocationType.DIGSPOT, SFARegion.SW_ENTRANCE),
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