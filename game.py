import pygame
import math
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE,
                       MAP_COLS, MAP_ROWS, TOP_BAR_H, BOTTOM_PANEL_H,
                       GAME_AREA_Y, GAME_AREA_H, ZOOM_STEP,
                       MINIMAP_SIZE, MINIMAP_MARGIN, MINIMAP_X, MINIMAP_Y,
                       TERRAIN_GRASS, TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON, TERRAIN_STONE,
                       TERRAIN_COLORS, BUILDING_DEFS, BUILDING_LABELS,
                       COL_BG, COL_SELECT, COL_TEXT,
                       DIFFICULTY_PROFILES,
                       HEAL_RATE_NEAR_TH, HEAL_RADIUS_TH,
                       GROUND_ARROW_MAX,
                       SELECT_RADIUS, DRAG_THRESHOLD,
                       TOWER_UPGRADE_COST, TOWER_CANNON_DAMAGE,
                       TOWER_CANNON_CD, TOWER_EXPLOSIVE_DIRECT,
                       MAX_CONTROL_GROUPS, RALLY_POINT_COLOR,
                       GARRISON_COST,
                       DROPOFF_BUILDING_TYPES, PRODUCTION_RATES,
                       UPGRADE_PATH,
                       STANCE_AGGRESSIVE, STANCE_DEFENSIVE, STANCE_GUARD,
                       STANCE_HUNT, STANCE_NAMES, STANCE_COLORS,
                       FORMATION_POLAR_ROSE, FORMATION_GOLDEN_SPIRAL,
                       FORMATION_SIERPINSKI, FORMATION_KOCH, FORMATION_NAMES,
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
        self.select_start = None
        self.placing_building = None  # building type str or None

        # font cache
        self.font = pygame.font.SysFont(None, 22)
        self.font_sm = pygame.font.SysFont(None, 18)
        self.font_lg = pygame.font.SysFont(None, 48)
        self.font_notif = pygame.font.SysFont(None, 26)

        # minimap
        self.minimap_surf = None

        # notifications
        self._notifications = []  # list of [text, timer, color]

        # wave clear tracking
        self._had_enemies = False

        # v10_1: control groups (Ctrl+0-9 to assign, 0-9 to recall)
        self.control_groups = [[] for _ in range(MAX_CONTROL_GROUPS)]

        # v10_1: attack-move mode (A key, then click)
        self.attack_move_mode = False

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
            wx = th.x + 50 + i * 25
            wy = th.y + 50
            w = Unit(wx, wy, "worker", "player")
            self.player_units.append(w)

    def add_notification(self, text, duration=3.0, color=(255, 255, 100)):
        """Add a floating notification message."""
        self._notifications.append([text, duration, color])

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self.game_time += dt
            self.handle_events()
            if not self.game_over and not self.game_won:
                self.update(dt)
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

            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if GAME_AREA_Y <= my < GAME_AREA_Y + GAME_AREA_H:
                    self.camera.apply_zoom(event.y * ZOOM_STEP, mx, my)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_left_down(event.pos)
                elif event.button == 3:
                    self._handle_right_click(event.pos)

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

        # cache worker selection (used by both control groups and build hotkeys)
        workers_selected = [u for u in self.selected if isinstance(u, Unit) and u.unit_type == "worker"]

        # v10_1: control groups — Ctrl+0-9 assigns, 0-9 recalls
        mods = pygame.key.get_mods()
        num_keys = {pygame.K_0: 0, pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
                    pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7,
                    pygame.K_8: 8, pygame.K_9: 9}
        if key in num_keys:
            group_idx = num_keys[key]
            if mods & pygame.KMOD_CTRL:
                # assign current selection to control group
                units_sel = [e for e in self.selected if isinstance(e, Unit)]
                if units_sel:
                    self.control_groups[group_idx] = [u.eid for u in units_sel]
                    self.add_notification(f"Group {group_idx}: {len(units_sel)} units", 1.5, (180, 220, 255))
                    return
            else:
                # recall control group — check if workers selected first (build hotkeys 1-4)
                if workers_selected and group_idx in (1, 2, 3, 4):
                    # fall through to build hotkeys below
                    pass
                elif self.control_groups[group_idx]:
                    # recall: select units in this group
                    for e in self.selected:
                        e.selected = False
                    self.selected.clear()
                    eids = set(self.control_groups[group_idx])
                    for u in self.player_units:
                        if u.alive and u.eid in eids:
                            u.selected = True
                            self.selected.append(u)
                    # clean dead units from group
                    alive_eids = {u.eid for u in self.player_units if u.alive}
                    self.control_groups[group_idx] = [eid for eid in self.control_groups[group_idx] if eid in alive_eids]
                    if self.selected:
                        # center camera on first unit
                        e = self.selected[0]
                        z = self.camera.zoom
                        self.camera.x = e.x - SCREEN_WIDTH / (2 * z)
                        self.camera.y = e.y - GAME_AREA_H / (2 * z)
                    return

        # v10_6: Formation hotkeys F1-F4, Stance hotkeys F5-F8
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
                for u in combat_sel:
                    self.player_squad_mgr.set_formation(u, fmt)
                self.add_notification(f"Formation: {FORMATION_NAMES[fmt]}", 1.5, (180, 220, 255))
                return
            if key in stance_keys:
                st = stance_keys[key]
                for u in combat_sel:
                    u.command_set_stance(st)
                    self.player_squad_mgr.set_stance(u, st)
                    if st == STANCE_GUARD:
                        self.player_squad_mgr.set_guard_position(u, u.x, u.y)
                color = STANCE_COLORS.get(st, (180, 220, 255))
                self.add_notification(f"Stance: {STANCE_NAMES[st]}", 1.5, color)
                return

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

        # train hotkeys (need building selected)
        buildings_selected = [e for e in self.selected if isinstance(e, Building) and e.built]
        for b in buildings_selected:
            if key == pygame.K_q and b.building_type == "town_hall":
                b.start_train("worker", self)
            elif key == pygame.K_w and b.building_type == "barracks":
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

        # deselect all
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
            best.selected = True
            self.selected.append(best)
        else:
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

    def _box_select(self, start, end):
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
            sx, sy = self.camera.world_to_screen(u.x, u.y)
            if x1 <= sx <= x2 and y1 <= sy <= y2:
                u.selected = True
                self.selected.append(u)

    def _handle_right_click(self, pos):
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
            return

        # check enemy at position
        for e in self.enemy_units:
            if not e.alive:
                continue
            if dist(wx, wy, e.x, e.y) < SELECT_RADIUS:
                for u in units_sel:
                    u.command_attack(e, self)
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
                others = [u for u in units_sel if u.unit_type != "worker"]
                for u in others:
                    u.command_move(wx, wy, self)
                return

        # move command
        for u in units_sel:
            u.command_move(wx, wy, self)

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
        for u in self.player_units:
            if u.unit_type in ("soldier", "archer") and u.state != "garrisoned":
                u.command_move(def_x, def_y, self)
                u.command_set_stance(STANCE_GUARD)
                # set guard position for squad
                self.player_squad_mgr.set_guard_position(u, def_x, def_y)

    def global_attack(self):
        """All combat units hunt down enemies."""
        for u in self.player_units:
            if u.unit_type not in ("soldier", "archer") or u.state == "garrisoned":
                continue
            # find nearest enemy
            best = None
            best_d = 1e9
            for e in self.enemy_units:
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
        # suppress WASD only during attack-move targeting click
        suppress = self.attack_move_mode
        self.camera.update(keys, dt, mx, my, suppress_wasd=suppress)

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

        # v9: update squad managers
        self.player_squad_mgr.update(dt, self.player_units)
        self.enemy_squad_mgr.update(dt, self.enemy_units)

        # passive healing near town hall
        town_halls = [b for b in self.player_buildings
                      if b.alive and b.built and not b.ruined
                      and b.building_type == "town_hall"]
        for u in self.player_units:
            if not u.alive or u.hp >= u.max_hp:
                continue
            for th in town_halls:
                if dist(u.x, u.y, th.x, th.y) <= HEAL_RADIUS_TH:
                    u.hp = min(u.max_hp, u.hp + HEAL_RATE_NEAR_TH * dt)
                    break

        # v10_1: record combat heat for dead units (minimap overlay)
        for u in self.enemy_units:
            if not u.alive:
                self._combat_heat.append([u.x, u.y, 30.0])  # 30 sec decay
        for u in self.player_units:
            if not u.alive and u.unit_type != "worker":
                self._combat_heat.append([u.x, u.y, 30.0])
        # decay heat
        self._combat_heat = [[x, y, t - dt] for x, y, t in self._combat_heat if t - dt > 0]

        # v10_6: count player losses for adaptive difficulty
        dead_player_units = sum(1 for u in self.player_units if not u.alive and u.unit_type != "worker")
        dead_player_buildings = sum(1 for b in self.player_buildings if not b.alive)
        self.enemy_ai.units_lost_this_wave += dead_player_units
        self.enemy_ai.buildings_lost_this_wave += dead_player_buildings

        # remove dead
        self.player_units = [u for u in self.player_units if u.alive]
        self.enemy_units = [u for u in self.enemy_units if u.alive]
        self.player_buildings = [b for b in self.player_buildings if b.alive]
        self.selected = [e for e in self.selected if e.alive]
        # v10_2: clear inspected enemy if dead
        if self.inspected_enemy and not self.inspected_enemy.alive:
            self.inspected_enemy = None

        # wave cleared check
        enemies_now = len(self.enemy_units) > 0
        if had_enemies and not enemies_now and self.enemy_ai.wave_number > 0:
            self._on_wave_cleared()

        # update notifications (filter uses timer - dt so no negative timers survive)
        self._notifications = [[t, timer - dt, c]
                                for t, timer, c in self._notifications if timer - dt > 0]

        # check game over
        if not self.player_buildings:
            self.game_over = True
            self.logger.log(self.game_time, "GAME_OVER",
                            self.enemy_ai.wave_number, "defeat", self.difficulty)

        if self.enemy_ai.game_won and not self.enemy_units:
            self.game_won = True
            self.logger.log(self.game_time, "GAME_OVER",
                            self.enemy_ai.wave_number, "victory", self.difficulty)

    def _on_wave_cleared(self):
        """Award wave completion bonus and apply veterancy."""
        wn = self.enemy_ai.wave_number
        profile = self.difficulty_profile

        # wave completion bonus (scales slightly with wave number)
        bonus_gold = profile["wave_bonus_gold"] + wn * 2
        bonus_wood = profile["wave_bonus_wood"] + wn
        bonus_steel = profile["wave_bonus_steel"] + wn // 3
        self.resources.gold += bonus_gold
        self.resources.wood += bonus_wood
        self.resources.steel += bonus_steel

        self.add_notification(
            f"Wave {wn} cleared! +{bonus_gold}g +{bonus_wood}w +{bonus_steel}s",
            3.5, (255, 255, 100))

        # count escaped enemies for notification
        esc = len(self.escaped_enemies)
        if esc > 0:
            self.add_notification(
                f"{esc} {'enemy' if esc == 1 else 'enemies'} escaped — they will return stronger!",
                3.5, (255, 140, 80))

        self.logger.log(self.game_time, "WAVE_CLEARED", wn,
                        str(bonus_gold), str(bonus_wood), str(bonus_steel),
                        esc, f"enemies_escaped:{esc}")

        # v10_6: record wave pressure for adaptive difficulty
        self.enemy_ai.enemies_escaped_this_wave = esc
        wave_count = self.enemy_ai.get_wave_count(wn)
        self.enemy_ai.record_wave_pressure(wave_count)

        # v9: rank-up notifications (XP is granted per-hit during combat, not here)
        # Clear projectiles between waves for visual cleanliness
        self.ground_arrows.clear()
        self.cannonballs.clear()
        self.craters.clear()

    def render(self):
        self.screen.fill(COL_BG)

        # clip game area
        clip_rect = pygame.Rect(0, GAME_AREA_Y, SCREEN_WIDTH, GAME_AREA_H)
        self.screen.set_clip(clip_rect)

        self._render_map()
        self._render_ground_arrows()   # v9: stuck arrows on ground (below units)
        self._render_craters()         # v10_5: cannonball impact craters
        self._render_buildings()
        self._render_units()
        self._render_arrows()          # v9: flying arrows (above units)
        self._render_cannonballs()     # v10c: tower cannonballs + explosions
        self._render_placement_ghost()
        self._render_rally_points()     # v10_1: rally point flags
        self._render_select_rect()
        self._render_enemy_inspect()    # v10_2: red ring on inspected enemy

        self.screen.set_clip(None)

        # GUI
        self.gui.draw_top_bar(self.screen, self.resources, self.enemy_ai, self.player_units)
        self.gui.draw_bottom_panel(self.screen, self.selected, self,
                                   inspected_enemy=self.inspected_enemy)

        # minimap
        self._render_minimap()

        # v10_2: attack-move cursor indicator
        if self.attack_move_mode:
            mx, my = pygame.mouse.get_pos()
            draw_text(self.screen, "ATTACK MOVE", mx + 12, my - 12, self.font_sm, (255, 80, 80))

        # notifications
        self._render_notifications()

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

    def _render_map(self):
        vr = self.camera.visible_rect()
        z = self.camera.zoom
        ts = int(TILE_SIZE * z) + 1  # screen-space tile size (+ 1 to avoid gaps)
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
            w = (c_max - c_min) * ts + ts
            h = (r_max - r_min) * ts + ts
            cache = pygame.Surface((max(1, w), max(1, h)))
            cache.fill((40, 118, 74))  # grass base

            for r in range(r_min, r_max):
                for c in range(c_min, c_max):
                    t = self.game_map.tiles[r][c]
                    lx = (c - c_min) * ts
                    ly = (r - r_min) * ts
                    if t != TERRAIN_GRASS:
                        color = TERRAIN_COLORS.get(t, (40, 118, 74))
                        pygame.draw.rect(cache, color, (lx, ly, ts, ts))

                    # decorations
                    if t == TERRAIN_TREE:
                        cx = lx + ts // 2
                        cy = ly + ts // 2
                        r1 = max(2, int(10 * z))
                        r2 = max(2, int(8 * z))
                        pygame.draw.circle(cache, (0, 60, 0), (cx, cy - int(4 * z)), r1)
                        pygame.draw.circle(cache, (10, 80, 10), (cx, cy - int(4 * z)), r2)
                    elif t == TERRAIN_GOLD:
                        cx = lx + ts // 2
                        cy = ly + ts // 2
                        pygame.draw.circle(cache, (255, 230, 80), (cx, cy), max(2, int(6 * z)))
                    elif t == TERRAIN_IRON:
                        cx = lx + ts // 2
                        cy = ly + ts // 2
                        s = int(7 * z)
                        s2 = int(6 * z)
                        s3 = int(5 * z)
                        pts = [(cx, cy - s), (cx - s2, cy + s3), (cx + s2, cy + s3)]
                        pygame.draw.polygon(cache, (180, 180, 195), pts)
                    elif t == TERRAIN_STONE:
                        cx = lx + ts // 2
                        cy = ly + ts // 2
                        s = int(6 * z)
                        pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
                        pygame.draw.polygon(cache, (185, 175, 155), pts)

            # grid lines (only at zoom >= 0.7)
            if z >= 0.7:
                grid_col = (30, 90, 56)
                for r in range(r_max - r_min + 1):
                    y = r * ts
                    pygame.draw.line(cache, grid_col, (0, y), (w, y))
                for c in range(c_max - c_min + 1):
                    x = c * ts
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

    def _draw_overlay(self, text, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        draw_text(self.screen, text, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, self.font_lg, color, center=True)
        draw_text(self.screen, "Press R to restart or ESC for menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, self.font, COL_TEXT, center=True)
