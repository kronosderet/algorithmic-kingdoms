# ---------------------------------------------------------------------------
# Event Logger — Lightweight CSV game event recorder
# ---------------------------------------------------------------------------
import csv
import os
import sys
from datetime import datetime
from collections import Counter


class EventLogger:
    """Records key game events to a CSV file for balance analysis."""

    COLUMNS = [
        "game_time",       # float: seconds since game start
        "wall_clock",      # str: ISO timestamp
        "event_type",      # str: WAVE_START, UNIT_KILLED, etc.
        "wave",            # int: current wave number
        "detail_1",        # str: primary (killer type, building type, ...)
        "detail_2",        # str: secondary (killed type, rank, ...)
        "detail_3",        # str: tertiary (bounty, amount, ...)
        "numeric_value",   # float: key numeric value
        "note",            # str: free-form context
    ]

    def __init__(self, difficulty):
        self._rows = []
        self._closed = False
        self._flush_threshold = 50
        self._difficulty = difficulty

        # summary counters — incremented by log()
        self._counts = Counter()
        self._total_bounty = 0
        self._game_duration = 0.0
        self._waves_survived = 0

        # resolve output directory
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))

        logs_dir = os.path.join(base, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"game_{difficulty}_{timestamp}.csv"
        self._filepath = os.path.join(logs_dir, filename)

        self._file = open(self._filepath, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.COLUMNS)

    def log(self, game_time, event_type, wave=0, detail_1="", detail_2="",
            detail_3="", numeric_value=0, note=""):
        """Append one event row. Call from anywhere via game.logger.log(...)."""
        if self._closed:
            return

        wall = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self._writer.writerow([
            f"{game_time:.1f}", wall, event_type, wave,
            detail_1, detail_2, detail_3, numeric_value, note
        ])

        # update summary counters
        self._game_duration = game_time
        if event_type == "UNIT_KILLED":
            self._counts["kills"] += 1
            self._total_bounty += numeric_value
        elif event_type == "WAVE_CLEARED":
            self._waves_survived = max(self._waves_survived, wave)
        elif event_type == "RANK_UP":
            self._counts["rank_ups"] += 1
        elif event_type == "BUILDING_RUINED":
            self._counts["buildings_lost"] += 1
        elif event_type == "BUILDING_DESTROYED":
            self._counts["buildings_destroyed"] += 1
        elif event_type == "PLAYER_UNIT_LOST":
            self._counts["player_units_lost"] += 1
        elif event_type == "ENEMY_ESCAPED":
            self._counts["enemies_escaped"] += 1
        elif event_type == "RESOURCE_DEPOSIT":
            self._counts["deposits"] += 1
        elif event_type == "BUILDING_PLACED":
            self._counts["buildings_placed"] += 1
        elif event_type == "BUILDING_COMPLETE":
            self._counts["buildings_completed"] += 1
        elif event_type == "TRAINING_STARTED":
            self._counts["units_trained"] += 1
        elif event_type == "WORKER_RANK_UP":
            self._counts["worker_rank_ups"] += 1
        elif event_type == "TOWER_UPGRADE":
            self._counts["tower_upgrades"] += 1

        self._rows.append(1)  # cheap counter for flush check
        if len(self._rows) >= self._flush_threshold:
            self._file.flush()
            self._rows.clear()

    def write_summary(self, game):
        """Append a GAME_SUMMARY row with aggregate stats."""
        if self._closed:
            return

        # gather final resource totals
        r = game.resources
        res_str = f"Flux:{int(r.gold)} Fiber:{int(r.wood)} Ore:{int(r.iron)} Alloy:{int(r.steel)} Crystal:{int(r.stone)}"
        if game.game_won:
            outcome = "victory"
        elif getattr(game, 'game_surrendered', False):
            outcome = "surrender"
        else:
            outcome = "defeat"

        summary_note = (
            f"kills:{self._counts['kills']} "
            f"losses:{self._counts['player_units_lost']} "
            f"bounty:{self._total_bounty} "
            f"rank_ups:{self._counts['rank_ups']} "
            f"bldg_lost:{self._counts['buildings_lost']} "
            f"bldg_destr:{self._counts['buildings_destroyed']} "
            f"escaped:{self._counts['enemies_escaped']} "
            f"deposits:{self._counts['deposits']} "
            f"bldg_placed:{self._counts['buildings_placed']} "
            f"bldg_complete:{self._counts['buildings_completed']} "
            f"trained:{self._counts['units_trained']} "
            f"worker_rank_ups:{self._counts['worker_rank_ups']} "
            f"tower_upgrades:{self._counts['tower_upgrades']} "
            f"resources:{res_str}"
        )

        self.log(
            self._game_duration, "GAME_SUMMARY",
            wave=self._waves_survived,
            detail_1=outcome,
            detail_2=self._difficulty,
            detail_3=f"{self._game_duration:.0f}s",
            numeric_value=self._counts["kills"],
            note=summary_note
        )

    def close(self, game=None):
        """Flush and close the log file. Pass game for summary row."""
        if self._closed:
            return
        if game:
            self.write_summary(game)
        self._file.flush()
        self._file.close()
        self._closed = True
