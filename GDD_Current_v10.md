# Game Design Document — Resonance v10_epsilon4 (Current)

> Reflects the actual implemented state of all systems.
> Last updated: 2026-03-15

---

## 1. Overview

**Title:** Resonance
**Tagline:** Gather, Build, Survive!
**Engine:** Python 3.13 + Pygame 2.6.1, NumPy
**Distribution:** PyInstaller single-file .exe (console hidden)
**Resolution:** 1280 x 720 @ 60 FPS
**Art Style:** Zero-asset — all visuals are algorithmic (polar roses, L-systems, golden spirals, Mandelbrot menus, fractal font, Koch borders)

**Core Loop:** Gather resources, construct buildings (including helper drop-offs and production Spires), train units, and survive escalating enemy incidents driven by a dramaturgic tension engine. Gatherers gain skill XP in 6 specializations with 3 ranks each — Foreman rank unlocks helper buildings, Master unlocks production buildings. Combat units gain XP through 5 military ranks, form player-driven squads with fractal formations, and develop procedural personality traits. Units move via physics-based velocity/acceleration with per-unit energy pools. Rangers fire ballistic arrows with rank-scaled accuracy. Sentinels project Koch-snowflake resonance fields that damage nearby enemies. Formations grant harmonic resonance bonuses based on composition quality. All units use utility-scored targeting with live retargeting and threat response. Enemy hordes check local morale and flee when outnumbered. Global command buttons provide AoE2-style macro controls. Tree of Life garrisons Gatherers for damage reduction and counter-attack.

**Version History:**
- v9.3: Ballistic archery, XP ranks, squads, morale, formations, retargeting, weighted terrain
- v10: Stone resource, worker skill XP (6 tracks, 3 ranks), tower cannon overhaul (ballistic + explosive)
- v10_1: Procedural unit traits (10 traits), control groups (Ctrl+0-9), enemy inspection panel, combat heat minimap
- v10_2: Town Hall garrison (workers barricade for armor + stone-hurling), hold ground stance, attack-move, helper buildings (drop-offs), production buildings (Spires)
- v10_3: Water terrain removed (reserved for terrain overhaul), visual pip cleanup
- v10_4: Performance — spatial grid, map caching, insertion sort, minimap dirty flags, player death logging
- v10_5: Module split (entities.py → entity_base/unit/building/building_shapes/projectiles), parabolic projectiles with lead aiming
- v10_6: Major difficulty rebalance — fractal formations (4 types), stances (4 types), 5 new enemy types, adaptive difficulty engine
- v10_7: Edge case polish — tower upgrade fire penalty, Harmonic Pulse, straggler metamorphosis
- v10_8: Resonance fields — per-formation aura bonuses, harmonic resonance quality, dissonance system
- v10_9: Incident Director — FSM-based dramaturgic threat engine replaces fixed wave system, 13 incident flavours, tension/catharsis, dramatic arc
- v10_alpha: Harmonic resonance math — `compute_harmony()`, musical interval labels, tooltip/info card system
- v10_beta: Counter-pick AI counters formations, formation move, worker skill rank bonus on production, shift-click waypoint queue
- v10_delta: Physics movement (velocity/acceleration), energy/stamina system, spring-based formations, player-driven squad management, formation discovery system
- v10_epsilon: Formation combat — Rose sweep, Sierpinski pulse, Koch contract, Spiral tighten/loosen, type-aware slot classification, Quick-Form (F key)
- v10_epsilon2: Quick-Form auto-picks best harmony formation, fractal GUI overhaul begins
- v10_epsilon3: Fractal font, Koch borders, fractal progress bars — complete GUI rebirth
- v10_epsilon4: UX overhaul (game-over stats, attack arrows, difficulty descriptions, formation hints, incident alerts), energy bar visual, velocity trails, exhaustion particles, free unit counter, Don't Panic advisor (basic)

---

## 2. Incident Director — Dramaturgic Threat Engine

The Incident Director (v10_9) replaced the old fixed-interval wave system with an FSM-driven dramatic engine. Enemies arrive as **incidents** — narrative events with escalating tension, not predictable timer-based waves.

### 2.1 Difficulty Profiles

Three selectable profiles from the main menu (hotkeys 1/2/3):

| Parameter | Easy | Medium | Hard |
|---|---|---|---|
| Starting Flux / Fiber | 300 / 150 | 200 / 100 | 180 / 100 |
| Starting Gatherers | 4 | 3 | 3 |
| Incidents Required (to win) | 7 | 14 | 21 |
| First Incident (seconds) | 300 | 270 | 240 |
| Base Cooldown (seconds) | 90 | 70 | 50 |
| Min Cooldown (seconds) | 40 | 25 | 15 |
| Tension Drift Rate | 0.003 | 0.005 | 0.007 |
| HP Scale / Incident | +4% | +5% | +6% |
| ATK Scale / Incident | +3% | +4% | +5% |
| Kill Bounty Base | 5 | 4 | 2 |
| Incident Bonus Flux / Fiber / Alloy | 30/15/3 | 25/15/3 | 15/8/2 |

### 2.2 FSM States (5-state cycle)

```
CALM → FOREBODING → IMMINENT → ACTIVE → AFTERMATH → CALM
```

| State | Duration | Behavior |
|---|---|---|
| **CALM** | Variable (cooldown) | Tension drifts upward. 15% chance of **false calm** (1.8× duration, eerie narrative). Waits for cooldown expiry, then selects next incident |
| **FOREBODING** | 10-30s (inversely scales with tension) | Narrative warning text. Player has time to prepare |
| **IMMINENT** | 4.0s | Final warning. Pre-computes spawn edges. Red alert UI |
| **ACTIVE** | Until all enemies dead/fled | Combat. Tension bleeds at 0.02/s (catharsis). Enemies spawn at map edges |
| **AFTERMATH** | 5-15s | Tension decays at 0.06/s (relief). Bonus resources awarded. Victory check |

### 2.3 Tension System (0.0 – 1.0)

Tension is the drama thermostat:
- **Drifts upward** during CALM (rate accelerates over game time, capped at 2.5×)
- **Bleeds** during ACTIVE and AFTERMATH (catharsis)
- **Adjusted** after each incident by outcome classification:

| Outcome | Pain Threshold | Tension Delta | Cooldown Mult |
|---|---|---|---|
| Dominated | < 0.05, no escapes, < 30s | +0.08 (escalate) | 0.6× (faster) |
| Won | < 0.20, ≤1 escape | -0.05 (slight relief) | 1.0× |
| Costly | < 0.50 | -0.15 (real relief) | 1.5× (slower) |
| Devastating | ≥ 0.50 | -0.30 (major catharsis) | 2.2× (much slower) |

**Pain ratio:** `(buildings_lost × 3 + units_lost) / total_spawned`

### 2.4 Tier System

Tension determines which incident tiers are available:

| Tier | Tension ≥ | Stat Scaling | Count Range |
|---|---|---|---|
| Light | 0.00 | 0.7× | 2-5 |
| Medium | 0.25 | 1.0× | 6-12 |
| Strong | 0.50 | 1.2× | 12-20 |
| Deadly | 0.75 | 1.5× | 20-35 |

### 2.5 Dramatic Arc

Progress through the game follows a dramatic arc (fraction of `incidents_required`):

| Phase | Progress | Available Tiers |
|---|---|---|
| Opening | 0–25% | Light only |
| Rising | 25–50% | Light + Medium |
| Midgame | 50–75% | Light + Medium + Strong |
| Climax | 75–95% | All tiers |
| Finale | Last incident | Always Deadly |

### 2.6 Incident Catalogue (13 flavours)

| Incident | Tier | Count | Composition | Behavior | Dirs |
|---|---|---|---|---|---|
| Scout | Light | 2-4 | Hollow Wardens only | Flee after 3s combat | 1 |
| Forager Raid | Light | 3-5 | 60% Reapers, 40% Wardens | Economy target | 1 |
| Probe | Light | 3-5 | 50/50 Wardens/Rangers | Retreat after 8s | 1 |
| Assault | Medium | 6-10 | Mixed infantry + siege | Standard | 1 |
| Flanking | Medium | 6-10 | Infantry + raiders | Standard | 2 |
| Economy Raid | Medium | 6-10 | Raider-heavy | Economy target | 1 |
| Siege Column | Strong | 12-18 | Siege + shields + healers | Standard | 1 |
| War Party | Strong | 12-18 | Elites + mixed | Standard | 1 |
| Pincer | Strong | 14-20 | Raiders + elites | Standard | 3 |
| Healer Push | Strong | 12-16 | Shields + healers | Standard | 1 |
| Grand Assault | Deadly | 22-32 | All types | Standard | 3 |
| Swarm | Deadly | 28-35 | Mass infantry + raiders | Standard | 2 |
| Dark Resonance | Deadly | 20-28 | Elites + shields + healers | 50% forced dissonance | 2 |

### 2.7 Counter-Pick AI

Modifies incident composition based on player state:
- Many Sentinels, no mobile army → +Hexweavers (siege)
- Strong economy (6+ workers) → +Blight Reapers (raiders)
- Heavy Ranger meta → +Ironbark (shieldbearers)
- Player clumps units → +siege types
- Counters player's most-used formation: Sierpinski → +Thornknights; Koch → +Hexweavers; Rose → +Thornknights; Spiral → +Ironbark

### 2.8 Straggler Metamorphosis

Enemy units that survive across incident boundaries evolve:
- **After 1 incident:** Unit roots in place (speed=0, stops attacking, grows root tendrils VFX)
- **After 2 incidents:** Metamorphoses into **Bitter Root** — a lingering dissonant tone grown into something worse (3× HP, 2× ATK, 60% base speed, pulsing red aura)

### 2.9 Evolution — Incident Conductor v2

The current FSM (Section 2.2) remains the skeleton of the Incident Director.
A future **Incident Conductor** upgrade layers three perceptual "ears" on top:

| Ear | Version | Listens To |
|---|---|---|
| **Tempo Ear** | v10_zeta | Pacing — APM, idle time, gather cadence |
| **Harmony Ear** | v10_eta | Composition — formation quality, army balance, economy shape |
| **Drama Ear** | v11 | Narrative — arc momentum, player surprise budget, catharsis debt |

Each ear produces a normalized signal (0–1). The conductor blends them into
a single **incident score** that modulates tier selection, cooldown, and
composition — replacing the current tension-only gate.

The FSM states, tier table, and catalogue remain unchanged; the conductor
only adjusts *when* and *what* fires, not the event lifecycle itself.

> Full specification: see **GDD_Roadmap.md § Incident Conductor v2**.

---

## 3. Map & Terrain

- **Grid:** Scales with difficulty — Easy: 64×64, Medium: 128×128, Hard: 256×256
- **Tile Size:** 32px

| ID | Terrain | Color (RGB) | Passable | Buildable | Move Cost | Notes |
|---|---|---|---|---|---|---|
| 0 | Grass | (40, 118, 74) | Yes | Yes | 1.0× | Default terrain |
| 1 | Water | — | — | — | — | **Reserved** (removed in v10_3) |
| 2 | Tree | (20, 100, 20) | Yes | No | 2.0× | Harvestable → Fiber |
| 3 | Gold | (218, 165, 32) | Yes | No | 1.8× | Harvestable → Flux |
| 4 | Iron | (140, 140, 155) | Yes | No | 1.8× | Harvestable → Ore |
| 5 | Shallow Water | — | — | — | — | **Reserved** |
| 6 | Stone | (160, 150, 130) | Yes | No | 1.8× | Harvestable → Crystal |

**Passability:**
- `is_passable(c, r)` — True for any terrain in TERRAIN_MOVE_COST
- `is_walkable(c, r)` — True only for grass. Used for building placement
- Units can walk through resource tiles at reduced speed
- Harvesting depletes tiles to grass, creating cleared paths

**Procedural Generation:**
- 15-22 tree forests (random walk, 8-30 tiles each)
- 5-8 Flux deposits (3-6 tiles), 4-7 Ore deposits (3-6 tiles), 3-5 Crystal deposits (4-8 tiles)
- 3 guaranteed tree clusters + 2 guaranteed Flux deposits near start
- 9×9 clear zone around map center for starting base

**Resource Capacities:**

| Resource | Capacity | Gather Time | Amount/Trip |
|---|---|---|---|
| Tree → Fiber | 50 | 2.0s | 10 |
| Gold → Flux | 80 | 3.0s | 10 |
| Iron → Ore | 60 | 3.0s | 15 |
| Stone → Crystal | 70 | 3.5s | 10 |

---

## 4. Resources

Five resource types managed by `ResourceManager` (code name → UI name):

| Resource | UI Name | Icon Color | Primary Source | Secondary Source |
|---|---|---|---|---|
| gold | **Flux** | (255, 215, 0) | Gold tiles | Kill bounty, incident bonus |
| wood | **Fiber** | (34, 180, 34) | Tree tiles | Incident bonus |
| iron | **Ore** | (170, 170, 185) | Iron tiles | — |
| steel | **Alloy** | (100, 160, 220) | Harmonic Mill (2 Ore → 1 Alloy) / Fractal Forge | Incident bonus |
| stone | **Crystal** | (160, 150, 130) | Stone tiles | — |

Ore → Alloy pipeline via Harmonic Mill (6s) or Fractal Forge (4s, uses 2 Crystal + 1 Ore). Crystal is used for Sentinels and garrison bell cost.

---

## 5. Buildings

All buildings are player-side only. Built by Gatherers through right-click assignment.

### 5.1 Core Building Stats

| Building (code → UI) | Flux | Fiber | Ore | Alloy | Crystal | HP | Build Time | Size |
|---|---|---|---|---|---|---|---|---|
| town_hall → **Tree of Life** | 200 | 120 | 0 | 0 | 0 | 500 | 30s | 2×2 |
| barracks → **Resonance Forge** | 120 | 80 | 0 | 0 | 0 | 400 | 18s | 2×2 |
| refinery → **Harmonic Mill** | 80 | 60 | 30 | 0 | 0 | 300 | 22s | 2×2 |
| tower → **Sentinel** | 30 | 0 | 15 | 0 | 35 | 220 | 18s | 1×1 |

### 5.2 Helper Buildings (1×1, Foreman unlocks)

Unlocked when a Gatherer reaches Foreman rank in the corresponding skill. Placed near resource patches to shorten worker travel time.

| Building (code → UI) | Flux | Fiber | Ore | Alloy | Crystal | HP | Build | Unlock |
|---|---|---|---|---|---|---|---|---|
| goldmine_hut → **Flux Node** | 40 | 30 | 0 | 0 | 0 | 150 | 12s | Flux Miner Foreman |
| lumber_camp → **Fiber Node** | 30 | 40 | 0 | 0 | 0 | 150 | 12s | Fiberjack Foreman |
| quarry_hut → **Crystal Node** | 40 | 30 | 0 | 0 | 10 | 150 | 12s | Crystal Mason Foreman |
| iron_depot → **Ore Node** | 40 | 30 | 0 | 0 | 0 | 150 | 12s | Ore Miner Foreman |
| scaffold → **Lattice** | 50 | 40 | 0 | 0 | 0 | 100 | 10s | Builder Foreman |

**Drop-off function:** Gatherers deposit resources at the nearest valid drop-off (Tree of Life, matching helper, or matching production building) instead of trekking back to the Tree of Life.

**Lattice aura:** Workers within 128px get +25% build/repair speed.

### 5.3 Production Buildings (2×2, Master upgrades)

Upgraded from helper buildings when a Gatherer reaches Master rank. Generate resources passively, boosted by stationed workers.

| Building (code → UI) | Flux | Crystal | HP | Build | Upgrades From | Production |
|---|---|---|---|---|---|---|
| sawmill → **Fiber Spire** | 60 | 40 | 300 | 20s | Fiber Node | Fiber: 1.5 base + 5.0/worker per tick |
| goldmine → **Flux Spire** | 80 | 40 | 300 | 20s | Flux Node | Flux: 1.0 base + 4.0/worker per tick |
| stoneworks → **Crystal Spire** | 60 | 30 | 300 | 20s | Crystal Node | Crystal: 1.0 base + 4.0/worker per tick |
| iron_works → **Ore Spire** | 60 | 40 | 300 | 20s | Ore Node | Ore: 0.8 base + 3.5/worker per tick |
| forge → **Fractal Forge** | 60 | 30 (+20 Ore) | 350 | 22s | Harmonic Mill | 2 Crystal + 1 Ore → 1 Alloy (4s) |

**Production tick:** Every 5 seconds. Worker skill rank bonus: +10% per average skill rank. Max 3 workers (2 for Forge). Forge speed boosted +30% per stationed worker.

**Smelter Foreman bonus:** Refineries with a Smelter Foreman worker nearby get +30% refine speed.

### 5.4 Core Building Functionality

**Tree of Life** (`town_hall`):
- Trains Gatherers (Q key, 50 Flux, 8s)
- Resource drop-off point
- Passive healing aura: 2 HP/s within 192px (6 tiles)
- Garrison — Gatherers barricade inside (see Section 6.6)

**Resonance Forge** (`barracks`):
- Trains Wardens (T key, 75 Flux + 8 Alloy, 13s)
- Trains Rangers (E key, 55 Flux + 25 Fiber + 4 Alloy, 11s)
- Training queue (FIFO)

**Harmonic Mill** (`refinery`):
- Auto-refines: 2 Ore → 1 Alloy every 6s
- Operates while Ore is available
- Upgrades to Fractal Forge (Master rank)

**Sentinel** (`tower`):
- **Lattice anchor** — standing stone for future dihedral symmetry system (see GDD_Roadmap)
- **Passive Resonance Field:** Damages enemies within 220px radius
  - 12 DPS, scaling with symmetry order (+25% per completed axis)
  - No projectiles — continuous aura effect
  - Visual: Koch snowflake outline at defense range, pulsing
- **Level 2 — Amplified Resonance:** Upgrade costs 15 Alloy, 12s Gatherer build time
  - 18 DPS base + 10 DPS AoE burst when enemy dies in field (60px splash)
  - Field range extends to 260px
- **Harmonic Pulse:** Sentinel emits expanding resonance wave (Koch ring VFX, 0.6s)
  - Friendly units within 120px get 25% attack speed buff for 3.0s
  - 4.0s cooldown

> **Migration note:** Code currently uses `tower` internally. The rename `tower` → `sentinel` is pending.

### 5.5 Building Ruin System

When a completed player building reaches 0 HP:
- Becomes a ruin (`ruined = True`), retains residual HP
- Training/refining halted, rendered at 1/3 brightness
- Enemies deprioritize ruins (15% of base priority)
- Garrisoned Gatherers ejected on ruin transition
- Right-click workers to rebuild at 40% of original cost

---

## 6. Units

### 6.1 Player Units

| Unit | Flux | Fiber | Alloy | HP | Speed | ATK | Range | CD | Train |
|---|---|---|---|---|---|---|---|---|---|
| Gatherer (`worker`) | 50 | 0 | 0 | 50 | 80 | 4 | 40 | 1.0s | 8s |
| Warden (`soldier`) | 75 | 0 | 8 | 140 | 70 | 14 | 40 | 1.0s | 13s |
| Ranger (`archer`) | 55 | 25 | 4 | 75 | 75 | 9 | 170 | 1.4s | 11s |

### 6.2 Enemy Units — The Dark 7 (Base Stats)

Seven enemy types, each a corrupted mirror of a player Heptarchy tone:

| Code Name | Display Name | Tone Mirror | HP | Speed | ATK | Range | CD | Special |
|---|---|---|---|---|---|---|---|---|
| enemy_soldier | **Hollow Warden** | Re (2) | 100 | 55 | 12 | 40 | 1.2s | — |
| enemy_archer | **Fade Ranger** | Mi (3) | 60 | 50 | 6 | 140 | 1.8s | — |
| enemy_siege | **Hexweaver** | Ti (7) | 200 | 35 | 20 | 40 | 3.0s | 2× building damage |
| enemy_elite | **Thornknight** | Sol (5) | 160 | 60 | 18 | 40 | 1.0s | Fast, high DPS |
| enemy_shieldbearer | **Ironbark** | Fa (4) | 250 | 40 | 8 | 40 | 1.5s | 50% frontal armor |
| enemy_healer | **Bloodtithe** | La (6) | 60 | 45 | 0 | 120 | — | 5 HP/s heal |
| enemy_raider | **Blight Reaper** | Do (1) | 70 | 80 | 10 | 40 | 1.0s | Economy-only targeting |

**Stat scaling per incident:** `hp = base × (1 + hp_scale × incident#)`, `atk = base × (1 + atk_scale × incident#)`

**Enemy unlock by incident count (Medium):** Fade Ranger (2), Blight Reaper (4), Hexweaver (6), Ironbark (7), Bloodtithe (9), Thornknight (12).

### 6.3 Unit States

| State | Description |
|---|---|
| `idle` | No task. Combat units auto-aggro within range+64px |
| `moving` | Following A* path via physics movement |
| `gathering` | Gatherer harvesting resource tile |
| `returning` | Gatherer carrying resources to nearest drop-off |
| `building` | Gatherer constructing/rebuilding |
| `attacking` | Engaged with target, retargets every 1.5s |
| `repairing` | Gatherer repairing damaged building |
| `fleeing` | Gatherer/enemy fleeing threats (5s cooldown between flee-resume) |
| `garrisoned` | Gatherer inside Tree of Life, hidden from rendering |

### 6.4 Gatherer Behaviors

**Gathering:** Walk to tile → harvest over time → carry to nearest valid drop-off (Tree of Life, helper building, or production building) → auto-resume. Remembers last gather type for resume after interruption.

**Building:** Right-click unbuilt/ruined building. Must be within 2.5 tiles. Multiple Gatherers can build simultaneously. Lattice aura grants +25% speed within 128px.

**Repairing:** Right-click damaged building. 15 HP/s per Gatherer. Costs 15% of building's full cost.

**Fleeing:** Triggers when enemy within 160px. Saves task state, paths 6 tiles away, resumes after 2.0s safety. 5-second cooldown between flee-resume cycles.

### 6.5 Gatherer Skill XP System

Gatherers gain XP in the specific skill they are actively using. Six skill tracks:

| Skill (code → UI) | Activity | Color |
|---|---|---|
| lumberjack → **Fiberjack** | Harvesting Fiber (trees) | Green |
| gold_miner → **Flux Miner** | Harvesting Flux (gold deposits) | Gold |
| iron_miner → **Ore Miner** | Harvesting Ore (iron veins) | Silver |
| stone_mason → **Crystal Mason** | Harvesting Crystal (stone quarries) | Sandstone |
| builder → **Builder** | Constructing/repairing | Cyan |
| smelter → **Smelter** | Harmonic Mill boost (+30% refine speed at Foreman) | Steel Blue |

**Three ranks per skill:**

| Rank | Title | XP Threshold | Speed Bonus | Unlock |
|---|---|---|---|---|
| 0 | Novice | 0 | +0% | — |
| 1 | Foreman | 80 | +15% | Helper building for that skill |
| 2 | Master | 200 | +30% | Production building upgrade |

XP is per-skill, not global. A Flux Miner Foreman switching to trees gathers at Novice speed. Builder XP accrues at 0.5 XP/s during build/repair work.

### 6.6 Tree of Life Garrison

| Parameter | Value |
|---|---|
| Max Gatherers | 10 |
| Armor per Gatherer | 5% damage reduction (caps at 50%) |
| Crystal-hurling damage | 3 per Gatherer per tick |
| Attack cooldown | 2.0s |
| Attack range | 120px |
| Bell cost | 20 Fiber, 5 Ore, 10 Crystal |

**Mechanics:**
- Town Bell global button recalls all Gatherers into nearest Tree of Life (costs resources)
- Garrisoned Gatherers are hidden from rendering and skip all behavior updates
- Gatherers auto-deposit carried resources on entering garrison
- Tree of Life damage reduced by `5% × num_Gatherers` (max 50%)
- Garrisoned Gatherers collectively hurl crystals at nearest enemy within 120px
- Gatherers ejected on ruin transition
- Resume Work global button ungarrisons all and resumes gathering

---

## 7. Physics Movement (v10_delta)

All units use velocity/acceleration-based movement. Each unit type has a distinct movement profile:

| Unit | Accel | Decel | Max Speed | Character |
|---|---|---|---|---|
| Warden (`soldier`) | 180 | 250 | 70 | Steady march |
| Ranger (`archer`) | 280 | 150 | 75 | Quick, slides |
| Gatherer (`worker`) | 120 | 200 | 80 | Deliberate |
| Hollow Warden | 160 | 220 | 55 | — |
| Hexweaver (siege) | 60 | 400 | 35 | Lumbering |
| Thornknight (elite) | 250 | 200 | 60 | Fast |
| Blight Reaper (raider) | 400 | 80 | 80 | Sprint-and-slide |

**Movement mechanics:**
- Effective speed = `(max_speed / terrain_cost) × energy_factor × carry_penalty`
- **Kinematic braking:** Braking distance = `v² / (2 × decel)`. Units decelerate smoothly to waypoints
- **Soft repulsion:** Same-owner units within 16px push apart (quadratic falloff). Stacked units splay using golden angle
- **Wall-sliding:** Blocked axes damped, unblocked axes preserved (units slide along obstacles)
- Arrival threshold: 12px for waypoints, 48px for worker task snap

---

## 8. Energy / Stamina System (v10_delta)

Every unit has a per-unit energy pool. Actions drain energy, regen depends on state and formation harmony.

### 8.1 Energy Profiles

| Unit | Max | Regen/s | Accel Cost | Cruise Cost | Attack Cost |
|---|---|---|---|---|---|
| Warden | 100 | 8 | 10/s | 2/s | 6 |
| Ranger | 80 | 10 | 8/s | 1.5/s | 4 |
| Gatherer | 150 | 15 | 6/s | 1/s | — (gather: 2/s) |

**Cost model:** Acceleration costs a lot, cruising costs a little, braking is free.

### 8.2 Exhaustion

- Below 20% energy → **exhausted**
- Exhausted speed: 60% of normal (linear ramp from 0 energy to 20% threshold)
- Exhausted attack cooldown: +30%

### 8.3 Regen Modifiers

| Condition | Multiplier |
|---|---|
| Idle (standing still) | 3.0× regen |
| Carrying resources | 0.85× regen, 0.7× speed |
| Fleeing | 1.5× energy drain |
| Formation harmony | ×(1 + harmony × 0.8) regen |

### 8.4 Harmonic Energy Fields

| Formation | Energy Bonus |
|---|---|
| Rose anchor (commander) | 1.5× regen, shares 3 energy/s to petals |
| Koch | 30% less attack energy cost |
| Spiral | 2 energy/s transfer inner→outer |

---

## 9. Procedural Unit Traits (v10_1)

Every unit rolls 0-2 traits at creation (40% zero, 45% one, 15% two). Traits are cached multipliers.

| Trait | Rarity | Effect | Allowed Types |
|---|---|---|---|
| Brave | Common | +50% morale resistance | Warden, Ranger, Enemies |
| Cowardly | Common | -30% morale resistance | Warden, Ranger, Enemies |
| Aggressive | Common | +40% aggro range, +30% targeting noise | Warden, Ranger, Enemies |
| Cautious | Common | -30% aggro range, +30% low-HP bonus | Warden, Ranger, Enemies |
| Loyal | Uncommon | 2× squad cohesion | Warden, Ranger, Enemies |
| Lone Wolf | Uncommon | +15% ATK when alone (80px isolation) | Warden, Ranger, Enemies |
| Sharpshooter | Rare | -40% arrow spread | Ranger only |
| Berserker | Rare | +25% ATK below 50% HP | Warden only |
| Inspiring | Very Rare | Morale leader at any rank | Warden, Ranger, Enemies |
| Nimble | Common | +15% terrain speed bonus | All combat |

**Conflicts (mutually exclusive):** Brave/Cowardly, Aggressive/Cautious, Loyal/Lone Wolf

---

## 10. XP & Military Rank System

### 10.1 XP Acquisition

| Event | Player XP | Enemy XP |
|---|---|---|
| Dealing a hit | +1 | +1 |
| Killing a target | +3 bonus | +2 bonus |

Gatherers do NOT gain combat XP.

### 10.2 Military Ranks

| Rank | Name | XP | HP Mult | ATK Mult | Range+ | Accuracy+ |
|---|---|---|---|---|---|---|
| 0 | Recruit | 0 | 1.00× | 1.00× | +0 | +0.00 |
| 1 | Veteran | 10 | 1.08× | 1.06× | +5 | +0.03 |
| 2 | Corporal | 30 | 1.16× | 1.12× | +10 | +0.06 |
| 3 | Sergeant | 70 | 1.26× | 1.20× | +18 | +0.10 |
| 4 | Captain | 140 | 1.40× | 1.30× | +25 | +0.15 |

HP ratio preserved on rank-up. Rank colors: Gray → Bronze → Silver → Gold → Diamond Blue.

---

## 11. Ballistic Archery

Rangers fire real projectiles with accuracy spread. Sentinels use resonance fields (no projectiles).

| Property | Value |
|---|---|
| Speed | 350 px/s |
| Max flight | 2.0s |
| Hit radius | 12px |
| Base spread | 0.18 rad (Recruit) |
| Min spread | 0.03 rad (Captain) |
| Arc height | 40px parabolic |
| Flight time | 0.8s to target |
| Trail | 4-point afterimage |
| Lead aiming | Corporal+ (rank 2), accuracy scales with rank |

**Arrow lifecycle:** Fire → parabolic arc with spread → hit detection (12px) → damage + XP → or miss → ground arrow (8s persist, max 50).

---

## 12. Squad System (Player-Driven)

### 12.1 Overview

Squads are **player-created**, not auto-formed. Max size: 12. Leader = highest rank member (promotes on death). Followers are pulled toward formation slots via spring physics.

### 12.2 Squad Creation

| Method | How |
|---|---|
| **F1-F4** | Select military units, press formation hotkey. Creates new squad from free units (min 2). Shift+F# force-pulls from existing squads |
| **F (Quick-Form)** | Auto-picks best-harmony formation for selected free units. Double-tap cycles formations |
| **Pending Group Discovery** | form a squad from free or mixxed units → triggers composition check → formation auto-discovered if recipe matches |

### 12.3 Formation Discovery

Formations must be **discovered** before use. Discovery requirements:

| Formation | Min Size | Min Veterans | Ratio Requirement |
|---|---|---|---|
| Polar Rose | 3 | 1 | Any (tutorial) |
| Sierpinski | 4 | 1 | Within 35% of 3:1 |
| Golden Spiral | 5 | 1 | Within 35% of 3:2 (φ) |
| Koch Snowflake | 6 | 1 | Within 35% of 1:1 |

**Discovery event:** Slow-motion (15% speed for 1.5s), discovery banner (3s), notification, auto-squad creation.

### 12.4 Fractal Formations

4 formation types, each a mathematical object:

| Formation | Hotkey | Math | Slot Calculator |
|---|---|---|---|
| **Polar Rose** | F1 | `r = cos(kθ)`, k = n-1 | Leader at center, followers on petals. Spacing 25px |
| **Golden Spiral** | F2 | Vogel sunflower `θ_n = n × golden_angle` | Fibonacci-spaced rings. Default c=18, adjustable 10-30 |
| **Sierpinski Triangle** | F3 | Recursive triangle subdivision | Depth scales with count. Spacing 30px |
| **Koch Snowflake** | F4 | Units distributed on Koch perimeter | Depth scales with count (<4→triangle, 4-12→d1, 13+→d2). Radius 40px |

### 12.5 Type-Aware Slot Assignment

Units are assigned to formation slots based on their type:
- **Rose:** Wardens at petal tips (sweeping damage), Rangers at center/bases
- **Spiral:** Wardens at inner rings (protective), Rangers at outer (sightlines)
- **Sierpinski:** Wardens at outermost vertices (exposed), Rangers at midpoints
- **Koch:** Wardens at convex peaks (outward-facing), Rangers at concave bays

### 12.6 Spring-Based Positioning (v10_delta)

Units gravitate toward formation slots via critically-damped spring:
- Spring constant: 3.0, Damping: 0.7 (critically damped — no oscillation)
- Max force: 120 px/s²
- In combat within leash (80px): spring weakened to 30%
- Beyond leash: spring tripled (rubber-band)
- 0.5s grace period after combat before spring resumes

### 12.7 Formation Combat Abilities (v10_epsilon)

| Formation | Ability | Key | Mechanic |
|---|---|---|---|
| **Rose** | Sweep | R (toggle) | Rotation at 0.3 rad/s. Petal-tip Wardens deal 15% ATK to enemies within 20px. 1.5s per-target cooldown. Costs 5 energy/s shared |
| **Spiral** | Tighten/Loosen | Scroll wheel | Adjusts Vogel spacing (c=10 tight, c=30 loose). No cost |
| **Sierpinski** | Vertex Pulse | V | Expand 1.8× for 0.4s, then burst: 10% ATK to enemies within 25px. Costs 20 energy. 3s cooldown |
| **Koch** | Perimeter Contract | V | Shrink to 40% for 0.6s, then crush: 12% ATK to trapped enemies within 35px. Costs 25 energy. 4s cooldown |

### 12.8 Harmonic Resonance

**Harmony quality** (0.3–1.0) measures how well a squad's soldier:archer ratio matches the formation's ideal:

| Formation | Ideal Ratio | Musical Interval |
|---|---|---|
| Rose | 2:1 | Octave |
| Spiral | 1.618:1 (φ) | Perfect Fifth |
| Sierpinski | 3:1 | Major |
| Koch | 1:1 | Unison |

**Resonance bonuses** (scale with harmony quality):
- **Rose:** +3% damage per petal depth
- **Spiral:** Evasion chance = 1/φ^depth
- **Sierpinski:** AOE damage reduction = 1/3^depth
- **Koch:** 15% slow to nearby enemies per depth (radius = formation radius × 1.5)

**Multi-squad penalty:** -30% resonance per duplicate formation type across active squads.

**Dissonance:** 20% of enemies (after incident 8) gain anti-resonance aura (60px radius) that nullifies nearby formation bonuses. Dark Resonance incidents force 50% dissonance.

### 12.9 Stance System

4 stance modes (F5-F8):

| Stance | Hotkey | Aggro Behavior | Chase |
|---|---|---|---|
| Aggressive | F5 | weapon_range + idle aggro range | Chase targets |
| Defensive | F6 | weapon_range only | No chase |
| Guard | F7 | weapon_range + 40px, return to guard position | No chase |
| Hunt | F8 | 1.5× aggro range, prioritize Raiders/siege | Chase targets |

---

## 13. Target Priority System

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

## 14. Enemy Horde Morale

- Check interval: 1.0s per unit (staggered)
- Scan radius: 160px — count player vs enemy forces
- Flee ratio: 3.0 × rank resistance (Recruit 1.0, Veteran 1.3, Corporal 1.6, Sergeant+ 999)
- Leader aura: Sergeant+ within 120px suppresses flee entirely
- Flee behavior: regroup with allied cluster OR escape to map edge with XP preserved
- Veterans return next incident with +25% stats + accumulated XP/ranks

---

## 15. Global Command System

When no unit or building is selected, 4 macro buttons appear:

| Button | Action |
|---|---|
| **Defend Base** | All combat units move to area between Tree of Life and nearest Sentinel |
| **Hunt Enemies** | All combat units attack-move to nearest enemy, or map center if none visible |
| **Town Bell** | Pay 20 Fiber/5 Ore/10 Crystal, all Gatherers garrison in nearest Tree of Life |
| **Resume Work** | Ungarrison all Gatherers, resume previous gathering task |

**Unit Command Buttons** (when combat units selected):
- **Attack Move** — enter attack-move mode (click to set destination, engage enemies en route)
- **Hold Ground** — stop and fight in range, never chase (toggleable)

**Shift-click:** Queue waypoints for move/attack-move commands.

---

## 16. Pathfinding

**Algorithm:** A* with 8-directional movement, weighted terrain costs.

| Terrain | Move Cost |
|---|---|
| Grass | 1.0× |
| Tree | 2.0× |
| Flux / Ore / Crystal tiles | 1.8× |

- Heuristic: Chebyshev distance
- Node limit: 4000
- Building tiles blocked. Building's own tiles excluded for workers building it
- Effective speed: `base_speed / terrain_cost` (further modified by physics and energy)
- Repath cooldown: 1.5s after A* failure before retrying

---

## 17. Camera & Input

**Camera:** WASD (always priority over hotkeys) + edge scroll (25px margin), 400 px/s. Zoom 0.4×–2.0× via mousewheel. Space centers on selection.

**Selection:** Click (20px radius), box-drag (5px threshold), ESC deselect. Garrisoned units excluded. Double-click (400ms) for control group camera center.

**Control Groups:** Ctrl+0-9 assign, 0-9 recall, double-tap centers camera.

**Right-Click Context:**

| Target | Gatherer | Combat Unit |
|---|---|---|
| Enemy | Attack | Attack |
| Resource tile | Gather | Move |
| Unbuilt building | Build | Move |
| Ruined building | Rebuild (40%) | Move |
| Damaged building | Repair | Move |
| Empty ground | Move | Move |

**Hotkeys:**

| Key | Action |
|---|---|
| 1-4 | Place buildings (Gatherer selected) |
| Q | Train Gatherer (Tree of Life) |
| T/E | Train Warden/Ranger (Resonance Forge) |
| U | Upgrade Sentinel |
| F1-F4 | Set formation (Rose/Spiral/Sierpinski/Koch) |
| F | Quick-Form (auto-pick best formation) |
| F5-F8 | Set stance (Aggressive/Defensive/Guard/Hunt) |
| R | Toggle Rose rotation |
| V | Activate formation ability (Sierpinski pulse / Koch contract) |
| Delete | Dissolve squad |
| F10 | Surrender |

---

## 18. User Interface

### 18.1 Fractal GUI (v10_epsilon3)

All UI elements use the **fractal visual system**:
- **Fractal font** — geometric strokes at any size, glow at 14px+, falls back to SysFont only below 7px
- **Koch borders** — fractal border ornament on all panels, buttons, and cards. Max bump: 6px, always folds inward
- **Fractal progress bars** — gradient-filled bars with cached column scaling
- **Radial gradient backgrounds** — concentric ellipses on major panels
- **Fractal resource icons** — Fibonacci spiral (Flux), binary tree (Fiber), octahedron (Ore), Reuleaux triangle (Alloy), Voronoi cluster (Crystal)
- **Fractal selection rings** — Koch-snowflake rings replace simple circles

### 18.2 Layout

| Region | Position | Content |
|---|---|---|
| Top Bar | y=0, h=40 | Resources (fractal icons + values), population, tension bar, incident counter |
| Game Area | y=40, h=550 | Map, units, buildings, arrows, resonance fields |
| Bottom Panel | y=590, h=130 | Selection info, action buttons, global commands |
| Minimap | Upper-right, 160×160 | Terrain, units, buildings, camera rect, combat heat |
| Message Log | Above bottom panel | Scrollable log with categories (info/discovery/attack/economy/command) |

Golden-ratio panel layout: the bottom panel uses a φ split at 368px Koch divider between info column (left) and action column (right).

### 18.3 Bottom Panel States

Fractal font sizing: buttons use 13px, cost labels 10px, message log entries 8px.

- **Nothing selected:** 4 global command buttons + help text
- **Enemy inspected:** Read-only panel with Dark 7 name, rank, traits, HP, stats, state
- **Building selected:** Icon with Koch border, name, HP bar, status, action buttons
- **Single unit:** Icon, name+rank, traits, HP/energy bars, stats+state, XP bar, skill info (Gatherer)
- **Multi-unit:** Count by type with rank distribution, aggregate HP, build/command buttons

### 18.4 Tooltip System

Hover delay: 0.4s. Max width: 240px. Every UI element has a tooltip:
- Resources, buildings, units, traits, stances, formations, harmony, ranks
- Fractal font rendering, Koch border frame, fractal info cards

### 18.5 Tutorial Hints

7 progressive hints triggered by game state milestones (select TH → train worker → gather → build forge → train military → defend → move units). Each shows for 8s with 3s cooldown between hints.

### 18.6 Minimap

- 160×160px, terrain rebuilt on dirty flag
- Player buildings: blue (ruins: dark gray)
- Player units: cyan dots, Enemy units: red dots
- Camera viewport: white rectangle
- Combat heat overlay: red glow at recent combat locations (30s decay)
- Click to jump camera
- Incident alert: minimap flash (2s) on enemy spawn

### 18.7 Presence Director (v10_zeta+)

The **Presence Director** is an adaptive GUI conductor that manages what
information reaches the player and when. It replaces ad-hoc show/hide logic
with a unified 5-channel priority system.

**Channels:**

| # | Channel | Governs | Current Prototype |
|---|---|---|---|
| 1 | **Economy** | Resource alerts, worker idle nudges, gather rate sparklines | Progressive resource reveal (top bar) |
| 2 | **Threat** | Incident warnings, enemy composition preview, damage flash | Incident alert system |
| 3 | **Command** | Selection feedback, formation hints, stance reminders | Context-sensitive bottom panel |
| 4 | **Information** | Tooltips, discovery banners, advisor messages | Tooltip system + Don't Panic advisor |
| 5 | **Atmosphere** | Ambient VFX intensity, music cue triggers, screen tint | (not yet prototyped) |

Current progressive resource reveal (top bar hiding unneeded resources) and
the context-sensitive bottom panel (Section 18.3) are Channel 1 and Channel 3
prototypes respectively.

**Priority stack:**
```
Threat > Command > Economy > Information > Atmosphere
```

When multiple channels compete for the same screen real estate or attention
budget, higher-priority channels suppress lower ones. Suppressed messages
queue and replay during the next CALM phase (Section 2.2).

**Attention budget:** Each frame has a finite "attention token" pool (tuned
per difficulty). Channels bid for tokens; the director allocates top-down by
priority, guaranteeing that critical threat information is never buried under
economy spam.

**Player profile tracking:** The director maintains a rolling profile of
player behavior — APM, camera movement patterns, selection frequency,
reaction time to incidents. Over a session it classifies the player on two
axes: **tempo** (fast/slow) and **focus** (macro/micro). The profile biases
channel thresholds:
- Fast-macro players see fewer tooltips, more sparklines
- Slow-micro players see more formation hints, fewer economy nudges

The profile persists only within a single game session (no cross-session
storage in current design).

> Full specification: see **GDD_Roadmap.md § Presence Director**.

---

## 19. Visual Rendering

### 19.1 Algorithmic Unit Shapes
- **Gatherers:** Hexagonal shape with resource-colored carry indicator
- **Wardens:** Polar rose pattern with shield element
- **Rangers:** Fibonacci spiral with bow element
- **Enemies:** Dark-tinted versions of corresponding player shapes

All drawn with `pygame.draw` — no sprite assets.

### 19.2 Map Rendering
- Terrain surface cached — only rebuilt on tile changes or zoom changes
- Dirty flag system: `_map_dirty` for tile changes, `_minimap_dirty` for minimap
- Grid lines at zoom ≥ 0.7×

### 19.3 Unit Rendering
- Insertion sort on pre-maintained `_sorted_units` list (O(n) for nearly-sorted data)
- Garrisoned units skipped
- Health bars (fractal) above damaged units
- Selection rings (Koch-snowflake) for selected units

### 19.4 Pause Menu
- Radial gradient background (cached)
- Koch depth-2 border on panel
- Fractal font for title (36px), menu items (18px), footer (11px)

---

## 20. Performance Systems

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

## 21. Event Logging

CSV-based logging to `logs/` directory. Events:

| Event Type | Details Logged |
|---|---|
| INCIDENT_START | Incident flavour, enemy count, composition, tier |
| INCIDENT_RESOLVED | Incident number, outcome, time taken |
| UNIT_KILLED | Killer type, killed type, killer rank, bounty |
| PLAYER_UNIT_LOST | Lost unit type, killer type, lost rank, lost XP |
| BUILDING_RUINED | Building type, damage source |
| BUILDING_DESTROYED | Building type, damage source |
| BUILDING_PLACED | Building type |
| BUILDING_COMPLETE | Building type |
| TRAINING_STARTED | Unit type |
| RESOURCE_DEPOSIT | Resource type, amount |
| RANK_UP | Unit type, new rank, owner |
| WORKER_RANK_UP | Gatherer skill, new rank |
| TOWER_UPGRADE | Sentinel level |
| ENEMY_ESCAPED | Enemy type, XP carried |
| FORMATION_DISCOVERED | Formation type |
| SURRENDER | — |
| GAME_SUMMARY | Outcome, kills, losses, bounty, buildings, resources |

---

## 22. Game State & Win Conditions

**Victory:** All incidents survived (incident_number ≥ incidents_required) AND all enemy units dead.
**Defeat:** All player buildings destroyed (including ruins — all `alive = False`).
**Surrender:** F10 key.

**Game-over screen:** Performance grade, tips (different for victory/defeat), and fractal font rendering.

---

## 23. Architecture

```
rts/
  main.py            — Entry point, pygame init, menu → game
  menu.py            — Main menu with Mandelbrot fractal background + fractal font
  game.py            — Game class: update/render loop, input, global commands, pause menu
  constants.py       — All constants, difficulty profiles, incident catalogue, unit/building defs, trait system
  utils.py           — dist, clamp, tile_center, pos_to_tile, draw_text, ruin_rebuild_cost
  game_map.py        — Procedural terrain gen, harvest, passability
  camera.py          — Pan/zoom/clamp/transforms
  resources.py       — ResourceManager (Flux, Fiber, Ore, Alloy, Crystal)
  entity_base.py     — Entity base class (v10_5 split from entities.py)
  unit.py            — Unit class: physics movement, energy, combat, gathering, building,
                       fleeing, XP/rank, traits, arrow firing, spring formations,
                       target scoring, retargeting, morale, stances, Gatherer skills,
                       garrison, attack-move, Harmonic Pulse buff, metamorphosis
  building.py        — Building class: construction, training queue, Harmonic Mill, Forge,
                       resonance field, ruin system, garrison, rally point, Harmonic Pulse,
                       production buildings, helper drop-offs
  building_shapes.py — Algorithmic building shape drawing functions
  projectiles.py     — Arrow with parabolic arcs + lead aiming
  entities.py        — Re-export facade (backward compat)
  squads.py          — SquadManager: player-driven squads, 4 fractal formation calculators,
                       type-aware slot assignment, spring positioning, formation combat
                       (sweep/pulse/contract), harmonic resonance, discovery system
  enemy_ai.py        — Incident Director FSM, tension system, dramatic arc, counter-pick AI,
                       incident catalogue, straggler processing
  gui.py             — HUD: top bar, bottom panel, buttons, formation/stance UI,
                       tooltips, message log, tutorial hints (fractal GUI)
  fractal_font.py    — Geometric fractal font renderer (stroke-based, glow, any size)
  fractal_ui.py      — Koch borders, radial gradients, fractal bars, resource icons,
                       selection rings
  pathfinding.py     — A* with weighted terrain (4000 node limit)
  spatial_grid.py    — O(1) spatial neighbor queries for unit interactions
  advisor.py         — Don't Panic live advisor (rule-based diagnostic)
  presence.py        — Presence Director: adaptive GUI conductor (v10_zeta)
  event_logger.py    — CSV event recording + game summary
```

**Entity Hierarchy:**
```
Entity (eid, x, y, hp, max_hp, owner, alive, last_attacker, frontal_armor)
  ├── Unit (state machine, physics velocity, energy pool, commands, combat,
  │         gathering, building, fleeing, XP/rank, traits, arrow firing,
  │         spring formation gravitation, target scoring, retargeting,
  │         morale, fractal formations, stances, Gatherer skills,
  │         garrison, attack-move, Harmonic Pulse buff, rooting,
  │         metamorphosis, waypoint queue)
  └── Building (construction, training queue, Harmonic Mill, Fractal Forge,
                resonance field, ruin system, garrison, rally point,
                Harmonic Pulse, production generation, helper drop-off,
                scaffold aura, Smelter boost)
```
