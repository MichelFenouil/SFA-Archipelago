from BaseClasses import CollectionState
from rule_builder.rules import HasAll, HasAllCounts, Rule


has_blaster = HasAll("Staff", "Fire Blaster")

has_staff_booster = HasAll("Staff", "Staff Booster")

# Also explodes with ground quake
can_explode_bomb_plant = HasAll("Staff", "Fire Blaster", "Bomb Plant")


def can_buy(price: int) -> Rule:
    if price <= 10:
        # Force a scarab bag in logic for convenience
        return HasAllCounts({"Scarab Bag (Progressive)": 1})
    if price <= 50:
        return HasAllCounts({"Scarab Bag (Progressive)": 1})
    if price <= 100:
        return HasAllCounts({"Scarab Bag (Progressive)": 2})
    # Price <= 200 (max)
    return HasAllCounts({"Scarab Bag (Progressive)": 3})
