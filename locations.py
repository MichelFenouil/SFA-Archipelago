from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from BaseClasses import ItemClassification, Location
from rule_builder.rules import Has, HasAllCounts, Rule, True_

from .addresses import T0_ADDRESS
from .bit_helper import GameBit
from .items import SFAItem
from .macros import CanBuy, can_explode_bomb_plant, has_blaster, has_staff_booster, can_grow_moon_seed
from .regions import SFARegion

if TYPE_CHECKING:
    from .world import SFAWorld


class SFALocation(Location):
    """Location class for Star Fox Adventures."""

    game: str = "Star Fox Adventures"


class SFALocationTags(Enum):
    """This class defines constants for various types of locations in Star Fox Adventures."""

    MAP = auto()
    ACTIVE_ZONE = auto()
    CUTSCENE = auto()  # Not yet used


@dataclass
class SFALocationData:
    """Data class for locations in Star Fox Adventures."""

    id: int
    game_bit: GameBit
    region: SFARegion
    rule: Rule[SFAWorld]
    tags: list[SFALocationTags] = field(default_factory=lambda: [])

    def is_checked(self) -> bool:
        """Get bool value if checked in game."""
        return self.game_bit.get_bit()

    def get_bit(self) -> bool:
        """Get bit value for item."""
        return self.game_bit.get_bit()

    def set_bit(self, state: bool) -> None:
        """Set bit for item."""
        self.game_bit.set_bit(state)


@dataclass
class SFAUpgradeLocationData(SFALocationData):
    """Data class for magic cave upgrade locations."""

    linked_item: int = 0
    mc_bitflag: int = 0


@dataclass
class SFAShopLocationData(SFALocationData):
    """Data class for shop locations."""

    linked_item: int = 0
    cost: int = 0


@dataclass
class SFACountLocationData(SFALocationData):
    """Data class for count locations."""

    count: int = 1

    def is_checked(self):
        """Get bool value if checked in game."""
        value = self.game_bit.get_value()
        return value >= self.count


def locations_name_to_id_dict() -> dict[str, int]:
    """Name to id dict for Star Fox Adventures locations."""
    return {name: data.id for name, data in LOCATION_TABLE.items()}


def create_regular_locations(world: SFAWorld) -> None:
    """Create locations for AP world."""
    for loc_name, loc_data in LOCATION_TABLE.items():
        if world.options.shop_locations == "nothing" and loc_data in LOCATION_SHOP.values():
            continue
        if world.options.shop_locations == "no_map" and SFALocationTags.MAP in loc_data.tags:
            continue

        region = world.get_region(loc_data.region.value)
        sfa_location = SFALocation(world.player, loc_name, loc_data.id, region)
        if loc_name == "DIM: Defeat Boss Galdon":
            sfa_location.place_locked_item(SFAItem("Victory", ItemClassification.progression, 2000, world.player))
        region.locations.append(sfa_location)
        world.progress_locations.add(loc_name)
        world.set_rule(sfa_location, loc_data.rule)


def create_events(world: SFAWorld) -> None:
    """Create events for AP world."""
    # darkice_mines = world.get_region(SFARegion.DIM_BOTTOM.value)
    # darkice_mines.add_event(
    #     "Defeated Boss Galdon",
    #     "Victory",
    #     location_type=SFALocation,
    #     item_type=SFAItem,
    #     rule=lambda state: has_blaster(state, world.player) and state.has("Tricky (Progressive)", world.player, 2)
    # )


def create_all_locations(world: SFAWorld) -> None:
    """Generate all locations for the world."""
    create_regular_locations(world)
    create_events(world)


LOCATION_UPGRADE: dict[str, SFAUpgradeLocationData] = {
    "TTH: Fire Blaster Upgrade": SFAUpgradeLocationData(
        1, GameBit(0x06FC), SFARegion.TH, True_(), linked_item=2, mc_bitflag=0
    ),
    "TTH Well: Staff Booster Upgrade": SFAUpgradeLocationData(
        2, GameBit(0x0706), SFARegion.TH_WELL, can_explode_bomb_plant, linked_item=3, mc_bitflag=1
    ),
    "VFP: Freeze Blast Upgrade": SFAUpgradeLocationData(
        3, GameBit(0x0703), SFARegion.VFP_PAST_BRIDGE, has_blaster & Has("Fire SpellStone 1") & Has("Tricky (Progressive)", 2), linked_item=4, mc_bitflag=8
    ),
    "MMP: Ground Quake Upgrade": SFAUpgradeLocationData(
        4, GameBit(0x06FE), SFARegion.MMP, Has("Moon Pass Key"), linked_item=5, mc_bitflag=0x10 # Change just read value
    ),
}

LOCATION_SHOP: dict[str, SFAShopLocationData] = {
    "TTH Store: Rock Candy": SFAShopLocationData(
        200, GameBit(0x035F), SFARegion.TH, CanBuy(10), linked_item=200, cost=10
    ),
    "TTH Store: Hi-Tech Display Device": SFAShopLocationData(
        201, GameBit(0x035E), SFARegion.TH, CanBuy(20), linked_item=201, cost=20
    ),
    "TTH Store: Tricky Ball": SFAShopLocationData(
        202, GameBit(0x084C), SFARegion.TH, CanBuy(15), linked_item=202, cost=15
    ),
    "TTH Store: BafomDad Holder": SFAShopLocationData(
        203, GameBit(0x09EE), SFARegion.TH, CanBuy(20), linked_item=203, cost=20
    ),
    "TTH Store: FireFly Lantern": SFAShopLocationData(
        204, GameBit(0x0717), SFARegion.TH, CanBuy(20), linked_item=204, cost=20
    ),
    "TTH Store: Snowhorn Artifact": SFAShopLocationData(
        205, GameBit(0x0060), SFARegion.TH, CanBuy(130), linked_item=205, cost=130
    ),
    "TTH Store: Map Cape Claw": SFAShopLocationData(
        210, GameBit(0x0841), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map Ocean Force Point": SFAShopLocationData(
        211, GameBit(0x083F), SFARegion.TH, CanBuy(10), [SFALocationTags.MAP], cost=10
    ),
    "TTH Store: Map Krazoa Palace": SFAShopLocationData(
        212, GameBit(0x083D), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map Dragon Rock": SFAShopLocationData(
        213, GameBit(0x0839), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map ThornTail Hollow": SFAShopLocationData(
        214, GameBit(0x0837), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map Moon Pass": SFAShopLocationData(
        215, GameBit(0x0845), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map LightFoot Village": SFAShopLocationData(
        216, GameBit(0x0836), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map DarkIce Mines": SFAShopLocationData(
        217, GameBit(0x0833), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map CloudRunner Fortress": SFAShopLocationData(
        218, GameBit(0x0835), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map Walled City": SFAShopLocationData(
        219, GameBit(0x0840), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map SnowHorn Wastes": SFAShopLocationData(
        220, GameBit(0x0834), SFARegion.TH, CanBuy(5), [SFALocationTags.MAP], cost=5
    ),
    "TTH Store: Map Volcano Force Point": SFAShopLocationData(
        221, GameBit(0x0832), SFARegion.TH, CanBuy(10), [SFALocationTags.MAP], cost=10
    ),
}

LOCATION_ANY: dict[str, SFALocationData] = {
    "SHW: Magic Upgrade": SFALocationData(
        20, GameBit(0x0010), SFARegion.SW_WATERSPOUT, Has("Tricky (Progressive)")
    ),
    "SHW: Feed Alpine Root 1": SFACountLocationData(
        21, GameBit(0x0033, bit_size=3), SFARegion.SW_WATERSPOUT, Has("SHW Alpine Root", 1), count=1
    ),
    "SHW: Feed Alpine Root 2": SFACountLocationData(
        22, GameBit(0x0033, bit_size=3), SFARegion.SW_WATERSPOUT, Has("SHW Alpine Root", 2), count=2
    ),
    "SHW: Rescue GateKeeper": SFALocationData(23, GameBit(0x0058), SFARegion.SW_ENTRANCE, True_()),
    "TTH Well: White GrubTub 1": SFALocationData(24, GameBit(0x00A8), SFARegion.TH_WELL_BOTTOM, True_()),
    "TTH Well: White GrubTub 2": SFALocationData(25, GameBit(0x00A7), SFARegion.TH_WELL_BOTTOM, True_()),
    "TTH Well: White GrubTub 3": SFALocationData(
        26, GameBit(0x00A5), SFARegion.TH_WELL_BOTTOM, can_explode_bomb_plant
    ),
    "TTH Well: White GrubTub 4": SFALocationData(
        27, GameBit(0x00A3), SFARegion.TH_WELL_BOTTOM, has_staff_booster
    ),
    "TTH Well: White GrubTub 5": SFALocationData(
        28,
        GameBit(0x00A4),
        SFARegion.TH_WELL_BOTTOM,
        has_staff_booster & can_explode_bomb_plant,
    ),
    "TTH Well: White GrubTub 6": SFALocationData(
        29,
        GameBit(0x00A6),
        SFARegion.TH_WELL_BOTTOM,
        has_staff_booster & can_explode_bomb_plant,
    ),
    "TTH: Magic Upgrade above Store": SFALocationData(
        30,
        GameBit(0x0011),
        SFARegion.TH,
        has_staff_booster & has_blaster & can_explode_bomb_plant,
    ),
    "TTH: Feed Queen White GrubTubs": SFACountLocationData(
        31, GameBit(0x00AD, bit_size=3), SFARegion.TH, Has("White GrubTub", 6), count=6
    ),
    "DIM: Release Entrance SnowHorn": SFALocationData(
        32, GameBit(0x0366), SFARegion.DIM_ENTRANCE, Has("Tricky (Progressive)")
    ),
    "DIM: Rescue Injured SnowHorn": SFALocationData(
        33, GameBit(0x036B), SFARegion.DIM_ENTRANCE, Has("Entrance Bridge Cog")
    ),
    "DIM: Feed Injured SnowHorn": SFALocationData(
        34,
        GameBit(0x036D),
        SFARegion.DIM_ENTRANCE,
        HasAllCounts({"Entrance Bridge Cog": 1, "DIM Alpine Root": 2}),
    ),
    "DIM: Enemy Gate Cog Chest": SFALocationData(
        35, GameBit(0x0370), SFARegion.DIM_FORT, has_staff_booster
    ),
    "DIM: Hut Cog Chest": SFALocationData(36, GameBit(0x0372), SFARegion.DIM_FORT, has_staff_booster),
    "DIM: Ice Cog Chest": SFALocationData(
        37,
        GameBit(0x0374),
        SFARegion.DIM_FORT,
        has_staff_booster & Has("Tricky (Progressive)", 2),
    ),
    "DIM: Fire Puzzle Reward": SFALocationData(
        38,
        GameBit(0x03BC),
        SFARegion.DIM_FORT,
        has_blaster & HasAllCounts({"SharpClaw Fort Bridge Cogs": 3, "Tricky (Progressive)": 2}),
    ),
    # "DIM: Get Silver Key": SFALinkedLocationData(
    #     39,
    #     0x03DC,
    #     T2_ADDRESS,
    #     SFALocationType.FLAG,
    #     SFARegion.DIM_BOTTOM,
    #     linked_item=111,
    #     map_address=0x803A3891,
    #     map_bit_size=4,
    #     map_value=0x40042,
    #     has_staff_booster(state, world.player) and has_blaster(state, world.player),
    # ),
    "DIM: Defeat Boss Galdon": SFALocationData(
        40,
        GameBit(0x0120, T0_ADDRESS),
        SFARegion.DIM_BOTTOM,
        has_blaster & Has("Tricky (Progressive)", 2),
    ),
    "VFP: Insert Fire SpellStone 1": SFALocationData(
        41, GameBit(0x0573), SFARegion.VFP_PAST_PUZZLE, has_blaster & Has("Tricky (Progressive)", 2) & Has("Fire SpellStone 1") & Has("Freeze Blast")
    ),
    "MMP: Test of Combat": SFALocationData(
        42, GameBit(0x0537), SFARegion.MMP_METEORITE, Has("Freeze Blast") & Has("Tricky (Progressive)", 2), [SFALocationTags.ACTIVE_ZONE]
    ),
}

# Last id = 138
LOCATION_FUEL_CELL: dict[str, SFALocationData] = {
    ## ThornTail Hollow
    "TTH: Queen Cave Fuel Cell": SFALocationData(100, GameBit(0x0945), SFARegion.TH, True_()),
    "TTH: Pillar Fuel Cell Left": SFALocationData(101, GameBit(0x0946), SFARegion.TH, True_()),
    "TTH: Pillar Fuel Cell Right": SFALocationData(102, GameBit(0x0943), SFARegion.TH, True_()),
    "TTH: Beside WarpStone Fuel Cell Left": SFALocationData(
        103, GameBit(0x0947), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: Beside WarpStone Fuel Cell Right": SFALocationData(
        104, GameBit(0x0949), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: Waterfall Cave Fuel Cell Center": SFALocationData(
        105, GameBit(0x094E), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: Waterfall Cave Fuel Cell Left": SFALocationData(
        106, GameBit(0x094C), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: Waterfall Cave Fuel Cell Right": SFALocationData(
        107, GameBit(0x0950), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: Waterfall Cave Fuel Cell Back": SFALocationData(
        108, GameBit(0x0948), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: South Cave Fuel Cell Center": SFALocationData(
        109, GameBit(0x0944), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: South Cave Fuel Cell Right": SFALocationData(
        110, GameBit(0x0942), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: South Cave Fuel Cell Left": SFALocationData(
        111, GameBit(0x0941), SFARegion.TH, can_explode_bomb_plant
    ),
    "TTH: Above Store Fuel Cell Left": SFALocationData(
        112, GameBit(0x094F), SFARegion.TH, has_staff_booster
    ),
    "TTH: Above Store Fuel Cell Right": SFALocationData(
        113, GameBit(0x094D), SFARegion.TH, has_staff_booster
    ),
    "TTH Well: Fuel Cell Left": SFALocationData(128, GameBit(0x095D), SFARegion.TH_WELL, has_staff_booster),
    "TTH Well: Fuel Cell Right": SFALocationData(
        129, GameBit(0x095E), SFARegion.TH_WELL, has_staff_booster
    ),

    ## Ice Mountain
    "IM: Cheat Well Fuel Cell": SFALocationData(114, GameBit(0x0957), SFARegion.IM, True_()),
    "IM: Race Cave Fuel Cell Front": SFALocationData(115, GameBit(0x0955), SFARegion.IM, True_()),
    "IM: Race Cave Fuel Cell Back": SFALocationData(116, GameBit(0x0956), SFARegion.IM, True_()),

    ## SnowHorn Wastes
    "SHW: Ice Block Fuel Cell Left": SFALocationData(
        117, GameBit(0x0958), SFARegion.SW_WATERSPOUT, True_()
    ),
    "SHW: Ice Block Fuel Cell Right": SFALocationData(
        118, GameBit(0x0959), SFARegion.SW_WATERSPOUT, True_()
    ),
    "SHW: Water Platform Fuel Cell Left": SFALocationData(
        119, GameBit(0x0952), SFARegion.SW_ENTRANCE, Has("Staff")
    ),
    "SHW: Water Platform Fuel Cell Right": SFALocationData(
        120, GameBit(0x0953), SFARegion.SW_ENTRANCE, Has("Staff")
    ),  # Also Linked to dig cave fuel cell
    "SHW: Dig Cave near Entrance Fuel Cell": SFALocationData(
        121, GameBit(0x0954), SFARegion.SW_ENTRANCE, Has("Tricky (Progressive)")
    ),
    "SHW: Path to TTH Booster Fuel Cell Left": SFALocationData(
        122,
        GameBit(0x095F),
        SFARegion.SW_ENTRANCE,
        has_blaster & has_staff_booster,
    ),
    "SHW: Path to TTH Booster Fuel Cell Right": SFALocationData(
        123,
        GameBit(0x0960),
        SFARegion.SW_ENTRANCE,
        has_blaster & has_staff_booster,
    ),
    "SHW: Blast Tree past Gate Fuel Cell Left": SFALocationData(
        133, GameBit(0x0967), SFARegion.SW_GATE, has_blaster
    ),
    "SHW: Blast Tree past Gate Fuel Cell Right": SFALocationData(
        134, GameBit(0x0968), SFARegion.SW_GATE, has_blaster
    ),
    "SHW: River past Gate Cheat Well Fuel Cell": SFALocationData(
        135, GameBit(0x0984), SFARegion.SW_GATE, True_()
    ),
    "SHW: River Ledge past Gate Fuel Cell Center": SFALocationData(
        136, GameBit(0x095A), SFARegion.SW_GATE, True_()
    ),
    "SHW: River Ledge past Gate Fuel Cell Right": SFALocationData(
        137, GameBit(0x095B), SFARegion.SW_GATE, has_blaster
    ),
    "SHW: River Ledge past Gate Fuel Cell Left": SFALocationData(
        138, GameBit(0x095C), SFARegion.SW_GATE, has_blaster
    ),

    ## LightFoot Village
    "TTH: Entrance to LFV Fuel Cell Right": SFALocationData(
        124, GameBit(0x094A), SFARegion.LFV, Has("Staff")
    ),
    "TTH: Entrance to LFV Fuel Cell Left": SFALocationData(
        125, GameBit(0x094B), SFARegion.LFV, Has("Staff")
    ),
    # "LFV Entrance Booster Ledge 1": SFALocationData(126, 0x096B, SFALocationType.FUELCELL, SFARegion.LFV),
    # "LFV Entrance Booster Ledge 2": SFALocationData(127, 0x096C, SFALocationType.FUELCELL, SFARegion.LFV),
    
    ## Moon Mountain Pass
    "MMP: Wind Draft Entrance Fuel Cell": SFALocationData(130, GameBit(0x0985), SFARegion.MMP, True_()),
    "MMP: Wind Draft Exit Fuel Cell": SFALocationData(131, GameBit(0x097E), SFARegion.MMP, True_()),
    "MMP: Barrel Hill Fuel Cell": SFALocationData(132, GameBit(0x0961), SFARegion.MMP, True_()),
    "MMP: Behind Fort Fuel Cell": SFALocationData(139, GameBit(0x0966), SFARegion.MMP, Has("Moon Pass Key")),
    "MMP: Meteorite Area Fuel Cell": SFALocationData(149, GameBit(0x0977), SFARegion.MMP_METEORITE, True_()),
    "MMP: Cheat Well near Warp Fuel Cell": SFALocationData(150, GameBit(0x0978), SFARegion.MMP_METEORITE, can_grow_moon_seed),
    "MMP: Beside Krazoa Warp Fuel Cell": SFALocationData(151, GameBit(0x0979), SFARegion.MMP_METEORITE, True_()),
    
    ## Volcano Force Point
    "VFP: Ice Blast Alcove Fuel Cell Left": SFALocationData(140, GameBit(0x096F), SFARegion.VFP, has_staff_booster & Has("Freeze Blast")),
    "VFP: Ice Blast Alcove Fuel Cell Right": SFALocationData(141, GameBit(0x0970), SFARegion.VFP, has_staff_booster & Has("Freeze Blast")),
    # "VFP: Disguise Alcove Fuel Cell Left": SFALocationData(142, GameBit(0x0973), SFARegion.VFP, has_staff_booster & Has("SharpClaw Disguise")),
    # "VFP: Disguise Alcove Fuel Cell Right": SFALocationData(143, GameBit(0x0974), SFARegion.VFP, has_staff_booster & Has("SharpClaw Disguise")),
    "VFP: Below Bridge Fuel Cell": SFALocationData(144, GameBit(0x098A), SFARegion.VFP, True_()),
    "VFP: Cheat Well Fuel Cell Left": SFALocationData(145, GameBit(0x097A), SFARegion.VFP_PAST_BRIDGE, can_grow_moon_seed),
    "VFP: Cheat Well Fuel Cell Right": SFALocationData(146, GameBit(0x097B), SFARegion.VFP_PAST_BRIDGE, can_grow_moon_seed),
    "VFP: Round Room Ledge Fuel Cell": SFALocationData(147, GameBit(0x0989), SFARegion.VFP_PAST_PUZZLE, Has("Freeze Blast")), # Damage Boost?
    "VFP: Warp Room Fuel Cell": SFALocationData(148, GameBit(0x0962), SFARegion.VFP_PAST_PUZZLE, has_blaster & Has("Tricky (Progressive)", 2) & Has("Freeze Blast")), # Damage Boost?
}

# Last id = 307
LOCATION_DIG_SPOT: dict[str, SFALocationData] = {
    "SHW: Dig Alpine Root near Campfire": SFALocationData(
        300, GameBit(0x002F), SFARegion.SW_WATERSPOUT, Has("Tricky (Progressive)")
    ),
    "SHW: Dig Alpine Root near Fallen Tree": SFALocationData(
        301, GameBit(0x002E), SFARegion.SW_WATERSPOUT, Has("Tricky (Progressive)")
    ),
    "SHW: Dig Egg near Water Spout": SFALocationData(
        302, GameBit(0x003A), SFARegion.SW_WATERSPOUT, Has("Tricky (Progressive)")
    ),
    "SHW: Dig BafomDad near Entrance": SFALocationData(
        303, GameBit(0x086F), SFARegion.SW_ENTRANCE, Has("Tricky (Progressive)")
    ),
    "SHW: Dig in Cave past Gate": SFALocationData(
        307, GameBit(0x086E), SFARegion.SW_GATE, Has("Tricky (Progressive)")
    ),
    "TTH: Dig near Store": SFALocationData(304, GameBit(0x0857), SFARegion.TH, Has("Tricky (Progressive)")),
    "TTH: Dig near Queen Cave": SFALocationData(
        305, GameBit(0x0856), SFARegion.TH, Has("Tricky (Progressive)")
    ),
    "TTH: Dig in Entrance to LFV": SFALocationData(
        306, GameBit(0x0858), SFARegion.LFV, Has("Tricky (Progressive)")
    ),
    "DIM: Dig Alpine Root in Entrance Hut": SFALocationData(
        308, GameBit(0x037C), SFARegion.DIM_ENTRANCE, Has("Tricky (Progressive)")
    ),
    "DIM: Dig Alpine Root in Boulder Path": SFALocationData(
        309, GameBit(0x037D), SFARegion.DIM_ENTRANCE, Has("Tricky (Progressive)")
    ),
}

NORMAL_TABLES: dict[str, SFALocationData] = {
    **LOCATION_ANY,
    **LOCATION_FUEL_CELL,
    **LOCATION_DIG_SPOT,
}

LOCATION_TABLE: dict[str, SFALocationData] = {
    **LOCATION_UPGRADE,
    **LOCATION_SHOP,
    **LOCATION_ANY,
    **LOCATION_FUEL_CELL,
    **LOCATION_DIG_SPOT,
}
