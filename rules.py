from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has

if TYPE_CHECKING:
    from .world import SFAWorld


def set_all_rules(world: SFAWorld) -> None:
    """Generate rules for AP world."""
    set_completion_condition(world)


def set_completion_condition(world: SFAWorld) -> None:
    """Create victory condition."""
    # Defeat Boss Galdon
    world.set_completion_rule(Has("Victory"))
