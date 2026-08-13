import asyncio
from typing import TYPE_CHECKING

import dolphin_memory_engine as dme
from CommonClient import logger

from .addresses import *  # noqa: F403
from .bit_helper import GameBit, clear_bit, extract_bitflag_list, set_bit, set_flag_bit, set_value_bytes, swap_endian
from .game_flags import (
    CC_ACT_GAMEBIT,
    CC_OBJGROUP_VALUE,
    CRF_ENTRANCE_RACE,
    CRF_OPEN_BACK_PATH,
    CRF_OPEN_POST_BOSS,
    CRF_PRISON_WIND,
    CRF_QUEEN_BROKEN_PILLAR,
    CRF_QUEEN_CHILDREN_CHECK,
    DIM_OBJGROUP_VALUE,
    DIM_OPEN_BIKE,
    DIM_OPEN_BLIZZARD,
    KP_ACT_GAMEBIT,
    KP_OBJGROUP_VALUE,
    KRAZOA_SPIRIT_1,
    KRAZOA_STATUE_2,
    LFV_ACT_GAMEBIT,
    LFV_GATE,
    MAGIC_CAVE_ACT_GAMEBIT,
    OFP_ACT_GAMEBIT,
)
from .game_memory.code_edit import trigger_objgroup_load
from .game_memory.hook_handlers import PlayerCoordZone
from .game_memory.loaded_objects import get_all_loaded_objects, search_objects
from .game_memory.memory_struct import ObjState
from .item_hooks import (
    lfv_disable_circle_platform,
    lfv_disable_square_platform,
    lfv_disable_triangle_platform,
    lfv_enable_circle_platform,
    lfv_enable_square_platform,
    lfv_enable_triangle_platform,
)
from .items import ITEM_INVENTORY, ITEM_PLANET, ITEM_STAFF, SFAItemData, SFAProgressiveItemData, give_item_in_game
from .locations import (
    LOCATION_ANY,
    LOCATION_SHOP,
    LOCATION_TABLE,
    LOCATION_UPGRADE,
    SFALocationTags,
    SFAShopLocationData,
    SFAUpgradeLocationData,
)

if TYPE_CHECKING:
    from .SFAClient import SFAContext


async def _sync_current_map(ctx: "SFAContext", entered_map: int, _from_map: int) -> None:
    await ctx.send_msgs(
        [
            {
                "cmd": "Set",
                "key": f"SFA_current_map_{ctx.team}_{ctx.slot}",
                "default": {},
                "operations": [{"operation": "replace", "value": entered_map}],
            }
        ]
    )


def _set_special_location_state(
    ctx: "SFAContext",
    location: SFAUpgradeLocationData | SFAShopLocationData,
    entered_map: int,
    from_map: int,
    expected_map: int,
) -> None:
    if entered_map == expected_map:
        location.set_bit(location.id in ctx.checked_locations or location.id not in ctx.server_locations)
    if from_map == expected_map:
        location.set_bit(SFALocationTags.MAP in location.tags or location.linked_item in ctx.received_items_id)


async def _handle_magic_cave_transition(ctx: "SFAContext", entered_map: int, from_map: int) -> None:
    if entered_map != MAGIC_CAVE_ID and from_map != MAGIC_CAVE_ID:
        return
    mc_act = MAGIC_CAVE_ACT_GAMEBIT.get_value()
    mc_flags_bytes = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
    mc_flags = extract_bitflag_list(swap_endian(mc_flags_bytes))
    for loc_data in LOCATION_UPGRADE.values():
        if mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags:
            _set_special_location_state(ctx, loc_data, entered_map, from_map, MAGIC_CAVE_ID)


async def _handle_shop_transition(ctx: "SFAContext", entered_map: int, from_map: int) -> None:
    if entered_map != SHOP_ID and from_map != SHOP_ID:
        return

    if entered_map == SHOP_ID and not ctx.shop_visited:
        await ctx.send_msgs(
            [
                {
                    "cmd": "LocationScouts",
                    "locations": [loc.id for loc in LOCATION_SHOP.values() if loc.id in ctx.server_locations],
                    "create_as_hint": 2,
                }
            ]
        )
        ctx.shop_visited = True

    for loc_data in LOCATION_SHOP.values():
        _set_special_location_state(ctx, loc_data, entered_map, from_map, SHOP_ID)


def lfv_platform_on_entering(ctx) -> None:  # noqa: D103
    if SFAItemData.get_by_name("Triangle Block Platforms").id not in ctx.received_items_id:
        lfv_disable_triangle_platform()
    if SFAItemData.get_by_name("Square Block Platforms").id not in ctx.received_items_id:
        lfv_disable_square_platform()
    if SFAItemData.get_by_name("Circle Block Platforms").id not in ctx.received_items_id:
        lfv_disable_circle_platform()


async def _handle_map_entry_state(ctx: "SFAContext", entered_map: int, from_map: int) -> None:
    if entered_map == THORNTAIL_HOLLOW_ID:
        set_value_bytes(T2_ADDRESS, THORNTAIL_HOLLOW_ACT_OFFSET, 0x2, value_size=4)

    if entered_map == MOON_MOUNTAIN_PASS_ID:
        set_value_bytes(T1_ADDRESS, MOON_MOUNTAIN_PASS_ACT_OFFSET, 0x2, value_size=4)

    if entered_map == CLOUDRUNNER_FORTRESS_ID:
        set_value_bytes(CRF_OBJGROUP_ADDRESS, 16, 1)
        CRF_ENTRANCE_RACE.set_bit(True)

    if entered_map == WORLD_MAP_ID:
        SFAItemData.get_by_name("Fire Blaster").set_value(False)
        for planet in ITEM_PLANET.values():
            planet.set_value(planet.id in ctx.received_items_id)
        for flag in CRF_OPEN_POST_BOSS:
            flag.set_bit(flag.state)
    elif from_map == WORLD_MAP_ID:
        item = SFAItemData.get_by_name("Fire Blaster")
        item.set_value(item.id in ctx.received_items_id)

    if entered_map == KRAZOA_PALACE_ID:
        KRAZOA_SPIRIT_1.set_bit(True)

    if entered_map == COMBAT_SHRINE_ID:
        LOCATION_ANY["MMP: Test of Combat"].set_bit(False)
    if entered_map == FEAR_SHRINE_ID:
        LOCATION_ANY["LFV: Test of Fear"].set_bit(False)

    if entered_map == CAPE_CLAW_ID:
        CC_ACT_GAMEBIT.set_value(2)

    if entered_map == OCEAN_FORCE_POINT_BEACH_ID:
        OFP_ACT_GAMEBIT.set_value(1)

    if entered_map == LIGHTFOOT_VILLAGE_ID:
        LFV_ACT_GAMEBIT.set_value(6)
        lfv_platform_on_entering(ctx)


async def _handle_krazoa_palace(ctx: "SFAContext", entered_map: int, from_map: int) -> None:
    if entered_map != KRAZOA_PALACE_ID:
        return
    await asyncio.sleep(1)  # Wait for the map to fully load so the flag is set correctly
    act_nb = GameBit(0x02DA, T1_ADDRESS, bit_size=4).get_value()
    if act_nb == 0x1:
        KRAZOA_SPIRIT_1.set_bit(True)


async def _handle_dim_zone_transition(ctx: "SFAContext", entered_zone: int, from_zone: int) -> None:
    logger.debug(f"Entering dim zone {entered_zone:x}")
    # 0000 0000 0100 0100 1000 0011 1000 0000
    # 0000 0000 0101 0100 1000 0011 1000 0000
    if entered_zone == DIM_COGS_ZONE_VALUE or entered_zone == DIM_COGS_ZONE_VALUE2:
        item = ITEM_INVENTORY.get("SharpClaw Fort Bridge Cogs")
        assert isinstance(item, SFAProgressiveItemData)
        count = ctx.received_items_id.count(item.id)
        for index, progress in enumerate(item.progressive_data):
            set_flag_bit(progress.address, progress.offset, count > index)
            set_flag_bit(progress.address, progress.offset - 1, False)
    elif (
        entered_zone - from_zone == DIM_BLIZZARD_ZONE_TRANSITION
        or from_zone - entered_zone == DIM_BLIZZARD_ZONE_TRANSITION
    ):
        logger.debug("Entering Blizzard zone")
        for flag in DIM_OPEN_BLIZZARD:
            flag.set_bit(False)
    elif from_zone - entered_zone == DIM_BIKE_ZONE_TRANSITION:
        logger.debug("Bike zone transition")
        for flag in DIM_OPEN_BIKE:
            flag.set_bit(False)
    else:
        item = ITEM_INVENTORY.get("SharpClaw Fort Bridge Cogs")
        locations = [
            LOCATION_ANY["DIM: Enemy Gate Cog Chest"],
            LOCATION_ANY["DIM: Hut Cog Chest"],
            LOCATION_ANY["DIM: Ice Cog Chest"],
        ]
        assert isinstance(item, SFAProgressiveItemData)
        for progress in item.progressive_data:
            progress.set_bit(True)
        for location in locations:
            location.set_bit(location.id in ctx.checked_locations)


async def _handle_test_of_combat_warppad(ctx: "SFAContext", zone_name: str) -> None:
    object_list = get_all_loaded_objects()
    warppad = search_objects(object_list, 0xEC)
    if warppad is None:
        return
    flag_e_offset = ObjState.flagE.offset
    if LOCATION_ANY["MMP: Test of Combat"].id in ctx.checked_locations:
        dme.write_bytes(warppad.state_ptr + flag_e_offset, bytes.fromhex("20"))
    else:
        dme.write_bytes(warppad.state_ptr + flag_e_offset, bytes.fromhex("01"))


async def _handle_test_of_fear_warppad(ctx: "SFAContext", zone_name: str) -> None:
    # TODO: Improve get_objects to find all loaded objects
    warppad = None
    tries = 0
    while True:
        object_list = get_all_loaded_objects()
        warppad = search_objects(object_list, 0xEC)
        if warppad is not None:
            break
        if tries >= 10:
            return
        tries += 1
        await asyncio.sleep(0.5)
    flag_e_offset = ObjState.flagE.offset
    if LOCATION_ANY["LFV: Test of Fear"].id in ctx.checked_locations:
        dme.write_bytes(warppad.state_ptr + flag_e_offset, bytes.fromhex("20"))
    else:
        dme.write_bytes(warppad.state_ptr + flag_e_offset, bytes.fromhex("01"))


async def _handle_fire_spellstone_door(ctx: "SFAContext", zone_name: str) -> None:
    ITEM_INVENTORY["Fire SpellStone 1"].set_value(True)


async def _give_spirit_near_warpstone(ctx: "SFAContext", zone_name: str) -> None:
    krazoa_spirit_2 = SFAItemData.get_by_name("Krazoa Spirit 2")
    krazoa_spirit_3 = SFAItemData.get_by_name("Krazoa Spirit 3")

    if krazoa_spirit_2.id in ctx.received_items_id:
        if LOCATION_TABLE["KP: Dark Room BafomDad"].id not in ctx.checked_locations:
            krazoa_spirit_2.set_value(True)
            krazoa_spirit_3.set_value(False)
            return

        if LOCATION_ANY["KP: Release Spirit 2"].id not in ctx.checked_locations:
            krazoa_spirit_2.set_value(True)

    if krazoa_spirit_3.id in ctx.received_items_id:
        krazoa_spirit_3.set_value(True)


async def _handle_spirit_2(ctx: "SFAContext", zone_name: str) -> None:
    act = 2
    spirit = SFAItemData.get_by_name("Krazoa Spirit 2")
    if spirit.id in ctx.received_items_id:
        spirit.set_value(True)
        KP_ACT_GAMEBIT.set_value(act)
        KRAZOA_STATUE_2.set_bit(True)
        trigger_objgroup_load(KRAZOA_PALACE_ID, act, KP_OBJGROUP_VALUE.get_value())


async def _handle_spirit_3(ctx: "SFAContext", zone_name: str) -> None:
    act = 3
    spirit = SFAItemData.get_by_name("Krazoa Spirit 3")
    if spirit.id in ctx.received_items_id:
        spirit.set_value(True)
        KP_ACT_GAMEBIT.set_value(act)
        objgroup_value = KP_OBJGROUP_VALUE.get_value()
        trigger_objgroup_load(KRAZOA_PALACE_ID, act, objgroup_value)


async def _show_race_ring(ctx: "SFAContext", zone_name: str) -> None:
    if zone_name != "CRF_ENTRANCE_RACE_START" and zone_name != "CRF_ENTRANCE_RACE_LADDER":
        return
    # False on race start, True on ladder to leave zone
    CRF_ENTRANCE_RACE.set_bit(zone_name == "CRF_ENTRANCE_RACE_LADDER")


async def _turn_off_up_draft(ctx: "SFAContext", zone_name: str) -> None:
    # False = Up draft, True = Down draft
    CRF_PRISON_WIND.set_bit(True)
    give_item_in_game(ctx, ITEM_INVENTORY["CRF Power Key"])
    give_item_in_game(ctx, ITEM_STAFF["SharpClaw Disguise"])


async def _toggle_babies_quest(ctx: "SFAContext", zone_name: str) -> None:
    quest_condition = (
        SFAItemData.get_by_name("Fire Blaster").id in ctx.received_items_id
        and SFAItemData.get_by_name("Staff Booster").id in ctx.received_items_id
        and SFAItemData.get_by_name("CloudRunner Flute").id in ctx.received_items_id
        and CRF_QUEEN_BROKEN_PILLAR.get_bit()
    )
    CRF_QUEEN_CHILDREN_CHECK.set_bit(quest_condition)


async def _prevent_softlock_on_back_path(ctx: "SFAContext", zone_name: str) -> None:
    for flag in CRF_OPEN_BACK_PATH:
        flag.set_bit(flag.state)


async def _close_back_path(ctx: "SFAContext", zone_name: str) -> None:
    if SFAItemData.get_by_name("SharpClaw Disguise").id not in ctx.received_items_id:
        CRF_OPEN_BACK_PATH[0].set_bit(False)


async def _cc_act1_on(ctx: "SFAContext", zone_name: str) -> None:
    act = 1
    CC_ACT_GAMEBIT.set_value(act)
    objgroup_value = CC_OBJGROUP_VALUE.get_value()
    trigger_objgroup_load(CAPE_CLAW_ID, act, objgroup_value)


async def _cc_act1_off(ctx: "SFAContext", zone_name: str) -> None:
    act = 2
    CC_ACT_GAMEBIT.set_value(act)
    objgroup_value = CC_OBJGROUP_VALUE.get_value()
    trigger_objgroup_load(CAPE_CLAW_ID, act, objgroup_value)


async def _handle_lfv_gate(ctx: "SFAContext", zone_name: str) -> None:
    if (
        ctx.options["lightfoot_entrance"] == "always_open"
        or SFAItemData.get_by_name("LightFoot Village Gate").id in ctx.received_items_id
    ):
        LFV_GATE.set_bit(True)
    elif ctx.options["lightfoot_entrance"] == "ap_item":
        LFV_GATE.set_bit(False)


async def _handle_circle_platform(ctx: "SFAContext", zone_name: str) -> None:
    if SFAItemData.get_by_name("Circle Block Platforms").id not in ctx.received_items_id:
        lfv_disable_circle_platform()
    else:
        lfv_enable_circle_platform(None)


async def _handle_square_platform(ctx: "SFAContext", zone_name: str) -> None:
    if SFAItemData.get_by_name("Square Block Platforms").id not in ctx.received_items_id:
        lfv_disable_square_platform()
    else:
        lfv_enable_square_platform(None)


async def _handle_triangle_platform(ctx: "SFAContext", zone_name: str) -> None:
    if SFAItemData.get_by_name("Triangle Block Platforms").id not in ctx.received_items_id:
        lfv_disable_triangle_platform()
    else:
        lfv_enable_triangle_platform(None)


async def _handle_dim_shackle_key(ctx: "SFAContext", zone_name: str) -> None:
    location = LOCATION_ANY["DIM: Shackle Key Chest"]
    location.set_bit(location.id in ctx.checked_locations)
    value = DIM_OBJGROUP_VALUE.get_value()
    # Clear bit then set it again to refresh Chest
    value = clear_bit(value, 2)
    DIM_OBJGROUP_VALUE.set_value(value)
    trigger_objgroup_load(DARKICE_TOP_ID, 1, value)
    await asyncio.sleep(0.1)
    value = set_bit(value, 2)
    DIM_OBJGROUP_VALUE.set_value(value)
    trigger_objgroup_load(DARKICE_TOP_ID, 1, value)


async def _leave_dim_shackle_key(ctx: "SFAContext", zone_name: str) -> None:
    item = SFAItemData.get_by_name("DIM Shackle Key")
    item.set_value(item.id in ctx.received_items_id)


def register_default_special_hooks(ctx: "SFAContext") -> None:
    """Register all hooks."""
    ctx.hooks.add_map_transition(_sync_current_map)
    ctx.hooks.add_map_transition(_handle_magic_cave_transition)
    ctx.hooks.add_map_transition(_handle_shop_transition)
    ctx.hooks.add_map_transition(_handle_map_entry_state)
    ctx.hooks.add_map_transition(_handle_krazoa_palace)
    ctx.hooks.add_zone_transition(_handle_dim_zone_transition, map_id=DARKICE_TOP_ID)
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("MMP_TEST_OF_COMBAT_WARPPAD", -11900, -11780, -4650, -4550, MOON_MOUNTAIN_PASS_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_test_of_combat_warppad, "MMP_TEST_OF_COMBAT_WARPPAD", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("VFP_SPELLSTONE_DOOR_ZONE", -17350, -17000, -420, -230, VOLCANO_FORCE_POINT_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_fire_spellstone_door, "VFP_SPELLSTONE_DOOR_ZONE", "enter")
    ctx.hooks.add_player_coord_zone(PlayerCoordZone.circle("TTH_WARPSTONE", -5225, -1726, 100, THORNTAIL_HOLLOW_ID))
    ctx.hooks.add_player_coord_transition(_give_spirit_near_warpstone, "TTH_WARPSTONE", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("CRF_ENTRANCE_RACE_START", 2650, -17600, 100, CLOUDRUNNER_FORTRESS_ID)
    )
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("CRF_ENTRANCE_RACE_LADDER", 2529, -18360, 100, CLOUDRUNNER_FORTRESS_ID)
    )
    ctx.hooks.add_player_coord_transition(_show_race_ring, "CRF_ENTRANCE_RACE_START", "enter")
    ctx.hooks.add_player_coord_transition(_show_race_ring, "CRF_ENTRANCE_RACE_LADDER", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("CRF_PRISON_WIND_DRAFT", 1650, 1520, -16770, -16690, CLOUDRUNNER_FORTRESS_ID)
    )
    ctx.hooks.add_player_coord_transition(_turn_off_up_draft, "CRF_PRISON_WIND_DRAFT", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("CRF_QUEEN_ENTRANCE", -160, -100, -17520, -17660, CLOUDRUNNER_FORTRESS_ID)
    )
    ctx.hooks.add_player_coord_transition(_toggle_babies_quest, "CRF_QUEEN_ENTRANCE", "enter")
    ctx.hooks.add_player_coord_transition(_toggle_babies_quest, "CRF_QUEEN_ENTRANCE", "leave")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("CRF_BACK_PATH", 770, 680, -17040, -16900, CLOUDRUNNER_FORTRESS_ID)
    )
    ctx.hooks.add_player_coord_transition(_prevent_softlock_on_back_path, "CRF_BACK_PATH", "enter")
    ctx.hooks.add_player_coord_transition(_close_back_path, "CRF_BACK_PATH", "leave")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("CC_CLOUDRUNNER_CELL", 3800, 3300, -3100, -4100, CAPE_CLAW_ID)
    )
    ctx.hooks.add_player_coord_zone(PlayerCoordZone.square("CC_HIGHTOP_QUEST", 3600, 2340, -2500, -1870, CAPE_CLAW_ID))
    ctx.hooks.add_player_coord_transition(_cc_act1_on, "CC_CLOUDRUNNER_CELL", "enter")
    ctx.hooks.add_player_coord_transition(_cc_act1_off, "CC_CLOUDRUNNER_CELL", "leave")
    ctx.hooks.add_player_coord_transition(_cc_act1_on, "CC_HIGHTOP_QUEST", "enter")
    ctx.hooks.add_player_coord_transition(_cc_act1_off, "CC_HIGHTOP_QUEST", "leave")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.square("LFV_GATE", -1600, -1800, -3000, -2585, LIGHTFOOT_VILLAGE_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_lfv_gate, "LFV_GATE", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("LFV_TEST_OF_FEAR_WARPPAD", -1600, -960, 50, LIGHTFOOT_VILLAGE_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_test_of_fear_warppad, "LFV_TEST_OF_FEAR_WARPPAD", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("LFV_CIRCLE_PLATFORM", -500, -1750, 800, LIGHTFOOT_VILLAGE_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_circle_platform, "LFV_CIRCLE_PLATFORM", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("LFV_SQUARE_PLATFORM", -2000, -1600, 800, LIGHTFOOT_VILLAGE_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_square_platform, "LFV_SQUARE_PLATFORM", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("LFV_TRIANGLE_PLATFORM", -900, -1300, 800, LIGHTFOOT_VILLAGE_ID)
    )
    ctx.hooks.add_player_coord_transition(_handle_triangle_platform, "LFV_TRIANGLE_PLATFORM", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("KP_SPIRIT_2", 12330, 2700, 100, KRAZOA_PALACE_ID, min_y=718, max_y=720)
    )
    ctx.hooks.add_player_coord_transition(_handle_spirit_2, "KP_SPIRIT_2", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("KP_SPIRIT_3", 12390, 2780, 100, KRAZOA_PALACE_ID, min_y=483, max_y=485)
    )
    ctx.hooks.add_player_coord_transition(_handle_spirit_3, "KP_SPIRIT_3", "enter")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("DIM_SHACKLE_KEY_ZONE", -7260, 11100, 400, DARKICE_TOP_ID, min_y=-1500, max_y=-1300)
    )
    ctx.hooks.add_player_coord_transition(_handle_dim_shackle_key, "DIM_SHACKLE_KEY_ZONE", "enter")
    ctx.hooks.add_player_coord_transition(_leave_dim_shackle_key, "DIM_SHACKLE_KEY_ZONE", "leave")
    ctx.hooks.add_player_coord_zone(
        PlayerCoordZone.circle("DIM_SHACKLE_CHEST", -7325, 11400, 100, DARKICE_TOP_ID, min_y=-1439, max_y=-1441)
    )  # No function, just checking in _check_location function
