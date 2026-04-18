from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from BaseClasses import Region
from rule_builder.rules import Has, HasAllCounts, True_
from .macros import can_explode_bomb_plant, has_staff_booster, has_blaster, can_grow_moon_seed

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
    MMP_METEORITE = "Moon Mountain Pass - Meteorite Area"
    DIM_ENTRANCE = "DarkIce Mines - Entrance"
    DIM_FORT = "DarkIce Mines - SharpClaw Fort"
    DIM_BOTTOM = "DarkIce Mines - Bottom"
    VFP = "Volcano Force Point"
    VFP_PAST_BRIDGE = "Volcano Force Point - Past Bridge"
    VFP_PAST_PUZZLE = "Volcano Force Point - Past Puzzle"



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
    mmp_meteorite = world.get_region(SFARegion.MMP_METEORITE.value)
    dim_entrance = world.get_region(SFARegion.DIM_ENTRANCE.value)
    dim_fort = world.get_region(SFARegion.DIM_FORT.value)
    dim_bottom = world.get_region(SFARegion.DIM_BOTTOM.value)
    vfp = world.get_region(SFARegion.VFP.value)
    vfp_past_bridge = world.get_region(SFARegion.VFP_PAST_BRIDGE.value)
    vfp_past_puzzle = world.get_region(SFARegion.VFP_PAST_PUZZLE.value)

    world_map.connect(thorntail_hollow, "Fly to Planet", Has("Dinosaur Planet Access"))
    thorntail_hollow.connect(
        ice_mountain,
        "WarpStone to Ice Mountain",
        Has("Rock Candy"),
    )
    ice_mountain.connect(
        sw_water_spout,
        "Race down to SnowHorn Wastes",
        Has("Tricky (Progressive)"),
    )
    # Open SnowHorn Wastes to prevent locking SW
    sw_water_spout.connect(
        sw_entrance,
        "SW - Water Spout to Entrance",
        True_(),
    )
    thorntail_hollow.connect(sh_well, "Tunnel to Well", Has("Tricky (Progressive)"))
    sh_well.connect(
        sh_well_bottom,
        "Descend to Well Bottom",
        has_staff_booster & can_explode_bomb_plant & Has("FireFly Lantern"),
    )
    sw_entrance.connect(sw_gate, "Pass SnowHorn Gate", Has("Gate Key"))
    thorntail_hollow.connect(lightfoot_village, "Access to LightFoot Village", Has("Staff"))
    thorntail_hollow.connect(
        moon_mountain_pass,
        "Entrance to Moon Mountain Pass",
        can_explode_bomb_plant,
    )

    world_map.connect(dim_entrance, "Fly to DarkIce Mines", Has("DarkIce Mines Access"))
    # 2 Roots to open gate and Flame command to access cog area or the cannon
    dim_entrance.connect(
        dim_fort,
        "Enter SharpClaw Fort",
        HasAllCounts({"Entrance Bridge Cog": 1, "DIM Alpine Root": 2, "Tricky (Progressive)": 2}),
    )
    dim_fort.connect(
        dim_bottom,
        "Descend to DarkIce Mines Bottom",
        has_staff_booster & Has("Dinosaur Horn"),
    )
    moon_mountain_pass.connect(vfp, "Access Volcano Force Point", Has("Moon Pass Key"))
    moon_mountain_pass.connect(mmp_meteorite, "Access Meteorite Area", Has("Moon Pass Key") & can_grow_moon_seed & can_explode_bomb_plant)
    vfp.connect(vfp_past_bridge, "Cross VFP Bridge", Has("Fire SpellStone 1"))
    vfp_past_bridge.connect(vfp_past_puzzle, "Access VFP Past Puzzle", has_blaster & Has("Tricky (Progressive)", 2) & Has("Freeze Blast"))