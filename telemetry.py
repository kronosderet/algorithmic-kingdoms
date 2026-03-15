# ---------------------------------------------------------------------------
# Telemetry Hub — Central metrics system for CSV stats, advisor, and UX
# ---------------------------------------------------------------------------
# v10_zeta.1: Economy flow, combat depth, UX telemetry, advisor intelligence.
# Pure data — no pygame imports. All game-state access via tick(dt, game).
# ---------------------------------------------------------------------------
from __future__ import annotations

import csv
import os
import sys
from collections import deque, Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from constants import (TELEMETRY_WINDOW, TELEMETRY_TICK_INTERVAL,
                       BOTTLENECK_THRESHOLD, ADVISOR_ACTION_WINDOW,
                       RESOURCE_KEYS)

if TYPE_CHECKING:
    from game import Game


# ---------------------------------------------------------------------------
# Sliding window — deque of (timestamp, amount) for rate calculation
# ---------------------------------------------------------------------------
class SlidingWindow:
    __slots__ = ('_entries', '_window')

    def __init__(self, window: float = TELEMETRY_WINDOW):
        self._entries: deque[tuple[float, float]] = deque()
        self._window = window

    def record(self, t: float, amount: float) -> None:
        self._entries.append((t, amount))

    def prune(self, t: float) -> None:
        cutoff = t - self._window
        while self._entries and self._entries[0][0] < cutoff:
            self._entries.popleft()

    def total(self, t: float) -> float:
        cutoff = t - self._window
        return sum(amt for ts, amt in self._entries if ts >= cutoff)

    def rate(self, t: float) -> float:
        """Amount per second over the window."""
        cutoff = t - self._window
        s = sum(amt for ts, amt in self._entries if ts >= cutoff)
        elapsed = min(self._window, t)
        return s / max(1.0, elapsed)


# ---------------------------------------------------------------------------
# Incident Scorecard — per-incident combat summary
# ---------------------------------------------------------------------------
@dataclass
class IncidentScorecard:
    incident_number: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    kills: int = 0
    player_losses: int = 0
    buildings_damaged: int = 0
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    outcome: str = ""
    flavour: str = ""
    formation_used: str = ""


# ---------------------------------------------------------------------------
# TelemetryHub — the single metrics instance
# ---------------------------------------------------------------------------
class TelemetryHub:

    def __init__(self, difficulty: str):
        self._difficulty = difficulty

        # -- Economy flow: sliding windows per resource ----------------------
        self._income: dict[str, SlidingWindow] = {k: SlidingWindow() for k in RESOURCE_KEYS}
        self._spend: dict[str, SlidingWindow] = {k: SlidingWindow() for k in RESOURCE_KEYS}
        self._peak: dict[str, float] = {k: 0.0 for k in RESOURCE_KEYS}
        self._first_zero: str | None = None  # first resource to hit 0 during play
        self._worker_alloc: dict[str, int] = {}  # updated each tick

        # -- Combat depth: per-unit tracking by eid --------------------------
        self._spawn_times: dict[int, float] = {}       # eid -> game_time
        self._unit_types: dict[int, str] = {}           # eid -> unit_type
        self._unit_owners: dict[int, str] = {}          # eid -> owner
        self._dmg_dealt: dict[int, float] = {}          # eid -> cumulative damage dealt
        self._dmg_taken: dict[int, float] = {}          # eid -> cumulative damage taken
        self._formation_dmg: dict[int, float] = {}      # eid -> damage dealt while in formation
        self._stance_kills: Counter[str] = Counter()    # stance_name -> kill count
        self._lifetimes: list[tuple[str, str, float]] = []  # (unit_type, owner, seconds_alive)

        # Per-type aggregate (for game-over summary)
        self._type_dmg_dealt: dict[str, float] = {}  # unit_type -> total damage
        self._type_dmg_taken: dict[str, float] = {}
        self._type_kills: Counter[str] = Counter()
        self._type_deaths: Counter[str] = Counter()

        # -- Incident scorecards ---------------------------------------------
        self._scorecards: list[IncidentScorecard] = []
        self._active_incident: IncidentScorecard | None = None
        self._incident_kills = 0          # kills during current incident
        self._incident_losses = 0         # player losses during current incident
        self._incident_bldg_damaged = 0   # buildings damaged during current incident
        self._incident_dmg_dealt = 0.0    # total damage dealt during current incident
        self._incident_dmg_taken = 0.0    # total damage taken during current incident

        # -- UX telemetry ----------------------------------------------------
        self.hotkey_count: int = 0
        self.click_count: int = 0
        self.pause_count: int = 0
        self._pause_start: float | None = None
        self.pause_total_duration: float = 0.0
        self.advisor_open_count: int = 0
        self._advisor_open_start: float | None = None
        self.advisor_total_duration: float = 0.0
        self.selection_counts: Counter[str] = Counter()
        self.camera_distance: float = 0.0
        self.first_action_time: float | None = None
        self._game_started: float = 0.0

        # -- Advisor rule tracking -------------------------------------------
        self._rule_fire_times: dict[str, list[float]] = {}  # rule_name -> [fire times]
        self._rule_conditions_at_fire: dict[str, str] = {}  # rule_name -> condition key
        self._rule_acted_count: Counter[str] = Counter()     # rule_name -> times player acted
        self._rule_ignored_count: Counter[str] = Counter()   # rule_name -> times ignored

        # -- Internal timing -------------------------------------------------
        self._tick_accum: float = 0.0
        self._closed = False

        # -- Incident scorecard CSV ------------------------------------------
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(base, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        sc_path = os.path.join(logs_dir, f"incidents_{difficulty}_{ts}.csv")
        self._sc_file = open(sc_path, "w", newline="", encoding="utf-8")
        self._sc_writer = csv.writer(self._sc_file)
        self._sc_writer.writerow([
            "incident", "start_time", "end_time", "duration",
            "kills", "player_losses", "buildings_damaged",
            "damage_dealt", "damage_taken", "outcome", "flavour",
            "formation_used"
        ])
        # UX telemetry CSV
        ux_path = os.path.join(logs_dir, f"ux_{difficulty}_{ts}.csv")
        self._ux_file = open(ux_path, "w", newline="", encoding="utf-8")
        self._ux_writer = csv.writer(self._ux_file)
        self._ux_writer.writerow([
            "game_time", "hotkey_count", "click_count", "hotkey_pct",
            "pause_count", "pause_duration", "advisor_opens", "advisor_duration",
            "camera_distance", "first_action_time",
            "top_selection_1", "top_selection_2", "top_selection_3"
        ])

    # -----------------------------------------------------------------------
    # Economy flow
    # -----------------------------------------------------------------------
    def record_income(self, t: float, rtype: str, amount: float) -> None:
        if rtype in self._income:
            self._income[rtype].record(t, amount)

    def record_spend(self, t: float, rtype: str, amount: float) -> None:
        if rtype in self._spend:
            self._spend[rtype].record(t, amount)

    def income_rate(self, t: float, rtype: str) -> float:
        return self._income[rtype].rate(t) if rtype in self._income else 0.0

    def spend_rate(self, t: float, rtype: str) -> float:
        return self._spend[rtype].rate(t) if rtype in self._spend else 0.0

    def net_flow(self, t: float, rtype: str) -> float:
        return self.income_rate(t, rtype) - self.spend_rate(t, rtype)

    def time_to_zero(self, t: float, rtype: str, current: float) -> float | None:
        """Seconds until resource hits zero at current net flow. None if stable/growing."""
        nf = self.net_flow(t, rtype)
        if nf >= 0 or current <= 0:
            return None
        return current / abs(nf)

    def bottleneck_resource(self, t: float, resources: object) -> str | None:
        """Return the resource with the worst net flow that is also low."""
        worst: str | None = None
        worst_score = 0.0
        for rtype in RESOURCE_KEYS:
            current = getattr(resources, rtype, 0.0)
            if current < BOTTLENECK_THRESHOLD:
                deficit = abs(min(0.0, self.net_flow(t, rtype)))
                if deficit > worst_score:
                    worst_score = deficit
                    worst = rtype
        return worst

    # -----------------------------------------------------------------------
    # Combat depth
    # -----------------------------------------------------------------------
    def record_unit_spawn(self, t: float, eid: int, unit_type: str, owner: str) -> None:
        self._spawn_times[eid] = t
        self._unit_types[eid] = unit_type
        self._unit_owners[eid] = owner

    def record_damage_dealt(self, t: float, attacker_eid: int, amount: float,
                            in_formation: bool = False,
                            attacker_type: str = "",
                            attacker_stance: str = "") -> None:
        self._dmg_dealt[attacker_eid] = self._dmg_dealt.get(attacker_eid, 0.0) + amount
        if in_formation:
            self._formation_dmg[attacker_eid] = self._formation_dmg.get(attacker_eid, 0.0) + amount
        if attacker_type:
            self._type_dmg_dealt[attacker_type] = self._type_dmg_dealt.get(attacker_type, 0.0) + amount
        # Incident tracking
        if self._active_incident is not None:
            self._incident_dmg_dealt += amount

    def record_damage_taken(self, t: float, target_eid: int, amount: float,
                            target_type: str = "") -> None:
        self._dmg_taken[target_eid] = self._dmg_taken.get(target_eid, 0.0) + amount
        if target_type:
            self._type_dmg_taken[target_type] = self._type_dmg_taken.get(target_type, 0.0) + amount
        if self._active_incident is not None:
            self._incident_dmg_taken += amount

    def record_kill(self, killer_type: str, victim_type: str, victim_owner: str,
                    killer_stance: str = "") -> None:
        self._type_kills[killer_type] += 1
        self._type_deaths[victim_type] += 1
        if killer_stance:
            self._stance_kills[killer_stance] += 1
        if self._active_incident is not None:
            if victim_owner == "enemy":
                self._incident_kills += 1
            elif victim_owner == "player":
                self._incident_losses += 1

    def record_unit_death(self, t: float, eid: int) -> None:
        spawn = self._spawn_times.get(eid)
        if spawn is not None:
            utype = self._unit_types.get(eid, "unknown")
            owner = self._unit_owners.get(eid, "unknown")
            self._lifetimes.append((utype, owner, t - spawn))
            # Cleanup to avoid memory leak on long games
            self._spawn_times.pop(eid, None)
            self._unit_types.pop(eid, None)
            self._unit_owners.pop(eid, None)

    def record_building_damaged(self) -> None:
        if self._active_incident is not None:
            self._incident_bldg_damaged += 1

    # -----------------------------------------------------------------------
    # Incident scorecards
    # -----------------------------------------------------------------------
    def start_incident(self, t: float, incident_number: int, flavour: str = "") -> None:
        self._active_incident = IncidentScorecard(
            incident_number=incident_number,
            start_time=t,
            flavour=flavour,
        )
        self._incident_kills = 0
        self._incident_losses = 0
        self._incident_bldg_damaged = 0
        self._incident_dmg_dealt = 0.0
        self._incident_dmg_taken = 0.0

    def end_incident(self, t: float, outcome: str, game: Game) -> None:
        sc = self._active_incident
        if sc is None:
            return
        sc.end_time = t
        sc.kills = self._incident_kills
        sc.player_losses = self._incident_losses
        sc.buildings_damaged = self._incident_bldg_damaged
        sc.damage_dealt = self._incident_dmg_dealt
        sc.damage_taken = self._incident_dmg_taken
        sc.outcome = outcome

        # Determine most-used formation during incident
        squads = game.player_squad_mgr.squad_list
        from constants import FORMATION_NAMES
        fmt_counts: Counter[int] = Counter()
        for sq in squads:
            if sq.alive_count > 0:
                fmt_counts[sq.formation] += 1
        if fmt_counts:
            top_fmt = fmt_counts.most_common(1)[0][0]
            sc.formation_used = FORMATION_NAMES[top_fmt] if 0 <= top_fmt < len(FORMATION_NAMES) else str(top_fmt)

        self._scorecards.append(sc)
        self._write_scorecard(sc)
        self._active_incident = None

    def _write_scorecard(self, sc: IncidentScorecard) -> None:
        if self._closed:
            return
        duration = sc.end_time - sc.start_time
        self._sc_writer.writerow([
            sc.incident_number, f"{sc.start_time:.1f}", f"{sc.end_time:.1f}",
            f"{duration:.1f}",
            sc.kills, sc.player_losses, sc.buildings_damaged,
            f"{sc.damage_dealt:.0f}", f"{sc.damage_taken:.0f}",
            sc.outcome, sc.flavour, sc.formation_used
        ])
        self._sc_file.flush()

    # -----------------------------------------------------------------------
    # UX telemetry
    # -----------------------------------------------------------------------
    def record_hotkey(self) -> None:
        self.hotkey_count += 1
        if self.first_action_time is None:
            self.first_action_time = -1.0  # placeholder, set properly with game_time

    def record_hotkey_at(self, t: float) -> None:
        self.hotkey_count += 1
        if self.first_action_time is None:
            self.first_action_time = t

    def record_click_at(self, t: float) -> None:
        self.click_count += 1
        if self.first_action_time is None:
            self.first_action_time = t

    def record_pause_start(self, t: float) -> None:
        self.pause_count += 1
        self._pause_start = t

    def record_pause_end(self, t: float) -> None:
        if self._pause_start is not None:
            self.pause_total_duration += t - self._pause_start
            self._pause_start = None

    def record_advisor_open(self, t: float) -> None:
        self.advisor_open_count += 1
        self._advisor_open_start = t

    def record_advisor_close(self, t: float) -> None:
        if self._advisor_open_start is not None:
            self.advisor_total_duration += t - self._advisor_open_start
            self._advisor_open_start = None

    def record_selection(self, entity_type: str) -> None:
        self.selection_counts[entity_type] += 1

    def record_camera_move(self, distance: float) -> None:
        self.camera_distance += distance

    def hotkey_pct(self) -> float:
        total = self.hotkey_count + self.click_count
        return (self.hotkey_count / total * 100.0) if total > 0 else 0.0

    # -----------------------------------------------------------------------
    # Advisor rule tracking
    # -----------------------------------------------------------------------
    def record_rule_fired(self, rule_name: str, t: float) -> None:
        if rule_name not in self._rule_fire_times:
            self._rule_fire_times[rule_name] = []
        self._rule_fire_times[rule_name].append(t)

    def record_rule_acted(self, rule_name: str) -> None:
        self._rule_acted_count[rule_name] += 1

    def rule_fire_count(self, rule_name: str) -> int:
        return len(self._rule_fire_times.get(rule_name, []))

    def check_rule_effectiveness(self, t: float, active_rules: list[str],
                                  game: object) -> None:
        """Check if previously-fired rules have been resolved (player acted)."""
        for rule_name, fire_times in self._rule_fire_times.items():
            if not fire_times:
                continue
            last_fire = fire_times[-1]
            if t - last_fire > ADVISOR_ACTION_WINDOW:
                if rule_name not in active_rules:
                    # Rule no longer fires — player acted
                    self._rule_acted_count[rule_name] += 1
                else:
                    # Still firing after window — player ignored it
                    self._rule_ignored_count[rule_name] += 1
                fire_times.clear()

    def rule_response_rate(self, rule_name: str) -> float:
        """Fraction of times a rule was acted on vs ignored."""
        acted = self._rule_acted_count.get(rule_name, 0)
        ignored = self._rule_ignored_count.get(rule_name, 0)
        total = acted + ignored
        return acted / total if total > 0 else 0.5

    # -----------------------------------------------------------------------
    # Per-frame tick
    # -----------------------------------------------------------------------
    def tick(self, dt: float, game: Game) -> None:
        if self._closed:
            return
        self._tick_accum += dt
        if self._tick_accum < TELEMETRY_TICK_INTERVAL:
            return
        self._tick_accum = 0.0

        t = game.game_time
        r = game.resources

        # Update highwater marks
        for rtype in RESOURCE_KEYS:
            val = float(getattr(r, rtype, 0))
            if val > self._peak[rtype]:
                self._peak[rtype] = val

        # Track first resource bottleneck
        if self._first_zero is None and t > 30:
            for rtype in RESOURCE_KEYS:
                val = getattr(r, rtype, 0)
                if val <= 0 and self._peak[rtype] > 10:
                    self._first_zero = rtype
                    break

        # Prune sliding windows
        for rtype in RESOURCE_KEYS:
            self._income[rtype].prune(t)
            self._spend[rtype].prune(t)

        # Worker allocation
        alloc: dict[str, int] = {"wood": 0, "gold": 0, "iron": 0, "stone": 0,
                                  "building": 0, "idle": 0, "other": 0}
        for u in game.player_units:
            if u.unit_type != "worker" or not u.alive:
                continue
            if u.state == "idle":
                alloc["idle"] += 1
            elif u.state == "gathering":
                gt = getattr(u, 'gather_target', None) or getattr(u, '_last_gather_type', None)
                if gt in alloc:
                    alloc[gt] += 1
                else:
                    alloc["other"] += 1
            elif u.state == "building" or u.state == "repairing":
                alloc["building"] += 1
            elif u.state == "returning":
                ct = getattr(u, 'carry_type', None)
                if ct in alloc:
                    alloc[ct] += 1
                else:
                    alloc["other"] += 1
            else:
                alloc["other"] += 1
        self._worker_alloc = alloc

        # Camera distance (tracked externally via record_camera_move)

    # -----------------------------------------------------------------------
    # Summaries for game-over panel and CSV
    # -----------------------------------------------------------------------
    def avg_unit_lifetime(self, owner: str = "player") -> float:
        times = [lt for ut, o, lt in self._lifetimes if o == owner]
        return sum(times) / len(times) if times else 0.0

    def formation_damage_pct(self) -> float:
        """% of total player damage dealt while in a formation."""
        total = sum(v for eid, v in self._dmg_dealt.items()
                    if self._unit_owners.get(eid) == "player")
        fmt = sum(self._formation_dmg.values())
        return (fmt / total * 100.0) if total > 0 else 0.0

    def top_unit_types_by_damage(self, n: int = 3) -> list[tuple[str, float]]:
        # Sort dict by value descending, return top n
        items = sorted(self._type_dmg_dealt.items(), key=lambda x: x[1], reverse=True)
        return items[:n]

    def stance_effectiveness(self) -> dict[str, int]:
        return dict(self._stance_kills)

    def get_game_over_stats(self, t: float, resources: object) -> dict:
        """Compile all telemetry into a single dict for the game-over panel."""
        total_dmg_dealt = sum(self._type_dmg_dealt.values())
        total_dmg_taken = sum(self._type_dmg_taken.values())

        top_sel = self.selection_counts.most_common(3)
        top_sel_strs = [f"{name}({cnt})" for name, cnt in top_sel]

        return {
            # Economy
            "peak_resources": dict(self._peak),
            "first_bottleneck": self._first_zero,
            "worker_alloc": dict(self._worker_alloc),
            # Combat
            "total_damage_dealt": total_dmg_dealt,
            "total_damage_taken": total_dmg_taken,
            "avg_unit_lifetime": self.avg_unit_lifetime("player"),
            "avg_enemy_lifetime": self.avg_unit_lifetime("enemy"),
            "formation_damage_pct": self.formation_damage_pct(),
            "top_damage_types": self.top_unit_types_by_damage(),
            "stance_kills": self.stance_effectiveness(),
            "incidents": len(self._scorecards),
            "incident_grades": Counter(sc.outcome for sc in self._scorecards),
            # UX
            "hotkey_count": self.hotkey_count,
            "click_count": self.click_count,
            "hotkey_pct": self.hotkey_pct(),
            "pause_count": self.pause_count,
            "pause_duration": self.pause_total_duration,
            "advisor_opens": self.advisor_open_count,
            "advisor_duration": self.advisor_total_duration,
            "first_action_time": self.first_action_time,
            "camera_distance": self.camera_distance,
            "top_selections": top_sel_strs,
        }

    def write_ux_summary(self, t: float) -> None:
        """Write final UX row to CSV."""
        if self._closed:
            return
        top_sel = self.selection_counts.most_common(3)
        sel_strs = [f"{name}({cnt})" for name, cnt in top_sel]
        while len(sel_strs) < 3:
            sel_strs.append("")
        self._ux_writer.writerow([
            f"{t:.1f}", self.hotkey_count, self.click_count,
            f"{self.hotkey_pct():.1f}",
            self.pause_count, f"{self.pause_total_duration:.1f}",
            self.advisor_open_count, f"{self.advisor_total_duration:.1f}",
            f"{self.camera_distance:.0f}",
            f"{self.first_action_time:.1f}" if self.first_action_time else "",
            sel_strs[0], sel_strs[1], sel_strs[2]
        ])
        self._ux_file.flush()

    def close(self, game_time: float = 0.0) -> None:
        if self._closed:
            return
        self.write_ux_summary(game_time)
        self._sc_file.flush()
        self._sc_file.close()
        self._ux_file.flush()
        self._ux_file.close()
        self._closed = True
