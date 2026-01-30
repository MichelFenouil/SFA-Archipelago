from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

from BaseClasses import Region

from .macros import *

if TYPE_CHECKING:
    from .world import SFAWorld


class SFARegion(Enum):
    """
    Region names for Star Fox Adventure
    """
    WORLDMAP = "World Map"
    SH = "ThornTail Hollow" # Originally SwapStone Hollow in game
    IM = "Ice Mountain"
    SW_WATERSPOUT = "SnowHorn Wastes - Water Spout" # Called MW in game
    SW_ENTRANCE = "SnowHorn Wastes - Entrance" # Exit to ThornTail Hollow the first time
    SH_SW_TRANSITION = "Transition to SnowHorn Wastes"


def create_and_connect_regions(world: SFAWorld) -> None:
    create_all_regions(world)
    connect_regions(world)

def create_all_regions(world: SFAWorld) -> None:
    sfa_region_list = []
    for region in SFARegion:
        sfa_region_list.append(Region(region.value, world.player, world.multiworld))
    print(f"Added regions: {sfa_region_list}")
    world.multiworld.regions += sfa_region_list

def connect_regions(world: SFAWorld) -> None:
    world_map = world.get_region(SFARegion.WORLDMAP.value)
    thorntail_hollow = world.get_region(SFARegion.SH.value)
    ice_mountain = world.get_region(SFARegion.IM.value)
    sw_water_spout = world.get_region(SFARegion.SW_WATERSPOUT.value)
    sw_entrance = world.get_region(SFARegion.SW_ENTRANCE.value)
    sh_sw_transition = world.get_region(SFARegion.SH_SW_TRANSITION.value)

    world_map.connect(thorntail_hollow, "Fly to Planet")
    thorntail_hollow.connect(ice_mountain, "WarpStone to Ice Mountain", lambda state: can_explode_bomb_plant(state, world.player) and state.has("Rock Candy", world.player))
    # ice_mountain.connect(sw_water_spout, "Ice Mountain to SnowHorn Wastes", lambda state: state.has("Tricky", world.player))
    # Temp solution to generate roots early
    ice_mountain.connect(sw_water_spout, "Race down to SnowHorn Wastes", lambda state: state.has_all_counts({"Tricky": 1, "Alpine Root": 2}, world.player))
    sw_water_spout.connect(sw_entrance, "SW - Water Spout to Entrance", lambda state: state.has("Alpine Root", world.player, 2))
    sw_entrance.connect(sh_sw_transition, "Transition to SnowHorn Wastes", lambda state: state.has_all(["Scarab Bag (Progressive)", "Tricky"], world.player))

