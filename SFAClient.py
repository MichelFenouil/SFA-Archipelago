import asyncio
import sys
import traceback
from typing import ClassVar

import dolphin_memory_engine as dme
import Utils
from CommonClient import (
    ClientStatus,
    get_base_parser,
    gui_enabled,
    logger,
    server_loop,
)
from CommonClient import (
    CommonContext as SuperContext,
)

from .addresses import *  # noqa: F403
from .bit_helper import (
    extract_bitflag_list,
    extract_bits_value,
    get_bit_address,
    read_value_bytes,
    set_flag_bit,
    set_on_or_bytes,
    set_value_bytes,
    swap_endian,
    update_bits,
)
from .items import (
    FILLER_ITEMS,
    ITEM_INVENTORY,
    ITEM_STAFF,
    ITEM_TRICKY,
    USEFUL_ITEMS,
    SFAConsumableItemData,
    SFACountItemData,
    SFAItemData,
    SFAItemType,
    SFAProgressiveItemData,
    SFAQuestItemData,
)
from .locations import (
    LOCATION_ANY,
    LOCATION_SHOP,
    LOCATION_UPGRADE,
    NORMAL_TABLES,
    SFACountLocationData,
    SFALinkedLocationData,
    SFALocationData,
    SFALocationType,
    SFAShopLocationData,
    SFAUpgradeLocationData,
)

TRACKER_LOADED = False
# try:
#     from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
#     TRACKER_LOADED = True
# except ModuleNotFoundError:

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
    """
    The context for Star Fox Adventures client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Star Fox Adventures.
    """

    game = "Star Fox Adventures"
    items_handling = 0b111  # full remote

    #: Temp should save in memory
    expected_idx = 0
    received_items_id: ClassVar[list[int]] = []

    victory = False

    #: Player state (probably change to server)
    fuel_cell_count = 156

    #: Suppose the player starts in main menu
    stored_map = 0x3F
    stored_dim = 0
    stored_dim2 = 0

    def __init__(self, server_address, password):
        """
        Initialize the Star Fox Adventures context.

        :param server_address: Address of the Archipelago server
        :param password: Password for server authentication
        """
        super().__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = False
        self.awaiting_bridge = False
        self.dolphin_sync_task: asyncio.Task[None] | None = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.tags = {"AP"}

    async def server_auth(self, password_requested: bool = False):
        """
        Authenticate with the Archipelago server.

        :param password_requested: Indicates if the server has requested a password
        """
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def make_gui(self):
        """
        Create the GUI for the Star Fox Adventures client.

        :return: The GUI instance
        """
        ui = super().make_gui()
        ui.base_title = "Star Fox Adventures Client"
        return ui


async def dolphin_sync_task(ctx: SFAContext) -> None:
    """
    Task to manage the connection and synchronization with the Dolphin emulator.

    :param ctx: The Star Fox Adventures context
    """
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
    """
    Synchronize the player's state with the current game data.

    :param ctx: The Star Fox Adventures context
    """
    _give_item_in_game(ctx, FILLER_ITEMS["Fuel Cell"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Alpine Root"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Scarab Bag (Progressive)"])
    _give_item_in_game(ctx, USEFUL_ITEMS["HP Upgrade"])
    _give_item_in_game(ctx, USEFUL_ITEMS["MP Upgrade"])
    _give_item_in_game(ctx, ITEM_INVENTORY["White GrubTub"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Gate Key"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Cog 1"])
    _give_item_in_game(ctx, ITEM_INVENTORY["DIM Alpine Root"])
    _give_item_in_game(ctx, ITEM_TRICKY["Tricky (Progressive)"])


async def sync_full_player_state(ctx: SFAContext):
    """
    Fully synchronize the player's state with the current game data.

    :param ctx: The Star Fox Adventures context
    """
    ctx.expected_idx = 0
    await give_items(ctx)  # type: ignore


async def _wait_cutscene_end():
    """Wait until a cutscene is over."""
    seq = dme.read_byte(0x803DD08C)
    while seq != 0:
        seq = dme.read_byte(0x803DD08C)
        await asyncio.sleep(0.1)


async def locations_watcher(ctx):
    """
    Watch for location checks in the game and notify the server.

    :param ctx: The Star Fox Adventures context
    """

    def _check_location_flag(ctx: SFAContext, location: SFALocationData) -> None:
        """
        Check if a location has been checked based on its flag.

        :param ctx: The Star Fox Adventures context
        :param location: The location data to check
        """
        if location.id not in ctx.server_locations:
            return
        address, bit_position = get_bit_address(location.table_address, location.bit_offset)
        byte = dme.read_byte(address)
        if bit_position in extract_bitflag_list(byte):
            ctx.locations_checked.add(location.id)

    def _check_location_value(ctx: SFAContext, location: SFACountLocationData) -> None:
        """
        Check if a location has been checked based on its value.

        :param ctx: The Star Fox Adventures context
        :param location: The location data to check
        """
        if location.id not in ctx.server_locations:
            return
        value = read_value_bytes(location.table_address, location.bit_offset, location.bit_size)
        if value >= location.count:
            ctx.locations_checked.add(location.id)

    for location_data in NORMAL_TABLES.values():
        if isinstance(location_data, SFALinkedLocationData):
            map_value = read_value_bytes(
                location_data.map_address, 0, location_data.map_bit_size * 8, location_data.map_bit_size
            )
            if map_value == location_data.map_value:
                _check_location_flag(ctx, location_data)
        elif isinstance(location_data, SFACountLocationData):
            _check_location_value(ctx, location_data)
            await _wait_cutscene_end()
        else:
            _check_location_flag(ctx, location_data)

    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if map_value == MAP_MAGIC_CAVE_NO and ctx.stored_map == MAP_MAGIC_CAVE_NO:
        for loc_data in LOCATION_UPGRADE.values():
            mc_act_byte = dme.read_byte(MAGIC_CAVE_ACT_ADDRESS)
            mc_act = extract_bits_value(mc_act_byte, offset=2, size=4)
            mc_flags_raw = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
            mc_flags = extract_bitflag_list(swap_endian(mc_flags_raw))
            if (mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags) or (
                mc_act == MAGIC_CAVE_MANA_ACT and loc_data.mc_bitflag is None
            ):
                _check_location_flag(ctx, loc_data)
                # Wait for anim end
                await _wait_cutscene_end()

    if map_value == MAP_SHOP_NO and ctx.stored_map == MAP_SHOP_NO:
        for loc_data in LOCATION_SHOP.values():
            _check_location_flag(ctx, loc_data)

    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        sync_player_state(ctx)
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])

    if ctx.victory and not ctx.finished_game:
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
        ctx.finished_game = True


async def give_items(ctx: SFAContext):
    """
    Give items to the player in the game.

    :param ctx: The Star Fox Adventures context
    """
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
    """
    Give an item to the player in the game.

    :param ctx: The Star Fox Adventures context
    :param item: The item data to give
    :return: True if the item was given successfully, False otherwise
    """
    if item.id == 2000:  # Victory
        ctx.victory = True
        return True

    if ctx.stored_map == MAP_SHOP_NO and (
        item.type == SFAItemType.SHOP_PROGRESSION or item.type == SFAItemType.SHOP_USEFUL
    ):
        # Don't send shop items if inside shop
        return True

    if isinstance(item, SFAProgressiveItemData):
        count = ctx.received_items_id.count(item.id)
        for id, progress in enumerate(item.progressive_data):
            # Set True until count and False for the rest
            set_flag_bit(progress[1], progress[0], count > id)
        logger.debug(f"Received {count} of progressive object: {item}")
        return True

    if isinstance(item, SFAQuestItemData):
        count = ctx.received_items_id.count(item.id)
        if count > item.max_count:
            count = item.max_count
            # Could read location count instead
        used_count = read_value_bytes(item.table_address, item.item_used_flag_offset, item.item_used_bit_size)
        value = item.start_amount + (count - used_count) * item.count_increment
        if value < 0:
            value = 0
        logger.debug(f"Received {count} of quest object: {item}")
        set_value_bytes(item.table_address, item.bit_offset, value, item.bit_size)
        return True

    if isinstance(item, SFACountItemData):
        count = ctx.received_items_id.count(item.id)
        if count > item.max_count:
            count = item.max_count
        value = item.start_amount + count * item.count_increment
        logger.debug(f"Received {count} of count object: {item}")
        set_value_bytes(item.table_address, item.bit_offset, value, item.bit_size)
        return True

    if isinstance(item, SFAConsumableItemData):
        current_value = read_value_bytes(item.table_address, item.bit_offset, item.bit_size)
        value = current_value + item.add_value
        max_value = read_value_bytes(item.max_read_address, 0x0, item.max_read_bit_size)
        if value > max_value:
            value = max_value
        set_value_bytes(item.table_address, item.bit_offset, value, item.bit_size)
        return True

    # All other items
    if item.id == 105:
        logger.debug(f"Cog 1 received: {item.id in ctx.received_items_id}")
    set_flag_bit(item.table_address, item.bit_offset, item.id in ctx.received_items_id)
    return True


async def force_gameflags(ctx: SFAContext) -> None:
    """
    Force game flags when starting a save.

    :param ctx: The Star Fox Adventures context
    """
    # Set bitflags when starting save
    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if ctx.stored_map != map_value and ctx.stored_map == 0x3F:
        logger.info("Set starting flags ON")
        set_on_or_bytes(ITEM_MAP_ADDRESS, ITEM_MAP_INIT_VALUE, 3)
        set_on_or_bytes(SKIP_TUTO_ADDRESS, SKIP_TUTO_VALUE, 2)
        for item in STARTING_FLAGS:
            set_flag_bit(item.table_address, item.bit_offset, item.state)
        await sync_full_player_state(ctx)

    for item in CONSTANT_FLAGS:
        set_flag_bit(item.table_address, item.bit_offset, item.state)

    # Force Bomb_spore to 1 for testing
    address, position = get_bit_address(T2_ADDRESS, 0x77)
    cache_byte = dme.read_byte(address)
    updated_byte = update_bits(cache_byte, position, True)
    dme.write_byte(address, updated_byte)


async def special_map_flags(ctx: SFAContext) -> None:
    """
    Handle special map flags for certain locations.

    :param ctx: The Star Fox Adventures context
    """

    def _special_location_item_toggle(
        ctx: SFAContext,
        location: SFAUpgradeLocationData | SFAShopLocationData,
        map_entered: int,
        map_expected: int,
    ):
        """
        Toggle special location items based on the map entered.

        :param ctx: The Star Fox Adventures context
        :param location: The location data to toggle
        :param map_entered: The map that was entered
        :param map_expected: The expected map for the location
        """
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
        for loc_data in LOCATION_UPGRADE.values():
            if mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags:
                _special_location_item_toggle(ctx, loc_data, map_value, MAP_MAGIC_CAVE_NO)

        #: Check Shop locations
        for loc_data in LOCATION_SHOP.values():
            _special_location_item_toggle(ctx, loc_data, map_value, MAP_SHOP_NO)

        # Force SH act2
        if map_value == 0x7:  # SH
            address, offset = get_bit_address(T2_ADDRESS, 0x0722)
            im_act_byte = dme.read_byte(address)
            im_act = extract_bits_value(im_act_byte, offset=offset, size=4)
            logger.info(f"SH act: {im_act}")
            set_value_bytes(address, offset, 0x2, 4)

        # Remove fireblaster in world map
        if map_value == 0x29:
            item = ITEM_STAFF["Fire Blaster"]
            address, offset = get_bit_address(item.table_address, item.bit_offset)
            set_flag_bit(address, offset, False)
        if ctx.stored_map == 0x29:
            item = ITEM_STAFF["Fire Blaster"]
            address, offset = get_bit_address(item.table_address, item.bit_offset)
            set_flag_bit(address, offset, item.id in ctx.received_items_id)

        # Give Krystal Spirit 1
        if map_value == 0x0B:
            address, offset = get_bit_address(T2_ADDRESS, 0x053C)
            set_flag_bit(address, offset, True)

        ctx.stored_map = map_value

    # Shakle key is annoying but cogs are fine, only give cogs while inside cog room
    # flags = 448380 inside cog room
    dim_obj_value = read_value_bytes(0x803A3895, 0, 32, 4)
    if dim_obj_value != ctx.stored_dim:
        logger.info(f"Entering dim zone {dim_obj_value:x}")
        _give_item_in_game(ctx, ITEM_INVENTORY["Dinosaur Horn"])
        if dim_obj_value == 0x448380:
            item = ITEM_INVENTORY.get("Cog 2/3/4")
            assert isinstance(item, SFAProgressiveItemData)
            count = ctx.received_items_id.count(item.id)
            for id, progress in enumerate(item.progressive_data):
                # Set True until count and False for the rest
                set_flag_bit(progress[1], progress[0], count > id)
                set_flag_bit(progress[1], progress[0] - 1, False)
        else:
            item = ITEM_INVENTORY.get("Cog 2/3/4")
            location = [
                LOCATION_ANY["DIM: Cog 2 Chest"],
                LOCATION_ANY["DIM: Get Cog 3"],
                LOCATION_ANY["DIM: Get Cog 4"],
            ]
            assert isinstance(item, SFAProgressiveItemData)
            for _id, progress in enumerate(item.progressive_data):
                # True to hide all cogs
                set_flag_bit(progress[1], progress[0], True)
            for loc in location:
                if loc.id in ctx.checked_locations:
                    set_flag_bit(loc.table_address, loc.bit_offset, True)
                else:
                    set_flag_bit(loc.table_address, loc.bit_offset, False)

        ctx.stored_dim = dim_obj_value

    dim2_obj_value = read_value_bytes(0x803A3891, 0, 32, 4)
    if dim2_obj_value != ctx.stored_dim2:
        logger.info(f"Entering dim 2 zone {dim2_obj_value:x}")
        location = LOCATION_ANY["DIM: Get Silver Key"]
        assert isinstance(location, SFALinkedLocationData)
        if dim2_obj_value == 0x40003 or dim2_obj_value == 0x40042:
            set_flag_bit(location.table_address, location.bit_offset, location.id in ctx.checked_locations)
        else:
            set_flag_bit(location.table_address, location.bit_offset, location.linked_item in ctx.received_items_id)

        ctx.stored_dim2 = dim2_obj_value


async def game_watcher(ctx: SFAContext):
    """
    Main game watcher loop.

    :param ctx: The Star Fox Adventures context
    """
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
    """
    Main entry point for the Star Fox Adventures client.

    :param launch_args: Command-line arguments for the client
    """
    parser = get_base_parser()
    args = parser.parse_args(launch_args)

    async def _main(connect, password):
        """
        Main asynchronous function for the Star Fox Adventures client.

        :param connect: The server address to connect to
        :param password: The password for server authentication
        """
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
