from dataclasses import dataclass

T0_ADDRESS = 0x803A4198
T1_ADDRESS = 0x803A380C
T2_ADDRESS = 0x803A32CC
T3_ADDRESS = 0x803A3880

MAP_ID_ADDRESS = 0x803DCECB

MAP_SHOP_NO = 0x33

MAP_ICE_MOUNTAIN = 0x17
ICE_MOUNTAIN_ACT_OFFSET = 0x02FA

MAP_MAGIC_CAVE_NO = 0x36
MAGIC_CAVE_ACT_ADDRESS = 0x803A3871
MAGIC_CAVE_FLAG_ADDRESS = 0x803A3905
MAGIC_CAVE_UPGRADE_ACT = 0x2
MAGIC_CAVE_MANA_ACT = 0x1

ITEM_MAP_ADDRESS = 0x803A33D2
ITEM_MAP_INIT_VALUE = 0b111111001010001000101111

SKIP_TUTO_ADDRESS = 0x803A32DC
SKIP_TUTO_VALUE = 0b1111111100111100

PLAYER_MAX_HP = 0x803A32B5
PLAYER_CUR_HP = 0x803A32B4
PLAYER_MAX_MP = 0x803A32BB
PLAYER_CUR_MP = 0x803A32B9


@dataclass
class GameFlag:
    """GameFlag represents flags to set ON/OFF for QoL."""

    flag_name: str
    bit_offset: int
    table_address: int


FORCE_TRICKY = GameFlag("Spawn Tricky", 0x0847, T2_ADDRESS)
FORCE_TRICKY_CALL = GameFlag("Give Call", 0x0849, T2_ADDRESS)

SAW_ITEM_FLAGS: list[GameFlag] = [
    GameFlag("Saw Apple", 0x0015, T2_ADDRESS),
    GameFlag("Saw Bafomdad", 0x0020, T2_ADDRESS),
    GameFlag("Saw BarrelGen", 0x001D, T2_ADDRESS),
    GameFlag("Saw BigHealth", 0x0014, T2_ADDRESS),
    GameFlag("Saw BombPlant", 0x001F, T2_ADDRESS),
    GameFlag("Saw BombPlantPatch", 0x001E, T2_ADDRESS),
    GameFlag("Saw BombSpore", 0x0853, T2_ADDRESS),
    GameFlag("Saw CMenuExplanation", 0x001B, T2_ADDRESS),
    GameFlag("Saw FuelCell", 0x0854, T2_ADDRESS),
    GameFlag("Saw LifeDoorExplanation", 0x0024, T2_ADDRESS),
    GameFlag("Saw Magic", 0x0013, T2_ADDRESS),
    GameFlag("Saw Scarab", 0x0016, T2_ADDRESS),
    GameFlag("Saw StaffBoostPad", 0x0022, T2_ADDRESS),
    GameFlag("Saw WarpPad", 0x0018, T2_ADDRESS),
    GameFlag("Saw GrubTubs", 0x084F, T2_ADDRESS),
    GameFlag("Saw Alpine Root", 0x0851, T2_ADDRESS),
    GameFlag("Entered Shop", 0x035A, T2_ADDRESS),
    GameFlag("Saw Pushable Block", 0x0019, T2_ADDRESS),
    GameFlag("GrubTub Tutorial 1", 0x0345, T2_ADDRESS),
    GameFlag("GrubTub Tutorial 2", 0x0346, T2_ADDRESS),
    GameFlag("GrubTub Tutorial 3", 0x0347, T2_ADDRESS),
    GameFlag("Slippy Cold Water", 0x001C, T2_ADDRESS),
    GameFlag("Saw Firefly", 0x0021, T2_ADDRESS),
    GameFlag("Saw White GrubTubs", 0x0850, T2_ADDRESS),
    GameFlag("Saw Last Tutorial Message", 0x0104, T2_ADDRESS),  # Also spawns Queen Cave correctly
    GameFlag("Learned To Speak", 0x001A, T2_ADDRESS),
]

SH_STATE_FLAGS: list[GameFlag] = [
    GameFlag("SH WarpStone Open", 0x00D5, T2_ADDRESS),
]

IM_OPENED_FLAGS: list[GameFlag] = [
    GameFlag("IM Lava Path Open", 0x0341, T2_ADDRESS),
    GameFlag("IM Dig Tunnel to Waterspout", 0x0344, T2_ADDRESS),
    GameFlag("SW Geyser Stop", 0x0036, T2_ADDRESS),
    GameFlag("SW Ice Block Spawn", 0x0067, T2_ADDRESS),
    GameFlag("SW Bribed Guard", 0x0039, T2_ADDRESS),
]

INTRO_OPENED_FLAGS: list[GameFlag] = [
    GameFlag("Enable C Menu", 0x0356, T1_ADDRESS),
    GameFlag("Gold Key Got", 0x01DC, T1_ADDRESS),
    GameFlag("Gold Key Used", 0x4FB, T2_ADDRESS),
    GameFlag("Skip landing cutscene", 0x04FA, T2_ADDRESS),
    GameFlag("Destroyed Wall 1", 0x0502, T2_ADDRESS),
    GameFlag("Destroyed Wall 2", 0x0504, T2_ADDRESS),
    GameFlag("Switch Door Open", 0x050D, T2_ADDRESS),
    GameFlag("Dino Talked After Test", 0x0508, T2_ADDRESS),
    GameFlag("Spirit Got", 0x053C, T2_ADDRESS),
]

CUTSCENE_SKIP_FLAGS: list[GameFlag] = [
    GameFlag("SH Warpstone explanation", 0x0106, T2_ADDRESS),
    GameFlag("SH Entered Well", 0x0096, T2_ADDRESS),
    GameFlag("SH Returned with Tricky", 0x0093, T2_ADDRESS),
    GameFlag("IM Skip Tricky captured", 0x0310, T2_ADDRESS),
    GameFlag("IM Skip Hut bullying", 0x0312, T2_ADDRESS),
    GameFlag("IM Skip Starting first race", 0x0314, T2_ADDRESS),
    GameFlag("IM Spawn Tricky on bottom", 0x0325, T2_ADDRESS),
    GameFlag("IM Open Hut Door", 0x0323, T2_ADDRESS),
]

STARTING_ON_FLAGS: list[GameFlag] = [
    *SAW_ITEM_FLAGS,
    *CUTSCENE_SKIP_FLAGS,
    *SH_STATE_FLAGS,
    *IM_OPENED_FLAGS,
    *INTRO_OPENED_FLAGS,
]

CONSTANT_ON_FLAGS: list[GameFlag] = [
    FORCE_TRICKY,
    FORCE_TRICKY_CALL,
]

OFF_FLAGS: list[GameFlag] = [
    GameFlag("MagicCaveDoorOpen", 0x0008, T2_ADDRESS),
    GameFlag("MagicCaveDoorRelated", 0x0009, T2_ADDRESS),
]
