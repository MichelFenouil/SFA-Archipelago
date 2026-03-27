from .addresses import T0_ADDRESS, T1_ADDRESS, T2_ADDRESS, T3_ADDRESS
from .bit_helper import GameBit, GameFlag

## Dynamic flags ##

MAGIC_CAVE_ACT_GAMEBIT = GameBit(0x2, 0x803A3871, bit_size=4)
MAGIC_CAVE_FLAG_ADDRESS = 0x803A3905

KRAZOA_SPIRIT_1 = GameFlag(0x053C, T2_ADDRESS)
DIM_OPEN_BLIZZARD = [
    GameFlag(0x03B3, T2_ADDRESS), # Allow horn interaction
    GameFlag(0x0104, T0_ADDRESS), # Blow horn cutscene 1
    GameFlag(0x010F, T0_ADDRESS), # Blow horn cutscene 2
    GameFlag(0x03A1, T2_ADDRESS), # SnowHorn cutscene 1
    GameFlag(0x03B2, T2_ADDRESS), # SnowHorn cutscene 2
]
DIM_OPEN_BIKE = [
    GameFlag(0x0415, T2_ADDRESS), # Bike Trigger
    GameFlag(0x03E1, T2_ADDRESS), # Prevent Crash 1FB
    GameFlag(0x03D9, T2_ADDRESS), # Bike 1F0
]
DINO_CAVE = GameFlag(0x003E, T3_ADDRESS) # Dino horn cave detection


## Global static flags ##

FORCE_TRICKY = GameFlag(0x0847, T2_ADDRESS) # Spawn Tricky
FORCE_TRICKY_CALL = GameFlag(0x0849, T2_ADDRESS) # Give Tricky call command

SAW_ITEM_FLAGS: list[GameFlag] = [
    GameFlag(0x0015, T2_ADDRESS), # Saw Apple
    GameFlag(0x0020, T2_ADDRESS), # Saw Bafomdad
    GameFlag(0x001D, T2_ADDRESS), # Saw BarrelGen
    GameFlag(0x0014, T2_ADDRESS), # Saw BigHealth
    GameFlag(0x001F, T2_ADDRESS), # Saw BombPlant
    GameFlag(0x001E, T2_ADDRESS), # Saw BombPlantPatch
    GameFlag(0x0853, T2_ADDRESS), # Saw BombSpore
    GameFlag(0x001B, T2_ADDRESS), # Saw CMenuExplanation
    GameFlag(0x0854, T2_ADDRESS), # Saw FuelCell
    GameFlag(0x0024, T2_ADDRESS), # Saw LifeDoorExplanation
    GameFlag(0x0013, T2_ADDRESS), # Saw Magic
    GameFlag(0x0016, T2_ADDRESS), # Saw Scarab
    GameFlag(0x0022, T2_ADDRESS), # Saw StaffBoostPad
    GameFlag(0x0018, T2_ADDRESS), # Saw WarpPad
    GameFlag(0x084F, T2_ADDRESS), # Saw GrubTubs
    GameFlag(0x0851, T2_ADDRESS), # Saw Alpine Root
    GameFlag(0x035A, T2_ADDRESS), # Entered Shop
    GameFlag(0x0019, T2_ADDRESS), # Saw Pushable Block
    GameFlag(0x0345, T2_ADDRESS), # GrubTub Tutorial 1
    GameFlag(0x0346, T2_ADDRESS), # GrubTub Tutorial 2
    GameFlag(0x0347, T2_ADDRESS), # GrubTub Tutorial 3
    GameFlag(0x001C, T2_ADDRESS), # Slippy Cold Water
    GameFlag(0x0021, T2_ADDRESS), # Saw Firefly
    GameFlag(0x0850, T2_ADDRESS), # Saw White GrubTubs
    GameFlag(0x0104, T2_ADDRESS), # Saw Last Tutorial Message, Also spawns Queen Cave correctly
    GameFlag(0x001A, T2_ADDRESS), # Learned To Speak
]

SH_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x00D5, T2_ADDRESS), # TTH Warpstone path open 
]

IM_OPENED_FLAGS: list[GameFlag] = [
    GameFlag(0x0341, T2_ADDRESS), # IM Lava Path Open
    GameFlag(0x0344, T2_ADDRESS), # IM Dig Tunnel to Waterspout
    GameFlag(0x0036, T2_ADDRESS), # SW Geyser Stop
    GameFlag(0x0067, T2_ADDRESS), # SW Ice Block Spawn
    GameFlag(0x0039, T2_ADDRESS), # SW Bribed Guard
]

INTRO_OPENED_FLAGS: list[GameFlag] = [
    GameFlag(0x0356, T1_ADDRESS), # Enable C Menu
    GameFlag(0x01DC, T1_ADDRESS), # Gold Key Got
    GameFlag(0x04FB, T2_ADDRESS), # Gold Key Used
    GameFlag(0x04FA, T2_ADDRESS), # Skip landing cutscene
    GameFlag(0x0502, T2_ADDRESS), # Destroyed Wall 1
    GameFlag(0x0504, T2_ADDRESS), # Destroyed Wall 2
    GameFlag(0x050D, T2_ADDRESS), # Switch Door Open
    GameFlag(0x0508, T2_ADDRESS), # Dino Talked After Test
]

DIM_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x03ED, T2_ADDRESS, True), # Belina Te at Bottom
]

CUTSCENE_SKIP_FLAGS: list[GameFlag] = [
    GameFlag(0x0106, T2_ADDRESS), # SH Warpstone explanation
    GameFlag(0x0096, T2_ADDRESS), # SH Entered Well
    GameFlag(0x0093, T2_ADDRESS), # SH Returned with Tricky
    GameFlag(0x0310, T2_ADDRESS), # IM Skip Tricky captured
    GameFlag(0x0312, T2_ADDRESS), # IM Skip Hut bullying
    GameFlag(0x0314, T2_ADDRESS), # IM Skip Starting first race
    GameFlag(0x0325, T2_ADDRESS), # IM Spawn Tricky on bottom
    GameFlag(0x0323, T2_ADDRESS), # IM Open Hut Door
]

STARTING_FLAGS: list[GameFlag] = [
    *SAW_ITEM_FLAGS,
    *CUTSCENE_SKIP_FLAGS,
    *SH_STATE_FLAGS,
    *IM_OPENED_FLAGS,
    *INTRO_OPENED_FLAGS,
    *DIM_STATE_FLAGS,
]

CONSTANT_FLAGS: list[GameFlag] = [
    FORCE_TRICKY,
    FORCE_TRICKY_CALL,
    GameFlag(0x0008, T2_ADDRESS, False), # MagicCaveDoorOpen
    GameFlag(0x0009, T2_ADDRESS, False), # MagicCaveDoorRelated
    GameFlag(0x0138, T1_ADDRESS, False), # DIM Landing Pad Gate Open
]
