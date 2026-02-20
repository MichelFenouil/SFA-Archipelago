from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from BaseClasses import CollectionState

from worlds.generic.Rules import set_rule

from . import macros as mc
from .locations import LOCATION_DIG_SPOT, LOCATION_SHOP
from .regions import SFARegion

if TYPE_CHECKING:
    from .world import SFAWorld


def set_all_rules(world: SFAWorld) -> None:
    """Generate rules for AP world."""
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_location_rules(world: SFAWorld) -> None:
    """Create all location rules for AP world."""

    def set_rule_if_exists(location_name: str, rule: Callable[[CollectionState], bool]) -> None:
        if location_name in world.progress_locations:
            set_rule(world.get_location(location_name), rule)

    # Shop Items
    for shop_name, shop_data in LOCATION_SHOP.items():
        set_rule_if_exists(shop_name, lambda state, cost=shop_data.cost: mc.can_buy(state, world.player, cost))

    # Digspot global
    for dig_name in LOCATION_DIG_SPOT:
        set_rule_if_exists(dig_name, lambda state: state.has("Tricky (Progressive)", world.player))

    # ThornTail Hollow
    set_rule_if_exists("Fireblaster Upgrade", lambda state: True)
    set_rule_if_exists("TH Pillar Fuel Cell Left", lambda state: True)
    set_rule_if_exists("TH Pillar Fuel Cell Right", lambda state: True)
    set_rule_if_exists("TH Queen Cave Fuel Cell", lambda state: True)
    set_rule_if_exists(
        "TH Beside Warpstone Left",
        lambda state: mc.can_explode_bomb_plant(state, world.player),
    )
    set_rule_if_exists(
        "TH Beside Warpstone Right",
        lambda state: mc.can_explode_bomb_plant(state, world.player),
    )
    set_rule_if_exists("TH Waterfall Cave 1", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("TH Waterfall Cave 2", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("TH Waterfall Cave 3", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists(
        "TH Waterfall Cave Back",
        lambda state: mc.can_explode_bomb_plant(state, world.player),
    )
    set_rule_if_exists("TH South Cave 1", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("TH South Cave 2", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("TH South Cave 3", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("TH Shop Booster Ledge 1", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists("TH Shop Booster Ledge 2", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists(
        "TH Above Shop Magic Upgrade",
        lambda state: mc.has_staff_booster(state, world.player)
        and mc.has_blaster(state, world.player)
        and mc.can_explode_bomb_plant(state, world.player),
    )
    set_rule_if_exists("TH Queen Gave White GrubTubs", lambda state: state.has("White GrubTub", world.player, 6))

    # TH Well
    set_rule_if_exists("TH Well Booster Ledge 1", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists("TH Well Booster Ledge 2", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists("TH Dark Well Shroom 1", lambda state: True)
    set_rule_if_exists("TH Dark Well Shroom 2", lambda state: True)
    set_rule_if_exists("TH Dark Well Shroom 3", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("TH Dark Well Shroom 4", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists(
        "TH Dark Well Shroom 5",
        lambda state: mc.has_staff_booster(state, world.player) and mc.can_explode_bomb_plant(state, world.player),
    )
    set_rule_if_exists(
        "TH Dark Well Shroom 6",
        lambda state: mc.has_staff_booster(state, world.player) and mc.can_explode_bomb_plant(state, world.player),
    )
    set_rule_if_exists("Staff Booster Upgrade", lambda state: mc.can_explode_bomb_plant(state, world.player))

    # Ice Mountain
    set_rule_if_exists("IM Cheat Well Cave", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("IM Race Cave Front", lambda state: True)
    set_rule_if_exists("IM Race Cave Back", lambda state: True)

    # SnowHorn Wastes
    set_rule_if_exists("SW Magic Upgrade", lambda state: state.has("Tricky (Progressive)", world.player))
    set_rule_if_exists("SW Give Alpine Root 1", lambda state: state.has("Alpine Root", world.player, 1))
    set_rule_if_exists("SW Give Alpine Root 2", lambda state: state.has("Alpine Root", world.player, 2))
    set_rule_if_exists("SW Ice Block Left", lambda state: True)  # Requires 2 Alpine Roots without open SW
    set_rule_if_exists("SW Ice Block Right", lambda state: True)  # Requires 2 Alpine Roots without open SW
    set_rule_if_exists("SW Cold Water Left", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("SW Cold Water Right", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("SW Dig Cave Left", lambda state: state.has("Tricky (Progressive)", world.player))
    set_rule_if_exists(
        "SW Transition Booster Left",
        lambda state: mc.has_blaster(state, world.player) and mc.has_staff_booster(state, world.player),
    )
    set_rule_if_exists(
        "SW Transition Booster Right",
        lambda state: mc.has_blaster(state, world.player) and mc.has_staff_booster(state, world.player),
    )
    set_rule_if_exists("SW Rescue Gate Keeper", lambda state: True)
    set_rule_if_exists("SW Gate After Tree 1", lambda state: mc.has_blaster(state, world.player))
    set_rule_if_exists("SW Gate After Tree 2", lambda state: mc.has_blaster(state, world.player))
    set_rule_if_exists("SW Gate River Cheat Well", lambda state: True)
    set_rule_if_exists("SW Gate River Ledge 1", lambda state: True)
    set_rule_if_exists("SW Gate River Ledge 2", lambda state: mc.has_blaster(state, world.player))
    set_rule_if_exists("SW Gate River Ledge 3", lambda state: mc.has_blaster(state, world.player))

    # LightFoot Village
    set_rule_if_exists("TH Cape Claw Entrance 1", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("TH Cape Claw Entrance 2", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("LFV Entrance Booster Ledge 1", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists("LFV Entrance Booster Ledge 2", lambda state: mc.has_staff_booster(state, world.player))

    # Moon Mountain Pass
    set_rule_if_exists("MMP Windy Path In", lambda state: True)
    set_rule_if_exists("MMP Windy Path Out", lambda state: True)
    set_rule_if_exists("MMP Barrel Hill", lambda state: True)

    # DarkIce Mines
    set_rule_if_exists("DIM: Release SnowHorn", lambda state: state.has("Tricky (Progressive)", world.player))
    set_rule_if_exists("DIM: Find Injured SnowHorn", lambda state: state.has("Cog 1", world.player))
    set_rule_if_exists(
        "DIM: Feed Injured SnowHorn",
        lambda state: state.has_all_counts({"Cog 1": 1, "DIM Alpine Root": 2}, world.player),
    )
    set_rule_if_exists("DIM: Get Cog 2", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists("DIM: Get Cog 3", lambda state: mc.has_staff_booster(state, world.player))
    set_rule_if_exists(
        "DIM: Get Cog 4",
        lambda state: mc.has_staff_booster(state, world.player) and state.has("Tricky (Progressive)", world.player, 2),
    )
    set_rule_if_exists(
        "DIM: Dinosaur Horn",
        lambda state: mc.has_blaster(state, world.player)
        and state.has_all_counts({"Cog 2/3/4": 3, "Tricky (Progressive)": 2}, world.player),
    )
    set_rule_if_exists("DIM: Get Silver Key", lambda state: mc.has_staff_booster(state, world.player) and mc.has_blaster(state, world.player))
    set_rule_if_exists(
        "DIM: Defeat Boss Galdon",
        lambda state: mc.has_blaster(state, world.player)
        and state.has_all_counts({"Cell Silver Key": 1, "Tricky (Progressive)": 2}, world.player),
    )
    set_rule_if_exists("DIM: Dig Alpine Root 1", lambda state: state.has("Tricky (Progressive)", world.player, 2))
    set_rule_if_exists(
        "DIM: Dig Alpine Root 2",
        lambda state: state.has_all_counts({"Cog 1": 1, "Tricky (Progressive)": 2}, world.player),
    )


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

    world_map.connect(thorntail_hollow, "Fly to Planet", lambda state: state.has("Dinosaur Planet", world.player))
    thorntail_hollow.connect(
        ice_mountain,
        "WarpStone to Ice Mountain",
        lambda state: state.has("Rock Candy", world.player),
    )
    ice_mountain.connect(
        sw_water_spout,
        "Race down to SnowHorn Wastes",
        lambda state: state.has_all_counts({"Tricky (Progressive)": 1}, world.player),
    )
    # Open SnowHorn Wastes to prevent locking SW
    sw_water_spout.connect(
        sw_entrance,
        "SW - Water Spout to Entrance",
        lambda state: True,
    )
    thorntail_hollow.connect(sh_well, "Tunnel to Well", lambda state: state.has("Tricky (Progressive)", world.player))
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

    world_map.connect(dim_entrance, "Fly to DarkIce Mines", lambda state: state.has("DarkIce Mines", world.player))
    # 2 Roots to open gate and Flame command to access cog area or the cannon
    dim_entrance.connect(
        dim_fort,
        "Enter SharpClaw Fort",
        lambda state: state.has_all_counts({"Cog 1": 1, "DIM Alpine Root": 2, "Tricky (Progressive)": 2}, world.player),
    )
    dim_fort.connect(
        dim_bottom,
        "Descend to DarkIce Mines Bottom",
        lambda state: mc.has_staff_booster(state, world.player) and state.has("Dinosaur Horn", world.player),
    )


def set_completion_condition(world: SFAWorld) -> None:
    """Create victory condition."""
    # Defeat Boss Galdon
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
