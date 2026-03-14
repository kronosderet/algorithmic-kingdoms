# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FPS = 60

TILE_SIZE = 32
MAP_COLS, MAP_ROWS = 128, 128
CAMERA_SPEED = 400
EDGE_SCROLL_MARGIN = 25
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
TERRAIN_WATER = 1          # reserved (water removed in v10_3, will return in terrain overhaul)
TERRAIN_TREE = 2
TERRAIN_GOLD = 3
TERRAIN_IRON = 4
TERRAIN_SHALLOW_WATER = 5  # reserved
TERRAIN_STONE = 6          # v10: stone resource

TERRAIN_COLORS = {
    TERRAIN_GRASS: (40, 118, 74),  # v10g2: desaturated for unit contrast
    TERRAIN_TREE: (20, 100, 20),
    TERRAIN_GOLD: (218, 165, 32),
    TERRAIN_IRON: (140, 140, 155),
    TERRAIN_STONE: (160, 150, 130),
}

# Movement cost multipliers — all terrain is passable with varying speed penalty
TERRAIN_MOVE_COST = {
    TERRAIN_GRASS: 1.0,
    TERRAIN_TREE: 2.0,
    TERRAIN_GOLD: 1.8,
    TERRAIN_IRON: 1.8,
    TERRAIN_STONE: 1.8,
}

RESOURCE_CAPACITY = {TERRAIN_TREE: 50, TERRAIN_GOLD: 80, TERRAIN_IRON: 60, TERRAIN_STONE: 70}
TERRAIN_RESOURCE_MAP = {TERRAIN_TREE: "wood", TERRAIN_GOLD: "gold", TERRAIN_IRON: "iron", TERRAIN_STONE: "stone"}

# Difficulty profiles
DIFFICULTY_PROFILES = {
    "easy": {
        "start_gold": 300, "start_wood": 150, "start_iron": 0, "start_steel": 0, "start_stone": 0,
        "start_workers": 4,
        "kill_bounty_base": 5,
        "wave_bonus_gold": 30, "wave_bonus_wood": 15, "wave_bonus_steel": 3,
        "label": "Easy",
        # v10_9: Incident Director
        "incidents_required": 12,
        "tension_drift": 0.003,
        "first_incident_time": 300,
        "min_cooldown": 40,
        "base_cooldown": 90,
        "incident_hp_scale": 0.04,
        "incident_atk_scale": 0.03,
        "incident_unlock": {
            "enemy_archer": 2, "enemy_sapper": 5, "enemy_raider": 6,
            "enemy_siege": 7, "enemy_shieldbearer": 8,
            "enemy_healer": 10, "enemy_elite": 11, "enemy_warlock": 12,
        },
    },
    "medium": {
        "start_gold": 200, "start_wood": 100, "start_iron": 0, "start_steel": 0, "start_stone": 0,
        "start_workers": 3,
        "kill_bounty_base": 4,
        "wave_bonus_gold": 25, "wave_bonus_wood": 15, "wave_bonus_steel": 3,
        "label": "Medium",
        # v10_9: Incident Director
        "incidents_required": 16,
        "tension_drift": 0.005,
        "first_incident_time": 270,
        "min_cooldown": 25,
        "base_cooldown": 70,
        "incident_hp_scale": 0.05,
        "incident_atk_scale": 0.04,
        "incident_unlock": {
            "enemy_archer": 2, "enemy_sapper": 4, "enemy_raider": 5,
            "enemy_siege": 6, "enemy_shieldbearer": 7,
            "enemy_healer": 9, "enemy_elite": 10, "enemy_warlock": 13,
        },
    },
    "hard": {
        "start_gold": 180, "start_wood": 100, "start_iron": 0, "start_steel": 0, "start_stone": 0,
        "start_workers": 3,
        "kill_bounty_base": 2,
        "wave_bonus_gold": 15, "wave_bonus_wood": 8, "wave_bonus_steel": 2,
        "label": "Hard",
        # v10_9: Incident Director
        "incidents_required": 22,
        "tension_drift": 0.007,
        "first_incident_time": 240,
        "min_cooldown": 15,
        "base_cooldown": 50,
        "incident_hp_scale": 0.06,
        "incident_atk_scale": 0.05,
        "incident_unlock": {
            "enemy_archer": 2, "enemy_sapper": 3, "enemy_raider": 4,
            "enemy_siege": 5, "enemy_shieldbearer": 6,
            "enemy_healer": 8, "enemy_elite": 9, "enemy_warlock": 11,
        },
    },
}

# ---------------------------------------------------------------------------
# v10_9: Incident Director — Dramaturgic Threat Engine
# ---------------------------------------------------------------------------

# Threat tier tension thresholds
TIER_TENSION_THRESHOLDS = {
    "light": 0.0,
    "medium": 0.25,
    "strong": 0.50,
    "deadly": 0.75,
}

# Stat scaling multipliers per tier
TIER_STAT_SCALING = {
    "light": 0.7,
    "medium": 1.0,
    "strong": 1.2,
    "deadly": 1.5,
}

# Tension adjustment after incident outcome
OUTCOME_TENSION_DELTA = {
    "dominated": 0.08,    # player too strong → escalate
    "won": -0.05,         # slight relief
    "costly": -0.15,      # real relief
    "devastating": -0.30, # major catharsis
}

# Outcome cooldown multipliers (how long before next incident)
OUTCOME_COOLDOWN_MULT = {
    "dominated": 0.6,
    "won": 1.0,
    "costly": 1.5,
    "devastating": 2.2,
}

# Pain ratio thresholds for outcome classification
OUTCOME_PAIN_THRESHOLDS = {
    "dominated": 0.05,   # pain < 0.05, no escapes, < 30s
    "won": 0.20,         # pain < 0.2, ≤1 escape
    "costly": 0.50,      # pain < 0.5
    # devastating: pain ≥ 0.5
}
OUTCOME_DOMINATED_MAX_TIME = 30.0  # seconds — must resolve faster than this
OUTCOME_WON_MAX_ESCAPES = 1

# FSM state durations
INCIDENT_FOREBODING_MIN = 10.0
INCIDENT_FOREBODING_MAX = 30.0
INCIDENT_IMMINENT_DURATION = 4.0
INCIDENT_AFTERMATH_MIN = 5.0
INCIDENT_AFTERMATH_MAX = 15.0

# False calm chance and multiplier
FALSE_CALM_CHANCE = 0.15
FALSE_CALM_MULT = 1.8

# Dramatic arc phase boundaries (fraction of incidents_required)
ARC_OPENING = 0.25       # Light only, long cooldowns
ARC_RISING = 0.50        # Medium unlocks, counter-pick
ARC_MIDGAME = 0.75       # Strong appears, economy raids
ARC_CLIMAX = 0.95        # Deadly possible, short cooldowns
# Finale = last incident, always deadly

# Incident catalogue: 13 flavours across 4 tiers
# composition: dict of unit_type → (min, max) count range within tier count budget
# behaviour: special incident-wide behaviour flag (None, "flee_on_contact", "probe_retreat", "economy_target")
# directions: number of spawn directions (1, 2, or 3)
# narrative_foreboding: text shown during FOREBODING state
# narrative_imminent: text shown during IMMINENT state
INCIDENT_CATALOGUE = {
    # --- LIGHT (tension >= 0.0, count 2-5) ---
    "scout": {
        "tier": "light", "count_range": (2, 4),
        "composition": {"enemy_soldier": 1.0},
        "behaviour": "flee_on_contact",
        "directions": 1,
        "narrative_foreboding": "Scouts spotted on the horizon...",
        "narrative_imminent": "They're watching us!",
    },
    "forager_raid": {
        "tier": "light", "count_range": (3, 5),
        "composition": {"enemy_raider": 0.6, "enemy_soldier": 0.4},
        "behaviour": "economy_target",
        "directions": 1,
        "narrative_foreboding": "Foragers are approaching our resources...",
        "narrative_imminent": "Protect the gatherers!",
    },
    "probe": {
        "tier": "light", "count_range": (3, 5),
        "composition": {"enemy_soldier": 0.5, "enemy_archer": 0.5},
        "behaviour": "probe_retreat",
        "directions": 1,
        "narrative_foreboding": "An enemy patrol is testing our perimeter...",
        "narrative_imminent": "Skirmishers incoming!",
    },
    # --- MEDIUM (tension >= 0.25, count 6-12) ---
    "assault": {
        "tier": "medium", "count_range": (6, 10),
        "composition": {"enemy_soldier": 0.5, "enemy_archer": 0.3, "enemy_siege": 0.2},
        "behaviour": None,
        "directions": 1,
        "narrative_foreboding": "War drums echo in the distance...",
        "narrative_imminent": "BRACE YOURSELVES!",
    },
    "flanking": {
        "tier": "medium", "count_range": (6, 10),
        "composition": {"enemy_soldier": 0.4, "enemy_archer": 0.3, "enemy_raider": 0.3},
        "behaviour": None,
        "directions": 2,
        "narrative_foreboding": "Movement detected on multiple fronts...",
        "narrative_imminent": "They're flanking us!",
    },
    "economy_raid": {
        "tier": "medium", "count_range": (6, 10),
        "composition": {"enemy_raider": 0.4, "enemy_sapper": 0.3, "enemy_soldier": 0.3},
        "behaviour": "economy_target",
        "directions": 1,
        "narrative_foreboding": "Raiders are eyeing our production...",
        "narrative_imminent": "Defend the economy!",
    },
    # --- STRONG (tension >= 0.50, count 12-20) ---
    "siege_column": {
        "tier": "strong", "count_range": (12, 18),
        "composition": {"enemy_siege": 0.2, "enemy_shieldbearer": 0.2, "enemy_soldier": 0.3, "enemy_healer": 0.1, "enemy_archer": 0.2},
        "behaviour": None,
        "directions": 1,
        "narrative_foreboding": "The ground trembles... siege engines approach.",
        "narrative_imminent": "SIEGE INCOMING!",
    },
    "war_party": {
        "tier": "strong", "count_range": (12, 18),
        "composition": {"enemy_elite": 0.15, "enemy_soldier": 0.35, "enemy_archer": 0.25, "enemy_healer": 0.1, "enemy_raider": 0.15},
        "behaviour": None,
        "directions": 1,
        "narrative_foreboding": "A warlord marshals their forces...",
        "narrative_imminent": "The war party charges!",
    },
    "pincer": {
        "tier": "strong", "count_range": (14, 20),
        "composition": {"enemy_soldier": 0.3, "enemy_archer": 0.25, "enemy_raider": 0.25, "enemy_elite": 0.2},
        "behaviour": None,
        "directions": 3,
        "narrative_foreboding": "We're being surrounded...",
        "narrative_imminent": "ENEMIES ON ALL SIDES!",
    },
    "healer_push": {
        "tier": "strong", "count_range": (12, 16),
        "composition": {"enemy_shieldbearer": 0.25, "enemy_healer": 0.2, "enemy_soldier": 0.35, "enemy_warlock": 0.2},
        "behaviour": None,
        "directions": 1,
        "narrative_foreboding": "Dark mending energy gathers...",
        "narrative_imminent": "An unkillable wall approaches!",
    },
    # --- DEADLY (tension >= 0.75, count 20-35) ---
    "grand_assault": {
        "tier": "deadly", "count_range": (22, 32),
        "composition": {"enemy_soldier": 0.25, "enemy_archer": 0.15, "enemy_siege": 0.1, "enemy_elite": 0.1, "enemy_shieldbearer": 0.1, "enemy_healer": 0.1, "enemy_raider": 0.1, "enemy_warlock": 0.1},
        "behaviour": None,
        "directions": 3,
        "narrative_foreboding": "The sky darkens. This is it.",
        "narrative_imminent": "THE FINAL STORM!",
    },
    "swarm": {
        "tier": "deadly", "count_range": (28, 35),
        "composition": {"enemy_soldier": 0.6, "enemy_raider": 0.4},
        "behaviour": None,
        "directions": 2,
        "narrative_foreboding": "An endless tide gathers at the edge...",
        "narrative_imminent": "THEY'RE EVERYWHERE!",
    },
    "dark_resonance": {
        "tier": "deadly", "count_range": (20, 28),
        "composition": {"enemy_warlock": 0.3, "enemy_elite": 0.25, "enemy_shieldbearer": 0.25, "enemy_healer": 0.2},
        "behaviour": None,
        "directions": 2,
        "dissonance_override": 0.50,  # 50% of enemies get dissonance regardless of normal chance
        "narrative_foreboding": "Reality fractures... the resonance fields waver.",
        "narrative_imminent": "DISSONANCE OVERWHELMING!",
    },
}

# Tiers grouped for easy lookup
INCIDENT_TIERS = {
    "light": [k for k, v in INCIDENT_CATALOGUE.items() if v["tier"] == "light"],
    "medium": [k for k, v in INCIDENT_CATALOGUE.items() if v["tier"] == "medium"],
    "strong": [k for k, v in INCIDENT_CATALOGUE.items() if v["tier"] == "strong"],
    "deadly": [k for k, v in INCIDENT_CATALOGUE.items() if v["tier"] == "deadly"],
}

# Incident behaviour constants
SCOUT_FLEE_CONTACT_TIME = 3.0    # seconds of combat before scouts flee
PROBE_RETREAT_TIME = 8.0         # seconds from spawn before probes retreat regardless

# Narrative text for FSM states
NARRATIVE_CALM = "Calm"
NARRATIVE_CALM_FALSE = "An unsettling silence falls..."
NARRATIVE_ACTIVE = "Under Attack!"
NARRATIVE_AFTERMATH = "Catching breath..."

# Building definitions: (gold, wood, iron, steel, hp, build_time, size_tiles)
BUILDING_DEFS = {
    "town_hall": {"gold": 200, "wood": 120, "iron": 0, "steel": 0, "stone": 0, "hp": 500, "build_time": 30, "size": 2},
    "barracks": {"gold": 120, "wood": 80, "iron": 0, "steel": 0, "stone": 0, "hp": 400, "build_time": 18, "size": 2},
    "refinery": {"gold": 80, "wood": 60, "iron": 30, "steel": 0, "stone": 0, "hp": 300, "build_time": 22, "size": 2},
    "tower": {"gold": 30, "wood": 0, "iron": 15, "steel": 0, "stone": 35, "hp": 220, "build_time": 18, "size": 1},  # v10g: iron 20→15, stone 40→35
    # v10.2: Helper buildings (1×1, Foreman unlocks)
    "goldmine_hut": {"gold": 40, "wood": 30, "iron": 0, "steel": 0, "stone": 0, "hp": 150, "build_time": 12, "size": 1},
    "lumber_camp":  {"gold": 30, "wood": 40, "iron": 0, "steel": 0, "stone": 0, "hp": 150, "build_time": 12, "size": 1},
    "quarry_hut":   {"gold": 40, "wood": 30, "iron": 0, "steel": 0, "stone": 10, "hp": 150, "build_time": 12, "size": 1},
    "iron_depot":   {"gold": 40, "wood": 30, "iron": 0, "steel": 0, "stone": 0, "hp": 150, "build_time": 12, "size": 1},
    "scaffold":     {"gold": 50, "wood": 40, "iron": 0, "steel": 0, "stone": 0, "hp": 100, "build_time": 10, "size": 1},
    # v10.2: Production buildings (2×2, Master upgrades from helper)
    "sawmill":      {"gold": 60, "wood": 0, "iron": 0, "steel": 0, "stone": 40, "hp": 300, "build_time": 20, "size": 2},
    "goldmine":     {"gold": 80, "wood": 0, "iron": 0, "steel": 0, "stone": 40, "hp": 300, "build_time": 20, "size": 2},
    "stoneworks":   {"gold": 60, "wood": 0, "iron": 0, "steel": 0, "stone": 30, "hp": 300, "build_time": 20, "size": 2},
    "iron_works":   {"gold": 60, "wood": 0, "iron": 0, "steel": 0, "stone": 40, "hp": 300, "build_time": 20, "size": 2},
    "forge":        {"gold": 60, "wood": 0, "iron": 20, "steel": 0, "stone": 30, "hp": 350, "build_time": 22, "size": 2},
}

BUILDING_COLORS = {
    "town_hall": (139, 90, 43),
    "barracks": (140, 45, 45),
    "refinery": (100, 100, 130),
    "tower": (160, 160, 140),
    # v10.2: helper buildings
    "goldmine_hut": (180, 150, 40),
    "lumber_camp": (60, 130, 50),
    "quarry_hut": (140, 130, 110),
    "iron_depot": (120, 120, 140),
    "scaffold": (50, 160, 200),
    # v10.2: production buildings
    "sawmill": (80, 160, 70),
    "goldmine": (200, 170, 50),
    "stoneworks": (160, 150, 130),
    "iron_works": (140, 140, 165),
    "forge": (180, 100, 50),
}

BUILDING_LABELS = {
    "town_hall": "TL", "barracks": "WN", "refinery": "CR", "tower": "SN",
    "goldmine_hut": "GN", "lumber_camp": "GT", "quarry_hut": "QN",
    "iron_depot": "IN", "scaffold": "LT",
    "sawmill": "TS", "goldmine": "GS", "stoneworks": "SS",
    "iron_works": "IS", "forge": "FF",
}

# v10_7: Thematic display names — Resonance identity
DISPLAY_NAMES = {
    # Buildings
    "town_hall": "Tree of Life", "barracks": "War Nexus", "refinery": "Crucible",
    "tower": "Sentinel",
    "goldmine_hut": "Gold Node", "lumber_camp": "Grove Tap",
    "quarry_hut": "Stone Node", "iron_depot": "Iron Node", "scaffold": "Lattice",
    "sawmill": "Timber Spire", "goldmine": "Gold Spire",
    "stoneworks": "Stone Spire", "iron_works": "Iron Spire", "forge": "Fractal Forge",
    # Player units
    "worker": "Gatherer", "soldier": "Warden", "archer": "Ranger",
    # Enemy units
    "enemy_soldier": "Dark Warden", "enemy_archer": "Shadow Ranger",
    "enemy_siege": "Siege Golem", "enemy_elite": "Void Knight",
    "enemy_sapper": "Blight Sapper", "enemy_shieldbearer": "Iron Bulwark",
    "enemy_healer": "Plague Mender", "enemy_raider": "Rift Raider",
    "enemy_warlock": "Chaos Warlock",
    "entrenched": "Entrenched Titan",
}

def display_name(key: str) -> str:
    """Get thematic display name for a building or unit type."""
    return DISPLAY_NAMES.get(key, key.replace("_", " ").title())

# Unit definitions: (gold, wood, steel, hp, speed, attack, attack_range, attack_cd, train_time)
UNIT_DEFS = {
    "worker": {"gold": 50, "wood": 0, "steel": 0, "hp": 50, "speed": 80, "attack": 4, "range": 40, "cd": 1.0, "train": 8},
    "soldier": {"gold": 75, "wood": 0, "steel": 8, "hp": 140, "speed": 70, "attack": 14, "range": 40, "cd": 1.0, "train": 13},  # v10g: HP 130→140
    "archer": {"gold": 55, "wood": 25, "steel": 4, "hp": 75, "speed": 75, "attack": 9, "range": 170, "cd": 1.4, "train": 11},
}

UNIT_COLORS = {  # Rainbow scheme: 7 colors for 7 unit types (ROYGBIV reversed)
    "worker":  (138, 43, 226),   # Violet — Gatherer
    "soldier": (75, 0, 180),     # Indigo — Warden
    "archer":  (30, 100, 255),   # Blue — Ranger
    # Future unit types:
    # unit_4:  (50, 205, 50),    # Green
    # unit_5:  (255, 220, 50),   # Yellow
    # unit_6:  (255, 140, 0),    # Orange
    # unit_7:  (220, 20, 60),    # Red — Sage
}

UNIT_LABELS = {"worker": "G", "soldier": "W", "archer": "R",
               "enemy_soldier": "E", "enemy_archer": "E", "enemy_siege": "SG", "enemy_elite": "VK",
               "enemy_sapper": "SP", "enemy_shieldbearer": "IB", "enemy_healer": "PM",
               "enemy_raider": "RR", "enemy_warlock": "CW"}
UNIT_RADIUS = {"worker": 10, "soldier": 12, "archer": 11,
               "enemy_soldier": 12, "enemy_archer": 11, "enemy_siege": 14, "enemy_elite": 12,
               "enemy_sapper": 11, "enemy_shieldbearer": 14, "enemy_healer": 10,
               "enemy_raider": 11, "enemy_warlock": 12}

# Enemy defs (base stats, scaled per wave)
ENEMY_DEFS = {
    "enemy_soldier": {"hp": 100, "speed": 55, "attack": 12, "range": 40, "cd": 1.2},
    "enemy_archer": {"hp": 60, "speed": 50, "attack": 6, "range": 140, "cd": 1.8},
    "enemy_siege": {"hp": 200, "speed": 35, "attack": 20, "range": 40, "cd": 3.0, "building_mult": 2.0},
    "enemy_elite": {"hp": 160, "speed": 60, "attack": 18, "range": 40, "cd": 1.0},
    # v10_6: New enemy types
    "enemy_sapper":       {"hp": 80,  "speed": 70, "attack": 5,  "range": 40,  "cd": 2.0, "building_mult": 3.0, "self_destruct": True},
    "enemy_shieldbearer": {"hp": 250, "speed": 40, "attack": 8,  "range": 40,  "cd": 1.5, "frontal_armor": 0.50},
    "enemy_healer":       {"hp": 60,  "speed": 45, "attack": 0,  "range": 120, "cd": 0,   "heal_rate": 5.0},
    "enemy_raider":       {"hp": 70,  "speed": 80, "attack": 10, "range": 40,  "cd": 1.0, "economy_only": True},
    "enemy_warlock":      {"hp": 90,  "speed": 45, "attack": 15, "range": 100, "cd": 3.0, "aoe_radius": 30},
}

ENEMY_COLORS = {  # Dark mirror of player rainbow — same hue, desaturated/darkened
    "enemy_soldier":      (30, 5, 55),    # dark indigo (mirrors Warden)
    "enemy_archer":       (12, 30, 75),   # dark blue (mirrors Ranger)
    "enemy_siege":        (50, 25, 5),    # dark amber
    "enemy_elite":        (50, 10, 25),   # dark crimson
    # v10_6: new enemy type colors
    "enemy_sapper":       (45, 40, 10),   # dark olive
    "enemy_shieldbearer": (40, 40, 45),   # dark steel
    "enemy_healer":       (15, 40, 20),   # dark green
    "enemy_raider":       (45, 15, 35),   # dark magenta
    "enemy_warlock":      (30, 10, 45),   # dark purple
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
TOWER_CANNON_SPEED = 250         # kept for legacy; flight_time governs arc
TOWER_CANNON_RANGE = 220         # slightly more than old 200
TOWER_MIN_RANGE = 45             # v10_7: dead zone directly below — can't depress cannon
TOWER_CANNON_LIFETIME = 2.5      # max flight seconds before despawn
TOWER_CANNON_HIT_RADIUS = 16    # bigger than arrow (12) — landing proximity
TOWER_CANNON_SPREAD = 0.10      # radians — less scatter than recruit archer
CANNONBALL_ARC_HEIGHT = 12       # low flat arc (heavy, fast)
CANNONBALL_FLIGHT_TIME = 0.4     # seconds to reach target (fast and dangerous)

# v10c: Level 2 — Explosive cannon (steel upgrade)
TOWER_UPGRADE_COST = {"steel": 15}
TOWER_UPGRADE_TIME = 12          # seconds of worker build work
TOWER_EXPLOSIVE_DAMAGE = 35      # AoE splash (less than direct, hits many)
TOWER_EXPLOSIVE_RADIUS = 60      # blast radius in pixels
TOWER_EXPLOSIVE_DIRECT = 50      # direct-hit damage (Level 2)

# v10_5: Crater VFX (cannonball ground impact)
CRATER_DURATION = 6.0            # seconds before full fade
CRATER_RADIUS_NORMAL = 10        # normal cannonball crater size (px)
CRATER_RADIUS_EXPLOSIVE = 26     # explosive crater size (px)
CRATER_BURN_PARTICLES = 8        # ember count for explosive craters
CRATER_BURN_DURATION = 3.5       # seconds burning embers persist

# v10_5: Impact screen shake
IMPACT_SHAKE_AMOUNT = 3          # pixels of camera displacement
IMPACT_SHAKE_DURATION = 0.12     # seconds

# v10_7: Tower upgrade fire penalty (50% rate while upgrading)
TOWER_UPGRADE_FIRE_MULT = 2.0    # cooldown multiplier during upgrade

# v10_7: Sentinel's Cry — tower dead zone mechanic
SENTINEL_CRY_COOLDOWN = 4.0      # seconds between cries
SENTINEL_CRY_RADIUS = 120        # px — friendly units within this get attack speed buff
SENTINEL_CRY_BUFF_DURATION = 3.0 # seconds the buff lasts
SENTINEL_CRY_SPEED_BONUS = 0.25  # 25% attack speed bonus for buffed units
SENTINEL_CRY_PULSE_DURATION = 0.6  # visual pulse ring duration

# v10_7: Sapper sympathetic detonation
SAPPER_BLAST_RADIUS = 40         # px — AOE damage radius on self-destruct

# v10_7: Straggler Metamorphosis — surviving enemies root and transform
STRAGGLER_ROOT_WAVES = 1         # root after surviving 1 wave beyond their own
STRAGGLER_METAMORPH_WAVES = 2    # transform after surviving 2 waves beyond their own
METAMORPH_HP_MULT = 3.0          # HP multiplier on transformation
METAMORPH_ATK_MULT = 2.0         # Attack multiplier
METAMORPH_SPEED_MULT = 0.6       # Slower but mobile again after transform

# ---------------------------------------------------------------------------
# v10_delta: Physics Movement Profiles
# ---------------------------------------------------------------------------
MOVEMENT_PROFILES = {
    "soldier":        {"accel": 180, "decel": 250, "max_speed": 70},
    "archer":         {"accel": 280, "decel": 150, "max_speed": 75},
    "worker":         {"accel": 120, "decel": 200, "max_speed": 80},
    "enemy_soldier":  {"accel": 160, "decel": 220, "max_speed": 55},
    "enemy_archer":   {"accel": 200, "decel": 150, "max_speed": 50},
    "enemy_siege":    {"accel": 60,  "decel": 400, "max_speed": 35},
    "enemy_elite":    {"accel": 250, "decel": 200, "max_speed": 60},
    "enemy_sapper":   {"accel": 300, "decel": 100, "max_speed": 70},
    "enemy_shieldbearer": {"accel": 80, "decel": 350, "max_speed": 40},
    "enemy_healer":   {"accel": 150, "decel": 180, "max_speed": 45},
    "enemy_raider":   {"accel": 400, "decel": 80,  "max_speed": 80},
    "enemy_warlock":  {"accel": 140, "decel": 200, "max_speed": 45},
}
MOVEMENT_PROFILE_DEFAULT = {"accel": 180, "decel": 200, "max_speed": 60}

# Collision avoidance (soft repulsion)
REPULSION_RADIUS = 16.0          # px — units start pushing apart
REPULSION_STRENGTH = 80.0        # px/sec² peak force (gentle nudge, not a shove)
REPULSION_FALLOFF = 2.0          # power falloff (quadratic — strong only when stacked)

# Formation gravitation (spring physics)
FORMATION_SPRING_K = 3.0         # spring constant (higher = snappier)
FORMATION_SPRING_DAMP = 0.7      # damping ratio (0=bouncy, 1=critical)
FORMATION_SPRING_MAX = 120       # max spring force px/sec²
FORMATION_COMBAT_LEASH = 80      # px — max stray before rubber-band

# Formation rotation & combat abilities (v10_epsilon)
FORMATION_ROTATION_SPEED = 0.3     # rad/sec base rotation
ROSE_SWEEP_DMG_FRACTION = 0.15     # 15% of unit ATK per sweep hit
ROSE_SWEEP_COOLDOWN = 1.5          # seconds between hits on same target
ROSE_SWEEP_RADIUS = 20.0           # px — contact distance for sweep hit
ROSE_ROTATION_ENERGY_COST = 5.0    # energy/sec shared across squad while rotating
# v10_epsilon: Spiral tighten/loosen
SPIRAL_C_MIN = 10.0                # tightest spiral (Vogel c)
SPIRAL_C_MAX = 30.0                # loosest spiral
SPIRAL_C_STEP = 2.0                # per scroll tick

# v10_epsilon: Sierpinski vertex pulse
SIERPINSKI_PULSE_EXPAND = 1.8      # multiply spacing temporarily
SIERPINSKI_PULSE_DURATION = 0.4    # seconds expanded
SIERPINSKI_PULSE_COOLDOWN = 3.0    # seconds between pulses
SIERPINSKI_PULSE_DMG = 0.10        # 10% ATK to nearby enemies
SIERPINSKI_PULSE_RADIUS = 25.0     # px — damage range from vertex
SIERPINSKI_PULSE_ENERGY = 20.0     # squad pool energy cost to activate pulse

# v10_epsilon: Koch perimeter contract
KOCH_CONTRACT_FACTOR = 0.4         # shrink to 40% radius
KOCH_CONTRACT_DURATION = 0.6       # seconds contracted
KOCH_CONTRACT_COOLDOWN = 4.0       # seconds between contracts
KOCH_CONTRACT_DMG = 0.12           # 12% ATK to trapped enemies
KOCH_CONTRACT_RADIUS = 35.0        # px — trap range from perimeter
KOCH_CONTRACT_ENERGY = 25.0        # squad pool energy cost to activate contract

# Physics arrival (replaces old grid-snap)
PHYSICS_ARRIVAL_DIST = 12.0      # px — "arrived at waypoint"
PHYSICS_WORKER_SNAP_DIST = 48.0  # px — workers snap to exact position at tasks

# ---------------------------------------------------------------------------
# v10_delta: Stamina / Energy System
# ---------------------------------------------------------------------------
# Energy model: acceleration costs a lot, cruising costs a little, braking is free.
# "accel_cost" = energy/sec while accelerating (dv > 0)
# "cruise_cost" = energy/sec while at constant speed
# "attack_cost" = energy per attack swing
# Braking/deceleration costs nothing.
ENERGY_PROFILES = {
    "soldier":        {"max": 100, "regen": 8,  "accel_cost": 10.0, "cruise_cost": 2.0, "attack_cost": 6.0},
    "archer":         {"max": 80,  "regen": 10, "accel_cost": 8.0,  "cruise_cost": 1.5, "attack_cost": 4.0},
    "worker":         {"max": 150, "regen": 15, "accel_cost": 6.0,  "cruise_cost": 1.0, "attack_cost": 0,  "gather_cost": 2.0},
    "enemy_soldier":  {"max": 100, "regen": 7,  "accel_cost": 10.0, "cruise_cost": 2.0, "attack_cost": 6.0},
    "enemy_archer":   {"max": 80,  "regen": 7,  "accel_cost": 8.0,  "cruise_cost": 1.5, "attack_cost": 4.0},
    "enemy_siege":    {"max": 150, "regen": 4,  "accel_cost": 5.0,  "cruise_cost": 1.0, "attack_cost": 10.0},
    "enemy_elite":    {"max": 120, "regen": 6,  "accel_cost": 12.0, "cruise_cost": 2.5, "attack_cost": 8.0},
    "enemy_sapper":   {"max": 70,  "regen": 5,  "accel_cost": 12.0, "cruise_cost": 2.0, "attack_cost": 8.0},
    "enemy_shieldbearer": {"max": 130, "regen": 5, "accel_cost": 8.0, "cruise_cost": 1.5, "attack_cost": 5.0},
    "enemy_healer":   {"max": 90,  "regen": 9,  "accel_cost": 6.0,  "cruise_cost": 1.0, "attack_cost": 3.0},
    "enemy_raider":   {"max": 70,  "regen": 5,  "accel_cost": 12.0, "cruise_cost": 2.0, "attack_cost": 8.0},
    "enemy_warlock":  {"max": 100, "regen": 6,  "accel_cost": 8.0,  "cruise_cost": 1.5, "attack_cost": 7.0},
}
ENERGY_PROFILE_DEFAULT = {"max": 100, "regen": 8, "accel_cost": 10.0, "cruise_cost": 2.0, "attack_cost": 6.0}

ENERGY_EXHAUSTED_SPEED = 0.6        # 60% speed at zero energy (not crippling)
ENERGY_EXHAUSTED_THRESHOLD = 0.2    # below 20% → exhausted debuffs
ENERGY_TIRED_COOLDOWN_MULT = 1.3    # +30% attack cooldown when exhausted
ENERGY_IDLE_REGEN_MULT = 3.0        # 3× regen when standing still (quick recovery)
ENERGY_FLEE_DRAIN_MULT = 1.5        # fleeing costs 50% more energy
ENERGY_CARRY_SPEED_MULT = 0.7       # workers move 30% slower when carrying resources
ENERGY_CARRY_REGEN_MULT = 0.85      # workers regen slightly slower while carrying

# Harmonic energy field
HARMONY_ENERGY_MULT = 0.8           # harmony bonus to energy regen
ROSE_ANCHOR_REGEN_MULT = 1.5        # commander energy regen bonus
ROSE_ANCHOR_SHARE_RATE = 3.0        # energy/sec shared to petal units
KOCH_ATTACK_ENERGY_DISCOUNT = 0.3   # 30% less attack energy in Koch
SPIRAL_ENERGY_TRANSFER_RATE = 2.0   # energy/sec from inner to outer

# ---------------------------------------------------------------------------
# v10_delta: Player-Driven Squad Management
# ---------------------------------------------------------------------------
FORMATION_MIN_VIABLE = 2            # below this, squad auto-dissolves
SQUAD_MAX_SIZE = 12                 # max units per squad
SQUAD_REINFORCE_RANGE = 120.0       # px — max distance for nearby free units
ARRIVAL_CHECK_RADIUS = 20.0         # px — "arrived at group destination"
ARRIVAL_CHECK_TIMEOUT = 10.0        # seconds before pending group expires
PENDING_GROUP_MIN = 3               # minimum units for group discovery check

# v10_beta: Extracted magic numbers → named constants
GARRISON_SPAWN_RADIUS = 40          # px — unit exit distance from building center
STANCE_GUARD_AGGRO_BONUS = 40       # px — extra aggro range in Guard stance
LONE_WOLF_ISOLATION_DIST = 80       # px — "alone" threshold for lone wolf trait
MORALE_CLUSTER_RADIUS = 200         # px — enemy cluster detection radius
ARROW_FLIGHT_DISTANCE_NORM = 180.0  # px — distance normalization for arrow flight time
WARLOCK_AOE_EDGE_FACTOR = 0.5       # damage falloff at AOE edge (1.0 center, this at edge)
HEALER_FOLLOW_RANGE_MULT = 0.7      # fraction of attack_range to chase wounded ally
REPATH_COOLDOWN = 1.5               # seconds — cooldown after A* fail before retrying
FORGE_WORKER_SPEED_BONUS = 0.3      # +30% forge speed per worker stationed
DOUBLE_CLICK_THRESHOLD = 400        # ms — max time between clicks for double-click
COMBAT_HEAT_DURATION = 30.0         # seconds — heat overlay decay time
WORKER_SPAWN_OFFSET = 50            # px — starting worker offset from town hall
WORKER_SPAWN_SPACING = 25           # px — spacing between starting workers
ENTITY_TOOLTIP_RADIUS = 30          # px — max distance to pick up entity tooltip

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

# v9/v10_5: Ballistic Archery — parabolic arc
ARROW_SPEED = 350               # kept for legacy compat; flight_time governs arc
ARROW_MAX_LIFETIME = 2.0        # seconds in flight before despawn
ARROW_HIT_RADIUS = 12           # collision detection radius (px)
ARROW_BASE_SPREAD = 0.18        # radians — max aim scatter for Recruit
ARROW_MIN_SPREAD = 0.03         # radians — best accuracy (Captain)
GROUND_ARROW_LIFETIME = 8.0     # seconds stuck arrows persist as visuals
GROUND_ARROW_MAX = 50           # oldest culled when exceeded
ARROW_ARC_HEIGHT = 40           # pixels of peak arc (elegant lob)
ARROW_FLIGHT_TIME = 0.8         # seconds to reach target
ARROW_TRAIL_LENGTH = 4          # afterimage ghost points
ARROW_LEAD_MIN_RANK = 2         # rank threshold for lead aiming
ARROW_LEAD_FACTOR_PER_RANK = 0.4  # lead accuracy per rank above threshold

# v9: Squad System (SQUAD_MAX_SIZE now in v10_delta block above)
SQUAD_FOLLOW_DIST = 60          # followers stay within this of leader (px)
SQUAD_REASSIGN_INTERVAL = 2.0   # seconds between full squad rebuilds

# v9: Enemy XP
ENEMY_XP_PER_HIT = 1
ENEMY_XP_KILL_BONUS = 2

# Enemy flee / veteran return
ENEMY_FLEE_HP_FRACTION = 0.20  # flee when below 20% HP
ENEMY_VETERAN_BONUS = 0.25    # +25% stats for returning veterans

# v9.1: Target Priority System
BUILDING_PRIORITY = {
    "town_hall": 10.0, "tower": 7.0, "barracks": 6.0, "refinery": 5.0,
    # v10.2: helper buildings (low priority)
    "goldmine_hut": 2.0, "lumber_camp": 2.0, "quarry_hut": 2.0,
    "iron_depot": 2.0, "scaffold": 1.5,
    # v10.2: production buildings (high value targets)
    "sawmill": 4.0, "goldmine": 4.0, "stoneworks": 4.0,
    "iron_works": 4.0, "forge": 5.0,
}
UNIT_PRIORITY = {
    "soldier": 4.0, "archer": 4.5, "worker": 1.0,
    "enemy_soldier": 4.0, "enemy_archer": 4.5,
    "enemy_elite": 6.0, "enemy_siege": 7.0,
    # v10_6: new enemy type priorities
    "enemy_sapper": 8.0,        # highest — beelines buildings, must intercept
    "enemy_healer": 9.0,        # must focus-fire to break sustain
    "enemy_raider": 7.0,        # economy threat
    "enemy_warlock": 6.0,       # ranged AOE danger
    "enemy_shieldbearer": 3.0,  # low — tanky, skip if possible
}
RUIN_PRIORITY_MULT = 0.15          # ruins are worth much less
DISTANCE_NORMALIZATION = 300.0     # px — at this distance priority halved
RANK_TARGETING_NOISE = {           # higher rank = less noise = smarter picks
    0: 0.50, 1: 0.30, 2: 0.15, 3: 0.05, 4: 0.00,
}
TOWER_LOW_HP_BONUS = 2.0           # finish off wounded targets
TOWER_LOW_HP_THRESHOLD = 0.30      # HP fraction for bonus
TOWER_HIGH_THREAT_TYPES = {"enemy_elite": 1.5, "enemy_siege": 1.8, "enemy_sapper": 2.0, "enemy_warlock": 1.3}
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


# ---------------------------------------------------------------------------
# v10_6: Stance System (replaces hold_ground boolean)
# ---------------------------------------------------------------------------
STANCE_AGGRESSIVE = 0    # Chase targets, auto-engage, break formation
STANCE_DEFENSIVE = 1     # Hold formation, weapon-range only
STANCE_GUARD = 2         # Protect building/area, return to post after engagement
STANCE_HUNT = 3          # Prioritize Sappers/Raiders, ignore frontline
STANCE_NAMES = ["Aggressive", "Defensive", "Guard", "Hunt"]
STANCE_COLORS = {0: (220, 50, 50), 1: (50, 140, 220), 2: (50, 200, 80), 3: (200, 160, 50)}

# ---------------------------------------------------------------------------
# v10_6: Fractal Formation System (self-similar mathematical formations)
# ---------------------------------------------------------------------------
FORMATION_POLAR_ROSE = 0       # r = cos(kθ) — soldiers on petals, archers in valleys
FORMATION_GOLDEN_SPIRAL = 1    # Vogel sunflower θ_n = n*2π/φ² — assault/flanking
FORMATION_SIERPINSKI = 2       # Recursive triangles — spread/anti-AOE
FORMATION_KOCH = 3             # Koch snowflake perimeter — guard/defensive ring
FORMATION_NAMES = ["Rose", "Spiral", "Sierpinski", "Koch"]
FORMATION_SLOT_ARRIVAL = 15        # px — snap threshold for reaching formation slot
FORMATION_REGROUP_DELAY = 0.5      # seconds after last combat before returning to slot
# (FORMATION_MOVE_SPEED_MULT removed in v10_beta — replaced by FORMATION_RETURN_SPEED)

# Formation spacing parameters (tunable)
FORMATION_ROSE_SPACING = 25.0      # px between polar rose slots
FORMATION_SPIRAL_C = 18.0          # Vogel sunflower spacing constant
FORMATION_SIERPINSKI_SPACING = 30.0  # base triangle side length
FORMATION_KOCH_RADIUS = 40.0      # snowflake perimeter radius

# ---------------------------------------------------------------------------
# v10_alpha: Formation Discovery & Harmonic Resonance
# ---------------------------------------------------------------------------
# Ideal ratio (majority:minority) for each formation — from fractal geometry
HARMONY_IDEAL_RATIOS = {
    FORMATION_POLAR_ROSE: 2.0,          # 2 petals → octave (2:1 frequency)
    FORMATION_GOLDEN_SPIRAL: 1.618,     # golden ratio φ → perfect fifth (3:2)
    FORMATION_SIERPINSKI: 3.0,          # 3 triangle vertices → major interval (3:1)
    FORMATION_KOCH: 1.0,                # 6-fold hexagonal → perfect unison (1:1)
}

# v10_epsilon: Musical interval labels for chord preview
HARMONY_LABELS = {
    FORMATION_POLAR_ROSE: "octave",
    FORMATION_GOLDEN_SPIRAL: "fifth",
    FORMATION_SIERPINSKI: "major",
    FORMATION_KOCH: "unison",
}

# Discovery requirements per formation
FORMATION_DISCOVERY = {
    FORMATION_POLAR_ROSE: {
        "min_size": 3, "min_veterans": 1,
        "any_ratio": True,  # Rose always discovered at min size (tutorial)
    },
    FORMATION_SIERPINSKI: {
        "min_size": 4, "min_veterans": 1,
        "any_ratio": False,
    },
    FORMATION_GOLDEN_SPIRAL: {
        "min_size": 5, "min_veterans": 1,
        "any_ratio": False,
    },
    FORMATION_KOCH: {
        "min_size": 6, "min_veterans": 1,
        "any_ratio": False,
    },
}

DISCOVERY_RATIO_TOLERANCE = 0.35  # 35% deviation from ideal ratio allowed for discovery

# Discovery notification text
DISCOVERY_NOTIFICATIONS = {
    FORMATION_POLAR_ROSE: "Formation Discovered: Rose -- The petals bloom with harmonic resonance!",
    FORMATION_GOLDEN_SPIRAL: "Formation Discovered: Spiral -- The golden ratio sings!",
    FORMATION_SIERPINSKI: "Formation Discovered: Sierpinski -- Triangular symmetry resonates!",
    FORMATION_KOCH: "Formation Discovered: Koch -- Hexagonal perfection achieved!",
}

# Discovery event timing
DISCOVERY_SLOWMO_DURATION = 1.5    # seconds of slow-motion
DISCOVERY_SLOWMO_FACTOR = 0.15     # game speed during slowmo (15%)
DISCOVERY_BANNER_DURATION = 3.0    # seconds the banner stays visible

# GUI hint text for undiscovered formations
DISCOVERY_HINTS = {
    FORMATION_POLAR_ROSE: "? · 3+ units",
    FORMATION_SIERPINSKI: "? · 4 at 3:1",
    FORMATION_GOLDEN_SPIRAL: "? · 5 at 3:2",
    FORMATION_KOCH: "? · 6 at 3:3",
}

# ---------------------------------------------------------------------------
# v10_8: Resonance Fields
# ---------------------------------------------------------------------------
RESONANCE_ROSE_DMG_PER_PETAL = 0.03    # +3% damage per petal
# (RESONANCE_SPIRAL_BASE_MISS, RESONANCE_SIERPINSKI_BASE removed v10_beta —
#  computed algorithmically in squads.py from 1/phi^d and (1/3)^d)
RESONANCE_KOCH_SLOW_PER_DEPTH = 0.15   # 15% slow per Koch depth
RESONANCE_KOCH_RADIUS_MULT = 1.5       # slow field = formation radius * mult
RESONANCE_MULTI_SQUAD_PENALTY = 0.30   # -30% per duplicate formation across squads
RESONANCE_DISSONANCE_RADIUS = 60.0     # px -- enemy anti-resonance nullification
RESONANCE_DISSONANCE_WAVE = 8          # wave threshold for dissonance spawning
RESONANCE_DISSONANCE_CHANCE = 0.20     # 20% of enemies after threshold
RESONANCE_HISTORY_WAVES = 3            # track last N waves for formation usage
WORKER_FLEE_COOLDOWN = 5.0             # seconds between flee->resume cycles

# Resonance visual colors (RGB)
RESONANCE_COLORS = {
    0: (220, 80, 40),     # Rose: red-orange
    1: (220, 190, 50),    # Spiral: gold-amber
    2: (40, 180, 220),    # Sierpinski: blue-cyan
    3: (50, 200, 80),     # Koch: green
}
RESONANCE_DISSONANCE_COLORS = {
    0: (110, 30, 15),     # anti-Rose: dark red
    1: (110, 95, 20),     # anti-Spiral: dark gold
    2: (15, 80, 110),     # anti-Sierpinski: dark cyan
    3: (20, 100, 35),     # anti-Koch: dark green
}

# (v10_6 Pressure System removed v10_beta — replaced by Incident Director FSM tension)

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
# v10.2: Economy Phase 2 — Helper & Production Buildings
# ---------------------------------------------------------------------------
# Drop-off building → resource type they accept
DROPOFF_BUILDING_TYPES = {
    "goldmine_hut": "gold", "lumber_camp": "wood",
    "quarry_hut": "stone", "iron_depot": "iron",
}

# Foreman skill → helper building unlock
FOREMAN_BUILDINGS = {
    "gold_miner": "goldmine_hut", "lumberjack": "lumber_camp",
    "stone_mason": "quarry_hut", "iron_miner": "iron_depot",
    "builder": "scaffold",
    # smelter has no building — upgrades existing refinery
}

# Helper → production building upgrade path
UPGRADE_PATH = {
    "lumber_camp": "sawmill", "goldmine_hut": "goldmine",
    "quarry_hut": "stoneworks", "iron_depot": "iron_works",
    "refinery": "forge",
}

# Production building resource generation (per tick)
PRODUCTION_RATES = {
    "sawmill":    {"resource": "wood",  "base_rate": 1.5, "worker_rate": 5.0, "max_workers": 3, "skill": "lumberjack"},
    "goldmine":   {"resource": "gold",  "base_rate": 1.0, "worker_rate": 4.0, "max_workers": 3, "skill": "gold_miner"},
    "stoneworks": {"resource": "stone", "base_rate": 1.0, "worker_rate": 4.0, "max_workers": 3, "skill": "stone_mason"},
    "iron_works": {"resource": "iron",  "base_rate": 0.8, "worker_rate": 3.5, "max_workers": 3, "skill": "iron_miner"},
    "forge":      {"resource": "steel", "base_rate": 0.0, "worker_rate": 0.0, "max_workers": 2, "skill": "smelter"},
}
PRODUCTION_TICK_INTERVAL = 5.0  # seconds between ticks

# Forge (replaces/upgrades refinery: Stone+Iron → Steel, faster)
FORGE_STONE_COST = 2
FORGE_IRON_COST = 1
FORGE_STEEL_YIELD = 1
FORGE_TIME = 4.0  # faster than refinery's 6s

# Scaffold aura (Builder Foreman)
SCAFFOLD_AURA_RANGE = 128  # pixels (4 tiles)
SCAFFOLD_SPEED_BONUS = 0.25  # +25% build/repair speed

# Smelter Foreman refinery boost
SMELTER_REFINERY_BONUS = 0.30  # +30% refine speed

# ---------------------------------------------------------------------------
# v10_2: Town Hall Garrison
# ---------------------------------------------------------------------------
GARRISON_MAX_WORKERS = 10              # max workers inside TH
GARRISON_ARMOR_PER_WORKER = 0.05       # 5% damage reduction per worker (caps at 50%)
GARRISON_DAMAGE_PER_WORKER = 3         # damage per garrisoned worker per tick
GARRISON_ATTACK_CD = 2.0               # seconds between garrison attacks
GARRISON_ATTACK_RANGE = 120            # range of stone-hurling
GARRISON_COST = {"wood": 20, "iron": 5, "stone": 10}  # cost per bell ring

# ---------------------------------------------------------------------------
# v10_1: Unit Trait System (procedural personalities)
# ---------------------------------------------------------------------------
TRAIT_POOL = {
    # trait_name: (rarity_weight, allowed_types)
    "brave":        (30, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite", "enemy_shieldbearer"}),
    "cowardly":     (30, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_raider"}),
    "aggressive":   (30, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite", "enemy_raider"}),
    "cautious":     (30, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_healer"}),
    "loyal":        (15, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_shieldbearer"}),
    "lone_wolf":    (15, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_raider"}),
    "sharpshooter": (8,  {"archer", "enemy_archer", "enemy_warlock"}),
    "berserker":    (8,  {"soldier", "enemy_soldier", "enemy_elite", "enemy_sapper"}),
    "inspiring":    (4,  {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite", "enemy_shieldbearer"}),
    "nimble":       (25, {"soldier", "archer", "enemy_soldier", "enemy_archer", "enemy_elite", "enemy_siege", "enemy_raider", "enemy_sapper"}),
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

# ---------------------------------------------------------------------------
# Command confirmation effects
# ---------------------------------------------------------------------------
CMD_RING_DURATION = 0.5        # seconds for move ring to expand and fade
CMD_RING_MAX_RADIUS = 18       # max expansion radius
CMD_RING_COLOR_MOVE = (100, 255, 100, 200)      # green ring for move
CMD_RING_COLOR_ATTACK = (255, 80, 80, 200)       # red ring for attack
CMD_RING_COLOR_GATHER = (255, 215, 0, 200)       # gold ring for gather
CMD_RING_COLOR_BUILD = (100, 180, 255, 200)       # blue ring for build
CMD_RING_COLOR_RALLY = (255, 160, 0, 200)         # orange for rally point

# ---------------------------------------------------------------------------
# Message log
# ---------------------------------------------------------------------------
MSG_LOG_MAX = 80               # max messages kept in buffer
MSG_LOG_VISIBLE = 8            # lines visible when expanded
MSG_LOG_FADE = 6.0             # seconds before old messages start fading
MSG_COL_INFO = (200, 200, 200)    # white — general info
MSG_COL_DISCOVERY = (255, 220, 80) # gold — formation/unlock discoveries
MSG_COL_ATTACK = (255, 80, 80)     # red — enemy attacks, unit deaths
MSG_COL_ECONOMY = (80, 200, 80)    # green — economy events
MSG_COL_COMMAND = (140, 180, 255)   # blue — player commands

# ---------------------------------------------------------------------------
# v10_alpha: Tooltip / Info Card System
# ---------------------------------------------------------------------------
TOOLTIP_HOVER_DELAY = 0.4  # seconds before tooltip appears
TOOLTIP_MAX_WIDTH = 240    # pixels
TOOLTIP_BG = (20, 20, 30, 230)
TOOLTIP_BORDER = (80, 80, 100)
TOOLTIP_PADDING = 6

# Tooltip text dictionary — keyed by element identifier
TOOLTIP_DATA = {
    # --- Resources ---
    "res_gold": "Gold — Primary currency.\nUsed for buildings, units, and upgrades.",
    "res_wood": "Wood — Building material.\nGathered from trees. Used for structures.",
    "res_iron": "Iron — Advanced material.\nMined from ore. Refined into Steel.",
    "res_steel": "Steel — Refined metal.\nForged from Iron + Stone. Needed for military.",
    "res_stone": "Stone — Construction material.\nQuarried from deposits. Used for towers & forges.",
    # --- Population ---
    "pop": "Population — Total living units.\nIncludes workers and military.",
    # --- Tension ---
    "tension_bar": "Tension — Threat level rising over time.\nHigher tension brings stronger incidents.",
    "incident_counter": "Incidents — Attacks survived / total required.\nSurvive all incidents to win.",
    # --- Military Ranks ---
    "rank_0": "Recruit — Fresh conscript.\nNo bonuses. Gains XP from combat.",
    "rank_1": "Veteran — Seasoned fighter.\n+8% HP, +6% ATK, +5 range.\nUnlocks squad formation.",
    "rank_2": "Corporal — Proven warrior.\n+16% HP, +12% ATK, +10 range.\nBetter target selection.",
    "rank_3": "Sergeant — Squad leader.\n+26% HP, +20% ATK, +18 range.\nBoosts nearby morale.",
    "rank_4": "Captain — Elite commander.\n+40% HP, +30% ATK, +25 range.\nPerfect target priority.",
    # --- Worker Ranks ---
    "wrank_Novice": "Novice — Learning the trade.\nNo speed bonus yet.",
    "wrank_Foreman": "Foreman — Skilled worker.\n+15% gather/build speed.\nUnlocks helper buildings.",
    "wrank_Master": "Master — Expert craftsman.\n+30% gather/build speed.",
    # --- Stances ---
    "stance_Aggressive": "Aggressive — Chase and engage.\nUnits pursue enemies beyond weapon range.\nHigher aggro range, breaks formation.",
    "stance_Defensive": "Defensive — Hold position.\nOnly attacks within weapon range.\nMaintains formation discipline.",
    "stance_Guard": "Guard — Protect an area.\nEngages nearby threats, returns to post.\nIdeal for base defense.",
    "stance_Hunt": "Hunt — Priority targeting.\nFocuses Sappers and Raiders first.\nIgnores frontline soldiers.",
    # --- Formations ---
    "fmt_Rose": "Rose Formation (Polar Rose curve)\nIdeal ratio: 2:1 (octave harmony)\nAura: +DMG% per petal depth.\nBest for raw damage output.",
    "fmt_Spiral": "Spiral Formation (Golden Spiral)\nIdeal ratio: 3:2 (perfect fifth)\nAura: Evasion chance per depth.\nAssault/flanking formation.",
    "fmt_Sierpinski": "Sierpinski Formation (Recursive triangles)\nIdeal ratio: 3:1 (major interval)\nAura: AOE damage reduction.\nSpread anti-AOE formation.",
    "fmt_Koch": "Koch Formation (Koch snowflake)\nIdeal ratio: 3:3 (perfect unison)\nAura: Slows nearby enemies.\nDefensive perimeter guard.",
    # --- Harmony ---
    "harmony": "Harmony Quality — How well the squad's\nunit mix matches the formation's ideal ratio.\nHigher harmony = stronger resonance aura.",
    # --- Traits ---
    "trait_brave": "Brave — 50% harder to rout.\nStands firm under pressure.",
    "trait_cowardly": "Cowardly — 30% easier to rout.\nFlees sooner when outnumbered.",
    "trait_aggressive": "Aggressive — +40% aggro range.\nEngages targets more eagerly.\nSlightly less precise targeting.",
    "trait_cautious": "Cautious — -30% aggro range.\nPrefers wounded targets (+30% low-HP bonus).",
    "trait_loyal": "Loyal — 2x cohesion force.\nStays close to squad leader.",
    "trait_lone_wolf": "Lone Wolf — +15% ATK when alone.\nFights better without nearby allies.",
    "trait_sharpshooter": "Sharpshooter — 40% less arrow spread.\nDeadly accurate at range.",
    "trait_berserker": "Berserker — +25% ATK below 50% HP.\nGrows stronger when wounded.",
    "trait_inspiring": "Inspiring — Morale leader aura.\nNearby allies resist fleeing.",
    "trait_nimble": "Nimble — +15% speed on rough terrain.\nMoves faster through trees and hills.",
    # --- Buildings ---
    "bld_town_hall": "Tree of Life — Main structure.\nTrains Gatherers. Heals nearby units.\nGarrison workers for defense.",
    "bld_barracks": "War Nexus — Military hub.\nTrains Wardens and Rangers.\nUnlocks Sentinel construction.",
    "bld_refinery": "Crucible — Iron smelter.\nConverts 2 Iron → 1 Steel.\nUpgrades to Fractal Forge.",
    "bld_tower": "Sentinel — Defensive tower.\nFires cannonballs at enemies.\nUpgrades to explosive AoE.",
    "bld_goldmine_hut": "Gold Node — Drop-off for gold.\nReduces worker travel time.\nUnlocked by Gold Miner Foreman.",
    "bld_lumber_camp": "Grove Tap — Drop-off for wood.\nReduces worker travel time.\nUnlocked by Lumberjack Foreman.",
    "bld_quarry_hut": "Stone Node — Drop-off for stone.\nReduces worker travel time.\nUnlocked by Stone Mason Foreman.",
    "bld_iron_depot": "Iron Node — Drop-off for iron.\nReduces worker travel time.\nUnlocked by Iron Miner Foreman.",
    "bld_scaffold": "Lattice — Builder's scaffold.\n+25% build/repair speed nearby.\nUnlocked by Builder Foreman.",
    "bld_sawmill": "Timber Spire — Wood production.\nPassive wood + worker-boosted output.\nUpgraded from Grove Tap.",
    "bld_goldmine": "Gold Spire — Gold production.\nPassive gold + worker-boosted output.\nUpgraded from Gold Node.",
    "bld_stoneworks": "Stone Spire — Stone production.\nPassive stone + worker-boosted output.\nUpgraded from Stone Node.",
    "bld_iron_works": "Iron Spire — Iron production.\nPassive iron + worker-boosted output.\nUpgraded from Iron Node.",
    "bld_forge": "Fractal Forge — Advanced smelter.\n2 Stone + 1 Iron → 1 Steel (faster).\nUpgraded from Crucible.",
    # --- Unit Types ---
    "unit_worker": "Gatherer — Economic backbone.\nGathers resources, builds, repairs.\nGains skill XP per resource type.",
    "unit_soldier": "Warden — Melee fighter.\n140 HP, 14 ATK, short range.\nTough frontline with high HP.",
    "unit_archer": "Ranger — Ranged attacker.\n75 HP, 9 ATK, long range.\nBallistic arrows with rank accuracy.",
    # --- Enemy Types ---
    "enemy_enemy_soldier": "Dark Warden — Enemy melee.\nStandard frontline attacker.",
    "enemy_enemy_archer": "Shadow Ranger — Enemy ranged.\nWeaker arrows but keeps distance.",
    "enemy_enemy_siege": "Siege Golem — Building destroyer.\n2x damage to buildings. Slow but tough.",
    "enemy_enemy_elite": "Void Knight — Elite warrior.\nFast, strong, hard to kill.",
    "enemy_enemy_sapper": "Blight Sapper — Suicide bomber.\n3x building damage. Self-destructs on contact.",
    "enemy_enemy_shieldbearer": "Iron Bulwark — Armored tank.\n50% frontal armor. Flank to bypass!",
    "enemy_enemy_healer": "Plague Mender — Enemy healer.\nHeals 5 HP/s to nearby allies.",
    "enemy_enemy_raider": "Rift Raider — Economy hunter.\nTargets workers and resource buildings.",
    "enemy_enemy_warlock": "Chaos Warlock — AOE caster.\nSplash damage in 30px radius.",
    # --- Global Buttons ---
    "btn_Defend Base": "Rally all military to defend\nthe nearest Town Hall.",
    "btn_Hunt Enemies": "Send all military to attack-move\ntoward the nearest enemy threat.",
    "btn_Town Bell": "Ring the bell — all idle workers\ngarrison inside the Town Hall.",
    "btn_Resume Work": "Ungarrison workers and send them\nback to their previous tasks.",
    # --- Gather ---
    "btn_Wood": "Send selected workers to gather\nwood from the nearest trees.",
    "btn_Gold": "Send selected workers to gather\ngold from the nearest deposit.",
    "btn_Iron": "Send selected workers to gather\niron from the nearest ore vein.",
    "btn_Stone": "Send selected workers to gather\nstone from the nearest quarry.",
}
