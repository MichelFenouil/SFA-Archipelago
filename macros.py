from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAny, Rule

from .options import PlantShuffle

if TYPE_CHECKING:
    from .world import SFAWorld


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
        plant_shuffle_rule = Has("Moon Seed", options=[OptionFilter(PlantShuffle, True)]) | Has(
            "Ground Quake", options=[OptionFilter(PlantShuffle, False)]
        )
        return (plant_shuffle_rule & Has("Tricky (Progressive)", count=2)).resolve(world)


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
