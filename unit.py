import math
import random
import pygame
import constants
from constants import (UNIT_DEFS, ENEMY_DEFS, UNIT_COLORS, ENEMY_COLORS,
                       UNIT_LABELS, UNIT_RADIUS, BUILDING_DEFS, BUILDING_LABELS,
                       TILE_SIZE,
                       SCREEN_WIDTH, GAME_AREA_Y, GAME_AREA_H,
                       COL_SELECT, COL_GOLD, COL_WOOD, COL_IRON_C, COL_STONE,
                       TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON,
                       TERRAIN_STONE, TERRAIN_RESOURCE_MAP,
                       GATHER_TIME, GATHER_AMOUNT, IRON_GATHER_AMOUNT,
                       ARROW_BASE_SPREAD, ARROW_MIN_SPREAD,
                       ARROW_FLIGHT_TIME, ARROW_LEAD_MIN_RANK,
                       ARROW_LEAD_FACTOR_PER_RANK,
                       FORMATION_COMBAT_LEASH,
                       WORKER_FLEE_RADIUS, WORKER_SAFE_TIME,
                       WORKER_FLEE_DISTANCE, REPAIR_RATE, REPAIR_COST_FRACTION,
                       ENEMY_FLEE_HP_FRACTION,
                       RESOURCE_TO_SKILL, WORKER_RANK_XP,
                       WORKER_RANK_SPEED_BONUS, WORKER_RANKS,
                       WORKER_SKILL_NAMES, WORKER_SKILL_COLORS,
                       BUILDER_XP_PER_SECOND,
                       PATH_ARRIVAL_THRESHOLD, BUILD_PROXIMITY,
                       IDLE_AGGRO_RANGE,
                       RANK_XP_THRESHOLDS, RANK_BONUSES,
                       SQUAD_FOLLOW_DIST,
                       BUILDING_PRIORITY, UNIT_PRIORITY, RUIN_PRIORITY_MULT,
                       DISTANCE_NORMALIZATION, RANK_TARGETING_NOISE,
                       LOW_HP_FINISH_BONUS, LOW_HP_FINISH_THRESHOLD,
                       ENGAGED_TARGET_BONUS,
                       MORALE_CHECK_INTERVAL, MORALE_SCAN_RADIUS,
                       MORALE_FLEE_RATIO, MORALE_LEADER_AURA,
                       MORALE_LEADER_MIN_RANK, MORALE_RANK_RESISTANCE,
                       RETARGET_INTERVAL, RETARGET_SWITCH_THRESHOLD,
                       THREAT_BONUS, TERRAIN_MOVE_COST,
                       TRAIT_POOL, TRAIT_CONFLICTS, TRAIT_ROLL_WEIGHTS,
                       TRAIT_MODIFIERS,
                       GARRISON_MAX_WORKERS,
                       GARRISON_SPAWN_RADIUS,
                       SCAFFOLD_AURA_RANGE, SCAFFOLD_SPEED_BONUS,
                       PRODUCTION_RATES,
                       TOWER_UPGRADE_TIME,
                       STANCE_AGGRESSIVE, STANCE_DEFENSIVE, STANCE_GUARD,
                       STANCE_HUNT, STANCE_GUARD_AGGRO_BONUS,
                       FORMATION_SLOT_ARRIVAL, FORMATION_REGROUP_DELAY,
                       SENTINEL_CRY_SPEED_BONUS,
                       METAMORPH_HP_MULT, METAMORPH_ATK_MULT,
                       METAMORPH_SPEED_MULT,
                       WORKER_FLEE_COOLDOWN,
                       LONE_WOLF_ISOLATION_DIST, MORALE_CLUSTER_RADIUS,
                       ARROW_FLIGHT_DISTANCE_NORM,
                       HEALER_FOLLOW_RANGE_MULT, REPATH_COOLDOWN,
                       MOVEMENT_PROFILES, MOVEMENT_PROFILE_DEFAULT,
                       REPULSION_RADIUS, REPULSION_STRENGTH, REPULSION_FALLOFF,
                       FORMATION_SPRING_K, FORMATION_SPRING_DAMP,
                       FORMATION_SPRING_MAX,
                       PHYSICS_ARRIVAL_DIST, PHYSICS_WORKER_SNAP_DIST,
                       ENERGY_PROFILES, ENERGY_PROFILE_DEFAULT,
                       ENERGY_EXHAUSTED_SPEED, ENERGY_EXHAUSTED_THRESHOLD,
                       ENERGY_TIRED_COOLDOWN_MULT, ENERGY_IDLE_REGEN_MULT,
                       ENERGY_FLEE_DRAIN_MULT, ENERGY_CARRY_REGEN_MULT,
                       ENERGY_CARRY_SPEED_MULT, HARMONY_ENERGY_MULT,
                       MSG_COL_ECONOMY, display_name)
from utils import dist, pos_to_tile, tile_center, draw_text
from pathfinding import a_star
from entity_base import Entity, _process_combat_hit
from squads import formation_slot
from fractal_ui import draw_selection_ring

# ---------------------------------------------------------------------------
# Lazy imports to avoid circular dependencies
# ---------------------------------------------------------------------------
_Arrow = None


def _get_arrow_class():
    global _Arrow
    if _Arrow is None:
        from projectiles import Arrow
        _Arrow = Arrow
    return _Arrow


_Building = None


def _get_building_class():
    global _Building
    if _Building is None:
        from building import Building
        _Building = Building
    return _Building


class Unit(Entity):
    def __init__(self, x, y, unit_type, owner):
        d = UNIT_DEFS.get(unit_type) or ENEMY_DEFS.get(unit_type, {})
        super().__init__(x, y, d.get("hp", 50), owner)
        self.unit_type = unit_type
        self.speed = d.get("speed", 60)
        self.attack_power = d.get("attack", 5)
        self.attack_range = d.get("range", 40)
        self.attack_cd = d.get("cd", 1.0)
        self.attack_timer = 0.0
        self.building_mult = d.get("building_mult", 1.0)  # siege bonus vs buildings
        # v10_6: new enemy type attributes
        self.self_destruct = d.get("self_destruct", False)
        self.frontal_armor = d.get("frontal_armor", 0.0)
        self.heal_rate = d.get("heal_rate", 0.0)
        self.economy_only = d.get("economy_only", False)
        self.aoe_radius = d.get("aoe_radius", 0)

        # v10_delta: physics movement profile
        mp = MOVEMENT_PROFILES.get(unit_type, MOVEMENT_PROFILE_DEFAULT)
        self.accel = mp["accel"]
        self.decel = mp["decel"]
        self.max_speed = mp["max_speed"]
        self.current_speed = 0.0

        # v10_delta: energy / stamina system
        ep = ENERGY_PROFILES.get(unit_type, ENERGY_PROFILE_DEFAULT)
        self.energy = float(ep["max"])
        self.max_energy = float(ep["max"])
        self.energy_regen = float(ep["regen"])
        self.energy_accel_cost = ep.get("accel_cost", 10.0)
        self.energy_cruise_cost = ep.get("cruise_cost", 2.0)
        self.energy_attack_cost = ep.get("attack_cost", 6.0)
        self.energy_gather_cost = ep.get("gather_cost", 0.0)

        # state: idle, moving, gathering, building, attacking, returning
        self.state = "idle"
        self.target_pos = None
        self.target_entity = None
        self.path = []
        self.path_index = 0

        # worker
        self.carry_type = None
        self.carry_amount = 0
        self.gather_timer = 0.0
        self.gather_tile = None  # (col, row)
        self.build_target = None  # Building ref
        self._last_gather_type = None  # tracks resource type for auto-resume
        self.repair_target = None  # Building ref for repair
        # worker flee
        self._saved_task = None
        self._flee_timer = 0.0
        # XP / military rank (v9)
        self.xp = 0
        self.rank = 0  # index into MILITARY_RANKS / RANK_XP_THRESHOLDS
        self._base_hp = self.max_hp
        self._base_attack = self.attack_power
        self._base_range = self.attack_range
        self._base_speed = self.speed
        # v10: worker skill XP system (replaces old single-specialization)
        self.skill_xp = {"lumberjack": 0, "gold_miner": 0, "iron_miner": 0,
                         "stone_mason": 0, "builder": 0, "smelter": 0}
        self.skill_ranks = {"lumberjack": 0, "gold_miner": 0, "iron_miner": 0,
                            "stone_mason": 0, "builder": 0, "smelter": 0}
        self._flee_start_time = 0.0
        # v9.2 morale timer (staggered to avoid per-frame spike)
        self._morale_timer = random.uniform(0, MORALE_CHECK_INTERVAL)
        # v9.3 live retarget timer (staggered)
        self._retarget_timer = random.uniform(0, RETARGET_INTERVAL)
        # v10f: repath cooldown — prevent attack→idle→attack loop when stuck
        self._repath_cooldown = 0.0
        # v10_1: trait system — procedural unit personalities
        self.traits = set()
        self.trait_modifiers = {}
        if unit_type != "worker":
            self._roll_traits()
        # v10_beta: command queue for shift-click waypoints
        self._command_queue = []  # list of (command_type, args) tuples
        # v10_1: attack-move destination (enhanced aggro on arrival)
        self._attack_move_target = None
        # v10_6: stance system (replaces hold_ground)
        self.stance = STANCE_AGGRESSIVE
        # v10_beta: formation lattice timer
        self._out_of_combat_timer = 0.0
        # v10_2: garrison
        self.garrison_target = None
        # v10_2: station target (production buildings)
        self.station_target = None
        # v10_7: Sentinel's Cry buff (attack speed bonus from nearby tower)
        self.sentinel_cry_buff = 0.0
        # v10_7: highlighted by Sentinel's Cry (enemy in dead zone)
        self.sentinel_highlighted = 0.0
        # v10_7: Straggler metamorphosis
        self.spawn_wave = 0       # wave this enemy was spawned in
        self.rooted = False       # straggler has taken root
        self.metamorphosed = False  # straggler has transformed
        # v10_8: Worker flee cooldown
        self._flee_resume_time = -999.0
        # v10_8: Resonance attributes (set per-frame by game._update_resonance)
        self._spiral_miss_chance = 0.0
        self._sierpinski_aoe_factor = 1.0
        self._dissonance_nullified = False
        self._resonance_visual = -1  # -1=none, 0=rose, 1=spiral, 2=sierpinski, 3=koch
        self._koch_slow_factor = 1.0  # 1.0 = no slow; Koch resonance sets < 1.0 on enemies
        self.dissonant_formation = -1  # -1=none, 0-3=anti-formation type
        # v10_9: Incident Director dynamic attributes (set by enemy_ai)
        self.incident_behaviour: str | None = None
        self.contact_timer = 0.0
        self.flee_contact_time = 0.0
        self.probe_timer = 0.0
        self.probe_duration = 0.0
        self._dissonance_target_formation = -1

    # -- Helpers ---------------------------------------------------------------

    def _clear_tasks(self):
        """Reset all task-related state."""
        self.target_entity = None
        self.gather_tile = None
        self.build_target = None
        self.repair_target = None
        self.garrison_target = None
        self.station_target = None
        self._attack_move_target = None

    # -- v10_1: Trait system ---------------------------------------------------

    def _roll_traits(self):
        """Roll 0-2 traits at creation based on unit type and rarity weights."""
        # determine roll count via weighted random
        counts, weights = zip(*TRAIT_ROLL_WEIGHTS.items())
        total = sum(weights)
        r = random.random() * total
        cumulative = 0
        roll_count = 0
        for count, weight in zip(counts, weights):
            cumulative += weight
            if r <= cumulative:
                roll_count = count
                break
        if roll_count == 0:
            return
        # collect eligible traits for this unit type
        eligible = []
        for trait_name, (rarity, allowed_types) in TRAIT_POOL.items():
            if self.unit_type in allowed_types:
                eligible.append((trait_name, rarity))
        if not eligible:
            return
        # weighted sample without conflicts
        random.shuffle(eligible)
        for _ in range(roll_count):
            # build candidate list excluding conflicts with current traits
            candidates = []
            for tname, rarity in eligible:
                if tname in self.traits:
                    continue
                # check for conflict
                conflict = False
                for conflict_set in TRAIT_CONFLICTS:
                    if tname in conflict_set and self.traits & conflict_set:
                        conflict = True
                        break
                if not conflict:
                    candidates.append((tname, rarity))
            if not candidates:
                break
            # weighted random selection
            names, rarities = zip(*candidates)
            total_r = sum(rarities)
            pick = random.random() * total_r
            cum = 0
            chosen = names[0]
            for name, rar in candidates:
                cum += rar
                if pick <= cum:
                    chosen = name
                    break
            self.traits.add(chosen)
        # compute cached modifiers
        self._compute_trait_modifiers()

    def _compute_trait_modifiers(self):
        """Build flat modifier dict from trait set."""
        self.trait_modifiers = {}
        for trait_name in self.traits:
            mods = TRAIT_MODIFIERS.get(trait_name, {})
            for key, value in mods.items():
                if isinstance(value, bool):
                    self.trait_modifiers[key] = value
                else:
                    # multiplicative stacking
                    self.trait_modifiers[key] = self.trait_modifiers.get(key, 1.0) * value

    # -- v10: Worker skill helpers ---------------------------------------------

    def get_skill_rank(self, skill_name):
        """Return rank index (0=Novice, 1=Foreman, 2=Master) for a skill."""
        return self.skill_ranks.get(skill_name, 0)

    def get_skill_speed_bonus(self, skill_name):
        """Return speed bonus fraction for a skill's current rank."""
        rank = self.skill_ranks.get(skill_name, 0)
        return WORKER_RANK_SPEED_BONUS.get(rank, 0.0)

    def grant_skill_xp(self, skill_name, amount, game=None):
        """Grant XP to a worker skill, handling rank-up if threshold reached."""
        if skill_name not in self.skill_xp:
            return
        self.skill_xp[skill_name] += amount
        current_rank = self.skill_ranks[skill_name]
        # check for rank-up
        if current_rank < len(WORKER_RANK_XP) - 1:
            next_threshold = WORKER_RANK_XP[current_rank + 1]
            if self.skill_xp[skill_name] >= next_threshold:
                self.skill_ranks[skill_name] = current_rank + 1
                new_rank = current_rank + 1
                rank_name = WORKER_RANKS[new_rank]
                skill_display = WORKER_SKILL_NAMES.get(skill_name, skill_name)
                if game and hasattr(game, 'add_notification'):
                    color = WORKER_SKILL_COLORS.get(skill_name, (200, 200, 200))
                    game.add_notification(
                        f"Worker → {skill_display} {rank_name}!", 3.0, color)
                if game and hasattr(game, 'logger'):
                    game.logger.log(
                        game.game_time, "WORKER_RANK_UP",
                        game.enemy_ai.wave_number,
                        skill_name, rank_name,
                        str(new_rank),
                        self.skill_xp[skill_name])

    def get_primary_skill(self):
        """Return (skill_name, rank) for highest-ranked skill (XP tiebreak)."""
        best_skill = None
        best_rank = -1
        best_xp = -1
        for skill, rank in self.skill_ranks.items():
            xp = self.skill_xp[skill]
            if rank > best_rank or (rank == best_rank and xp > best_xp):
                best_skill = skill
                best_rank = rank
                best_xp = xp
        if best_rank <= 0 and best_xp <= 0:
            return None, 0
        return best_skill, best_rank

    def _path_to(self, col, row, game, exclude_building=None):
        """Compute A* path, optionally excluding a building's tiles from blocked set."""
        sc, sr = self.get_tile()
        blocked = game.get_blocked_tiles()
        if exclude_building:
            for tile in exclude_building.get_tiles():
                blocked.discard(tile)
        self.path = a_star(sc, sr, col, row, game.game_map, blocked_set=blocked)
        self.path_index = 0

    def _score_target(self, target):
        """Compute utility score for a potential target. Higher = more attractive."""
        # --- Base priority ---
        if isinstance(target, _get_building_class()):
            base = BUILDING_PRIORITY.get(target.building_type, 3.0)
            if getattr(target, 'ruined', False):
                base *= RUIN_PRIORITY_MULT
            elif not target.built:
                base *= 0.5  # under construction
        else:
            base = UNIT_PRIORITY.get(target.unit_type, 3.0)

        # --- Distance falloff: smooth 0-1 curve ---
        d = dist(self.x, self.y, target.x, target.y)
        distance_factor = 1.0 / (1.0 + d / DISTANCE_NORMALIZATION)

        # --- Prefer finishing wounded targets ---
        hp_ratio = target.hp / target.max_hp if target.max_hp > 0 else 1.0
        hp_modifier = LOW_HP_FINISH_BONUS if hp_ratio < LOW_HP_FINISH_THRESHOLD else 1.0
        # v10_1: cautious trait adds extra bonus vs wounded targets
        if hp_ratio < LOW_HP_FINISH_THRESHOLD:
            hp_modifier += self.trait_modifiers.get("low_hp_bonus", 0)

        # --- Engagement stickiness (prevent target flip-flop) ---
        engage_modifier = ENGAGED_TARGET_BONUS if self.target_entity is target else 1.0

        # --- v9.3 Threat response: "the guy hitting me" ---
        threat_modifier = 1.0
        if (hasattr(self, 'last_attacker') and self.last_attacker is target
                and target.alive):
            threat_modifier = THREAT_BONUS

        # --- Compute raw score ---
        score = base * distance_factor * hp_modifier * engage_modifier * threat_modifier

        # --- Rank-based noise: higher rank = smarter picks ---
        noise_weight = RANK_TARGETING_NOISE.get(self.rank, 0.50)
        # v10_1: aggressive/cautious trait modifies aggro range
        noise_weight *= self.trait_modifiers.get("noise_mult", 1.0)
        noise_weight = max(0.0, min(1.0, noise_weight))
        if noise_weight > 0:
            noise = random.uniform(0, score)
            score = score * (1.0 - noise_weight) + noise * noise_weight

        return score

    # -- XP / Rank -------------------------------------------------------------

    def grant_xp(self, amount):
        """Add XP and check for rank-up. Workers are excluded by callers."""
        self.xp += amount
        self._check_rank_up()

    def _check_rank_up(self):
        """Promote if XP exceeds next threshold. Enemies skip bonuses during combat."""
        while (self.rank < len(RANK_XP_THRESHOLDS) - 1
               and self.xp >= RANK_XP_THRESHOLDS[self.rank + 1]):
            self.rank += 1
            # enemies don't get stat bonuses mid-fight; applied on veteran return
            if self.owner != "enemy":
                self._apply_rank_bonuses()

    def _apply_rank_bonuses(self):
        """Recalculate stats from base values × rank multipliers."""
        b = RANK_BONUSES.get(self.rank, RANK_BONUSES[0])
        ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
        self.max_hp = int(self._base_hp * b["hp_mult"])
        self.hp = int(self.max_hp * ratio)
        self.attack_power = int(self._base_attack * b["atk_mult"])
        self.attack_range = self._base_range + b["range_bonus"]

    def force_apply_rank_bonuses(self):
        """Force-apply rank bonuses (used for enemy veterans on respawn)."""
        self._apply_rank_bonuses()

    # -- v10_delta: Physics + Energy -------------------------------------------

    def _energy_factor(self):
        """Returns speed multiplier based on current energy.
        Above 20%: full speed (1.0). Below 20%: degrades to EXHAUSTED_SPEED."""
        if self.max_energy <= 0:
            return 1.0
        ratio = self.energy / self.max_energy
        if ratio >= ENERGY_EXHAUSTED_THRESHOLD:
            return 1.0
        # 0-20% range: linear ramp from EXHAUSTED_SPEED to 1.0
        t = ratio / ENERGY_EXHAUSTED_THRESHOLD
        return ENERGY_EXHAUSTED_SPEED + (1.0 - ENERGY_EXHAUSTED_SPEED) * t

    def _energy_tick(self, dt, game):
        """Regenerate energy. Rate depends on state + formation harmony."""
        regen = self.energy_regen
        # idle units regen faster
        if self.state == "idle":
            regen *= ENERGY_IDLE_REGEN_MULT
        # workers carrying resources regen slower
        if self.carry_amount > 0:
            regen *= ENERGY_CARRY_REGEN_MULT
        # v10_delta: harmonic energy field — formation harmony boosts regen
        squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
        sq = squad_mgr.get_squad(self)
        if sq:
            cache = getattr(sq, '_resonance_cache', None)
            if cache:
                harmony = cache[2]  # 3rd element is harmony value
                regen *= (1.0 + harmony * HARMONY_ENERGY_MULT)
        self.energy = min(self.max_energy, self.energy + regen * dt)

    def _drain_energy(self, amount):
        """Drain energy, clamped to 0. Returns actual amount drained."""
        actual = min(self.energy, amount)
        self.energy -= actual
        return actual

    def _physics_step(self, target_x, target_y, dt, game, arrival_dist=None,
                      do_brake=True):
        """Move toward target using acceleration/deceleration physics.
        Returns True when arrived within arrival_dist.
        do_brake=False: steer toward target at full speed, no braking."""
        if arrival_dist is None:
            arrival_dist = PHYSICS_ARRIVAL_DIST

        dx = target_x - self.x
        dy = target_y - self.y
        dist_to_target = math.hypot(dx, dy)

        if dist_to_target < 1.0:
            if do_brake:
                self.vx, self.vy = 0.0, 0.0
                self.current_speed = 0.0
            return True

        # Direction to target
        inv_d = 1.0 / dist_to_target
        dir_x, dir_y = dx * inv_d, dy * inv_d

        # Effective max speed (energy + terrain)
        tc, tr = pos_to_tile(self.x, self.y)
        terrain_cost = TERRAIN_MOVE_COST.get(
            game.game_map.get_tile(tc, tr), 1.0)
        if "nimble" in self.traits:
            terrain_cost = max(1.0, terrain_cost * 0.6)
        eff_speed = (self.max_speed / terrain_cost) * self._energy_factor()

        # Koch resonance slow (value = slow %, e.g. 0.45 = 45% slow → 55% speed)
        koch_slow = getattr(self, '_koch_slow_factor', 1.0)
        if koch_slow < 1.0 and not getattr(self, '_dissonance_nullified', False):
            eff_speed *= (1.0 - koch_slow)

        # Workers move slower when carrying resources
        if self.unit_type == "worker" and self.carry_amount > 0:
            eff_speed *= ENERGY_CARRY_SPEED_MULT

        if do_brake:
            # Braking distance: d = v² / (2*decel)
            braking_d = (self.current_speed ** 2) / (2.0 * self.decel + 0.01)

            if dist_to_target <= arrival_dist:
                # Arrived — brake to stop (braking costs no energy)
                self.vx *= max(0.0, 1.0 - self.decel * dt / max(1.0, self.current_speed))
                self.vy *= max(0.0, 1.0 - self.decel * dt / max(1.0, self.current_speed))
                self.current_speed = math.hypot(self.vx, self.vy)
                if self.current_speed < 2.0:
                    self.vx, self.vy = 0.0, 0.0
                    self.current_speed = 0.0
                    return True
                # Still coasting to stop — no energy cost
                return False

            # Desired velocity — decelerate near target
            if dist_to_target < braking_d:
                desired_speed = eff_speed * (dist_to_target / max(1.0, braking_d))
            else:
                desired_speed = eff_speed
        else:
            # No braking — full speed cruise toward target
            desired_speed = eff_speed

        desired_vx = dir_x * desired_speed
        desired_vy = dir_y * desired_speed

        # Velocity delta
        dvx = desired_vx - self.vx
        dvy = desired_vy - self.vy
        dv_mag = math.hypot(dvx, dvy)

        if dv_mag > 0.01:
            # Choose accel or decel rate based on whether speeding up or slowing
            rate = self.accel if desired_speed >= self.current_speed else self.decel
            max_dv = rate * dt
            if dv_mag > max_dv:
                scale = max_dv / dv_mag
                dvx *= scale
                dvy *= scale
            self.vx += dvx
            self.vy += dvy

        # Energy drain: acceleration is expensive, cruising is cheap, braking is free
        if desired_speed > self.current_speed + 1.0:
            # Accelerating — high energy cost
            self._drain_energy(self.energy_accel_cost * dt)
        elif desired_speed < self.current_speed - 1.0:
            # Decelerating/braking — free
            pass
        else:
            # Cruising at steady speed — low energy cost
            self._drain_energy(self.energy_cruise_cost * dt)

        # Position updated by _integrate_velocity (centralized, once per frame)
        self.current_speed = math.hypot(self.vx, self.vy)

        # Update facing
        if self.current_speed > 3.0:
            self.facing_angle = math.atan2(self.vy, self.vx)

        return False

    def _apply_repulsion(self, dt, game):
        """Soft collision avoidance — push away from nearby same-owner units.
        Workers at work (gathering/building/repairing) are anchored — no repulsion."""
        if self.unit_type == "worker" and self.state in ("gathering", "building", "repairing"):
            return
        grid = game.player_grid if self.owner == "player" else game.enemy_grid
        force_x, force_y = 0.0, 0.0
        for other in grid.query_radius(self.x, self.y, REPULSION_RADIUS):
            if other is self or not other.alive:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            d = math.hypot(dx, dy)
            if d < 0.5:
                # Stacked — splay with golden angle
                angle = (self.eid * 2.399) % (2 * math.pi)
                force_x += math.cos(angle) * REPULSION_STRENGTH
                force_y += math.sin(angle) * REPULSION_STRENGTH
            elif d < REPULSION_RADIUS:
                overlap = 1.0 - d / REPULSION_RADIUS
                strength = REPULSION_STRENGTH * (overlap ** REPULSION_FALLOFF)
                force_x += (dx / d) * strength
                force_y += (dy / d) * strength
        # Apply as velocity impulse (capped)
        f_mag = math.hypot(force_x, force_y)
        if f_mag > REPULSION_STRENGTH:
            force_x *= REPULSION_STRENGTH / f_mag
            force_y *= REPULSION_STRENGTH / f_mag
        self.vx += force_x * dt
        self.vy += force_y * dt

    def _integrate_velocity(self, dt, game):
        """Final position update — called ONCE per frame after all forces."""
        # Friction: idle/stationary units bleed velocity quickly (no infinite drift)
        if self.state in ("idle", "gathering", "building", "repairing"):
            damping = 0.85  # lose 15% velocity per frame
            self.vx *= damping
            self.vy *= damping
            if abs(self.vx) < 0.5 and abs(self.vy) < 0.5:
                self.vx, self.vy = 0.0, 0.0
                self.current_speed = 0.0
        # Clamp to passable tile
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            nx = self.x + self.vx * dt
            ny = self.y + self.vy * dt
            nc, nr = pos_to_tile(nx, ny)
            if game.game_map.is_passable(nc, nr):
                self.x, self.y = nx, ny
            else:
                # Slide along obstacle
                # Try X only
                nc2, nr2 = pos_to_tile(nx, self.y)
                if game.game_map.is_passable(nc2, nr2):
                    self.x = nx
                    self.vy *= 0.3  # damp blocked axis
                else:
                    self.vx *= 0.3
                # Try Y only
                nc3, nr3 = pos_to_tile(self.x, ny)
                if game.game_map.is_passable(nc3, nr3):
                    self.y = ny
                else:
                    self.vy *= 0.3
            self.current_speed = math.hypot(self.vx, self.vy)

    # -- Update ----------------------------------------------------------------

    def update(self, dt, game):
        if not self.alive:
            return
        # v10_7: Sentinel's Cry buff decay + attack speed bonus
        if self.sentinel_cry_buff > 0:
            self.sentinel_cry_buff = max(0, self.sentinel_cry_buff - dt)
        if self.sentinel_highlighted > 0:
            self.sentinel_highlighted = max(0, self.sentinel_highlighted - dt)
        # v10_7: rooted enemies cannot act (waiting to metamorphose)
        if self.rooted:
            return
        cry_bonus = SENTINEL_CRY_SPEED_BONUS if self.sentinel_cry_buff > 0 else 0.0
        self.attack_timer = max(0, self.attack_timer - dt * (1.0 + cry_bonus))

        # worker flee check -- before state dispatch
        if (self.unit_type == "worker" and self.owner == "player"
                and self.state not in ("fleeing", "garrisoned", "stationed")):
            self._check_flee(dt, game)
            if self.state == "fleeing":
                return  # just started fleeing, skip normal update this frame

        # v10_9: incident behaviour — flee_on_contact / probe_retreat
        if self.owner == "enemy" and self.state != "fleeing":
            ib = getattr(self, 'incident_behaviour', None)
            if ib == "flee_on_contact" and self.state == "attacking":
                self.contact_timer = getattr(self, 'contact_timer', 0.0) + dt
                if self.contact_timer >= getattr(self, 'flee_contact_time', 3.0):
                    self._start_enemy_flee(game)
                    if self.state == "fleeing":
                        return
            elif ib == "probe_retreat":
                self.probe_timer = getattr(self, 'probe_timer', 0.0) + dt
                if self.probe_timer >= getattr(self, 'probe_duration', 8.0):
                    self._start_enemy_flee(game)
                    if self.state == "fleeing":
                        return

        # enemy flee check -- low HP enemies run to map edge
        # v10_1: berserker trait ignores flee entirely
        if (self.owner == "enemy" and self.state != "fleeing"
                and "berserker" not in self.traits
                and self.hp > 0 and self.hp < self.max_hp * ENEMY_FLEE_HP_FRACTION):
            self._start_enemy_flee(game)
            if self.state == "fleeing":
                return

        # v9.2 morale check — outnumbered enemies flee even at full HP
        if (self.owner == "enemy" and self.state not in ("fleeing", "idle")):
            if self._check_morale_flee(dt, game):
                return

        if self.state == "idle":
            self._process_queue(game)  # v10_beta: shift-queue waypoints
            self._idle_behavior(dt, game)
        elif self.state == "moving":
            self._move_along_path(dt, game)
        elif self.state == "gathering":
            self._gather(dt, game)
        elif self.state == "returning":
            self._move_along_path(dt, game)
            if not self.path or self.path_index >= len(self.path):
                self._deposit_resources(game)
        elif self.state == "building":
            self._do_build(dt, game)
        elif self.state == "attacking":
            self._do_attack(dt, game)
        elif self.state == "repairing":
            self._do_repair(dt, game)
        elif self.state == "garrisoned":
            return  # inside building, skip all behavior
        elif self.state == "stationed":
            return  # inside production building, skip all behavior
        elif self.state == "fleeing":
            if self.owner == "player":
                self._do_flee(dt, game)
            else:
                self._do_enemy_flee(dt, game)

        # v10_delta: energy regeneration
        self._energy_tick(dt, game)

        # v10_delta: formation spring gravitation (replaces hard slot-seeking)
        if self.state in ("idle", "gathering", "building", "attacking", "repairing"):
            self._formation_tick(dt, game)

        # v10_delta: soft repulsion + final velocity integration
        self._apply_repulsion(dt, game)
        self._integrate_velocity(dt, game)

    # -- Commands --------------------------------------------------------------

    def command_move(self, wx, wy, game, queued=False):
        if queued:
            self._command_queue.append(("move", (wx, wy)))
            return
        self._clear_tasks()
        tc, tr = pos_to_tile(wx, wy)
        self._path_to(tc, tr, game)
        self.target_pos = (wx, wy)
        self.state = "moving"

    def _process_queue(self, game):
        """v10_beta: Pop next queued command when idle."""
        if not self._command_queue or self.state != "idle":
            return
        cmd, args = self._command_queue.pop(0)
        if cmd == "move":
            self.command_move(args[0], args[1], game)
        elif cmd == "attack_move":
            self.command_attack_move(args[0], args[1], game)

    def _find_adjacent_tile(self, col, row, game):
        """Find nearest passable tile adjacent to (col,row) for worker to stand beside work."""
        sc, sr = self.get_tile()
        best = None
        best_d = 9999
        for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nc, nr = col + dc, row + dr
            if game.game_map.is_passable(nc, nr):
                d = abs(nc - sc) + abs(nr - sr)  # Manhattan to worker
                if d < best_d:
                    best_d = d
                    best = (nc, nr)
        return best if best else (col, row)

    def command_gather(self, col, row, game):
        if self.unit_type != "worker":
            return
        self._clear_tasks()
        self.gather_tile = (col, row)
        # Path to adjacent tile so worker stands beside the resource, not on it
        adj = self._find_adjacent_tile(col, row, game)
        self._path_to(adj[0], adj[1], game)
        self.state = "moving"

    def command_gather_nearest(self, game, resource_type=None):
        """v10_8c: Mine the nearest resource tile. If resource_type given, only that type."""
        if self.unit_type != "worker":
            return
        if resource_type:
            # Use existing method for specific type
            tile = self._find_nearest_resource_tile(resource_type, game)
            if tile:
                self._clear_tasks()
                self.gather_tile = tile
                adj = self._find_adjacent_tile(tile[0], tile[1], game)
                self._path_to(adj[0], adj[1], game)
                self.state = "moving"
                return
            # v10_delta1: specific type not found — fall through to any resource
            # (don't return silently with worker stuck)
        self._clear_tasks()
        my_col, my_row = self.get_tile()
        best = None
        best_d = 999999
        for (c, r), remaining in game.game_map.resource_remaining.items():
            if remaining <= 0:
                continue
            d = abs(c - my_col) + abs(r - my_row)
            if d < best_d:
                best_d = d
                best = (c, r)
        if best:
            self.gather_tile = best
            adj = self._find_adjacent_tile(best[0], best[1], game)
            self._path_to(adj[0], adj[1], game)
            self.state = "moving"

    def command_attack(self, target, game):
        self._clear_tasks()
        self.target_entity = target
        self.state = "attacking"

    def command_attack_move(self, wx, wy, game):
        """Move to position with enhanced aggro on arrival."""
        self.command_move(wx, wy, game)
        self._attack_move_target = (wx, wy)

    def command_set_stance(self, stance):
        """Set unit stance (Aggressive/Defensive/Guard/Hunt)."""
        self.stance = stance

    def root(self):
        """v10_7: Straggler takes root — stops moving, becomes stationary."""
        self.rooted = True
        self.speed = 0
        self.state = "idle"
        self.target_entity = None
        self.path = []

    def metamorphose(self):
        """v10_7: Rooted straggler transforms into an Entrenched Titan."""
        self.metamorphosed = True
        self.rooted = False
        self.max_hp = int(self.max_hp * METAMORPH_HP_MULT)
        self.hp = self.max_hp
        self.attack_power = int(self.attack_power * METAMORPH_ATK_MULT)
        self.speed = int(self._base_speed * METAMORPH_SPEED_MULT) if hasattr(self, '_base_speed') else 35
        self._base_hp = self.max_hp
        self._base_attack = self.attack_power

    def command_garrison(self, building, game):
        """Move to a town hall and enter garrison."""
        self._clear_tasks()
        self.garrison_target = building
        tc, tr = building.col, building.row
        self._path_to(tc, tr, game, exclude_building=building)
        self.state = "moving"

    def command_ungarrison(self, game):
        """Exit garrison and become idle."""
        if self.garrison_target and self in self.garrison_target.garrison:
            self.garrison_target.garrison.remove(self)
        if self.garrison_target:
            angle = random.uniform(0, 2 * math.pi)
            self.x = self.garrison_target.x + math.cos(angle) * GARRISON_SPAWN_RADIUS
            self.y = self.garrison_target.y + math.sin(angle) * GARRISON_SPAWN_RADIUS
        self.garrison_target = None
        self.state = "idle"

    def command_station(self, building, game):
        """Move to a production building and station inside."""
        if self.unit_type != "worker":
            return
        self._clear_tasks()
        self.station_target = building
        tc, tr = building.col, building.row
        self._path_to(tc, tr, game, exclude_building=building)
        self.state = "moving"

    def command_unstation(self, game):
        """Exit a production building and become idle."""
        if self.station_target and self in self.station_target.stationed_workers:
            self.station_target.stationed_workers.remove(self)
        if self.station_target:
            angle = random.uniform(0, 2 * math.pi)
            self.x = self.station_target.x + math.cos(angle) * GARRISON_SPAWN_RADIUS
            self.y = self.station_target.y + math.sin(angle) * GARRISON_SPAWN_RADIUS
        self.station_target = None
        self.state = "idle"

    def command_build(self, building, game):
        if self.unit_type != "worker":
            return
        self._clear_tasks()
        self.build_target = building
        bc, br = building.get_tile()
        self._path_to(bc, br, game, exclude_building=building)
        self.state = "moving"

    def command_repair(self, building, game):
        if self.unit_type != "worker":
            return
        self._clear_tasks()
        self.repair_target = building
        bc, br = building.get_tile()
        self._path_to(bc, br, game, exclude_building=building)
        self.state = "moving"

    def command_tower_upgrade(self, building, game):
        """v10c: Send worker to upgrade a tower to explosive cannon."""
        if self.unit_type != "worker":
            return
        self._clear_tasks()
        self.build_target = building
        building.tower_upgrading = True
        bc, br = building.get_tile()
        self._path_to(bc, br, game, exclude_building=building)
        self.state = "moving"

    # -- Resource gathering ----------------------------------------------------

    def _find_nearest_resource_tile(self, resource_type, game):
        """Find the nearest reachable tile of the given resource type.
        v10f: collect candidates sorted by Manhattan distance, then verify
        the closest few are actually reachable via A* before committing."""
        my_col, my_row = self.get_tile()
        candidates = []
        for (c, r), remaining in game.game_map.resource_remaining.items():
            if remaining <= 0:
                continue
            terrain = game.game_map.get_tile(c, r)
            if TERRAIN_RESOURCE_MAP.get(terrain) != resource_type:
                continue
            d = abs(c - my_col) + abs(r - my_row)
            candidates.append((d, c, r))
        if not candidates:
            return None
        candidates.sort()
        # try up to 5 nearest by Manhattan distance — pick first one A* can reach
        for d, c, r in candidates[:5]:
            path = a_star(my_col, my_row, c, r, game.game_map)
            if path:
                return (c, r)
        # fallback: just use Manhattan-nearest (might fail A* but worth trying)
        _, c, r = candidates[0]
        return (c, r)

    def _auto_resume_gather(self, rtype, game):
        """Try to find and path to nearest tile of resource type. Returns True if successful.
        If rtype is None, tries any gatherable resource."""
        if rtype:
            new_tile = self._find_nearest_resource_tile(rtype, game)
            if new_tile:
                self.gather_tile = new_tile
                adj = self._find_adjacent_tile(new_tile[0], new_tile[1], game)
                self._path_to(adj[0], adj[1], game)
                self.state = "moving"
                return True
            return False
        # v10_beta: fallback — try any resource type
        for fallback in ("wood", "gold", "iron", "stone"):
            new_tile = self._find_nearest_resource_tile(fallback, game)
            if new_tile:
                self.gather_tile = new_tile
                adj = self._find_adjacent_tile(new_tile[0], new_tile[1], game)
                self._path_to(adj[0], adj[1], game)
                self.state = "moving"
                return True
        return False

    # -- State behaviors -------------------------------------------------------

    def _idle_behavior(self, dt, game):
        # combat units auto-aggro
        if self.unit_type in ("soldier", "archer", "enemy_soldier", "enemy_archer",
                               "enemy_elite", "enemy_siege",
                               "enemy_shieldbearer", "enemy_healer",
                               "enemy_raider"):
            # v10_6: Healer — heal allies instead of fighting
            if self.unit_type == "enemy_healer":
                if self._healer_tick(dt, game):
                    return
            # v10_beta: squad follower — assist leader's target (formation_tick handles positioning)
            squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
            leader = squad_mgr.get_leader(self)
            if leader and leader.alive:
                if (leader.target_entity and leader.target_entity.alive
                        and leader.state == "attacking"):
                    self.target_entity = leader.target_entity
                    self.state = "attacking"
                    return

            # v10_6: stance-based aggro range
            if self.stance == STANCE_DEFENSIVE:
                aggro_range = self.attack_range
            elif self.stance == STANCE_GUARD:
                aggro_range = self.attack_range + STANCE_GUARD_AGGRO_BONUS
            elif self.stance == STANCE_HUNT:
                aggro_range = (self.attack_range + IDLE_AGGRO_RANGE) * 1.5
            else:  # AGGRESSIVE (default)
                aggro_range = self.attack_range + IDLE_AGGRO_RANGE
            # v10_1: aggressive/cautious trait modifies aggro range
            aggro_range *= self.trait_modifiers.get("aggro_range_mult", 1.0)
            # v10_1: attack-move destination — double aggro range on arrival
            if self._attack_move_target is not None:
                aggro_range *= 2.0
                self._attack_move_target = None  # consume on first idle tick
            # v10_4: use spatial grid for fast neighbor lookup
            enemy_grid = game.enemy_grid if self.owner == "player" else game.player_grid
            nearby = enemy_grid.query_radius(self.x, self.y, aggro_range)
            # also check buildings for enemy units targeting player structures
            candidates = [e for e in nearby
                          if e.alive and dist(self.x, self.y, e.x, e.y) < aggro_range]
            # enemy units also target buildings (not in spatial grid)
            if self.owner == "enemy":
                for b in game.player_buildings:
                    if b.alive and dist(self.x, self.y, b.x, b.y) < aggro_range:
                        candidates.append(b)
            # v10_6: Hunt stance — prioritize raiders and siege
            if self.stance == STANCE_HUNT and candidates:
                hunt_targets = [e for e in candidates
                                if getattr(e, 'unit_type', '') in
                                ("enemy_raider", "enemy_siege")]
                if hunt_targets:
                    candidates = hunt_targets
            if candidates:
                best = max(candidates, key=lambda e: self._score_target(e))
                self.target_entity = best
                self.state = "attacking"
                return
            # v10_6: Guard stance — return to guard position when no enemies
            if self.stance == STANCE_GUARD:
                squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
                squad = squad_mgr.get_squad(self)
                if squad and squad.guard_position:
                    gx, gy = squad.guard_position
                    if dist(self.x, self.y, gx, gy) > 20:
                        tc, tr = pos_to_tile(gx, gy)
                        self._path_to(tc, tr, game)
                        self.state = "moving"

    def _move_along_path(self, dt, game):
        if not self.path or self.path_index >= len(self.path):
            # arrived
            if self.gather_tile:
                tc, tr = self.gather_tile
                tile_t = game.game_map.get_tile(tc, tr)
                if tile_t in (TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON, TERRAIN_STONE):
                    self.state = "gathering"
                    self.gather_timer = 0.0
                else:
                    # tile depleted while walking — find nearest of same type, then any
                    rtype = self.carry_type or self._last_gather_type
                    if self._auto_resume_gather(rtype, game):
                        return
                    # v10_beta: fallback — try any gatherable resource
                    if self._auto_resume_gather(None, game):
                        return
                    self.state = "idle"
                    self.gather_tile = None
            elif self.build_target and self.build_target.alive and (
                    not self.build_target.built or self.build_target.tower_upgrading):
                self.state = "building"
            elif self.repair_target and self.repair_target.alive and self.repair_target.hp < self.repair_target.max_hp:
                self.state = "repairing"
            elif self.garrison_target and self.garrison_target.alive and not self.garrison_target.ruined:
                # v10_2: enter garrison on arrival
                bld = self.garrison_target
                if len(bld.garrison) < GARRISON_MAX_WORKERS:
                    # auto-deposit carried resources
                    if self.carry_amount > 0 and self.carry_type:
                        game.resources.add(self.carry_type, self.carry_amount)
                        self.carry_amount = 0
                        self.carry_type = None
                    bld.garrison.append(self)
                    self.state = "garrisoned"
                else:
                    self.garrison_target = None
                    self.state = "idle"
            elif self.station_target and self.station_target.alive and not self.station_target.ruined and self.station_target.built:
                # v10.2: enter production building on arrival
                bld = self.station_target
                pconfig = PRODUCTION_RATES.get(bld.building_type, {})
                max_w = pconfig.get("max_workers", 3)
                if len(bld.stationed_workers) < max_w:
                    # auto-deposit carried resources
                    if self.carry_amount > 0 and self.carry_type:
                        game.resources.add(self.carry_type, self.carry_amount)
                        self.carry_amount = 0
                        self.carry_type = None
                    bld.stationed_workers.append(self)
                    self.state = "stationed"
                else:
                    self.station_target = None
                    self.state = "idle"
            elif self.target_entity and self.target_entity.alive:
                self.state = "attacking"
            else:
                self.state = "idle"
            return

        # v10_epsilon1: lookahead path following — cruise through, brake at final
        # Skip past intermediate waypoints we're already close to
        while self.path_index < len(self.path) - 1:
            wc, wr = self.path[self.path_index]
            wx, wy = tile_center(wc, wr)
            if dist(self.x, self.y, wx, wy) < TILE_SIZE:
                self.path_index += 1
            else:
                break

        # Target: look ahead for smooth steering
        lookahead = min(self.path_index + 3, len(self.path) - 1)
        tc, tr = self.path[lookahead]
        tx, ty = tile_center(tc, tr)

        is_final = (lookahead >= len(self.path) - 1)
        if is_final:
            # Final waypoint: brake and stop
            arrived = self._physics_step(tx, ty, dt, game,
                                         arrival_dist=PHYSICS_ARRIVAL_DIST)
            if arrived:
                self.path_index = len(self.path)  # trigger arrival next frame
        else:
            # Intermediate: cruise at full speed, no braking
            self._physics_step(tx, ty, dt, game, do_brake=False)
            # Advance past reached lookahead target (handles curved paths)
            if dist(self.x, self.y, tx, ty) < TILE_SIZE:
                self.path_index = lookahead + 1

    def _gather(self, dt, game):
        if not self.gather_tile:
            self.state = "idle"
            return
        tc, tr = self.gather_tile
        # v10 fix: proximity check -- must be within 2 tiles of resource
        tx, ty = tile_center(tc, tr)
        if dist(self.x, self.y, tx, ty) > TILE_SIZE * 2:
            # pushed away or never arrived — re-path to adjacent tile
            adj = self._find_adjacent_tile(tc, tr, game)
            self._path_to(adj[0], adj[1], game)
            self.gather_timer = 0.0  # reset — must re-gather from scratch
            self.state = "moving"
            return
        tile_t = game.game_map.get_tile(tc, tr)
        if tile_t not in (TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON, TERRAIN_STONE):
            # resource depleted -- auto-resume
            rtype = self.carry_type or self._last_gather_type
            if self._auto_resume_gather(rtype, game):
                return
            self.state = "idle"
            self.gather_tile = None
            return

        rtype = TERRAIN_RESOURCE_MAP[tile_t]
        self._last_gather_type = rtype
        self.gather_timer += dt
        gather_t = GATHER_TIME[rtype]
        # v10: skill-based speed bonus
        skill_name = RESOURCE_TO_SKILL.get(rtype)
        if skill_name:
            speed_bonus = self.get_skill_speed_bonus(skill_name)
            if speed_bonus > 0:
                gather_t *= (1.0 - speed_bonus)
        if self.gather_timer >= gather_t:
            self.gather_timer = 0.0
            gather_amt = IRON_GATHER_AMOUNT if rtype == "iron" else GATHER_AMOUNT
            tile_before = game.game_map.get_tile(tc, tr)
            rtype_got, amount = game.game_map.harvest(tc, tr, gather_amt)
            if game.game_map.get_tile(tc, tr) != tile_before:
                game._map_dirty = True
                game._minimap_dirty = True
            if rtype_got and amount > 0:
                self.carry_type = rtype_got
                self.carry_amount += amount
                # return to nearest drop-off (TH, helper building, or production building)
                dropoff = game.get_nearest_dropoff(self.x, self.y, rtype_got)
                if dropoff:
                    bc, br = dropoff.get_tile()
                    self._path_to(bc, br, game, exclude_building=dropoff)
                    if self.path:
                        self.state = "returning"
                    else:
                        # A* failed — try adjacent tiles of dropoff
                        for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
                            self._path_to(bc + dc, br + dr, game)
                            if self.path:
                                self.state = "returning"
                                break
                        else:
                            self.state = "idle"
                else:
                    self.state = "idle"
            else:
                # harvest returned nothing -- tile just depleted
                if self._auto_resume_gather(rtype, game):
                    return
                self.state = "idle"
                self.gather_tile = None

    def _deposit_resources(self, game):
        # v10.2: proximity check — find nearest drop-off for carried resource
        dropoff = game.get_nearest_dropoff(self.x, self.y, self.carry_type) if self.carry_type else None
        if not dropoff:
            # fallback to any town hall
            dropoff = game.get_nearest_town_hall(self.x, self.y)
        if not dropoff:
            # v10f: no drop-off exists — go idle and keep carrying resources
            self.state = "idle"
            return
        td = dist(self.x, self.y, dropoff.x, dropoff.y)
        if td > BUILD_PROXIMITY:
            # not close enough -- re-path to drop-off
            bc, br = dropoff.get_tile()
            self._path_to(bc, br, game, exclude_building=dropoff)
            if self.path:
                self.state = "returning"
            else:
                self.state = "idle"  # can't reach drop-off
            return
        deposited_type = self.carry_type
        deposited_amount = self.carry_amount
        if self.carry_amount > 0 and self.carry_type:
            game.resources.add(self.carry_type, self.carry_amount)
            # v10: grant skill XP for resource delivery
            skill_name = RESOURCE_TO_SKILL.get(self.carry_type)
            if skill_name:
                self.grant_skill_xp(skill_name, 1, game)
            # log deposit event
            rank_str = ""
            if skill_name:
                rank_str = WORKER_RANKS[self.get_skill_rank(skill_name)]
            game.logger.log(
                game.game_time, "RESOURCE_DEPOSIT",
                game.enemy_ai.wave_number,
                self.carry_type, str(self.carry_amount),
                rank_str, self.carry_amount)
            self.carry_amount = 0
            self.carry_type = None
        # go back to gather
        if self.gather_tile:
            tc, tr = self.gather_tile
            tile_t = game.game_map.get_tile(tc, tr)
            if tile_t in (TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON, TERRAIN_STONE):
                adj = self._find_adjacent_tile(tc, tr, game)
                self._path_to(adj[0], adj[1], game)
                self.state = "moving"
                return
            else:
                # original tile depleted -- find nearest of same type
                rtype = deposited_type or self._last_gather_type
                if self._auto_resume_gather(rtype, game):
                    return
        self.state = "idle"
        self.gather_tile = None

    def _do_build(self, dt, game):
        b = self.build_target
        if not b or not b.alive:
            self.state = "idle"
            self.build_target = None
            return
        # v10c: tower upgrade — building is already built, worker upgrades it
        if b.built and b.tower_upgrading:
            d = dist(self.x, self.y, b.x, b.y)
            if d > BUILD_PROXIMITY:
                bc, br = b.get_tile()
                self._path_to(bc, br, game, exclude_building=b)
                self.state = "moving"
                return
            b.tower_upgrade_progress += dt
            self.grant_skill_xp("builder", BUILDER_XP_PER_SECOND * dt, game)
            if b.tower_upgrade_progress >= TOWER_UPGRADE_TIME:
                b.tower_level = 2
                b.tower_upgrading = False
                b.tower_upgrade_progress = 0.0
                game.logger.log(
                    game.game_time, "TOWER_UPGRADE",
                    game.enemy_ai.wave_number,
                    "tower", "explosive", "", 0,
                    f"upgraded to Lv.2")
                game.add_notification("Tower upgraded to Explosive Cannon!", 3.0, (255, 140, 40))
                self.state = "idle"
                self.build_target = None
            return
        # v10.2: building upgrade — worker builds upgrade on a completed helper building
        if b.built and b.upgrading_to:
            d = dist(self.x, self.y, b.x, b.y)
            if d > BUILD_PROXIMITY:
                bc, br = b.get_tile()
                self._path_to(bc, br, game, exclude_building=b)
                self.state = "moving"
                return
            # scaffold aura for upgrade work too
            build_dt = dt
            for sb in game.player_buildings:
                if (sb.building_type == "scaffold" and sb.built and not sb.ruined
                        and dist(self.x, self.y, sb.x, sb.y) <= SCAFFOLD_AURA_RANGE):
                    build_dt = dt * (1.0 + SCAFFOLD_SPEED_BONUS)
                    break
            b.upgrade_progress += build_dt
            self.grant_skill_xp("builder", BUILDER_XP_PER_SECOND * dt, game)
            if b.upgrade_progress >= b.upgrade_time:
                # mutate building in-place to new type
                new_type = b.upgrading_to
                new_def = BUILDING_DEFS[new_type]
                b.building_type = new_type
                b.size = new_def["size"]
                b.max_hp = new_def["hp"]
                b.hp = b.max_hp
                # recalculate center for new size
                b.x = b.col * TILE_SIZE + (b.size * TILE_SIZE) // 2
                b.y = b.row * TILE_SIZE + (b.size * TILE_SIZE) // 2
                b.upgrading_to = None
                b.upgrade_progress = 0.0
                b.upgrade_time = 0.0
                b.production_timer = 0.0
                game.logger.log(
                    game.game_time, "BUILDING_UPGRADED",
                    game.enemy_ai.wave_number,
                    new_type, "", "", 0,
                    f"upgraded from helper")
                game.add_notification(
                    f"{BUILDING_LABELS.get(new_type, new_type)} built!", 3.0, (100, 255, 100))
                self.state = "idle"
                self.build_target = None
            return
        if b.built:
            self.state = "idle"
            self.build_target = None
            return
        d = dist(self.x, self.y, b.x, b.y)
        if d > BUILD_PROXIMITY:
            # move closer
            bc, br = b.get_tile()
            self._path_to(bc, br, game, exclude_building=b)
            self.state = "moving"
            return
        # v10.2: scaffold aura — +25% build speed
        build_dt = dt
        for sb in game.player_buildings:
            if (sb.building_type == "scaffold" and sb.built and not sb.ruined
                    and dist(self.x, self.y, sb.x, sb.y) <= SCAFFOLD_AURA_RANGE):
                build_dt = dt * (1.0 + SCAFFOLD_SPEED_BONUS)
                break
        b.build_progress += build_dt
        # v10: builder XP while constructing
        self.grant_skill_xp("builder", BUILDER_XP_PER_SECOND * dt, game)
        if b.build_progress >= b.build_time:
            b.built = True
            b.build_progress = b.build_time
            b.hp = b.max_hp  # restore full HP (critical for rebuilt ruins)
            game.logger.log(
                game.game_time, "BUILDING_COMPLETE",
                game.enemy_ai.wave_number,
                b.building_type, "", "", 0,
                f"{b.build_time:.0f}s build")
            game.add_message(f"{display_name(b.building_type)} complete", MSG_COL_ECONOMY)
            self.state = "idle"
            self.build_target = None

    def _do_repair(self, dt, game):
        b = self.repair_target
        if not b or not b.alive or b.hp >= b.max_hp:
            self.state = "idle"
            self.repair_target = None
            return
        d = dist(self.x, self.y, b.x, b.y)
        if d > BUILD_PROXIMITY:
            bc, br = b.get_tile()
            self._path_to(bc, br, game, exclude_building=b)
            self.state = "moving"
            return
        # v10.2: scaffold aura — +25% repair speed
        repair_dt = dt
        for sb in game.player_buildings:
            if (sb.building_type == "scaffold" and sb.built and not sb.ruined
                    and dist(self.x, self.y, sb.x, sb.y) <= SCAFFOLD_AURA_RANGE):
                repair_dt = dt * (1.0 + SCAFFOLD_SPEED_BONUS)
                break
        # calculate resource cost per HP
        bdef = BUILDING_DEFS.get(b.building_type, {})
        total_cost_gold = bdef.get("gold", 0) * REPAIR_COST_FRACTION
        total_cost_wood = bdef.get("wood", 0) * REPAIR_COST_FRACTION
        hp_to_repair = min(REPAIR_RATE * repair_dt, b.max_hp - b.hp)
        fraction = hp_to_repair / b.max_hp
        gold_needed = total_cost_gold * fraction
        wood_needed = total_cost_wood * fraction
        # check if player can afford the repair tick
        if game.resources.gold < gold_needed or game.resources.wood < wood_needed:
            self.state = "idle"
            self.repair_target = None
            return
        game.resources.gold -= gold_needed
        game.resources.wood -= wood_needed
        b.hp = min(b.max_hp, b.hp + hp_to_repair)
        # v10: builder XP while repairing
        self.grant_skill_xp("builder", BUILDER_XP_PER_SECOND * dt, game)
        if b.hp >= b.max_hp:
            self.state = "idle"
            self.repair_target = None

    # -- Worker flee behavior --------------------------------------------------

    def _check_flee(self, dt, game):
        """Check for nearby enemies and start fleeing if found."""
        # v10_8: cooldown between flee->resume cycles to stop ping-ponging
        if game.game_time - self._flee_resume_time < WORKER_FLEE_COOLDOWN:
            return
        nearest_enemy = None
        nearest_d = WORKER_FLEE_RADIUS
        # v10_4: spatial grid lookup instead of scanning all enemies
        for e in game.enemy_grid.query_radius(self.x, self.y, WORKER_FLEE_RADIUS):
            if not e.alive:
                continue
            d = dist(self.x, self.y, e.x, e.y)
            if d < nearest_d:
                nearest_d = d
                nearest_enemy = e
        if not nearest_enemy:
            return
        # v10 fix: only save task on FIRST flee — never overwrite while already fleeing
        if self.state != "fleeing":
            self._saved_task = {
                "state": self.state,
                "gather_tile": self.gather_tile,
                "build_target": self.build_target,
                "repair_target": self.repair_target,
                "target_pos": self.target_pos,
                "carry_type": self.carry_type,
                "carry_amount": self.carry_amount,
                "_last_gather_type": self._last_gather_type,
            }
        # compute flee direction (away from enemy)
        dx = self.x - nearest_enemy.x
        dy = self.y - nearest_enemy.y
        fd = math.hypot(dx, dy)
        if fd < 1:
            dx, dy = 1, 0
            fd = 1
        fx = self.x + (dx / fd) * WORKER_FLEE_DISTANCE
        fy = self.y + (dy / fd) * WORKER_FLEE_DISTANCE
        # clamp to map bounds
        fx = max(TILE_SIZE, min(fx, (constants.MAP_COLS - 1) * TILE_SIZE))
        fy = max(TILE_SIZE, min(fy, (constants.MAP_ROWS - 1) * TILE_SIZE))
        tc, tr = pos_to_tile(fx, fy)
        self._path_to(tc, tr, game)
        self._flee_start_time = game.game_time
        game.logger.log(
            game.game_time, "WORKER_FLEE",
            game.enemy_ai.wave_number,
            self._saved_task.get("state", "idle") if self._saved_task else "idle",
            nearest_enemy.unit_type if nearest_enemy else "unknown")
        self.state = "fleeing"
        self._flee_timer = 0.0
        # clear task fields so _move_along_path doesn't enter gather/build/repair on arrival
        self._clear_tasks()

    def _do_flee(self, dt, game):
        """Flee state: run away, check if safe to resume work."""
        # move along flee path (preserve fleeing state — _move_along_path sets idle on arrival)
        saved_state = self.state
        self._move_along_path(dt, game)
        if saved_state == "fleeing" and self.state == "idle":
            self.state = "fleeing"

        # check if enemies still nearby (v10_4: spatial grid)
        enemy_nearby = False
        for e in game.enemy_grid.query_radius(self.x, self.y, WORKER_FLEE_RADIUS):
            if e.alive and dist(self.x, self.y, e.x, e.y) < WORKER_FLEE_RADIUS:
                enemy_nearby = True
                break

        if enemy_nearby:
            self._flee_timer = 0.0
            # if we've stopped moving, re-flee WITHOUT overwriting _saved_task
            if not self.path or self.path_index >= len(self.path):
                # find nearest enemy for flee direction (v10_4: spatial grid)
                nearest_enemy = None
                nearest_d = WORKER_FLEE_RADIUS * 2
                for e in game.enemy_grid.query_radius(self.x, self.y, WORKER_FLEE_RADIUS * 2):
                    if not e.alive:
                        continue
                    ed = dist(self.x, self.y, e.x, e.y)
                    if ed < nearest_d:
                        nearest_d = ed
                        nearest_enemy = e
                if nearest_enemy:
                    dx = self.x - nearest_enemy.x
                    dy = self.y - nearest_enemy.y
                    fd = math.hypot(dx, dy)
                    if fd < 1:
                        dx, dy = 1, 0
                        fd = 1
                    fx = self.x + (dx / fd) * WORKER_FLEE_DISTANCE
                    fy = self.y + (dy / fd) * WORKER_FLEE_DISTANCE
                    fx = max(TILE_SIZE, min(fx, (constants.MAP_COLS - 1) * TILE_SIZE))
                    fy = max(TILE_SIZE, min(fy, (constants.MAP_ROWS - 1) * TILE_SIZE))
                    tc, tr = pos_to_tile(fx, fy)
                    self._path_to(tc, tr, game)
        else:
            self._flee_timer += dt
            if self._flee_timer >= WORKER_SAFE_TIME:
                self._resume_saved_task(game)

    def _resume_saved_task(self, game):
        """Restore the worker's previous task after fleeing."""
        self._flee_resume_time = game.game_time  # v10_8: start cooldown
        task = self._saved_task
        self._saved_task = None
        self._flee_timer = 0.0
        if not task:
            self.state = "idle"
            return
        # v10: log resume with flee duration
        flee_duration = game.game_time - self._flee_start_time
        game.logger.log(
            game.game_time, "WORKER_RESUME",
            game.enemy_ai.wave_number,
            task.get("state", "idle"), "", "",
            flee_duration)
        # restore attributes
        self.gather_tile = task.get("gather_tile")
        self.build_target = task.get("build_target")
        self.repair_target = task.get("repair_target")
        self.target_pos = task.get("target_pos")
        self.carry_type = task.get("carry_type")
        self.carry_amount = task.get("carry_amount", 0)
        self._last_gather_type = task.get("_last_gather_type")
        prev_state = task.get("state", "idle")
        # re-path to the task target
        if prev_state in ("gathering", "moving") and self.gather_tile:
            tc, tr = self.gather_tile
            self._path_to(tc, tr, game)
            self.state = "moving"
        elif prev_state == "returning" and self.carry_amount > 0 and self.carry_type:
            dropoff = game.get_nearest_dropoff(self.x, self.y, self.carry_type)
            if not dropoff:
                dropoff = game.get_nearest_town_hall(self.x, self.y)
            if dropoff:
                bc, br = dropoff.get_tile()
                self._path_to(bc, br, game, exclude_building=dropoff)
                self.state = "returning"
            else:
                self.state = "idle"
        elif prev_state == "building" and self.build_target and self.build_target.alive and (
                not self.build_target.built or self.build_target.tower_upgrading):
            bc, br = self.build_target.get_tile()
            self._path_to(bc, br, game, exclude_building=self.build_target)
            self.state = "moving"
        elif prev_state == "repairing" and self.repair_target and self.repair_target.alive and self.repair_target.hp < self.repair_target.max_hp:
            bc, br = self.repair_target.get_tile()
            self._path_to(bc, br, game, exclude_building=self.repair_target)
            self.state = "moving"
        else:
            self.state = "idle"

    # -- Enemy flee behavior ---------------------------------------------------

    def _start_enemy_flee(self, game):
        """Low-HP enemy starts fleeing toward nearest map edge.
        Smarter: only flee when at a disadvantage (more player units nearby)."""
        # v10_4: count nearby forces using spatial grid
        scan_radius = WORKER_FLEE_RADIUS
        p_nearby = game.player_grid.query_radius(self.x, self.y, scan_radius)
        player_nearby = sum(1 for u in p_nearby
                            if u.alive and u.unit_type != "worker"
                            and dist(self.x, self.y, u.x, u.y) < scan_radius)
        e_nearby = game.enemy_grid.query_radius(self.x, self.y, scan_radius)
        enemy_nearby = sum(1 for u in e_nearby
                           if u.alive and dist(self.x, self.y, u.x, u.y) < scan_radius)
        # only flee if outnumbered (player has more than 60% of local enemies)
        if player_nearby <= enemy_nearby * 0.6:
            return  # stay and fight — we have numbers advantage

        fx, fy = self._nearest_edge()
        tc, tr = pos_to_tile(fx, fy)
        self._path_to(tc, tr, game)
        self.state = "fleeing"
        self.target_entity = None

    def _check_morale_flee(self, dt, game):
        """v9.2: periodic morale check — outnumbered enemies without a leader flee."""
        self._morale_timer -= dt
        if self._morale_timer > 0:
            return False
        self._morale_timer = MORALE_CHECK_INTERVAL

        # Sergeants/Captains never morale-flee
        resistance = MORALE_RANK_RESISTANCE.get(self.rank, 1.0)
        if resistance >= 999:
            return False

        # v10_4: Count local forces using spatial grid
        scan = MORALE_SCAN_RADIUS
        p_nearby = game.player_grid.query_radius(self.x, self.y, scan)
        player_nearby = sum(1 for u in p_nearby
                            if u.alive and u.unit_type != "worker"
                            and dist(self.x, self.y, u.x, u.y) < scan)
        e_nearby = game.enemy_grid.query_radius(self.x, self.y, scan)
        enemy_nearby = max(1, sum(1 for u in e_nearby
                                  if u.alive
                                  and dist(self.x, self.y, u.x, u.y) < scan))
        ratio = player_nearby / enemy_nearby

        # Check for morale leader (Sergeant+ OR inspiring trait) nearby
        leader_nearby = game.enemy_grid.query_radius(self.x, self.y, MORALE_LEADER_AURA)
        for u in leader_nearby:
            if u is not self and u.alive and dist(self.x, self.y, u.x, u.y) < MORALE_LEADER_AURA:
                if u.rank >= MORALE_LEADER_MIN_RANK or u.trait_modifiers.get("is_morale_leader"):
                    return False

        # Apply rank resistance: veterans need worse odds to break
        # v10_1: brave/cowardly trait modifies flee ratio
        morale_mult = self.trait_modifiers.get("morale_mult", 1.0)
        if ratio >= MORALE_FLEE_RATIO * resistance * morale_mult:
            self._start_morale_flee(game)
            return True
        return False

    def _start_morale_flee(self, game):
        """v9.2: morale-flee — regroup with allied cluster or run to edge."""
        # Look for allied cluster at medium range (not in our local area)
        regroup_target = None
        best_score = -1
        scan = MORALE_SCAN_RADIUS

        for u in game.enemy_units:
            if u is self or not u.alive:
                continue
            d = dist(self.x, self.y, u.x, u.y)
            if d < scan or d > scan * 3:
                continue  # skip nearby (also outnumbered) and too far
            # v10_beta: use spatial grid instead of O(n) scan for cluster
            cluster = len(game.enemy_grid.query_radius(u.x, u.y, MORALE_CLUSTER_RADIUS))
            score = cluster + (3 if u.rank >= MORALE_LEADER_MIN_RANK else 0)
            if score > best_score and cluster >= 2:
                best_score = score
                regroup_target = u

        if regroup_target:
            tc, tr = regroup_target.get_tile()
            self._path_to(tc, tr, game)
        else:
            fx, fy = self._nearest_edge()
            tc, tr = pos_to_tile(fx, fy)
            self._path_to(tc, tr, game)
        self.state = "fleeing"
        self.target_entity = None

    def _do_enemy_flee(self, dt, game):
        """Enemy flee: move toward edge (escape) or regroup point (rally)."""
        self._move_along_path(dt, game)

        # v9.2: check if path ended — decide edge-escape vs regroup-rally
        if not self.path or self.path_index >= len(self.path):
            c, r = self.get_tile()
            at_edge = (c <= 2 or c >= constants.MAP_COLS - 3 or r <= 2 or r >= constants.MAP_ROWS - 3)
            if at_edge:
                # escaped! add to veteran list with accumulated XP
                if hasattr(game, 'escaped_enemies'):
                    game.escaped_enemies.append({
                        "unit_type": self.unit_type,
                        "building_mult": self.building_mult,
                        "xp": self.xp,
                    })
                game.logger.log(game.game_time, "ENEMY_ESCAPED",
                                game.enemy_ai.wave_number,
                                self.unit_type, str(self.xp),
                                f"rank_{self.rank}", self.xp)
                self.alive = False
            else:
                # reached regroup point — rally and re-engage
                new_target = self._find_new_target(game)
                if new_target:
                    self.target_entity = new_target
                    self.state = "attacking"
                else:
                    self.state = "idle"
            return

        # still on path — keep fleeing
        if self.state != "fleeing":
            self.state = "fleeing"

    def _nearest_edge(self):
        """Return world coords of nearest map edge."""
        map_w = constants.MAP_COLS * TILE_SIZE
        map_h = constants.MAP_ROWS * TILE_SIZE
        candidates = [
            (self.x,         (TILE_SIZE, self.y)),                          # left
            (map_w - self.x, ((constants.MAP_COLS - 2) * TILE_SIZE, self.y)),        # right
            (self.y,         (self.x, TILE_SIZE)),                          # top
            (map_h - self.y, (self.x, (constants.MAP_ROWS - 2) * TILE_SIZE)),       # bottom
        ]
        return min(candidates, key=lambda c: c[0])[1]

    # -- Formation Lattice (v10_beta) ------------------------------------------

    def _get_front_direction(self, game):
        """Compute 'front' direction for formation — toward nearest threat."""
        squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
        leader = squad_mgr.get_leader(self)
        ref = leader if leader and leader.alive else self
        # If ref is attacking, front = toward that target
        if ref.target_entity and ref.target_entity.alive:
            dx = ref.target_entity.x - ref.x
            dy = ref.target_entity.y - ref.y
            d = math.hypot(dx, dy)
            if d > 1:
                return dx / d, dy / d
        # Otherwise, toward nearest threat
        best_d = 1e9
        bx, by = 0.0, -1.0
        threats = game.enemy_units if self.owner == "player" else game.player_units
        for e in threats:
            if not e.alive:
                continue
            d = dist(ref.x, ref.y, e.x, e.y)
            if d < best_d:
                best_d = d
                bx, by = e.x - ref.x, e.y - ref.y
        d = math.hypot(bx, by)
        return (bx / d, by / d) if d > 1 else (0.0, -1.0)

    def _formation_tick(self, dt, game):
        """v10_delta: Spring-based formation gravitation.

        Units feel a critically-damped spring pull toward their formation slot.
        In combat, spring is weaker; beyond leash, spring triples.
        Repulsion is handled separately by _apply_repulsion.
        """
        if self.unit_type == "worker":
            return

        squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
        squad = squad_mgr.get_squad(self)
        if not squad or not squad.leader or not squad.leader.alive:
            return
        if squad.leader is self:
            return  # leader is the anchor

        slot_idx = squad.get_slot_index(self)
        if slot_idx <= 0:
            return

        # Track out-of-combat timer
        if self.state == "attacking":
            self._out_of_combat_timer = 0.0
        else:
            self._out_of_combat_timer += dt

        # Compute slot world position
        leader = squad.leader
        front_x, front_y = self._get_front_direction(game)
        rotation = getattr(squad, 'rotation_angle', 0.0)
        params = squad.get_formation_params() if hasattr(squad, 'get_formation_params') else None
        ox, oy = formation_slot(
            squad.formation, squad.alive_count,
            slot_idx, front_x, front_y, params=params)
        # Apply squad rotation
        if rotation != 0.0:
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            ox, oy = ox * cos_r - oy * sin_r, ox * sin_r + oy * cos_r
        slot_x = leader.x + ox
        slot_y = leader.y + oy

        dx = slot_x - self.x
        dy = slot_y - self.y
        d = math.hypot(dx, dy)

        if d < FORMATION_SLOT_ARRIVAL:
            return  # close enough

        # Determine spring strength
        k = FORMATION_SPRING_K
        # In combat with target in range — weaken spring (let them fight)
        if (self.state == "attacking" and self.target_entity
                and self.target_entity.alive and d <= FORMATION_COMBAT_LEASH):
            k *= 0.3  # gentle pull during combat
        elif d > FORMATION_COMBAT_LEASH:
            k *= 3.0  # strong rubber-band beyond leash
        elif self._out_of_combat_timer < FORMATION_REGROUP_DELAY:
            return  # brief grace period after combat

        # Spring force: F = k * displacement - damping * velocity
        fx = k * dx - FORMATION_SPRING_DAMP * self.vx
        fy = k * dy - FORMATION_SPRING_DAMP * self.vy

        # Clamp spring force magnitude
        f_mag = math.hypot(fx, fy)
        if f_mag > FORMATION_SPRING_MAX:
            scale = FORMATION_SPRING_MAX / f_mag
            fx *= scale
            fy *= scale

        # Apply as velocity impulse
        self.vx += fx * dt
        self.vy += fy * dt

    # -- Combat ----------------------------------------------------------------

    def _find_new_target(self, game):
        """Find best target by utility score. Siege units prefer buildings. Enemies skip ruins."""
        Building = _get_building_class()
        if self.owner == "enemy":
            # prefer non-ruined targets
            candidates = [u for u in game.player_units if u.alive]
            candidates += [b for b in game.player_buildings
                           if b.alive and not getattr(b, 'ruined', False)]
            if not candidates:
                # fallback: include ruins
                candidates = [e for e in game.player_units + game.player_buildings if e.alive]
        else:
            candidates = [e for e in game.enemy_units if e.alive]
        if not candidates:
            return None
        # v10_6: Raider — prioritize workers and economy buildings
        if self.economy_only:
            econ_targets = [c for c in candidates
                            if (hasattr(c, 'unit_type') and c.unit_type == 'worker')
                            or (isinstance(c, Building) and getattr(c, 'building_type', '')
                                in ('refinery', 'town_hall', 'forge'))]
            if econ_targets:
                candidates = econ_targets
        # siege units: strongly prefer non-ruined buildings
        if self.building_mult > 1.0:
            buildings = [c for c in candidates if isinstance(c, Building)
                         and not getattr(c, 'ruined', False)]
            if not buildings:
                buildings = [c for c in candidates if isinstance(c, Building)]
            if buildings:
                candidates = buildings
        # v9.1: utility-scored selection instead of pure distance
        return max(candidates, key=lambda c: self._score_target(c))

    def _do_attack(self, dt, game):
        t = self.target_entity
        if not t or not t.alive:
            # retarget: find nearest valid target
            new_target = self._find_new_target(game)
            if new_target:
                self.target_entity = new_target
                return
            self.target_entity = None
            self.state = "idle"
            return

        # v9.3: periodic live retarget — switch to better target mid-combat
        self._retarget_timer -= dt
        if self._retarget_timer <= 0:
            self._retarget_timer = RETARGET_INTERVAL
            current_score = self._score_target(t)
            better = self._find_new_target(game)
            if (better and better is not t
                    and self._score_target(better) > current_score * RETARGET_SWITCH_THRESHOLD):
                self.target_entity = better
                t = better

        d = dist(self.x, self.y, t.x, t.y)
        if d <= self.attack_range:
            if self.attack_timer <= 0:
                # v10_delta: drain energy on attack
                self._drain_energy(self.energy_attack_cost)
                # v10_delta: exhaustion slows attack speed
                cd = self.attack_cd
                if self.energy < self.max_energy * ENERGY_EXHAUSTED_THRESHOLD:
                    cd *= ENERGY_TIRED_COOLDOWN_MULT
                if self.attack_range > 60:
                    # --- ranged: fire ballistic arrow ---
                    self._fire_arrow(t, game)
                else:
                    # --- melee: instant damage ---
                    dmg = self.attack_power
                    # v10_8: Polar Rose resonance damage bonus
                    if self._resonance_visual == 0 and not self._dissonance_nullified:
                        sq = game.player_squad_mgr.get_squad(self)
                        if sq:
                            rc = game.player_squad_mgr._resonance_cache.get(sq.squad_id)
                            if rc:
                                dmg = int(dmg * (1.0 + rc[1]))
                    # v10_1: berserker bonus below 50% HP
                    if "berserker" in self.traits and self.hp < self.max_hp * 0.5:
                        dmg = int(dmg * (1.0 + self.trait_modifiers.get("berserk_atk_bonus", 0)))
                    # v10_beta: lone wolf bonus — spatial grid instead of O(n) scan
                    if "lone_wolf" in self.traits:
                        ally_grid = game.player_grid if self.owner == "player" else game.enemy_grid
                        nearby_allies = [o for o in ally_grid.query_radius(
                            self.x, self.y, LONE_WOLF_ISOLATION_DIST) if o is not self and o.alive]
                        if not nearby_allies:
                            dmg = int(dmg * (1.0 + self.trait_modifiers.get("lone_atk_bonus", 0)))
                    if isinstance(t, _get_building_class()):
                        dmg = int(dmg * self.building_mult)
                    t.take_damage(dmg, self)
                    _process_combat_hit(self, t, game, "melee")
                self.attack_timer = cd
        else:
            # v10_6: defensive/guard stance — don't chase, drop target and idle
            if self.stance in (STANCE_DEFENSIVE, STANCE_GUARD):
                self.target_entity = None
                self.state = "idle"
                return
            # v10_delta: physics-based chase (acceleration/deceleration)
            self._repath_cooldown = max(0, self._repath_cooldown - dt)
            self._physics_step(t.x, t.y, dt, game,
                               arrival_dist=self.attack_range * 0.8)
            # If blocked (no velocity change + not arriving), try A* repath
            if self.current_speed < 2.0 and self._repath_cooldown <= 0:
                tc, tr = pos_to_tile(t.x, t.y)
                self._path_to(tc, tr, game)
                if self.path:
                    self.state = "moving"
                    self.target_entity = t
                self._repath_cooldown = REPATH_COOLDOWN

    def _fire_arrow(self, target, game):
        """Fire a parabolic arrow toward target. Advanced archers lead moving targets."""
        Arrow = _get_arrow_class()
        # Base aim point: target's current position
        aim_x, aim_y = target.x, target.y

        # v10_5: Lead aiming for advanced archers (rank 2+)
        if self.rank >= ARROW_LEAD_MIN_RANK and hasattr(target, 'path') and target.path:
            # Estimate target velocity from their path + speed
            pi = getattr(target, 'path_index', 0)
            if pi < len(target.path):
                from utils import tile_center
                nx_t, ny_t = tile_center(*target.path[pi])
                tdx, tdy = nx_t - target.x, ny_t - target.y
                td = math.hypot(tdx, tdy)
                if td > 1:
                    tspeed = getattr(target, 'speed', 60)
                    tvx = (tdx / td) * tspeed
                    tvy = (tdy / td) * tspeed
                    # Predict where target will be after flight time
                    d = math.hypot(target.x - self.x, target.y - self.y)
                    flight_t = max(0.3, ARROW_FLIGHT_TIME * (d / ARROW_FLIGHT_DISTANCE_NORM))
                    lead_factor = min(1.0,
                        (self.rank - ARROW_LEAD_MIN_RANK + 1) * ARROW_LEAD_FACTOR_PER_RANK)
                    # Sharpshooter trait boosts lead accuracy
                    lead_factor = min(1.0, lead_factor * (
                        1.0 + self.trait_modifiers.get("lead_bonus", 0)))
                    aim_x += tvx * flight_t * lead_factor
                    aim_y += tvy * flight_t * lead_factor

        # Apply accuracy spread based on rank
        accuracy = RANK_BONUSES.get(self.rank, RANK_BONUSES[0])["accuracy_bonus"]
        spread = max(ARROW_MIN_SPREAD, ARROW_BASE_SPREAD - accuracy)
        # v10_1: sharpshooter trait tightens spread further
        spread *= self.trait_modifiers.get("spread_mult", 1.0)
        spread_angle = random.uniform(-spread, spread)

        # Damage
        dmg = self.attack_power
        # v10_8: Polar Rose resonance damage bonus for arrows
        if self._resonance_visual == 0 and not self._dissonance_nullified:
            sq = game.player_squad_mgr.get_squad(self)
            if sq:
                rc = game.player_squad_mgr._resonance_cache.get(sq.squad_id)
                if rc:
                    dmg = int(dmg * (1.0 + rc[1]))
        if isinstance(target, _get_building_class()):
            dmg = int(dmg * self.building_mult)

        arrow = Arrow(self.x, self.y, aim_x, aim_y, dmg, self.owner,
                      source_unit=self, spread_angle=spread_angle)
        game.arrows.append(arrow)

    def _healer_tick(self, dt, game):
        """Healer: find and heal nearest wounded ally. Called from _idle_behavior."""
        if self.heal_rate <= 0:
            return False
        # v10_beta: spatial grid instead of O(n) scan
        best = None
        best_d = self.attack_range + 1
        for e in game.enemy_grid.query_radius(self.x, self.y, self.attack_range + 1):
            if e is self or not e.alive or e.hp >= e.max_hp:
                continue
            d = dist(self.x, self.y, e.x, e.y)
            if d < best_d:
                best_d = d
                best = e
        if best:
            best.hp = min(best.max_hp, int(best.hp + self.heal_rate * dt))
            # follow healing target to stay in range
            if best_d > self.attack_range * HEALER_FOLLOW_RANGE_MULT:
                tc, tr = best.get_tile()
                self._path_to(tc, tr, game)
                self.state = "moving"
            return True
        return False

    # -- Drawing (v10f: algorithmic shapes) ------------------------------------

    @staticmethod
    def _polar_points(cx, cy, radius, r_func, n_points=48, rotation=0.0):
        """Generate polygon points from polar function. Returns list of (x,y)."""
        pts = []
        two_pi = 2 * math.pi
        for i in range(n_points):
            theta = rotation + two_pi * i / n_points
            r = r_func(theta) * radius
            pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        return pts

    @staticmethod
    def _hex_func(theta, n_power=4.0):
        """Superellipse hex: r(theta) = 1/(|cos|^n + |sin|^n)^(1/n)."""
        ct = abs(math.cos(theta))
        st = abs(math.sin(theta))
        denom = ct ** n_power + st ** n_power
        return 1.0 / (denom ** (1.0 / n_power)) if denom > 1e-10 else 1.0

    @staticmethod
    def _rose_func(theta, k):
        """Polar rose: r = |cos(k*theta)|."""
        return abs(math.cos(k * theta))

    @staticmethod
    def _blade_func(theta, k, sharpness=0.6):
        """Sharpened polar rose: blade-like petal tips (v10g2)."""
        v = abs(math.cos(k * theta))
        return v ** sharpness if v > 1e-10 else 0.0

    def _draw_worker_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw worker as rounded hexagon (superellipse) with self-similar inners."""
        color = (25, 35, 55) if is_enemy else (138, 43, 226)  # Violet — Gatherer
        rotation = math.pi / 6
        n_pts = 36 if r < 8 else 48

        pts = self._polar_points(sx, sy, r, lambda t: self._hex_func(t, 4.0),
                                 n_pts, rotation)
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
            # v10g2: black edge for player, jagged overlay for enemy
            if is_enemy:
                jagged = self._polar_points(
                    sx, sy, r * 1.05,
                    lambda t: self._hex_func(t, 4.0) * (1.0 + 0.08 * math.sin(17 * t)),
                    n_pts, rotation)
                if len(jagged) >= 3:
                    pygame.draw.polygon(surf, (60, 15, 15), jagged, max(1, int(2 * z)))
            else:
                pygame.draw.polygon(surf, (0, 0, 0), pts, max(1, int(z)))

        # (rank/skill visuals removed — will be part of dynamic unit animation overhaul)

    def _draw_soldier_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw soldier as blade-like polar rose (v10g2)."""
        color = (30, 5, 55) if is_enemy else (75, 0, 180)  # Indigo — Warden
        k = 2.5  # 5 petals
        rotation = -math.pi / 2  # petal points up
        n_pts = 36 if r < 8 else 60

        # v10g2: blade_func for sharper petal tips
        pts = self._polar_points(sx, sy, r, lambda t: self._blade_func(t, k),
                                 n_pts, rotation)
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
            # v10g2: black edge shading for player soldiers
            if not is_enemy:
                pygame.draw.polygon(surf, (0, 0, 0), pts, max(1, int(2 * z)))
        # enemy jagged overlay
        if is_enemy and r >= 5:
            jagged = self._polar_points(
                sx, sy, r * 1.08,
                lambda t: self._blade_func(t, k) * (1.0 + 0.12 * math.sin(13 * t)),
                n_pts, rotation)
            if len(jagged) >= 3:
                pygame.draw.polygon(surf, (50, 10, 80), jagged, max(1, int(2 * z)))

    def _draw_archer_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw archer as golden spiral bow with filled body (v10g2: enhanced visibility)."""
        color = (12, 30, 75) if is_enemy else (30, 100, 255)  # Blue — Ranger
        phi = (1 + math.sqrt(5)) / 2
        b = math.log(phi) / (math.pi / 2)
        n_arc = 30 if r < 10 else 50

        # v10g2: compute bow arc points for both limbs first
        top_pts = []
        bot_pts = []
        for i in range(n_arc):
            theta = math.pi * 0.1 + (math.pi * 1.3) * i / (n_arc - 1)
            rv = 0.3 * math.exp(b * theta) * r / 3.0
            x = sx + rv * math.cos(theta) * 0.5
            top_pts.append((x, sy - rv * math.sin(theta) * 0.7))
            bot_pts.append((x, sy + rv * math.sin(theta) * 0.7))

        # v10g2: filled bow body polygon for visibility
        bow_polygon = top_pts + bot_pts[::-1]
        if len(bow_polygon) >= 3:
            fill_c = tuple(max(0, c - 40) for c in color)
            pygame.draw.polygon(surf, fill_c, bow_polygon)
            pygame.draw.polygon(surf, color, bow_polygon, max(1, int(2 * z)))

        # v10g2: black shadow under bow limbs for edge definition (player only)
        if not is_enemy:
            for pts_list in [top_pts, bot_pts]:
                if len(pts_list) >= 2:
                    pygame.draw.lines(surf, (0, 0, 0), False, pts_list,
                                      max(4, r // 10))

        # bow limbs on top — v10g2: thicker lines
        for pts_list in [top_pts, bot_pts]:
            if len(pts_list) >= 2:
                pygame.draw.lines(surf, color, False, pts_list, max(3, r // 12))

        # bowstring
        st = sy - r * 0.65
        sb = sy + r * 0.65
        pygame.draw.line(surf, color, (int(sx - r * 0.1), int(st)),
                         (int(sx - r * 0.1), int(sb)), max(1, r // 30))
        # nocked arrow
        if r >= 5:
            tip_x = sx + r * 0.8
            tail_x = sx - r * 0.3
            glow = (240, 235, 220)
            pygame.draw.line(surf, glow, (int(tail_x), sy), (int(tip_x), sy),
                             max(1, r // 25))
            hs = r * 0.12
            pygame.draw.polygon(surf, glow, [
                (int(tip_x), sy),
                (int(tip_x - hs), int(sy - hs * 0.6)),
                (int(tip_x - hs), int(sy + hs * 0.6)),
            ])
        # enemy jagged border
        if is_enemy and r >= 5:
            n = 30
            epts = []
            for i in range(n):
                theta = 2 * math.pi * i / n
                rv = r * (0.85 + 0.08 * math.sin(11 * theta))
                epts.append((sx + rv * math.cos(theta), sy + rv * math.sin(theta)))
            if len(epts) >= 3:
                pygame.draw.polygon(surf, (60, 10, 40), epts, max(1, int(2 * z)))

    def _draw_siege_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw siege unit as a heavy spiked polygon (v10g2: darker enemy)."""
        color = (100, 50, 0) if not is_enemy else (40, 18, 8)  # v10g2: enemy near-black
        n = 24
        pts = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            spike = 1.0 + 0.25 * (1 if i % 3 == 0 else 0)
            rv = r * spike
            pts.append((sx + rv * math.cos(theta), sy + rv * math.sin(theta)))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
        # inner gear
        inner_pts = []
        for i in range(n):
            theta = 2 * math.pi * i / n + math.pi / n
            rv = r * 0.6
            inner_pts.append((sx + rv * math.cos(theta), sy + rv * math.sin(theta)))
        if len(inner_pts) >= 3:
            pygame.draw.polygon(surf, (25, 12, 5), inner_pts, max(1, int(z)))

    def _draw_elite_shape(self, surf, sx, sy, r, z):
        """Draw enemy elite as a compound rose — v10g2: dark with purple accents."""
        color = (50, 10, 45)  # v10g2: near-black purple
        k = 3.0
        n_pts = 48
        pts = self._polar_points(sx, sy, r,
                                 lambda t: self._rose_func(t, k), n_pts, -math.pi / 2)
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
        # inner star — dark purple accent
        inner = self._polar_points(sx, sy, r * 0.5,
                                   lambda t: self._rose_func(t, k + 1), n_pts, 0)
        if len(inner) >= 3:
            pygame.draw.polygon(surf, (100, 30, 90), inner)
        # central glow — muted
        pygame.draw.circle(surf, (180, 40, 140), (sx, sy), max(2, r // 5))

    def _draw_shieldbearer_shape(self, surf, sx, sy, r, z):
        """Shieldbearer: Thick polar rose with flat front — shield shape, dark steel."""
        color = ENEMY_COLORS.get("enemy_shieldbearer", (80, 90, 110))
        pts = self._polar_points(sx, sy, r,
                                 lambda t: 0.6 + 0.4 * abs(math.cos(t)), 36, self.facing_angle)
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
        # shield front bar
        fa = self.facing_angle
        fx, fy = math.cos(fa) * r * 0.8, math.sin(fa) * r * 0.8
        perp_x, perp_y = -fy * 0.6, fx * 0.6
        p1 = (int(sx + fx + perp_x), int(sy + fy + perp_y))
        p2 = (int(sx + fx - perp_x), int(sy + fy - perp_y))
        pygame.draw.line(surf, (160, 170, 190), p1, p2, max(2, int(3 * z)))

    def _draw_healer_shape(self, surf, sx, sy, r, z):
        """Healer: Lissajous curve x=sin(2t), y=sin(3t) — flowing organic, dark green."""
        color = ENEMY_COLORS.get("enemy_healer", (30, 100, 50))
        pts = []
        for i in range(48):
            t = 2 * math.pi * i / 48
            px = sx + r * 0.8 * math.sin(2 * t)
            py = sy + r * 0.8 * math.sin(3 * t)
            pts.append((int(px), int(py)))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
        # healing cross
        cr = max(2, r // 3)
        pygame.draw.line(surf, (100, 255, 130), (sx - cr, sy), (sx + cr, sy), max(1, int(2 * z)))
        pygame.draw.line(surf, (100, 255, 130), (sx, sy - cr), (sx, sy + cr), max(1, int(2 * z)))

    def _draw_raider_shape(self, surf, sx, sy, r, z):
        """Raider: Star polygon (pentagram) — sharp aggressive, dark magenta."""
        color = ENEMY_COLORS.get("enemy_raider", (130, 30, 80))
        pts = []
        for i in range(10):
            angle = -math.pi / 2 + 2 * math.pi * i / 10
            rad = r if i % 2 == 0 else r * 0.4
            pts.append((int(sx + rad * math.cos(angle)), int(sy + rad * math.sin(angle))))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, color, pts)
        pygame.draw.circle(surf, (200, 60, 120), (sx, sy), max(1, r // 4))

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        margin = int(30 * z)
        if sx < -margin or sx > SCREEN_WIDTH + margin or sy < GAME_AREA_Y - margin or sy > GAME_AREA_Y + GAME_AREA_H + margin:
            return

        r = max(2, int(UNIT_RADIUS.get(self.unit_type, 12) * z))
        is_enemy = self.owner == "enemy"

        # selection ring — fractal shape per unit type
        if self.selected:
            sel_r = r + max(1, int(3 * z))
            draw_selection_ring(surf, self.unit_type, sx, sy, sel_r, COL_SELECT, 2)

        # v10f: algorithmic shape based on unit type
        if self.unit_type == "worker":
            self._draw_worker_shape(surf, sx, sy, r, z, is_enemy)
        elif self.unit_type in ("soldier", "enemy_soldier"):
            self._draw_soldier_shape(surf, sx, sy, r, z, is_enemy)
        elif self.unit_type in ("archer", "enemy_archer"):
            self._draw_archer_shape(surf, sx, sy, r, z, is_enemy)
        elif self.unit_type == "enemy_siege":
            self._draw_siege_shape(surf, sx, sy, r, z, is_enemy=True)
        elif self.unit_type == "enemy_elite":
            self._draw_elite_shape(surf, sx, sy, r, z)
        elif self.unit_type == "enemy_shieldbearer":
            self._draw_shieldbearer_shape(surf, sx, sy, r, z)
        elif self.unit_type == "enemy_healer":
            self._draw_healer_shape(surf, sx, sy, r, z)
        elif self.unit_type == "enemy_raider":
            self._draw_raider_shape(surf, sx, sy, r, z)
        else:
            # fallback: simple circle for any unmapped type
            color = UNIT_COLORS.get(self.unit_type) or ENEMY_COLORS.get(self.unit_type, (150, 150, 150))
            pygame.draw.circle(surf, color, (sx, sy), r)
            pygame.draw.circle(surf, (0, 0, 0), (sx, sy), r, 1)

        # v10_7: Rooted straggler — draw root tendrils below
        if self.rooted and r >= 3:
            root_c = (90, 60, 30)
            for i in range(4):
                angle = math.pi * 0.25 + i * math.pi * 0.5
                rx = sx + int(r * 1.3 * math.cos(angle))
                ry = sy + int(r * 1.1 * math.sin(angle)) + r // 2
                pygame.draw.line(surf, root_c, (sx, sy + r // 2), (rx, ry), max(1, int(2 * z)))
                # small root tip
                pygame.draw.circle(surf, (60, 40, 20), (rx, ry), max(1, int(1.5 * z)))

        # v10_7: Metamorphosed — pulsing red-black aura, larger visual
        if self.metamorphosed and r >= 3:
            aura_r = int(r * 1.5)
            aura_alpha = 60 + int(40 * abs(math.sin(pygame.time.get_ticks() * 0.003)))
            aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (180, 30, 30, aura_alpha), (aura_r, aura_r), aura_r)
            surf.blit(aura_surf, (sx - aura_r, sy - aura_r))

        # v10_8: Resonance aura (player units in formation)
        if getattr(self, '_resonance_visual', -1) >= 0 and not getattr(self, '_dissonance_nullified', False) and r >= 3:
            from constants import RESONANCE_COLORS
            res_col = RESONANCE_COLORS.get(self._resonance_visual, (200, 200, 200))
            aura_r = int(r * 1.3)
            ticks = pygame.time.get_ticks()
            aura_alpha = 30 + int(35 * abs(math.sin(ticks * 0.002 + self.eid * 0.5)))
            aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*res_col, aura_alpha), (aura_r, aura_r), aura_r)
            surf.blit(aura_surf, (sx - aura_r, sy - aura_r))

        # v10_8: Dissonant enemy glow (dark inverse aura)
        if getattr(self, 'dissonant_formation', -1) >= 0 and r >= 3:
            from constants import RESONANCE_DISSONANCE_COLORS
            dis_col = RESONANCE_DISSONANCE_COLORS.get(self.dissonant_formation, (100, 100, 100))
            aura_r = int(r * 1.4)
            ticks = pygame.time.get_ticks()
            aura_alpha = 40 + int(30 * abs(math.sin(ticks * 0.004 + self.eid * 0.3)))
            aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (*dis_col, aura_alpha), (aura_r, aura_r), aura_r)
            surf.blit(aura_surf, (sx - aura_r, sy - aura_r))

        # v10_7: Sentinel Cry highlighted enemy — blue-white outline
        if self.sentinel_highlighted > 0 and r >= 3:
            hi_alpha = int(200 * min(1.0, self.sentinel_highlighted))
            pygame.draw.circle(surf, (120, 200, 255), (sx, sy), r + max(2, int(3 * z)), max(1, int(2 * z)))

        # v10f: orbiting resource indicators when carrying
        if self.carry_amount > 0 and r >= 4:
            carry_colors = {"gold": COL_GOLD, "wood": COL_WOOD, "iron": COL_IRON_C, "stone": COL_STONE}
            carry_col = carry_colors.get(self.carry_type or "iron", COL_IRON_C)
            # Fibonacci-spaced orbiting dots (golden angle = 137.5°)
            n_orbs = min(3, max(1, self.carry_amount // 5))
            orbit_r = r + max(3, int(5 * z))
            golden_angle = 2.3998277  # 137.508° in radians
            for i in range(n_orbs):
                angle = golden_angle * i
                ox = sx + int(orbit_r * math.cos(angle))
                oy = sy + int(orbit_r * math.sin(angle))
                cr = max(2, int(3 * z))
                pygame.draw.circle(surf, carry_col, (ox, oy), cr)

        self.draw_health_bar(surf, cam)
