# Game Design Document - Simple RTS v9.3 (Current)

> Auto-generated from source code. Reflects the actual implemented state of all systems.
> Last updated: 2026-03-12

---

## 1. Overview

**Title:** Simple RTS
**Tagline:** Gather, Build, Survive!
**Engine:** Python 3 + Pygame 2.6.1
**Distribution:** PyInstaller single-file .exe (console hidden)
**Resolution:** 1280 x 720 @ 60 FPS

**Core Loop:** Gather resources, construct buildings, train units, and survive escalating enemy waves. Units gain XP from combat hits, rank up through 5 military ranks, and self-organize into squads under higher-ranked leaders. Archers fire ballistic arrows that can miss, with accuracy improving as they rank up. Units use utility-scored targeting to prioritize high-value targets, retarget mid-combat when threatened, and navigate weighted terrain with movement penalties. Enemy hordes check local morale and flee when outnumbered. Victory is achieved by surviving all waves for the chosen difficulty. Defeat occurs when all player buildings are destroyed.

**What's New in v9:**
- Ballistic archery with accuracy spread and ground arrows
- XP-based military rank system (5 ranks: Recruit to Captain)
- Squad behavior with rank-based leadership
- Smarter enemy flee decisions and XP-carrying veteran returns

**v9.1 — Utility-Scored Target Priority:**
- All units use `_score_target()` with base priority, distance falloff, HP modifier, engagement stickiness, and rank-scaled noise
- Towers use inline scoring with threat-type bonuses and low-HP finishing
- Enemies prioritize Town Halls and high-value buildings over lone workers

**v9.2 — Enemy Horde Morale & Player Formations:**
- Enemies check local force ratio every 1s; outnumbered grunts flee to regroup or leave the map
- Sergeant+ leaders suppress morale flight within 120px aura
- Player combat units use soft formation hints: soldiers forward, archers back, rank-based push

**v9.3 — Live Retargeting, Terrain Passability, Menu Fix:**
- Units retarget every 1.5s during combat; attacker tracking gives 2.5x threat bonus to "who's hitting me"
- Terrain split: deep water (impassable) vs shallow water (passable, slow); trees/resources passable but slow
- Weighted A* pathfinding with terrain cost multipliers; actual movement speed reduced on difficult terrain
- Main menu button text overflow fixed (wider buttons, smaller font)

---

## 2. Difficulty System

Three selectable profiles from the main menu (hotkeys 1/2/3). Each profile tunes 19 parameters:

| Parameter | Easy | Medium | Hard |
|---|---|---|---|
| Starting Gold | 300 | 200 | 150 |
| Starting Wood | 150 | 100 | 80 |
| Starting Iron | 0 | 0 | 0 |
| Starting Steel | 0 | 0 | 0 |
| Starting Workers | 4 | 3 | 3 |
| First Wave (seconds) | 360 | 300 | 210 |
| Wave Interval (seconds) | 120 | 90 | 75 |
| Max Waves | 15 | 20 | 25 |
| Wave Count Base | 4 | 5 | 8 |
| Wave Count Scale | 3 | 4 | 5 |
| HP Scale / Wave | +5% | +8% | +10% |
| ATK Scale / Wave | +3% | +5% | +7% |
| Archers Unlock (wave) | 4 | 3 | 2 |
| Siege Unlock (wave) | 8 | 6 | 4 |
| Elite Unlock (wave) | 18 | 15 | 12 |
| Multi-dir Waves (wave) | 14 | 12 | 8 |
| 3-dir Waves (wave) | 20 | 18 | 14 |
| Kill Bounty Base | 5 | 3 | 2 |
| Wave Bonus Gold | 30 | 20 | 10 |
| Wave Bonus Wood | 15 | 10 | 5 |
| Wave Bonus Steel | 3 | 2 | 1 |

**Wave Size Formula:** `count = wave_base + wave_scale * sqrt(wave_number)`
**Kill Bounty Formula:** `bounty = kill_bounty_base + wave_number` (gold per kill)
**Wave Completion Bonus:** `bonus_gold + wave# * 2`, `bonus_wood + wave#`, `bonus_steel + wave# / 3`

---

## 3. Map & Terrain

- **Grid:** 128 x 128 tiles, 32px per tile
- **World Size:** 4096 x 4096 pixels
- **Terrain Types:**

| ID | Terrain | Color (RGB) | Passable | Buildable | Move Cost | Notes |
|---|---|---|---|---|---|---|
| 0 | Grass | (46, 139, 87) | Yes | Yes | 1.0x | Default terrain |
| 1 | Deep Water | (30, 90, 200) | **No** | No | — | Impassable, lake centers |
| 2 | Tree | (20, 100, 20) | Yes | No | 2.0x | Harvestable (wood), slow to traverse |
| 3 | Gold | (218, 165, 32) | Yes | No | 1.8x | Harvestable (gold), rocky |
| 4 | Iron | (140, 140, 155) | Yes | No | 1.8x | Harvestable (iron), rocky |
| 5 | Shallow Water | (60, 130, 220) | Yes | No | 2.5x | Wading, auto-generated around deep water |

**Passability Model (v9.3):**
- `is_passable(c, r)` — Returns True for any terrain type in `TERRAIN_MOVE_COST` (everything except deep water). Used by pathfinding.
- `is_walkable(c, r)` — Returns True only for grass. Used for building placement.
- `is_buildable(c, r)` — Alias for `is_walkable`.
- Units can walk through trees, gold, iron, and shallow water — but at reduced speed.
- Harvesting depletes resource tiles, converting them to grass (cost 1.0x) — creating cleared paths.

**Shallow Water Generation (v9.3):**
- After deep water lake clusters are placed, a border pass scans all grass tiles
- Any grass tile adjacent (8-directional) to deep water becomes `TERRAIN_SHALLOW_WATER`
- Creates natural-looking lakes: impassable deep center, passable but slow shores

**Procedural Generation:**
- 8-12 water lakes (random walk clusters, 15-40 tiles each) + shallow water borders
- 15-22 tree forests (random walk clusters, 8-30 tiles each)
- 5-8 gold deposits (clusters of 3-6 tiles)
- 4-7 iron deposits (clusters of 3-6 tiles)
- 3 guaranteed tree clusters near start (7-12 tiles away, 6-15 tiles each)
- 2 guaranteed gold deposits near start (8-14 tiles away, 3-5 tiles each)
- 9x9 tile clear zone around map center for starting base

**Resource Capacities:**
| Resource Tile | Capacity (harvest trips) |
|---|---|
| Tree | 50 units |
| Gold | 80 units |
| Iron | 60 units |

When a tile's resources are fully harvested, it converts to grass (walkable, buildable, 1.0x speed).

---

## 4. Resources

Four resource types managed by `ResourceManager`:

| Resource | Icon Color | Primary Source | Secondary Source |
|---|---|---|---|
| Gold | (255, 215, 0) | Gold tiles | Kill bounty, wave bonus |
| Wood | (34, 180, 34) | Tree tiles | Wave bonus |
| Iron | (170, 170, 185) | Iron tiles | - |
| Steel | (100, 160, 220) | Refinery (2 iron -> 1 steel) | Wave bonus |

Iron is the gateway to steel, making it the long-term bottleneck. Steel gates soldiers, archers, and towers.

---

## 5. Buildings

All buildings are player-side only. Built by workers through right-click assignment.

### 5.1 Building Stats

| Building | Gold | Wood | Iron | Steel | HP | Build Time | Size |
|---|---|---|---|---|---|---|---|
| Town Hall | 200 | 120 | 0 | 0 | 500 | 30s | 2x2 |
| Barracks | 120 | 80 | 0 | 0 | 400 | 18s | 2x2 |
| Refinery | 80 | 60 | 30 | 0 | 300 | 22s | 2x2 |
| Tower | 60 | 40 | 0 | 25 | 220 | 18s | 1x1 |

### 5.2 Building Functionality

**Town Hall:**
- Trains workers (Q key, cost: 50g, 8s train time)
- Resource drop-off point (workers auto-return here)
- Passive healing aura: heals friendly units within 192px (6 tiles) at 2 HP/s
- Primary win condition anchor

**Barracks:**
- Trains soldiers (W key, cost: 75g 8s, 13s train)
- Trains archers (E key, cost: 55g 25w 4s, 11s train)
- Training queue (FIFO)

**Refinery:**
- Auto-refines: consumes 2 iron, produces 1 steel every 6 seconds
- Operates continuously while iron is available
- No manual interaction needed

**Tower:**
- Auto-attacks enemies within 200px range using utility scoring (v9.1)
- 11 damage per shot, 2.0s cooldown
- Fires **homing projectiles** (guaranteed hit, unlike archer arrows)
- Target scoring: `UNIT_PRIORITY × threat_type_bonus × low_HP_bonus × distance_factor`
- Prioritizes elites (1.5x) and siege (1.8x), finishes wounded targets (<30% HP gets 2.0x)

### 5.3 Building Collision

Buildings occupy their tile footprint. All tiles under a building are added to the pathfinding blocked set. Units path around buildings using A*.

### 5.4 Building Ruin System

When a completed player building reaches 0 HP:
- It does NOT die. Instead it becomes a **ruin**
- `ruined = True`, `built = False`, `build_progress = 0.0`
- Retains 10% of max HP (minimum 1)
- All training queues and refining are halted
- Rendered at 1/3 brightness
- Enemies deprioritize ruins (15% of base priority via RUIN_PRIORITY_MULT)
- Ruins can still be attacked and destroyed permanently (second time = `alive = False`)

**Rebuilding Ruins:**
- Right-click workers onto a ruin
- Costs 40% of the original building cost
- Workers then build it as normal (same build time)
- Upon completion, building is fully restored to max HP

---

## 6. Units

### 6.1 Player Units

| Unit | Gold | Wood | Steel | HP | Speed | ATK | Range | ATK CD | Train Time |
|---|---|---|---|---|---|---|---|---|---|
| Worker | 50 | 0 | 0 | 50 | 80 | 4 | 40 | 1.0s | 8s |
| Soldier | 75 | 0 | 8 | 130 | 70 | 14 | 40 | 1.0s | 13s |
| Archer | 55 | 25 | 4 | 75 | 75 | 9 | 170 | 1.4s | 11s |

**Visual Radii:** Worker 10px, Soldier 12px, Archer 11px

### 6.2 Enemy Units (Base Stats, Before Wave Scaling)

| Unit | HP | Speed | ATK | Range | ATK CD | Special |
|---|---|---|---|---|---|---|
| Enemy Soldier | 100 | 55 | 12 | 40 | 1.2s | - |
| Enemy Archer | 60 | 50 | 6 | 140 | 1.8s | - |
| Enemy Siege | 200 | 35 | 20 | 40 | 3.0s | 2x damage vs buildings |
| Enemy Elite | 160 | 60 | 18 | 40 | 1.0s | Fast, high DPS |

**Wave Scaling:** Each wave, enemy stats multiply:
- HP: `base_hp * (1.0 + hp_scale * wave_number)`
- ATK: `base_atk * (1.0 + atk_scale * wave_number)`

### 6.3 Unit States (State Machine)

| State | Description |
|---|---|
| `idle` | No current task. Combat units auto-aggro within `range + 64px`. Squad followers assist leader or follow |
| `moving` | Following A* path to destination |
| `gathering` | Worker harvesting a resource tile |
| `returning` | Worker carrying resources back to Town Hall |
| `building` | Worker constructing/rebuilding a building |
| `attacking` | Engaged with target, chasing if out of range. Retargets every 1.5s (v9.3) |
| `repairing` | Worker repairing a damaged building |
| `fleeing` | Worker fleeing enemies / enemy fleeing to map edge / enemy morale flee (v9.2) |

### 6.4 Worker Behaviors

**Gathering:**
- Walk to resource tile, harvest over time
- Gather times: Wood 2.0s, Gold 3.0s, Iron 3.0s
- Gather amount: 10 per trip (iron: 15 per trip)
- Auto-return to nearest Town Hall to deposit
- Auto-resume: if tile depletes, find nearest tile of same resource type
- Remembers last gather type for resume after interruption

**Building:**
- Right-click on placed/unbuilt building to assign
- Must be within 2.5 tiles to build
- Multiple workers can build same building simultaneously
- `b.hp = b.max_hp` on completion (critical for ruins rebuild)

**Repairing:**
- Right-click on damaged built building
- Heals 15 HP/s per worker
- Costs 15% of building's gold/wood cost across full repair (0 to max)
- Proportional cost per tick

**Fleeing (Worker):**
- Triggers when enemy is within 160px
- Saves current task state (gather tile, build target, carry amount, etc.)
- Paths 6 tiles away from nearest enemy
- After 2.0s of safety (no enemies within 160px), resumes saved task
- Re-paths to original work target on resume

### 6.5 Unit Separation & Squad Cohesion

All units push apart when stationary (idle, gathering, building, attacking, repairing):
- Separation distance: 20px
- Separation force: 50 px/s
- Applies to both player and enemy units (within own faction)
- Prevents unit stacking

**Squad Cohesion (v9):** Non-worker units with a squad leader are gently pulled toward their leader:
- Cohesion force: 35 px/s
- Activates when distance to leader exceeds 50% of follow distance (30px)
- Pull strength scales linearly with distance

### 6.6 Formation Hints (v9.2)

Player combat units receive soft positional forces that create organic formations:

**Front Direction Calculation:**
- If the unit's squad leader has an attack target → direction toward that target
- Otherwise → direction toward the nearest enemy
- Fallback → no formation force applied

**Type-Based Positioning:**
- **Soldiers:** Pushed forward toward the enemy by `FORMATION_FRONT_OFFSET` (30px)
- **Archers:** Pushed behind the front line by `FORMATION_REAR_OFFSET` (35px)
- **Workers:** No formation force

**Rank-Based Push:**
- Lower-ranked units are pushed further forward: `rank_diff = leader_rank - unit_rank`
- Additional forward offset: `FORMATION_RANK_PUSH * rank_diff` (5px per rank difference)
- Effect: Recruits serve as front-line shields, officers stay protected

**Force Parameters:**
- Force strength: 25 px/s (gentle, not robotic)
- Dead zone: 5px (no jitter when close to ideal position)
- Applied as part of the separation pass, weaker than cohesion/separation

### 6.7 Terrain Movement Speed (v9.3)

Unit movement speed is divided by the terrain cost multiplier at their current position:
- `effective_speed = base_speed / TERRAIN_MOVE_COST[current_tile]`
- Applies to both path-following and chase-target movement
- Projectiles (tower bolts, arrows) are NOT terrain-slowed
- Walking through trees at 2.0x cost means half speed; through shallow water at 2.5x means 40% speed
- Clearing trees via harvesting opens fast-travel paths (grass = 1.0x)

---

## 7. XP & Military Rank System (v9 — replaces v8 Veterancy)

### 7.1 XP Acquisition

| Event | Player XP | Enemy XP |
|---|---|---|
| Dealing a hit (melee) | +1 | +1 |
| Arrow hits target | +1 | +1 |
| Killing a target | +3 bonus | +2 bonus |

- Workers do NOT gain combat XP
- XP is tracked per-unit, not shared
- Enemies accumulate XP during combat but do NOT rank up mid-fight

### 7.2 Military Ranks

| Rank | Name | XP Threshold | HP Mult | ATK Mult | Range Bonus | Accuracy Bonus |
|---|---|---|---|---|---|---|
| 0 | Recruit | 0 | 1.00x | 1.00x | +0 | +0.00 rad |
| 1 | Veteran | 10 | 1.08x | 1.06x | +5 | +0.03 rad |
| 2 | Corporal | 30 | 1.16x | 1.12x | +10 | +0.06 rad |
| 3 | Sergeant | 70 | 1.26x | 1.20x | +18 | +0.10 rad |
| 4 | Captain | 140 | 1.40x | 1.30x | +25 | +0.15 rad |

**Stat Calculation:** All bonuses are computed from base (unscaled) values:
- `max_hp = base_hp * hp_mult`
- `attack = base_attack * atk_mult`
- `range = base_range + range_bonus`
- HP ratio is preserved on rank-up (e.g., if unit was at 80% HP, it stays at 80%)

### 7.3 Rank Colors

| Rank | Color | RGB |
|---|---|---|
| 0 - Recruit | Gray | (140, 140, 140) |
| 1 - Veteran | Bronze | (205, 127, 50) |
| 2 - Corporal | Silver | (192, 192, 210) |
| 3 - Sergeant | Gold | (255, 215, 0) |
| 4 - Captain | Diamond Blue | (80, 180, 255) |

### 7.4 Worker Specialization (unchanged from v8)

- **Threshold:** Gather 500 total units of a single resource type
- **Bonus:** +10% gather speed for that resource (reduced gather time)
- **Visual:** Colored pip matching specialized resource (green=wood, gold=gold, grey=iron)
- **Notification:** Floating text on specialization trigger
- **Limit:** One specialization per worker (first resource to hit 500 wins)

---

## 8. Ballistic Archery System (v9)

### 8.1 Overview

Archers (both player and enemy) fire **ballistic arrows** — real projectiles that travel in a straight line with accuracy spread. Arrows can miss their target. Towers retain homing projectiles (guaranteed hit).

### 8.2 Arrow Properties

| Property | Value |
|---|---|
| Speed | 350 px/s |
| Max Flight Time | 2.0 seconds |
| Hit Radius | 12px |
| Base Spread (Recruit) | 0.18 radians (~10.3 degrees) |
| Min Spread (Captain) | 0.03 radians (~1.7 degrees) |

**Spread Formula:** `spread = max(ARROW_MIN_SPREAD, ARROW_BASE_SPREAD - rank_accuracy_bonus)`

### 8.3 Arrow Lifecycle

1. **Fire:** Archer calculates direction to target, applies random angular spread, creates Arrow
2. **Flight:** Arrow moves in straight line at 350 px/s for up to 2 seconds
3. **Hit Detection:** Each frame, checks all valid targets within 12px radius
4. **On Hit:** Deals damage, grants XP to source archer, arrow destroyed
5. **On Miss (lifetime expired / off-map):** Arrow becomes grounded

### 8.4 Ground Arrows

- Missed arrows stick in the ground as visual reminders
- Persist for 8 seconds, then fade
- Maximum 50 ground arrows at once (oldest culled when exceeded)
- Cleared between waves for visual cleanliness
- Drawn below units (ground layer)

### 8.5 XP from Arrows

- XP is granted to the **source archer** when an arrow hits
- If the hit kills the target, kill bonus XP is also granted to the source archer
- If the source archer died before the arrow lands, no XP is granted

---

## 9. Squad System (v9)

### 9.1 Overview

Units self-organize into squads based on military rank. Higher-ranked units become squad leaders; lower-ranked units follow and assist them. This creates emergent auto-battler behavior.

### 9.2 Squad Formation Rules

- **Reassignment Interval:** Every 2.0 seconds, squads are fully rebuilt
- **Leader Eligibility:** Any military unit with rank >= 1 (Veteran or higher)
- **Max Squad Size:** 6 (1 leader + 5 followers)
- **Assignment:** Unassigned units are assigned to the nearest leader with room
- **Rank 0 units with no leader:** Act independently (normal auto-aggro)

### 9.3 Follower Behavior (Idle State)

When a follower is idle:
1. If leader is attacking a target: follower assists (attacks same target)
2. If leader is alive but distant (>60px): follower moves toward leader
3. Otherwise: normal auto-aggro behavior

### 9.4 Squad Cohesion

- Non-separation force that gently pulls followers toward their leader
- Activates when distance to leader > 30px (50% of follow distance)
- Pull force: 35 px/s, scales with distance
- Works alongside unit separation (push-apart stays active)

### 9.5 Enemy Squads

- Enemy units also form squads via a separate SquadManager
- Returning veterans with accumulated XP/ranks become natural squad leaders
- Creates organized enemy groups (higher-ranked returnees lead fresh spawns)

---

## 10. Target Priority System (v9.1)

### 10.1 Utility-Scored Targeting

All units (player and enemy) use a `_score_target(target)` method that produces a floating-point priority score. The highest-scoring target wins.

**Score Formula:**
```
base_priority                          # from BUILDING_PRIORITY or UNIT_PRIORITY tables
  × distance_falloff                   # 1.0 / (1.0 + distance / 300)
  × hp_modifier                        # 1.3x bonus for targets below 40% HP
  × engagement_stickiness              # 1.15x if target is our current attack target
  × threat_modifier (v9.3)             # 2.5x if target is our last_attacker
  × (1 + random_noise * rank_noise)    # rank-scaled noise: ±50% for Recruit, 0% for Captain
```

### 10.2 Priority Tables

**Building Priority:**
| Building | Base Score |
|---|---|
| Town Hall | 10.0 |
| Tower | 7.0 |
| Barracks | 6.0 |
| Refinery | 5.0 |

**Unit Priority:**
| Unit | Base Score |
|---|---|
| Enemy Siege | 7.0 |
| Enemy Elite | 6.0 |
| Archer | 4.5 |
| Enemy Archer | 4.5 |
| Soldier | 4.0 |
| Enemy Soldier | 4.0 |
| Worker | 1.0 |

**Modifiers:**
- `RUIN_PRIORITY_MULT = 0.15` — ruins scored at 15% of their base priority
- `DISTANCE_NORMALIZATION = 300px` — at 300px distance, score halved
- `LOW_HP_FINISH_BONUS = 1.3` — wounded targets (<40% HP) are 30% more attractive
- `ENGAGED_TARGET_BONUS = 1.15` — slight stickiness to prevent constant switching
- `THREAT_BONUS = 2.5` (v9.3) — the enemy attacking you is 2.5x more attractive

**Rank Targeting Noise:**
| Rank | Noise Range |
|---|---|
| 0 - Recruit | ±50% |
| 1 - Veteran | ±30% |
| 2 - Corporal | ±15% |
| 3 - Sergeant | ±5% |
| 4 - Captain | 0% (perfect decisions) |

### 10.3 Tower Targeting (v9.1)

Towers use a separate inline scoring formula:
```
score = UNIT_PRIORITY[type] × threat_type_bonus × low_hp_bonus × (1 / (1 + dist/TOWER_RANGE))
```
- `TOWER_HIGH_THREAT_TYPES`: Elite 1.5x, Siege 1.8x
- `TOWER_LOW_HP_BONUS = 2.0` for targets below 30% HP
- Towers have no noise (always optimal targeting)

### 10.4 Where Targeting Is Used

1. **Idle auto-aggro** (`_idle_behavior`): Scans range+64px, picks `max(candidates, key=_score_target)`
2. **Target-died retarget** (`_find_new_target`): Scans all enemies, picks best by score
3. **Enemy AI initial target** (`enemy_ai._find_target`): Uses `unit._score_target()` for all candidates
4. **Tower auto-attack** (`Building`): Inline scoring for all enemies in range

---

## 11. Live Retargeting & Threat Response (v9.3)

### 11.1 Attacker Tracking

When any entity takes damage, it records who hit it:
- `Entity.take_damage(dmg, attacker=None)` stores `self.last_attacker = attacker`
- Melee hits pass the attacking unit as `attacker`
- Arrow hits pass the `source_unit` (the archer who fired) as `attacker`
- Tower bolts pass no attacker (building, not unit)

### 11.2 Threat Bonus

In `_score_target()`, if `target is self.last_attacker` and target is alive:
- Score multiplied by `THREAT_BONUS = 2.5`
- Effect: A soldier attacking you (base 4.0 × 2.5 = 10.0) matches a Town Hall (10.0), and distance makes the nearby attacker win decisively
- Creates responsive "fight back" behavior instead of ignoring damage

### 11.3 Periodic Retarget Timer

During the `attacking` state (`_do_attack`):
- `_retarget_timer` counts up by `dt` each frame
- When timer reaches `RETARGET_INTERVAL = 1.5s`, it resets and runs a retarget check
- New target must score > `RETARGET_SWITCH_THRESHOLD × current_target_score` (1.2x = 20% better)
- Combined with `ENGAGED_TARGET_BONUS` (1.15x stickiness), a new target needs ~38% raw score improvement
- But `THREAT_BONUS` (2.5x) easily clears this threshold for "who's attacking me"
- Prevents constant jittering while still responding to real threats

---

## 12. Enemy Horde Morale (v9.2)

### 12.1 Overview

Enemy units periodically check local force ratios. When heavily outnumbered and without officer support, they flee — either regrouping with allies or escaping the map entirely. This creates horde behavior: groups attack confidently but scatter when losing.

### 12.2 Morale Check

Every `MORALE_CHECK_INTERVAL = 1.0s` (staggered start per unit):
1. Count player military units within `MORALE_SCAN_RADIUS = 160px`
2. Count enemy units in same radius
3. If enemy count is 0, skip (avoid division by zero)
4. Calculate ratio: `player_count / enemy_count`
5. Apply rank resistance: `flee_ratio = MORALE_FLEE_RATIO × MORALE_RANK_RESISTANCE[rank]`
6. If `ratio >= flee_ratio`, unit panics and flees

### 12.3 Rank Resistance

| Rank | Resistance Multiplier | Effective Flee Ratio |
|---|---|---|
| 0 - Recruit | 1.0x | 3.0 (flees at 3:1) |
| 1 - Veteran | 1.3x | 3.9 (braver) |
| 2 - Corporal | 1.6x | 4.8 (significantly braver) |
| 3 - Sergeant | 999x | Never flees (leader) |
| 4 - Captain | 999x | Never flees (leader) |

### 12.4 Leader Aura Suppression

Before a unit flees from morale:
- Scan for any allied enemy with `rank >= MORALE_LEADER_MIN_RANK (3 = Sergeant+)` within `MORALE_LEADER_AURA = 120px`
- If a leader is nearby, morale flee is **suppressed entirely**
- Effect: Sergeants and Captains act as anchors; their presence keeps grunts fighting

### 12.5 Flee Behavior (Dual Mode)

When morale breaks, the unit chooses one of two strategies:

**Regroup (default):**
- Search for the largest allied enemy cluster more than 200px away
- Path toward that cluster to join reinforcements
- Upon arrival (within 60px of destination), reset state and find a new target
- Effect: Scattered enemies reform into larger groups

**Edge Escape (fallback):**
- If no allied cluster found, path to nearest map edge
- Upon reaching edge (within 3 tiles), removed from game with XP preserved
- Returns next wave as veteran with 25% stat bonus + accumulated XP/ranks
- Same behavior as HP-based flee

---

## 13. Enemy AI

### 13.1 Wave Spawning

- Enemies spawn at map edges (top/bottom/left/right)
- After `multi_dir_wave`: 2 random edges simultaneously
- After `three_dir_wave`: 3 random edges simultaneously
- Spawn position: random along edge, seeks walkable tile (up to 30 attempts)

### 13.2 Adaptive Composition

The AI reads player defenses each wave and adjusts probabilities:

**Base Probabilities (when unlocked):**
- Elite: 10%, Siege: 15%, Archer: 30%, Soldier: remainder (min 20%)

**Adaptation Rules:**
- Player has 2+ towers: +10% siege probability
- Player has 4+ towers: +10% more siege probability
- Player army is >50% archers: +8% elite probability (melee counters ranged)
- Player army is >60% soldiers: +10% enemy archer probability (ranged counters melee)

All probabilities are normalized to sum to 1.0.

### 13.3 Enemy Targeting

Uses the utility-scored target priority system (Section 10):
- `enemy_ai._find_target(unit, game)` calls `unit._score_target()` on all candidates
- Siege units have `prefer_buildings=True` which limits candidates to buildings when available
- All enemy types prioritize high-value targets (Town Halls, Towers) over lone workers
- Recruits may make suboptimal choices due to targeting noise; Captains always pick the best target

**Auto-retarget (v9.3):** When current target dies, find best target by score. Also periodic retarget every 1.5s during combat (Section 11).

### 13.4 Enemy Flee & Veteran Return (v9 Enhanced)

**HP-Based Flee Trigger:** Enemy HP drops below 20% of max HP **AND** local force check passes

**Smart Flee (v9):** Before fleeing, enemy counts nearby forces:
- Counts player military within 160px vs enemy count in same radius
- Only flees if `player_count > enemy_count * 0.6` (outnumbered)
- If enemy has local numbers advantage, stays and fights

**Morale-Based Flee (v9.2):** See Section 12 — force ratio check independent of HP.

**Escape Behavior:** Paths to nearest map edge. If enemy reaches within 3 tiles of map border, removed from game and stored with accumulated XP.

**Veteran Return (v9 Enhanced):**
- All escaped enemies respawn with the NEXT wave
- Base stats: wave scaling * 1.25 (25% bonus on top of normal scaling)
- **XP Preserved:** Accumulated XP is restored on respawn
- **Rank Applied:** XP triggers rank calculation, then stat bonuses applied on top of wave/veteran scaling
- **Squad Leadership:** Ranked returning veterans naturally become squad leaders for fresh enemy spawns
- Random edge spawn
- Notification warns player of escapees

---

## 14. Passive Healing

- **Source:** Town Hall (must be built, not ruined, alive)
- **Radius:** 192px (6 tiles) from Town Hall center
- **Rate:** 2 HP/s
- **Targets:** All player units (workers and combat units)
- **Stacking:** Does not stack from multiple Town Halls (first found TH heals, then break)
- **Combat note:** Heals during combat if unit is near TH

---

## 15. Pathfinding (v9.3 — Weighted Terrain)

**Algorithm:** A* with 8-directional movement

**Cost Calculation:**
- Base step cost: Cardinal = 1.0, Diagonal = 1.414
- **Terrain multiplier (v9.3):** `cost = base_step × TERRAIN_MOVE_COST[tile_type]`
- Deep water tiles are excluded from pathfinding entirely (not in `TERRAIN_MOVE_COST`)

| Terrain | Move Cost | Effect on A* |
|---|---|---|
| Grass | 1.0x | Normal |
| Tree | 2.0x | Paths prefer to go around forests, but will cut through if shortcut is big enough |
| Gold / Iron | 1.8x | Rocky terrain, slight detour preference |
| Shallow Water | 2.5x | Strong preference to avoid; will wade if necessary |
| Deep Water | Impassable | Hard barrier, no path through |

**Heuristic:** Chebyshev distance (max of dx, dy)
**Node limit:** 1000 nodes max (performance cap)
**Closed set:** Prevents re-expansion of already-visited nodes
**Blocked set:** All tiles occupied by alive buildings
**Fallback:** If target tile is impassable, find nearest passable neighbor
**No-path fallback:** Returns empty path (unit idles gracefully instead of walking into walls)
**Building construction:** Excludes building's own tiles from blocked set so workers can reach it

**Movement Speed (v9.3 hotfix):**
- Actual unit movement speed is also divided by terrain cost at current position
- `effective_speed = base_speed / TERRAIN_MOVE_COST[current_tile]`
- This means both pathfinding AND movement respect terrain difficulty
- Walking through a forest: A* pays 2x cost to route through AND unit moves at 50% speed

---

## 16. Camera System

- **Pan:** WASD keys or edge scrolling (15px margin)
- **Pan Speed:** 400 px/s, divided by zoom level
- **Zoom Range:** 0.4x to 2.0x
- **Zoom Step:** 0.1 per scroll tick
- **Zoom Anchor:** Zooms toward/away from mouse cursor position
- **Clamping:** Cannot scroll past map boundaries
- **Center hotkey:** Space bar centers on first selected entity

---

## 17. Selection & Input

### 17.1 Selection

- **Single click:** Select nearest unit within 20px, or building if click is within its rect
- **Box select:** Drag to select all player units within rectangle (buildings excluded from box select)
- **Deselect:** ESC clears selection

### 17.2 Commands (Right-Click Context)

| Click Target | Worker Action | Combat Unit Action |
|---|---|---|
| Enemy unit | Attack | Attack |
| Resource tile | Gather | Move nearby |
| Unbuilt building | Build/resume | Move nearby |
| Ruined building | Rebuild (pay 40%) | Move nearby |
| Damaged building | Repair | Move nearby |
| Empty ground | Move | Move |

### 17.3 Hotkeys

| Key | Action | Context |
|---|---|---|
| 1 | Place Town Hall | Worker(s) selected |
| 2 | Place Barracks | Worker(s) selected |
| 3 | Place Refinery | Worker(s) selected |
| 4 | Place Tower | Worker(s) selected |
| Q | Train Worker | Town Hall selected |
| W | Train Soldier | Barracks selected |
| E | Train Archer | Barracks selected |
| WASD / Arrows | Pan camera | Always |
| Mouse wheel | Zoom | Cursor over game area |
| Space | Center on selection | Entity selected |
| ESC | Cancel placement / deselect | Context-dependent |
| R | Restart (same difficulty) | Game over / victory |

---

## 18. User Interface

### 18.1 Layout

| Region | Position | Height | Content |
|---|---|---|---|
| Top Bar | y=0 | 40px | Resources, wave info, population |
| Game Area | y=40 | 550px | Map, units, buildings, arrows |
| Bottom Panel | y=590 | 130px | Selection info, action buttons |
| Minimap | Upper-right | 160x160px | Terrain, units, buildings, camera rect |

### 18.2 Main Menu (v9.3)

- Difficulty buttons: 170px wide, 75px tall, 30pt font, evenly spaced with gaps
- Easy (green accent, key [1]), Medium (gold accent, key [2]), Hard (red accent, key [3])
- Exit button: 220px wide, centered below difficulty buttons
- Keyboard shortcuts: 1/2/3 to start, ESC to quit

### 18.3 Top Bar

- Gold/Wood/Iron/Steel counts with colored icons
- Wave counter: `Wave: X/MAX`
- Next wave timer: `Next: Xs`
- Predicted next wave size: `(~N enemies)`
- Population count

### 18.4 Bottom Panel

**Nothing Selected:** Control hints
**Building Selected:** Icon, name, HP, status (building %/training/refining/ruin rebuild cost), action buttons
**Single Unit Selected:**
- Icon with rank pips (colored circles based on rank level)
- Name with rank title (e.g., "Soldier [Veteran]")
- HP/ATK/SPD stats
- State display
- XP progress bar showing progress to next rank
- Carry info (workers)
- Specialist info (workers)
- Build buttons (workers)

**Multi-Unit Selected:**
- Unit type counts with rank distribution (e.g., "x5 (2* 1**)")
- Build buttons if all workers

### 18.5 Minimap

- 160x160px, upper-right corner (8px margin)
- Terrain base rebuilt every 2 seconds
- Player buildings: blue (ruins: dark gray)
- Player units: rank-colored (gray=recruit, bronze/silver/gold/blue for higher ranks, cyan for workers)
- Enemy units: red
- White rectangle = camera viewport
- Click to jump camera

### 18.6 Notification System

- Floating text centered at top of game area
- Fade out over duration (1s fade at end)
- Multiple notifications stack vertically (28px spacing)
- Used for: wave clears, bonus awards, escapes, rebuilds, specializations

---

## 19. Visual Rendering

### 19.1 Map Rendering

- Only visible tiles rendered (camera frustum culling)
- Tree decoration: double circle (dark/light green)
- Gold decoration: small gold circle
- Iron decoration: small triangle
- **Shallow water (v9.3):** Lighter blue (60, 130, 220), distinct from deep water (30, 90, 200)
- Grid lines shown at zoom >= 0.7x

### 19.2 Building Rendering

- Colored rectangles (2x2 or 1x1 tiles)
- Unbuilt: half brightness + build progress bar
- Ruins: 1/3 brightness
- Selected: green outline
- Label text at zoom >= 0.5x
- Training progress bar below building

### 19.3 Unit Rendering

- Colored circles with black outline
- Size based on UNIT_RADIUS
- Label text at zoom >= 0.6x
- Carry indicator: small colored dot (gold/wood/iron) at upper-right
- **Rank pip (v9):** Colored dot at upper-right for ranked units (bronze/silver/gold/blue)
- Specialist indicator: resource-colored dot at upper-left (workers only)
- Health bar above unit when damaged
- Sorted by Y-coordinate for depth ordering

### 19.4 Arrow Rendering (v9)

**In Flight:**
- Bright line in direction of travel (yellow=player, red=enemy)
- Tail trails behind arrowhead
- Small dot at arrowhead

**Grounded:**
- Short dimmed line stuck at landing angle
- Color: muted brown (120, 100, 80)
- Drawn on ground layer (below units)

### 19.5 Projectiles (Tower Only)

- Small colored circles (yellow=player, red=enemy)
- Homing: travel at 300 px/s toward target
- Despawn on arrival or target death

---

## 20. Game State & Win Conditions

**Victory:** All waves completed AND all enemy units dead
**Defeat:** All player buildings destroyed (including ruins -- if all are dead)

**Game Over Screen:**
- Semi-transparent dark overlay
- "DEFEAT" (red) or "VICTORY! (Difficulty)" (green)
- Press R to restart (same difficulty), ESC for menu

---

## 21. Architecture & File Structure

```
rts/
  main.py          - Entry point, pygame init, menu -> game loop
  menu.py          - MainMenu class, difficulty selection (v9.3: wider buttons, 30pt font)
  game.py          - Game class, master update/render, all game state
  constants.py     - All numeric constants, difficulty profiles, colors, v9-v9.3 constants
  utils.py         - Utility functions (dist, clamp, tile_center, pos_to_tile, draw_text, ruin_rebuild_cost)
  game_map.py      - GameMap class, procedural terrain generation, harvest logic, passability (v9.3)
  camera.py        - Camera class, pan/zoom/clamp/transforms
  resources.py     - ResourceManager class, afford/spend/add
  entities.py      - Entity, Unit, Building, Projectile, Arrow, SquadManager classes
  enemy_ai.py      - EnemyAI class, wave spawning, adaptive composition, veteran return with XP
  gui.py           - GUI class, top bar, bottom panel (rank pips, XP bars), buttons
  pathfinding.py   - A* implementation with weighted terrain costs (v9.3)
  sim_economy.py   - Offline economy simulation (dev tool, not used in game)
  RTS_Game.spec    - PyInstaller build spec (v9.3)
```

### 21.1 Entity Hierarchy

```
Entity (base: eid, x, y, hp, max_hp, owner, selected, alive, last_attacker)
  |
  +-- Unit (state machine, commands, combat, gathering, building, fleeing,
  |         XP/rank system, arrow firing, squad follower behavior,
  |         target scoring, retarget timer, morale check, formation hints)
  |
  +-- Building (construction, training queue, refinery, tower auto-attack w/ scoring, ruin system)

Projectile (homing: tower visual flight to target)
Arrow (v9: ballistic non-homing, accuracy spread, ground persistence, XP granting)
SquadManager (v9: periodic squad rebuild, rank-based leadership, follower assignment)
```

### 21.2 Key Interactions Between Systems

- **Resource flow:** Gather tile -> worker carry -> TH deposit -> ResourceManager -> spend on buildings/units
- **Steel pipeline:** Iron tile -> worker -> TH -> ResourceManager.iron -> Refinery auto-consume -> ResourceManager.steel
- **Wave bonus:** Wave cleared -> gold/wood/steel added directly to ResourceManager
- **Kill bounty:** Enemy dies in combat -> gold added to ResourceManager
- **Building lifecycle:** Place (pay cost) -> workers build -> functional -> take damage -> ruin -> rebuild (40% cost) -> functional again
- **XP pipeline (v9):** Hit dealt -> grant_xp() -> _check_rank_up() -> _apply_rank_bonuses() -> stat recalculation
- **Arrow pipeline (v9):** Archer attacks -> _fire_arrow() -> Arrow created with spread -> flight -> hit detection -> damage + XP grant
- **Squad pipeline (v9):** SquadManager.update() every 2s -> sort by rank -> leaders pick followers -> followers assist leader's target
- **Target priority (v9.1):** _score_target() evaluates base priority × distance × HP × engagement × threat × noise -> best target selected
- **Live retarget (v9.3):** Every 1.5s in combat -> rescore all candidates -> switch only if 20% better
- **Threat response (v9.3):** take_damage(attacker) -> store last_attacker -> _score_target gives 2.5x bonus -> unit fights back
- **Morale pipeline (v9.2):** Every 1s -> count local forces -> apply rank resistance -> check leader aura -> flee or hold
- **Formation (v9.2):** Separation pass -> compute front direction -> push soldiers forward, archers back -> rank-weighted offset
- **Terrain pipeline (v9.3):** A* uses weighted costs -> pathfinder prefers grass -> movement speed divided by terrain cost -> clearing trees opens paths
- **Worker specialization:** Deposit resources -> `total_gathered[type]++` -> threshold met -> permanent gather speed boost
- **Enemy adaptation:** Wave spawns -> read player towers/soldiers/archers -> adjust composition probabilities
- **Enemy XP pipeline (v9):** Enemy hits player -> accumulate XP silently -> flee to edge -> store XP -> respawn next wave -> apply rank + bonuses -> become squad leader

---

## 22. Balance Parameters Summary

### 22.1 Economy Constants

| Parameter | Value |
|---|---|
| Gather Time (Wood) | 2.0s |
| Gather Time (Gold) | 3.0s |
| Gather Time (Iron) | 3.0s |
| Gather Amount | 10 per trip |
| Iron Gather Amount | 15 per trip |
| Refine Cost | 2 iron |
| Refine Yield | 1 steel |
| Refine Time | 6.0s |

### 22.2 Combat Constants

| Parameter | Value |
|---|---|
| Tower Range | 200px |
| Tower Damage | 11 |
| Tower Cooldown | 2.0s |
| Unit Separation Distance | 20px |
| Unit Separation Force | 50 px/s |
| Worker Flee Radius | 160px |
| Worker Safe Timer | 2.0s |
| Worker Repair Rate | 15 HP/s |
| Repair Cost Fraction | 15% of building cost |

### 22.3 v9 Constants

| Parameter | Value |
|---|---|
| XP Per Hit (Player) | 1 |
| XP Kill Bonus (Player) | 3 |
| XP Per Hit (Enemy) | 1 |
| XP Kill Bonus (Enemy) | 2 |
| Arrow Speed | 350 px/s |
| Arrow Max Flight | 2.0s |
| Arrow Hit Radius | 12px |
| Arrow Base Spread | 0.18 rad |
| Arrow Min Spread | 0.03 rad |
| Ground Arrow Lifetime | 8.0s |
| Ground Arrow Max | 50 |
| Squad Max Size | 6 |
| Squad Follow Distance | 60px |
| Squad Reassign Interval | 2.0s |
| Squad Cohesion Force | 35 px/s |

### 22.4 v9.1 Target Priority Constants

| Parameter | Value |
|---|---|
| Town Hall Priority | 10.0 |
| Tower Priority | 7.0 |
| Barracks Priority | 6.0 |
| Refinery Priority | 5.0 |
| Soldier Priority | 4.0 |
| Archer Priority | 4.5 |
| Worker Priority | 1.0 |
| Ruin Priority Mult | 0.15 |
| Distance Normalization | 300px |
| Low HP Finish Bonus | 1.3x (below 40% HP) |
| Engaged Target Bonus | 1.15x |
| Tower Low HP Bonus | 2.0x (below 30% HP) |
| Tower Threat: Elite | 1.5x |
| Tower Threat: Siege | 1.8x |
| Rank Targeting Noise | 50%/30%/15%/5%/0% |

### 22.5 v9.2 Morale & Formation Constants

| Parameter | Value |
|---|---|
| Morale Check Interval | 1.0s (staggered) |
| Morale Scan Radius | 160px |
| Morale Flee Ratio | 3.0 (player:enemy) |
| Leader Aura Range | 120px |
| Leader Min Rank | 3 (Sergeant) |
| Formation Front Offset | 30px (soldiers) |
| Formation Rear Offset | 35px (archers) |
| Formation Force | 25 px/s |
| Formation Rank Push | 5px per rank diff |

### 22.6 v9.3 Retargeting & Terrain Constants

| Parameter | Value |
|---|---|
| Retarget Interval | 1.5s |
| Retarget Switch Threshold | 1.2 (20% better required) |
| Threat Bonus | 2.5x |
| Grass Move Cost | 1.0x |
| Tree Move Cost | 2.0x |
| Shallow Water Move Cost | 2.5x |
| Gold/Iron Move Cost | 1.8x |
| Deep Water | Impassable |

### 22.7 Healing & Building Constants

| Parameter | Value |
|---|---|
| Heal Rate Near TH | 2 HP/s |
| Heal Radius (TH) | 192px (6 tiles) |
| Ruin Rebuild Fraction | 40% of original cost |
| Worker Specialize Threshold | 500 of one resource gathered |
| Worker Specialist Speed | +10% gather speed |
| Enemy Flee HP Threshold | 20% of max HP |
| Enemy Veteran Bonus | +25% HP and ATK |

---

## 23. Known Behaviors & Edge Cases

1. **Float HP:** Healing and repair make HP fractional; all displays cast to int
2. **Ruin double-death:** A ruin can be attacked again; second time it's permanently destroyed
3. **TH heal doesn't stack:** Only first found TH heals (uses `break`)
4. **Minimap rebuild:** Terrain layer rebuilt every 2s for performance; entity dots drawn fresh each frame
5. **Wave clear detection:** Uses frame-to-frame enemy count transition (had enemies -> no enemies)
6. **Path fallback:** If A* exceeds 1000 nodes, returns empty path (unit idles gracefully)
7. **Siege vs ruins:** Siege units deprioritize ruins via RUIN_PRIORITY_MULT (0.15); they prefer functional buildings
8. **Worker resume:** Workers remember full task state through flee (gather tile, build target, carry)
9. **Building placement:** Checks against all alive buildings including ruins for overlap prevention. Requires grass tiles only (`is_walkable`)
10. **Escaped enemies:** Cleared after respawning as veterans in next wave
11. **Arrow friendly fire:** Arrows only hit enemy-faction targets (no friendly fire)
12. **Enemy XP silent:** Enemies accumulate XP during combat but ranks don't apply stat bonuses until veteran return
13. **Squad rebuild timing:** Squads fully rebuilt every 2s; dead leaders cause followers to act independently until next rebuild
14. **Rank-up HP preservation:** When a unit ranks up, HP ratio (current/max) is preserved, not absolute HP value
15. **Ground arrows cleared:** All ground arrows removed between waves for visual cleanliness
16. **Retarget stickiness (v9.3):** Engaged target bonus (1.15x) × switch threshold (1.2x) = ~38% raw score improvement needed; prevents jitter while still allowing threat response
17. **Threat bonus vs TH (v9.3):** Soldier attacking you scores 4.0 × 2.5 = 10.0, equal to a Town Hall at base, but nearby distance makes attacker win decisively
18. **Morale leader absence (v9.2):** If all Sergeant+ enemies die, remaining grunts lose aura protection and may scatter rapidly
19. **Morale regroup (v9.2):** Enemies that morale-flee toward allies will re-engage with a fresh target on arrival; not permanently demoralized
20. **Terrain speed double-dip (v9.3):** Both A* routing AND movement speed respect terrain cost; forests are doubly expensive (longer route + slower travel). This is intentional — creates strong incentive to harvest paths through forests
21. **Shallow water generation order (v9.3):** Shallow borders are added after deep water but before trees/resources; tree clusters placed later may overwrite some shallow water tiles
22. **Building still grass-only (v9.3):** Despite trees/resources being passable, buildings can only be placed on grass tiles
