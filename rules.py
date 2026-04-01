from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has, HasAllCounts, True_

from . import macros as mc
from .regions import SFARegion

if TYPE_CHECKING:
    from .world import SFAWorld


def set_all_rules(world: SFAWorld) -> None:
    """Generate rules for AP world."""
    set_completion_condition(world)


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
    dim_entrance = world.get_region(SFARegion.DIM_ENTRANCE.value)
    dim_fort = world.get_region(SFARegion.DIM_FORT.value)
    dim_bottom = world.get_region(SFARegion.DIM_BOTTOM.value)

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
        mc.has_staff_booster & mc.can_explode_bomb_plant & Has("FireFly Lantern"),
    )
    sw_entrance.connect(sw_gate, "Pass SnowHorn Gate", Has("Gate Key"))
    thorntail_hollow.connect(lightfoot_village, "Access to LightFoot Village", Has("Staff"))
    thorntail_hollow.connect(
        moon_mountain_pass,
        "Entrance to Moon Mountain Pass",
        mc.can_explode_bomb_plant,
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
        mc.has_staff_booster & Has("Dinosaur Horn"),
    )


def set_completion_condition(world: SFAWorld) -> None:
    """Create victory condition."""
    # Defeat Boss Galdon
    world.set_completion_rule(Has("Victory"))
