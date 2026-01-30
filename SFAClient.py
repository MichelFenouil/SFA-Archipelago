import traceback
from typing import Any, Optional
import Utils
import sys

import asyncio

from CommonClient import get_base_parser, logger, server_loop, ClientCommandProcessor, gui_enabled, ClientStatus

import dolphin_memory_engine as dme

from .bit_helper import bit_flagger, extract_bitflag_list, extract_bits_value, get_bit_address, read_value_bytes, set_flag_bit, set_on_or_bytes, set_value_bytes, swap_endian
from .items import ALL_ITEMS_TABLE, FILLER_ITEMS, INVENTORY_ITEMS, SHOP_ITEMS, STAFF_ITEMS, TRICKY_ITEMS, USEFUL_ITEMS, SFACountItemData, SFAItemData, SFAItemType, SFAProgressiveItemData
from .locations import LOCATION_FUEL_CELL, LOCATION_SHOP, LOCATION_UPGRADE, NORMAL_TABLES, SFACountLocationData, SFALocation, SFALocationData, SFALocationType, SFAShopLocationData, SFAUpgradeLocationData
from .addresses import *

TRACKER_LOADED = False
# try:
#     from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
#     TRACKER_LOADED = True
# except ModuleNotFoundError:
from CommonClient import CommonContext as SuperContext


CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a randomized ROM for Super Mario Sunshine. Trying again in 5 seconds..."
)
CONNECTION_REFUSED_SAVE_STATUS = (
    "Dolphin failed to connect. Please load into the save file. Trying again in 5 seconds..."
)
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Super Mario Sunshine is running."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."



class SFAContext(SuperContext):
    game = "Star Fox Adventure"
    tags = {"AP"}
    items_handling = 0b111  # full remote

    #: Temp should save in memory
    expected_idx=0
    received_items_id = []

    victory=False

    #: Player state (probably change to server)
    fuel_cell_count=156

    #: Suppose the player starts in main menu
    stored_map=0x3F

    def __init__(self, server_address, password):
        super(SFAContext, self).__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = False
        self.awaiting_bridge = False
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(SFAContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    @property
    def endpoints(self):
        if self.server:
            return [self.server]
        else:
            return []
        
    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Star Fox Adventure Client"
        return ui


async def dolphin_sync_task(ctx: SFAContext) -> None:
    logger.info("Starting Dolphin connector. Use /dolphin for status information.")
    while not ctx.exit_event.is_set():
        try:
            if dme.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if ctx.awaiting_rom:
                    logger.info("Connected")
                    await ctx.server_auth()
                await asyncio.sleep(0.5)
            else:
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                logger.info("Attempting to connect to Dolphin...")
                dme.hook()
                if dme.is_hooked():
                    if dme.read_bytes(0x80000000, 6) != b"GSAE01":
                        logger.info(CONNECTION_REFUSED_GAME_STATUS)
                        ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                        dme.un_hook()
                        await asyncio.sleep(5)
                    else:
                        logger.info(CONNECTION_CONNECTED_STATUS)
                        ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
                        ctx.locations_checked = set()
                        await asyncio.sleep(5)
                else:
                    logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
                    dme_status = dme.get_status()
                    logger.info(dme_status)
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    await asyncio.sleep(5)
                    continue
        except Exception:
            dme.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            await asyncio.sleep(5)
            continue


def sync_player_state(ctx: SFAContext):
    _give_item_in_game(ctx, FILLER_ITEMS["Fuel Cell"])
    _give_item_in_game(ctx, INVENTORY_ITEMS["Alpine Root"])
    _give_item_in_game(ctx, INVENTORY_ITEMS["Scarab Bag (Progressive)"])
    _give_item_in_game(ctx, USEFUL_ITEMS["HP Upgrade"])
    _give_item_in_game(ctx, USEFUL_ITEMS["MP Upgrade"])


async def _wait_cutscene_end():
    seq = dme.read_byte(0x803DD08C)
    while seq != 0:
        seq = dme.read_byte(0x803DD08C)
        await asyncio.sleep(0.1)

async def locations_watcher(ctx):
    def _check_location_flag(ctx: SFAContext, location: SFALocationData) -> None:
        if location.id not in ctx.server_locations:
            return
        address, bit_position = get_bit_address(location.table_address, location.bit_offset)
        byte = dme.read_byte(address)
        if bit_position in extract_bitflag_list(byte):
            ctx.locations_checked.add(location.id)

    def _check_location_value(ctx: SFAContext, location: SFACountLocationData) -> None:
        if location.id not in ctx.server_locations:
            return
        value = read_value_bytes(location.table_address, location.bit_offset, location.bit_size)
        if value >= location.count:
            ctx.locations_checked.add(location.id)
        

    for cell_name, cell_data  in NORMAL_TABLES.items():
        if isinstance(cell_data, SFACountLocationData):
            _check_location_value(ctx, cell_data)
            await _wait_cutscene_end()
        else:
            _check_location_flag(ctx, cell_data)

    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if map_value == MAP_MAGIC_CAVE_NO and ctx.stored_map == MAP_MAGIC_CAVE_NO:
        for loc_name, loc_data in LOCATION_UPGRADE.items():
            mc_act_byte = dme.read_byte(MAGIC_CAVE_ACT_ADDRESS)
            mc_act = extract_bits_value(mc_act_byte, offset=2, size=4)
            mc_flags_raw = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
            mc_flags = extract_bitflag_list(swap_endian(mc_flags_raw))
            if \
                (mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags) \
                or (mc_act == MAGIC_CAVE_MANA_ACT and loc_data.mc_bitflag is None) :
                _check_location_flag(ctx, loc_data)
                # Wait for anim end
                await _wait_cutscene_end()
    
    if map_value == MAP_SHOP_NO and ctx.stored_map == MAP_SHOP_NO:
        for loc_name, loc_data in LOCATION_SHOP.items():
            _check_location_flag(ctx, loc_data)

    # TODO Failsafe if sending a location that doesn't exist?
    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        sync_player_state(ctx)
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])


async def give_items(ctx: SFAContext):
    #: Read the expected index of the player, which is the index of the next item they're expecting to receive.
    #: The expected index starts at 0 for a fresh save file.
    #: TODO save value in memory 
    expected_idx = ctx.expected_idx

    # Check if there are new items.
    received_items = ctx.items_received
    if len(received_items) <= expected_idx:
        # There are no new items.
        return

    # Loop through items to give.
    # Give the player all items at an index greater than or equal to the expected index.
    for idx, item in enumerate(received_items[expected_idx:], expected_idx):
        # Attempt to give the item and increment the expected index.
        logger.debug(f"Received item: {item}")
        ctx.received_items_id.append(item.item)
        while not _give_item_in_game(ctx, SFAItemData.get_by_id(item.item)):
            await asyncio.sleep(0.01)
        ctx.expected_idx = idx + 1

def _give_item_in_game(ctx: SFAContext, item: SFAItemData):
    if ctx.stored_map == MAP_SHOP_NO and (item.type == SFAItemType.SHOP_PROGRESSION or item.type == SFAItemType.SHOP_USEFUL):
        # Don't send shop items if inside shop
        return True
    if isinstance(item, SFAProgressiveItemData):
        count = ctx.received_items_id.count(item.id)
        for id, progress in enumerate(item.progressive_data):
            # Set True until count and False for the rest
            set_flag_bit(progress[1], progress[0], count > id)
        logger.debug(f"Received {count} of progressive object: {item}")
        return True
    
    if isinstance(item, SFACountItemData):
        count = ctx.received_items_id.count(item.id)
        if count > item.max_count:
            count = item.max_count
        value = item.start_amount + count * item.count_increment
        logger.debug(f"Received {count} of count object: {item}")
        set_value_bytes(item.table_address, item.bit_offset, value, item.bit_size)
        return True
        
    if item.type != SFAItemType.FILLER:
        set_flag_bit(item.table_address, item.bit_offset, True)
        return True
    return True


async def force_gameflags(ctx):
    # Set bitflags when starting save
    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if ctx.stored_map != map_value and ctx.stored_map == 0x3F:
        logger.info("Set starting flags ON")
        set_on_or_bytes(ITEM_MAP_ADDRESS, ITEM_MAP_INIT_VALUE, 3)
        set_on_or_bytes(SKIP_TUTO_ADDRESS, SKIP_TUTO_VALUE, 2)
        for item in STARTING_ON_FLAGS:
            set_flag_bit(item.table_address, item.bit_offset, True)

    for item in CONSTANT_ON_FLAGS:
        set_flag_bit(item.table_address, item.bit_offset, True)

    # Force magic cave gate open
    for item in OFF_FLAGS:
        set_flag_bit(item.table_address, item.bit_offset, False)

    # Force Bomb_spore to 1 for testing
    address, position = get_bit_address(T2_ADDRESS, 0x77)
    cache_byte = dme.read_byte(address)
    updated_byte = bit_flagger(cache_byte, position, True)
    dme.write_byte(address, updated_byte)


async def special_map_flags(ctx: SFAContext):
    def _special_location_item_toggle(ctx: SFAContext, location: SFAUpgradeLocationData | SFAShopLocationData, map_entered: int, map_expected: int):
        if map_entered == map_expected:
            if location.id in ctx.checked_locations or location.id not in ctx.server_locations:
                # Checked location (or does not exist), force item ON
                set_flag_bit(location.table_address, location.bit_offset, True)
            else:
                # Unchecked location, force item OFF
                set_flag_bit(location.table_address, location.bit_offset, False)
        if ctx.stored_map == map_expected:
            if location.type == SFALocationType.MAP or location.linked_item in ctx.received_items_id:
                # Item received, set flag back ON
                set_flag_bit(location.table_address, location.bit_offset, True)
            else:
                # Item not received, set flag back OFF
                set_flag_bit(location.table_address, location.bit_offset, False)

    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if ctx.stored_map != map_value:
        logger.info(f"Entering map {map_value:x}")

        #: Check Magic Cave locations
        mc_act_byte = dme.read_byte(MAGIC_CAVE_ACT_ADDRESS)
        mc_act = extract_bits_value(mc_act_byte, offset=2, size=4)
        mc_flags_bytes = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
        mc_flags = extract_bitflag_list(swap_endian(mc_flags_bytes))
        for loc_name, loc_data in LOCATION_UPGRADE.items():
            if mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags:
                _special_location_item_toggle(ctx, loc_data, map_value, MAP_MAGIC_CAVE_NO)

        #: Check Shop locations
        for loc_name, loc_data in LOCATION_SHOP.items():
            ctx.server_locations
            _special_location_item_toggle(ctx, loc_data, map_value, MAP_SHOP_NO)

        #: Check Ice Mountain Act
        # tricky = TRICKY_ITEMS["Tricky"]
        # root = INVENTORY_ITEMS["Alpine Root"]
        # if tricky.id in ctx.received_items_id and ctx.received_items_id.count(root.id) == 2:
        #     set_value_bytes(ICE_MOUNTAIN_ACT_ADDRESS, 2, 2, 4)
        # else:
        #     set_value_bytes(ICE_MOUNTAIN_ACT_ADDRESS, 2, 1, 4)

        ctx.stored_map = map_value


async def game_watcher(ctx: SFAContext):
    while not ctx.exit_event.is_set():
        try:
            if not dme.is_hooked() or ctx.slot is None:
                logger.info("Not connected to a slot")
                logger.info(ctx.slot)
                await asyncio.sleep(5)
                continue

            await force_gameflags(ctx)
            await locations_watcher(ctx)
            await give_items(ctx)
            await special_map_flags(ctx)

            if ctx.victory and not ctx.finished_game:
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True

            await asyncio.sleep(0.1)
        except Exception:
            dme.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            await asyncio.sleep(10)
            continue


def main(*launch_args: str):
    server_address: str = ""

    parser = get_base_parser()
    args = parser.parse_args(launch_args)

    async def _main(connect, password):
        ctx = SFAContext(connect, password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        await asyncio.sleep(1)

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="SmsDolphinSync")
        progression_watcher = asyncio.create_task(game_watcher(ctx), name="SmsProgressionWatcher")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()
        
        if ctx.dolphin_sync_task:
                await ctx.dolphin_sync_task

        if progression_watcher:
                await progression_watcher
    
    asyncio.run(_main(args.connect, args.password))

if __name__ == "__main__":
    Utils.init_logging("SFAClient", exception_logger="Client")
    main(*sys.argv[1:])