import pygame
import math
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE,
                       MAP_COLS, MAP_ROWS, TOP_BAR_H, BOTTOM_PANEL_H,
                       GAME_AREA_Y, GAME_AREA_H, ZOOM_STEP,
                       MINIMAP_SIZE, MINIMAP_MARGIN, MINIMAP_X, MINIMAP_Y,
                       TERRAIN_GRASS, TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON, TERRAIN_STONE,
                       TERRAIN_COLORS, BUILDING_DEFS, BUILDING_LABELS,
                       COL_BG, COL_SELECT, COL_TEXT, COL_GUI_BG, COL_GUI_BORDER,
                       DIFFICULTY_PROFILES,
                       HEAL_RATE_NEAR_TH, HEAL_RADIUS_TH,
                       GROUND_ARROW_MAX,
                       SELECT_RADIUS, DRAG_THRESHOLD,
                       TOWER_UPGRADE_COST, TOWER_CANNON_DAMAGE,
                       TOWER_CANNON_CD, TOWER_EXPLOSIVE_DIRECT,
                       RALLY_POINT_COLOR,
                       GARRISON_COST,
                       DROPOFF_BUILDING_TYPES, PRODUCTION_RATES,
                       UPGRADE_PATH,
                       STANCE_AGGRESSIVE, STANCE_DEFENSIVE, STANCE_GUARD,
                       STANCE_HUNT, STANCE_NAMES, STANCE_COLORS,
                       FORMATION_POLAR_ROSE, FORMATION_GOLDEN_SPIRAL,
                       FORMATION_SIERPINSKI, FORMATION_KOCH, FORMATION_NAMES,
                       FORMATION_ROTATION_SPEED,
                       SPIRAL_C_MIN, SPIRAL_C_MAX, SPIRAL_C_STEP,
                       RESONANCE_KOCH_RADIUS_MULT, FORMATION_KOCH_RADIUS,
                       RESONANCE_DISSONANCE_RADIUS, RESONANCE_COLORS,
                       FORMATION_DISCOVERY, HARMONY_IDEAL_RATIOS,
                       DISCOVERY_RATIO_TOLERANCE, DISCOVERY_NOTIFICATIONS,
                       DOUBLE_CLICK_THRESHOLD, COMBAT_HEAT_DURATION,
                       WORKER_SPAWN_OFFSET, WORKER_SPAWN_SPACING,
                       ENTITY_TOOLTIP_RADIUS,
                       ARRIVAL_CHECK_RADIUS, ARRIVAL_CHECK_TIMEOUT,
                       PENDING_GROUP_MIN, FORMATION_MIN_VIABLE,
                       CMD_RING_DURATION, CMD_RING_MAX_RADIUS,
                       CMD_RING_COLOR_MOVE, CMD_RING_COLOR_ATTACK,
                       CMD_RING_COLOR_GATHER, CMD_RING_COLOR_BUILD,
                       CMD_RING_COLOR_RALLY,
                       MSG_LOG_MAX, MSG_LOG_VISIBLE, MSG_LOG_FADE,
                       MSG_COL_INFO, MSG_COL_DISCOVERY, MSG_COL_ATTACK,
                       MSG_COL_ECONOMY, MSG_COL_COMMAND,
                       display_name)
from utils import dist, pos_to_tile, draw_text, ruin_rebuild_cost
from game_map import GameMap
from camera import Camera
from spatial_grid import SpatialGrid
from resources import ResourceManager
from entities import Unit, Building
from squads import SquadManager
from enemy_ai import EnemyAI
from gui import GUI
from event_logger import EventLogger


class Game:
    def __init__(self, screen, difficulty="medium"):
        # close previous logger on restart (R key re-calls __init__)
        if hasattr(self, 'logger') and self.logger:
            self.logger.close(self)

        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.game_won = False
        self.game_surrendered = False
        self.paused = False
        self.pause_menu_selection = 0  # v10_8d: highlighted menu item

        # difficulty
        self.difficulty = difficulty
        self.difficulty_profile = DIFFICULTY_PROFILES[difficulty]
        profile = self.difficulty_profile

        self.game_map = GameMap()
        self.camera = Camera()
        self.resources = ResourceManager(
            gold=profile["start_gold"],
            wood=profile["start_wood"],
            iron=profile["start_iron"],
            steel=profile["start_steel"])
        self.gui = GUI()
        self.gui.init_fonts()
        self.enemy_ai = EnemyAI(difficulty)
        self.game_time = 0.0
        self.logger = EventLogger(difficulty)

        self.player_units = []
        self.player_buildings = []
        self.enemy_units = []
        self.arrows = []           # v9: ballistic arrows in flight
        self.ground_arrows = []    # v9: grounded arrows (visual only)
        self.cannonballs = []      # v10c: tower cannonballs in flight
        self.explosions = []       # v10c: explosion VFX
        self.craters = []          # v10_5: ground craters from cannonball impacts
        self.escaped_enemies = []  # enemies that fled to map edge

        # v9: squad managers
        self.player_squad_mgr = SquadManager()
        self.enemy_squad_mgr = SquadManager()

        self.selected = []  # list of entities

        # input state
        self.selecting = False
        self.select_start: tuple[int, int] | None = None
        self.placing_building = None  # building type str or None

        # font cache
        self.font = pygame.font.SysFont(None, 22)
        self.font_sm = pygame.font.SysFont(None, 18)
        self.font_xs = pygame.font.SysFont(None, 15)
        self.font_lg = pygame.font.SysFont(None, 48)
        self.font_notif = pygame.font.SysFont(None, 26)

        # minimap
        self.minimap_surf = None

        # notifications
        self._notifications = []  # list of [text, timer, color]

        # command confirmation effects (world-space expanding rings)
        self._cmd_effects = []  # list of [wx, wy, timer, color_rgba]

        # message log (persistent, color-coded)
        self._message_log: list[list] = []  # [[text, game_time, color], ...]
        self.show_message_log = False  # toggle with L key

        # wave clear tracking
        self._had_enemies = False

        # v10_1: attack-move mode (A key, then click)
        self.attack_move_mode = False

        # v10_delta: pending group formation checks
        self._pending_groups = []  # list of {units, dest, timestamp}

        # v10_2: inspected enemy (left-click enemy to view stats, no commands)
        self.inspected_enemy = None

        # v10_1: minimap combat heat overlay
        self._combat_heat = []  # list of [x, y, timer]  (world coords)

        # v10_4: spatial grids for O(1) neighbor queries
        self.player_grid = SpatialGrid(cell_size=80)
        self.enemy_grid = SpatialGrid(cell_size=80)

        # v10_4: cached map terrain surface (redrawn only when tiles change)
        self._map_cache = None       # pygame.Surface
        self._map_cache_zoom = None  # zoom level when cache was built
        self._map_cache_rect = None  # visible_rect when cache was built
        self._map_dirty = True       # flag to force rebuild
        self._minimap_dirty = True   # separate flag for minimap rebuild

        # v10_4: pre-sorted unit list (maintained via insertion sort)
        self._sorted_units = []

        # v10_8d: progressive UI unlock tracker
        self.unlocks = {
            "has_barracks": False,       # built a barracks
            "has_refinery": False,       # built a refinery
            "has_tower": False,          # built a tower
            "has_squad": False,          # any squad formed (rank 1+ unit)
            "has_iron": False,           # mined iron at least once
            "has_stone": False,          # mined stone at least once
            "has_steel": False,          # refined steel at least once
            "first_wave_cleared": False, # cleared wave 1
            "max_rank_seen": 0,          # highest unit rank achieved
            "formations_used": set(),    # which formations player has tried
        }
        # v10_alpha: formation discovery — starts empty, discovered through composition
        self.discovered_formations = set()

        self._setup_start()

    def _setup_start(self):
        profile = self.difficulty_profile
        center_c, center_r = MAP_COLS // 2, MAP_ROWS // 2
        # place town hall
        th = Building(center_c - 1, center_r - 1, "town_hall", "player")
        th.built = True
        # mark tiles as occupied
        for tc, tr in th.get_tiles():
            self.game_map.tiles[tr][tc] = 0  # TERRAIN_GRASS
        self.player_buildings.append(th)

        # starting workers (from difficulty profile)
        num_workers = profile.get("start_workers", 3)
        for i in range(num_workers):
            wx = th.x + WORKER_SPAWN_OFFSET + i * WORKER_SPAWN_SPACING
            wy = th.y + WORKER_SPAWN_OFFSET
            w = Unit(wx, wy, "worker", "player")
            self.player_units.append(w)

    def add_notification(self, text, duration=3.0, color=(255, 255, 100)):
        """Add a floating notification message + persistent log entry."""
        self._notifications.append([text, duration, color])
        self.add_message(text, color)

    def add_cmd_effect(self, wx: float, wy: float, color: tuple = CMD_RING_COLOR_MOVE):
        """Add an expanding ring at world position to confirm a command."""
        self._cmd_effects.append([wx, wy, CMD_RING_DURATION, color])

    def add_message(self, text: str, color: tuple = MSG_COL_INFO):
        """Add a persistent message to the in-game log."""
        self._message_log.append([text, self.game_time, color])
        if len(self._message_log) > MSG_LOG_MAX:
            self._message_log.pop(0)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self.handle_events()
            if not self.paused:
                self.game_time += dt
            if not self.game_over and not self.game_won and not self.paused:
                self.update(dt)
            self.gui.update_tooltip(dt)
            self.render()
        self.logger.close(self)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.game_over or self.game_won:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__(self.screen, self.difficulty)
                    return
                continue

            # v10_8d: pause toggle
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_PAUSE):
                self.paused = not self.paused
                self.pause_menu_selection = 0
                continue

            # v10_8d: pause menu navigation
            if self.paused and event.type == pygame.KEYDOWN:
                self._handle_pause_key(event.key)
                continue
            if self.paused and event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_pause_click(event.pos)
                continue
            if self.paused:
                continue  # swallow all other input while paused

            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                # v10_epsilon: Ctrl+scroll adjusts Spiral formation tightness
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    handled = False
                    for u in self.selected:
                        if not hasattr(u, 'unit_type'):
                            continue
                        sq = self.player_squad_mgr.get_squad(u)
                        if sq and sq.formation == FORMATION_GOLDEN_SPIRAL:
                            sq.spiral_c = max(SPIRAL_C_MIN,
                                              min(SPIRAL_C_MAX,
                                                  sq.spiral_c + event.y * SPIRAL_C_STEP))
                            if not handled:
                                label = "tight" if sq.spiral_c <= 14 else "loose" if sq.spiral_c >= 26 else "normal"
                                self.add_notification(
                                    f"Spiral: {label} (c={sq.spiral_c:.0f})",
                                    1.0, RESONANCE_COLORS[FORMATION_GOLDEN_SPIRAL])
                                handled = True
                elif GAME_AREA_Y <= my < GAME_AREA_Y + GAME_AREA_H:
                    self.camera.apply_zoom(event.y * ZOOM_STEP, mx, my)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_left_down(event.pos)
                elif event.button == 3:
                    shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                    self._handle_right_click(event.pos, queued=bool(shift))

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self._handle_left_up(event.pos)

    def _handle_key(self, key):
        # F10: surrender — end the suffering
        if key == pygame.K_F10:
            self.game_over = True
            self.game_surrendered = True
            self.logger.log(self.game_time, "SURRENDER",
                            self.enemy_ai.wave_number, "surrender", self.difficulty,
                            note="player surrendered")
            return

        if key == pygame.K_ESCAPE:
            if self.attack_move_mode:
                self.attack_move_mode = False
                return
            if self.placing_building:
                self.placing_building = None
            else:
                for e in self.selected:
                    e.selected = False
                self.selected.clear()
                self.inspected_enemy = None

        # cache worker selection (used by build hotkeys)
        workers_selected = [u for u in self.selected if isinstance(u, Unit) and u.unit_type == "worker"]

        # v10_beta: X key = attack-move mode (WASD reserved for camera)
        if key == pygame.K_x:
            combat_sel = [e for e in self.selected
                          if isinstance(e, Unit) and e.unit_type in ("soldier", "archer")]
            if combat_sel:
                self.attack_move_mode = True
                return

        # v10_8: Tab / Shift+Tab = cycle through squads
        if key == pygame.K_TAB:
            mods = pygame.key.get_mods()
            squads = self.player_squad_mgr.squad_list
            active = [s for s in squads if s.alive_count > 0]
            if active:
                direction = -1 if (mods & pygame.KMOD_SHIFT) else 1
                self._select_squad_cycle(active, direction)
            return

        # v10_8: 1-9 = squad selection (replaces Ctrl+0-9 groups)
        # When workers selected, 1-4 fall through to build hotkeys
        mods = pygame.key.get_mods()
        num_keys = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4,
                    pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7, pygame.K_8: 8,
                    pygame.K_9: 9}
        if key in num_keys and not (mods & pygame.KMOD_CTRL):
            squad_idx = num_keys[key] - 1  # 0-based
            # workers + keys 1-4: fall through to build hotkeys
            if workers_selected and squad_idx < 4:
                pass  # fall through
            else:
                active = [s for s in self.player_squad_mgr.squad_list if s.alive_count > 0]
                if squad_idx < len(active):
                    self._select_squad(active[squad_idx])
                    # v10_8: double-tap = center camera on squad leader
                    now = pygame.time.get_ticks()
                    if (hasattr(self, '_last_squad_tap_idx')
                            and self._last_squad_tap_idx == squad_idx
                            and now - self._last_squad_tap_time < DOUBLE_CLICK_THRESHOLD):
                        leader = active[squad_idx].leader
                        if leader and leader.alive:
                            z = self.camera.zoom
                            self.camera.x = leader.x - SCREEN_WIDTH / (2 * z)
                            self.camera.y = leader.y - GAME_AREA_H / (2 * z)
                    self._last_squad_tap_idx = squad_idx
                    self._last_squad_tap_time = now
                    return

        # v10_6: Formation hotkeys F1-F4 — apply to selected squads
        combat_sel = [e for e in self.selected
                      if isinstance(e, Unit) and e.unit_type in ("soldier", "archer")]
        if combat_sel:
            formation_keys = {
                pygame.K_F1: FORMATION_POLAR_ROSE,
                pygame.K_F2: FORMATION_GOLDEN_SPIRAL,
                pygame.K_F3: FORMATION_SIERPINSKI,
                pygame.K_F4: FORMATION_KOCH,
            }
            stance_keys = {
                pygame.K_F5: STANCE_AGGRESSIVE,
                pygame.K_F6: STANCE_DEFENSIVE,
                pygame.K_F7: STANCE_GUARD,
                pygame.K_F8: STANCE_HUNT,
            }
            if key in formation_keys:
                fmt = formation_keys[key]
                shift = pygame.key.get_mods() & pygame.KMOD_SHIFT

                # v10_delta: check if selected units are free → create squad
                free_units = [u for u in combat_sel if self.player_squad_mgr.is_free(u)]
                squadded_units = [u for u in combat_sel if not self.player_squad_mgr.is_free(u)]

                if shift and len(combat_sel) >= FORMATION_MIN_VIABLE:
                    # Priority mode: pull ALL selected into new squad
                    if fmt not in self.discovered_formations:
                        self.add_notification("Formation not yet discovered", 1.5, (180, 100, 100))
                        return
                    sq = self.player_squad_mgr.create_squad(free_units, formation=fmt)
                    if sq:
                        for u in squadded_units:
                            self.player_squad_mgr.reinforce_squad(sq, [u], force=True)
                        self.add_notification(
                            f"Priority: {FORMATION_NAMES[fmt]} ({sq.alive_count} units)",
                            2.0, (255, 180, 40))
                    return
                elif free_units and len(free_units) >= FORMATION_MIN_VIABLE:
                    # Create new squad from free units
                    if fmt not in self.discovered_formations:
                        self.add_notification("Formation not yet discovered", 1.5, (180, 100, 100))
                        return
                    sq = self.player_squad_mgr.create_squad(free_units, formation=fmt)
                    if sq:
                        self.add_notification(
                            f"Squad formed: {FORMATION_NAMES[fmt]} ({sq.alive_count} units)",
                            2.0, (100, 255, 100))
                    return
                else:
                    # Change formation of existing squads
                    seen_squads = set()
                    for u in combat_sel:
                        sq = self.player_squad_mgr.get_squad(u)
                        if sq and sq.squad_id not in seen_squads:
                            seen_squads.add(sq.squad_id)
                            sq.formation = fmt
                    if seen_squads:
                        self.add_notification(
                            f"Formation: {FORMATION_NAMES[fmt]}", 1.5, (180, 220, 255))
                    return
            if key in stance_keys:
                st = stance_keys[key]
                seen_squads = set()
                for u in combat_sel:
                    sq = self.player_squad_mgr.get_squad(u)
                    if sq and sq.squad_id not in seen_squads:
                        seen_squads.add(sq.squad_id)
                        sq.stance = st
                        for m in sq.members:
                            if m.alive:
                                m.command_set_stance(st)
                                m.stance = st
                        if st == STANCE_GUARD:
                            sq.guard_position = (sq.leader.x, sq.leader.y) if sq.leader else None
                color = STANCE_COLORS.get(st, (180, 220, 255))
                self.add_notification(f"Stance: {STANCE_NAMES[st]}", 1.5, color)
                return

        # v10_delta: Delete key — dissolve selected squad
        if key == pygame.K_DELETE and combat_sel:
            seen = set()
            for u in combat_sel:
                sq = self.player_squad_mgr.get_squad(u)
                if sq and sq.squad_id not in seen:
                    seen.add(sq.squad_id)
                    freed = self.player_squad_mgr.dissolve_squad(sq)
                    self.add_notification(
                        f"Squad dissolved — {len(freed)} units freed", 2.5, (255, 180, 40))

        # v10_epsilon: R key — toggle Rose rotation (sweep combat)
        if key == pygame.K_r and combat_sel:
            seen = set()
            for u in combat_sel:
                sq = self.player_squad_mgr.get_squad(u)
                if sq and sq.squad_id not in seen and sq.formation == FORMATION_POLAR_ROSE:
                    seen.add(sq.squad_id)
                    sq.is_rotating = not sq.is_rotating
                    sq.rotation_speed = FORMATION_ROTATION_SPEED if sq.is_rotating else 0.0
                    label = "Rose sweep activated" if sq.is_rotating else "Rose sweep stopped"
                    self.add_notification(label, 1.5, (220, 80, 40))

        # v10_epsilon: V key — formation ability (Sierpinski pulse / Koch contract)
        if key == pygame.K_v and combat_sel:
            seen = set()
            for u in combat_sel:
                sq = self.player_squad_mgr.get_squad(u)
                if sq and sq.squad_id not in seen:
                    seen.add(sq.squad_id)
                    if sq.activate_ability():
                        if sq.formation == FORMATION_SIERPINSKI:
                            self.add_notification("Sierpinski pulse!",
                                                  1.0, RESONANCE_COLORS[FORMATION_SIERPINSKI])
                        elif sq.formation == FORMATION_KOCH:
                            self.add_notification("Koch contract!",
                                                  1.0, RESONANCE_COLORS[FORMATION_KOCH])

        # L key: toggle message log panel
        if key == pygame.K_l:
            self.show_message_log = not self.show_message_log

        # build hotkeys (need worker selected)
        if workers_selected:
            if key == pygame.K_1:
                self.start_placement("town_hall")
            elif key == pygame.K_2:
                self.start_placement("barracks")
            elif key == pygame.K_3:
                self.start_placement("refinery")
            elif key == pygame.K_4:
                self.start_placement("tower")
            # v10_8c: G = mine nearest resource
            elif key == pygame.K_g:
                self.command_gather_nearest_selected()
                return

        # train hotkeys (need building selected)
        buildings_selected = [e for e in self.selected if isinstance(e, Building) and e.built]
        for b in buildings_selected:
            if key == pygame.K_q and b.building_type == "town_hall":
                b.start_train("worker", self)
            elif key == pygame.K_t and b.building_type == "barracks":
                b.start_train("soldier", self)
            elif key == pygame.K_e and b.building_type == "barracks":
                b.start_train("archer", self)
            elif key == pygame.K_u and b.can_upgrade_tower():
                self.start_tower_upgrade(b)

        if key == pygame.K_SPACE and self.selected:
            e = self.selected[0]
            z = self.camera.zoom
            self.camera.x = e.x - SCREEN_WIDTH / (2 * z)
            self.camera.y = e.y - GAME_AREA_H / (2 * z)

    def _handle_left_down(self, pos):
        sx, sy = pos

        # check minimap click
        if self._minimap_click(sx, sy):
            return

        # check GUI first
        if sy >= SCREEN_HEIGHT - BOTTOM_PANEL_H:
            if self.gui.handle_click(pos):
                return

        if sy < GAME_AREA_Y or sy >= GAME_AREA_Y + GAME_AREA_H:
            return

        # v10_1: attack-move click — move to position, auto-attack anything in range
        if self.attack_move_mode:
            self.attack_move_mode = False
            wx, wy = self.camera.screen_to_world(sx, sy)
            units_sel = [e for e in self.selected if isinstance(e, Unit) and e.unit_type != "worker"]
            for u in units_sel:
                u.command_attack_move(wx, wy, self)
            return

        # building placement
        if self.placing_building:
            wx, wy = self.camera.screen_to_world(sx, sy)
            col, row = pos_to_tile(wx, wy)
            if self._can_place_building(self.placing_building, col, row):
                self._place_building(self.placing_building, col, row)
            return

        # start drag select
        self.selecting = True
        self.select_start = pos

    def _handle_left_up(self, pos):
        if not self.selecting:
            return
        self.selecting = False

        sx, sy = pos
        assert self.select_start is not None
        start_sx, start_sy = self.select_start

        if abs(sx - start_sx) < DRAG_THRESHOLD and abs(sy - start_sy) < DRAG_THRESHOLD:
            # single click select
            self._single_select(pos)
        else:
            # drag select
            self._box_select(self.select_start, pos)

        self.select_start = None

    def _single_select(self, pos):
        sx, sy = pos
        wx, wy = self.camera.screen_to_world(sx, sy)
        shift = pygame.key.get_mods() & pygame.KMOD_SHIFT

        # v10_8: shift+click = additive, otherwise deselect all
        if not shift:
            for e in self.selected:
                e.selected = False
            self.selected.clear()
            self.inspected_enemy = None

        # check player units first
        best = None
        best_d = SELECT_RADIUS
        for u in self.player_units:
            if not u.alive or u.state in ("garrisoned", "stationed"):
                continue
            d = dist(wx, wy, u.x, u.y)
            if d < best_d:
                best_d = d
                best = u

        # check buildings
        if not best:
            best = self._find_building_at(wx, wy)

        if best:
            if shift and best in self.selected:
                # shift+click on already-selected: deselect it
                best.selected = False
                self.selected.remove(best)
            elif best not in self.selected:
                best.selected = True
                self.selected.append(best)
                # v10_8: double-click = select all same type on screen
                now = pygame.time.get_ticks()
                if (isinstance(best, Unit)
                        and hasattr(self, '_last_click_time')
                        and now - self._last_click_time < 400
                        and hasattr(self, '_last_click_unit')
                        and self._last_click_unit is best):
                    self._select_all_same_type(best)
                self._last_click_time = now
                self._last_click_unit = best
        else:
            if not shift:
                # v10_2: check enemy units for inspection (info only, no commands)
                best_enemy = None
                best_ed = SELECT_RADIUS
                for e in self.enemy_units:
                    if not e.alive:
                        continue
                    d = dist(wx, wy, e.x, e.y)
                    if d < best_ed:
                        best_ed = d
                        best_enemy = e
                if best_enemy:
                    self.inspected_enemy = best_enemy

    def _select_all_same_type(self, unit):
        """Double-click: select all visible units of same type."""
        utype = unit.unit_type
        for u in self.player_units:
            if not u.alive or u.state in ("garrisoned", "stationed"):
                continue
            if u.unit_type != utype or u in self.selected:
                continue
            sx, sy = self.camera.world_to_screen(u.x, u.y)
            if 0 <= sx <= SCREEN_WIDTH and GAME_AREA_Y <= sy <= GAME_AREA_Y + GAME_AREA_H:
                u.selected = True
                self.selected.append(u)

    def _box_select(self, start, end):
        shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if not shift:
            for e in self.selected:
                e.selected = False
            self.selected.clear()

        x1 = min(start[0], end[0])
        y1 = min(start[1], end[1])
        x2 = max(start[0], end[0])
        y2 = max(start[1], end[1])

        for u in self.player_units:
            if not u.alive or u.state in ("garrisoned", "stationed"):
                continue
            if u in self.selected:
                continue
            sx, sy = self.camera.world_to_screen(u.x, u.y)
            if x1 <= sx <= x2 and y1 <= sy <= y2:
                u.selected = True
                self.selected.append(u)

    def _select_squad(self, squad):
        """Select all alive members of a squad."""
        for e in self.selected:
            e.selected = False
        self.selected.clear()
        self.inspected_enemy = None
        for m in squad.members:
            if m.alive:
                m.selected = True
                self.selected.append(m)

    def _select_squad_cycle(self, active_squads, direction=1):
        """Cycle through squads with Tab/Shift+Tab."""
        # Find which squad is currently selected (if any)
        current_idx = -1
        if self.selected:
            first = self.selected[0]
            if isinstance(first, Unit):
                sq = self.player_squad_mgr.get_squad(first)
                if sq:
                    for i, s in enumerate(active_squads):
                        if s is sq:
                            current_idx = i
                            break
        next_idx = (current_idx + direction) % len(active_squads)
        self._select_squad(active_squads[next_idx])

    def _handle_right_click(self, pos, queued=False):
        sx, sy = pos
        if sy < GAME_AREA_Y or sy >= GAME_AREA_Y + GAME_AREA_H:
            return

        # cancel placement
        if self.placing_building:
            self.placing_building = None
            return

        wx, wy = self.camera.screen_to_world(sx, sy)

        units_sel = [e for e in self.selected if isinstance(e, Unit)]
        if not units_sel:
            # v10_1: rally point — right-click with building selected sets rally
            buildings_sel = [e for e in self.selected if isinstance(e, Building) and e.built
                             and e.building_type in ("town_hall", "barracks")]
            if buildings_sel:
                for b in buildings_sel:
                    b.rally_point = (wx, wy)
                self.add_notification("Rally point set", 1.5, RALLY_POINT_COLOR)
                self.add_cmd_effect(wx, wy, CMD_RING_COLOR_RALLY)
            return

        # check enemy at position
        for e in self.enemy_units:
            if not e.alive:
                continue
            if dist(wx, wy, e.x, e.y) < SELECT_RADIUS:
                for u in units_sel:
                    u.command_attack(e, self)
                self.add_cmd_effect(e.x, e.y, CMD_RING_COLOR_ATTACK)
                return

        # check resource tile
        col, row = pos_to_tile(wx, wy)
        tile_t = self.game_map.get_tile(col, row)
        if tile_t in (TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON, TERRAIN_STONE):
            workers = [u for u in units_sel if u.unit_type == "worker"]
            for w in workers:
                w.command_gather(col, row, self)
            # move non-workers near the spot
            others = [u for u in units_sel if u.unit_type != "worker"]
            for u in others:
                u.command_move(wx, wy, self)
            self.add_cmd_effect(wx, wy, CMD_RING_COLOR_GATHER)
            return

        # check player building -- ruin rebuild, resume build, or repair
        b = self._find_building_at(wx, wy)
        if b:
            workers = [u for u in units_sel if u.unit_type == "worker"]
            handled = False
            if b.ruined:
                # rebuild from ruin at reduced cost
                gold_cost, wood_cost, iron_cost, steel_cost, stone_cost = ruin_rebuild_cost(b.building_type)
                if workers and self.resources.can_afford(
                        gold=gold_cost, wood=wood_cost,
                        iron=iron_cost, steel=steel_cost,
                        stone=stone_cost):
                    self.resources.spend(
                        gold=gold_cost, wood=wood_cost,
                        iron=iron_cost, steel=steel_cost,
                        stone=stone_cost)
                    b.ruined = False
                    for w in workers:
                        w.command_build(b, self)
                    self.add_notification(
                        f"Rebuilding {display_name(b.building_type)} from ruins",
                        2.0, (180, 180, 255))
                    handled = True
            elif not b.built:
                # resume/assist construction
                for w in workers:
                    w.command_build(b, self)
                handled = True
            elif b.hp < b.max_hp:
                # repair damaged building
                for w in workers:
                    w.command_repair(b, self)
                handled = True
            elif b.can_upgrade_tower():
                # v10c: upgrade tower to explosive cannon
                cost = TOWER_UPGRADE_COST
                if workers and self.resources.can_afford(steel=cost["steel"]):
                    self.resources.spend(steel=cost["steel"])
                    for w in workers:
                        w.command_tower_upgrade(b, self)
                    self.add_notification("Upgrading tower to Explosive Cannon (15 steel)", 2.0, (255, 140, 40))
                    handled = True
            elif (b.built and not b.ruined
                  and (b.building_type in PRODUCTION_RATES or b.building_type == "forge")):
                # v10.2: station workers in production buildings
                if workers:
                    for w in workers:
                        w.command_station(b, self)
                    self.add_notification(
                        f"Workers stationing in {BUILDING_LABELS.get(b.building_type, b.building_type)}",
                        1.5, (220, 180, 80))
                    handled = True
            # else: fully built and healthy -- fall through to move
            if handled:
                self.add_cmd_effect(wx, wy, CMD_RING_COLOR_BUILD)
                others = [u for u in units_sel if u.unit_type != "worker"]
                for u in others:
                    u.command_move(wx, wy, self)
                return

        # v10_beta: formation-aware move — squads arrive in formation
        self._formation_move_selected(units_sel, wx, wy, queued=queued)
        self.add_cmd_effect(wx, wy, CMD_RING_COLOR_MOVE)

    def _formation_move_selected(self, units, wx, wy, queued=False):
        """v10_beta: Move selected units. Squads move in formation;
        solo units move individually to the destination."""
        seen_squads = {}
        solo = []
        for u in units:
            sq = self.player_squad_mgr.get_squad(u)
            if sq:
                if sq.squad_id not in seen_squads:
                    seen_squads[sq.squad_id] = (sq, [])
                seen_squads[sq.squad_id][1].append(u)
            else:
                solo.append(u)

        for sq_id, (sq, members) in seen_squads.items():
            if sq.leader in members:
                if queued:
                    # Shift-queue: each unit queues their slot position
                    for u in members:
                        u.command_move(wx, wy, self, queued=True)
                else:
                    self.player_squad_mgr.formation_move(sq, wx, wy, self)
            else:
                for u in members:
                    u.command_move(wx, wy, self, queued=queued)

        for u in solo:
            u.command_move(wx, wy, self, queued=queued)

        # v10_delta: track free military units for group discovery
        free_military = [u for u in solo
                         if u.unit_type in ("soldier", "archer") and u.alive]
        if len(free_military) >= PENDING_GROUP_MIN and not queued:
            self._pending_groups.append({
                "units": free_military,
                "dest": (wx, wy),
                "timestamp": self.game_time,
            })

    def _update_pending_groups(self, dt):
        """v10_delta: Check if pending free-unit groups have arrived at destination."""
        still_pending = []
        for pg in self._pending_groups:
            # Timeout
            if self.game_time - pg["timestamp"] > ARRIVAL_CHECK_TIMEOUT:
                continue
            # Remove dead units
            pg["units"] = [u for u in pg["units"] if u.alive]
            if len(pg["units"]) < PENDING_GROUP_MIN:
                continue
            # Check if all arrived
            dx, dy = pg["dest"]
            all_arrived = all(
                u.state == "idle" and
                math.hypot(u.x - dx, u.y - dy) < ARRIVAL_CHECK_RADIUS * 3
                for u in pg["units"]
            )
            if all_arrived:
                self._check_group_discovery(pg["units"])
            else:
                still_pending.append(pg)
        self._pending_groups = still_pending

    def _check_group_discovery(self, units):
        """v10_delta: Check if a group of free units matches a formation recipe."""
        soldiers = sum(1 for u in units if u.unit_type == "soldier")
        archers = sum(1 for u in units if u.unit_type == "archer")
        total = soldiers + archers
        if total < PENDING_GROUP_MIN:
            return
        veterans = sum(1 for u in units if u.alive and getattr(u, 'rank', 0) >= 1)

        from constants import (FORMATION_DISCOVERY, DISCOVERY_RATIO_TOLERANCE,
                               DISCOVERY_NOTIFICATIONS, HARMONY_IDEAL_RATIOS)

        discovered_any = False
        best_formation = None
        for fmt_idx, recipe in FORMATION_DISCOVERY.items():
            if fmt_idx in self.discovered_formations:
                continue
            if total < recipe["min_size"]:
                continue
            if veterans < recipe["min_veterans"]:
                continue
            # Check ratio
            if recipe.get("any_ratio"):
                pass  # Rose: any composition works
            else:
                majority = max(soldiers, archers)
                minority = min(soldiers, archers)
                if minority == 0:
                    continue  # monotone can't discover non-Rose
                actual_ratio = majority / minority
                ideal = HARMONY_IDEAL_RATIOS[fmt_idx]
                deviation = abs(actual_ratio - ideal) / max(ideal, 0.01)
                if deviation >= DISCOVERY_RATIO_TOLERANCE:
                    continue

            self.discovered_formations.add(fmt_idx)
            note = DISCOVERY_NOTIFICATIONS.get(fmt_idx, "New formation discovered!")
            self.add_notification(note, 4.0, (255, 220, 80))
            discovered_any = True
            best_formation = fmt_idx

        if not discovered_any:
            # Subtle hint
            if total >= 3:
                self.add_notification("Units grouped... no resonance detected", 2.0, (120, 120, 140))
            return

        # Auto-create squad from these units with the discovered formation
        # Only use free units
        free_units = [u for u in units if self.player_squad_mgr.is_free(u)]
        if len(free_units) >= FORMATION_MIN_VIABLE:
            sq = self.player_squad_mgr.create_squad(free_units, formation=best_formation)
            if sq:
                self.add_notification(f"Squad formed! ({len(free_units)} units)", 3.0, (100, 255, 100))

    def start_placement(self, building_type):
        d = BUILDING_DEFS[building_type]
        if self.resources.can_afford(gold=d["gold"], wood=d["wood"], iron=d.get("iron", 0),
                                     steel=d.get("steel", 0), stone=d.get("stone", 0)):
            self.placing_building = building_type

    def _can_place_building(self, btype, col, row):
        d = BUILDING_DEFS[btype]
        size = d["size"]
        if not self.resources.can_afford(gold=d["gold"], wood=d["wood"], iron=d.get("iron", 0),
                                         steel=d.get("steel", 0), stone=d.get("stone", 0)):
            return False
        for dr in range(size):
            for dc in range(size):
                tc, tr = col + dc, row + dr
                if not self.game_map.is_buildable(tc, tr):
                    return False
                # check overlap with other buildings (including ruins)
                for b in self.player_buildings:
                    if not b.alive:
                        continue
                    for bc, br in b.get_tiles():
                        if tc == bc and tr == br:
                            return False
        return True

    def _place_building(self, btype, col, row):
        d = BUILDING_DEFS[btype]
        self.resources.spend(gold=d["gold"], wood=d["wood"], iron=d.get("iron", 0),
                             steel=d.get("steel", 0), stone=d.get("stone", 0))
        b = Building(col, row, btype, "player")
        self.player_buildings.append(b)
        self.placing_building = None
        self.add_cmd_effect(b.x + TILE_SIZE, b.y + TILE_SIZE, CMD_RING_COLOR_BUILD)
        self.add_message(f"{display_name(btype)} placed", MSG_COL_COMMAND)
        self.logger.log(
            self.game_time, "BUILDING_PLACED",
            self.enemy_ai.wave_number,
            btype, f"{d['gold']}g {d['wood']}w")

        # assign a selected worker to build
        workers = [u for u in self.selected if isinstance(u, Unit) and u.unit_type == "worker"]
        if workers:
            workers[0].command_build(b, self)

    def get_blocked_tiles(self):
        """Return set of tiles occupied by alive buildings (both player and enemy)."""
        blocked = set()
        for b in self.player_buildings + getattr(self, 'enemy_buildings', []):
            if not b.alive:
                continue
            for tile in b.get_tiles():
                blocked.add(tile)
        return blocked

    def _find_building_at(self, wx, wy):
        """Return the first alive player building at world coordinates, or None."""
        for b in self.player_buildings:
            if not b.alive:
                continue
            bx1 = b.col * TILE_SIZE
            by1 = b.row * TILE_SIZE
            bx2 = bx1 + b.size * TILE_SIZE
            by2 = by1 + b.size * TILE_SIZE
            if bx1 <= wx <= bx2 and by1 <= wy <= by2:
                return b
        return None

    def get_nearest_town_hall(self, x, y):
        best = None
        best_d = 1e9
        for b in self.player_buildings:
            if b.alive and b.built and b.building_type == "town_hall":
                d = dist(x, y, b.x, b.y)
                if d < best_d:
                    best_d = d
                    best = b
        return best

    def get_nearest_dropoff(self, x, y, resource_type):
        """Return nearest valid drop-off for a resource type.

        Valid targets: any Town Hall, or a matching helper building
        (via DROPOFF_BUILDING_TYPES), or a matching production building
        (via PRODUCTION_RATES).
        """
        best = None
        best_d = 1e9
        for b in self.player_buildings:
            if not b.alive or not b.built or b.ruined:
                continue
            valid = False
            if b.building_type == "town_hall":
                valid = True
            elif b.building_type in DROPOFF_BUILDING_TYPES:
                if DROPOFF_BUILDING_TYPES[b.building_type] == resource_type:
                    valid = True
            elif b.building_type in PRODUCTION_RATES:
                if PRODUCTION_RATES[b.building_type]["resource"] == resource_type:
                    valid = True
            if valid:
                d = dist(x, y, b.x, b.y)
                if d < best_d:
                    best_d = d
                    best = b
        return best

    def start_upgrade(self, building):
        """v10.2: Start upgrading a helper building to a production building."""
        if not building.can_upgrade() or not building._can_upgrade_at(self):
            return False
        new_type = UPGRADE_PATH[building.building_type]
        new_def = BUILDING_DEFS[new_type]
        # check cost
        if not self.resources.can_afford(
                gold=new_def["gold"], wood=new_def.get("wood", 0),
                iron=new_def.get("iron", 0), steel=new_def.get("steel", 0),
                stone=new_def.get("stone", 0)):
            return False
        self.resources.spend(
            gold=new_def["gold"], wood=new_def.get("wood", 0),
            iron=new_def.get("iron", 0), steel=new_def.get("steel", 0),
            stone=new_def.get("stone", 0))
        building.upgrading_to = new_type
        building.upgrade_progress = 0.0
        building.upgrade_time = new_def["build_time"]
        # auto-assign nearest idle worker
        best_w = None
        best_d = 1e9
        for u in self.player_units:
            if (u.alive and u.unit_type == "worker" and u.state == "idle"):
                d = dist(u.x, u.y, building.x, building.y)
                if d < best_d:
                    best_d = d
                    best_w = u
        if best_w:
            best_w.command_build(building, self)
        self.add_notification(
            f"Upgrading to {BUILDING_LABELS.get(new_type, new_type)}",
            2.0, (100, 255, 100))
        return True

    def unstation_workers(self, building):
        """v10.2: Unstation all workers from a production building."""
        for w in list(building.stationed_workers):
            w.command_unstation(self)

    # ------------------------------------------------------------------
    # v10_2: Global commands (no-selection buttons)
    # ------------------------------------------------------------------
    def global_defend(self):
        """All combat units move to base and hold ground."""
        th = self.get_nearest_town_hall(MAP_COLS * TILE_SIZE / 2, MAP_ROWS * TILE_SIZE / 2)
        if not th:
            return
        # find nearest tower to TH for defense midpoint
        towers = [b for b in self.player_buildings
                  if b.alive and b.built and b.building_type == "tower"]
        if towers:
            nearest_tower = min(towers, key=lambda t: dist(th.x, th.y, t.x, t.y))
            def_x = (th.x + nearest_tower.x) / 2
            def_y = (th.y + nearest_tower.y) / 2
        else:
            def_x, def_y = th.x, th.y
        # v10_beta: formation-move squads to defense point
        seen_squads = set()
        for u in self.player_units:
            if u.unit_type in ("soldier", "archer") and u.state != "garrisoned":
                sq = self.player_squad_mgr.get_squad(u)
                if sq and sq.squad_id not in seen_squads:
                    seen_squads.add(sq.squad_id)
                    self.player_squad_mgr.formation_move(sq, def_x, def_y, self)
                    sq.stance = STANCE_GUARD
                    for m in sq.members:
                        if m.alive:
                            m.command_set_stance(STANCE_GUARD)
                    self.player_squad_mgr.set_guard_position(u, def_x, def_y)
                elif not sq:
                    u.command_move(def_x, def_y, self)
                    u.command_set_stance(STANCE_GUARD)

    def global_attack(self):
        """v10_beta: All combat units hunt down enemies (spatial grid, not O(n²))."""
        for u in self.player_units:
            if u.unit_type not in ("soldier", "archer") or u.state == "garrisoned":
                continue
            # find nearest enemy via spatial grid expanding search
            nearby = self.enemy_grid.query_radius(u.x, u.y, 400)
            if not nearby:
                nearby = [e for e in self.enemy_units if e.alive]
            best = None
            best_d = 1e9
            for e in nearby:
                if not e.alive:
                    continue
                d = dist(u.x, u.y, e.x, e.y)
                if d < best_d:
                    best_d = d
                    best = e
            if best:
                u.command_attack(best, self)
            else:
                # no enemies visible — attack-move to map center
                cx = MAP_COLS * TILE_SIZE / 2
                cy = MAP_ROWS * TILE_SIZE / 2
                u.command_attack_move(cx, cy, self)

    def global_bell(self):
        """Town Bell — recall all workers into garrison (costs resources)."""
        gc = GARRISON_COST
        if not self.resources.can_afford(wood=gc["wood"], iron=gc["iron"], stone=gc["stone"]):
            return
        self.resources.spend(wood=gc["wood"], iron=gc["iron"], stone=gc["stone"])
        for u in self.player_units:
            if u.unit_type == "worker" and u.state not in ("garrisoned", "stationed"):
                th = self.get_nearest_town_hall(u.x, u.y)
                if th:
                    u.command_garrison(th, self)

    def start_tower_upgrade(self, b):
        """Upgrade tower to explosive cannon — shared by hotkey U and GUI button."""
        if not b.can_upgrade_tower():
            return
        cost = TOWER_UPGRADE_COST
        if self.resources.can_afford(steel=cost["steel"]):
            self.resources.spend(steel=cost["steel"])
            best_worker = None
            best_d = float("inf")
            for u in self.player_units:
                if u.alive and u.unit_type == "worker" and u.state == "idle":
                    wd = dist(u.x, u.y, b.x, b.y)
                    if wd < best_d:
                        best_d = wd
                        best_worker = u
            if best_worker:
                best_worker.command_tower_upgrade(b, self)
                self.add_notification("Upgrading tower to Explosive Cannon (15 steel)", 2.0, (255, 140, 40))
            else:
                self.resources.steel += cost["steel"]
                self.add_notification("No idle workers available for upgrade!", 2.0, (255, 80, 80))

    def _update_resonance(self):
        """v10_8: Compute resonance fields and stamp per-unit attributes."""
        cache = self.player_squad_mgr.compute_resonance_cache()

        # Clear per-frame resonance attributes on all player units
        for u in self.player_units:
            if not u.alive:
                continue
            u._spiral_miss_chance = 0.0
            u._sierpinski_aoe_factor = 1.0
            u._dissonance_nullified = False
            u._resonance_visual = -1

        # Clear Koch slow on all enemies (1.0 = no slow)
        for e in self.enemy_units:
            if e.alive:
                e._koch_slow_factor = 1.0

        # Stamp resonance attributes per squad
        for squad in self.player_squad_mgr.squad_list:
            if squad.alive_count == 0:
                continue
            res = cache.get(squad.squad_id)
            if not res:
                continue
            fmt, value = res[0], res[1]

            if fmt == FORMATION_POLAR_ROSE:
                # Rose: damage bonus applied at attack time, just stamp visual
                for m in squad.members:
                    if m.alive:
                        m._resonance_visual = 0
            elif fmt == FORMATION_GOLDEN_SPIRAL:
                for m in squad.members:
                    if m.alive:
                        m._spiral_miss_chance = value
                        m._resonance_visual = 1
            elif fmt == FORMATION_SIERPINSKI:
                for m in squad.members:
                    if m.alive:
                        m._sierpinski_aoe_factor = value
                        m._resonance_visual = 2
            elif fmt == FORMATION_KOCH:
                # Stamp visual on members
                for m in squad.members:
                    if m.alive:
                        m._resonance_visual = 3
                # Slow enemies within Koch radius
                if squad.leader and squad.leader.alive:
                    kr = FORMATION_KOCH_RADIUS * RESONANCE_KOCH_RADIUS_MULT
                    for e in self.enemy_grid.query_radius(
                            squad.leader.x, squad.leader.y, kr):
                        if e.alive:
                            e._koch_slow_factor = min(e._koch_slow_factor, value)

        # Dissonance pass: nullify resonance near dissonant enemies
        for e in self.enemy_units:
            if not e.alive or e.dissonant_formation < 0:
                continue
            anti_fmt = e.dissonant_formation
            for u in self.player_grid.query_radius(
                    e.x, e.y, RESONANCE_DISSONANCE_RADIUS):
                if u.alive and u._resonance_visual == anti_fmt:
                    u._dissonance_nullified = True
                    u._spiral_miss_chance = 0.0
                    u._sierpinski_aoe_factor = 1.0

    def command_gather_nearest_selected(self, resource_type=None):
        """v10_8c: Send selected workers to mine nearest resource (optionally specific type)."""
        workers = [u for u in self.selected if isinstance(u, Unit) and u.unit_type == "worker"]
        count = 0
        for w in workers:
            w.command_gather_nearest(self, resource_type)
            if w.state == "moving":
                count += 1
        rname = resource_type.title() if resource_type else "resource"
        if count:
            self.add_notification(f"{count} worker(s) → nearest {rname}", 1.5, (200, 180, 80))
        elif workers:
            self.add_notification(f"No {rname} found", 1.5, (200, 80, 80))

    def global_resume(self):
        """Ungarrison all workers and resume previous work."""
        for b in self.player_buildings:
            if b.building_type == "town_hall" and b.garrison:
                for w in list(b.garrison):
                    w.command_ungarrison(self)
                    # try to resume gathering
                    rtype = w._last_gather_type
                    if rtype:
                        w._auto_resume_gather(rtype, self)

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        # v10_beta: WASD always pans camera (no suppression)
        self.camera.update(keys, dt, mx, my)

        self.enemy_ai.update(dt, self)

        # v10_4: rebuild spatial grids once per frame (O(n))
        self.player_grid.rebuild(self.player_units)
        self.enemy_grid.rebuild(self.enemy_units)

        # track whether enemies exist before updates
        had_enemies = len(self.enemy_units) > 0

        for u in self.player_units:
            u.update(dt, self)
        for u in self.enemy_units:
            u.update(dt, self)
        for b in self.player_buildings:
            b.update(dt, self)

        # v9: update ballistic arrows (v10_4: single-pass partition)
        still_flying = []
        for a in self.arrows:
            a.update(dt, self)
            if not a.alive:
                continue
            if a.grounded:
                self.ground_arrows.append(a)
            else:
                still_flying.append(a)
        self.arrows = still_flying
        # cull expired ground arrows + cap at max
        if len(self.ground_arrows) > GROUND_ARROW_MAX:
            self.ground_arrows = [a for a in self.ground_arrows[-GROUND_ARROW_MAX:] if a.alive]

        # v10c: update cannonballs and explosions
        for c in self.cannonballs:
            c.update(dt, self)
        self.cannonballs = [c for c in self.cannonballs if c.alive]
        for ex in self.explosions:
            ex.update(dt)
        self.explosions = [ex for ex in self.explosions if ex.alive]
        # v10_5: update craters (fading ground scars)
        for cr in self.craters:
            cr.update(dt)
        self.craters = [cr for cr in self.craters if cr.alive]
        # v10_5: update camera shake
        self.camera.update_shake(dt)

        # v10_delta: squad maintenance (player-driven, no auto-grouping)
        dissolution_msgs = self.player_squad_mgr.update(dt, self.player_units)
        for msg in dissolution_msgs:
            self.add_notification(msg, 3.0, (255, 180, 40))
        self.enemy_squad_mgr.update(dt, self.enemy_units)

        # v10_delta: check pending group arrivals for formation discovery
        self._update_pending_groups(dt)

        # v10_8: update resonance fields
        self._update_resonance()

        # v10_epsilon: update formation rotation, sweep damage, and abilities
        for squad in self.player_squad_mgr.squad_list:
            squad.update_rotation(dt, self)
            squad.update_ability(dt, self)

        # v10_beta: passive healing near town hall (spatial grid per TH instead of n×m)
        town_halls = [b for b in self.player_buildings
                      if b.alive and b.built and not b.ruined
                      and b.building_type == "town_hall"]
        for th in town_halls:
            for u in self.player_grid.query_radius(th.x, th.y, HEAL_RADIUS_TH):
                if u.alive and u.hp < u.max_hp:
                    u.hp = min(u.max_hp, u.hp + HEAL_RATE_NEAR_TH * dt)

        # v10_1: record combat heat for dead units (minimap overlay)
        for u in self.enemy_units:
            if not u.alive:
                self._combat_heat.append([u.x, u.y, COMBAT_HEAT_DURATION])  # 30 sec decay
        for u in self.player_units:
            if not u.alive and u.unit_type != "worker":
                self._combat_heat.append([u.x, u.y, COMBAT_HEAT_DURATION])
        # decay heat
        self._combat_heat = [[x, y, t - dt] for x, y, t in self._combat_heat if t - dt > 0]

        # v10_9: count player losses for incident outcome classification
        dead_player_units = sum(1 for u in self.player_units if not u.alive and u.unit_type != "worker")
        dead_player_buildings = sum(1 for b in self.player_buildings if not b.alive)
        self.enemy_ai.units_lost_this_incident += dead_player_units
        self.enemy_ai.buildings_lost_this_incident += dead_player_buildings

        # remove dead
        self.player_units = [u for u in self.player_units if u.alive]
        self.enemy_units = [u for u in self.enemy_units if u.alive]
        self.player_buildings = [b for b in self.player_buildings if b.alive]
        self.selected = [e for e in self.selected if e.alive]
        # v10_2: clear inspected enemy if dead
        if self.inspected_enemy and not self.inspected_enemy.alive:
            self.inspected_enemy = None

        # v10_9: wave/incident cleared is now handled internally by EnemyAI FSM
        # (via _resolve_incident → game._on_attack_resolved callback)

        # v10_8d: update progressive unlocks (every ~0.5s)
        if int(self.game_time * 2) != int((self.game_time - dt) * 2):
            self._update_unlocks()

        # update notifications (filter uses timer - dt so no negative timers survive)
        self._notifications = [[t, timer - dt, c]
                                for t, timer, c in self._notifications if timer - dt > 0]

        # update command confirmation effects
        self._cmd_effects = [[wx, wy, t - dt, col]
                              for wx, wy, t, col in self._cmd_effects if t - dt > 0]

        # check game over
        if not self.player_buildings:
            self.game_over = True
            self.logger.log(self.game_time, "GAME_OVER",
                            self.enemy_ai.wave_number, "defeat", self.difficulty)

        if self.enemy_ai.game_won and not self.enemy_units:
            self.game_won = True
            self.logger.log(self.game_time, "GAME_OVER",
                            self.enemy_ai.wave_number, "victory", self.difficulty)

    def _on_attack_resolved(self, incident_number, outcome):
        """v10_9: Called by EnemyAI FSM when an incident is resolved."""
        # Count escaped enemies
        esc = len(self.escaped_enemies)
        if esc > 0:
            self.enemy_ai.incident_enemies_fled = esc
            self.add_notification(
                f"{esc} {'enemy' if esc == 1 else 'enemies'} escaped — they will return stronger!",
                3.5, (255, 140, 80))

        # Clear projectiles between incidents for visual cleanliness
        self.ground_arrows.clear()
        self.cannonballs.clear()
        self.craters.clear()

    def _update_unlocks(self):
        """v10_8d: Update progressive UI unlock state from current game state."""
        u = self.unlocks
        # buildings
        for b in self.player_buildings:
            if b.built and not b.ruined:
                if b.building_type == "barracks":
                    u["has_barracks"] = True
                elif b.building_type == "refinery":
                    u["has_refinery"] = True
                elif b.building_type == "tower":
                    u["has_tower"] = True
        # resources
        if self.resources.iron > 0:
            u["has_iron"] = True
        if self.resources.stone > 0:
            u["has_stone"] = True
        if self.resources.steel > 0:
            u["has_steel"] = True
        # squads
        squads = self.player_squad_mgr.squad_list
        if any(s.alive_count > 0 for s in squads):
            u["has_squad"] = True
        # max rank
        for unit in self.player_units:
            if unit.alive and unit.rank > u["max_rank_seen"]:
                u["max_rank_seen"] = unit.rank
        # incident (was wave)
        if self.enemy_ai.incident_number >= 1:
            u["first_wave_cleared"] = True
        # v10_alpha: formation discovery
        self._check_formation_discovery()

    def _check_formation_discovery(self):
        """v10_alpha: Check if any squad's composition discovers a new formation."""
        from squads import get_squad_composition
        for squad in self.player_squad_mgr.squad_list:
            if squad.alive_count == 0:
                continue
            # Count veterans
            veterans = sum(1 for m in squad.members if m.alive and m.rank >= 1)
            soldiers, archers = get_squad_composition(squad)
            total = soldiers + archers

            for fmt_idx, req in FORMATION_DISCOVERY.items():
                if fmt_idx in self.discovered_formations:
                    continue  # already discovered
                if total < req["min_size"]:
                    continue
                if veterans < req["min_veterans"]:
                    continue

                # Check ratio
                if req.get("any_ratio"):
                    # Rose: any composition works
                    pass
                else:
                    majority = max(soldiers, archers)
                    minority = min(soldiers, archers)
                    if minority == 0:
                        continue  # monotone can't discover non-Rose
                    actual_ratio = majority / minority
                    ideal = HARMONY_IDEAL_RATIOS[fmt_idx]
                    deviation = abs(actual_ratio - ideal) / max(ideal, 0.01)
                    if deviation >= DISCOVERY_RATIO_TOLERANCE:
                        continue  # ratio too far from ideal

                # Discovery!
                self.discovered_formations.add(fmt_idx)
                msg = DISCOVERY_NOTIFICATIONS.get(fmt_idx, "Formation Discovered!")
                self.add_notification(msg, 4.0, (255, 230, 80))
                self.logger.log(self.game_time, "FORMATION_DISCOVERED",
                                detail_1=FORMATION_NAMES[fmt_idx],
                                detail_2=f"{soldiers}S:{archers}A",
                                detail_3=f"squad:{squad.squad_id}")
                # Auto-switch discovering squad to this formation
                squad.formation = fmt_idx

    def render(self):
        self.screen.fill(COL_BG)

        # clip game area
        clip_rect = pygame.Rect(0, GAME_AREA_Y, SCREEN_WIDTH, GAME_AREA_H)
        self.screen.set_clip(clip_rect)

        self._render_map()
        self._render_ground_arrows()   # v9: stuck arrows on ground (below units)
        self._render_craters()         # v10_5: cannonball impact craters
        self._render_buildings()
        self._render_koch_rings()  # v10_8: Koch slow territory rings
        self._render_units()
        self._render_arrows()          # v9: flying arrows (above units)
        self._render_cannonballs()     # v10c: tower cannonballs + explosions
        self._render_placement_ghost()
        self._render_rally_points()     # v10_1: rally point flags
        self._render_select_rect()
        self._render_enemy_inspect()    # v10_2: red ring on inspected enemy
        self._render_cmd_effects()      # command confirmation rings

        self.screen.set_clip(None)

        # GUI
        self.gui.draw_top_bar(self.screen, self.resources, self.enemy_ai, self.player_units)
        self.gui.draw_bottom_panel(self.screen, self.selected, self,
                                   inspected_enemy=self.inspected_enemy)

        # minimap
        self._render_minimap()

        # v10_alpha: Register map entity tooltips for hovered units/buildings
        mx, my = pygame.mouse.get_pos()
        if TOP_BAR_H < my < SCREEN_HEIGHT - BOTTOM_PANEL_H:
            self._register_entity_tooltip(mx, my)

        # v10_2: attack-move cursor indicator
        if self.attack_move_mode:
            draw_text(self.screen, "ATTACK MOVE", mx + 12, my - 12, self.font_sm, (255, 80, 80))

        # notifications
        self._render_notifications()

        # message log panel
        if self.show_message_log:
            self._render_message_log()
        elif self._message_log:
            # subtle hint that log exists with unread count
            n = len(self._message_log)
            draw_text(self.screen, f"[L] Log ({n})", 10,
                      SCREEN_HEIGHT - BOTTOM_PANEL_H - 18, self.font_xs, (70, 70, 90))

        # v10_alpha: Draw tooltip overlay (last, on top of everything)
        self.gui.draw_tooltip(self.screen)

        # v10_8d: pause menu overlay
        if self.paused:
            self._draw_pause_menu()

        # game over / win overlay
        if self.game_over:
            label = "SURRENDERED" if self.game_surrendered else "DEFEAT"
            self._draw_overlay(label, (200, 50, 50))
        elif self.game_won:
            label = self.difficulty_profile.get("label", "Medium")
            self._draw_overlay(f"VICTORY! ({label})", (50, 200, 50))

        pygame.display.flip()

    def _render_notifications(self):
        """Draw floating notification messages."""
        y = GAME_AREA_Y + 50
        for text, timer, color in self._notifications:
            fade_color = tuple(max(0, min(255, int(c * max(0.0, min(1.0, timer))))) for c in color)
            draw_text(self.screen, text, SCREEN_WIDTH // 2, y, self.font_notif,
                      fade_color, center=True)
            y += 28

    def _render_cmd_effects(self):
        """Draw expanding ring confirmations at command target positions."""
        z = self.camera.zoom
        for wx, wy, timer, rgba in self._cmd_effects:
            sx, sy = self.camera.world_to_screen(wx, wy)
            progress = 1.0 - timer / CMD_RING_DURATION  # 0 -> 1
            radius = max(2, int((4 + CMD_RING_MAX_RADIUS * progress) * z))
            alpha = max(0, min(255, int(rgba[3] * timer / CMD_RING_DURATION)))
            color = (rgba[0], rgba[1], rgba[2])
            # outer ring
            thickness = max(1, int(2 * z * (1.0 - progress * 0.5)))
            ring_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*color, alpha),
                               (radius + 2, radius + 2), radius, thickness)
            # small cross at center (only early in animation)
            if progress < 0.4:
                cross_a = max(0, int(alpha * (1.0 - progress / 0.4)))
                cr = max(2, int(4 * z))
                cx, cy = radius + 2, radius + 2
                pygame.draw.line(ring_surf, (*color, cross_a),
                                 (cx - cr, cy), (cx + cr, cy), max(1, int(z)))
                pygame.draw.line(ring_surf, (*color, cross_a),
                                 (cx, cy - cr), (cx, cy + cr), max(1, int(z)))
            self.screen.blit(ring_surf, (sx - radius - 2, sy - radius - 2))

    def _render_message_log(self):
        """Draw the collapsible message log panel on the left side."""
        line_h = 18
        pad = 6
        log_w = 340
        n_lines = min(MSG_LOG_VISIBLE, len(self._message_log))
        if n_lines == 0:
            # draw empty hint
            log_h = line_h + pad * 2
            log_x = 8
            log_y = SCREEN_HEIGHT - BOTTOM_PANEL_H - log_h - 4
            bg = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
            bg.fill((20, 20, 30, 180))
            self.screen.blit(bg, (log_x, log_y))
            pygame.draw.rect(self.screen, COL_GUI_BORDER, (log_x, log_y, log_w, log_h), 1)
            draw_text(self.screen, "-- No messages --", log_x + pad, log_y + pad,
                      self.font_xs, (100, 100, 120))
            return

        log_h = n_lines * line_h + pad * 2
        log_x = 8
        log_y = SCREEN_HEIGHT - BOTTOM_PANEL_H - log_h - 4

        # semi-transparent background
        bg = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
        bg.fill((20, 20, 30, 180))
        self.screen.blit(bg, (log_x, log_y))
        pygame.draw.rect(self.screen, COL_GUI_BORDER, (log_x, log_y, log_w, log_h), 1)

        # header
        draw_text(self.screen, "[L] Log", log_x + log_w - 52, log_y - 14,
                  self.font_xs, (100, 100, 140))

        # draw recent messages (newest at bottom)
        recent = self._message_log[-n_lines:]
        y = log_y + pad
        for text, msg_time, color in recent:
            age = self.game_time - msg_time
            # fade old messages
            if age > MSG_LOG_FADE:
                fade = max(0.3, 1.0 - (age - MSG_LOG_FADE) / MSG_LOG_FADE)
                faded = tuple(max(0, int(c * fade)) for c in color)
            else:
                faded = color
            # timestamp prefix
            mins = int(msg_time) // 60
            secs = int(msg_time) % 60
            prefix = f"{mins:02d}:{secs:02d}"
            draw_text(self.screen, prefix, log_x + pad, y, self.font_xs, (80, 80, 100))
            # message text — truncate if too long
            max_text_w = log_w - 60
            txt_surf = self.font_xs.render(text, True, faded)
            if txt_surf.get_width() > max_text_w:
                # truncate with ellipsis
                while txt_surf.get_width() > max_text_w - 10 and len(text) > 5:
                    text = text[:-1]
                txt_surf = self.font_xs.render(text + "..", True, faded)
            self.screen.blit(txt_surf, (log_x + pad + 44, y))
            y += line_h

    def _render_map(self):
        vr = self.camera.visible_rect()
        z = self.camera.zoom
        # v10_8c: use exact tile positions to prevent grid drift
        # Each tile's pixel position is computed from its world coord, not accumulated ts
        tsf = TILE_SIZE * z  # exact floating-point tile size
        ts = max(1, int(tsf) + 1)  # padded for fill (no gaps between tiles)
        c_min = max(0, int(vr.x // TILE_SIZE))
        r_min = max(0, int(vr.y // TILE_SIZE))
        c_max = min(MAP_COLS, int((vr.x + vr.width) // TILE_SIZE) + 1)
        r_max = min(MAP_ROWS, int((vr.y + vr.height) // TILE_SIZE) + 1)

        # v10_4: cache map surface — only rebuild on zoom change, large pan, or tile change
        cache_valid = (
            self._map_cache is not None
            and not self._map_dirty
            and self._map_cache_zoom == z
            and self._map_cache_rect is not None
            and self._map_cache_rect[0] == c_min
            and self._map_cache_rect[1] == r_min
            and self._map_cache_rect[2] == c_max
            and self._map_cache_rect[3] == r_max
        )

        if not cache_valid:
            # v10_8c: cache size from exact tile positions (not ts accumulation)
            w = int((c_max - c_min) * tsf) + ts
            h = int((r_max - r_min) * tsf) + ts
            cache = pygame.Surface((max(1, w), max(1, h)))
            cache.fill((40, 118, 74))  # grass base

            for r in range(r_min, r_max):
                for c in range(c_min, c_max):
                    t = self.game_map.tiles[r][c]
                    # v10_8c: exact position from world coords
                    lx = int((c - c_min) * tsf)
                    ly = int((r - r_min) * tsf)
                    if t != TERRAIN_GRASS:
                        color = TERRAIN_COLORS.get(t, (40, 118, 74))
                        pygame.draw.rect(cache, color, (lx, ly, ts, ts))

                    # decorations
                    if t == TERRAIN_TREE:
                        cx = lx + int(tsf * 0.5)
                        cy = ly + int(tsf * 0.5)
                        r1 = max(2, int(10 * z))
                        r2 = max(2, int(8 * z))
                        pygame.draw.circle(cache, (0, 60, 0), (cx, cy - int(4 * z)), r1)
                        pygame.draw.circle(cache, (10, 80, 10), (cx, cy - int(4 * z)), r2)
                    elif t == TERRAIN_GOLD:
                        cx = lx + int(tsf * 0.5)
                        cy = ly + int(tsf * 0.5)
                        pygame.draw.circle(cache, (255, 230, 80), (cx, cy), max(2, int(6 * z)))
                    elif t == TERRAIN_IRON:
                        cx = lx + int(tsf * 0.5)
                        cy = ly + int(tsf * 0.5)
                        s = int(7 * z)
                        s2 = int(6 * z)
                        s3 = int(5 * z)
                        pts = [(cx, cy - s), (cx - s2, cy + s3), (cx + s2, cy + s3)]
                        pygame.draw.polygon(cache, (180, 180, 195), pts)
                    elif t == TERRAIN_STONE:
                        cx = lx + int(tsf * 0.5)
                        cy = ly + int(tsf * 0.5)
                        s = int(6 * z)
                        pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
                        pygame.draw.polygon(cache, (185, 175, 155), pts)

            # grid lines (only at zoom >= 0.7)
            if z >= 0.7:
                grid_col = (30, 90, 56)
                for r in range(r_max - r_min + 1):
                    y = int(r * tsf)
                    pygame.draw.line(cache, grid_col, (0, y), (w, y))
                for c in range(c_max - c_min + 1):
                    x = int(c * tsf)
                    pygame.draw.line(cache, grid_col, (x, 0), (x, h))

            self._map_cache = cache
            self._map_cache_zoom = z
            self._map_cache_rect = (c_min, r_min, c_max, r_max)
            self._map_dirty = False

        # blit cached surface
        sx, sy = self.camera.world_to_screen(c_min * TILE_SIZE, r_min * TILE_SIZE)
        self.screen.blit(self._map_cache, (sx, sy))

    def _render_buildings(self):
        for b in self.player_buildings:
            b.draw(self.screen, self.camera)

    def _render_koch_rings(self):
        """v10_8: Draw Koch slow territory rings around Koch-formation squads."""
        cache = getattr(self.player_squad_mgr, '_resonance_cache', {})
        z = self.camera.zoom
        ticks = pygame.time.get_ticks()
        alpha = 25 + int(20 * abs(math.sin(ticks * 0.002)))
        for sid, entry in cache.items():
            ftype, val = entry[0], entry[1]
            if ftype != 3:  # Koch = formation index 3
                continue
            sq = next((s for s in self.player_squad_mgr.squad_list if s.squad_id == sid), None)
            if not sq or not sq.leader or not sq.leader.alive:
                continue
            radius = FORMATION_KOCH_RADIUS * RESONANCE_KOCH_RADIUS_MULT * z
            sx, sy = self.camera.world_to_screen(sq.leader.x, sq.leader.y)
            ring_r = int(radius)
            if ring_r < 4:
                continue
            ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (50, 200, 80, alpha),
                               (ring_r + 2, ring_r + 2), ring_r, 2)
            self.screen.blit(ring_surf, (sx - ring_r - 2, sy - ring_r - 2))

    def _render_units(self):
        # v10_4: maintain sorted list with insertion sort (O(n) on nearly-sorted data)
        units = self._sorted_units
        units.clear()
        for u in self.player_units:
            if u.alive:
                units.append(u)
        for u in self.enemy_units:
            if u.alive:
                units.append(u)
        # insertion sort — fast when units barely change Y order frame-to-frame
        for i in range(1, len(units)):
            key_u = units[i]
            key_y = key_u.y
            j = i - 1
            while j >= 0 and units[j].y > key_y:
                units[j + 1] = units[j]
                j -= 1
            units[j + 1] = key_u
        for u in units:
            if u.state in ("garrisoned", "stationed"):
                continue  # v10_2: hidden inside building
            u.draw(self.screen, self.camera)

    def _render_ground_arrows(self):
        """Draw grounded arrows (stuck in terrain, below units)."""
        for a in self.ground_arrows:
            a.draw(self.screen, self.camera)

    def _render_arrows(self):
        """Draw flying arrows (above units)."""
        for a in self.arrows:
            a.draw(self.screen, self.camera)

    def _render_cannonballs(self):
        """v10c: Draw tower cannonballs and explosion VFX."""
        for c in self.cannonballs:
            c.draw(self.screen, self.camera)
        for ex in self.explosions:
            ex.draw(self.screen, self.camera)

    def _render_craters(self):
        """v10_5: Draw cannonball impact craters on the ground."""
        for cr in self.craters:
            cr.draw(self.screen, self.camera)

    def _render_placement_ghost(self):
        if not self.placing_building:
            return
        mx, my = pygame.mouse.get_pos()
        if my < GAME_AREA_Y or my >= GAME_AREA_Y + GAME_AREA_H:
            return
        wx, wy = self.camera.screen_to_world(mx, my)
        col, row = pos_to_tile(wx, wy)
        d = BUILDING_DEFS[self.placing_building]
        size = d["size"]
        sx, sy = self.camera.world_to_screen(col * TILE_SIZE, row * TILE_SIZE)
        z = self.camera.zoom
        px_size = int(size * TILE_SIZE * z)

        valid = self._can_place_building(self.placing_building, col, row)

        ghost = pygame.Surface((px_size, px_size), pygame.SRCALPHA)
        if valid:
            ghost.fill((0, 200, 0, 80))
        else:
            ghost.fill((200, 0, 0, 80))
        self.screen.blit(ghost, (sx, sy))

        label = BUILDING_LABELS.get(self.placing_building, "??")
        draw_text(self.screen, label, sx + px_size // 2, sy + px_size // 2, self.font, (255, 255, 255), center=True)

        # cost tooltip above ghost
        cost = GUI.building_cost_str(self.placing_building)
        name = display_name(self.placing_building)
        draw_text(self.screen, f"{name} - {cost}", sx + px_size // 2, sy - 14, self.font_sm, (255, 255, 200), center=True)

    def _render_rally_points(self):
        """v10_1: Draw rally point flags for selected buildings."""
        for b in self.player_buildings:
            if b.alive and b.built and b.rally_point and b.selected:
                sx, sy = self.camera.world_to_screen(b.rally_point[0], b.rally_point[1])
                z = self.camera.zoom
                # flag pole
                pole_h = max(8, int(18 * z))
                pygame.draw.line(self.screen, RALLY_POINT_COLOR, (sx, sy), (sx, sy - pole_h), max(1, int(2 * z)))
                # flag triangle
                flag_w = max(4, int(8 * z))
                flag_h = max(3, int(6 * z))
                pts = [(sx, sy - pole_h), (sx + flag_w, sy - pole_h + flag_h // 2), (sx, sy - pole_h + flag_h)]
                pygame.draw.polygon(self.screen, RALLY_POINT_COLOR, pts)
                # connecting line from building
                bsx, bsy = self.camera.world_to_screen(b.x, b.y)
                pygame.draw.line(self.screen, (60, 200, 60), (bsx, bsy), (sx, sy), 1)

    def _render_select_rect(self):
        if not self.selecting or not self.select_start:
            return
        mx, my = pygame.mouse.get_pos()
        x1, y1 = self.select_start
        w = mx - x1
        h = my - y1
        if abs(w) < 1 or abs(h) < 1:
            return
        rect_surf = pygame.Surface((abs(w), abs(h)), pygame.SRCALPHA)
        rect_surf.fill((0, 255, 0, 30))
        rx = min(x1, mx)
        ry = min(y1, my)
        self.screen.blit(rect_surf, (rx, ry))
        pygame.draw.rect(self.screen, COL_SELECT, (rx, ry, abs(w), abs(h)), 1)

    def _render_enemy_inspect(self):
        """v10_2: Draw red selection ring around inspected enemy."""
        if not self.inspected_enemy or not self.inspected_enemy.alive:
            return
        e = self.inspected_enemy
        sx, sy = self.camera.world_to_screen(e.x, e.y)
        z = self.camera.zoom
        from constants import UNIT_RADIUS
        r = max(2, int(UNIT_RADIUS.get(e.unit_type, 12) * z))
        pygame.draw.circle(self.screen, (255, 60, 60), (sx, sy), r + max(1, int(3 * z)), 2)

    def _build_minimap_base(self):
        """Build the static terrain layer of the minimap."""
        scale = MINIMAP_SIZE / max(MAP_COLS, MAP_ROWS)
        surf = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        surf.fill((20, 20, 20))
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                t = self.game_map.tiles[r][c]
                color = TERRAIN_COLORS.get(t, (40, 118, 74))
                px = int(c * scale)
                py = int(r * scale)
                pw = max(1, int(scale) + 1)
                ph = max(1, int(scale) + 1)
                pygame.draw.rect(surf, color, (px, py, pw, ph))
        return surf

    def _register_entity_tooltip(self, mx, my):
        """Register tooltip for the entity under the mouse cursor on the map."""
        wx, wy = self.camera.screen_to_world(mx, my)
        best = None
        best_dist = ENTITY_TOOLTIP_RADIUS
        for u in self.player_units:
            if not u.alive:
                continue
            d = dist(wx, wy, u.x, u.y)
            if d < best_dist:
                best_dist = d
                best = u
        for e in self.enemy_units:
            if not e.alive:
                continue
            d = dist(wx, wy, e.x, e.y)
            if d < best_dist:
                best_dist = d
                best = e
        if best is not None:
            key = f"enemy_{best.unit_type}" if best.owner == "enemy" else f"unit_{best.unit_type}"
            self.gui._register_tooltip(pygame.Rect(mx - 10, my - 10, 20, 20), key)
            return
        # Check buildings
        for b in self.player_buildings:
            bx, by = b.x, b.y
            half = b.size * TILE_SIZE / 2
            if abs(wx - bx) < half and abs(wy - by) < half:
                self.gui._register_tooltip(pygame.Rect(mx - 10, my - 10, 20, 20), f"bld_{b.building_type}")
                return

    def _render_minimap(self):
        # v10_4: rebuild base terrain only when tiles change
        if self.minimap_surf is None or self._minimap_dirty:
            self.minimap_surf = self._build_minimap_base()
            self._minimap_dirty = False

        mm = self.minimap_surf.copy()
        scale = MINIMAP_SIZE / max(MAP_COLS, MAP_ROWS)
        tile_scale = scale / TILE_SIZE  # world coords to minimap coords

        # draw player buildings
        for b in self.player_buildings:
            px = int(b.col * scale)
            py = int(b.row * scale)
            ps = max(2, int(b.size * scale))
            color = (50, 50, 80) if b.ruined else (80, 140, 255)
            pygame.draw.rect(mm, color, (px, py, ps, ps))

        # draw player units
        for u in self.player_units:
            if u.state in ("garrisoned", "stationed"):
                continue
            px = int(u.x * tile_scale)
            py = int(u.y * tile_scale)
            pygame.draw.circle(mm, (100, 200, 255), (px, py), 2)

        # draw enemy units
        for u in self.enemy_units:
            px = int(u.x * tile_scale)
            py = int(u.y * tile_scale)
            pygame.draw.circle(mm, (255, 80, 80), (px, py), 2)

        # v10_1: combat heat overlay (fading red hotspots where kills occurred)
        if self._combat_heat:
            heat_surf = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE), pygame.SRCALPHA)
            for hx, hy, ht in self._combat_heat:
                px = int(hx * tile_scale)
                py = int(hy * tile_scale)
                intensity = min(1.0, ht / 15.0)  # fades over 15 sec
                alpha = int(80 * intensity)
                r_heat = max(2, int(6 * intensity))
                pygame.draw.circle(heat_surf, (255, 40, 40, alpha), (px, py), r_heat)
            mm.blit(heat_surf, (0, 0))

        # v10_1: rally point flags on minimap
        for b in self.player_buildings:
            if b.alive and b.built and b.rally_point:
                rpx = int(b.rally_point[0] * tile_scale)
                rpy = int(b.rally_point[1] * tile_scale)
                pygame.draw.circle(mm, RALLY_POINT_COLOR, (rpx, rpy), 3, 1)

        # draw camera viewport rectangle
        vr = self.camera.visible_rect()
        vx = int(vr.x * tile_scale)
        vy = int(vr.y * tile_scale)
        vw = max(4, int(vr.width * tile_scale))
        vh = max(4, int(vr.height * tile_scale))
        pygame.draw.rect(mm, (255, 255, 255), (vx, vy, vw, vh), 1)

        # draw border and blit to screen
        pygame.draw.rect(mm, (180, 180, 180), (0, 0, MINIMAP_SIZE, MINIMAP_SIZE), 1)
        self.screen.blit(mm, (MINIMAP_X, MINIMAP_Y))

    def _minimap_rect(self):
        return pygame.Rect(MINIMAP_X, MINIMAP_Y, MINIMAP_SIZE, MINIMAP_SIZE)

    def _minimap_click(self, sx, sy):
        """Jump camera to the clicked position on the minimap."""
        mr = self._minimap_rect()
        if not mr.collidepoint(sx, sy):
            return False
        # convert minimap coords to world coords
        scale = MINIMAP_SIZE / max(MAP_COLS, MAP_ROWS)
        tile_scale = scale / TILE_SIZE
        wx = (sx - MINIMAP_X) / tile_scale
        wy = (sy - MINIMAP_Y) / tile_scale
        z = self.camera.zoom
        self.camera.x = wx - SCREEN_WIDTH / (2 * z)
        self.camera.y = wy - GAME_AREA_H / (2 * z)
        self.camera._clamp()
        return True

    # ------------------------------------------------------------------
    # v10_8d: PAUSE MENU
    # ------------------------------------------------------------------
    _PAUSE_ITEMS = [
        ("Resume", "resume"),
        ("Save Game (coming soon)", "save"),
        ("Load Game (coming soon)", "load"),
        ("Settings (coming soon)", "settings"),
        ("Restart", "restart"),
        ("Quit to Menu", "quit"),
    ]

    def _handle_pause_key(self, key):
        n = len(self._PAUSE_ITEMS)
        if key == pygame.K_UP:
            self.pause_menu_selection = (self.pause_menu_selection - 1) % n
        elif key == pygame.K_DOWN:
            self.pause_menu_selection = (self.pause_menu_selection + 1) % n
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_pause_item(self.pause_menu_selection)
        elif key == pygame.K_ESCAPE:
            self.paused = False

    def _handle_pause_click(self, pos):
        mx, my = pos
        menu_x = SCREEN_WIDTH // 2 - 140
        menu_y_start = SCREEN_HEIGHT // 2 - 80
        for i in range(len(self._PAUSE_ITEMS)):
            item_y = menu_y_start + i * 40
            if menu_x <= mx <= menu_x + 280 and item_y <= my <= item_y + 34:
                self._activate_pause_item(i)
                return

    def _activate_pause_item(self, idx):
        action = self._PAUSE_ITEMS[idx][1]
        if action == "resume":
            self.paused = False
        elif action == "restart":
            self.paused = False
            self.__init__(self.screen, self.difficulty)
        elif action == "quit":
            self.paused = False
            self.running = False
        # save/load/settings: future stubs — no action yet

    def _draw_pause_menu(self):
        import math as _m
        ticks = pygame.time.get_ticks()

        # darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # title with subtle pulse
        pulse = 0.85 + 0.15 * _m.sin(ticks * 0.003)
        title_col = tuple(int(c * pulse) for c in (200, 220, 255))
        draw_text(self.screen, "PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130,
                  self.font_lg, title_col, center=True)

        # menu panel background
        menu_w, menu_h = 280, len(self._PAUSE_ITEMS) * 40 + 10
        menu_x = SCREEN_WIDTH // 2 - menu_w // 2
        menu_y = SCREEN_HEIGHT // 2 - 80
        panel_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        panel_surf.fill((20, 20, 35, 200))
        pygame.draw.rect(panel_surf, (60, 70, 100), (0, 0, menu_w, menu_h), 1, border_radius=6)
        self.screen.blit(panel_surf, (menu_x, menu_y))

        # menu items
        mx, my = pygame.mouse.get_pos()
        for i, (label, action) in enumerate(self._PAUSE_ITEMS):
            item_y = menu_y + 5 + i * 40
            is_selected = (i == self.pause_menu_selection)
            # mouse hover updates selection
            if menu_x <= mx <= menu_x + menu_w and item_y <= my <= item_y + 34:
                self.pause_menu_selection = i
                is_selected = True

            is_stub = action in ("save", "load", "settings")

            # highlight bar
            if is_selected:
                bar_col = (40, 50, 80, 180) if not is_stub else (35, 35, 50, 120)
                bar_surf = pygame.Surface((menu_w - 8, 34), pygame.SRCALPHA)
                bar_surf.fill(bar_col)
                self.screen.blit(bar_surf, (menu_x + 4, item_y))
                # left accent line
                accent = (100, 180, 255) if not is_stub else (60, 60, 80)
                pygame.draw.line(self.screen, accent, (menu_x + 4, item_y + 2),
                                 (menu_x + 4, item_y + 32), 2)

            # text
            if is_stub:
                text_col = (80, 80, 100)
            elif is_selected:
                text_col = (220, 230, 255)
            else:
                text_col = (160, 170, 200)
            draw_text(self.screen, label, menu_x + 16, item_y + 9, self.font, text_col)

        # footer hint
        draw_text(self.screen, "P to resume  |  Arrow keys to navigate  |  Enter to select",
                  SCREEN_WIDTH // 2, menu_y + menu_h + 16, self.font_xs,
                  (80, 90, 120), center=True)

        # game time display
        mins = int(self.game_time) // 60
        secs = int(self.game_time) % 60
        draw_text(self.screen, f"Time: {mins}:{secs:02d}  |  Incident: {self.enemy_ai.incident_number}/{self.enemy_ai.incidents_required}",
                  SCREEN_WIDTH // 2, menu_y + menu_h + 34, self.font_xs,
                  (80, 90, 120), center=True)

    def _draw_overlay(self, text, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, self.font_lg, color, center=True)
        draw_text(self.screen, "Press R to restart or ESC for menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, self.font, COL_TEXT, center=True)
