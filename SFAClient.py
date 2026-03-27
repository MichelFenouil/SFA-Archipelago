import asyncio
from itertools import count
import sys
import traceback
from typing import ClassVar

import dolphin_memory_engine as dme
import Utils
from CommonClient import (
    ClientCommandProcessor,
    ClientStatus,
    CommonContext,
    get_base_parser,
    gui_enabled,
    logger,
    server_loop,
)
from MultiServer import mark_raw

from .addresses import *  # noqa: F403
from .game_flags import MAGIC_CAVE_ACT_GAMEBIT, STARTING_FLAGS, CONSTANT_FLAGS, DINO_CAVE, DIM_OPEN_BIKE, DIM_OPEN_BLIZZARD, KRAZOA_SPIRIT_1
from .bit_helper import (
    extract_bitflag_list,
    extract_bits_value,
    get_bit_address,
    read_value_bytes,
    set_flag_bit,
    set_on_or_bytes,
    set_value_bytes,
    swap_endian,
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
    SFAItemTags,
    SFAPlanetItemData,
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
    SFALocationTags,
    SFAShopLocationData,
    SFAUpgradeLocationData,
)

TRACKER_LOADED = False
# try:
#     from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext
#     TRACKER_LOADED = True
# except ModuleNotFoundError:

CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a Star Fox Adventures ROM. Trying again in 5 seconds..."
)
CONNECTION_REFUSED_SAVE_STATUS = (
    "Dolphin failed to connect. Please load into the save file. Trying again in 5 seconds..."
)
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Star Fox Adventures is running."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."


class SFACommandProcessor(ClientCommandProcessor):
    """
    Command Processor for The Wind Waker client commands.

    This class handles commands specific to The Wind Waker.
    """

    def __init__(self, ctx: "SFAContext"):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        self.ctx = ctx

    @mark_raw
    def _cmd_sync(self, name: str = "") -> bool:
        """
        Synchronize items with server state.

        :param name: Which item to synchronize. Synchronizes all items if empty.
        """
        if name == "":
            self.ctx.sync_task = asyncio.create_task(sync_full_player_state(self.ctx))
            logger.info("Player state synchronized with server state.")
        else:
            return _give_item_in_game(self.ctx, SFAItemData.get_by_name(name))
        return True


class SFAContext(CommonContext):
    """
    The context for Star Fox Adventures client.

    This class manages all interactions with the Dolphin emulator and the Archipelago server for Star Fox Adventures.
    """

    command_processor = SFACommandProcessor
    game = "Star Fox Adventures"
    items_handling = 0b111  # full remote

    #: Temp should save in memory
    expected_idx = 0
    received_items_id: ClassVar[list[int]] = []

    victory = False

    #: Player state (probably change to server)
    fuel_cell_count = 0
    shop_visited = False

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
        self.sync_task: asyncio.Task[None] | None = None

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

    def on_package(self, cmd: str, args: dict):
        """Handle incoming packages from the server."""
        return super().on_package(cmd, args)


def sync_player_state(ctx: SFAContext):
    """
    Synchronize the player's state with the current game data.

    :param ctx: The Star Fox Adventures context
    """
    _give_item_in_game(ctx, FILLER_ITEMS["Fuel Cell"])
    _give_item_in_game(ctx, ITEM_INVENTORY["SHW Alpine Root"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Scarab Bag (Progressive)"])
    _give_item_in_game(ctx, USEFUL_ITEMS["HP Upgrade"])
    _give_item_in_game(ctx, USEFUL_ITEMS["MP Upgrade"])
    _give_item_in_game(ctx, ITEM_INVENTORY["White GrubTub"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Gate Key"])
    _give_item_in_game(ctx, ITEM_INVENTORY["Entrance Bridge Cog"])
    _give_item_in_game(ctx, ITEM_INVENTORY["DIM Alpine Root"])
    _give_item_in_game(ctx, ITEM_TRICKY["Tricky (Progressive)"])


async def sync_full_player_state(ctx: SFAContext):
    """
    Fully synchronize the player's state with the current game data.

    :param ctx: The Star Fox Adventures context
    """
    logger.debug("Syncing full player state")
    received_items = ctx.items_received
    for _, item in enumerate(received_items):
        while not _give_item_in_game(ctx, SFAItemData.get_by_id(item.item)):
            await asyncio.sleep(0.01)
    sync_player_state(ctx)


async def _wait_cutscene_end():
    """Wait until a cutscene is over."""
    seq = dme.read_byte(CURRENT_SEQ_ADDRESS)
    while seq != 0:
        seq = dme.read_byte(CURRENT_SEQ_ADDRESS)
        await asyncio.sleep(0.1)


async def locations_watcher(ctx):
    """
    Watch for location checks in the game and notify the server.

    :param ctx: The Star Fox Adventures context
    """

    def _check_location_flag(ctx: SFAContext, location: SFALocationData) -> bool:
        """
        Check if a location has been checked based on its flag.

        :param ctx: The Star Fox Adventures context
        :param location: The location data to check
        """
        if location.id not in ctx.server_locations or location.id in ctx.locations_checked:
            return False
        if location.is_checked():
            ctx.locations_checked.add(location.id)
            return True
        return False

    # TODO: verify snowhorn and queen cutscenes
    for location_data in NORMAL_TABLES.values():
        _check_location_flag(ctx, location_data)

    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if map_value == MAGIC_CAVE_ID and ctx.stored_map == MAGIC_CAVE_ID:
        mc_act = MAGIC_CAVE_ACT_GAMEBIT.get_value()
        mc_flags_bytes = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
        mc_flags = extract_bitflag_list(swap_endian(mc_flags_bytes))
        for loc_data in LOCATION_UPGRADE.values():
            if mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags:
                _check_location_flag(ctx, loc_data)

    # TODO: just check CTX
    if map_value == SHOP_ID and ctx.stored_map == SHOP_ID:
        for loc_data in LOCATION_SHOP.values():
            _check_location_flag(ctx, loc_data)

    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        await _wait_cutscene_end()
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


def _give_item_in_game(ctx: SFAContext, item: SFAItemData | None) -> bool:
    """
    Give an item to the player in the game.

    :param ctx: The Star Fox Adventures context
    :param item: The item data to give
    :return: True if the item was given successfully, False otherwise
    """
    if item is None or item.id == 0:
        logger.error("Item not found in data.")
        return False

    if item.id == SFAItemData.get_by_name("Victory").id:  # Victory
        ctx.victory = True
        return True

    if ctx.stored_map == SHOP_ID and (
        SFAItemTags.SHOP in item.tags
    ):
        # Don't send shop items if inside shop
        return True

    if isinstance(item, (SFAProgressiveItemData, SFACountItemData, SFAQuestItemData)):
        count = ctx.received_items_id.count(item.id)
        item.set_value(count)
        logger.debug(f"Received {count} of counted object: {item.name}")
        return True

    if isinstance(item, SFAConsumableItemData):
        item.set_value()
        return True

    if isinstance(item, SFAPlanetItemData):
        item.game_bit.set_bit(item.id in ctx.received_items_id)
        set_flag_bit(item.gate_table_address, item.gate_bit_offset, item.id in ctx.received_items_id)
        return True

    # All other items
    item.set_value(item.id in ctx.received_items_id)
    return True


async def force_gameflags(ctx: SFAContext) -> None:
    """
    Force game flags when starting a save.

    :param ctx: The Star Fox Adventures context
    """
    # Set bitflags when starting save
    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if ctx.stored_map != map_value and ctx.stored_map == MAIN_MENU_ID:
        logger.debug("Set starting flags")
        set_on_or_bytes(ITEM_MAP_ADDRESS, ITEM_MAP_INIT_VALUE, 3)
        set_on_or_bytes(SKIP_TUTO_ADDRESS, SKIP_TUTO_VALUE, 2)
        for item in STARTING_FLAGS:
            set_flag_bit(item.address, item.offset, item.state)
        await sync_full_player_state(ctx)

    for item in CONSTANT_FLAGS:
        set_flag_bit(item.address, item.offset, item.state)

    if map_value == ICE_MOUNTAIN_BOTTOM_ID:
        tricky_item = ITEM_TRICKY["Tricky (Progressive)"]
        tricky_flag = tricky_item.progressive_data[0]
        set_flag_bit(tricky_flag[1], tricky_flag[0], tricky_item.id in ctx.received_items_id)

    if DINO_CAVE.get_bit():
        dino_horn = SFAItemData.get_by_name("Dinosaur Horn")
        dino_horn.set_value(dino_horn.id in ctx.received_items_id)

    # Force Bomb_spore to 1 for testing
    # address, position = get_bit_address(T2_ADDRESS, 0x77)
    # cache_byte = dme.read_byte(address)
    # updated_byte = update_bits(cache_byte, position, True)
    # dme.write_byte(address, updated_byte)


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
            # Give item inside if location is checked
            location.set_bit(location.id in ctx.checked_locations or location.id not in ctx.server_locations)
        if ctx.stored_map == map_expected:
            # Retrieve item when leaving map
            location.set_bit(SFALocationTags.MAP in location.tags or location.linked_item in ctx.received_items_id)

    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if ctx.stored_map != map_value:
        logger.info(f"Entering map {map_value:x}")
        await ctx.send_msgs(
            [
                {
                    "cmd": "Set",
                    "key": f"SFA_current_map_{ctx.team}_{ctx.slot}",
                    "default": {},
                    "operations": [
                        {
                            "operation": "replace",
                            "value": map_value,
                        }
                    ],
                }
            ]
        )

        #: Check Magic Cave locations
        mc_act = MAGIC_CAVE_ACT_GAMEBIT.get_value()
        mc_flags_bytes = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
        mc_flags = extract_bitflag_list(swap_endian(mc_flags_bytes))
        for loc_data in LOCATION_UPGRADE.values():
            if mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags:
                _special_location_item_toggle(ctx, loc_data, map_value, MAGIC_CAVE_ID)

        #: Check Shop locations
        if map_value == SHOP_ID and not ctx.shop_visited:
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
            _special_location_item_toggle(ctx, loc_data, map_value, SHOP_ID)

        # Force SH act2
        if map_value == THORNTAIL_HOLLOW_ID:
            set_value_bytes(T2_ADDRESS, THORNTAIL_HOLLOW_ACT_OFFSET, 0x2, value_size=4)

        # Remove fireblaster in world map
        if map_value == WORLD_MAP_ID:
            SFAItemData.get_by_name("Fire Blaster").set_value(False)
        if ctx.stored_map == WORLD_MAP_ID:
            item = SFAItemData.get_by_name("Fire Blaster")
            item.set_value(item.id in ctx.received_items_id)

        # Give Krystal Spirit 1
        if map_value == KRAZOA_PALACE_ID:
            KRAZOA_SPIRIT_1.set_bit(True)

        ctx.stored_map = map_value

    # Place bridge cogs when entering the room
    dim_obj_value = read_value_bytes(DIM_OBJECTS_ADDRESS, 0, 32, 4)
    if dim_obj_value != ctx.stored_dim:
        logger.debug(f"Entering dim zone {dim_obj_value:x}")
        if dim_obj_value == DIM_COGS_ZONE_VALUE or dim_obj_value == DIM_COGS_ZONE_VALUE2:
            item = ITEM_INVENTORY.get("SharpClaw Fort Bridge Cogs")
            assert isinstance(item, SFAProgressiveItemData)
            count = ctx.received_items_id.count(item.id)
            for id, progress in enumerate(item.progressive_data):
                # Set True until count and False for the rest
                set_flag_bit(progress[1], progress[0], count > id)
                set_flag_bit(progress[1], progress[0] - 1, False)
        elif (
            dim_obj_value - ctx.stored_dim == DIM_BLIZZARD_ZONE_TRANSITION
            or ctx.stored_dim - dim_obj_value == DIM_BLIZZARD_ZONE_TRANSITION
        ):
            logger.debug("Entering Blizzard zone")
            for flag in DIM_OPEN_BLIZZARD:
                flag.set_bit(False)
        elif ctx.stored_dim - dim_obj_value == DIM_BIKE_ZONE_TRANSITION:
            logger.debug("Bike zone transition")
            for flag in DIM_OPEN_BIKE:
                flag.set_bit(False)
        else:
            item = ITEM_INVENTORY.get("SharpClaw Fort Bridge Cogs")
            location = [
                LOCATION_ANY["DIM: Enemy Gate Cog Chest"],
                LOCATION_ANY["DIM: Hut Cog Chest"],
                LOCATION_ANY["DIM: Ice Cog Chest"],
            ]
            assert isinstance(item, SFAProgressiveItemData)
            for _id, progress in enumerate(item.progressive_data):
                # True to hide all cogs
                set_flag_bit(progress[1], progress[0], True)
            for loc in location:
                loc.set_bit(loc.id in ctx.checked_locations)

        ctx.stored_dim = dim_obj_value


async def game_watcher(ctx: SFAContext):
    """
    Main game watcher loop.

    :param ctx: The Star Fox Adventures context
    """
    while not ctx.exit_event.is_set():
        try:
            if not dme.is_hooked() or ctx.slot is None:
                await asyncio.sleep(1)
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
            logger.debug(traceback.format_exc())
            dme.un_hook()
            ctx.dolphin_status = CONNECTION_LOST_STATUS


async def dolphin_sync_task(ctx: SFAContext) -> None:
    """
    Task to manage the connection and synchronization with the Dolphin emulator.

    :param ctx: The Star Fox Adventures context
    """
    logger.info("Starting Dolphin connector. Use /dolphin for status information.")
    sleep_time = 0.0
    while not ctx.exit_event.is_set():
        if sleep_time > 0.0:
            try:
                # ctx.watcher_event gets set when receiving ReceivedItems or LocationInfo, or when shutting down.
                await asyncio.wait_for(ctx.watcher_event.wait(), sleep_time)
            except TimeoutError:
                pass
            sleep_time = 0.0
        ctx.watcher_event.clear()

        try:
            if dme.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if ctx.awaiting_rom:
                    logger.info("Connected to Dolphin")
                    await ctx.server_auth()
                sleep_time = 0.1
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
