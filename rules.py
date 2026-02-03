from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from BaseClasses import CollectionState

from worlds.generic.Rules import set_rule

from . import macros as mc
from .locations import LOCATION_DIG_SPOT, LOCATION_SHOP

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
        set_rule_if_exists(dig_name, lambda state: state.has("Tricky", world.player))

    # ThornTail Hollow
    set_rule_if_exists("Fireblaster Upgrade", lambda state: True)
    set_rule_if_exists("TH Pillar Fuel Cell Left", lambda state: True)
    set_rule_if_exists("TH Pillar Fuel Cell Right", lambda state: True)
    set_rule_if_exists("TH Queen Cave Fuel Cell", lambda state: mc.has_blaster(state, world.player))
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

    # Ice Mountain
    set_rule_if_exists("IM Cheat Well Cave", lambda state: mc.can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("IM Race Cave Front", lambda state: mc.has_blaster(state, world.player))
    set_rule_if_exists("IM Race Cave Back", lambda state: mc.has_blaster(state, world.player))

    # SnowHorn Wastes
    set_rule_if_exists("SW Magic Upgrade", lambda state: state.has("Tricky", world.player))
    set_rule_if_exists("SW Give Alpine Root 1", lambda state: state.has("Alpine Root", world.player, 1))
    set_rule_if_exists("SW Give Alpine Root 2", lambda state: state.has("Alpine Root", world.player, 2))
    set_rule_if_exists("SW Ice Block Left", lambda state: state.has("Alpine Root", world.player, 2))
    set_rule_if_exists("SW Ice Block Right", lambda state: state.has("Alpine Root", world.player, 2))
    set_rule_if_exists("SW Cold Water Left", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("SW Cold Water Right", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("SW Dig Cave Left", lambda state: state.has("Tricky", world.player))
    set_rule_if_exists(
        "SW Transition Booster Left",
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


def set_completion_condition(world: SFAWorld) -> None:
    """Create victory condition."""
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(
        ["Staff", "Fire Blaster", "Staff Booster", "Scarab Bag (Progressive)"],
        world.player,
    )
