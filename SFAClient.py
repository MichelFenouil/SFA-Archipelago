import asyncio
import sys
import traceback
from typing import ClassVar

import dolphin_memory_engine as dme
import Utils
from CommonClient import (
    ClientCommandProcessor,
    ClientStatus,
    get_base_parser,
    gui_enabled,
    logger,
    server_loop,
)
from MultiServer import mark_raw

from .addresses import *  # noqa: F403
from .bit_helper import (
    extract_bitflag_list,
    read_value_bytes,
    set_flag_bit,
    set_on_or_bytes,
    swap_endian,
)
from .game_flags import (
    CONSTANT_FLAGS,
    DINO_CAVE,
    MAGIC_CAVE_ACT_GAMEBIT,
    STARTING_FLAGS,
    TRICKY_FOOD_COUNT,
)
from .game_memory.code_edit import remove_max_bafomdad_check
from .game_memory.hook_handlers import SFAHookHandlers
from .game_memory.loaded_objects import get_player
from .items import (
    FILLER_ITEMS,
    ITEM_INVENTORY,
    ITEM_TRICKY,
    USEFUL_ITEMS,
    SFAItemData,
    SFAItemTags,
    SFALockedConsumableItemData,
    give_item_in_game,
)
from .locations import (
    LOCATION_ANY,
    LOCATION_SHOP,
    LOCATION_UPGRADE,
    NORMAL_TABLES,
    SFALocationData,
    SFALocationTags,
)
from .player_hooks import register_default_special_hooks

TRACKER_LOADED = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext

    TRACKER_LOADED = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext

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
            return give_item_in_game(self.ctx, SFAItemData.get_by_name(name))
        return True

    def _cmd_export_json(self) -> bool:
        """
        Export location and item data to a JSON file.

        This is a utility command for debugging and analysis purposes.
        """
        from .export import export_json as export_main

        export_main()
        logger.info("Exported location and item data to locations-output.json.")
        return True


class SFAContext(SuperContext):
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
    stored_dim_objgroup = 0
    stored_dim2 = 0

    def __init__(self, server_address, password):
        """
        Initialize the Star Fox Adventures context.

        :param server_address: Address of the Archipelago server
        :param password: Password for server authentication
        """
        super().__init__(server_address, password)
        self.send_index: int = 0
        self.syncing = True
        self.awaiting_bridge = False
        self.dolphin_sync_task: asyncio.Task[None] | None = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.tags = {"AP"}
        self.sync_task: asyncio.Task[None] | None = None
        self.hooks = SFAHookHandlers(self)
        register_default_special_hooks(self)

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
        super().on_package(cmd, args)

        if cmd == "Connected":
            self.slot_data = args["slot_data"]
            self.options = self.slot_data["options"]
        return


def sync_player_state(ctx: SFAContext):
    """
    Synchronize the player's state with the current game data.

    :param ctx: The Star Fox Adventures context
    """
    give_item_in_game(ctx, FILLER_ITEMS["Fuel Cell"])
    give_item_in_game(ctx, ITEM_INVENTORY["SHW Alpine Root"])
    give_item_in_game(ctx, ITEM_INVENTORY["Scarab Bag (Progressive)"])
    give_item_in_game(ctx, USEFUL_ITEMS["HP Upgrade"])
    give_item_in_game(ctx, USEFUL_ITEMS["MP Upgrade"])
    give_item_in_game(ctx, ITEM_INVENTORY["White GrubTub"])
    give_item_in_game(ctx, ITEM_INVENTORY["Gate Key"])
    give_item_in_game(ctx, ITEM_INVENTORY["Entrance Bridge Cog"])
    give_item_in_game(ctx, ITEM_INVENTORY["DIM Alpine Root"])
    give_item_in_game(ctx, ITEM_TRICKY["Tricky (Progressive)"])
    give_item_in_game(ctx, ITEM_INVENTORY["Krazoa Spirit 2"])
    give_item_in_game(ctx, ITEM_INVENTORY["Krazoa Spirit 3"])
    give_item_in_game(ctx, ITEM_INVENTORY["Gold Bars"])
    give_item_in_game(ctx, ITEM_INVENTORY["CRF Power Key"])
    give_item_in_game(ctx, ITEM_INVENTORY["CRF Light Gems"])
    give_item_in_game(ctx, ITEM_INVENTORY["CloudRunner Flute"])
    give_item_in_game(ctx, ITEM_INVENTORY["Fire Gem"])


async def sync_full_player_state(ctx: SFAContext):
    """
    Fully synchronize the player's state with the current game data.

    :param ctx: The Star Fox Adventures context
    """
    logger.debug("Syncing full player state")
    received_items = ctx.items_received
    for _, item in enumerate(received_items):
        while not give_item_in_game(ctx, SFAItemData.get_by_id(item.item)):
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

    for location_data in NORMAL_TABLES.values():
        if SFALocationTags.ACTIVE_ZONE not in location_data.tags:
            _check_location_flag(ctx, location_data)

    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if map_value == MAGIC_CAVE_ID and ctx.stored_map == MAGIC_CAVE_ID:
        mc_act = MAGIC_CAVE_ACT_GAMEBIT.get_value()
        mc_flags_bytes = dme.read_word(MAGIC_CAVE_FLAG_ADDRESS)
        mc_flags = extract_bitflag_list(swap_endian(mc_flags_bytes))
        for loc_data in LOCATION_UPGRADE.values():
            if mc_act == MAGIC_CAVE_UPGRADE_ACT and loc_data.mc_bitflag in mc_flags:
                _check_location_flag(ctx, loc_data)

    if map_value == SHOP_ID and ctx.stored_map == SHOP_ID:
        for loc_data in LOCATION_SHOP.values():
            _check_location_flag(ctx, loc_data)

    if ctx.stored_map == COMBAT_SHRINE_ID:
        _check_location_flag(ctx, LOCATION_ANY["MMP: Test of Combat"])
    if ctx.stored_map == FEAR_SHRINE_ID:
        _check_location_flag(ctx, LOCATION_ANY["LFV: Test of Fear"])

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
        ctx.syncing = False
        return

    # Loop through items to give.
    # Give the player all items at an index greater than or equal to the expected index.
    for idx, item in enumerate(received_items[expected_idx:], expected_idx):
        # Attempt to give the item and increment the expected index.
        logger.debug(f"Received item: {item}")
        ctx.received_items_id.append(item.item)
        while not give_item_in_game(ctx, SFAItemData.get_by_id(item.item)):
            await asyncio.sleep(0.01)
        ctx.expected_idx = idx + 1


async def force_gameflags(ctx: SFAContext) -> None:
    """
    Force game flags when starting a save.

    :param ctx: The Star Fox Adventures context
    """
    if ctx.syncing:
        return

    for item in CONSTANT_FLAGS:
        set_flag_bit(item.address, item.offset, item.state)

    if ctx.stored_map == ICE_MOUNTAIN_BOTTOM_ID:
        tricky_item = SFAItemData.get_by_name("Tricky (Progressive)")
        tricky_commands_flag = tricky_item.progressive_data[0]  # type: ignore
        tricky_commands_flag.set_bit(tricky_item.id in ctx.received_items_id)

    if DINO_CAVE.get_bit():
        dino_horn = SFAItemData.get_by_name("Dinosaur Horn")
        dino_horn.set_value(dino_horn.id in ctx.received_items_id)

    if ctx.options["infinite_tricky_food"]:
        TRICKY_FOOD_COUNT.set_value(TRICKY_FOOD_COUNT.max_value)

    # Lock plants
    # 0 = off, 1 = any, -1 = max
    for item in ITEM_INVENTORY.values():
        if isinstance(item, SFALockedConsumableItemData):
            plant_value = 1
            if ctx.options["infinite_consumables"]:
                plant_value = -1
            if ctx.options["plant_shuffle"] and SFAItemTags.SEED in item.tags:
                if item.id not in ctx.received_items_id:
                    plant_value = 0
            item.set_value(plant_value)


async def set_starting_flags(ctx: SFAContext) -> None:
    """Set all GameFlags when starting the game."""
    logger.debug("Set starting flags")
    set_on_or_bytes(ITEM_MAP_ADDRESS, ITEM_MAP_INIT_VALUE, 3)
    set_on_or_bytes(SKIP_TUTO_ADDRESS, SKIP_TUTO_VALUE, 2)
    for item in STARTING_FLAGS:
        item.set_bit(item.state)
    remove_max_bafomdad_check()
    await sync_full_player_state(ctx)


async def player_hooks_watcher(ctx: SFAContext) -> None:
    """
    Handle special map flags for certain locations.

    :param ctx: The Star Fox Adventures context
    """
    map_value = dme.read_byte(MAP_ID_ADDRESS)
    if ctx.stored_map != map_value:
        if ctx.stored_map == MAIN_MENU_ID:
            await set_starting_flags(ctx)
        logger.debug(f"Entering map {map_value:x}")
        await ctx.hooks.run_map_transition(map_value, ctx.stored_map)
        ctx.stored_map = map_value

    if map_value == DARKICE_TOP_ID:
        dim_obj_value = read_value_bytes(DIM_OBJGROUP_ADDRESS, 0, 32, 4)
        if dim_obj_value != ctx.stored_dim_objgroup:
            logger.debug(f"Entering dim zone objgroups {dim_obj_value:x}")
            await ctx.hooks.run_zone_transition(dim_obj_value, ctx.stored_dim_objgroup, map_value)
            ctx.stored_dim_objgroup = dim_obj_value

    player = get_player()
    await ctx.hooks.update_player_coord_transitions(
        player.position.pos.x,
        player.position.pos.y,
        player.position.pos.z,
        map_value,
    )


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
            await player_hooks_watcher(ctx)

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

        if TRACKER_LOADED:
            ctx.run_generator()
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
