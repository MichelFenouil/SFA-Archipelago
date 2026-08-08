from .addresses import MMP_OBJGROUP_ADDRESS, T0_ADDRESS, T1_ADDRESS, T3_ADDRESS
from .bit_helper import GameBit, GameFlag

## Dynamic flags ##

MAGIC_CAVE_ACT_GAMEBIT = GameBit(0x2, 0x803A3871, bit_size=4)
MAGIC_CAVE_FLAG_ADDRESS = 0x803A3905

CC_ACT_GAMEBIT = GameBit(0x072A, bit_size=4)
CC_OBJGROUP_VALUE = GameBit(0x00E8, T3_ADDRESS, bit_size=32)

OFP_ACT_GAMEBIT = GameBit(0x0326, T1_ADDRESS, bit_size=4)
LFV_ACT_GAMEBIT = GameBit(0x02E6, T1_ADDRESS, bit_size=4)
KP_ACT_GAMEBIT = GameBit(0x02DA, T1_ADDRESS, bit_size=4)
KP_OBJGROUP_VALUE = GameBit(0x0148, T3_ADDRESS, bit_size=32)

KRAZOA_SPIRIT_1 = GameFlag(0x053C)
DIM_OPEN_BLIZZARD = [
    GameFlag(0x03B3),  # Allow horn interaction
    GameFlag(0x0104, T0_ADDRESS),  # Blow horn cutscene 1
    GameFlag(0x010F, T0_ADDRESS),  # Blow horn cutscene 2
    GameFlag(0x03A1),  # SnowHorn cutscene 1
    GameFlag(0x03B2),  # SnowHorn cutscene 2
]
DIM_OPEN_BIKE = [
    GameFlag(0x0415),  # Bike Trigger
    GameFlag(0x03E1),  # Prevent Crash 1FB
    GameFlag(0x03D9),  # Bike 1F0
]
DINO_CAVE = GameFlag(0x003E, T3_ADDRESS)  # Dino horn cave detection
KRAZOA_STATUE_2 = GameFlag(0x0525)  # Krazoa Statue 2 interaction
CRF_ENTRANCE_RACE = GameFlag(0x02F9)  # CloudRunner Fortress race and cutscene
CRF_PRISON_WIND = GameFlag(0x02B1)  # Prison wind draft direction (ON = Down, OFF = Up)
CRF_QUEEN_CHILDREN_CHECK = GameFlag(0x0298)
CRF_QUEEN_BROKEN_PILLAR = GameFlag(0x030C)  # Queen's broken pillar cutscene
CRF_OPEN_BACK_PATH = [
    GameFlag(0x008F, T1_ADDRESS, True),
    GameFlag(0x0045, T1_ADDRESS, False),
    GameFlag(0x0035, T1_ADDRESS, False),
]
CRF_OPEN_POST_BOSS = [
    GameFlag(0x0130, T1_ADDRESS, False),
    GameFlag(0x012D, T1_ADDRESS, False),
]
LFV_GATE = GameFlag(0x017F)  # LFV Gate open

TRICKY_FOOD_COUNT = GameBit(0x0, 0x803A32C0, bit_size=8, max_value=20)

## Global static flags ##

FORCE_TRICKY = GameFlag(0x0847)  # Spawn Tricky
FORCE_TRICKY_CALL = GameFlag(0x0849)  # Give Tricky call command

TTH_WELL_OPEN = [GameFlag(0x00A1), GameFlag(0x00A2)]  # Open access to TTH Well without Lantern

SAW_ITEM_FLAGS: list[GameFlag] = [
    GameFlag(0x0015),  # Saw Apple
    GameFlag(0x0020),  # Saw Bafomdad
    GameFlag(0x001D),  # Saw BarrelGen
    GameFlag(0x0014),  # Saw BigHealth
    GameFlag(0x001F),  # Saw BombPlant
    GameFlag(0x001E),  # Saw BombPlantPatch
    GameFlag(0x0853),  # Saw BombSpore
    GameFlag(0x001B),  # Saw CMenuExplanation
    GameFlag(0x0854),  # Saw FuelCell
    GameFlag(0x0024),  # Saw LifeDoorExplanation
    GameFlag(0x0013),  # Saw Magic
    GameFlag(0x0016),  # Saw Scarab
    GameFlag(0x0022),  # Saw StaffBoostPad
    GameFlag(0x0018),  # Saw WarpPad
    GameFlag(0x084F),  # Saw GrubTubs
    GameFlag(0x0851),  # Saw Alpine Root
    GameFlag(0x035A),  # Entered Shop
    GameFlag(0x0019),  # Saw Pushable Block
    GameFlag(0x0345),  # GrubTub Tutorial 1
    GameFlag(0x0346),  # GrubTub Tutorial 2
    GameFlag(0x0347),  # GrubTub Tutorial 3
    GameFlag(0x001C),  # Slippy Cold Water
    GameFlag(0x0021),  # Saw Firefly
    GameFlag(0x0850),  # Saw White GrubTubs
    GameFlag(0x0104),  # Saw Last Tutorial Message, Also spawns Queen Cave correctly
    GameFlag(0x001A),  # Learned To Speak
    GameFlag(0x01FD),  # Saw MoonSeed
]

SH_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x00D5),  # TTH Warpstone path open
]

IM_OPENED_FLAGS: list[GameFlag] = [
    GameFlag(0x0341),  # IM Lava Path Open
    GameFlag(0x0344),  # IM Dig Tunnel to Waterspout
    GameFlag(0x0036),  # SW Geyser Stop
    GameFlag(0x0067),  # SW Ice Block Spawn
    GameFlag(0x0039),  # SW Bribed Guard
]

INTRO_OPENED_FLAGS: list[GameFlag] = [
    GameFlag(0x0356, T1_ADDRESS),  # Enable C Menu
    GameFlag(0x01DC, T1_ADDRESS),  # Gold Key Got
    GameFlag(0x04FB),  # Gold Key Used
    GameFlag(0x04FA),  # Skip landing cutscene
    GameFlag(0x0502),  # Destroyed Wall 1
    GameFlag(0x0504),  # Destroyed Wall 2
    GameFlag(0x050D),  # Switch Door Open
    GameFlag(0x0508),  # Dino Talked After Test
]

DIM_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x03ED),  # Belina Te at Bottom
]

MMP_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x01D0),  # Skip Krazoa Intro
    GameFlag(0x0218),  # Open Door to Quake Upgrade
    GameFlag(0x01CF),  # Skip Krazoa Combat Cutscene
    GameFlag(11, MMP_OBJGROUP_ADDRESS),  # MMP wind after warps
    GameFlag(0x01C7),  # Skip Barrels Cutscene
]

VFP_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x0583),  # Skip Peppy Cutscene
]

CC_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x0229),  # Skip Cape Claw entrance Cutscene
    GameFlag(0x0241),  # Activate HighTop Quest
]

CRF_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x02FA),  # Entrance Platform cutscene
    GameFlag(0x0115, T1_ADDRESS),  # Entrance Ring on target
    GameFlag(0x0299),  # Prison Guard Left
    GameFlag(0x0297),  # Explode Ceiling Cutscene
    GameFlag(0x0093, T1_ADDRESS),  # Guard Cutscene post Power Key
]

LFV_STATE_FLAGS: list[GameFlag] = [
    GameFlag(0x0178),  # Tests done skip cutscene
    GameFlag(0x0177),  # Tests done trigger
    GameFlag(0x01A7),  # Tricky cutscene skip
    GameFlag(0x010E),  # Chief tests cutscene skip
    GameFlag(0x0181),  # Underground door open
    GameFlag(0x01BD),  # Hut Door open
    GameFlag(0x01B3),  # Booster enabled
    GameFlag(0x019B),  # Triangle block used
    GameFlag(0x018D),  # Square block used
    GameFlag(0x0194),  # Circle block used
]

CUTSCENE_SKIP_FLAGS: list[GameFlag] = [
    GameFlag(0x0106),  # SH Warpstone explanation
    GameFlag(0x0096),  # SH Entered Well
    GameFlag(0x0093),  # SH Returned with Tricky
    GameFlag(0x0310),  # IM Skip Tricky captured
    GameFlag(0x0312),  # IM Skip Hut bullying
    GameFlag(0x0314),  # IM Skip Starting first race
    GameFlag(0x0325),  # IM Spawn Tricky on bottom
    GameFlag(0x0323),  # IM Open Hut Door
    GameFlag(0x0528),  # KP Skip First Cutscene
    GameFlag(0x09EC),  # KP Skip Krystal Cutscene
]

STARTING_FLAGS: list[GameFlag] = [
    *SAW_ITEM_FLAGS,
    *CUTSCENE_SKIP_FLAGS,
    *SH_STATE_FLAGS,
    *IM_OPENED_FLAGS,
    *INTRO_OPENED_FLAGS,
    *DIM_STATE_FLAGS,
    *MMP_STATE_FLAGS,
    *VFP_STATE_FLAGS,
    *CC_STATE_FLAGS,
    *CRF_STATE_FLAGS,
    *TTH_WELL_OPEN,
    *LFV_STATE_FLAGS,
]

CONSTANT_FLAGS: list[GameFlag] = [
    FORCE_TRICKY,
    FORCE_TRICKY_CALL,
    GameFlag(0x0008, state=False),  # MagicCaveDoorOpen
    GameFlag(0x0009, state=False),  # MagicCaveDoorRelated
    GameFlag(0x0138, T1_ADDRESS, False),  # DIM Landing Pad Gate Open
]
