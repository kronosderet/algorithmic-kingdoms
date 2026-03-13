# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60

TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 128, 128
CAMERA_SPEED = 400
EDGE_SCROLL_MARGIN = 15
ZOOM_MIN = 0.4
ZOOM_MAX = 2.0
ZOOM_STEP = 0.1

# GUI layout
TOP_BAR_H = 40
BOTTOM_PANEL_H = 130
GAME_AREA_Y = TOP_BAR_H
GAME_AREA_H = SCREEN_HEIGHT - TOP_BAR_H - BOTTOM_PANEL_H

# Minimap
MINIMAP_SIZE = 160
MINIMAP_MARGIN = 8
MINIMAP_X = SCREEN_WIDTH - MINIMAP_SIZE - MINIMAP_MARGIN
MINIMAP_Y = TOP_BAR_H + MINIMAP_MARGIN

# Terrain
TERRAIN_GRASS = 0
TERRAIN_WATER = 1          # deep water — impassable
TERRAIN_TREE = 2
TERRAIN_GOLD = 3
TERRAIN_IRON = 4
TERRAIN_SHALLOW_WATER = 5  # v9.3: passable but slow
TERRAIN_STONE = 6          # v10: stone resource

TERRAIN_COLORS = {
    TERRAIN_GRASS: (40, 118, 74),  # v10g2: desaturated for unit contrast
    TERRAIN_WATER: (30, 90, 200),
    TERRAIN_TREE: (20, 100, 20),
    TERRAIN_GOLD: (218, 165, 32),
    TERRAIN_IRON: (140, 140, 155),
    TERRAIN_SHALLOW_WATER: (60, 130, 220),
    TERRAIN_STONE: (160, 150, 130),
}

# v9.3: movement cost multipliers (deep water omitted = impassable)
TERRAIN_MOVE_COST = {
    TERRAIN_GRASS: 1.0,
    TERRAIN_TREE: 2.0,
    TERRAIN_SHALLOW_WATER: 2.5,
    TERRAIN_GOLD: 1.8,
    TERRAIN_IRON: 1.8,
    TERRAIN_STONE: 1.8,
}

RESOURCE_CAPACITY = {TERRAIN_TREE: 50, TERRAIN_GOLD: 80, TERRAIN_IRON: 60, TERRAIN_STONE: 70}
TERRAIN_RESOURCE_MAP = {TERRAIN_TREE: "wood", TERRAIN_GOLD: "gold", TERRAIN_IRON: "iron", TERRAIN_STONE: "stone"}

# Difficulty profiles
DIFFICULTY_PROFILES = {
    "easy": {
        "start_gold": 300, "start_wood": 150, "start_iron": 0, "start_steel": 0,
        "start_workers": 4,
        "first_wave_time": 360, "wave_interval": 120, "max_waves": 15,
        "wave_base": 4, "wave_scale": 3,       # count = base + scale*sqrt(n)
        "hp_scale": 0.05, "atk_scale": 0.03,
        "archer_wave": 4, "siege_wave": 8, "elite_wave": 18,
        "multi_dir_wave": 14, "three_dir_wave": 20,
        "kill_bounty_base": 5,
        "wave_bonus_gold": 30, "wave_bonus_wood": 15, "wave_bonus_steel": 3,
        "label": "Easy",
    },
    "medium": {
        "start_gold": 200, "start_wood": 100, "start_iron": 0, "start_steel": 0,
        "start_workers": 3,
        "first_wave_time": 330, "wave_interval": 90, "max_waves": 20,   # v10g: +30s prep
        "wave_base": 4, "wave_scale": 4,                                # v10g: 5→4 smaller early waves
        "hp_scale": 0.07, "atk_scale": 0.04,                            # v10g: softer scaling
        "archer_wave": 3, "siege_wave": 7, "elite_wave": 15,            # v10g: siege 6→7
        "multi_dir_wave": 12, "three_dir_wave": 18,
        "kill_bounty_base": 4,                                           # v10g: 3→4 more reward
        "wave_bonus_gold": 25, "wave_bonus_wood": 15, "wave_bonus_steel": 3,  # v10g: better bonuses
        "label": "Medium",
    },
    "hard": {
        "start_gold": 180, "start_wood": 100, "start_iron": 0, "start_steel": 0,  # v10g: +30g +20w
        "start_workers": 3,
        "first_wave_time": 300, "wave_interval": 80, "max_waves": 25,   # v10g: 210→300, 75→80
        "wave_base": 5, "wave_scale": 5,                                # v10g: 8→5 base enemies
        "hp_scale": 0.08, "atk_scale": 0.05,                            # v10g: 0.10→0.08, 0.07→0.05
        "archer_wave": 2, "siege_wave": 5, "elite_wave": 12,            # v10g: siege 4→5
        "multi_dir_wave": 8, "three_dir_wave": 14,
        "kill_bounty_base": 2,
        "wave_bonus_gold": 15, "wave_bonus_wood": 8, "wave_bonus_steel": 2,  # v10g: better bonuses
        "label": "Hard",
    },
}

# Building definitions: (gold, wood, iron, steel, hp, build_time, size_tiles)
BUILDING_DEFS = {
    "town_hall": {"gold": 200, "wood": 120, "iron": 0, "steel": 0, "stone": 0, "hp": 500, "build_time": 30, "size": 2},
    "barracks": {"gold": 120, "wood": 80, "iron": 0, "steel": 0, "stone": 0, "hp": 400, "build_time": 18, "size": 2},
    "refinery": {"gold": 80, "wood": 60, "iron": 30, "steel": 0, "stone": 0, "hp": 300, "build_time": 22, "size": 2},
    "tower": {"gold": 30, "wood": 0, "iron": 15, "steel": 0, "stone": 35, "hp": 220, "build_time": 18, "size": 1},  # v10g: iron 20→15, stone 40→35
}

BUILDING_COLORS = {
    "town_hall": (139, 90, 43),
    "barracks": (140, 45, 45),
    "refinery": (100, 100, 130),
    "tower": (160, 160, 140),
}

BUILDING_LABELS = {"town_hall": "TH", "barracks": "BK", "refinery": "RF", "tower": "TW"}

# Unit definitions: (gold, wood, steel, hp, speed, attack, attack_range, attack_cd, train_time)
UNIT_DEFS = {
    "worker": {"gold": 50, "wood": 0, "steel": 0, "hp": 50, "speed": 80, "attack": 4, "range": 40, "cd": 1.0, "train": 8},
    "soldier": {"gold": 75, "wood": 0, "steel": 8, "hp": 140, "speed": 70, "attack": 14, "range": 40, "cd": 1.0, "train": 13},  # v10g: HP 130→140
    "archer": {"gold": 55, "wood": 25, "steel": 4, "hp": 75, "speed": 75, "attack": 9, "range": 170, "cd": 1.4, "train": 11},
}

UNIT_COLORS = {
    "worker": (50, 130, 220),
    "soldier": (200, 60, 60),
    "archer": (50, 190, 50),
}

UNIT_LABELS = {"worker": "W", "soldier": "S", "archer": "A",
               "enemy_soldier": "E", "enemy_archer": "E", "enemy_siege": "SG", "enemy_elite": "EL"}
UNIT_RADIUS = {"worker": 10, "soldier": 12, "archer": 11,
               "enemy_soldier": 12, "enemy_archer": 11, "enemy_siege": 14, "enemy_elite": 12}

# Enemy defs (base stats, scaled per wave)
ENEMY_DEFS = {
    "enemy_soldier": {"hp": 100, "speed": 55, "attack": 12, "range": 40, "cd": 1.2},
    "enemy_archer": {"hp": 60, "speed": 50, "attack": 6, "range": 140, "cd": 1.8},
    "enemy_siege": {"hp": 200, "speed": 35, "attack": 20, "range": 40, "cd": 3.0, "building_mult": 2.0},
    "enemy_elite": {"hp": 160, "speed": 60, "attack": 18, "range": 40, "cd": 1.0},
}

ENEMY_COLORS = {  # v10g2: black-dominant with faint color accents
    "enemy_soldier": (35, 12, 12),
    "enemy_archer": (35, 10, 30),
    "enemy_siege": (50, 25, 5),
    "enemy_elite": (50, 10, 25),
}

# Gather config
GATHER_TIME = {"wood": 2.0, "gold": 3.0, "iron": 3.0, "stone": 3.5}
GATHER_AMOUNT = 10
IRON_GATHER_AMOUNT = 15  # iron gathers faster per trip

# Refinery config
REFINE_IRON_COST = 2
REFINE_STEEL_YIELD = 1
REFINE_TIME = 6.0

# v10c: Tower Cannon (ballistic, replaces old hitscan)
TOWER_CANNON_DAMAGE = 45         # Level 1: single big hit
TOWER_CANNON_CD = 3.5            # slower than old 2.0s — massive damage per shot
TOWER_CANNON_SPEED = 250         # slower than arrows (350) — can miss movers
TOWER_CANNON_RANGE = 220         # slightly more than old 200
TOWER_CANNON_LIFETIME = 2.5      # max flight seconds before despawn
TOWER_CANNON_HIT_RADIUS = 16    # bigger than arrow (12)
TOWER_CANNON_SPREAD = 0.10      # radians — less scatter than recruit archer

# v10c: Level 2 — Explosive cannon (steel upgrade)
TOWER_UPGRADE_COST = {"steel": 15}
TOWER_UPGRADE_TIME = 12          # seconds of worker build work
TOWER_EXPLOSIVE_DAMAGE = 35      # AoE splash (less than direct, hits many)
TOWER_EXPLOSIVE_RADIUS = 60      # blast radius in pixels
TOWER_EXPLOSIVE_DIRECT = 50      # direct-hit damage (Level 2)

# Unit collision / separation
UNIT_SEPARATION_DIST = 20
UNIT_SEPARATION_FORCE = 50

# Worker flee behavior
WORKER_FLEE_RADIUS = 160
WORKER_SAFE_TIME = 2.0

# Worker repair
REPAIR_RATE = 15          # HP per second per worker
REPAIR_COST_FRACTION = 0.15  # fraction of building cost to fully repair from 0

# Healing near Town Hall
HEAL_RATE_NEAR_TH = 2        # HP per second for units near TH
HEAL_RADIUS_TH = 192         # 6 tiles radius

# Building ruins
RUIN_REBUILD_FRACTION = 0.40  # fraction of original cost to rebuild from ruins

# ---------------------------------------------------------------------------
# v10: Worker Skill XP System
# ---------------------------------------------------------------------------
WORKER_SKILL_NAMES = {
    "lumberjack": "Lumberjack", "gold_miner": "Gold Miner",
    "iron_miner": "Iron Miner", "stone_mason": "Stone Mason",
    "builder": "Builder", "smelter": "Smelter",
}
WORKER_RANKS = ["Novice", "Foreman", "Master"]
WORKER_RANK_XP = [0, 80, 200]           # cumulative thresholds
WORKER_RANK_SPEED_BONUS = {0: 0.0, 1: 0.15, 2: 0.30}
RESOURCE_TO_SKILL = {
    "wood": "lumberjack", "gold": "gold_miner",
    "iron": "iron_miner", "stone": "stone_mason",
}
WORKER_SKILL_COLORS = {
    "lumberjack": (34, 180, 34),     # green (COL_WOOD)
    "gold_miner": (255, 215, 0),     # gold (COL_GOLD)
    "iron_miner": (170, 170, 185),   # silver (COL_IRON_C)
    "stone_mason": (160, 150, 130),  # sandstone
    "builder": (0, 180, 255),        # cyan
    "smelter": (100, 160, 220),      # steel blue (COL_STEEL)
}
BUILDER_XP_PER_SECOND = 0.5  # XP per second of build/repair work (v10b: nerfed from 2)

# ---------------------------------------------------------------------------
# v9: XP & Military Ranks
# ---------------------------------------------------------------------------
MILITARY_RANKS = ["Recruit", "Veteran", "Corporal", "Sergeant", "Captain"]
RANK_XP_THRESHOLDS = [0, 10, 30, 70, 140]  # cumulative XP for each rank
XP_PER_HIT = 1
XP_KILL_BONUS = 3
RANK_BONUSES = {
    0: {"hp_mult": 1.0,  "atk_mult": 1.0,  "range_bonus": 0,  "accuracy_bonus": 0.0},
    1: {"hp_mult": 1.08, "atk_mult": 1.06, "range_bonus": 5,  "accuracy_bonus": 0.03},
    2: {"hp_mult": 1.16, "atk_mult": 1.12, "range_bonus": 10, "accuracy_bonus": 0.06},
    3: {"hp_mult": 1.26, "atk_mult": 1.20, "range_bonus": 18, "accuracy_bonus": 0.10},
    4: {"hp_mult": 1.40, "atk_mult": 1.30, "range_bonus": 25, "accuracy_bonus": 0.15},
}
RANK_COLORS = {
    0: (140, 140, 140),   # gray — Recruit
    1: (205, 127, 50),    # bronze — Veteran
    2: (192, 192, 210),   # silver — Corporal
    3: (255, 215, 0),     # gold — Sergeant
    4: (80, 180, 255),    # diamond blue — Captain
}

# v9: Ballistic Archery
ARROW_SPEED = 350
ARROW_MAX_LIFETIME = 2.0        # seconds in flight before despawn
ARROW_HIT_RADIUS = 12           # collision detection radius (px)
ARROW_BASE_SPREAD = 0.18        # radians — max aim scatter for Recruit
ARROW_MIN_SPREAD = 0.03         # radians — best accuracy (Captain)
GROUND_ARROW_LIFETIME = 8.0     # seconds stuck arrows persist as visuals
GROUND_ARROW_MAX = 50           # oldest culled when exceeded

# v9: Squad System
SQUAD_MAX_SIZE = 6
SQUAD_FOLLOW_DIST = 60          # followers stay within this of leader (px)
SQUAD_REASSIGN_INTERVAL = 2.0   # seconds between full squad rebuilds
SQUAD_COHESION_FORCE = 35       # pull strength toward leader

# v9: Enemy XP
ENEMY_XP_PER_HIT = 1
ENEMY_XP_KILL_BONUS = 2

# Enemy flee / veteran return
ENEMY_FLEE_HP_FRACTION = 0.20  # flee when below 20% HP
ENEMY_VETERAN_BONUS = 0.25    # +25% stats for returning veterans

# v9.1: Target Priority System
BUILDING_PRIORITY = {
    "town_hall": 10.0, "tower": 7.0, "barracks": 6.0, "refinery": 5.0,
}
UNIT_PRIORITY = {
    "soldier": 4.0, "archer": 4.5, "worker": 1.0,
    "enemy_soldier": 4.0, "enemy_archer": 4.5,
    "enemy_elite": 6.0, "enemy_siege": 7.0,
}
RUIN_PRIORITY_MULT = 0.15          # ruins are worth much less
DISTANCE_NORMALIZATION = 300.0     # px — at this distance priority halved
RANK_TARGETING_NOISE = {           # higher rank = less noise = smarter picks
    0: 0.50, 1: 0.30, 2: 0.15, 3: 0.05, 4: 0.00,
}
TOWER_LOW_HP_BONUS = 2.0           # finish off wounded targets
TOWER_LOW_HP_THRESHOLD = 0.30      # HP fraction for bonus
TOWER_HIGH_THREAT_TYPES = {"enemy_elite": 1.5, "enemy_siege": 1.8}
LOW_HP_FINISH_BONUS = 1.3          # unit targeting: prefer wounded
LOW_HP_FINISH_THRESHOLD = 0.40
ENGAGED_TARGET_BONUS = 1.15        # slight preference for current target

# v9.3: Live Retargeting + Threat Response
RETARGET_INTERVAL = 1.5            # sec between retarget checks during combat
RETARGET_SWITCH_THRESHOLD = 1.2    # new target must score 20% better to switch
THREAT_BONUS = 2.5                 # score multiplier for "who's attacking me"

# v9.2: Enemy Horde Morale
MORALE_CHECK_INTERVAL = 1.0        # sec between morale checks per unit (staggered)
MORALE_SCAN_RADIUS = 160           # px — local force count area
MORALE_FLEE_RATIO = 3.0            # player:enemy ratio to trigger panic
MORALE_LEADER_AURA = 120           # px — Sergeant+ suppresses flee nearby
MORALE_LEADER_MIN_RANK = 3         # Sergeant+
MORALE_RANK_RESISTANCE = {         # multiplier on flee ratio (higher = braver)
    0: 1.0, 1: 1.3, 2: 1.6, 3: 999, 4: 999,
}

# v9.2: Player Formation Hints (soft positional forces)
FORMATION_FRONT_OFFSET = 30        # px — soldiers position forward of leader
FORMATION_REAR_OFFSET = 35         # px — archers position behind leader
FORMATION_FORCE = 25               # px/sec — gentle positional pull
FORMATION_RANK_PUSH = 5            # px per rank diff — low rank more forward

# Gameplay tuning (extracted from inline magic numbers)
PATH_ARRIVAL_THRESHOLD = 3            # px distance to snap to next path waypoint
BUILD_PROXIMITY = TILE_SIZE * 2.5     # max distance for worker to build/repair
WORKER_FLEE_DISTANCE = 6 * TILE_SIZE  # how far workers flee from enemies
SELECT_RADIUS = 20                    # click distance to select a unit
DRAG_THRESHOLD = 5                    # min drag pixels before box-select starts
SPAWN_MARGIN = 2                      # min tiles from map edge for enemy spawn
SPAWN_RETRIES = 30                    # max attempts to find walkable spawn pos
IDLE_AGGRO_RANGE = 64                 # bonus px range for idle auto-aggro

# ---------------------------------------------------------------------------
# v10_1: Unit Trait System (procedural personalities)
# ---------------------------------------------------------------------------
TRAIT_POOL = {
    # trait_name: (rarity_weight, allowed_types)
    "brave":        (30, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite"}),
    "cowardly":     (30, {"soldier", "archer", "enemy_soldier", "enemy_archer"}),
    "aggressive":   (30, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite"}),
    "cautious":     (30, {"soldier", "archer", "enemy_soldier", "enemy_archer"}),
    "loyal":        (15, {"soldier", "archer", "enemy_soldier", "enemy_archer"}),
    "lone_wolf":    (15, {"soldier", "archer", "enemy_soldier", "enemy_archer"}),
    "sharpshooter": (8,  {"archer", "enemy_archer"}),
    "berserker":    (8,  {"soldier", "enemy_soldier", "enemy_elite"}),
    "inspiring":    (4,  {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite"}),
    "nimble":       (25, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite", "enemy_siege"}),
}

TRAIT_CONFLICTS = {
    frozenset({"brave", "cowardly"}),
    frozenset({"aggressive", "cautious"}),
    frozenset({"loyal", "lone_wolf"}),
}

# How many traits a unit rolls at creation: {count: weight}
TRAIT_ROLL_WEIGHTS = {0: 40, 1: 45, 2: 15}

# Modifier keys each trait provides (applied as multipliers or additive bonuses)
TRAIT_MODIFIERS = {
    "brave":        {"morale_mult": 1.5},
    "cowardly":     {"morale_mult": 0.7},
    "aggressive":   {"aggro_range_mult": 1.4, "noise_mult": 1.3},  # more noise = less precise targeting
    "cautious":     {"aggro_range_mult": 0.7, "low_hp_bonus": 0.3},
    "loyal":        {"cohesion_mult": 2.0},
    "lone_wolf":    {"lone_atk_bonus": 0.15},
    "sharpshooter": {"spread_mult": 0.6},
    "berserker":    {"berserk_atk_bonus": 0.25},
    "inspiring":    {"is_morale_leader": True},
    "nimble":       {"terrain_speed_bonus": 0.15},
}

TRAIT_DISPLAY = {
    "brave":        {"color": (255, 215, 0),   "symbol": "B"},
    "cowardly":     {"color": (140, 140, 140), "symbol": "C"},
    "aggressive":   {"color": (220, 50, 50),   "symbol": "A"},
    "cautious":     {"color": (80, 140, 220),  "symbol": "E"},
    "loyal":        {"color": (50, 200, 80),   "symbol": "L"},
    "lone_wolf":    {"color": (192, 192, 210), "symbol": "W"},
    "sharpshooter": {"color": (160, 80, 220),  "symbol": "X"},
    "berserker":    {"color": (180, 20, 20),   "symbol": "K"},
    "inspiring":    {"color": (255, 230, 80),  "symbol": "I"},
    "nimble":       {"color": (0, 200, 180),   "symbol": "N"},
}

# Control groups
MAX_CONTROL_GROUPS = 10  # 0-9

# Rally point
RALLY_POINT_COLOR = (80, 255, 80)

# Colors
COL_BG = (20, 20, 30)
COL_GUI_BG = (30, 30, 45)
COL_GUI_BORDER = (80, 80, 100)
COL_TEXT = (220, 220, 220)
COL_GOLD = (255, 215, 0)
COL_WOOD = (34, 180, 34)
COL_IRON_C = (170, 170, 185)
COL_STEEL = (100, 160, 220)
COL_STONE = (160, 150, 130)
COL_SELECT = (0, 255, 0)
COL_HEALTH_BG = (60, 0, 0)
COL_HEALTH = (0, 200, 0)
COL_ENEMY_HEALTH = (200, 0, 0)
COL_BTN = (60, 60, 80)
COL_BTN_HOVER = (80, 80, 110)
COL_BTN_DISABLED = (40, 40, 50)
COL_BTN_TEXT = (200, 200, 220)
COL_PLACE_VALID = (0, 200, 0, 80)
COL_PLACE_INVALID = (200, 0, 0, 80)
