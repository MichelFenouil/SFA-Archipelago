from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from BaseClasses import Region

from . import macros as mc

if TYPE_CHECKING:
    from .world import SFAWorld


class SFARegion(Enum):
    """Region names for Star Fox Adventures."""

    WORLDMAP = "World Map"
    TH = "ThornTail Hollow"  # Originally SwapStone Hollow in game
    IM = "Ice Mountain"
    SW_WATERSPOUT = "SnowHorn Wastes - Water Spout"  # Called MW in game
    SW_ENTRANCE = "SnowHorn Wastes - Entrance"  # Exit to ThornTail Hollow the first time
    SW_GATE = "SnowHorn Wastes - Behind Gate"
    TH_WELL = "ThornTail Hollow - Well"
    TH_WELL_BOTTOM = "ThornTail Hollow - Dark Well Bottom"
    LFV = "LightFoot Village"
    MMP = "Moon Mountain Pass"


def create_and_connect_regions(world: SFAWorld) -> None:
    """Generate all regions for AP world."""
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: SFAWorld) -> None:
    """Create regions for AP world."""
    sfa_region_list = [Region(region.value, world.player, world.multiworld) for region in SFARegion]
    print(f"Added regions: {sfa_region_list}")  # noqa: T201
    world.multiworld.regions += sfa_region_list


def connect_regions(world: SFAWorld) -> None:
    """Create entrances for AP world."""
    world_map = world.get_region(SFARegion.WORLDMAP.value)
    thorntail_hollow = world.get_region(SFARegion.TH.value)
    ice_mountain = world.get_region(SFARegion.IM.value)
    sw_water_spout = world.get_region(SFARegion.SW_WATERSPOUT.value)
    sw_entrance = world.get_region(SFARegion.SW_ENTRANCE.value)
    sh_well = world.get_region(SFARegion.TH_WELL.value)
    sh_well_bottom = world.get_region(SFARegion.TH_WELL_BOTTOM.value)
    sw_gate = world.get_region(SFARegion.SW_GATE.value)
    lightfoot_village = world.get_region(SFARegion.LFV.value)
    moon_mountain_pass = world.get_region(SFARegion.MMP.value)

    world_map.connect(thorntail_hollow, "Fly to Planet")
    thorntail_hollow.connect(
        ice_mountain,
        "WarpStone to Ice Mountain",
        lambda state: state.has("Rock Candy", world.player),
    )
    # Temp solution to generate roots early
    ice_mountain.connect(
        sw_water_spout,
        "Race down to SnowHorn Wastes",
        lambda state: state.has_all_counts({"Tricky": 1}, world.player),
    )
    # Open SnowHorn Wastes to prevent locking SW
    sw_water_spout.connect(
        sw_entrance,
        "SW - Water Spout to Entrance",
        lambda state: True,
    )
    thorntail_hollow.connect(
        sw_entrance,
        "Access to SnowHorn Wastes",
        lambda state: state.has_all(["Tricky", "EVENT - Opened SnowHorn Wastes"], world.player),
    )
    thorntail_hollow.connect(sh_well, "Tunnel to Well", lambda state: state.has("Tricky", world.player))
    sh_well.connect(
        sh_well_bottom,
        "Descend to Well Bottom",
        lambda state: mc.has_staff_booster(state, world.player)
        and mc.can_explode_bomb_plant(state, world.player)
        and state.has("Firefly Lantern", world.player),
    )
    sw_entrance.connect(sw_gate, "Pass SnowHorn Gate", lambda state: state.has("Gate Key", world.player))
    thorntail_hollow.connect(
        lightfoot_village, "Access to LightFoot Village", lambda state: state.has("Staff", world.player)
    )
    thorntail_hollow.connect(
        moon_mountain_pass,
        "Entrance to Moon Mountain Pass",
        lambda state: mc.can_explode_bomb_plant(state, world.player),
    )
