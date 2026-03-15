from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from telemetry import TelemetryHub


class ResourceManager:
    def __init__(self, gold=0, wood=0, iron=0, steel=0, stone=0, tonic=0):
        self.gold = gold
        self.wood = wood
        self.iron = iron
        self.steel = steel
        self.stone = stone
        self.tonic = tonic
        # v10_zeta.1: telemetry hooks (set externally by Game after construction)
        self._telemetry: TelemetryHub | None = None
        self._game_time_fn: Callable[[], float] | None = None

    def _gt(self) -> float:
        """Get current game time from bound function."""
        fn = self._game_time_fn
        if fn is not None:
            return fn()
        return 0.0

    def can_afford(self, gold=0, wood=0, iron=0, steel=0, stone=0, tonic=0):
        return (self.gold >= gold and self.wood >= wood and self.iron >= iron
                and self.steel >= steel and self.stone >= stone
                and self.tonic >= tonic)

    def spend(self, gold=0, wood=0, iron=0, steel=0, stone=0, tonic=0):
        self.gold -= gold
        self.wood -= wood
        self.iron -= iron
        self.steel -= steel
        self.stone -= stone
        self.tonic -= tonic
        # v10_zeta.1: record spending to telemetry
        hub = self._telemetry
        if hub is not None:
            t = self._gt()
            if gold: hub.record_spend(t, "gold", gold)
            if wood: hub.record_spend(t, "wood", wood)
            if iron: hub.record_spend(t, "iron", iron)
            if steel: hub.record_spend(t, "steel", steel)
            if stone: hub.record_spend(t, "stone", stone)
            if tonic: hub.record_spend(t, "tonic", tonic)

    def add(self, rtype, amount):
        if rtype == "gold":
            self.gold += amount
        elif rtype == "wood":
            self.wood += amount
        elif rtype == "iron":
            self.iron += amount
        elif rtype == "steel":
            self.steel += amount
        elif rtype == "stone":
            self.stone += amount
        elif rtype == "tonic":
            self.tonic += amount
        # v10_zeta.1: record income to telemetry
        hub = self._telemetry
        if hub is not None:
            hub.record_income(self._gt(), rtype, amount)
