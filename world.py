from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from .items import (
    SFAItem,
    create_all_items,
    create_item_classification,
    get_random_filler_item_name,
    items_name_to_id_dict,
)
from .locations import create_all_locations, locations_name_to_id_dict
from .options import SFAOptions
from .regions import create_all_regions
from .rules import connect_regions, set_all_rules


class SFAWorld(World):
    """
    Star Fox Adventures is an action-adventure game for the GameCube.
    Unlike other Star Fox titles, play as Fox McCloud to save Dinosaur Planet in the Lylat System.
    """

    game = "Star Fox Adventures"

    data_version = 1

    options_dataclass = SFAOptions
    options: SFAOptions  # Common mistake: This has to be a colon (:), not an equals sign (=).

    item_name_to_id = items_name_to_id_dict()
    location_name_to_id = locations_name_to_id_dict()

    origin_region_name = "World Map"

    progress_locations: set[str] = set()  # noqa: RUF012

    def create_regions(self) -> None:
        """Create regions and entrances for this world player."""
        create_all_regions(self)
        connect_regions(self)
        create_all_locations(self)

    def set_rules(self) -> None:
        """Create rules for this world player."""
        set_all_rules(self)

    def create_items(self) -> None:
        """Create items for this world player."""
        create_all_items(self)

    def create_item(self, name: str) -> SFAItem:
        """
        Create an item for this world type and player.

        :param name: The name of the item to create.
        :raises KeyError: If an invalid item name is provided.
        """
        return create_item_classification(self, name)

    def get_filler_item_name(self) -> str:
        """
        Call when the item pool needs to be filled with additional items to match the location count.

        :param strict: Whether the item should be one strictly classified as filler. Defaults to `True`.
        :return: The name of a filler item from this world.
        """
        return get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        """
        Return the `slot_data` field that will be in the `Connected` network package.

        This is a way the generator can give custom data to the client.
        The client will receive this as JSON in the `Connected` response.

        :return: A dictionary to be sent to the client when it connects to the server.
        """
        # If you need access to the player's chosen options on the client side, there is a helper for that.
        return {}
