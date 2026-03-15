# ---------------------------------------------------------------------------
# Don't Panic — The Live Advisor (v10_epsilon foundation)
# ---------------------------------------------------------------------------
# Rule-based diagnostic engine that reads event_logger counters + game state
# and produces 1-3 actionable suggestions. 25 rules across economy, defense,
# formation, ecology, and strategic categories.
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


# -- v10_zeta: Economy depth rules -----------------------------------------

def _r_low_wood(game) -> bool:
    if game.resources.wood >= 30:
        return False
    # Check if any workers are on trees
    for u in game.player_units:
        if u.unit_type == "worker" and u.alive and u.state == "gathering":
            if hasattr(u, 'gather_target') and u.gather_target == "wood":
                return False
    return game.game_time > 60

def _s_low_wood(game) -> Suggestion:
    return Suggestion(
        "Fiber running low — send Gatherers to harvest trees (green tiles).",
        "economy", priority=55)


def _r_no_smelter_with_iron(game) -> bool:
    has_refinery = _count_buildings(game, "refinery") > 0
    has_forge = _count_buildings(game, "forge") > 0
    return (not has_refinery and not has_forge
            and game.resources.iron > 30 and game.game_time > 150)

def _s_no_smelter_with_iron(game) -> Suggestion:
    return Suggestion(
        "Sitting on Ore but no Harmonic Mill — build one (3) to refine Ore into Alloy for military upgrades.",
        "economy", priority=58)


def _r_tonic_available(game) -> bool:
    if game.resources.tonic < 5:
        return False
    # Any damaged units near town hall?
    for b in game.player_buildings:
        if b.building_type == "town_hall" and b.alive and b.built and not b.ruined:
            for u in game.player_units:
                if u.alive and u.hp < u.max_hp * 0.8:
                    dx = u.x - b.x
                    dy = u.y - b.y
                    if dx * dx + dy * dy < 200 * 200:
                        return True
    return False

def _s_tonic_available(game) -> Suggestion:
    return Suggestion(
        "Tonic is healing damaged units near the Tree of Life — keep wounded units nearby to recover.",
        "economy", priority=45)


def _r_excess_gold(game) -> bool:
    mil = _count_units(game, "soldier") + _count_units(game, "archer")
    return game.resources.gold > 500 and mil < 5 and game.game_time > 120

def _s_excess_gold(game) -> Suggestion:
    return Suggestion(
        "Hoarding Flux! Spend it on military units — train Wardens (T) and Rangers (E).",
        "economy", priority=52)


# -- v10_zeta: Defense depth rules -----------------------------------------

def _r_undefended_flank(game) -> bool:
    towers = [b for b in game.player_buildings
              if b.building_type == "tower" and b.built and b.alive and not b.ruined]
    if not towers:
        return False  # _r_no_tower handles this case
    for b in game.player_buildings:
        if not b.alive or not b.built or b.ruined:
            continue
        if b.building_type == "tower":
            continue
        # Check if any tower is within 250px
        near_tower = False
        for t in towers:
            dx = b.x - t.x
            dy = b.y - t.y
            if dx * dx + dy * dy < 250 * 250:
                near_tower = True
                break
        if not near_tower:
            return True
    return False

def _s_undefended_flank(game) -> Suggestion:
    return Suggestion(
        "Some buildings are far from any Sentinel — build a tower nearby (4) for defense coverage.",
        "defense", priority=48)


def _r_tower_without_garrison(game) -> bool:
    # Towers with garrison have the garrison field from town hall, but
    # this refers to the strategic concept — do we have towers with no
    # nearby military units?
    for b in game.player_buildings:
        if b.building_type == "tower" and b.built and b.alive and not b.ruined:
            # Check for military units within 150px
            has_guards = False
            for u in game.player_units:
                if u.alive and u.unit_type in ("soldier", "archer"):
                    dx = u.x - b.x
                    dy = u.y - b.y
                    if dx * dx + dy * dy < 150 * 150:
                        has_guards = True
                        break
            if not has_guards:
                return True
    return False

def _s_tower_without_garrison(game) -> Suggestion:
    return Suggestion(
        "A Sentinel has no nearby guards — station units near towers for mutual support.",
        "defense", priority=42)


def _r_single_army_group(game) -> bool:
    squads = game.player_squad_mgr.squad_list
    alive_squads = [s for s in squads if s.alive_count > 0]
    mil = _count_units(game, "soldier") + _count_units(game, "archer")
    return len(alive_squads) == 1 and mil >= 8 and game.game_time > 180

def _s_single_army_group(game) -> Suggestion:
    return Suggestion(
        "All units in one squad — consider splitting into two groups to cover more ground.",
        "formation", priority=40)


# -- v10_zeta: Ecology awareness rules ------------------------------------

def _r_resources_depleting(game) -> bool:
    # Check map center area for depletion
    if game.game_time < 180:
        return False
    total_tiles = 0
    depleted_tiles = 0
    gm = game.game_map
    cx, cy = gm.cols // 2, gm.rows // 2
    scan_range = min(20, gm.cols // 4)
    for r in range(max(0, cy - scan_range), min(gm.rows, cy + scan_range)):
        for c in range(max(0, cx - scan_range), min(gm.cols, cx + scan_range)):
            t = gm.tiles[r][c]
            if t != 0:  # TERRAIN_GRASS == 0, skip
                total_tiles += 1
            elif (c, r) in gm.regrowth_timers:
                depleted_tiles += 1
                total_tiles += 1
    return total_tiles > 0 and depleted_tiles > total_tiles * 0.4

def _s_resources_depleting(game) -> Suggestion:
    return Suggestion(
        "Resources near base are running low — expand to new deposits further out. Depleted tiles will regrow over time.",
        "economy", priority=50)


def _r_tree_of_life_damaged(game) -> bool:
    for b in game.player_buildings:
        if b.building_type == "town_hall" and b.alive and b.built and not b.ruined:
            if b.hp < b.max_hp * 0.5:
                return True
    return False

def _s_tree_of_life_damaged(game) -> Suggestion:
    return Suggestion(
        "Your Tree of Life is badly damaged! Protect it — without it, Tonic generation stops and you lose the game.",
        "defense", priority=97)


# -- v10_zeta: Strategic rules ---------------------------------------------

def _r_no_expansion(game) -> bool:
    if game.game_time < 300:  # 5 minutes
        return False
    # Count economy building clusters
    econ_buildings = [b for b in game.player_buildings
                      if b.alive and b.built and not b.ruined
                      and b.building_type in ("goldmine_hut", "lumber_camp",
                                              "quarry_hut", "iron_depot",
                                              "sawmill", "goldmine",
                                              "stoneworks", "iron_works")]
    if len(econ_buildings) < 2:
        return True
    # Check if all economy buildings are within 400px of each other (single cluster)
    if econ_buildings:
        avg_x = sum(b.x for b in econ_buildings) / len(econ_buildings)
        avg_y = sum(b.y for b in econ_buildings) / len(econ_buildings)
        all_near = all((b.x - avg_x) ** 2 + (b.y - avg_y) ** 2 < 400 * 400
                       for b in econ_buildings)
        return all_near
    return False

def _s_no_expansion(game) -> Suggestion:
    return Suggestion(
        "All economy buildings clustered together — expand outward to reach fresh resource deposits.",
        "economy", priority=44)


def _r_incident_approaching(game) -> bool:
    if not hasattr(game.enemy_ai, 'tension'):
        return False
    if game.enemy_ai.tension < 0.7:
        return False
    # Check if army is scattered (high spread)
    mil_units = [u for u in game.player_units
                 if u.alive and u.unit_type in ("soldier", "archer")]
    if len(mil_units) < 3:
        return False
    avg_x = sum(u.x for u in mil_units) / len(mil_units)
    avg_y = sum(u.y for u in mil_units) / len(mil_units)
    spread = sum((u.x - avg_x) ** 2 + (u.y - avg_y) ** 2
                 for u in mil_units) / len(mil_units)
    return spread > 300 * 300  # units are widely scattered

def _s_incident_approaching(game) -> Suggestion:
    return Suggestion(
        "Tension is rising — an attack is imminent! Rally your forces near key buildings.",
        "defense", priority=72)


# -- v10_zeta.1: Trend-aware rules (use telemetry rates) -------------------

def _has_telemetry(game) -> bool:
    return hasattr(game, 'telemetry') and game.telemetry is not None


def _r_gold_dropping(game) -> bool:
    if not _has_telemetry(game):
        return False
    t = game.game_time
    nf = game.telemetry.net_flow(t, "gold")
    return nf < -3.0 and game.resources.gold < 100 and t > 60

def _s_gold_dropping(game) -> Suggestion:
    t = game.game_time
    nf = game.telemetry.net_flow(t, "gold")
    ttz = game.telemetry.time_to_zero(t, "gold", game.resources.gold)
    if ttz is not None and ttz < 30:
        msg = f"Flux dropping at {nf:.1f}/s — will run out in {ttz:.0f}s! Boost income or cut spending."
    else:
        msg = f"Flux income is negative ({nf:.1f}/s). Assign more Gatherers to Flux deposits."
    return Suggestion(msg, "economy", priority=78)


def _r_resource_bottleneck(game) -> bool:
    if not _has_telemetry(game):
        return False
    return game.telemetry.bottleneck_resource(game.game_time, game.resources) is not None and game.game_time > 90

def _s_resource_bottleneck(game) -> Suggestion:
    from constants import display_name
    rtype = game.telemetry.bottleneck_resource(game.game_time, game.resources) or "gold"
    return Suggestion(
        f"{display_name(rtype)} is your bottleneck — prioritize gathering it.",
        "economy", priority=62)


def _r_income_stalled(game) -> bool:
    if not _has_telemetry(game):
        return False
    if game.game_time < 45:
        return False
    t = game.game_time
    # Check if all key resource income rates are near zero
    for rtype in ("gold", "wood"):
        if game.telemetry.income_rate(t, rtype) > 0.3:
            return False
    return True

def _s_income_stalled(game) -> Suggestion:
    return Suggestion(
        "No resource income detected! Send Gatherers to harvest Flux or Fiber tiles immediately.",
        "economy", priority=88)


def _r_overspending(game) -> bool:
    if not _has_telemetry(game):
        return False
    if game.game_time < 60:
        return False
    t = game.game_time
    for rtype in ("gold", "wood", "iron", "stone"):
        inc = game.telemetry.income_rate(t, rtype)
        spend = game.telemetry.spend_rate(t, rtype)
        if inc > 0.5 and spend > inc * 2.0:
            return True
    return False

def _s_overspending(game) -> Suggestion:
    from constants import display_name
    t = game.game_time
    worst = ""
    worst_ratio = 0.0
    for rtype in ("gold", "wood", "iron", "stone"):
        inc = game.telemetry.income_rate(t, rtype)
        spend = game.telemetry.spend_rate(t, rtype)
        if inc > 0 and spend / inc > worst_ratio:
            worst_ratio = spend / inc
            worst = rtype
    return Suggestion(
        f"Spending {display_name(worst)} faster than earning it ({worst_ratio:.1f}x). Slow down or boost production.",
        "economy", priority=58)


def _r_strong_formation(game) -> bool:
    """Notify player when formation effectiveness is high — positive reinforcement."""
    if not _has_telemetry(game):
        return False
    pct = game.telemetry.formation_damage_pct()
    return pct > 50 and game.game_time > 180

def _s_strong_formation(game) -> Suggestion:
    pct = game.telemetry.formation_damage_pct()
    return Suggestion(
        f"Formations account for {pct:.0f}% of your damage — keep your squads together!",
        "formation", priority=30)


def _r_short_unit_lifetime(game) -> bool:
    """Units dying very quickly — suggest repositioning."""
    if not _has_telemetry(game):
        return False
    avg = game.telemetry.avg_unit_lifetime("player")
    # Only trigger if we have enough data and lifetime is short
    return avg > 0 and avg < 20 and len(game.telemetry._lifetimes) >= 5 and game.game_time > 120

def _s_short_unit_lifetime(game) -> Suggestion:
    avg = game.telemetry.avg_unit_lifetime("player")
    return Suggestion(
        f"Your units survive only {avg:.0f}s on average — try defensive stance or positioning near towers.",
        "defense", priority=56)


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
    # v10_zeta: economy depth
    (_r_low_wood,               _s_low_wood,               "economy"),
    (_r_no_smelter_with_iron,   _s_no_smelter_with_iron,   "economy"),
    (_r_tonic_available,        _s_tonic_available,         "economy"),
    (_r_excess_gold,            _s_excess_gold,            "economy"),
    # v10_zeta: defense depth
    (_r_undefended_flank,       _s_undefended_flank,       "defense"),
    (_r_tower_without_garrison, _s_tower_without_garrison,  "defense"),
    (_r_single_army_group,      _s_single_army_group,      "formation"),
    # v10_zeta: ecology awareness
    (_r_resources_depleting,    _s_resources_depleting,    "economy"),
    (_r_tree_of_life_damaged,   _s_tree_of_life_damaged,   "defense"),
    # v10_zeta: strategic
    (_r_no_expansion,           _s_no_expansion,           "economy"),
    (_r_incident_approaching,   _s_incident_approaching,   "defense"),
    # v10_zeta.1: trend-aware (telemetry-based)
    (_r_gold_dropping,          _s_gold_dropping,          "economy"),
    (_r_resource_bottleneck,    _s_resource_bottleneck,    "economy"),
    (_r_income_stalled,         _s_income_stalled,         "economy"),
    (_r_overspending,           _s_overspending,           "economy"),
    (_r_strong_formation,       _s_strong_formation,       "formation"),
    (_r_short_unit_lifetime,    _s_short_unit_lifetime,    "defense"),
]


class Advisor:
    """Don't Panic — rule-based live diagnostic engine.
    v10_zeta.1: now trend-aware with telemetry integration and rule effectiveness tracking."""

    MAX_SUGGESTIONS = 3

    def analyze(self, game) -> list[Suggestion]:
        """Run all rules against current game state, return top suggestions."""
        fired: list[Suggestion] = []
        fired_names: list[str] = []
        hub = getattr(game, 'telemetry', None)

        for condition, factory, _cat in ADVISOR_RULES:
            try:
                if condition(game):
                    suggestion = factory(game)
                    fired.append(suggestion)
                    rule_name = condition.__name__
                    fired_names.append(rule_name)
                    # v10_zeta.1: record rule fire for effectiveness tracking
                    if hub is not None:
                        hub.record_rule_fired(rule_name, game.game_time)
            except Exception:
                pass  # advisor should never crash the game

        # v10_zeta.1: check rule effectiveness (did player act on previous suggestions?)
        if hub is not None:
            hub.check_rule_effectiveness(game.game_time, fired_names, game)

        # sort by priority descending, take top N
        fired.sort(key=lambda s: s.priority, reverse=True)
        return fired[:self.MAX_SUGGESTIONS]
