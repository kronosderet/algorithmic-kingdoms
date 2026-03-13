# Game Design Document — Algorithmic Kingdoms v10_4 (Current)

> Reflects the actual implemented state of all systems.
> Last updated: 2026-03-13

---

## 1. Overview

**Title:** Algorithmic Kingdoms
**Tagline:** Gather, Build, Survive!
**Engine:** Python 3.10 + Pygame 2.6.1, NumPy
**Distribution:** PyInstaller single-file .exe (console hidden)
**Resolution:** 1280 x 720 @ 60 FPS
**Art Style:** Zero-asset — all visuals are algorithmic (polar roses, L-systems, golden spirals, Mandelbrot menus)

**Core Loop:** Gather resources, construct buildings, train units, and survive escalating enemy waves. Workers gain skill XP in 6 specializations with 3 ranks each. Combat units gain XP through 5 military ranks, self-organize into squads, and develop procedural personality traits. Archers fire ballistic arrows with rank-scaled accuracy. All units use utility-scored targeting with live retargeting and threat response. Enemy hordes check local morale and flee when outnumbered. Global command buttons provide AoE2-style macro controls. Town Hall garrisons workers for damage reduction and counter-attack.

**Version History:**
- v9.3: Ballistic archery, XP ranks, squads, morale, formations, retargeting, weighted terrain
- v10: Stone resource, worker skill XP (6 tracks, 3 ranks), tower cannon overhaul (ballistic + explosive)
- v10_1: Procedural unit traits (10 traits), control groups (Ctrl+0-9), enemy inspection panel, combat heat minimap
- v10_2: Town Hall garrison (workers barricade for armor + stone-hurling), hold ground stance, attack-move
- v10_3: Water terrain removed (reserved for terrain overhaul), visual pip cleanup
- v10_4: Performance — spatial grid, map caching, insertion sort, minimap dirty flags, player death logging

---

## 2. Difficulty System

Three selectable profiles from the main menu (hotkeys 1/2/3). Each profile tunes starting resources, wave timing, scaling, and rewards.

| Parameter | Easy | Medium | Hard |
|---|---|---|---|
| Starting Gold / Wood | 300 / 150 | 200 / 100 | 180 / 100 |
| Starting Workers | 4 | 3 | 3 |
| First Wave (seconds) | 360 | 330 | 300 |
| Wave Interval (seconds) | 120 | 90 | 80 |
| Max Waves | 15 | 20 | 25 |
| Wave Count: base + scale×√n | 4 + 3√n | 4 + 4√n | 5 + 5√n |
| HP Scale / Wave | +5% | +7% | +8% |
| ATK Scale / Wave | +3% | +4% | +5% |
| Archers Unlock (wave) | 4 | 3 | 2 |
| Siege Unlock (wave) | 8 | 7 | 5 |
| Elite Unlock (wave) | 18 | 15 | 12 |
| Multi-dir Waves (wave) | 14 | 12 | 8 |
| 3-dir Waves (wave) | 20 | 18 | 14 |
| Kill Bounty Base | 5 | 4 | 2 |
| Wave Bonus Gold / Wood / Steel | 30/15/3 | 25/15/3 | 15/8/2 |

**Wave Size Formula:** `count = wave_base + wave_scale * sqrt(wave_number)`
**Kill Bounty Formula:** `bounty = kill_bounty_base + wave_number` (gold per kill)

---

## 3. Map & Terrain

- **Grid:** 128 × 128 tiles, 32px per tile
- **World Size:** 4096 × 4096 pixels

| ID | Terrain | Color (RGB) | Passable | Buildable | Move Cost | Notes |
|---|---|---|---|---|---|---|
| 0 | Grass | (40, 118, 74) | Yes | Yes | 1.0x | Default terrain |
| 1 | Water | — | — | — | — | **Reserved** (removed in v10_3, will return in terrain overhaul) |
| 2 | Tree | (20, 100, 20) | Yes | No | 2.0x | Harvestable (wood) |
| 3 | Gold | (218, 165, 32) | Yes | No | 1.8x | Harvestable (gold) |
| 4 | Iron | (140, 140, 155) | Yes | No | 1.8x | Harvestable (iron) |
| 5 | Shallow Water | — | — | — | — | **Reserved** |
| 6 | Stone | (160, 150, 130) | Yes | No | 1.8x | Harvestable (stone) — **v10 new** |

**Passability:**
- `is_passable(c, r)` — True for any terrain in TERRAIN_MOVE_COST. Out-of-bounds returns -1 (impassable).
- `is_walkable(c, r)` — True only for grass. Used for building placement.
- Units can walk through trees, gold, iron, stone — but at reduced speed.
- Harvesting depletes tiles to grass, creating cleared paths.

**Procedural Generation:**
- 15-22 tree forests (random walk, 8-30 tiles each)
- 5-8 gold deposits (3-6 tiles each)
- 4-7 iron deposits (3-6 tiles each)
- 3-5 stone deposits (4-8 tiles each) — **v10 new**
- 3 guaranteed tree clusters near start (7-12 tiles, 6-15 tiles each)
- 2 guaranteed gold deposits near start (8-14 tiles, 3-5 tiles each)
- 9×9 clear zone around map center for starting base

**Resource Capacities:**

| Resource | Capacity | Gather Time | Amount/Trip |
|---|---|---|---|
| Tree (wood) | 50 | 2.0s | 10 |
| Gold | 80 | 3.0s | 10 |
| Iron | 60 | 3.0s | 15 |
| Stone | 70 | 3.5s | 10 |

---

## 4. Resources

Five resource types managed by `ResourceManager`:

| Resource | Icon Color | Primary Source | Secondary Source |
|---|---|---|---|
| Gold | (255, 215, 0) | Gold tiles | Kill bounty, wave bonus |
| Wood | (34, 180, 34) | Tree tiles | Wave bonus |
| Iron | (170, 170, 185) | Iron tiles | — |
| Steel | (100, 160, 220) | Refinery (2 iron → 1 steel) | Wave bonus |
| Stone | (160, 150, 130) | Stone tiles | — |

Iron → Steel pipeline via Refinery. Stone is used for towers and garrison bell cost.

---

## 5. Buildings

All buildings are player-side only. Built by workers through right-click assignment.

### 5.1 Building Stats

| Building | Gold | Wood | Iron | Steel | Stone | HP | Build Time | Size |
|---|---|---|---|---|---|---|---|---|
| Town Hall | 200 | 120 | 0 | 0 | 0 | 500 | 30s | 2×2 |
| Barracks | 120 | 80 | 0 | 0 | 0 | 400 | 18s | 2×2 |
| Refinery | 80 | 60 | 30 | 0 | 0 | 300 | 22s | 2×2 |
| Tower | 30 | 0 | 15 | 0 | 35 | 220 | 18s | 1×1 |

### 5.2 Building Functionality

**Town Hall:**
- Trains workers (Q key, 50g, 8s)
- Resource drop-off point
- Passive healing aura: 2 HP/s within 192px (6 tiles)
- **v10_2: Garrison** — workers barricade inside (see Section 6.6)

**Barracks:**
- Trains soldiers (W key, 75g 8s, 13s train)
- Trains archers (E key, 55g 25w 4s, 11s train)
- Training queue (FIFO)

**Refinery:**
- Auto-refines: 2 iron → 1 steel every 6s
- Operates while iron is available

**Tower (v10c Cannon Overhaul):**
- **Level 1 — Cannon Tower:** Fires ballistic cannonballs (not homing)
  - 45 damage, 3.5s CD, 250 px/s speed, 220px range, 0.10 rad spread
  - Hit radius 16px, 2.5s max lifetime
- **Level 2 — Explosive Cannon:** Upgrade costs 15 steel, 12s worker build time
  - 50 direct damage + 35 AoE splash in 60px radius
  - Same speed/range/CD as Level 1
- Target scoring: threat-type bonuses (Elite 1.5×, Siege 1.8×), low-HP finishing (2.0× below 30%)

### 5.3 Building Ruin System

When a completed player building reaches 0 HP:
- Becomes a ruin (`ruined = True`), retains residual HP
- Training/refining halted, rendered at 1/3 brightness
- Enemies deprioritize ruins (15% of base priority)
- Garrisoned workers ejected on ruin transition
- Right-click workers to rebuild at 40% of original cost

---

## 6. Units

### 6.1 Player Units

| Unit | Gold | Wood | Steel | HP | Speed | ATK | Range | CD | Train |
|---|---|---|---|---|---|---|---|---|---|
| Worker | 50 | 0 | 0 | 50 | 80 | 4 | 40 | 1.0s | 8s |
| Soldier | 75 | 0 | 8 | 140 | 70 | 14 | 40 | 1.0s | 13s |
| Archer | 55 | 25 | 4 | 75 | 75 | 9 | 170 | 1.4s | 11s |

### 6.2 Enemy Units (Base Stats, Before Wave Scaling)

| Unit | HP | Speed | ATK | Range | CD | Special |
|---|---|---|---|---|---|---|
| Enemy Soldier | 100 | 55 | 12 | 40 | 1.2s | — |
| Enemy Archer | 60 | 50 | 6 | 140 | 1.8s | — |
| Enemy Siege | 200 | 35 | 20 | 40 | 3.0s | 2× damage vs buildings |
| Enemy Elite | 160 | 60 | 18 | 40 | 1.0s | Fast, high DPS |

**Wave Scaling:** `hp = base × (1 + hp_scale × wave#)`, `atk = base × (1 + atk_scale × wave#)`

### 6.3 Unit States

| State | Description |
|---|---|
| `idle` | No task. Combat units auto-aggro within range+64px |
| `moving` | Following A* path |
| `gathering` | Worker harvesting resource tile |
| `returning` | Worker carrying resources to TH |
| `building` | Worker constructing/rebuilding |
| `attacking` | Engaged with target, retargets every 1.5s |
| `repairing` | Worker repairing damaged building |
| `fleeing` | Worker/enemy fleeing threats |
| `garrisoned` | **v10_2:** Worker inside Town Hall, hidden from rendering |

### 6.4 Worker Behaviors

**Gathering:** Walk to tile → harvest over time → carry to nearest TH → auto-resume. Remembers last gather type for resume after interruption.

**Building:** Right-click unbuilt/ruined building. Must be within 2.5 tiles. Multiple workers can build simultaneously.

**Repairing:** Right-click damaged building. 15 HP/s per worker. Costs 15% of building's full cost.

**Fleeing:** Triggers when enemy within 160px. Saves task state, paths 6 tiles away, resumes after 2.0s safety.

### 6.5 Worker Skill XP System (v10)

Workers gain XP in the specific skill they are actively using. Six skill tracks:

| Skill | Activity | Color |
|---|---|---|
| Lumberjack | Harvesting trees | Green |
| Gold Miner | Harvesting gold | Gold |
| Iron Miner | Harvesting iron | Silver |
| Stone Mason | Harvesting stone | Sandstone |
| Builder | Constructing/repairing | Cyan |
| Smelter | (Future: refinery boost) | Steel Blue |

**Three ranks per skill:**

| Rank | Title | XP Threshold | Speed Bonus |
|---|---|---|---|
| 0 | Novice | 0 | +0% |
| 1 | Foreman | 80 | +15% |
| 2 | Master | 200 | +30% |

XP is per-skill, not global. A Gold Miner Foreman switching to trees works at Novice speed. Builder XP accrues at 0.5 XP/s during build/repair work.

### 6.6 Town Hall Garrison (v10_2)

Workers can be garrisoned inside the Town Hall for defense:

| Parameter | Value |
|---|---|
| Max workers | 10 |
| Armor per worker | 5% damage reduction (caps at 50%) |
| Stone-hurling damage | 3 per worker per tick |
| Attack cooldown | 2.0s |
| Attack range | 120px |
| Bell cost | 20 wood, 5 iron, 10 stone |

**Mechanics:**
- Town Bell global button recalls all workers into nearest TH (costs resources)
- Garrisoned workers are hidden from rendering and skip all behavior updates
- Workers auto-deposit carried resources on entering garrison
- TH damage reduced by `5% × num_workers` (max 50%)
- Garrisoned workers collectively hurl stones at nearest enemy within 120px
- Workers ejected on TH ruin transition
- Resume Work global button ungarisons all and resumes gathering

### 6.7 Unit Separation & Squad Cohesion

- Separation distance: 20px, force: 50 px/s (prevents stacking)
- Squad cohesion: 35 px/s pull toward leader when >30px away
- **v10_4:** Uses spatial grid for O(1) neighbor queries instead of O(n²) all-pairs

### 6.8 Formation Hints (v9.2)

Soldiers pushed forward (+30px), archers pushed back (-35px) relative to squad front. Lower ranks pushed further forward (+5px per rank difference). Force: 25 px/s.

---

## 7. Procedural Unit Traits (v10_1)

Every unit rolls 0-2 traits at creation (40% zero, 45% one, 15% two). Traits are cached multipliers — zero per-frame computation cost.

| Trait | Rarity | Effect | Allowed Types |
|---|---|---|---|
| Brave | Common | +50% morale resistance | Soldier, Archer, Enemies |
| Cowardly | Common | -30% morale resistance | Soldier, Archer, Enemies |
| Aggressive | Common | +40% aggro range, +30% targeting noise | Soldier, Archer, Enemies |
| Cautious | Common | -30% aggro range, +30% low-HP bonus | Soldier, Archer, Enemies |
| Loyal | Uncommon | 2× squad cohesion | Soldier, Archer, Enemies |
| Lone Wolf | Uncommon | +15% ATK when alone | Soldier, Archer, Enemies |
| Sharpshooter | Rare | -40% arrow spread | Archer only |
| Berserker | Rare | +25% ATK below 50% HP | Soldier only |
| Inspiring | Very Rare | Morale leader at any rank | Soldier, Archer, Enemies |
| Nimble | Common | +15% terrain speed bonus | All combat |

**Conflicts (mutually exclusive):** Brave/Cowardly, Aggressive/Cautious, Loyal/Lone Wolf

**Visual:** Traits displayed in selection panel as colored text. In-game trait pips removed in v10_3 (pending visual overhaul).

---

## 8. XP & Military Rank System

### 8.1 XP Acquisition

| Event | Player XP | Enemy XP |
|---|---|---|
| Dealing a hit | +1 | +1 |
| Killing a target | +3 bonus | +2 bonus |

Workers do NOT gain combat XP.

### 8.2 Military Ranks

| Rank | Name | XP | HP Mult | ATK Mult | Range+ | Accuracy+ |
|---|---|---|---|---|---|---|
| 0 | Recruit | 0 | 1.00× | 1.00× | +0 | +0.00 |
| 1 | Veteran | 10 | 1.08× | 1.06× | +5 | +0.03 |
| 2 | Corporal | 30 | 1.16× | 1.12× | +10 | +0.06 |
| 3 | Sergeant | 70 | 1.26× | 1.20× | +18 | +0.10 |
| 4 | Captain | 140 | 1.40× | 1.30× | +25 | +0.15 |

HP ratio preserved on rank-up. Rank colors: Gray → Bronze → Silver → Gold → Diamond Blue.

---

## 9. Ballistic Archery

Archers fire real projectiles with accuracy spread. Towers fire ballistic cannonballs (also non-homing as of v10c).

| Property | Arrows | Cannonballs |
|---|---|---|
| Speed | 350 px/s | 250 px/s |
| Max flight | 2.0s | 2.5s |
| Hit radius | 12px | 16px |
| Base spread | 0.18 rad (Recruit) | 0.10 rad |
| Min spread | 0.03 rad (Captain) | — |

**Arrow lifecycle:** Fire → straight-line flight with spread → hit detection (12px) → damage + XP → or miss → ground arrow (8s persist, max 50).

---

## 10. Squad System

- Reassignment every 2.0s. Leader: rank ≥ 1. Max size: 6.
- Followers assist leader's target or follow leader when idle.
- Enemy squads also form — returning veterans become natural leaders.

---

## 11. Target Priority System

**Score = base_priority × distance_falloff × hp_mod × engagement_stick × threat_mod × noise**

Key modifiers:
- Distance normalization: 300px (score halved at this distance)
- Low HP bonus: 1.3× below 40% HP
- Engagement stickiness: 1.15× for current target
- Threat bonus: 2.5× for "who's attacking me"
- Rank noise: ±50% (Recruit) to 0% (Captain)
- Ruin depriority: 0.15×

**Retargeting:** Every 1.5s during combat. New target must score 20% better to switch.

---

## 12. Enemy Horde Morale

- Check interval: 1.0s per unit (staggered)
- Scan radius: 160px — count player vs enemy forces
- Flee ratio: 3.0 × rank resistance (Recruit 1.0, Veteran 1.3, Corporal 1.6, Sergeant+ 999)
- Leader aura: Sergeant+ within 120px suppresses flee entirely
- Flee behavior: regroup with allied cluster OR escape to map edge with XP preserved
- Veterans return next wave with +25% stats + accumulated XP/ranks

---

## 13. Enemy AI

### 13.1 Wave Spawning
Edges of map, multi-directional after threshold wave. Spawn seeks walkable tile (30 retries).

### 13.2 Adaptive Composition
Base: Elite 10%, Siege 15%, Archer 30%, Soldier remainder.
Adaptations: +siege vs many towers, +elite vs archer-heavy army, +enemy archers vs soldier-heavy.

### 13.3 Enemy Flee & Veteran Return
HP-based (below 20% + outnumbered check) and morale-based. Escaped enemies return next wave as veterans.

---

## 14. Global Command System (v10_2)

When no unit or building is selected, 4 macro buttons appear:

| Button | Action |
|---|---|
| **Defend Base** | All combat units move to area between TH and nearest tower, enable hold ground |
| **Hunt Enemies** | All combat units attack-move to nearest enemy, or map center if none visible |
| **Town Bell** | Pay 20w/5i/10s, all workers garrison in nearest TH |
| **Resume Work** | Ungarrison all workers, resume previous gathering task |

### 14.1 Unit Command Buttons (v10_2)

When soldiers/archers selected, command buttons appear:
- **Attack Move** — enter attack-move mode (click to set destination, engage enemies en route)
- **Hold Ground** — stop and fight in range, never chase (toggleable)

---

## 15. Pathfinding

**Algorithm:** A* with 8-directional movement, weighted terrain costs.

| Terrain | Move Cost |
|---|---|
| Grass | 1.0× |
| Tree | 2.0× |
| Gold / Iron / Stone | 1.8× |

- Heuristic: Chebyshev distance
- Node limit: 4000
- Building tiles blocked. Building's own tiles excluded for workers building it.
- Movement speed also divided by terrain cost: `effective_speed = base_speed / cost`
- Clearing trees via harvesting opens fast-travel paths

---

## 16. Camera & Input

**Camera:** WASD + edge scroll (15px margin), 400 px/s. Zoom 0.4×–2.0× via mousewheel. Space centers on selection.

**Selection:** Click (20px radius), box-drag, ESC deselect. Garrisoned units excluded from selection.

**Control Groups (v10_1):** Ctrl+0-9 assign, 0-9 recall, double-tap centers camera.

**Right-Click Context:**

| Target | Worker | Combat Unit |
|---|---|---|
| Enemy | Attack | Attack |
| Resource tile | Gather | Move |
| Unbuilt building | Build | Move |
| Ruined building | Rebuild (40%) | Move |
| Damaged building | Repair | Move |
| Empty ground | Move | Move |

**Hotkeys:** 1-4 place buildings (worker), Q/W/E train units (building), U upgrade tower, F10 surrender.

---

## 17. User Interface

### 17.1 Layout

| Region | Position | Content |
|---|---|---|
| Top Bar | y=0, h=40 | Resources (icons+values), population, wave timer bar, enemy estimate |
| Game Area | y=40, h=550 | Map, units, buildings, arrows, cannonballs, explosions |
| Bottom Panel | y=590, h=130 | Selection info, action buttons, global commands |
| Minimap | Upper-right, 160×160 | Terrain, units, buildings, camera rect, combat heat |

### 17.2 Bottom Panel States

- **Nothing selected, no enemy inspected:** 4 global command buttons + help text
- **Enemy inspected (v10_2):** Read-only panel with enemy type, rank, traits, HP, stats, state
- **Building selected:** Icon, name, HP bar, status, action buttons (train/upgrade)
- **Single unit:** Icon, name+rank, traits, HP bar, stats+state, XP bar, skill info (worker), build/command buttons
- **Multi-unit:** Count by type with rank distribution, aggregate HP, build buttons (all workers) or command buttons (all combat)

### 17.3 Minimap

- 160×160px, terrain base rebuilt on dirty flag (v10_4, replaces 2s timer)
- Player buildings: blue (ruins: dark gray)
- Player units: cyan dots
- Enemy units: red dots
- Camera viewport: white rectangle
- Combat heat overlay: red glow at recent combat locations
- Click to jump camera

---

## 18. Visual Rendering

### 18.1 Algorithmic Unit Shapes (v10f)
- **Workers:** Hexagonal shape with resource-colored carry indicator
- **Soldiers:** Polar rose pattern with shield element
- **Archers:** Fibonacci spiral with bow element
- **Siege:** Large octagonal shape
- **Elite:** Star pattern

All drawn with `pygame.draw` — no sprite assets. Visual pips (rank/trait indicators) removed in v10_3, pending visual overhaul.

### 18.2 Map Rendering (v10_4)
- **Terrain surface cached** — only rebuilt when tiles change (gather/build) or camera zoom changes
- Dirty flag system: `_map_dirty` for tile changes, `_minimap_dirty` for minimap
- Tree/gold/iron/stone decorations drawn on cached surface
- Grid lines at zoom ≥ 0.7×

### 18.3 Unit Rendering (v10_4)
- **Insertion sort** on pre-maintained `_sorted_units` list (O(n) for nearly-sorted data)
- Garrisoned units skipped
- Health bars above damaged units
- Selection circles for selected units

---

## 19. Performance Systems (v10_4)

| System | Before | After |
|---|---|---|
| Unit separation | O(n²) all-pairs | O(n) spatial grid queries |
| Idle aggro scan | O(n×m) all enemies | O(k) grid radius query |
| Map rendering | Full redraw every frame | Cached surface + dirty flag |
| Unit depth sort | `list.sort()` O(n log n) | Insertion sort O(n) |
| Minimap rebuild | Every 2.0s timer | On dirty flag only |
| Arrow management | Two-pass update+partition | Single-pass partition |

**Spatial Grid (spatial_grid.py):**
- Cell size: 80px
- `rebuild(units)` — O(n) clear + insert per frame
- `query_radius(x, y, r)` — returns units within radius, checking only relevant cells
- `query_nearby(x, y)` — 3×3 cell neighborhood
- Two grids maintained: `player_grid`, `enemy_grid`

---

## 20. Event Logging

CSV-based logging to `logs/` directory. Events:

| Event Type | Details Logged |
|---|---|
| WAVE_START | Wave number, enemy count, composition |
| WAVE_CLEARED | Wave number, time taken |
| UNIT_KILLED | Killer type, killed type, killer rank, bounty |
| PLAYER_UNIT_LOST | Lost unit type, killer type, lost rank, lost XP |
| BUILDING_RUINED | Building type, damage source |
| BUILDING_DESTROYED | Building type, damage source |
| BUILDING_PLACED | Building type |
| BUILDING_COMPLETE | Building type |
| TRAINING_STARTED | Unit type |
| RESOURCE_DEPOSIT | Resource type, amount |
| RANK_UP | Unit type, new rank, owner |
| WORKER_RANK_UP | Worker skill, new rank |
| TOWER_UPGRADE | Tower level |
| ENEMY_ESCAPED | Enemy type, XP carried |
| SURRENDER | — |
| GAME_SUMMARY | Outcome, kills, losses, bounty, buildings, resources |

---

## 21. Game State & Win Conditions

**Victory:** All waves completed AND all enemy units dead.
**Defeat:** All player buildings destroyed (including ruins — all `alive = False`).
**Surrender:** F10 key.

---

## 22. Architecture

```
rts/
  main.py          — Entry point, pygame init, menu → game
  menu.py          — Main menu with algorithmic art background
  game.py          — Game class: update/render loop, input, global commands
  constants.py     — All constants, difficulty profiles, unit/building defs, trait system
  utils.py         — dist, clamp, tile_center, pos_to_tile, draw_text, ruin_rebuild_cost
  game_map.py      — Procedural terrain gen, harvest, passability
  camera.py        — Pan/zoom/clamp/transforms
  resources.py     — ResourceManager (gold, wood, iron, steel, stone)
  entities.py      — Entity, Unit, Building, Arrow, Projectile + combat helper
  squads.py        — SquadManager (rank-based leadership)
  enemy_ai.py      — Wave spawning, adaptive composition, veteran return
  gui.py           — HUD: top bar, bottom panel, buttons, enemy inspection
  pathfinding.py   — A* with weighted terrain (4000 node limit)
  spatial_grid.py  — O(1) spatial neighbor queries for unit interactions
  event_logger.py  — CSV event recording + game summary
```

**Entity Hierarchy:**
```
Entity (eid, x, y, hp, max_hp, owner, alive, last_attacker)
  ├── Unit (state machine, commands, combat, gathering, building,
  │         fleeing, XP/rank, traits, arrow firing, squad behavior,
  │         target scoring, retargeting, morale, formations,
  │         worker skills, garrison, hold ground, attack-move)
  └── Building (construction, training queue, refinery, tower cannon,
                ruin system, garrison, rally point)
```
