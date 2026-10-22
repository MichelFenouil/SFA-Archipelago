from worlds.AutoWorld import WebWorld

from .options import option_groups


class SFAWebWorld(WebWorld):
    """Web options interface for Star Fox Adventures."""

    game = "Star Fox Adventures"

    option_groups = option_groups
