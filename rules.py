from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAny, HasFromList, Rule, True_

from .constants import SFAEvent
from .items import UT_GLITCH_LOGIC
from .options import InfiniteConsumables, PlantShuffle

if TYPE_CHECKING:
    from .world import SFAWorld


@dataclass()
class Victory(Rule["SFAWorld"], game="Star Fox Adventures"):
    """Rule that checks if the player has completed the game."""

    def _instantiate(self, world: "SFAWorld") -> Rule.Resolved:
        rule = True_()

        if world.options.required_boss.value != 0:
            rule &= HasFromList(SFAEvent.BOSS_DIM, SFAEvent.BOSS_CRF, count=world.options.required_boss.value)
        if world.options.required_spellstones.value != 0:
            if world.options.goal_completion.value == "collect":
                rule &= HasFromList(
                    "Fire SpellStone 1", "Water SpellStone 1", count=world.options.required_spellstones.value
                )
            elif world.options.goal_completion.value == "place":
                rule &= HasFromList(
                    SFAEvent.FIRE_SPELLSTONE_1,
                    SFAEvent.WATER_SPELLSTONE_1,
                    count=world.options.required_spellstones.value,
                )
        if world.options.required_spirits.value != 0:
            if world.options.goal_completion.value == "collect":
                rule &= HasFromList("Krazoa Spirit 2", "Krazoa Spirit 3", count=world.options.required_spirits.value)
            elif world.options.goal_completion.value == "place":
                rule &= HasFromList(SFAEvent.SPIRIT_2, SFAEvent.SPIRIT_3, count=world.options.required_spirits.value)

        if rule == True_():
            raise ValueError("No goal completion requirements set. Please set at least one requirement.")
        return rule.resolve(world)


@dataclass()
class CanExplodeBombPlant(Rule["SFAWorld"], game="Star Fox Adventures"):
    """Rule that checks if the player can explode a bomb plant."""

    def _instantiate(self, world: "SFAWorld") -> Rule.Resolved:
        return (
            Has("Bomb Plant", options=[OptionFilter(PlantShuffle, True)], filtered_resolution=True)
            & HasAny("Fire Blaster", "Ground Quake")
        ).resolve(world)


@dataclass()
class CanGrowMoonSeed(Rule["SFAWorld"], game="Star Fox Adventures"):
    """Rule that checks if the player can grow a moon seed."""

    def _instantiate(self, world: "SFAWorld") -> Rule.Resolved:
        plant_shuffle_rule = Has("Moon Seed", options=[OptionFilter(PlantShuffle, True)], filtered_resolution=True)
        can_collect_seeds_rule = Has(
            "Ground Quake", options=[OptionFilter(InfiniteConsumables, False)], filtered_resolution=True
        )
        return (plant_shuffle_rule & can_collect_seeds_rule & Has("Tricky (Progressive)", count=2)).resolve(world)


@dataclass()
class CanGoDarkRoom(Rule["SFAWorld"], game="Star Fox Adventures"):
    """Rule that checks if the player can go in a dark room."""

    def _instantiate(self, world: "SFAWorld") -> Rule.Resolved:
        if world.options.dark_rooms.value:
            return True_().resolve(world)
        return self.Resolved(player=world.player, caching_enabled=False)

    class Resolved(Rule.Resolved):
        """Resolved version."""

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return state.has("FireFly Lantern", self.player) or state.has(UT_GLITCH_LOGIC, self.player)


@dataclass()
class CanBuy(Rule["SFAWorld"], game="Star Fox Adventures"):
    """Rule that checks if the player can buy an item based on its price and the number of scarab bags they have."""

    price: int

    @override
    def _instantiate(self, world: "SFAWorld") -> Rule.Resolved:
        # caching_enabled only needs to be passed in when your world inherits from CachedRuleBuilderWorld
        return self.Resolved(self.price, player=world.player, caching_enabled=False)

    class Resolved(Rule.Resolved):
        """Resolved version."""

        price: int

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            if self.price <= 10:
                # Force a scarab bag in logic for convenience
                return state.has("Scarab Bag (Progressive)", self.player, 1)
            if self.price <= 50:
                return state.has("Scarab Bag (Progressive)", self.player, 1)
            if self.price <= 100:
                return state.has("Scarab Bag (Progressive)", self.player, 2)
            # Price <= 200 (max)
            return state.has("Scarab Bag (Progressive)", self.player, 3)

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            # this function is only required if you have caching enabled
            return {"Scarab Bag (Progressive)": {id(self)}}

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            # this method can be overridden to display custom explanations
            return [
                {"type": "text", "text": "Buy for "},
                {"type": "color", "color": "green" if state and self(state) else "salmon", "text": str(self.price)},
                {"type": "text", "text": " scarabs"},
            ]
