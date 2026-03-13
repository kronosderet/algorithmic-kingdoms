# GDD Roadmap — Algorithmic Kingdoms

> Living document. Tracks planned versions, design decisions, and the Godot migration path.
> Current implemented version: **v10_4** (see `GDD_Current_v10.md` for full spec)
> Last updated: 2026-03-13

---

## Version Pipeline

| Version | Codename | Status | Scope |
|---|---|---|---|
| v9.3 | Tactical Depth | **SHIPPED** | Ballistic archery, XP ranks, squads, morale, formations, retargeting, terrain |
| v10 Phase 1 | Economy Foundation | **SHIPPED (v10_4)** | Stone, worker skill XP, tower cannon, traits, garrison, global commands, perf |
| v10 Phase 2 | Economy Depth | **NEXT** | Helper buildings (drop-offs), production buildings, Forge |
| v11 | Visual Overhaul | PLANNED | Dynamic unit animations, rank/trait visual pips, terrain water return |
| v12 | Godot Migration | PLANNED | Full port to Godot 4 + GDScript, same gameplay, new renderer |

---

## v10 Phase 1 — Economy Foundation (SHIPPED)

Everything below is implemented and playable in v10_4:

### Shipped Features

| Feature | Version | Summary |
|---|---|---|
| Stone resource | v10 | 6th terrain type, 3-5 map deposits, used for towers + garrison bell |
| Worker Skill XP | v10 | 6 skill tracks (lumber/gold/iron/stone/builder/smelter), 3 ranks, +15%/+30% speed |
| Tower Cannon Overhaul | v10c | Ballistic cannonballs (Lv1: 45dmg single, Lv2: 50+35 AoE splash), steel upgrade |
| Procedural Traits | v10_1 | 10 traits with cached modifiers, applied to player + enemy units |
| Control Groups | v10_1 | Ctrl+0-9 assign, 0-9 recall, double-tap centers camera |
| Enemy Inspection | v10_2 | Left-click enemy to view stats, rank, traits (read-only panel) |
| Town Hall Garrison | v10_2 | Workers barricade in TH: 5%/worker armor (max 50%), stone-hurling counter-attack |
| Global Commands | v10_2 | Defend Base, Hunt Enemies, Town Bell (resource cost), Resume Work |
| Hold Ground / Attack-Move | v10_2 | GUI buttons for soldiers/archers (no hotkey conflict with WASD) |
| Water Removal | v10_3 | Water terrain stripped (will return in v11 terrain overhaul) |
| Visual Pip Cleanup | v10_3 | Rank/trait visual indicators removed (will return in v11 visual overhaul) |
| Spatial Grid | v10_4 | O(1) neighbor queries for separation + aggro (replaces O(n²)) |
| Map Caching | v10_4 | Terrain surface cached, rebuilt only on tile change |
| Insertion Sort | v10_4 | O(n) depth ordering for unit rendering |
| Minimap Dirty Flags | v10_4 | Rebuild on change only (replaces 2s timer) |
| Player Death Logging | v10_4 | PLAYER_UNIT_LOST event with killer, rank, XP lost |

### Balance Observations (from v10_4 playtesting)

Identified but NOT yet tuned — balance pass deferred to after Phase 2.

**First clean playtest (Medium, 35min, Victory — all 20 waves):**

| Metric | Value | Concern |
|---|---|---|
| Player unit deaths | 5 (all in waves 16-18) | Zero deaths waves 1-15 = no mid-game tension |
| Training gap | 449s (waves 9-13) with zero consequence | Veterans too self-sufficient |
| Kill split | Archer 41%, Soldier 39%, Tower 21% | Tower contribution drops late-game |
| Enemies escaped | 22 (mostly siege) | Siege walks past defense unchallenged |
| Garrison usage | **Zero** | System not intuitive or not needed |
| Workers trained | 6 (never expanded) | 6 workers sustain entire game |
| Late-game economy | Collapsed wave 17+, still won | Resources irrelevant end-game |
| Worker flee events | 530 flee + 529 resume (47% of log) | Flee/resume ping-pong spam |

**Rebalance targets (post Phase 2):**

| Issue | Severity | Proposed Fix |
|---|---|---|
| Veterancy snowball | HIGH | Diminishing returns on rank bonuses OR faster enemy HP scaling |
| Siege escaping | HIGH | Tower AI prioritizes siege; siege gets aggro "taunt" radius |
| Late economy irrelevant | MEDIUM | Unit upkeep cost or maintenance mechanic |
| Worker flee spam | MEDIUM | 5s cooldown between flee→resume cycles |
| Training queue uncapped | LOW | Cap queue at 5 per building for timing pressure |
| Garrison unused | LOW | Auto-suggest when TH under attack, or lower cost |
| Wave pacing flat | LOW | Accelerate intervals in late waves or add variance |

---

## v10 Phase 2 — Economy Depth (NEXT)

Transform the economy from "gather piles until they run out" into two-phase progression with skilled workers building infrastructure.

### 10.2.1 Foreman Powers — Helper Buildings

When a Foreman-rank worker is gathering, a new build option appears. Helper buildings are 1×1 structures that serve as local resource drop-off points (cutting worker round-trip time).

| Worker Skill | Helper Building | Function |
|---|---|---|
| Gold Miner Foreman | Goldmine Hut | Local gold drop-off |
| Lumberjack Foreman | Lumber Camp | Local wood drop-off |
| Stone Mason Foreman | Quarry Hut | Local stone drop-off |
| Iron Miner Foreman | Iron Depot | Local iron drop-off |
| Builder Foreman | Scaffold | Passive aura: +25% build/repair speed nearby |
| Smelter Foreman | — | Upgrades existing Refinery: +30% refine speed |

**Drop-off buildings** are the key mechanic: workers deposit resources there instead of walking back to Town Hall. Placement near resource clusters matters. Drop-off buildings auto-transfer stored resources to TH periodically.

### 10.2.2 Master Powers — Production Buildings

Masters can upgrade helper buildings into 2×2 production buildings that generate resources passively (slow alone, 3-4× faster with workers stationed inside).

| Helper Building | Upgrades To | Production |
|---|---|---|
| Lumber Camp | Sawmill | Generates wood passively + worker boost |
| Goldmine Hut | Goldmine | Generates gold passively + worker boost |
| Quarry Hut | Stoneworks | Generates stone passively + worker boost |
| Iron Depot | Iron Works | Generates iron passively + worker boost |
| (Refinery) | Forge | Stone + Iron → Steel at 2:1 (faster path) |

Production buildings are the "second half economy" — when natural tiles deplete, these keep resources flowing.

### 10.2.3 Building Stats (Draft)

| Building | Cost | HP | Build Time | Size | Function |
|---|---|---|---|---|---|
| Goldmine Hut | 40g 30w | 150 | 12s | 1×1 | Gold drop-off |
| Lumber Camp | 30g 40w | 150 | 12s | 1×1 | Wood drop-off |
| Quarry Hut | 40g 30w 10st | 150 | 12s | 1×1 | Stone drop-off |
| Iron Depot | 40g 30w | 150 | 12s | 1×1 | Iron drop-off |
| Scaffold | 50g 40w | 100 | 10s | 1×1 | Build speed aura |
| Sawmill | +60g 40st | 300 | 20s | 2×2 | Wood production |
| Goldmine | +80g 40st | 300 | 20s | 2×2 | Gold production |
| Stoneworks | +60g 30st | 300 | 20s | 2×2 | Stone production |
| Iron Works | +60g 40st | 300 | 20s | 2×2 | Iron production |
| Forge | +60g 30st 20i | 350 | 22s | 2×2 | Stone+Iron→Steel |

### 10.2.4 Implementation Estimate

| File | Changes |
|---|---|
| constants.py | Helper/production building defs, drop-off routing constants |
| entities.py | Worker Foreman/Master build powers, production building tick, drop-off logic |
| game.py | Drop-off routing, production updates, new build commands |
| gui.py | Foreman/Master build buttons, production building info panels |
| enemy_ai.py | Target helper/production buildings appropriately |
| event_logger.py | BUILDING_UPGRADED, RESOURCE_PRODUCED events |

**Estimate:** 3-4 coding sessions

### 10.2.5 Additional Ideas (Evaluate During Implementation)

- **Resource Ecology:** Trees regrow slowly near other trees. Creates renewable wood.
- **Trading Post:** Convert excess resources at 3:1 ratios. Builder Master special building.
- **Worker Auto-Assignment:** Idle workers near helper building auto-start gathering.
- **Production Building Defense:** Losing a Sawmill mid-game is devastating — creates defend-the-economy gameplay.

---

## v11 — Visual Overhaul

### 11.1 Scope

Restore and improve all visual indicators that were stripped in v10_3:

| Feature | Description |
|---|---|
| Dynamic unit animations | Idle sway, walk cycle, attack animation using algorithmic shapes |
| Rank visual pips | Redesigned rank indicators on units (not the old dots) |
| Trait visual indicators | Subtle visual cues for active traits |
| Resource carry animation | Dynamic carry indicator replacing current colored dot |
| Water terrain return | Re-implement water with improved visuals and pathfinding |
| Terrain variety | Visual grass variants, terrain transitions |

### 11.2 Stretch Goals

- **Trait Discovery:** Traits hidden until demonstrated in combat
- **Named Units:** Sergeant+ with 2+ traits gets a procedural name
- **Enemy Named Units:** Occasional "named" enemy mini-boss

---

## v12 — Godot 4 Migration

### 12.1 Why Migrate

| Concern | Python/Pygame | Godot 4 |
|---|---|---|
| Unit cap | ~150 before FPS drops | 1000+ with built-in spatial indexing |
| Rendering | Software blitting | GPU-accelerated 2D with shaders |
| Pathfinding | Custom A*, 4000 node limit | Built-in NavigationServer2D, async |
| Audio | Manual mixer | Built-in audio bus system |
| UI | Manual pixel layouts | Node-based UI with themes |
| Distribution | PyInstaller (fragile) | One-click export to Win/Mac/Linux/Web |

### 12.2 Porting Strategy

Port system-by-system, not rewrite:
1. Constants + map + camera (get something visible)
2. Entities + basic combat (get something playable)
3. Advanced systems (squads, morale, ranks, traits, worker skills)
4. Polish: sprites, particles, audio

All Godot files are plain text (.gd, .tscn, .tres) — same Claude Code workflow.

---

## Idea Backlog

Ideas not scheduled for a specific version. Evaluate during or after Godot migration.

### Combat & Units
- Damage Types: Pierce (archers) vs Blunt (soldiers) with armor tables
- Charge Bonus: bonus damage after moving a distance
- Cavalry/Knight: fast melee, effective vs archers
- Healer/Priest: mobile healing unit
- Formations: select group → F for line/wedge/circle

### Economy & Buildings
- Wall Segments: 1×1 cheap pathfinding blockers, create choke points
- Blacksmith: research building for upgrades
- Building Sacrifice: demolish for 50% refund + 30s buff
- Food/Upkeep: population consumes food (macro pressure)

### Enemy AI
- Boss Waves: every 5th wave, single high-HP boss
- Healer Enemies: heal nearby enemies, must be focus-fired
- Stealth Enemies: skip defenses, target economy
- Economy Raids: enemies path to resource nodes
- Wave Negotiation: "dare" for harder wave + bigger bonus

### Map & Environment
- Day/Night Cycle: visual + gameplay effects
- Terrain Elevation: high ground bonus
- Seasonal Cycles: 4-phase affecting gather/movement/enemies
- Fog of War: scouting required

### Game Modes
- Endless Mode: no max waves, play until death
- Sandbox/Creative: unlimited resources, manual enemy spawn
- Challenge Maps: pre-set scenarios with constraints

### QoL & Polish
- Tooltip System: hover for detailed info
- Sound Effects: attack, gather, build, wave horn
- Music: ambient tracks intensifying during waves
- Save/Load: serialize game state
- Minimap Alerts: flash on enemy spawn

### Wild Ideas
- Morale Field: invisible territory from buildings/units, +5% stats in friendly territory
- Resource Ecology: trees regrow, gold regenerates
- Enemy Diplomacy: "messenger" enemy — spare it for smaller next wave

---

## Implemented & Retired

| Idea | Status | Version |
|---|---|---|
| Multi-tier veterancy | **Implemented** as 5-rank XP system | v9 |
| Enemy morale field | **Implemented** as horde morale system | v9.2 |
| Worker specialization | **Superseded** by v10 skill XP system | v10 |
| Flanking AI | **Implemented** as multi-directional spawns | v8 |
| Adaptive enemy composition | **Implemented** as counter-pick system | v8 |
| Enemy flee + veteran return | **Implemented** | v8 |
| Building ruin system | **Implemented** | v8 |
| Target priority scoring | **Implemented** as utility-scored targeting | v9.1 |
| Squad behavior | **Implemented** as rank-based squads | v9 |
| Terrain movement costs | **Implemented** as weighted pathfinding | v9.3 |
| Ballistic projectiles | **Implemented** as arrow + cannon spread | v9/v10c |
| Spatial hash grid | **Implemented** in Python (deferred to Godot was premature) | v10_4 |
| Unit trait system | **Implemented** (was planned for v11, pulled into v10_1) | v10_1 |
| Control groups (Ctrl+0-9) | **Implemented** | v10_1 |
| Rally points | **Implemented** | v10_1 |
| Town Hall garrison | **Implemented** | v10_2 |
| Global macro commands | **Implemented** (AoE2-style) | v10_2 |
| Tower splash damage | **Implemented** as Lv2 Explosive Cannon | v10c |
| Flow field pathfinding | **Deferred** to Godot (NavigationServer2D) | v12 |

---

## File Reference

| File | Purpose |
|---|---|
| `GDD_Current_v10.md` | Full specification of currently implemented v10_4 systems |
| `GDD_Roadmap.md` | This file — planned versions and design decisions |
| `GDD_Current_v9.md` | Historical v9.3 spec (superseded by v10) |
