from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState
from worlds.generic.Rules import set_rule, add_rule
from .locations import LOCATION_SHOP, LOCATION_DIG_SPOT
from .macros import *

if TYPE_CHECKING:
    from .world import SFAWorld

def set_all_rules(world: SFAWorld) -> None:
    set_all_location_rules(world)
    set_completion_condition(world)

def set_all_location_rules(world: SFAWorld) -> None:
    """
    Define the logic rules for locations in The Wind Waker.
    Rules are only set for locations if they are present in the world.

    :param world: The Wind Waker game world.
    """
    def set_rule_if_exists(location_name: str, rule: Callable[[CollectionState], bool]) -> None:
        if location_name in world.progress_locations:
            set_rule(world.get_location(location_name), rule)

    # Shop Items
    for shop_name, shop_data in LOCATION_SHOP.items():
        set_rule_if_exists(shop_name, lambda state: can_buy(state, world.player, shop_data.cost))

    # Digspot global
    for dig_name, dig_data in LOCATION_DIG_SPOT.items():
        set_rule_if_exists(dig_name, lambda state: state.has("Tricky", world.player))

    # ThornTail Hollow
    set_rule_if_exists("Fireblaster Upgrade", lambda state: True)
    set_rule_if_exists("SH Pillar Fuel Cell Left", lambda state: True)
    set_rule_if_exists("SH Pillar Fuel Cell Right", lambda state: True)
    set_rule_if_exists("SH Queen Cave Fuel Cell", lambda state: has_blaster(state, world.player))
    set_rule_if_exists("SH Beside Warpstone Left", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH Beside Warpstone Right", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH Waterfall Cave 1", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH Waterfall Cave 2", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH Waterfall Cave 3", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH Waterfall Cave Back", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH South Cave 1", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH South Cave 2", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("SH South Cave 3", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists( "SH Booster Ledge Left", lambda state: has_staff_booster(state, world.player))
    set_rule_if_exists( "SH Booster Ledge Right", lambda state: has_staff_booster(state, world.player))

    # Ice Mountain
    set_rule_if_exists("IM Cheat Well Cave", lambda state: can_explode_bomb_plant(state, world.player))
    set_rule_if_exists("IM Race Cave Front", lambda state: has_blaster(state, world.player))
    set_rule_if_exists("IM Race Cave Back", lambda state: has_blaster(state, world.player))

    # SnowHorn Wastes
    set_rule_if_exists("SW Magic Upgrade", lambda state: state.has("Tricky", world.player))
    set_rule_if_exists("SW Ice Block Left", lambda state: state.has("Alpine Root", world.player, 2))
    set_rule_if_exists("SW Ice Block Right", lambda state: state.has("Alpine Root", world.player, 2))
    set_rule_if_exists("SW Cold Water Left", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("SW Cold Water Right", lambda state: state.has("Staff", world.player))
    set_rule_if_exists("SW Dig Cave Left", lambda state: state.has("Tricky", world.player))
    set_rule_if_exists("SW Transition Booster Left", lambda state: has_blaster(state, world.player) and has_staff_booster(state, world.player))


    


def set_completion_condition(world:  SFAWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(["Staff", "Fire Blaster", "Staff Booster", "Scarab Bag (Progressive)"], world.player)