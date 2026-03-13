import math
import random
import pygame
from constants import (UNIT_DEFS, ENEMY_DEFS, UNIT_COLORS, ENEMY_COLORS,
                       UNIT_LABELS, UNIT_RADIUS, BUILDING_DEFS, BUILDING_COLORS,
                       BUILDING_LABELS, TILE_SIZE, MAP_COLS, MAP_ROWS,
                       SCREEN_WIDTH, GAME_AREA_Y,
                       GAME_AREA_H, COL_SELECT, COL_HEALTH_BG, COL_HEALTH,
                       COL_ENEMY_HEALTH, COL_GOLD, COL_WOOD, COL_IRON_C,
                       COL_STONE,
                       TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON,
                       TERRAIN_STONE, TERRAIN_RESOURCE_MAP,
                       GATHER_TIME, GATHER_AMOUNT, IRON_GATHER_AMOUNT,
                       REFINE_IRON_COST, REFINE_STEEL_YIELD, REFINE_TIME,
                       TOWER_CANNON_DAMAGE, TOWER_CANNON_CD,
                       TOWER_CANNON_SPEED, TOWER_CANNON_RANGE,
                       TOWER_CANNON_LIFETIME, TOWER_CANNON_HIT_RADIUS,
                       TOWER_CANNON_SPREAD,
                       TOWER_UPGRADE_COST, TOWER_UPGRADE_TIME,
                       TOWER_EXPLOSIVE_DAMAGE, TOWER_EXPLOSIVE_RADIUS,
                       TOWER_EXPLOSIVE_DIRECT,
                       UNIT_SEPARATION_DIST, UNIT_SEPARATION_FORCE,
                       WORKER_FLEE_RADIUS, WORKER_SAFE_TIME,
                       REPAIR_RATE, REPAIR_COST_FRACTION,
                       ENEMY_FLEE_HP_FRACTION,
                       RESOURCE_TO_SKILL, WORKER_RANK_XP,
                       WORKER_RANK_SPEED_BONUS, WORKER_RANKS,
                       WORKER_SKILL_NAMES, WORKER_SKILL_COLORS,
                       BUILDER_XP_PER_SECOND,
                       PATH_ARRIVAL_THRESHOLD, BUILD_PROXIMITY,
                       WORKER_FLEE_DISTANCE, IDLE_AGGRO_RANGE,
                       RANK_XP_THRESHOLDS, RANK_BONUSES, RANK_COLORS,
                       XP_PER_HIT, XP_KILL_BONUS,
                       ENEMY_XP_PER_HIT, ENEMY_XP_KILL_BONUS,
                       ARROW_SPEED, ARROW_MAX_LIFETIME, ARROW_HIT_RADIUS,
                       ARROW_BASE_SPREAD, ARROW_MIN_SPREAD,
                       GROUND_ARROW_LIFETIME,
                       SQUAD_FOLLOW_DIST, SQUAD_COHESION_FORCE,
                       BUILDING_PRIORITY, UNIT_PRIORITY, RUIN_PRIORITY_MULT,
                       DISTANCE_NORMALIZATION, RANK_TARGETING_NOISE,
                       LOW_HP_FINISH_BONUS, LOW_HP_FINISH_THRESHOLD,
                       ENGAGED_TARGET_BONUS,
                       TOWER_LOW_HP_BONUS, TOWER_LOW_HP_THRESHOLD,
                       TOWER_HIGH_THREAT_TYPES,
                       MORALE_CHECK_INTERVAL, MORALE_SCAN_RADIUS,
                       MORALE_FLEE_RATIO, MORALE_LEADER_AURA,
                       MORALE_LEADER_MIN_RANK, MORALE_RANK_RESISTANCE,
                       FORMATION_FRONT_OFFSET, FORMATION_REAR_OFFSET,
                       FORMATION_FORCE, FORMATION_RANK_PUSH,
                       RETARGET_INTERVAL, RETARGET_SWITCH_THRESHOLD,
                       THREAT_BONUS, TERRAIN_MOVE_COST,
                       TRAIT_POOL, TRAIT_CONFLICTS, TRAIT_ROLL_WEIGHTS,
                       TRAIT_MODIFIERS, TRAIT_DISPLAY)
from utils import dist, pos_to_tile, tile_center, draw_text
from pathfinding import a_star


# ---------------------------------------------------------------------------
# Shared combat helper  (deduplicates melee & arrow post-damage logic)
# ---------------------------------------------------------------------------
def _process_combat_hit(attacker, target, game, source_label):
    """Handle post-damage XP, rank-up, bounty, and building ruin/destroy logging.

    Args:
        attacker: Unit that dealt damage (or None for sourceless hits).
        target:   Entity that was damaged.
        game:     Game instance for logger, resources, enemy_ai.
        source_label: e.g. "melee" or "arrow" (appears in log).
    """
    # building ruin/destroy logging
    if isinstance(target, Building) and (target.ruined or not target.alive):
        evt = "BUILDING_RUINED" if target.alive else "BUILDING_DESTROYED"
        game.logger.log(game.game_time, evt,
                        game.enemy_ai.wave_number,
                        target.building_type, source_label)
    # XP for non-workers
    if attacker and attacker.alive and attacker.unit_type != "worker":
        old_rank = attacker.rank
        xp_hit = XP_PER_HIT if attacker.owner == "player" else ENEMY_XP_PER_HIT
        xp_kill = XP_KILL_BONUS if attacker.owner == "player" else ENEMY_XP_KILL_BONUS
        attacker.grant_xp(xp_hit)
        if not target.alive and target.owner != attacker.owner:
            attacker.grant_xp(xp_kill)
        if attacker.rank > old_rank:
            game.logger.log(game.game_time, "RANK_UP",
                            game.enemy_ai.wave_number,
                            attacker.unit_type, str(attacker.rank),
                            attacker.owner)
    # kill bounty (player kills enemy)
    if not target.alive and target.owner == "enemy":
        owner = attacker.owner if attacker else "player"
        if owner == "player":
            bounty = game.enemy_ai.get_kill_bounty()
            game.resources.gold += bounty
            game.logger.log(game.game_time, "UNIT_KILLED",
                            game.enemy_ai.wave_number,
                            attacker.unit_type if attacker else source_label,
                            target.unit_type,
                            f"rank_{attacker.rank}" if attacker else "",
                            bounty, f"{source_label} {owner}")


# ---------------------------------------------------------------------------
# Entity base
# ---------------------------------------------------------------------------
class Entity:
    _next_id = 0

    def __init__(self, x, y, hp, owner):
        Entity._next_id += 1
        self.eid = Entity._next_id
        self.x, self.y = float(x), float(y)
        self.hp = hp
        self.max_hp = hp
        self.owner = owner
        self.selected = False
        self.alive = True
        self.last_attacker = None  # v9.3: who last hit us

    def get_tile(self):
        return pos_to_tile(self.x, self.y)

    def take_damage(self, dmg, attacker=None):
        self.hp -= dmg
        if attacker is not None:
            self.last_attacker = attacker
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw_health_bar(self, surf, cam, width=24):
        if self.hp >= self.max_hp:
            return
        z = cam.zoom
        w = max(4, int(width * z))
        sx, sy = cam.world_to_screen(self.x, self.y)
        bx = sx - w // 2
        by = sy - int(20 * z)
        bh = max(2, int(4 * z))
        ratio = self.hp / self.max_hp
        col = COL_HEALTH if self.owner == "player" else COL_ENEMY_HEALTH
        pygame.draw.rect(surf, COL_HEALTH_BG, (bx, by, w, bh))
        pygame.draw.rect(surf, col, (bx, by, int(w * ratio), bh))


# ---------------------------------------------------------------------------
# Unit
# ---------------------------------------------------------------------------
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
        # v10_1: attack-move destination (enhanced aggro on arrival)
        self._attack_move_target = None

    # -- Helpers ---------------------------------------------------------------

    def _clear_tasks(self):
        """Reset all task-related state."""
        self.target_entity = None
        self.gather_tile = None
        self.build_target = None
        self.repair_target = None

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
        if isinstance(target, Building):
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
        # v10_1: aggressive trait adds noise, cautious reduces it
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

    # -- Update ----------------------------------------------------------------

    def update(self, dt, game):
        if not self.alive:
            return
        self.attack_timer = max(0, self.attack_timer - dt)

        # worker flee check -- before state dispatch
        if (self.unit_type == "worker" and self.owner == "player"
                and self.state != "fleeing"):
            self._check_flee(dt, game)
            if self.state == "fleeing":
                return  # just started fleeing, skip normal update this frame

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
        elif self.state == "fleeing":
            if self.owner == "player":
                self._do_flee(dt, game)
            else:
                self._do_enemy_flee(dt, game)

        # unit separation -- push apart when not actively moving along a path
        if self.state in ("idle", "gathering", "building", "attacking", "repairing"):
            self._apply_separation(dt, game)

    # -- Commands --------------------------------------------------------------

    def command_move(self, wx, wy, game):
        self._clear_tasks()
        tc, tr = pos_to_tile(wx, wy)
        self._path_to(tc, tr, game)
        self.target_pos = (wx, wy)
        self.state = "moving"

    def command_gather(self, col, row, game):
        if self.unit_type != "worker":
            return
        self._clear_tasks()
        self.gather_tile = (col, row)
        self._path_to(col, row, game)
        self.state = "moving"

    def command_attack(self, target, game):
        self._clear_tasks()
        self.target_entity = target
        self.state = "attacking"

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
        """Try to find and path to nearest tile of same resource type. Returns True if successful."""
        if not rtype:
            return False
        new_tile = self._find_nearest_resource_tile(rtype, game)
        if new_tile:
            self.gather_tile = new_tile
            self._path_to(new_tile[0], new_tile[1], game)
            self.state = "moving"
            return True
        return False

    # -- State behaviors -------------------------------------------------------

    def _idle_behavior(self, dt, game):
        # combat units auto-aggro
        if self.unit_type in ("soldier", "archer", "enemy_soldier", "enemy_archer",
                               "enemy_elite", "enemy_siege"):
            # v9 squad follower: assist leader's target or follow leader
            squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
            leader = squad_mgr.get_leader(self)
            if leader and leader.alive:
                # if leader is fighting, assist their target
                if (leader.target_entity and leader.target_entity.alive
                        and leader.state == "attacking"):
                    self.target_entity = leader.target_entity
                    self.state = "attacking"
                    return
                # if too far from leader, move toward them
                if dist(self.x, self.y, leader.x, leader.y) > SQUAD_FOLLOW_DIST:
                    tc, tr = leader.get_tile()
                    self._path_to(tc, tr, game)
                    self.state = "moving"
                    return

            # normal auto-aggro (for leaders, unassigned, and idle followers)
            # v9.1: utility-scored targeting instead of pure distance
            enemies = game.enemy_units if self.owner == "player" else game.player_units + game.player_buildings
            aggro_range = self.attack_range + IDLE_AGGRO_RANGE
            # v10_1: aggressive/cautious trait modifies aggro range
            aggro_range *= self.trait_modifiers.get("aggro_range_mult", 1.0)
            # v10_1: attack-move destination — double aggro range on arrival
            if self._attack_move_target is not None:
                aggro_range *= 2.0
                self._attack_move_target = None  # consume on first idle tick
            candidates = [e for e in enemies
                          if e.alive and dist(self.x, self.y, e.x, e.y) < aggro_range]
            if candidates:
                best = max(candidates, key=lambda e: self._score_target(e))
                self.target_entity = best
                self.state = "attacking"

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
                    # tile depleted while walking -- find nearest of same type
                    rtype = self.carry_type or self._last_gather_type
                    if self._auto_resume_gather(rtype, game):
                        return
                    self.state = "idle"
                    self.gather_tile = None
            elif self.build_target and self.build_target.alive and (
                    not self.build_target.built or self.build_target.tower_upgrading):
                self.state = "building"
            elif self.repair_target and self.repair_target.alive and self.repair_target.hp < self.repair_target.max_hp:
                self.state = "repairing"
            else:
                self.state = "idle"
            return

        tc, tr = self.path[self.path_index]
        tx, ty = tile_center(tc, tr)
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if d < PATH_ARRIVAL_THRESHOLD:
            self.path_index += 1
            return
        # v9.3: terrain slows movement (trees 2×, shallow water 2.5×)
        cur_tile = game.game_map.get_tile(*pos_to_tile(self.x, self.y))
        move_cost = TERRAIN_MOVE_COST.get(cur_tile, 1.0)
        # v10_1: nimble trait reduces difficult terrain penalty
        if move_cost > 1.0:
            nimble_bonus = self.trait_modifiers.get("terrain_speed_bonus", 0)
            if nimble_bonus > 0:
                move_cost = max(1.0, move_cost * (1.0 - nimble_bonus))
        step = (self.speed / move_cost) * dt
        if step >= d:
            # snap to waypoint — but only if it's passable
            wc, wr = pos_to_tile(tx, ty)
            if game.game_map.is_passable(wc, wr):
                self.x, self.y = tx, ty
            self.path_index += 1
        else:
            nx = self.x + (dx / d) * step
            ny = self.y + (dy / d) * step
            nc, nr = pos_to_tile(nx, ny)
            if game.game_map.is_passable(nc, nr):
                self.x, self.y = nx, ny
            else:
                # blocked mid-step — skip this waypoint to avoid getting stuck
                self.path_index += 1

    def _gather(self, dt, game):
        if not self.gather_tile:
            self.state = "idle"
            return
        tc, tr = self.gather_tile
        # v10 fix: proximity check -- must be within 2 tiles of resource
        tx, ty = tile_center(tc, tr)
        if dist(self.x, self.y, tx, ty) > TILE_SIZE * 2:
            # pushed away (separation) or never arrived — re-path
            self._path_to(tc, tr, game)
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
            rtype_got, amount = game.game_map.harvest(tc, tr, gather_amt)
            if rtype_got and amount > 0:
                self.carry_type = rtype_got
                self.carry_amount += amount
                # return to nearest town hall
                th = game.get_nearest_town_hall(self.x, self.y)
                if th:
                    bc, br = th.get_tile()
                    self._path_to(bc, br, game, exclude_building=th)
                    self.state = "returning"
                else:
                    self.state = "idle"
            else:
                # harvest returned nothing -- tile just depleted
                if self._auto_resume_gather(rtype, game):
                    return
                self.state = "idle"
                self.gather_tile = None

    def _deposit_resources(self, game):
        # v10 fix: proximity check -- must be near a town hall to deposit
        th = game.get_nearest_town_hall(self.x, self.y)
        if not th:
            # v10f: no town hall exists — go idle and keep carrying resources
            self.state = "idle"
            return
        td = dist(self.x, self.y, th.x, th.y)
        if td > BUILD_PROXIMITY:
            # not close enough -- re-path to town hall
            bc, br = th.get_tile()
            self._path_to(bc, br, game, exclude_building=th)
            if self.path:
                self.state = "returning"
            else:
                self.state = "idle"  # can't reach town hall
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
                self._path_to(tc, tr, game)
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
        b.build_progress += dt
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
        # calculate resource cost per HP
        bdef = BUILDING_DEFS.get(b.building_type, {})
        total_cost_gold = bdef.get("gold", 0) * REPAIR_COST_FRACTION
        total_cost_wood = bdef.get("wood", 0) * REPAIR_COST_FRACTION
        hp_to_repair = min(REPAIR_RATE * dt, b.max_hp - b.hp)
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
        nearest_enemy = None
        nearest_d = WORKER_FLEE_RADIUS
        for e in game.enemy_units:
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
        fx = max(TILE_SIZE, min(fx, (MAP_COLS - 1) * TILE_SIZE))
        fy = max(TILE_SIZE, min(fy, (MAP_ROWS - 1) * TILE_SIZE))
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
        # move along flee path
        self._move_along_path(dt, game)
        if self.state != "fleeing":
            # _move_along_path changed state to idle on arrival; override back
            self.state = "fleeing"

        # check if enemies still nearby
        enemy_nearby = False
        for e in game.enemy_units:
            if not e.alive:
                continue
            if dist(self.x, self.y, e.x, e.y) < WORKER_FLEE_RADIUS:
                enemy_nearby = True
                break

        if enemy_nearby:
            self._flee_timer = 0.0
            # if we've stopped moving, re-flee WITHOUT overwriting _saved_task
            if not self.path or self.path_index >= len(self.path):
                # find nearest enemy for flee direction
                nearest_enemy = None
                nearest_d = WORKER_FLEE_RADIUS * 2
                for e in game.enemy_units:
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
                    fx = max(TILE_SIZE, min(fx, (MAP_COLS - 1) * TILE_SIZE))
                    fy = max(TILE_SIZE, min(fy, (MAP_ROWS - 1) * TILE_SIZE))
                    tc, tr = pos_to_tile(fx, fy)
                    self._path_to(tc, tr, game)
        else:
            self._flee_timer += dt
            if self._flee_timer >= WORKER_SAFE_TIME:
                self._resume_saved_task(game)

    def _resume_saved_task(self, game):
        """Restore the worker's previous task after fleeing."""
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
        self.carry_amount = task.get("carry_amount")
        self._last_gather_type = task.get("_last_gather_type")
        prev_state = task.get("state", "idle")
        # re-path to the task target
        if prev_state in ("gathering", "moving") and self.gather_tile:
            tc, tr = self.gather_tile
            self._path_to(tc, tr, game)
            self.state = "moving"
        elif prev_state == "returning" and self.carry_amount > 0:
            th = game.get_nearest_town_hall(self.x, self.y)
            if th:
                bc, br = th.get_tile()
                self._path_to(bc, br, game, exclude_building=th)
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
        # count nearby forces to decide if fleeing makes sense
        scan_radius = WORKER_FLEE_RADIUS
        player_nearby = sum(1 for u in game.player_units
                            if u.alive and u.unit_type != "worker"
                            and dist(self.x, self.y, u.x, u.y) < scan_radius)
        enemy_nearby = sum(1 for u in game.enemy_units
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

        # Count local forces
        scan = MORALE_SCAN_RADIUS
        player_nearby = sum(1 for u in game.player_units
                            if u.alive and u.unit_type != "worker"
                            and dist(self.x, self.y, u.x, u.y) < scan)
        enemy_nearby = max(1, sum(1 for u in game.enemy_units
                                  if u.alive
                                  and dist(self.x, self.y, u.x, u.y) < scan))
        ratio = player_nearby / enemy_nearby

        # Check for morale leader (Sergeant+ OR inspiring trait) nearby
        for u in game.enemy_units:
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
            # Score: cluster size + leader bonus
            cluster = sum(1 for o in game.enemy_units
                          if o.alive and o is not self
                          and dist(u.x, u.y, o.x, o.y) < 200)
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
            at_edge = (c <= 2 or c >= MAP_COLS - 3 or r <= 2 or r >= MAP_ROWS - 3)
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
        map_w = MAP_COLS * TILE_SIZE
        map_h = MAP_ROWS * TILE_SIZE
        candidates = [
            (self.x,         (TILE_SIZE, self.y)),                          # left
            (map_w - self.x, ((MAP_COLS - 2) * TILE_SIZE, self.y)),        # right
            (self.y,         (self.x, TILE_SIZE)),                          # top
            (map_h - self.y, (self.x, (MAP_ROWS - 2) * TILE_SIZE)),       # bottom
        ]
        return min(candidates, key=lambda c: c[0])[1]

    # -- Unit separation -------------------------------------------------------

    def _get_front_direction(self, game):
        """v9.2: compute 'front' direction for formation — toward threat."""
        squad_mgr = game.player_squad_mgr
        leader = squad_mgr.get_leader(self)
        ref = leader if leader and leader.alive else self
        # If ref is attacking, front = toward that target
        if ref.target_entity and ref.target_entity.alive:
            dx = ref.target_entity.x - ref.x
            dy = ref.target_entity.y - ref.y
            d = math.hypot(dx, dy)
            if d > 1:
                return dx / d, dy / d
        # Otherwise, toward nearest enemy
        best_d = 1e9
        bx, by = 0.0, -1.0
        for e in game.enemy_units:
            if not e.alive:
                continue
            d = dist(ref.x, ref.y, e.x, e.y)
            if d < best_d:
                best_d = d
                bx, by = e.x - ref.x, e.y - ref.y
        d = math.hypot(bx, by)
        return (bx / d, by / d) if d > 1 else (0.0, -1.0)

    def _apply_separation(self, dt, game):
        """Gently push apart overlapping friendly units when stationary."""
        units = game.player_units if self.owner == "player" else game.enemy_units
        push_x, push_y = 0.0, 0.0
        for other in units:
            if other is self or not other.alive:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            d = math.hypot(dx, dy)
            if 0 < d < UNIT_SEPARATION_DIST:
                strength = (UNIT_SEPARATION_DIST - d) / UNIT_SEPARATION_DIST
                push_x += (dx / d) * strength
                push_y += (dy / d) * strength
            elif d == 0:
                # exactly overlapping -- nudge randomly
                push_x += (hash(id(self)) % 3 - 1) * 0.5
                push_y += (hash(id(self)) % 5 - 2) * 0.5
        if push_x != 0 or push_y != 0:
            mag = math.hypot(push_x, push_y)
            if mag > 1:
                push_x /= mag
                push_y /= mag
            nx = self.x + push_x * UNIT_SEPARATION_FORCE * dt
            ny = self.y + push_y * UNIT_SEPARATION_FORCE * dt
            # v10 fix: clamp to passable tiles
            nc, nr = pos_to_tile(nx, ny)
            if game.game_map.is_passable(nc, nr):
                self.x, self.y = nx, ny

        # v9 squad cohesion: gentle pull toward leader
        if self.unit_type != "worker":
            squad_mgr = game.player_squad_mgr if self.owner == "player" else game.enemy_squad_mgr
            leader = squad_mgr.get_leader(self)
            if leader and leader.alive:
                lx = leader.x - self.x
                ly = leader.y - self.y
                ld = math.hypot(lx, ly)
                if ld > SQUAD_FOLLOW_DIST * 0.5:
                    pull = min(1.0, (ld - SQUAD_FOLLOW_DIST * 0.5) / SQUAD_FOLLOW_DIST)
                    # v10_1: loyal trait multiplies cohesion force
                    cohesion = SQUAD_COHESION_FORCE * self.trait_modifiers.get("cohesion_mult", 1.0)
                    nx = self.x + (lx / ld) * cohesion * pull * dt
                    ny = self.y + (ly / ld) * cohesion * pull * dt
                    nc, nr = pos_to_tile(nx, ny)
                    if game.game_map.is_passable(nc, nr):
                        self.x, self.y = nx, ny

        # v9.2 formation hints: soldiers forward, archers back, low rank as shield
        if (self.owner == "player" and self.unit_type in ("soldier", "archer")
                and self.state in ("idle", "attacking")):
            squad_mgr = game.player_squad_mgr
            leader = squad_mgr.get_leader(self)
            if leader and leader.alive:
                front_x, front_y = self._get_front_direction(game)
                # Offset: positive = forward, negative = back
                if self.unit_type == "soldier":
                    offset = FORMATION_FRONT_OFFSET
                else:
                    offset = -FORMATION_REAR_OFFSET
                # Rank adjustment: lower rank pushed more forward
                offset += (leader.rank - self.rank) * FORMATION_RANK_PUSH
                # Target position along front axis
                tx = leader.x + front_x * offset
                ty = leader.y + front_y * offset
                fx = tx - self.x
                fy = ty - self.y
                fd = math.hypot(fx, fy)
                if fd > 5:  # dead zone to prevent jitter
                    pull = min(1.0, fd / SQUAD_FOLLOW_DIST)
                    nx = self.x + (fx / fd) * FORMATION_FORCE * pull * dt
                    ny = self.y + (fy / fd) * FORMATION_FORCE * pull * dt
                    nc, nr = pos_to_tile(nx, ny)
                    if game.game_map.is_passable(nc, nr):
                        self.x, self.y = nx, ny

    # -- Combat ----------------------------------------------------------------

    def _find_new_target(self, game):
        """Find best target by utility score. Siege units prefer buildings. Enemies skip ruins."""
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
                if self.attack_range > 60:
                    # --- ranged: fire ballistic arrow ---
                    self._fire_arrow(t, game)
                else:
                    # --- melee: instant damage ---
                    dmg = self.attack_power
                    # v10_1: berserker bonus below 50% HP
                    if "berserker" in self.traits and self.hp < self.max_hp * 0.5:
                        dmg = int(dmg * (1.0 + self.trait_modifiers.get("berserk_atk_bonus", 0)))
                    # v10_1: lone wolf bonus when no allies within 80px
                    if "lone_wolf" in self.traits:
                        allies = game.player_units if self.owner == "player" else game.enemy_units
                        alone = all(o is self or not o.alive or dist(self.x, self.y, o.x, o.y) > 80
                                    for o in allies)
                        if alone:
                            dmg = int(dmg * (1.0 + self.trait_modifiers.get("lone_atk_bonus", 0)))
                    if isinstance(t, Building):
                        dmg = int(dmg * self.building_mult)
                    t.take_damage(dmg, self)
                    _process_combat_hit(self, t, game, "melee")
                self.attack_timer = self.attack_cd
        else:
            # move towards target (terrain-slowed)
            self._repath_cooldown = max(0, self._repath_cooldown - dt)
            dx, dy = t.x - self.x, t.y - self.y
            nd = math.hypot(dx, dy)
            if nd > 0:
                cur_tile = game.game_map.get_tile(*pos_to_tile(self.x, self.y))
                move_cost = TERRAIN_MOVE_COST.get(cur_tile, 1.0)
                # v10_1 fix: nimble trait reduces difficult terrain penalty during chase
                if move_cost > 1.0:
                    nimble_bonus = self.trait_modifiers.get("terrain_speed_bonus", 0)
                    if nimble_bonus > 0:
                        move_cost = max(1.0, move_cost * (1.0 - nimble_bonus))
                step = (self.speed / move_cost) * dt
                nx = self.x + (dx / nd) * step
                ny = self.y + (dy / nd) * step
                # v10 fix: clamp to passable tiles (prevent walking through deep water)
                nc, nr = pos_to_tile(nx, ny)
                if game.game_map.is_passable(nc, nr):
                    self.x, self.y = nx, ny
                elif self._repath_cooldown <= 0:
                    # direct path blocked — use A* to path around obstacle
                    tc, tr = pos_to_tile(t.x, t.y)
                    self._path_to(tc, tr, game)
                    if self.path:
                        self.state = "moving"
                        self.target_entity = t
                    else:
                        # v10f: A* also failed — try lateral slide along obstacle
                        perp_x = -dy / nd * step
                        perp_y = dx / nd * step
                        for sign in [1, -1]:
                            lx = self.x + perp_x * sign
                            ly = self.y + perp_y * sign
                            lc, lr = pos_to_tile(lx, ly)
                            if game.game_map.is_passable(lc, lr):
                                self.x, self.y = lx, ly
                                break
                    self._repath_cooldown = 1.5  # prevent spam

    def _fire_arrow(self, target, game):
        """Fire a ballistic arrow toward target with accuracy spread based on rank."""
        dx = target.x - self.x
        dy = target.y - self.y
        d = math.hypot(dx, dy)
        if d < 1:
            dx, dy = 1.0, 0.0
            d = 1.0
        # normalize
        dx /= d
        dy /= d
        # apply accuracy spread based on rank
        accuracy = RANK_BONUSES.get(self.rank, RANK_BONUSES[0])["accuracy_bonus"]
        spread = max(ARROW_MIN_SPREAD, ARROW_BASE_SPREAD - accuracy)
        # v10_1: sharpshooter trait tightens spread further
        spread *= self.trait_modifiers.get("spread_mult", 1.0)
        angle_offset = random.uniform(-spread, spread)
        cos_a = math.cos(angle_offset)
        sin_a = math.sin(angle_offset)
        adx = dx * cos_a - dy * sin_a
        ady = dx * sin_a + dy * cos_a
        # damage
        dmg = self.attack_power
        if isinstance(target, Building):
            dmg = int(dmg * self.building_mult)
        arrow = Arrow(self.x, self.y, adx, ady, dmg, self.owner, source_unit=self)
        game.arrows.append(arrow)

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
        """Superellipse hex: r(θ) = 1/(|cos|^n + |sin|^n)^(1/n)."""
        ct = abs(math.cos(theta))
        st = abs(math.sin(theta))
        denom = ct ** n_power + st ** n_power
        return 1.0 / (denom ** (1.0 / n_power)) if denom > 1e-10 else 1.0

    @staticmethod
    def _rose_func(theta, k):
        """Polar rose: r = |cos(k*θ)|."""
        return abs(math.cos(k * theta))

    @staticmethod
    def _blade_func(theta, k, sharpness=0.6):
        """Sharpened polar rose: blade-like petal tips (v10g2)."""
        v = abs(math.cos(k * theta))
        return v ** sharpness if v > 1e-10 else 0.0

    def _draw_worker_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw worker as rounded hexagon (superellipse) with self-similar inners."""
        color = (25, 35, 55) if is_enemy else (50, 130, 220)  # v10g2: enemy near-black
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

        # inner self-similar hexes based on worker rank
        primary_skill, w_rank = self.get_primary_skill()
        if w_rank >= 1 and r >= 6:
            inner_c = tuple(min(255, c + 40) for c in color)
            inner_pts = self._polar_points(sx, sy, r * 0.55,
                                           lambda t: self._hex_func(t, 4.0),
                                           n_pts, rotation + 0.05)
            if len(inner_pts) >= 3:
                pygame.draw.polygon(surf, inner_c, inner_pts, max(1, int(z)))
        if w_rank >= 2 and r >= 8:
            inner_c2 = tuple(min(255, c + 70) for c in color)
            inner_pts2 = self._polar_points(sx, sy, r * 0.3,
                                            lambda t: self._hex_func(t, 4.0),
                                            n_pts, rotation + 0.10)
            if len(inner_pts2) >= 3:
                pygame.draw.polygon(surf, inner_c2, inner_pts2, max(1, int(z)))

        # v10g2: worker skill color — full hex border instead of tiny pip
        if primary_skill and w_rank > 0:
            skill_col = WORKER_SKILL_COLORS.get(primary_skill, (200, 200, 200))
            # Rank 1+: outer hex outline in skill color
            outer_skill_pts = self._polar_points(sx, sy, r * 1.02,
                                                 lambda t: self._hex_func(t, 4.0),
                                                 n_pts, rotation)
            if len(outer_skill_pts) >= 3:
                pygame.draw.polygon(surf, skill_col, outer_skill_pts,
                                    max(2, int(3 * z)))
            # Rank 2: inner hex filled solid in skill color
            if w_rank >= 2 and r >= 8:
                inner_skill_pts = self._polar_points(sx, sy, r * 0.3,
                                                     lambda t: self._hex_func(t, 4.0),
                                                     n_pts, rotation + 0.10)
                if len(inner_skill_pts) >= 3:
                    pygame.draw.polygon(surf, skill_col, inner_skill_pts)

    def _draw_soldier_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw soldier as blade-like polar rose with rank-scaling petals (v10g2)."""
        base_color = (35, 12, 12) if is_enemy else (200, 60, 60)  # v10g2: enemy near-black
        k_values = [1.5, 2.5, 3.5, 4.0, 5.0]  # 3,5,7,8,10 petals
        k = k_values[min(self.rank, len(k_values) - 1)]
        # rank tint (player only — enemies stay dark)
        if not is_enemy:
            if self.rank >= 3:
                tint = RANK_COLORS.get(self.rank, (200, 200, 200))
                color = tuple((a + b) // 2 for a, b in zip(base_color, tint))
            elif self.rank >= 1:
                tint = RANK_COLORS.get(self.rank, (200, 200, 200))
                color = tuple((a * 3 + b) // 4 for a, b in zip(base_color, tint))
            else:
                color = base_color
        else:
            color = base_color
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
        # inner rose for rank 2+
        if self.rank >= 2 and r >= 6:
            inner_k = k + 0.5
            inner_c = tuple(min(255, c + 50) for c in color)
            inner_pts = self._polar_points(sx, sy, r * 0.5,
                                           lambda t: self._blade_func(t, inner_k),
                                           n_pts, rotation)
            if len(inner_pts) >= 3:
                pygame.draw.polygon(surf, inner_c, inner_pts)
                if not is_enemy:
                    pygame.draw.polygon(surf, (0, 0, 0), inner_pts, max(1, int(z)))
        # central dot for sergeant+
        if self.rank >= 3:
            pygame.draw.circle(surf, RANK_COLORS.get(self.rank, (255, 215, 0)),
                               (sx, sy), max(2, r // 6))
        # v10g2: rank pip removed (petal count communicates rank)
        # enemy jagged overlay
        if is_enemy and r >= 5:
            jagged = self._polar_points(
                sx, sy, r * 1.08,
                lambda t: self._blade_func(t, k) * (1.0 + 0.12 * math.sin(13 * t)),
                n_pts, rotation)
            if len(jagged) >= 3:
                pygame.draw.polygon(surf, (80, 10, 10), jagged, max(1, int(2 * z)))

    def _draw_archer_shape(self, surf, sx, sy, r, z, is_enemy):
        """Draw archer as golden spiral bow with filled body (v10g2: enhanced visibility)."""
        color = (35, 10, 30) if is_enemy else (50, 190, 50)  # v10g2: enemy near-black
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
        # Fibonacci dots on bow limbs (rank-based)
        if self.rank >= 1 and r >= 6:
            fib_angles = [0.5, 0.8, 1.1, 1.4, 1.8]
            n_dots = min(self.rank + 1, len(fib_angles))
            dot_col = RANK_COLORS.get(self.rank, (200, 200, 200))
            for i in range(n_dots):
                theta = math.pi * 0.1 + fib_angles[i]
                rv = 0.3 * math.exp(b * theta) * r / 3.0
                for m in [1, -1]:
                    dx = sx + rv * math.cos(theta) * 0.5
                    dy = sy + m * rv * math.sin(theta) * 0.7
                    pygame.draw.circle(surf, dot_col, (int(dx), int(dy)),
                                       max(2, r // 15))
        # v10g2: rank pip removed (fibonacci dots communicate rank)
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
        # rank pip (kept — siege has no other rank indicator)
        if self.rank > 0:
            pip_r = max(2, int(4 * z))
            pip_col = RANK_COLORS.get(self.rank, (200, 200, 200))
            pygame.draw.circle(surf, pip_col, (sx + r, sy - r), pip_r)

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

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        margin = int(30 * z)
        if sx < -margin or sx > SCREEN_WIDTH + margin or sy < GAME_AREA_Y - margin or sy > GAME_AREA_Y + GAME_AREA_H + margin:
            return

        r = max(2, int(UNIT_RADIUS.get(self.unit_type, 12) * z))
        is_enemy = self.owner == "enemy"

        # selection ring
        if self.selected:
            pygame.draw.circle(surf, COL_SELECT, (sx, sy), r + max(1, int(3 * z)), 2)

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
        else:
            # fallback: simple circle for any unmapped type
            color = UNIT_COLORS.get(self.unit_type) or ENEMY_COLORS.get(self.unit_type, (150, 150, 150))
            pygame.draw.circle(surf, color, (sx, sy), r)
            pygame.draw.circle(surf, (0, 0, 0), (sx, sy), r, 1)

        # v10f: orbiting resource indicators when carrying
        if self.carry_amount > 0 and r >= 4:
            carry_colors = {"gold": COL_GOLD, "wood": COL_WOOD, "iron": COL_IRON_C, "stone": COL_STONE}
            carry_col = carry_colors.get(self.carry_type, COL_IRON_C)
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

        # v10_1: trait indicator dots — small colored pips below unit
        if self.traits and r >= 4:
            trait_x = sx - len(self.traits) * max(2, int(3 * z)) // 2
            trait_y = sy + r + max(3, int(5 * z))
            pip_r = max(1, int(2 * z))
            for trait_name in sorted(self.traits):
                td = TRAIT_DISPLAY.get(trait_name, {"color": (180, 180, 180)})
                pygame.draw.circle(surf, td["color"], (trait_x, trait_y), pip_r)
                trait_x += pip_r * 3

        self.draw_health_bar(surf, cam)


# ---------------------------------------------------------------------------
# VDD Phase 3: Algorithmic Building Shape Helpers
# ---------------------------------------------------------------------------
_TH_BROWN = (139, 90, 43)
_TH_GREEN = (30, 110, 50)
_BK_MAROON = (140, 45, 45)
_RF_GRAY = (100, 100, 130)
_TW_STONE = (160, 160, 140)
_FORGE_ORANGE = (255, 140, 40)
_STEEL_BLUE = (100, 160, 220)


def _l_system_expand(axiom, rules, iters):
    s = axiom
    for _ in range(iters):
        s = "".join(rules.get(c, c) for c in s)
    return s


def _l_system_render(surf, cx, cy, instructions, angle_deg=22.5,
                     step=8, start_angle=-90, col_trunk=_TH_BROWN,
                     col_tip=_TH_GREEN, line_width=2):
    """Interpret L-system string as turtle graphics."""
    angle_rad = math.radians(angle_deg)
    cur_angle = math.radians(start_angle)
    x, y = float(cx), float(cy)
    stack = []
    depth = 0
    max_depth = max(1, instructions.count('['))
    for ch in instructions:
        if ch == 'F':
            nx = x + step * math.cos(cur_angle)
            ny = y + step * math.sin(cur_angle)
            t = min(1.0, depth / max(1, max_depth * 0.5))
            col = tuple(int(a + (b - a) * t) for a, b in zip(col_trunk, col_tip))
            w = max(1, line_width - depth // 3)
            pygame.draw.line(surf, col, (int(x), int(y)), (int(nx), int(ny)), w)
            x, y = nx, ny
        elif ch == '+':
            cur_angle += angle_rad
        elif ch == '-':
            cur_angle -= angle_rad
        elif ch == '[':
            stack.append((x, y, cur_angle, depth))
            depth += 1
        elif ch == ']':
            if stack:
                x, y, cur_angle, depth = stack.pop()


def _sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color):
    if depth == 0:
        pygame.draw.polygon(surf, color,
                            [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])
        return
    mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
    mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2
    mx3, my3 = (x1 + x3) / 2, (y1 + y3) / 2
    darker = tuple(max(0, c - 12 * depth) for c in color)
    _sierpinski(surf, x1, y1, mx1, my1, mx3, my3, depth - 1, color)
    _sierpinski(surf, mx1, my1, x2, y2, mx2, my2, depth - 1, darker)
    _sierpinski(surf, mx3, my3, mx2, my2, x3, y3, depth - 1, color)


def _koch_curve_pts(x1, y1, x2, y2, depth):
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(_koch_curve_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(_koch_curve_pts(ax, ay, px, py, depth - 1))
    pts.extend(_koch_curve_pts(px, py, bx, by, depth - 1))
    pts.extend(_koch_curve_pts(bx, by, x2, y2, depth - 1))
    return pts


def _koch_snowflake(cx, cy, size, depth):
    r = size * 0.45
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]
    verts = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]
    all_pts = []
    for i in range(3):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 3]
        all_pts.extend(_koch_curve_pts(x1, y1, x2, y2, depth))
    return all_pts


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------
class Building(Entity):
    def __init__(self, col, row, building_type, owner):
        d = BUILDING_DEFS[building_type]
        size = d["size"]
        cx = col * TILE_SIZE + (size * TILE_SIZE) // 2
        cy = row * TILE_SIZE + (size * TILE_SIZE) // 2
        super().__init__(cx, cy, d["hp"], owner)
        self.building_type = building_type
        self.col, self.row = col, row
        self.size = size
        self.built = False
        self.build_progress = 0.0
        self.build_time = d["build_time"]

        # training
        self.train_queue = []
        self.train_progress = 0.0
        self.train_time = 0.0

        # refinery
        self.refine_progress = 0.0
        self.refine_active = False

        # tower
        self.tower_timer = 0.0
        self.tower_level = 1             # v10c: 1=cannon, 2=explosive
        self.tower_upgrading = False
        self.tower_upgrade_progress = 0.0

        # ruin state
        self.ruined = False

        # v10_1: VDD Phase 3 animation state
        self._refinery_rotation = random.uniform(0, 6.28)  # start offset
        # v10_1: rally point (world coords or None)
        self.rally_point = None

    def take_damage(self, dmg, attacker=None):
        """Override: completed player buildings become ruins instead of dying."""
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            if self.owner == "player" and self.built and not self.ruined:
                # become a ruin
                self.ruined = True
                self.built = False
                self.build_progress = 0.0
                self.hp = max(1, int(self.max_hp * 0.1))  # ruins have 10% HP
                self.train_queue.clear()
                self.refine_active = False
            else:
                self.alive = False

    def can_upgrade_tower(self):
        """v10c: Check if this tower can be upgraded to explosive."""
        return (self.building_type == "tower" and self.built
                and not self.ruined and self.tower_level < 2
                and not self.tower_upgrading)

    def get_tiles(self):
        tiles = []
        for dr in range(self.size):
            for dc in range(self.size):
                tiles.append((self.col + dc, self.row + dr))
        return tiles

    def update(self, dt, game):
        if not self.alive:
            return
        # v10_1: refinery gear rotation (always animates, even under construction)
        if self.building_type == "refinery":
            self._refinery_rotation += dt * 0.3
        if not self.built or self.ruined:
            return

        # training
        if self.train_queue:
            self.train_progress += dt
            if self.train_progress >= self.train_time:
                utype = self.train_queue.pop(0)
                self.train_progress = 0.0
                # spawn unit adjacent
                sx = self.x + (self.size * TILE_SIZE // 2 + 8)
                sy = self.y + (self.size * TILE_SIZE // 2 + 8)
                unit = Unit(sx, sy, utype, self.owner)
                game.player_units.append(unit)
                # v10_1: rally point — auto-move to rally
                if self.rally_point:
                    unit.command_move(self.rally_point[0], self.rally_point[1], game)
                if self.train_queue:
                    self.train_time = UNIT_DEFS[self.train_queue[0]]["train"]

        # refinery auto-refine
        if self.building_type == "refinery":
            if self.refine_active:
                self.refine_progress += dt
                if self.refine_progress >= REFINE_TIME:
                    self.refine_active = False
                    self.refine_progress = 0.0
                    game.resources.steel += REFINE_STEEL_YIELD
            elif game.resources.iron >= REFINE_IRON_COST:
                game.resources.iron -= REFINE_IRON_COST
                self.refine_active = True
                self.refine_progress = 0.0

        # v10c: tower ballistic cannon — utility-scored targeting, fires cannonball
        if self.building_type == "tower":
            self.tower_timer = max(0, self.tower_timer - dt)
            if self.tower_timer <= 0:
                best = None
                best_score = -1
                for e in game.enemy_units:
                    if not e.alive:
                        continue
                    d = dist(self.x, self.y, e.x, e.y)
                    if d > TOWER_CANNON_RANGE:
                        continue
                    score = UNIT_PRIORITY.get(e.unit_type, 3.0)
                    score *= TOWER_HIGH_THREAT_TYPES.get(e.unit_type, 1.0)
                    hp_ratio = e.hp / e.max_hp if e.max_hp > 0 else 1.0
                    if hp_ratio < TOWER_LOW_HP_THRESHOLD:
                        score *= TOWER_LOW_HP_BONUS
                    score *= 1.0 / (1.0 + d / TOWER_CANNON_RANGE)
                    if score > best_score:
                        best_score = score
                        best = e
                if best:
                    # fire cannonball toward target's current position (no lead)
                    dx = best.x - self.x
                    dy = best.y - self.y
                    d = math.hypot(dx, dy)
                    if d > 0:
                        dx /= d
                        dy /= d
                    # apply spread
                    angle_off = random.uniform(-TOWER_CANNON_SPREAD, TOWER_CANNON_SPREAD)
                    cos_a = math.cos(angle_off)
                    sin_a = math.sin(angle_off)
                    fdx = dx * cos_a - dy * sin_a
                    fdy = dx * sin_a + dy * cos_a
                    is_explosive = self.tower_level >= 2
                    dmg = TOWER_EXPLOSIVE_DIRECT if is_explosive else TOWER_CANNON_DAMAGE
                    ball = Cannonball(self.x, self.y, fdx, fdy, dmg, "player",
                                     explosive=is_explosive)
                    game.cannonballs.append(ball)
                    self.tower_timer = TOWER_CANNON_CD

    def start_train(self, unit_type, game):
        d = UNIT_DEFS[unit_type]
        if not game.resources.can_afford(gold=d["gold"], wood=d["wood"], steel=d["steel"]):
            return False
        game.resources.spend(gold=d["gold"], wood=d["wood"], steel=d["steel"])
        self.train_queue.append(unit_type)
        game.logger.log(
            game.game_time, "TRAINING_STARTED",
            game.enemy_ai.wave_number,
            unit_type, self.building_type)
        if len(self.train_queue) == 1:
            self.train_time = d["train"]
            self.train_progress = 0.0
        return True

    # -- v10_1: VDD Phase 3 — Algorithmic building shape renderers ----------

    def _draw_town_hall_shape(self, surf, cx, cy, size, build_pct, is_ruin):
        """L-system branching tree — grows during construction."""
        trunk_c = (46, 30, 14) if is_ruin else _TH_BROWN
        tip_c = (20, 40, 20) if is_ruin else _TH_GREEN
        iters = max(0, min(4, int(build_pct * 4 + 0.5)))
        if is_ruin:
            iters = min(1, iters)
        if size < 20:
            iters = min(2, iters)
        if iters == 0:
            pygame.draw.line(surf, trunk_c, (cx, cy), (cx, cy - size // 3), 3)
            return
        instructions = _l_system_expand("F", {"F": "FF+[+F-F-F]-[-F+F+F]"}, iters)
        step = size / (3.0 * (1.5 ** iters))
        _l_system_render(surf, cx, cy, instructions, angle_deg=22.5,
                         step=step, col_trunk=trunk_c, col_tip=tip_c,
                         line_width=max(1, 4 - iters))

    def _draw_barracks_shape(self, surf, cx, cy, size, build_pct, is_ruin):
        """Sierpinski triangle lattice — military precision."""
        color = (47, 15, 15) if is_ruin else _BK_MAROON
        depth = max(0, min(4, int(build_pct * 4 + 0.5)))
        if is_ruin:
            depth = min(1, depth)
        if size < 20:
            depth = min(2, depth)
        half = size * 0.45
        h = half * math.sqrt(3)
        x1, y1 = cx, cy - h * 0.6
        x2, y2 = cx - half, cy + h * 0.4
        x3, y3 = cx + half, cy + h * 0.4
        _sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color)
        border_c = tuple(min(255, c + 40) for c in color)
        pygame.draw.polygon(surf, border_c,
                            [(int(x1), int(y1)), (int(x2), int(y2)),
                             (int(x3), int(y3))], 2)

    def _draw_refinery_shape(self, surf, cx, cy, size, build_pct, is_ruin):
        """Spirograph epitrochoid gear — rotates when active."""
        color = (33, 33, 43) if is_ruin else _RF_GRAY
        if build_pct < 0.1:
            pygame.draw.circle(surf, color, (int(cx), int(cy)), int(size * 0.4), 2)
            return
        R, r, d = 5.0, 3.0, 5.0
        scale = size * 0.35 / (R + r + d)
        max_t = build_pct * 6 * math.pi
        n_points = max(20, int(max_t * 15))
        rotation = self._refinery_rotation
        points = []
        for i in range(n_points):
            t = rotation + max_t * i / max(1, n_points - 1)
            x = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
            y = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
            points.append((cx + x * scale, cy + y * scale))
        if len(points) >= 2:
            closed = build_pct >= 0.95
            pygame.draw.lines(surf, color, closed, points, max(1, size // 40))
        # cusp highlights (gear teeth)
        if build_pct >= 0.5 and not is_ruin:
            accent = _STEEL_BLUE
            step_pts = max(1, len(points) // 8)
            for i in range(0, len(points), step_pts):
                pygame.draw.circle(surf, accent,
                                   (int(points[i][0]), int(points[i][1])),
                                   max(2, size // 25))

    def _draw_tower_shape(self, surf, cx, cy, size, build_pct, is_ruin, level):
        """Koch snowflake battlement — more detail at Lv.2."""
        depth = max(0, min(3, int(build_pct * 3 + 0.5)))
        if level >= 2:
            depth = min(4, depth + 1)
        if is_ruin:
            depth = min(1, depth)
        if size < 16:
            depth = min(2, depth)
        if depth == 0:
            half = size * 0.35
            pygame.draw.rect(surf, _TW_STONE if not is_ruin else (53, 53, 47),
                             (cx - half, cy - half, half * 2, half * 2), 2)
            return
        points = _koch_snowflake(cx, cy, size, depth)
        int_pts = [(int(p[0]), int(p[1])) for p in points]
        if len(int_pts) >= 3:
            fill = (53, 53, 47) if is_ruin else (_TW_STONE if level == 1 else (180, 160, 120))
            pygame.draw.polygon(surf, fill, int_pts)
            border = (80, 80, 70) if is_ruin else ((200, 200, 180) if level == 1 else _FORGE_ORANGE)
            pygame.draw.polygon(surf, border, int_pts, max(1, size // 30))
        # Lv.2: orange glow dots on Koch tips
        if level >= 2 and not is_ruin and len(points) > 10:
            step_pts = max(1, len(points) // 12)
            for i in range(0, len(points), step_pts):
                pygame.draw.circle(surf, _FORGE_ORANGE,
                                   (int(points[i][0]), int(points[i][1])),
                                   max(2, size // 20))

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.col * TILE_SIZE, self.row * TILE_SIZE)
        z = cam.zoom
        px_size = int(self.size * TILE_SIZE * z)

        if sx + px_size < 0 or sx > SCREEN_WIDTH or sy + px_size < GAME_AREA_Y - px_size or sy > GAME_AREA_Y + GAME_AREA_H + px_size:
            return

        # -- v10_1: VDD Phase 3 algorithmic shapes replace flat rectangles --
        cx = sx + px_size // 2
        cy = sy + px_size // 2
        is_ruin = self.ruined
        build_pct = 1.0 if self.built else (self.build_progress / self.build_time if self.build_time > 0 else 0)

        # subtle dark foundation under the fractal shape
        if px_size >= 8:
            base_alpha = 40 if is_ruin else 80
            base_col = (15, 15, 20) if not is_ruin else (10, 10, 12)
            foundation = pygame.Surface((px_size, px_size), pygame.SRCALPHA)
            foundation.fill((*base_col, base_alpha))
            surf.blit(foundation, (sx, sy))

        if self.building_type == "town_hall":
            # tree grows from bottom center upward
            tree_base_y = sy + px_size - int(4 * z)
            self._draw_town_hall_shape(surf, cx, tree_base_y, px_size, build_pct, is_ruin)
        elif self.building_type == "barracks":
            self._draw_barracks_shape(surf, cx, cy, px_size, build_pct, is_ruin)
        elif self.building_type == "refinery":
            self._draw_refinery_shape(surf, cx, cy, px_size, build_pct, is_ruin)
        elif self.building_type == "tower":
            self._draw_tower_shape(surf, cx, cy, px_size, build_pct, is_ruin, self.tower_level)
        else:
            # fallback: flat rect
            color = BUILDING_COLORS.get(self.building_type, (100, 100, 100))
            if is_ruin:
                color = tuple(c // 3 for c in color)
            elif not self.built:
                color = tuple(c // 2 for c in color)
            pygame.draw.rect(surf, color, (sx, sy, px_size, px_size))

        # selection ring
        if self.selected:
            sel_rect = pygame.Rect(sx, sy, px_size, px_size).inflate(
                max(2, int(6 * z)), max(2, int(6 * z)))
            pygame.draw.rect(surf, COL_SELECT, sel_rect, 2)

        # label (fades to subtlety over large shapes)
        if z >= 0.5:
            label = BUILDING_LABELS.get(self.building_type, "??")
            fsz = max(10, int((20 if self.size > 1 else 16) * z))
            font = pygame.font.SysFont(None, fsz)
            draw_text(surf, label, cx, cy, font, (255, 255, 255), center=True)

        # build progress bar
        if not self.built:
            ratio = self.build_progress / self.build_time
            bw = px_size - 4
            bh = max(2, int(6 * z))
            pygame.draw.rect(surf, (40, 40, 40), (sx + 2, sy + px_size - bh - 2, bw, bh))
            pygame.draw.rect(surf, (0, 180, 255), (sx + 2, sy + px_size - bh - 2, int(bw * ratio), bh))

        # health bar
        if self.hp < self.max_hp:
            self.draw_health_bar(surf, cam, width=px_size)

        # train progress
        if self.built and self.train_queue:
            ratio = self.train_progress / self.train_time if self.train_time > 0 else 0
            bw = px_size - 4
            bh = max(2, int(4 * z))
            pygame.draw.rect(surf, (40, 40, 40), (sx + 2, sy + px_size + 2, bw, bh))
            pygame.draw.rect(surf, (255, 200, 0), (sx + 2, sy + px_size + 2, int(bw * ratio), bh))

        # tower upgrade progress bar
        if self.tower_upgrading and self.built:
            ratio = self.tower_upgrade_progress / TOWER_UPGRADE_TIME
            bw = px_size - 4
            bh = max(2, int(6 * z))
            pygame.draw.rect(surf, (40, 40, 40), (sx + 2, sy + px_size + 2, bw, bh))
            pygame.draw.rect(surf, (255, 140, 40), (sx + 2, sy + px_size + 2, int(bw * ratio), bh))


# (Projectile class removed v10_1 — replaced by Arrow and Cannonball)


# ---------------------------------------------------------------------------
# Arrow  (v9 — ballistic, non-homing projectile)
# ---------------------------------------------------------------------------
class Arrow:
    def __init__(self, x, y, dx, dy, damage, owner, source_unit=None):
        self.x, self.y = float(x), float(y)
        self.dx, self.dy = dx, dy          # normalized direction
        self.damage = damage
        self.owner = owner
        self.source_unit = source_unit      # for XP grant on hit
        self.speed = ARROW_SPEED
        self.alive = True
        self.lifetime = ARROW_MAX_LIFETIME
        self.grounded = False
        self.ground_timer = 0.0

    def update(self, dt, game):
        if self.grounded:
            self.ground_timer -= dt
            if self.ground_timer <= 0:
                self.alive = False
            return

        # move in straight line
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.lifetime -= dt

        # hit detection against appropriate targets
        if self.owner == "player":
            targets = game.enemy_units
        else:
            targets = game.player_units + game.player_buildings

        for t in targets:
            if not t.alive:
                continue
            if dist(self.x, self.y, t.x, t.y) < ARROW_HIT_RADIUS:
                t.take_damage(self.damage, self.source_unit)
                _process_combat_hit(self.source_unit, t, game, "arrow")
                self.alive = False
                return

        # off map or lifetime expired → become ground arrow
        if (self.lifetime <= 0
                or self.x < 0 or self.x > MAP_COLS * TILE_SIZE
                or self.y < 0 or self.y > MAP_ROWS * TILE_SIZE):
            self.grounded = True
            self.ground_timer = GROUND_ARROW_LIFETIME

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        if self.grounded:
            # small dimmed line stuck in ground
            length = max(3, int(6 * z))
            color = (120, 100, 80)
            ex = sx + int(self.dx * length)
            ey = sy + int(self.dy * length)
            pygame.draw.line(surf, color, (sx, sy), (ex, ey), max(1, int(z)))
        else:
            # in flight: bright line in direction of travel
            length = max(4, int(10 * z))
            color = (255, 240, 120) if self.owner == "player" else (255, 120, 120)
            # tail behind the arrow
            tx = sx - int(self.dx * length)
            ty = sy - int(self.dy * length)
            pygame.draw.line(surf, color, (tx, ty), (sx, sy), max(1, int(2 * z)))
            # arrowhead dot
            pygame.draw.circle(surf, color, (sx, sy), max(1, int(2 * z)))


# ---------------------------------------------------------------------------
# Cannonball  (v10c — ballistic tower projectile, can be explosive)
# ---------------------------------------------------------------------------
class Cannonball:
    def __init__(self, x, y, dx, dy, damage, owner, explosive=False):
        self.x, self.y = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.damage = damage
        self.owner = owner
        self.explosive = explosive
        self.speed = TOWER_CANNON_SPEED
        self.alive = True
        self.lifetime = TOWER_CANNON_LIFETIME

    def update(self, dt, game):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.lifetime -= dt

        targets = game.enemy_units  # towers are always player-owned

        for t in targets:
            if not t.alive:
                continue
            if dist(self.x, self.y, t.x, t.y) < TOWER_CANNON_HIT_RADIUS:
                if self.explosive:
                    t.take_damage(TOWER_EXPLOSIVE_DIRECT)
                    _process_combat_hit(None, t, game, "tower")
                    # AoE: damage all enemies in blast radius
                    for e in targets:
                        if e is t or not e.alive:
                            continue
                        if dist(self.x, self.y, e.x, e.y) < TOWER_EXPLOSIVE_RADIUS:
                            e.take_damage(TOWER_EXPLOSIVE_DAMAGE)
                            _process_combat_hit(None, e, game, "tower")
                    game.explosions.append(Explosion(self.x, self.y))
                else:
                    t.take_damage(self.damage)
                    _process_combat_hit(None, t, game, "tower")
                self.alive = False
                return

        # off map or lifetime expired
        if (self.lifetime <= 0
                or self.x < 0 or self.x > MAP_COLS * TILE_SIZE
                or self.y < 0 or self.y > MAP_ROWS * TILE_SIZE):
            # explosive cannonballs detonate on ground impact
            if self.explosive:
                for e in targets:
                    if not e.alive:
                        continue
                    if dist(self.x, self.y, e.x, e.y) < TOWER_EXPLOSIVE_RADIUS:
                        e.take_damage(TOWER_EXPLOSIVE_DAMAGE)
                        _process_combat_hit(None, e, game, "tower")
                game.explosions.append(Explosion(self.x, self.y))
            self.alive = False

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        r = max(3, int(5 * z))
        color = (80, 80, 80) if not self.explosive else (180, 100, 30)
        pygame.draw.circle(surf, color, (sx, sy), r)
        # motion trail
        tx = sx - int(self.dx * r * 2)
        ty = sy - int(self.dy * r * 2)
        pygame.draw.line(surf, (60, 60, 60), (tx, ty), (sx, sy), max(1, int(2 * z)))


# ---------------------------------------------------------------------------
# Explosion VFX  (v10_1 — Lissajous bloom replaces expanding ring)
# ---------------------------------------------------------------------------
class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.timer = 0.0
        self.duration = 0.5
        self.alive = True
        self._phase = random.uniform(0, math.pi)  # visual variety

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.alive = False

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        progress = self.timer / self.duration
        fade = max(0.0, 1.0 - progress)
        max_r = TOWER_EXPLOSIVE_RADIUS * z

        # Lissajous figure: expanding, rotating star-flower
        a_ratio, b_ratio = 3, 2  # 3:2 produces a trefoil-like figure
        delta = self._phase + progress * math.pi * 2
        n_pts = 48
        A = max_r * progress
        B = A * 0.85
        pts = []
        for i in range(n_pts):
            t = 2 * math.pi * i / n_pts
            lx = A * math.sin(a_ratio * t + delta)
            ly = B * math.sin(b_ratio * t)
            pts.append((sx + int(lx), sy + int(ly)))

        if len(pts) >= 3:
            # bright core → fading outer
            r_val = min(255, int(255 * fade))
            g_val = min(255, int(180 * fade + 60 * progress))
            b_val = min(255, int(40 * fade))
            color = (r_val, g_val, b_val)
            width = max(1, int(3 * z * fade))
            pygame.draw.polygon(surf, color, pts, width)

        # inner ring for extra glow
        if progress < 0.6:
            inner_r = max(2, int(max_r * progress * 0.4))
            glow_a = int(200 * fade)
            pygame.draw.circle(surf, (255, min(255, 200 + int(55 * progress)), 80),
                               (sx, sy), inner_r, max(1, int(2 * z * fade)))


# SquadManager moved to squads.py (v9.3 cleanup)
