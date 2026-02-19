from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import SFAWorld


class SFARegion(Enum):
    """Region names for Star Fox Adventures."""

    WORLDMAP = "World Map"
    TH = "ThornTail Hollow"  # Originally SwapStone Hollow in game
    IM = "Ice Mountain"
    SW_WATERSPOUT = "SnowHorn Wastes - Water Spout"  # Called MW in game
    SW_ENTRANCE = "SnowHorn Wastes - Entrance"  # Exit to ThornTail Hollow the first time
    SW_GATE = "SnowHorn Wastes - Behind Gate"
    TH_WELL = "ThornTail Hollow - Well"
    TH_WELL_BOTTOM = "ThornTail Hollow - Dark Well Bottom"
    LFV = "LightFoot Village"
    MMP = "Moon Mountain Pass"
    DIM_ENTRANCE = "DarkIce Mines - Entrance"
    DIM_FORT = "DarkIce Mines - SharpClaw Fort"
    DIM_BOTTOM = "DarkIce Mines - Bottom"


def create_all_regions(world: SFAWorld) -> None:
    """Create regions for AP world."""
    sfa_region_list = [Region(region.value, world.player, world.multiworld) for region in SFARegion]
    print(f"Added regions: {sfa_region_list}")  # noqa: T201
    world.multiworld.regions += sfa_region_list
