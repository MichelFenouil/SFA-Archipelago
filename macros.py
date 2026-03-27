from BaseClasses import CollectionState


def has_blaster(state: CollectionState, player: int) -> bool:
    return state.has_all(["Staff", "Fire Blaster"], player)


def has_staff_booster(state: CollectionState, player: int) -> bool:
    return state.has_all(["Staff", "Staff Booster"], player)


def can_explode_bomb_plant(state: CollectionState, player: int) -> bool:
    # Also explodes with ground quake
    return state.has_all(["Staff", "Fire Blaster", "Bomb Plant"], player)


def can_buy(state: CollectionState, player: int, price: int) -> bool:
    if price <= 10:
        # Force a scarab bag in logic for convenience
        return state.has("Scarab Bag (Progressive)", player, 1)
    if price <= 50:
        return state.has("Scarab Bag (Progressive)", player, 1)
    if price <= 100:
        return state.has("Scarab Bag (Progressive)", player, 2)
    # Price <= 200 (max)
    return state.has("Scarab Bag (Progressive)", player, 3)
