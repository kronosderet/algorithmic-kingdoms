# ---------------------------------------------------------------------------
# Don't Panic — The Live Advisor (v10_epsilon foundation)
# ---------------------------------------------------------------------------
# Rule-based diagnostic engine that reads event_logger counters + game state
# and produces 1-3 actionable suggestions. Layer 0-1 scope (~15 rules).
# ---------------------------------------------------------------------------
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Suggestion:
    """One actionable suggestion from the advisor."""
    text: str
    category: str          # "economy", "defense", "army", "formation"
    priority: int = 0      # higher = more urgent


# ---------------------------------------------------------------------------
# Rule definitions — each is (condition_fn, suggestion_factory)
# condition_fn(game) -> bool   (should this rule fire?)
# suggestion_factory(game) -> Suggestion
# ---------------------------------------------------------------------------

def _count_buildings(game, btype: str) -> int:
    return sum(1 for b in game.player_buildings
               if b.building_type == btype and b.built and b.alive)


def _count_units(game, utype: str) -> int:
    return sum(1 for u in game.player_units if u.unit_type == utype and u.alive)


def _free_military(game) -> int:
    """Count military units not assigned to any squad."""
    count = 0
    for u in game.player_units:
        if u.alive and u.unit_type in ("soldier", "archer"):
            if game.player_squad_mgr.get_squad(u) is None:
                count += 1
    return count


# -- Economy rules (Layer 0) -----------------------------------------------

def _r_no_workers(game) -> bool:
    return _count_units(game, "worker") == 0

def _s_no_workers(game) -> Suggestion:
    return Suggestion(
        "You have no Gatherers! Train one at the Town Hall (Q).",
        "economy", priority=100)


def _r_few_workers(game) -> bool:
    workers = _count_units(game, "worker")
    return 0 < workers < 2 and game.game_time > 30

def _s_few_workers(game) -> Suggestion:
    return Suggestion(
        "Only 1 Gatherer — consider training more (Q at Town Hall) to boost income.",
        "economy", priority=80)


def _r_idle_workers(game) -> bool:
    idle = sum(1 for u in game.player_units
               if u.unit_type == "worker" and u.alive and u.state == "idle")
    return idle >= 2 and game.game_time > 20

def _s_idle_workers(game) -> Suggestion:
    idle = sum(1 for u in game.player_units
               if u.unit_type == "worker" and u.alive and u.state == "idle")
    return Suggestion(
        f"{idle} Gatherers idle — right-click a resource (Fiber, Flux, Crystal) to put them to work.",
        "economy", priority=70)


def _r_no_gold(game) -> bool:
    return game.resources.gold < 20 and game.game_time > 60

def _s_no_gold(game) -> Suggestion:
    return Suggestion(
        "Flux is very low. Send Gatherers to Flux deposits (yellow tiles) or reduce spending.",
        "economy", priority=75)


def _r_no_barracks(game) -> bool:
    return _count_buildings(game, "barracks") == 0 and game.game_time > 45

def _s_no_barracks(game) -> Suggestion:
    return Suggestion(
        "No Resonance Forge yet — select a Gatherer and press 2 to place one. You need it to train Wardens.",
        "economy", priority=85)


def _r_no_refinery(game) -> bool:
    has_iron = game.resources.iron > 0 or game.unlocks.get("has_iron", False)
    return (_count_buildings(game, "refinery") == 0
            and has_iron and game.game_time > 120)

def _s_no_refinery(game) -> Suggestion:
    return Suggestion(
        "You have Ore but no Harmonic Mill — select a Gatherer and press 3 to build one. It refines Ore into Alloy for upgrades.",
        "economy", priority=60)


# -- Defense rules (Layer 0-1) ----------------------------------------------

def _r_no_army(game) -> bool:
    mil = _count_units(game, "soldier") + _count_units(game, "archer")
    return mil == 0 and game.game_time > 60

def _s_no_army(game) -> Suggestion:
    return Suggestion(
        "No military units! Train Wardens (T) or Rangers (E) at the Resonance Forge before enemies arrive.",
        "defense", priority=95)


def _r_small_army(game) -> bool:
    mil = _count_units(game, "soldier") + _count_units(game, "archer")
    return 0 < mil <= 2 and game.game_time > 90

def _s_small_army(game) -> Suggestion:
    mil = _count_units(game, "soldier") + _count_units(game, "archer")
    return Suggestion(
        f"Only {mil} military unit{'s' if mil != 1 else ''} — consider training more before the next incident.",
        "defense", priority=65)


def _r_no_tower(game) -> bool:
    return (_count_buildings(game, "tower") == 0
            and game.game_time > 120
            and game.enemy_ai._waves_survived >= 1)

def _s_no_tower(game) -> Suggestion:
    return Suggestion(
        "No Sentinel yet. Sentinels deal area damage and slow enemies. Select a Gatherer, press 4.",
        "defense", priority=55)


def _r_buildings_under_attack(game) -> bool:
    for b in game.player_buildings:
        if b.alive and b.hp < b.max_hp * 0.7:
            return True
    return False

def _s_buildings_under_attack(game) -> Suggestion:
    return Suggestion(
        "A building is taking damage! Send military units to defend it — right-click near the threatened building.",
        "defense", priority=90)


def _r_enemy_near_base(game) -> bool:
    if not game.enemy_units:
        return False
    # Check if any enemy is within 300px of town hall
    for b in game.player_buildings:
        if b.building_type == "town_hall" and b.alive:
            for e in game.enemy_units:
                if e.alive:
                    dx = e.x - b.x
                    dy = e.y - b.y
                    if dx * dx + dy * dy < 300 * 300:
                        return True
    return False

def _s_enemy_near_base(game) -> Suggestion:
    return Suggestion(
        "Enemies near your Town Hall! Rally your army to defend — select Wardens/Rangers and right-click near the threat.",
        "defense", priority=98)


# -- Army/formation rules (Layer 1) ----------------------------------------

def _r_free_units(game) -> bool:
    return _free_military(game) >= 3 and len(game.discovered_formations) > 0

def _s_free_units(game) -> Suggestion:
    n = _free_military(game)
    return Suggestion(
        f"{n} free military units — press F to form a squad with the best discovered formation.",
        "formation", priority=50)


def _r_undiscovered_formations(game) -> bool:
    mil = _count_units(game, "soldier") + _count_units(game, "archer")
    return (mil >= 3
            and len(game.discovered_formations) == 0
            and game.game_time > 90)

def _s_undiscovered_formations(game) -> Suggestion:
    return Suggestion(
        "Select 3+ military units and press F to form a squad — formations unlock powerful abilities!",
        "formation", priority=55)


def _r_losses_high(game) -> bool:
    losses = game.logger._counts.get("player_units_lost", 0)
    return losses >= 5 and game.game_time < 300

def _s_losses_high(game) -> Suggestion:
    return Suggestion(
        "Heavy losses early on. Try defensive stances (F6) or positioning near towers for support.",
        "defense", priority=60)


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------

ADVISOR_RULES: list[tuple] = [
    # (condition, factory, category)
    (_r_no_workers,             _s_no_workers,             "economy"),
    (_r_few_workers,            _s_few_workers,            "economy"),
    (_r_idle_workers,           _s_idle_workers,           "economy"),
    (_r_no_gold,                _s_no_gold,                "economy"),
    (_r_no_barracks,            _s_no_barracks,            "economy"),
    (_r_no_refinery,            _s_no_refinery,            "economy"),
    (_r_no_army,                _s_no_army,                "defense"),
    (_r_small_army,             _s_small_army,             "defense"),
    (_r_no_tower,               _s_no_tower,               "defense"),
    (_r_buildings_under_attack, _s_buildings_under_attack,  "defense"),
    (_r_enemy_near_base,        _s_enemy_near_base,        "defense"),
    (_r_free_units,             _s_free_units,             "formation"),
    (_r_undiscovered_formations, _s_undiscovered_formations, "formation"),
    (_r_losses_high,            _s_losses_high,            "defense"),
]


class Advisor:
    """Don't Panic — rule-based live diagnostic engine."""

    MAX_SUGGESTIONS = 3

    def analyze(self, game) -> list[Suggestion]:
        """Run all rules against current game state, return top suggestions."""
        fired: list[Suggestion] = []
        for condition, factory, _cat in ADVISOR_RULES:
            try:
                if condition(game):
                    fired.append(factory(game))
            except Exception:
                pass  # advisor should never crash the game

        # sort by priority descending, take top N
        fired.sort(key=lambda s: s.priority, reverse=True)
        return fired[:self.MAX_SUGGESTIONS]
