from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World
from worlds.sfa.options import SFAOptions

from .items import ALL_ITEMS_TABLE, SFAItem, create_item_classification, get_random_filler_item_name, items_name_to_id_dict
from .locations import create_all_locations, locations_name_to_id_dict
from .regions import create_and_connect_regions
from .rules import set_all_rules
from .items import create_all_items


class SFAWorld(World):
    """
    Star Fox Adventure is the Star Fox game where you go out of the spaceship.
    It's the one with the shmexy blue fox
    """
    game = "Star Fox Adventure"

    data_version = 1

    options_dataclass = SFAOptions
    options: SFAOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).

    item_name_to_id = items_name_to_id_dict()
    location_name_to_id = locations_name_to_id_dict()

    origin_region_name = "World Map"

    progress_locations: set[str] = set()

    def create_regions(self) -> None:
        create_and_connect_regions(self)
        create_all_locations(self)

    def set_rules(self) -> None:
        set_all_rules(self)

    def create_items(self) -> None:
        create_all_items(self)

    def create_item(self, name: str) -> SFAItem:
        return create_item_classification(self, name)
    
    def get_filler_item_name(self) -> str:
        return get_random_filler_item_name(self)
    
    def fill_slot_data(self) -> Mapping[str, Any]:
        # If you need access to the player's chosen options on the client side, there is a helper for that.
        return {}