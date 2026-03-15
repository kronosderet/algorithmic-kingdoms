import math
import random
import pygame
from constants import (UNIT_DEFS, BUILDING_DEFS, BUILDING_COLORS,
                       BUILDING_LABELS, TILE_SIZE,
                       SCREEN_WIDTH, GAME_AREA_Y, GAME_AREA_H,
                       COL_SELECT,
                       REFINE_IRON_COST, REFINE_STEEL_YIELD, REFINE_TIME,
                       TOWER_CANNON_DAMAGE, TOWER_CANNON_CD,
                       TOWER_CANNON_RANGE, TOWER_MIN_RANGE, TOWER_CANNON_SPREAD,
                       TOWER_UPGRADE_TIME, TOWER_UPGRADE_FIRE_MULT,
                       TOWER_EXPLOSIVE_DIRECT,
                       TOWER_LOW_HP_BONUS, TOWER_LOW_HP_THRESHOLD,
                       TOWER_HIGH_THREAT_TYPES,
                       UNIT_PRIORITY,
                       GARRISON_ARMOR_PER_WORKER,
                       GARRISON_DAMAGE_PER_WORKER, GARRISON_ATTACK_CD,
                       GARRISON_ATTACK_RANGE,
                       UPGRADE_PATH, PRODUCTION_RATES, PRODUCTION_TICK_INTERVAL,
                       FORGE_STONE_COST, FORGE_IRON_COST,
                       FORGE_STEEL_YIELD, FORGE_TIME,
                       SMELTER_REFINERY_BONUS, FORGE_WORKER_SPEED_BONUS,
                       SENTINEL_CRY_COOLDOWN, SENTINEL_CRY_RADIUS,
                       SENTINEL_CRY_BUFF_DURATION, SENTINEL_CRY_PULSE_DURATION,
                       MSG_COL_ECONOMY, display_name)
from entity_base import Entity
from fractal_ui import fractal_bar_simple
from building_shapes import (_l_system_expand, _l_system_render, _sierpinski,
                             _koch_snowflake,
                             _TH_BROWN, _TH_GREEN, _BK_MAROON,
                             _RF_GRAY, _TW_STONE, _FORGE_ORANGE, _STEEL_BLUE)
from utils import dist
from fractal_font import fractal_font


# Forward reference: Cannonball is imported at runtime to avoid circular import
_Cannonball = None


def _get_cannonball_class():
    global _Cannonball
    if _Cannonball is None:
        from projectiles import Cannonball
        _Cannonball = Cannonball
    return _Cannonball


# Forward reference: Unit is imported at runtime to avoid circular import
_Unit = None


def _get_unit_class():
    global _Unit
    if _Unit is None:
        from unit import Unit
        _Unit = Unit
    return _Unit


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
        self.rally_point: tuple[float, float] | None = None
        # v10_2: garrison (town hall only)
        self.garrison = []
        self.garrison_attack_timer = 0.0
        # v10.2: upgrade state (helper → production)
        self.upgrading_to = None
        self.upgrade_progress = 0.0
        self.upgrade_time = 0.0
        # v10.2: production building
        self.production_timer = 0.0
        self.stationed_workers = []
        # v10.2: smelter boost flag (refinery only)
        self.smelter_boosted = False
        # v10_7: Sentinel's Cry — tower dead zone mechanic
        self.cry_timer = 0.0
        self.cry_pulse_timer = 0.0

    def take_damage(self, dmg, attacker=None):
        """Override: completed player buildings become ruins instead of dying."""
        # v10_2: garrison armor — reduce damage when workers are inside
        if self.building_type == "town_hall" and self.garrison:
            reduction = min(len(self.garrison) * GARRISON_ARMOR_PER_WORKER, 0.5)
            dmg = max(1, int(dmg * (1.0 - reduction)))
        if attacker is not None:
            self.last_attacker = attacker
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            if self.owner == "player" and self.built and not self.ruined:
                # become a ruin — eject garrisoned/stationed workers
                if self.garrison:
                    self._eject_garrison()
                if self.stationed_workers:
                    self._eject_stationed()
                self.ruined = True
                self.built = False
                self.build_progress = 0.0
                self.hp = max(1, int(self.max_hp * 0.1))  # ruins have 10% HP
                self.train_queue.clear()
                self.refine_active = False
                self.upgrading_to = None
            else:
                self.alive = False

    def _eject_garrison(self):
        """Eject all garrisoned workers, placing them around the building."""
        for i, w in enumerate(self.garrison):
            angle = (2 * math.pi * i) / max(1, len(self.garrison))
            w.x = self.x + math.cos(angle) * 40
            w.y = self.y + math.sin(angle) * 40
            w.state = "idle"
            w.garrison_target = None
        self.garrison.clear()

    def _eject_stationed(self):
        """Eject all stationed workers from a production building."""
        for i, w in enumerate(self.stationed_workers):
            angle = (2 * math.pi * i) / max(1, len(self.stationed_workers))
            w.x = self.x + math.cos(angle) * 40
            w.y = self.y + math.sin(angle) * 40
            w.state = "idle"
            w.station_target = None
        self.stationed_workers.clear()

    def can_upgrade(self):
        """v10.2: Check if this helper building can be upgraded to production."""
        return (self.built and not self.ruined and self.upgrading_to is None
                and self.building_type in UPGRADE_PATH)

    def _can_upgrade_at(self, game):
        """v10.2: Check if surrounding tiles allow 1x1 → 2x2 expansion."""
        if self.building_type not in UPGRADE_PATH:
            return False
        new_def = BUILDING_DEFS[UPGRADE_PATH[self.building_type]]
        new_size = new_def["size"]
        if new_size <= self.size:
            return True  # no expansion needed (e.g. refinery→forge is 2x2→2x2)
        for dr in range(new_size):
            for dc in range(new_size):
                if dc < self.size and dr < self.size:
                    continue  # already occupied by this building
                tc, tr = self.col + dc, self.row + dr
                if not game.game_map.is_buildable(tc, tr):
                    return False
                for b in game.player_buildings:
                    if b is self or not b.alive:
                        continue
                    for bc, br in b.get_tiles():
                        if tc == bc and tr == br:
                            return False
        return True

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
                UnitClass = _get_unit_class()
                unit = UnitClass(sx, sy, utype, self.owner)
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
                    if d > TOWER_CANNON_RANGE or d < TOWER_MIN_RANGE:
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
                    # v10_5: fire cannonball at target position (parabolic arc)
                    # Apply spread as angular offset to the target point
                    aim_x, aim_y = best.x, best.y
                    angle_off = random.uniform(-TOWER_CANNON_SPREAD, TOWER_CANNON_SPREAD)
                    if angle_off != 0:
                        dx = aim_x - self.x
                        dy = aim_y - self.y
                        cos_a = math.cos(angle_off)
                        sin_a = math.sin(angle_off)
                        aim_x = self.x + dx * cos_a - dy * sin_a
                        aim_y = self.y + dx * sin_a + dy * cos_a
                    is_explosive = self.tower_level >= 2
                    dmg = TOWER_EXPLOSIVE_DIRECT if is_explosive else TOWER_CANNON_DAMAGE
                    CannonballClass = _get_cannonball_class()
                    ball = CannonballClass(self.x, self.y, aim_x, aim_y, dmg,
                                          "player", explosive=is_explosive)
                    game.cannonballs.append(ball)
                    # v10_7: 50% fire rate while upgrading
                    cd_mult = TOWER_UPGRADE_FIRE_MULT if self.tower_upgrading else 1.0
                    self.tower_timer = TOWER_CANNON_CD * cd_mult

        # v10_7: Sentinel's Cry — tower detects enemies in dead zone, buffs nearby allies
        if self.building_type == "tower" and self.built and not self.ruined:
            self.cry_pulse_timer = max(0, self.cry_pulse_timer - dt)
            self.cry_timer = max(0, self.cry_timer - dt)  # cooldown ticks always
            if self.cry_timer <= 0:
                # only scan for dead zone enemies when ready to fire
                dead_zone_enemies = [e for e in game.enemy_units
                                     if e.alive and dist(self.x, self.y, e.x, e.y) < TOWER_MIN_RANGE]
                if dead_zone_enemies:
                    self.cry_timer = SENTINEL_CRY_COOLDOWN
                    self.cry_pulse_timer = SENTINEL_CRY_PULSE_DURATION
                    # buff nearby friendly units
                    for u in game.player_units:
                        if u.alive and dist(self.x, self.y, u.x, u.y) <= SENTINEL_CRY_RADIUS:
                            u.sentinel_cry_buff = SENTINEL_CRY_BUFF_DURATION
                    # highlight dead zone enemies
                    for e in dead_zone_enemies:
                        e.sentinel_highlighted = SENTINEL_CRY_BUFF_DURATION

        # v10_2: garrison attack — garrisoned workers hurl stones at enemies
        if self.building_type == "town_hall" and self.garrison:
            self.garrison_attack_timer = max(0, self.garrison_attack_timer - dt)
            if self.garrison_attack_timer <= 0:
                best = None
                best_d = GARRISON_ATTACK_RANGE
                for e in game.enemy_units:
                    if not e.alive:
                        continue
                    d = dist(self.x, self.y, e.x, e.y)
                    if d < best_d:
                        best_d = d
                        best = e
                if best:
                    total_dmg = GARRISON_DAMAGE_PER_WORKER * len(self.garrison)
                    best.take_damage(total_dmg, self)
                    self.garrison_attack_timer = GARRISON_ATTACK_CD

        # v10.2: production buildings — generate resources on timer
        if self.built and not self.ruined and self.building_type in PRODUCTION_RATES:
            self.production_timer += dt
            if self.production_timer >= PRODUCTION_TICK_INTERVAL:
                self.production_timer -= PRODUCTION_TICK_INTERVAL
                n_workers = len(self.stationed_workers)
                pconfig = PRODUCTION_RATES[self.building_type]
                rate = pconfig["base_rate"] + pconfig["worker_rate"] * n_workers
                # v10_beta: skilled workers produce faster (worker rank speed bonus)
                if n_workers > 0:
                    skill_key = pconfig.get("skill")
                    if skill_key:
                        avg_rank = sum(
                            getattr(w, 'get_skill_rank', lambda s: 0)(skill_key)
                            for w in self.stationed_workers
                        ) / n_workers
                        rate *= (1.0 + avg_rank * 0.10)  # +10% per average skill rank
                game.resources.add(pconfig["resource"], rate)
                game.logger.log(
                    game.game_time, "RESOURCE_PRODUCED",
                    game.enemy_ai.wave_number,
                    self.building_type, pconfig["resource"],
                    "", rate,
                    f"workers={n_workers}")

        # v10.2: Forge — Stone + Iron → Steel (auto-refine like refinery)
        if self.built and not self.ruined and self.building_type == "forge":
            if not self.refine_active:
                # try to start a forge cycle
                if (game.resources.stone >= FORGE_STONE_COST
                        and game.resources.iron >= FORGE_IRON_COST):
                    game.resources.stone -= FORGE_STONE_COST
                    game.resources.iron -= FORGE_IRON_COST
                    self.refine_active = True
                    self.refine_progress = 0.0
            if self.refine_active:
                # stationed workers boost forge speed
                n_workers = len(self.stationed_workers)
                speed_mult = 1.0 + FORGE_WORKER_SPEED_BONUS * n_workers
                self.refine_progress += dt * speed_mult
                forge_time = FORGE_TIME
                if self.refine_progress >= forge_time:
                    self.refine_active = False
                    self.refine_progress = 0.0
                    game.resources.steel += FORGE_STEEL_YIELD
                    game.logger.log(
                        game.game_time, "RESOURCE_PRODUCED",
                        game.enemy_ai.wave_number,
                        "forge", "steel",
                        "", FORGE_STEEL_YIELD,
                        f"stone={FORGE_STONE_COST} iron={FORGE_IRON_COST}")

        # v10.2: Smelter-boosted refinery — faster refining
        if (self.built and not self.ruined and self.building_type == "refinery"
                and self.smelter_boosted and self.refine_active):
            # add bonus progress (30% of dt on top of normal)
            self.refine_progress += dt * SMELTER_REFINERY_BONUS

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
        game.add_message(f"Training {display_name(unit_type)}", MSG_COL_ECONOMY)
        if len(self.train_queue) == 1:
            self.train_time = d["train"]
            self.train_progress = 0.0
        return True

    # -- v10_1: VDD Phase 3 — Algorithmic building shape renderers ----------

    def _draw_town_hall_shape(self, surf, cx, cy, size, build_pct, is_ruin):
        """L-system Tree of Life — large, visible tree with thick trunk,
        root system, and dense canopy. Furls into protective bush when
        garrison is active."""
        trunk_c = (46, 30, 14) if is_ruin else _TH_BROWN
        tip_c = (20, 40, 20) if is_ruin else _TH_GREEN
        root_c = (90, 60, 30) if not is_ruin else (35, 25, 12)
        iters = max(0, min(5, int(build_pct * 5 + 0.5)))
        if is_ruin:
            iters = min(1, iters)
        if size < 30:
            iters = min(2, iters)
        if iters == 0:
            pygame.draw.line(surf, trunk_c, (cx, cy), (cx, cy - size // 3), 3)
            return

        # Trunk dimensions (used by cache)
        trunk_h = size * 0.18
        trunk_w = max(2, int(size * 0.06))

        # Symmetric rule: dense branching for full crown
        # v10_8b: Cache L-system expansion (deterministic per iters)
        if not hasattr(self, '_lsys_cache_iters') or self._lsys_cache_iters != iters:
            self._lsys_cache_iters = iters
            self._lsys_instructions = _l_system_expand("F", {"F": "FF[+F[-F]F][-F[+F]F]"}, iters)
        instructions = self._lsys_instructions
        step = size / (4.5 * (1.7 ** iters))
        # garrison furl: animate toward target (smooth lerp)
        furl_target = 1.0 if (self.garrison and not is_ruin) else 0.0
        self._garrison_furl = getattr(self, '_garrison_furl', 0.0)
        furl_speed = 1.2
        if self._garrison_furl < furl_target:
            self._garrison_furl = min(furl_target,
                                       self._garrison_furl + furl_speed / 60.0)
        elif self._garrison_furl > furl_target:
            self._garrison_furl = max(furl_target,
                                       self._garrison_furl - furl_speed / 60.0)
        # v10_8b: Cache rendered tree surface — quantize furl to avoid per-frame redraw
        furl_q = round(self._garrison_furl * 20) / 20.0  # 5% steps
        lw = max(1, 5 - iters)
        cache_key = (iters, int(size), is_ruin, furl_q)
        if not hasattr(self, '_tree_surf_cache_key') or self._tree_surf_cache_key != cache_key:
            self._tree_surf_cache_key = cache_key
            # Render tree onto a local surface centered at (margin, margin+trunk_h)
            margin = int(size * 0.6)
            tw, th = margin * 2, int(size * 1.2)
            tree_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
            # Draw roots on cached surface
            tcx, tcy = margin, int(th * 0.75)
            if iters >= 2 and not is_ruin:
                root_spread = size * 0.35
                root_depth = size * 0.08
                for angle_off in (-0.7, -0.35, 0.35, 0.7):
                    rx = tcx + root_spread * math.sin(angle_off)
                    ry = tcy + root_depth * abs(math.sin(angle_off * 2))
                    rw = max(1, 3 - abs(int(angle_off * 2)))
                    pygame.draw.line(tree_surf, root_c, (int(tcx), int(tcy)),
                                     (int(rx), int(ry)), rw)
            # Trunk
            pygame.draw.line(tree_surf, trunk_c, (tcx, int(tcy)),
                             (tcx, int(tcy - trunk_h)), trunk_w)
            # Branches
            _l_system_render(tree_surf, tcx, tcy - trunk_h, instructions, angle_deg=22.0,
                             step=step, col_trunk=trunk_c, col_tip=tip_c,
                             line_width=lw, furl=furl_q)
            self._tree_surf_cache = tree_surf
            self._tree_surf_offset = (margin, int(th * 0.75))
        # Blit cached tree
        ox, oy = self._tree_surf_offset
        surf.blit(self._tree_surf_cache, (int(cx - ox), int(cy - oy)))

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

    def _draw_economy_building(self, surf, cx, cy, size, build_pct, is_ruin):
        """v10.2: Algorithmic shapes for helper and production buildings."""
        bt = self.building_type
        color = BUILDING_COLORS.get(bt, (100, 100, 100))
        if is_ruin:
            color = tuple(c // 3 for c in color)
        elif not self.built:
            color = tuple(c // 2 for c in color)
        r = max(4, int(size * 0.4))

        if bt == "goldmine_hut":
            # small golden diamond
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(surf, color, pts)
            pygame.draw.polygon(surf, tuple(min(255, c + 50) for c in color), pts, max(1, size // 16))
        elif bt == "lumber_camp":
            # triangle log pile
            half = r
            pygame.draw.polygon(surf, color,
                [(cx, cy - half), (cx - half, cy + half), (cx + half, cy + half)])
            # log lines
            lc = tuple(min(255, c + 30) for c in color)
            for i in range(3):
                y_off = cy - half // 2 + i * (half // 2)
                pygame.draw.line(surf, lc, (cx - half // 2, y_off), (cx + half // 2, y_off), max(1, size // 16))
        elif bt == "quarry_hut":
            # hexagon (stone shape)
            pts = []
            for i in range(6):
                a = math.pi / 6 + i * math.pi / 3
                pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
            pygame.draw.polygon(surf, color, pts)
            pygame.draw.polygon(surf, tuple(min(255, c + 40) for c in color), pts, max(1, size // 16))
        elif bt == "iron_depot":
            # square with cross (iron ingots)
            pygame.draw.rect(surf, color, (cx - r, cy - r, r * 2, r * 2))
            lc = tuple(min(255, c + 50) for c in color)
            pygame.draw.line(surf, lc, (cx - r, cy), (cx + r, cy), max(1, size // 12))
            pygame.draw.line(surf, lc, (cx, cy - r), (cx, cy + r), max(1, size // 12))
        elif bt == "scaffold":
            # scaffold frame — crosshatch lines
            lw = max(1, size // 12)
            pygame.draw.rect(surf, color, (cx - r, cy - r, r * 2, r * 2), lw)
            pygame.draw.line(surf, color, (cx - r, cy - r), (cx + r, cy + r), lw)
            pygame.draw.line(surf, color, (cx + r, cy - r), (cx - r, cy + r), lw)
            # aura ring (subtle)
            if self.built and not is_ruin:
                pygame.draw.circle(surf, (200, 200, 100), (cx, cy), int(size * 0.6), 1)
        elif bt == "sawmill":
            # larger triangle with gear circle
            half = r
            pygame.draw.polygon(surf, color,
                [(cx, cy - half), (cx - half, cy + half), (cx + half, cy + half)])
            gc = tuple(min(255, c + 40) for c in color)
            pygame.draw.circle(surf, gc, (cx, cy + half // 4), half // 3, max(1, size // 20))
        elif bt == "goldmine":
            # larger diamond with inner diamond
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(surf, color, pts)
            ir = r // 2
            inner = [(cx, cy - ir), (cx + ir, cy), (cx, cy + ir), (cx - ir, cy)]
            pygame.draw.polygon(surf, tuple(min(255, c + 60) for c in color), inner)
        elif bt == "stoneworks":
            # larger hexagon with inner hexagon
            pts = []
            for i in range(6):
                a = math.pi / 6 + i * math.pi / 3
                pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
            pygame.draw.polygon(surf, color, pts)
            ir = r * 2 // 3
            inner = []
            for i in range(6):
                a = math.pi / 6 + i * math.pi / 3
                inner.append((cx + int(ir * math.cos(a)), cy + int(ir * math.sin(a))))
            pygame.draw.polygon(surf, tuple(min(255, c + 40) for c in color), inner)
        elif bt == "iron_works":
            # larger iron cross with filled center
            pygame.draw.rect(surf, color, (cx - r, cy - r, r * 2, r * 2))
            lc = tuple(min(255, c + 50) for c in color)
            third = r // 3
            pygame.draw.rect(surf, lc, (cx - third, cy - r, third * 2, r * 2))
            pygame.draw.rect(surf, lc, (cx - r, cy - third, r * 2, third * 2))
        elif bt == "forge":
            # anvil shape — trapezoid with flame-colored top
            half = r
            # base trapezoid
            pts = [(cx - half, cy + half), (cx + half, cy + half),
                   (cx + half // 2, cy - half // 2), (cx - half // 2, cy - half // 2)]
            pygame.draw.polygon(surf, color, pts)
            # flame accent on top
            if not is_ruin and self.built:
                flame_c = (255, 120, 30)
                fh = half // 3
                pygame.draw.polygon(surf, flame_c,
                    [(cx - half // 3, cy - half // 2),
                     (cx, cy - half // 2 - fh),
                     (cx + half // 3, cy - half // 2)])

        # upgrade progress bar (if upgrading)
        if self.upgrading_to and self.upgrade_time > 0:
            ratio = self.upgrade_progress / self.upgrade_time
            bw = size - 4
            bh = max(2, size // 8)
            pygame.draw.rect(surf, (40, 40, 40), (cx - bw // 2, cy + r + 4, bw, bh))
            pygame.draw.rect(surf, (100, 255, 100), (cx - bw // 2, cy + r + 4, int(bw * ratio), bh))

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
            # tree grows from bottom center upward — 2x visual height
            tree_base_y = sy + px_size - int(4 * z)
            tree_size = int(px_size * 2.0)
            self._draw_town_hall_shape(surf, cx, tree_base_y, tree_size, build_pct, is_ruin)
        elif self.building_type == "barracks":
            self._draw_barracks_shape(surf, cx, cy, px_size, build_pct, is_ruin)
        elif self.building_type == "refinery":
            self._draw_refinery_shape(surf, cx, cy, px_size, build_pct, is_ruin)
        elif self.building_type == "tower":
            self._draw_tower_shape(surf, cx, cy, px_size, build_pct, is_ruin, self.tower_level)
            # v10_7: Sentinel's Cry pulse ring VFX
            if self.cry_pulse_timer > 0 and not is_ruin:
                pulse_progress = 1.0 - self.cry_pulse_timer / SENTINEL_CRY_PULSE_DURATION
                pulse_r = int((SENTINEL_CRY_RADIUS * z) * pulse_progress)
                pulse_alpha = int(180 * (1.0 - pulse_progress))
                if pulse_r > 0 and pulse_alpha > 0:
                    cry_surf = pygame.Surface((pulse_r * 2, pulse_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(cry_surf, (80, 180, 255, pulse_alpha),
                                       (pulse_r, pulse_r), pulse_r, max(1, int(2 * z)))
                    surf.blit(cry_surf, (cx - pulse_r, cy - pulse_r))
        elif self.building_type in ("goldmine_hut", "lumber_camp", "quarry_hut",
                                     "iron_depot", "scaffold",
                                     "sawmill", "goldmine", "stoneworks",
                                     "iron_works", "forge"):
            self._draw_economy_building(surf, cx, cy, px_size, build_pct, is_ruin)
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
            fractal_font.draw(surf, label, cx, cy, fsz, (255, 255, 255), center=True)

        # build progress bar
        if not self.built and self.build_time > 0:
            ratio = self.build_progress / self.build_time
            bw = px_size - 4
            bh = max(2, int(6 * z))
            fractal_bar_simple(surf, sx + 2, sy + px_size - bh - 2, bw, bh, ratio, (0, 180, 255))

        # health bar
        if self.hp < self.max_hp:
            self.draw_health_bar(surf, cam, width=px_size)

        # train progress
        if self.built and self.train_queue:
            ratio = self.train_progress / self.train_time if self.train_time > 0 else 0
            bw = px_size - 4
            bh = max(2, int(4 * z))
            fractal_bar_simple(surf, sx + 2, sy + px_size + 2, bw, bh, ratio, (255, 200, 0))

        # tower upgrade progress bar
        if self.tower_upgrading and self.built:
            ratio = self.tower_upgrade_progress / TOWER_UPGRADE_TIME
            bw = px_size - 4
            bh = max(2, int(6 * z))
            pygame.draw.rect(surf, (40, 40, 40), (sx + 2, sy + px_size + 2, bw, bh))
            pygame.draw.rect(surf, (255, 140, 40), (sx + 2, sy + px_size + 2, int(bw * ratio), bh))


# (Projectile class removed v10_1 — replaced by Arrow and Cannonball)
