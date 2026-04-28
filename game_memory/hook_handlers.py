import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from CommonClient import logger

if TYPE_CHECKING:
    from ..SFAClient import SFAContext


# Hook signatures used by SFAHookHandlers.
MapTransitionHook = Callable[["SFAContext", int, int], Awaitable[None] | None]
ZoneTransitionHook = Callable[["SFAContext", int, int], Awaitable[None] | None]
PlayerCoordHook = Callable[["SFAContext", str], Awaitable[None] | None]


@dataclass
class PlayerCoordZone:
    """Describes a named player-coordinate zone with optional map scoping."""

    name: str
    zone_type: str
    map_id: int | None = None
    min_x: float | None = None
    max_x: float | None = None
    min_z: float | None = None
    max_z: float | None = None
    center_x: float | None = None
    center_z: float | None = None
    radius: float | None = None

    @staticmethod
    def square(
        name: str,
        x1: float,
        x2: float,
        z1: float,
        z2: float,
        map_id: int | None = None,
    ) -> "PlayerCoordZone":
        """Create a square zone from two X bounds and two Z bounds."""
        return PlayerCoordZone(
            name=name,
            zone_type="square",
            map_id=map_id,
            min_x=min(x1, x2),
            max_x=max(x1, x2),
            min_z=min(z1, z2),
            max_z=max(z1, z2),
        )

    @staticmethod
    def circle(
        name: str,
        center_x: float,
        center_z: float,
        radius: float,
        map_id: int | None = None,
    ) -> "PlayerCoordZone":
        """Create a circular zone from center coordinates and radius."""
        return PlayerCoordZone(
            name=name,
            zone_type="circle",
            map_id=map_id,
            center_x=center_x,
            center_z=center_z,
            radius=abs(radius),
        )

    def contains(self, x: float, z: float, map_id: int) -> bool:
        """Return whether the provided coordinates are inside this zone."""
        if self.map_id is not None and self.map_id != map_id:
            return False

        if self.zone_type == "square":
            if None in (self.min_x, self.max_x, self.min_z, self.max_z):
                return False
            assert (
                self.min_x is not None and self.max_x is not None and self.min_z is not None and self.max_z is not None
            )
            return self.min_x <= x <= self.max_x and self.min_z <= z <= self.max_z

        if self.zone_type == "circle":
            if None in (self.center_x, self.center_z, self.radius):
                return False
            assert self.center_x is not None and self.center_z is not None and self.radius is not None
            dx = x - self.center_x
            dz = z - self.center_z
            return dx * dx + dz * dz <= self.radius * self.radius

        logger.warning("Unknown player coord zone type: %s", self.zone_type)
        return False


class ZoneTransitionEvaluator:
    """Computes entered/left sets for coordinate-defined zones."""

    @staticmethod
    def evaluate(
        zones: dict[str, PlayerCoordZone],
        active_zones: set[str],
        x: float,
        z: float,
        map_id: int,
    ) -> tuple[set[str], set[str], set[str]]:
        """Evaluate zone transitions for the current position and map."""
        active_now = {zone_name for zone_name, zone in zones.items() if zone.contains(x, z, map_id)}
        entered = active_now.difference(active_zones)
        left = active_zones.difference(active_now)
        return active_now, entered, left


class SFAHookHandlers:
    """Registration and dispatch for map, zone, and player-coordinate hooks."""

    def __init__(self, ctx: "SFAContext"):
        """Initialize empty hook registries bound to a specific SFA context."""
        self.ctx = ctx
        self.map_transition_hooks: list[MapTransitionHook] = []
        self.zone_transition_hooks: dict[int | None, list[ZoneTransitionHook]] = {}
        self.player_coord_zones: dict[str, PlayerCoordZone] = {}
        self.active_player_coord_zones: set[str] = set()
        self.player_coord_enter_hooks: list[PlayerCoordHook] = []
        self.player_coord_leave_hooks: list[PlayerCoordHook] = []

    def add_map_transition(self, hook: MapTransitionHook) -> None:
        """Register a map transition hook if it has not already been added."""
        if hook not in self.map_transition_hooks:
            self.map_transition_hooks.append(hook)

    def remove_map_transition(self, hook: MapTransitionHook) -> None:
        """Unregister a map transition hook."""
        if hook in self.map_transition_hooks:
            self.map_transition_hooks.remove(hook)

    async def run_map_transition(self, entered_map: int, from_map: int) -> None:
        """Run all registered map transition hooks for a map change."""
        for hook in self.map_transition_hooks:
            try:
                result = hook(self.ctx, entered_map, from_map)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("Map transition hook failed (%s -> %s)", entered_map, from_map)

    def add_zone_transition(self, hook: ZoneTransitionHook, map_id: int | None) -> None:
        """Register a zone transition hook for a specific map or all maps."""
        if map_id not in self.zone_transition_hooks:
            self.zone_transition_hooks[map_id] = []
        if hook not in self.zone_transition_hooks[map_id]:
            self.zone_transition_hooks[map_id].append(hook)

    def remove_zone_transition(self, hook: ZoneTransitionHook, map_id: int | None) -> None:
        """Unregister a zone transition hook from a specific map scope."""
        if map_id in self.zone_transition_hooks and hook in self.zone_transition_hooks[map_id]:
            self.zone_transition_hooks[map_id].remove(hook)
            if not self.zone_transition_hooks[map_id]:
                del self.zone_transition_hooks[map_id]

    async def run_zone_transition(
        self,
        zone_objgroup_value: int,
        old_zone_objgroup_value: int,
        current_map: int,
    ) -> None:
        """Run zone hooks registered for the current map and global map scope."""
        # Run hooks for the current map and any global hooks (map_id=None)
        relevant_hooks = []
        if current_map in self.zone_transition_hooks:
            relevant_hooks.extend(self.zone_transition_hooks[current_map])
        if None in self.zone_transition_hooks:
            relevant_hooks.extend(self.zone_transition_hooks[None])
        for hook in relevant_hooks:
            try:
                result = hook(self.ctx, zone_objgroup_value, old_zone_objgroup_value)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception(
                    "Zone transition hook failed (%s -> %s)", zone_objgroup_value, old_zone_objgroup_value, current_map
                )

    def add_player_coord_zone(self, zone: PlayerCoordZone) -> None:
        """Register or replace a player-coordinate zone by name."""
        self.player_coord_zones[zone.name] = zone

    def remove_player_coord_zone(self, zone_name: str) -> None:
        """Remove a registered player-coordinate zone and its active state."""
        self.player_coord_zones.pop(zone_name, None)
        self.active_player_coord_zones.discard(zone_name)

    def add_player_coord_transition(self, hook: PlayerCoordHook, trigger: Literal["enter", "leave"]) -> None:
        """Register a player-coordinate transition hook for enter or leave events."""
        if trigger == "enter" and hook not in self.player_coord_enter_hooks:
            self.player_coord_enter_hooks.append(hook)
        elif trigger == "leave" and hook not in self.player_coord_leave_hooks:
            self.player_coord_leave_hooks.append(hook)

    def remove_player_coord_transition(self, hook: PlayerCoordHook) -> None:
        """Remove a player-coordinate transition hook from all trigger lists."""
        if hook in self.player_coord_enter_hooks:
            self.player_coord_enter_hooks.remove(hook)
        if hook in self.player_coord_leave_hooks:
            self.player_coord_leave_hooks.remove(hook)

    async def update_player_coord_transitions(self, x: float, y: float, z: float, map_id: int) -> None:
        """Evaluate zone transitions and dispatch enter/leave hooks."""
        active_now, entered, left = ZoneTransitionEvaluator.evaluate(
            self.player_coord_zones,
            self.active_player_coord_zones,
            x,
            z,
            map_id,
        )

        for zone_name in entered:
            await self._run_player_coord_hooks(self.player_coord_enter_hooks, zone_name)
        for zone_name in left:
            await self._run_player_coord_hooks(self.player_coord_leave_hooks, zone_name)

        self.active_player_coord_zones = active_now

    async def _run_player_coord_hooks(
        self,
        hooks: list[PlayerCoordHook],
        zone_name: str,
    ) -> None:
        """Execute the provided player-coordinate hooks for a single zone name."""
        for hook in list(hooks):
            try:
                result = hook(self.ctx, zone_name)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("Player coord transition hook failed for zone '%s'", zone_name)
