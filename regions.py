from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from BaseClasses import Region
from rule_builder.rules import Has, HasAll, HasAllCounts, True_

from .macros import CanBuy, CanExplodeBombPlant, CanGoDarkRoom, CanGrowMoonSeed

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
    MMP_SHRINE = "Moon Mountain Pass - Krazoa Shrine"
    DIM_ENTRANCE = "DarkIce Mines - Entrance"
    DIM_FORT = "DarkIce Mines - SharpClaw Fort"
    DIM_BOTTOM = "DarkIce Mines - Bottom"
    VFP = "Volcano Force Point"
    VFP_PAST_BRIDGE = "Volcano Force Point - Past Bridge"
    VFP_WARP_ROOM = "Volcano Force Point - Warp Room"
    KP_ENTRANCE = "Krazoa Palace - Entrance"  # Only accessed on first warp (Spirit 2)
    KP_MAIN = "Krazoa Palace - Main Area"  # Every other Spirit warps directly to main room
    CC_TRANSITION = "Cape Claw Transition"
    CC_OPEN = "Cape Claw Open Area"
    CRF_LANDING = "CloudRunner Fortress - Landing Pad"
    CRF_MAIN = "CloudRunner Fortress - Central Area"
    CRF_POWERED = "CloudRunner Fortress - With Power"


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
    mmp_shrine = world.get_region(SFARegion.MMP_SHRINE.value)
    dim_entrance = world.get_region(SFARegion.DIM_ENTRANCE.value)
    dim_fort = world.get_region(SFARegion.DIM_FORT.value)
    dim_bottom = world.get_region(SFARegion.DIM_BOTTOM.value)
    vfp = world.get_region(SFARegion.VFP.value)
    vfp_past_bridge = world.get_region(SFARegion.VFP_PAST_BRIDGE.value)
    vfp_warp_room = world.get_region(SFARegion.VFP_WARP_ROOM.value)
    krazoa_palace_entrance = world.get_region(SFARegion.KP_ENTRANCE.value)
    krazoa_palace_main = world.get_region(SFARegion.KP_MAIN.value)
    cc_transition = world.get_region(SFARegion.CC_TRANSITION.value)
    cc_open = world.get_region(SFARegion.CC_OPEN.value)
    cloudrunner_fortress_landing = world.get_region(SFARegion.CRF_LANDING.value)
    cloudrunner_fortress_main = world.get_region(SFARegion.CRF_MAIN.value)
    cloudrunner_fortress_powered = world.get_region(SFARegion.CRF_POWERED.value)

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
        Has("Staff Booster") & CanExplodeBombPlant() & CanGoDarkRoom(),
    )
    sw_entrance.connect(sw_gate, "Pass SnowHorn Gate", Has("Gate Key"))
    thorntail_hollow.connect(lightfoot_village, "Access to LightFoot Village", Has("Staff"))
    thorntail_hollow.connect(
        moon_mountain_pass,
        "Entrance to Moon Mountain Pass",
        CanExplodeBombPlant(),
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
        HasAll("Dinosaur Horn", "Staff Booster"),
    )
    moon_mountain_pass.connect(vfp, "Access Volcano Force Point", Has("Moon Pass Key"))
    moon_mountain_pass.connect(
        mmp_meteorite, "Access Meteorite Area", Has("Moon Pass Key") & CanGrowMoonSeed() & CanExplodeBombPlant()
    )
    mmp_meteorite.connect(
        mmp_shrine, "Access behind Meteorite to Krazoa Shrine", Has("Tricky (Progressive)", 2) & Has("Freeze Blast")
    )
    vfp.connect(vfp_past_bridge, "Cross VFP Bridge", Has("Fire SpellStone 1"))
    vfp_past_bridge.connect(
        vfp_warp_room,
        "Access VFP Past Puzzles",
        Has("Fire Blaster") & Has("Tricky (Progressive)", 2) & Has("Freeze Blast"),
    )
    thorntail_hollow.connect(
        krazoa_palace_entrance,
        "Warp to Krazoa Palace with Spirit 2",
        Has("Rock Candy") & Has("Krazoa Spirit 2"),
    )
    krazoa_palace_entrance.connect(
        krazoa_palace_main,
        "Enter Krazoa Palace Main Area",
        Has("Fire Blaster") & CanGoDarkRoom(),
    )
    # thorntail_hollow.connect(
    #     krazoa_palace_main,
    #     "Warp to Krazoa Palace Main Room",
    #     Has("Rock Candy") # & Has any other spirits
    # )
    lightfoot_village.connect(cc_transition, "Access Cape Claw Transition", CanBuy(60))
    cc_transition.connect(cc_open, "Access Cape Claw Open Area", True_())
    world_map.connect(cloudrunner_fortress_landing, "Fly to CloudRunner Fortress", Has("CloudRunner Fortress Access"))
    cloudrunner_fortress_landing.connect(
        cloudrunner_fortress_main, "Enter CloudRunner Fortress Main Area", Has("Fire Blaster")
    )
    cloudrunner_fortress_main.connect(
        cloudrunner_fortress_powered,
        "Access CloudRunner Fortress Powered Area",
        HasAll("CRF Power Key", "Red Crystal", "Green Crystal", "Blue Crystal", "SharpClaw Disguise"),
    )
