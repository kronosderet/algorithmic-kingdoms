import random
import math
from collections import Counter
import constants
from constants import (DIFFICULTY_PROFILES, ENEMY_DEFS, ENEMY_VETERAN_BONUS,
                       SPAWN_MARGIN, SPAWN_RETRIES,
                       STRAGGLER_ROOT_WAVES, STRAGGLER_METAMORPH_WAVES,
                       RESONANCE_DISSONANCE_CHANCE,
                       RESONANCE_HISTORY_WAVES,
                       INCIDENT_CATALOGUE, INCIDENT_TIERS,
                       TIER_TENSION_THRESHOLDS, TIER_STAT_SCALING,
                       OUTCOME_TENSION_DELTA, OUTCOME_COOLDOWN_MULT,
                       OUTCOME_PAIN_THRESHOLDS, OUTCOME_DOMINATED_MAX_TIME,
                       OUTCOME_WON_MAX_ESCAPES,
                       INCIDENT_FOREBODING_MIN, INCIDENT_FOREBODING_MAX,
                       INCIDENT_IMMINENT_DURATION,
                       INCIDENT_AFTERMATH_MIN, INCIDENT_AFTERMATH_MAX,
                       FALSE_CALM_CHANCE, FALSE_CALM_MULT,
                       ARC_OPENING, ARC_RISING, ARC_MIDGAME, ARC_CLIMAX,
                       SCOUT_FLEE_CONTACT_TIME, PROBE_RETREAT_TIME,
                       NARRATIVE_CALM, NARRATIVE_CALM_FALSE,
                       NARRATIVE_ACTIVE, NARRATIVE_AFTERMATH)
from utils import dist, clamp, tile_center, pos_to_tile
from entities import Unit, Building


# FSM States
STATE_CALM = "calm"
STATE_FOREBODING = "foreboding"
STATE_IMMINENT = "imminent"
STATE_ACTIVE = "active"
STATE_AFTERMATH = "aftermath"


class EnemyAI:
    def __init__(self, difficulty="medium"):
        profile = DIFFICULTY_PROFILES[difficulty]
        self.difficulty = difficulty

        # --- Incident Director state ---
        self.incident_number = 0
        self.incidents_required = profile["incidents_required"]
        self.game_won = False

        # Tension (0.0 - 1.0)
        self.tension = 0.0
        self.tension_drift = profile["tension_drift"]

        # Timing
        self.first_incident_time = profile["first_incident_time"]
        self.min_cooldown = profile["min_cooldown"]
        self.base_cooldown = profile["base_cooldown"]

        # Scaling
        self.incident_hp_scale = profile["incident_hp_scale"]
        self.incident_atk_scale = profile["incident_atk_scale"]
        self.incident_unlock = profile.get("incident_unlock", {})

        # Bounty / bonus (kept from old system)
        self.kill_bounty_base = profile["kill_bounty_base"]
        self.wave_bonus_gold = profile["wave_bonus_gold"]
        self.wave_bonus_wood = profile["wave_bonus_wood"]
        self.wave_bonus_steel = profile["wave_bonus_steel"]

        # FSM
        self.state = STATE_CALM
        self.state_timer = 0.0
        self.cooldown_duration = self.first_incident_time  # first calm = first_incident_time
        self.first_incident_sent = False
        self.is_false_calm = False

        # Current incident
        self.current_flavour: str | None = None
        self.current_incident_data: dict | None = None
        self.incident_start_time = 0.0
        self.incident_enemies_spawned = 0
        self.incident_enemies_killed = 0
        self.incident_enemies_fled = 0
        self.buildings_lost_this_incident = 0
        self.units_lost_this_incident = 0

        # Narrative text (read by GUI)
        self.narrative_text = NARRATIVE_CALM
        self.pending_spawn_edges: list[str] = []  # Phase 5: exposed for UI alerts
        self.last_spawn_edges: list[str] = []     # Phase 2: for minimap flash

        # Last outcome (for cooldown computation)
        self.last_outcome = "won"

        # v10_8: resonance dissonance tracking
        self.formation_history = []

        # Backward compat properties
        # (logger, GUI, and other references may still use wave_number / max_waves)

    # --- Backward compatibility ---
    @property
    def wave_number(self):
        return self.incident_number

    @wave_number.setter
    def wave_number(self, v):
        self.incident_number = v

    @property
    def max_waves(self):
        return self.incidents_required

    # ------------------------------------------------------------------
    # Main update — FSM tick
    # ------------------------------------------------------------------
    def update(self, dt, game):
        if self.game_won:
            return

        self.state_timer += dt

        if self.state == STATE_CALM:
            self._update_calm(dt, game)
        elif self.state == STATE_FOREBODING:
            self._update_foreboding(dt, game)
        elif self.state == STATE_IMMINENT:
            self._update_imminent(dt, game)
        elif self.state == STATE_ACTIVE:
            self._update_active(dt, game)
        elif self.state == STATE_AFTERMATH:
            self._update_aftermath(dt, game)

    def _enter_state(self, new_state):
        self.state = new_state
        self.state_timer = 0.0

    # ------------------------------------------------------------------
    # CALM — passive tension drift, wait for cooldown
    # ------------------------------------------------------------------
    def _update_calm(self, dt, game):
        # Passive tension drift (caps acceleration to prevent runaway)
        game_minutes = game.game_time / 600.0
        accel = min(2.5, 1.0 + game_minutes)  # cap at 2.5x drift
        self.tension += self.tension_drift * accel * dt
        self.tension = min(1.0, self.tension)

        if self.state_timer >= self.cooldown_duration:
            # Pick next incident
            self._select_incident(game)
            self._enter_state(STATE_FOREBODING)
            assert self.current_incident_data is not None
            self.narrative_text = self.current_incident_data["narrative_foreboding"]
            if self.is_false_calm:
                game.add_notification(NARRATIVE_CALM_FALSE, 3.0, (180, 180, 100))
                self.is_false_calm = False

    # ------------------------------------------------------------------
    # FOREBODING — narrative warning, duration scales with tension
    # ------------------------------------------------------------------
    def _update_foreboding(self, dt, game):
        # Higher tension = shorter foreboding
        t = self.tension
        duration = INCIDENT_FOREBODING_MAX - (INCIDENT_FOREBODING_MAX - INCIDENT_FOREBODING_MIN) * t
        if self.state_timer >= duration:
            self._enter_state(STATE_IMMINENT)
            assert self.current_incident_data is not None
            self.narrative_text = self.current_incident_data["narrative_imminent"]
            # Phase 5: pre-compute spawn edges for UI alert
            directions = self.current_incident_data.get("directions", 1)
            self.pending_spawn_edges = self._pick_edges_n(directions)
            game.add_notification(self.current_incident_data["narrative_imminent"],
                                  2.5, (255, 100, 50))

    # ------------------------------------------------------------------
    # IMMINENT — final warning, then spawn
    # ------------------------------------------------------------------
    def _update_imminent(self, dt, game):
        if self.state_timer >= INCIDENT_IMMINENT_DURATION:
            self._spawn_incident(game)
            self._enter_state(STATE_ACTIVE)
            self.narrative_text = NARRATIVE_ACTIVE
            self.incident_start_time = game.game_time

    # ------------------------------------------------------------------
    # ACTIVE — combat, wait for all enemies dead/fled
    # ------------------------------------------------------------------
    def _update_active(self, dt, game):
        # v10_gamma: tension slowly bleeds during combat (catharsis)
        self.tension = max(0.0, self.tension - 0.02 * dt)
        # Check if all incident enemies are dead or fled
        alive = sum(1 for e in game.enemy_units if e.alive)
        if alive == 0:
            self._resolve_incident(game)

    # ------------------------------------------------------------------
    # AFTERMATH — brief pause, award bonus, adjust tension
    # ------------------------------------------------------------------
    def _update_aftermath(self, dt, game):
        # v10_gamma: tension decays faster during aftermath (relief)
        self.tension = max(0.0, self.tension - 0.06 * dt)
        duration = INCIDENT_AFTERMATH_MIN + (INCIDENT_AFTERMATH_MAX - INCIDENT_AFTERMATH_MIN) * 0.5
        if self.state_timer >= duration:
            # Check for victory
            if self.incident_number >= self.incidents_required:
                self.game_won = True
                return
            # Compute next cooldown
            self._compute_cooldown()
            self._enter_state(STATE_CALM)
            self.narrative_text = NARRATIVE_CALM

    # ------------------------------------------------------------------
    # Incident selection
    # ------------------------------------------------------------------
    def _select_incident(self, game):
        progress = self.incident_number / max(1, self.incidents_required)

        # Determine available tiers based on dramatic arc + tension
        available_tiers = []
        if progress < ARC_OPENING:
            available_tiers = ["light"]
        elif progress < ARC_RISING:
            available_tiers = ["light", "medium"]
        elif progress < ARC_MIDGAME:
            available_tiers = ["light", "medium", "strong"]
        elif progress < ARC_CLIMAX:
            available_tiers = ["light", "medium", "strong", "deadly"]
        else:
            available_tiers = ["light", "medium", "strong", "deadly"]

        # Filter by tension threshold
        available_tiers = [t for t in available_tiers
                           if self.tension >= TIER_TENSION_THRESHOLDS[t]]

        # First incident is always scout
        if self.incident_number == 0:
            self.current_flavour = "scout"
            self.current_incident_data = INCIDENT_CATALOGUE["scout"]
            return

        # Finale: last incident is always deadly (if available)
        if self.incident_number == self.incidents_required - 1:
            if "deadly" in available_tiers or progress >= ARC_CLIMAX:
                flavours = INCIDENT_TIERS["deadly"]
                self.current_flavour = random.choice(flavours)
                self.current_incident_data = INCIDENT_CATALOGUE[self.current_flavour]
                return

        # Pick highest available tier, weighted toward it
        # 60% chance highest tier, 30% second highest, 10% lower
        if not available_tiers:
            available_tiers = ["light"]

        weights = []
        for i, t in enumerate(available_tiers):
            if i == len(available_tiers) - 1:
                weights.append(0.60)
            elif i == len(available_tiers) - 2:
                weights.append(0.30)
            else:
                weights.append(0.10 / max(1, len(available_tiers) - 2))

        chosen_tier = random.choices(available_tiers, weights=weights, k=1)[0]

        # Filter flavours by enemy type unlock
        possible = []
        for flavour_name in INCIDENT_TIERS[chosen_tier]:
            flavour = INCIDENT_CATALOGUE[flavour_name]
            # Check all composition types are unlocked
            all_unlocked = True
            for etype in flavour["composition"]:
                unlock_at = self.incident_unlock.get(etype, 0)
                if self.incident_number < unlock_at:
                    all_unlocked = False
                    break
            if all_unlocked:
                possible.append(flavour_name)

        # Fallback: if nothing unlocked in this tier, drop to lower tier
        if not possible:
            for fallback_tier in reversed(available_tiers):
                for flavour_name in INCIDENT_TIERS[fallback_tier]:
                    flavour = INCIDENT_CATALOGUE[flavour_name]
                    all_unlocked = True
                    for etype in flavour["composition"]:
                        unlock_at = self.incident_unlock.get(etype, 0)
                        if self.incident_number < unlock_at:
                            all_unlocked = False
                            break
                    if all_unlocked:
                        possible.append(flavour_name)
                if possible:
                    break

        if not possible:
            possible = ["scout"]  # absolute fallback

        self.current_flavour = random.choice(possible)
        self.current_incident_data = INCIDENT_CATALOGUE[self.current_flavour]

    # ------------------------------------------------------------------
    # Spawn incident enemies
    # ------------------------------------------------------------------
    def _spawn_incident(self, game):
        # v10_7: process stragglers before spawning
        self._process_stragglers(game)

        self.incident_number += 1
        assert self.current_incident_data is not None
        data = self.current_incident_data
        tier = data["tier"]

        # Count
        lo, hi = data["count_range"]
        count = random.randint(lo, hi)

        # Stat scaling
        tier_mult = TIER_STAT_SCALING[tier]
        hp_mult = 1.0 + self.incident_hp_scale * self.incident_number * tier_mult
        atk_mult = 1.0 + self.incident_atk_scale * self.incident_number * tier_mult

        # Build composition from catalogue ratios
        types = self._build_composition(data, count, game)

        # Edges — use pre-computed from IMMINENT phase if available
        if self.pending_spawn_edges:
            edges = self.pending_spawn_edges
        else:
            directions = data.get("directions", 1)
            edges = self._pick_edges_n(directions)
        self.last_spawn_edges = edges
        self.pending_spawn_edges = []

        # Reset incident tracking
        self.incident_enemies_spawned = len(types)
        self.incident_enemies_killed = 0
        self.incident_enemies_fled = 0
        self.buildings_lost_this_incident = 0
        self.units_lost_this_incident = 0

        # Log
        comp = Counter(types)
        comp_str = " ".join(f"{v}x{k.replace('enemy_', '')}" for k, v in comp.items())
        edge_str = ",".join(edges)
        game.logger.log(game.game_time, "INCIDENT_START", self.incident_number,
                        f"[{self.current_flavour}]", edge_str, comp_str,
                        len(types), f"hp:{hp_mult:.2f} atk:{atk_mult:.2f}")

        # Distribute across edges
        per_edge = len(types) // len(edges)
        remainder = len(types) % len(edges)

        # Behaviour flag
        behaviour = data.get("behaviour")
        dissonance_override = data.get("dissonance_override", None)

        idx = 0
        for ei, edge in enumerate(edges):
            edge_count = per_edge + (1 if ei < remainder else 0)
            for _ in range(edge_count):
                if idx >= len(types):
                    break
                utype = types[idx]
                idx += 1

                c, r = self._get_spawn_pos(edge, game)
                if c is None:
                    continue

                wx, wy = tile_center(c, r)
                enemy = self._create_enemy(wx, wy, utype, hp_mult, atk_mult, game,
                                           behaviour=behaviour,
                                           dissonance_override=dissonance_override)

        # Spawn escaped veterans
        self._spawn_veterans(game, hp_mult, atk_mult)

    def _build_composition(self, data, count, game):
        """Build enemy type list from catalogue composition ratios + counter-pick."""
        composition = data["composition"]

        # Apply counter-pick adjustments (same logic, modifies ratios)
        adjusted = dict(composition)
        self._counter_pick_adjust(adjusted, game)

        # Normalize
        total = sum(adjusted.values())
        if total <= 0:
            return ["enemy_soldier"] * count

        # Build cumulative distribution
        keys = list(adjusted.keys())
        cum = []
        running = 0.0
        for k in keys:
            running += adjusted[k] / total
            cum.append(running)

        types = []
        for _ in range(count):
            roll = random.random()
            for i, threshold in enumerate(cum):
                if roll < threshold:
                    types.append(keys[i])
                    break
            else:
                types.append(keys[0])
        return types

    def _counter_pick_adjust(self, probs, game):
        """Tweak composition ratios based on player state (counter-pick AI)."""
        tower_count = sum(1 for b in game.player_buildings
                          if b.building_type == "tower" and b.built
                          and b.alive and not getattr(b, 'ruined', False))
        soldier_count = sum(1 for u in game.player_units
                            if u.unit_type == "soldier" and u.alive)
        archer_count = sum(1 for u in game.player_units
                           if u.unit_type == "archer" and u.alive)
        worker_count = sum(1 for u in game.player_units
                           if u.unit_type == "worker" and u.alive)
        total_military = soldier_count + archer_count

        n = self.incident_number
        unlock = self.incident_unlock

        # Many towers, weak army → boost Hexweaver (building destroyer)
        if "enemy_siege" in probs and n >= unlock.get("enemy_siege", 99):
            if tower_count >= 3 and total_military < 5:
                probs["enemy_siege"] = probs.get("enemy_siege", 0) + 0.10
        # Strong economy → boost raiders
        if "enemy_raider" in probs and n >= unlock.get("enemy_raider", 99):
            if worker_count >= 6:
                probs["enemy_raider"] = probs.get("enemy_raider", 0) + 0.08
        # Archer-heavy → boost shieldbearers
        if "enemy_shieldbearer" in probs and n >= unlock.get("enemy_shieldbearer", 99):
            if total_military > 0 and archer_count / max(1, total_military) > 0.5:
                probs["enemy_shieldbearer"] = probs.get("enemy_shieldbearer", 0) + 0.08

        # v10_beta: Counter player formations
        most_used = self._get_most_used_formation()
        if most_used is not None and n >= 5:
            from constants import (FORMATION_SIERPINSKI, FORMATION_KOCH,
                                   FORMATION_POLAR_ROSE, FORMATION_GOLDEN_SPIRAL)
            # Sierpinski (anti-AOE spread) → boost single-target elites
            if most_used == FORMATION_SIERPINSKI:
                if "enemy_elite" in probs:
                    probs["enemy_elite"] = probs.get("enemy_elite", 0) + 0.06
            # Koch (defensive ring) → boost Hexweaver to break perimeter
            elif most_used == FORMATION_KOCH:
                if "enemy_siege" in probs and n >= unlock.get("enemy_siege", 99):
                    probs["enemy_siege"] = probs.get("enemy_siege", 0) + 0.06
            # Polar Rose (clumped petals) → boost Thornknight for single-target burst
            elif most_used == FORMATION_POLAR_ROSE:
                if "enemy_elite" in probs and n >= unlock.get("enemy_elite", 99):
                    probs["enemy_elite"] = probs.get("enemy_elite", 0) + 0.06
            # Golden Spiral (assault) → boost shieldbearers for frontline
            elif most_used == FORMATION_GOLDEN_SPIRAL:
                if "enemy_shieldbearer" in probs and n >= unlock.get("enemy_shieldbearer", 99):
                    probs["enemy_shieldbearer"] = probs.get("enemy_shieldbearer", 0) + 0.06

    def _pick_edges_n(self, n):
        """Return n random edges."""
        edges = ["top", "bottom", "left", "right"]
        n = min(n, len(edges))
        return random.sample(edges, n)

    # ------------------------------------------------------------------
    # Resolve incident — classify outcome, adjust tension, award bonus
    # ------------------------------------------------------------------
    def _resolve_incident(self, game):
        total = max(1, self.incident_enemies_spawned)
        pain_ratio = (self.buildings_lost_this_incident * 3
                      + self.units_lost_this_incident) / total
        combat_time = game.game_time - self.incident_start_time

        # Classify outcome
        if (pain_ratio < OUTCOME_PAIN_THRESHOLDS["dominated"]
                and self.incident_enemies_fled == 0
                and combat_time < OUTCOME_DOMINATED_MAX_TIME):
            outcome = "dominated"
        elif (pain_ratio < OUTCOME_PAIN_THRESHOLDS["won"]
              and self.incident_enemies_fled <= OUTCOME_WON_MAX_ESCAPES):
            outcome = "won"
        elif pain_ratio < OUTCOME_PAIN_THRESHOLDS["costly"]:
            outcome = "costly"
        else:
            outcome = "devastating"

        self.last_outcome = outcome

        # Adjust tension
        self.tension += OUTCOME_TENSION_DELTA[outcome]
        self.tension = max(0.0, min(1.0, self.tension))

        # Track formation usage for dissonance
        self.track_formation_usage(game)

        # Award bonus resources
        game.resources.add("gold", self.wave_bonus_gold)
        game.resources.add("wood", self.wave_bonus_wood)
        game.resources.add("steel", self.wave_bonus_steel)

        # Log
        game.logger.log(game.game_time, "INCIDENT_RESOLVED", self.incident_number,
                        f"[{self.current_flavour}]", outcome,
                        f"pain:{pain_ratio:.2f}", f"tension:{self.tension:.2f}",
                        f"time:{combat_time:.1f}s")

        # Notify
        outcome_msgs = {
            "dominated": ("Threat eliminated effortlessly.", (100, 255, 100)),
            "won": ("Threat repelled.", (150, 255, 150)),
            "costly": ("We held... but at great cost.", (255, 200, 100)),
            "devastating": ("Devastation. We barely survived.", (255, 80, 80)),
        }
        msg, color = outcome_msgs[outcome]
        game.add_notification(msg, 3.0, color)

        # Callback to game for wave-clear logic (unlocks, etc.)
        if hasattr(game, '_on_attack_resolved'):
            game._on_attack_resolved(self.incident_number, outcome)

        self._enter_state(STATE_AFTERMATH)
        self.narrative_text = NARRATIVE_AFTERMATH

    # ------------------------------------------------------------------
    # Cooldown computation
    # ------------------------------------------------------------------
    def _compute_cooldown(self):
        progress = self.incident_number / max(1, self.incidents_required)

        base = self.base_cooldown
        outcome_mult = OUTCOME_COOLDOWN_MULT.get(self.last_outcome, 1.0)
        late_game = max(0.5, 1.0 - progress * 0.3)

        cooldown = base * outcome_mult * late_game

        # False calm: 15% chance of extended delay with narrative
        if random.random() < FALSE_CALM_CHANCE:
            cooldown *= FALSE_CALM_MULT
            self.is_false_calm = True
        else:
            self.is_false_calm = False

        # Floor
        cooldown = max(self.min_cooldown, cooldown)
        self.cooldown_duration = cooldown

    # ------------------------------------------------------------------
    # Straggler system (kept from v10_7)
    # ------------------------------------------------------------------
    def _process_stragglers(self, game):
        n = self.incident_number
        for e in game.enemy_units:
            if not e.alive:
                continue
            spawn_inc = getattr(e, 'spawn_wave', n)
            wave_age = n - spawn_inc
            if wave_age >= STRAGGLER_METAMORPH_WAVES and not e.metamorphosed:
                e.metamorphose()
                game.add_notification("A straggler's dissonance has taken root... Bitter Root!",
                                      2.5, (255, 60, 60))
            elif wave_age >= STRAGGLER_ROOT_WAVES and not e.rooted and not e.metamorphosed:
                e.root()

    # ------------------------------------------------------------------
    # Veterans (kept from v9)
    # ------------------------------------------------------------------
    def _spawn_veterans(self, game, hp_mult, atk_mult):
        if not hasattr(game, 'escaped_enemies') or not game.escaped_enemies:
            return
        vet_mult = 1.0 + ENEMY_VETERAN_BONUS
        for vet in game.escaped_enemies:
            edge = random.choice(["top", "bottom", "left", "right"])
            c, r = self._get_spawn_pos(edge, game)
            if c is None:
                continue
            wx, wy = tile_center(c, r)
            enemy = self._create_enemy(wx, wy, vet["unit_type"],
                                       hp_mult * vet_mult, atk_mult * vet_mult, game)
            enemy.building_mult = vet.get("building_mult", 1.0)
            stored_xp = vet.get("xp", 0)
            if stored_xp > 0:
                enemy.xp = stored_xp
                enemy._check_rank_up()
                enemy.force_apply_rank_bonuses()
        game.escaped_enemies.clear()

    # ------------------------------------------------------------------
    # Enemy creation (kept, extended with behaviour)
    # ------------------------------------------------------------------
    def _create_enemy(self, wx, wy, utype, hp_mult, atk_mult, game,
                      behaviour=None, dissonance_override=None):
        enemy = Unit(wx, wy, utype, "enemy")
        enemy.max_hp = int(enemy.max_hp * hp_mult)
        enemy.hp = enemy.max_hp
        enemy.attack_power = int(enemy.attack_power * atk_mult)
        enemy._base_hp = enemy.max_hp
        enemy._base_attack = enemy.attack_power
        enemy._base_range = enemy.attack_range
        enemy.spawn_wave = self.incident_number

        # Incident behaviour
        if behaviour == "flee_on_contact":
            enemy.incident_behaviour = "flee_on_contact"
            enemy.contact_timer = 0.0
            enemy.flee_contact_time = SCOUT_FLEE_CONTACT_TIME
        elif behaviour == "probe_retreat":
            enemy.incident_behaviour = "probe_retreat"
            enemy.probe_timer = 0.0
            enemy.probe_duration = PROBE_RETREAT_TIME
        elif behaviour == "economy_target":
            enemy.incident_behaviour = "economy_target"
        else:
            enemy.incident_behaviour = None

        # Dissonance — visual nullification + v10_beta: tactical targeting
        dissonance_chance = RESONANCE_DISSONANCE_CHANCE
        if dissonance_override is not None:
            dissonance_chance = dissonance_override
        if random.random() < dissonance_chance:
            most_used = self._get_most_used_formation()
            if most_used >= 0:
                enemy.dissonant_formation = most_used
                # v10_beta: dissonant enemies prioritize squads using that formation
                enemy._dissonance_target_formation = most_used

        # Target
        prefer_econ = (behaviour == "economy_target")
        prefer_bldg = (getattr(enemy, 'building_mult', 1.0) > 1.0)
        target = self._find_target(enemy, game,
                                   prefer_buildings=prefer_bldg,
                                   prefer_economy=prefer_econ)
        if target:
            enemy.target_entity = target
            # Path to target so enemies don't walk in straight lines
            tc, tr = pos_to_tile(target.x, target.y)
            enemy._path_to(tc, tr, game)
            if enemy.path:
                enemy.state = "moving"
            else:
                enemy.state = "attacking"
        game.enemy_units.append(enemy)
        return enemy

    # ------------------------------------------------------------------
    # Spawn position (unchanged)
    # ------------------------------------------------------------------
    def _get_spawn_pos(self, edge, game):
        m = SPAWN_MARGIN
        spawn_fn = {
            "top":    lambda: (random.randint(m, constants.MAP_COLS - m - 1), 1),
            "bottom": lambda: (random.randint(m, constants.MAP_COLS - m - 1), constants.MAP_ROWS - 2),
            "left":   lambda: (1, random.randint(m, constants.MAP_ROWS - m - 1)),
            "right":  lambda: (constants.MAP_COLS - 2, random.randint(m, constants.MAP_ROWS - m - 1)),
        }
        for _ in range(SPAWN_RETRIES):
            c, r = spawn_fn[edge]()
            attempts = 0
            while not game.game_map.is_walkable(c, r) and attempts < 15:
                c += random.choice([-1, 0, 1])
                r += random.choice([-1, 0, 1])
                c = clamp(c, 1, constants.MAP_COLS - 2)
                r = clamp(r, 1, constants.MAP_ROWS - 2)
                attempts += 1
            if game.game_map.is_walkable(c, r):
                return c, r
        return None, None

    # ------------------------------------------------------------------
    # Kill bounty (scales with incident number)
    # ------------------------------------------------------------------
    def get_kill_bounty(self):
        return self.kill_bounty_base + self.incident_number

    # ------------------------------------------------------------------
    # Resonance dissonance helpers (kept from v10_8)
    # ------------------------------------------------------------------
    def track_formation_usage(self, game):
        counts = Counter()
        for sq in game.player_squad_mgr.squad_list:
            if sq.alive_count > 0:
                counts[sq.formation] += 1
        self.formation_history.append(counts)
        if len(self.formation_history) > RESONANCE_HISTORY_WAVES:
            self.formation_history.pop(0)

    def _get_most_used_formation(self):
        if not self.formation_history:
            return -1
        total = Counter()
        for c in self.formation_history:
            total.update(c)
        if not total:
            return -1
        return total.most_common(1)[0][0]

    # ------------------------------------------------------------------
    # Target selection (extended with economy preference)
    # ------------------------------------------------------------------
    def _find_target(self, unit, game, prefer_buildings=False, prefer_economy=False):
        best = None
        best_score = -1
        best_ruin = None
        best_ruin_score = -1

        economy_types = {"goldmine_hut", "lumber_camp", "quarry_hut", "iron_depot",
                         "sawmill", "goldmine", "stoneworks", "iron_works", "forge",
                         "refinery"}

        for b in game.player_buildings:
            if not b.alive:
                continue
            score = unit._score_target(b)
            # Boost economy buildings if economy_target behaviour
            if prefer_economy and b.building_type in economy_types:
                score *= 2.5
            if getattr(b, 'ruined', False):
                if score > best_ruin_score:
                    best_ruin_score = score
                    best_ruin = b
            else:
                if score > best_score:
                    best_score = score
                    best = b

        if prefer_buildings and best:
            return best

        for u in game.player_units:
            if not u.alive:
                continue
            score = unit._score_target(u)
            # Economy target: boost worker score
            if prefer_economy and u.unit_type == "worker":
                score *= 2.0
            if score > best_score:
                best_score = score
                best = u

        return best if best else best_ruin

    # ------------------------------------------------------------------
    # Pressure tracking (simplified — now uses outcome classification)
    # ------------------------------------------------------------------
    def record_wave_pressure(self, wave_enemy_count):
        """Kept for backward compat — no longer drives difficulty scaling."""
        self.buildings_lost_this_incident = 0
        self.units_lost_this_incident = 0
