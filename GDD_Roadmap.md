# GDD Roadmap — Simple RTS

> Living document. Tracks planned versions, design decisions, and the Godot migration path.
> Current implemented version: **v9.3** (see `GDD_Current_v9.md` for full spec)
> Last updated: 2026-03-12

---

## Version Pipeline

| Version | Codename | Status | Scope |
|---|---|---|---|
| v9.3 | Tactical Depth | **SHIPPED** | Ballistic archery, XP ranks, squads, morale, formations, retargeting, terrain |
| v10 | Economy Overhaul | **DESIGN** | Worker skill XP, Foreman/Master ranks, helper buildings, production buildings, stone |
| v11 | Personalities | CONCEPT | Procedural unit traits, emergent narrative, Rimworld-style attachment |
| v12 | Godot Migration | PLANNED | Full port to Godot 4 + GDScript, same gameplay, new renderer |

---

## v10 — Economy Overhaul

### 10.1 Vision

Transform the economy from "gather piles until they run out" into a two-phase progression:
- **Phase 1 (Early):** Classical gather-and-carry from natural resource tiles (current system)
- **Phase 2 (Mid-Late):** Skilled workers build infrastructure that generates resources passively, sustaining the army after natural deposits deplete

Workers become the economic backbone with visible progression. Losing a Master Lumberjack hurts like losing a Captain soldier.

### 10.2 New Resource: Stone

| Property | Value |
|---|---|
| Terrain ID | 6 (TERRAIN_STONE) |
| Color | ~(160, 150, 130) sandstone tan |
| Capacity | 70 per tile |
| Gather Time | 3.5s |
| Gather Amount | 10 per trip |
| Map Gen | 3-5 deposits, 4-8 tiles each, medium distance from start |

**Stone is used for:**
- Tower construction (replaces some steel cost, or added alongside)
- Production building upgrades (Sawmill, Goldmine, Stoneworks)
- Late-game defensive structures (walls, if added)

### 10.3 Worker Skill XP System

Workers gain XP in the **specific skill they are actively using**. Six skill tracks:

| Skill | XP Source | Activity |
|---|---|---|
| Lumberjack | Chopping trees | Harvesting tree tiles |
| Gold Miner | Mining gold | Harvesting gold tiles |
| Iron Miner | Mining iron | Harvesting iron tiles |
| Stone Mason | Mining stone | Harvesting stone tiles |
| Builder | Building/repairing | Constructing or repairing buildings |
| Smelter | Operating refinery | Workers assigned to refinery boost |

**XP Accumulation:** Each successful gather trip / build tick / refinery cycle grants skill XP. Threshold calibrated so ~3 waves of continuous focused work = one rank-up.

**Key design:** A worker's XP is per-skill, not global. A Gold Miner Foreman who switches to chopping trees works at Novice speed for lumberjacking. This encourages committing workers to roles.

### 10.4 Worker Ranks

Three ranks per skill track:

| Rank | Title | XP Threshold | Passive Bonus | Special Power |
|---|---|---|---|---|
| 0 | Novice | 0 | Base speed | None |
| 1 | Foreman | ~3 waves work | +15% work speed | Can build helper building |
| 2 | Master | ~6 waves work | +30% work speed | Can upgrade helper → production building |

**Replaces** the old single-specialization system (500 gathered → +10% speed). The new system is strictly more interesting: same role fantasy, deeper progression, and the helper/production building powers add strategic depth.

### 10.5 Foreman Powers — Helper Buildings

When a Foreman is working a resource, a new UI option appears: **"Build [Helper Building]"** (hotkey or right-click context). The Foreman walks nearby and constructs the helper building. Cost is moderate (gold + wood + some of the relevant resource).

| Worker Skill | Helper Building | Function |
|---|---|---|
| Gold Miner Foreman | Goldmine Hut | Local gold drop-off point (cuts worker round-trip) |
| Lumberjack Foreman | Lumber Camp | Local wood drop-off point |
| Stone Mason Foreman | Quarry Hut | Local stone drop-off point |
| Iron Miner Foreman | Iron Depot | Local iron drop-off point |
| Builder Foreman | Scaffold | Passive aura: +25% build/repair speed for nearby workers |
| Smelter Foreman | — | Upgrades existing Refinery: +30% refine speed |

**Drop-off buildings** are the key economic mechanic: workers deposit resources there instead of walking back to Town Hall. This means *placement matters* — build the Lumber Camp close to the tree blob, not randomly. The drop-off buildings periodically auto-transfer their stored resources to the Town Hall (or player can manually trigger).

**Scaffold** is unique: no building placed, instead the Builder Foreman radiates an aura that speeds up nearby construction. Makes builder specialists valuable during rebuild phases after enemy waves.

### 10.6 Master Powers — Production Buildings

When a Master is working at (or near) a helper building, a new option appears: **"Upgrade to [Production Building]"**. Costs stone + gold + the helper building is consumed in the upgrade.

| Helper Building | Upgrades To | Production |
|---|---|---|
| Lumber Camp | Sawmill | Generates wood passively (slow) + workers inside boost 3-4x |
| Goldmine Hut | Goldmine | Generates gold passively (slow) + workers inside boost 3-4x |
| Quarry Hut | Stoneworks | Generates stone passively (slow) + workers inside boost 3-4x |
| Iron Depot | Iron Works | Generates iron passively (slow) + workers inside boost 3-4x |
| (Refinery) | Forge | Unlocks Stone + Iron → Steel at 2:1 (faster than iron-only path) |

**Production buildings are the "second half economy."** When natural resource tiles deplete, these buildings keep resources flowing. They produce slowly on their own but much faster with workers stationed inside — so worker management stays relevant.

**Forge** is the Smelter Master's upgrade: the existing Refinery gains an additional conversion path (Stone + Iron → Steel at favorable ratio). Gives stone a mid-game purpose beyond building material.

### 10.7 Visual Identity

| Rank | Visual |
|---|---|
| Novice | Current worker appearance (blue circle, "W" label) |
| Foreman | Colored pip matching skill (green=lumber, gold=gold, gray=iron/stone, brown=builder, orange=smelter) |
| Master | Glowing version of Foreman pip |

Helper buildings: small 1x1 structures with skill-colored accent.
Production buildings: 2x2 structures with animated element (sawmill blade, mine cart, etc. — or simpler colored indicators at current art level).

### 10.8 Helper/Production Building Stats (Draft)

| Building | Cost | HP | Build Time | Size | Drop-off? |
|---|---|---|---|---|---|
| Goldmine Hut | 40g 30w | 150 | 12s | 1x1 | Yes (gold) |
| Lumber Camp | 30g 40w | 150 | 12s | 1x1 | Yes (wood) |
| Quarry Hut | 40g 30w 10st | 150 | 12s | 1x1 | Yes (stone) |
| Iron Depot | 40g 30w | 150 | 12s | 1x1 | Yes (iron) |
| Scaffold | 50g 40w | 100 | 10s | 1x1 | No (aura) |
| Sawmill | +60g 40st | 300 | 20s | 2x2 | Produces wood |
| Goldmine | +80g 40st | 300 | 20s | 2x2 | Produces gold |
| Stoneworks | +60g 30st | 300 | 20s | 2x2 | Produces stone |
| Iron Works | +60g 40st | 300 | 20s | 2x2 | Produces iron |
| Forge | +60g 30st 20i | 350 | 22s | 2x2 | Stone+Iron→Steel |

*(Costs prefixed with + are upgrade costs on top of the helper building)*

### 10.9 Implementation Estimate

| File | Changes | Lines Est. |
|---|---|---|
| `constants.py` | Stone terrain, worker skill defs, building defs, rank thresholds | ~60 |
| `game_map.py` | Stone terrain generation, stone clusters | ~20 |
| `resources.py` | Add stone to ResourceManager | ~5 |
| `entities.py` | Worker skill XP, rank system, helper/production building logic | ~150 |
| `game.py` | Drop-off routing, production tick, new build commands | ~80 |
| `gui.py` | Worker skill display, new building buttons, production info | ~60 |
| `enemy_ai.py` | Enemies target helper/production buildings appropriately | ~10 |
| `event_logger.py` | New event types: WORKER_RANK_UP, BUILDING_UPGRADED, RESOURCE_PRODUCED | ~15 |
| **Total** | | **~400 lines** |

**Session estimate:** 3-4 coding sessions (Session 1: stone + skill XP + ranks. Session 2: helper buildings + drop-offs. Session 3: production buildings + forge. Session 4: polish + balance).

### 10.10 Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Economy too complex for new players | Medium | Phase 1 (gather) is unchanged; Foreman powers are opt-in upgrades |
| Worker micro becomes tedious | Medium | Workers auto-resume; helper buildings reduce travel automatically |
| Production buildings make late-game too easy | Medium | Passive production rate is slow; active worker management still needed |
| Stone resource adds clutter | Low | Stone is just one more gather type; integrates cleanly with existing system |
| Drop-off routing bugs | Medium | Single clear rule: deposit at nearest valid drop-off (helper > TH) |
| Builder Foreman Scaffold aura stacking | Low | Cap at one aura per area or diminishing returns |

### 10.11 Additional Ideas (Evaluate During Implementation)

- **Cross-Training Penalty:** A Gold Foreman chopping trees works at Novice speed. Encourages role commitment without hard-locking.
- **Resource Ecology:** Trees regrow slowly (grass tiles adjacent to 2+ trees have small chance to become trees). Creates renewable wood. Evaluate if this conflicts with Sawmill design.
- **Trading Post Building:** Convert excess resources at unfavorable ratios (3:1). Useful when one resource is abundant and another scarce. Could be a Builder Master special building.
- **Worker Auto-Assignment:** Idle workers near a helper building auto-start gathering the relevant resource. Reduces micro.
- **Production Building Defense:** Production buildings can be raided by enemies — losing a Sawmill mid-game is devastating. Creates defend-the-economy gameplay.

---

## v11 — Procedural Unit Personalities

### 11.1 Concept

Every unit spawns with a procedurally generated **personality** — a small set of traits that act as multipliers on existing behavior systems. No new AI needed; traits just tune existing numbers (morale thresholds, targeting weights, formation offsets, flee timers, aggro ranges).

Goal: Rimworld-style emergent narrative. Players notice "their brave archer held the line while the cowardly soldier fled" and start caring about individual units. Combined with the v9 XP/rank system and v10 worker skills, losing a Captain with the "Loyal" trait or a Master Lumberjack with "Nimble" feels personal.

### 11.2 Trait Pool

Each unit rolls 0-2 traits at creation (weighted: 40% zero, 45% one, 15% two):

| Trait | Rarity | Effect | Systems Modified |
|---|---|---|---|
| **Brave** | Common | +50% morale flee ratio (harder to scare) | Morale check |
| **Cowardly** | Common | -30% morale flee ratio (flees earlier) | Morale check |
| **Aggressive** | Common | +40% aggro range, -10% targeting noise | Auto-aggro, _score_target |
| **Cautious** | Common | -30% aggro range, prefers wounded targets | Auto-aggro, _score_target |
| **Loyal** | Uncommon | 2x squad cohesion, won't retarget away from leader's target | Squad cohesion, retarget |
| **Lone Wolf** | Uncommon | Ignores squad, +15% ATK when no allies within 80px | Squad system, combat |
| **Sharpshooter** | Rare (archer) | -40% arrow spread (stacks with rank accuracy) | Arrow firing |
| **Berserker** | Rare (soldier) | +25% ATK below 50% HP, ignores flee | Combat, flee system |
| **Inspiring** | Very Rare | Morale leader even at rank 0 (aura 80px) | Morale leader check |
| **Nimble** | Common | +15% movement speed on difficult terrain | Terrain speed calc |

**Trait Conflicts** (mutually exclusive):
- Brave / Cowardly
- Aggressive / Cautious
- Loyal / Lone Wolf

**Enemy units also roll traits** — creating variety in enemy waves. A Brave enemy grunt who refuses to flee creates memorable tension.

### 11.3 Implementation Approach

Traits are cached numeric modifiers at spawn — **zero per-frame computation cost**:

```
self.traits = set()           # {"brave", "aggressive"}
self.trait_modifiers = {}     # {"morale_mult": 1.5, "aggro_range_mult": 1.4, ...}
```

Each existing system adds one multiplier lookup:
- Morale flee ratio: `× trait_modifiers.get("morale_mult", 1.0)`
- Auto-aggro range: `× trait_modifiers.get("aggro_range_mult", 1.0)`
- Targeting noise: `× trait_modifiers.get("noise_mult", 1.0)`
- Arrow spread: `× trait_modifiers.get("spread_mult", 1.0)`
- Squad cohesion: `× trait_modifiers.get("cohesion_mult", 1.0)`
- ATK calculation: `× trait_modifiers.get("atk_mult", 1.0)` (conditional)

**Estimated code: ~90 lines across 4 files.** Single session scope.

### 11.4 Visual Design

- **In-game:** Small colored icon next to rank pip
- **Selection panel:** Trait names below rank (e.g., "Soldier [Veteran] — Brave, Aggressive")

| Trait | Icon Color |
|---|---|
| Brave | Gold |
| Cowardly | Gray |
| Aggressive | Red |
| Cautious | Blue |
| Loyal | Green |
| Lone Wolf | Silver |
| Sharpshooter | Purple |
| Berserker | Dark Red |
| Inspiring | Bright Gold |
| Nimble | Teal |

### 11.5 Stretch Goals (v11.x)

- **Trait Discovery:** Traits hidden until demonstrated (first morale check, first kill). "Brave!" floating text when a Brave unit passes a check others would fail.
- **Trait Inheritance:** Surviving units' traits "spread" to nearby recruits over waves. Creates unit culture/lineage.
- **Named Units:** Sergeant+ with 2+ traits gets a procedural name. "Sergeant Marcus the Brave" — shown on minimap, announced on death.
- **Enemy Named Units:** Occasional "named" enemy with strong traits. Mini-boss feel without new unit types. "A Berserker Elite leads this wave!"

### 11.6 Scope Options

| Scope | Traits | Lines | Sessions |
|---|---|---|---|
| Minimal (safe) | 4 traits (Brave, Cowardly, Aggressive, Cautious) | ~50 | 1 |
| Standard (recommended) | Full 10 traits | ~90 | 1 |
| Extended (risky) | Standard + discovery + named units | ~150 | 2 |

**Recommendation: Standard.** 10 traits x 5 ranks x 3+ unit types = hundreds of unique identities for minimal code.

---

## v12 — Godot 4 Migration

### 12.1 Why Migrate

| Concern | Python/Pygame | Godot 4 |
|---|---|---|
| Unit cap | ~150 before FPS drops | 1000+ with built-in spatial indexing |
| Rendering | Software blitting | GPU-accelerated 2D with shaders |
| Pathfinding | Custom A*, 1000 node limit | Built-in NavigationServer2D, async |
| Audio | Manual mixer | Built-in audio bus system |
| UI | Manual pixel layouts | Node-based UI with themes |
| Distribution | PyInstaller (fragile) | One-click export to Win/Mac/Linux/Web |
| Animation | Manual frame logic | AnimationPlayer, tweens, particles |

### 12.2 Migration Checklist

| Step | Task | Effort |
|---|---|---|
| 1 | Install Godot 4.x, create project, set 1280x720 | 10 min |
| 2 | Port `constants.py` → `constants.gd` (autoload singleton) | 30 min |
| 3 | Port `game_map.gd` + TileMapLayer node for terrain | 2-3 hrs |
| 4 | Port `entities.gd` → Unit scene (CharacterBody2D) + Building scene (StaticBody2D) | 3-4 hrs |
| 5 | Port pathfinding → NavigationServer2D with navigation regions | 2 hrs |
| 6 | Port `camera.gd` → Camera2D node with zoom/pan | 30 min |
| 7 | Port `resources.gd` + `gui.gd` → Control nodes + theme | 2-3 hrs |
| 8 | Port `enemy_ai.gd` + wave system | 2 hrs |
| 9 | Port `squads.gd` + combat systems | 2 hrs |
| 10 | Port `event_logger.gd` (FileAccess API) | 30 min |
| 11 | Add proper sprites/animations (optional) | open-ended |
| 12 | Audio (SFX + music) | open-ended |
| 13 | Export to .exe | 10 min |

**Estimated total: 3-5 focused sessions** for functional parity, then open-ended for polish.

### 12.3 Claude Code Cooperation

All Godot project files are plain text — Claude Code can edit them directly:
- `.gd` — GDScript (Python-like syntax)
- `.tscn` — Scene files (node trees, text format)
- `.tres` — Resources (text format)
- `project.godot` — Project settings (INI-like)

No plugin needed. Same workflow: describe what you want, Claude edits files, you test in Godot editor.

### 12.4 Porting Strategy

**Don't rewrite from scratch.** Port system-by-system:
1. Start with constants + map + camera (get something visible)
2. Add entities + basic combat (get something playable)
3. Layer on advanced systems (squads, morale, ranks, traits, worker skills)
4. Polish phase: replace shapes with sprites, add particles/audio

Each system maps cleanly from Python class → GDScript class/scene.

---

## Idea Backlog

Ideas from brainstorming that aren't scheduled for a specific version. Evaluate during or after Godot migration.

### Combat & Units
- **Damage Types:** Pierce (archers) vs Blunt (soldiers) with armor effectiveness tables
- **Charge Bonus:** Units deal bonus damage on first attack after moving a distance
- **Cavalry/Knight:** Fast melee, high cost, effective vs archers
- **Healer/Priest:** Mobile healing unit (replaces TH aura for expeditionary forces)
- **Area of Effect:** Tower splash damage in small radius
- **Formations:** Select group → press F for line/wedge/circle formation

### Economy & Buildings
- **Wall Segments:** 1x1 cheap structures that block enemy pathing, create choke points
- **Blacksmith:** Research building for unit attack/armor/speed upgrades
- **Building Sacrifice:** Demolish for 50% refund + 30s buff to nearby units (+20% ATK)
- **Trading Post:** Convert excess resources at unfavorable ratios (3:1)
- **Food/Upkeep:** Population consumes food, farms as new building (adds macro pressure)

### Enemy AI
- **Boss Waves:** Every 5th wave has a single high-HP boss with special mechanics
- **Healer Enemies:** Must be focus-fired, heal nearby enemies
- **Stealth Enemies:** Skip past defenses, target economy buildings
- **Economy Raids:** Enemies path specifically to resource nodes or isolated workers
- **Enemy Buildings:** Late-game waves include structures that spawn reinforcements
- **Wave Negotiation:** Between waves, "dare" the enemy for harder wave in exchange for bigger bonus

### Map & Environment
- **Day/Night Cycle:** Visual dimming + gameplay effects (reduced enemy sight at night?)
- **Terrain Elevation:** High ground bonus for archers/towers
- **Seasonal Cycles:** 4-phase rotation affecting gather speed, movement, enemy strength
- **Fog of War:** Unexplored map hidden, scouting required

### Game Modes
- **Endless Mode:** No max waves, play until death. Local high score leaderboard
- **Sandbox/Creative:** Unlimited resources, spawn enemies manually, test builds
- **Challenge Maps:** Pre-set scenarios with unique constraints
- **Campaign:** Linked levels with story, each map has different rules

### QoL & Polish
- **Control Groups:** Ctrl+1-9 to save, 1-9 to recall (needs keybind refactor)
- **Rally Points:** Set building rally point for newly trained units
- **Tooltip System:** Hover over any element for detailed info
- **Sound Effects:** Attack, gather, build, wave horn, notifications
- **Music:** Ambient tracks that intensify during waves
- **Save/Load:** Serialize game state, resume later
- **Minimap Alerts:** Flash minimap when enemies spawn

### Wild Ideas
- **Morale Field:** Invisible territory radiates from buildings/unit clusters. Friendly territory = +5% stats, enemies slow down. Creates organic frontlines.
- **Resource Ecology:** Trees regrow. Gold slowly regenerates. Map is alive.
- **Unit Memory/Personality:** Units remember kills, preferred enemies, preferred resources (partially realized in v11 traits).
- **Enemy Diplomacy:** "Messenger" enemy — don't kill it and it reaches TH, next wave is smaller. Kill it, wave is normal. Ethical dilemma.

---

## Implemented & Retired

Ideas from old brainstorm documents that have been implemented or explicitly cut:

| Idea | Status | Version |
|---|---|---|
| Multi-tier veterancy | **Implemented** as 5-rank XP system | v9 |
| Named units (basic) | **Scheduled** for v11.5 stretch | v11 |
| Enemy morale field | **Implemented** as horde morale system | v9.2 |
| Worker specialization | **Superseded** by v10 skill XP system | v10 |
| Flanking AI | **Implemented** as multi-directional spawns | v8 |
| Adaptive enemy composition | **Implemented** as counter-pick system | v8 |
| Enemy flee + veteran return | **Implemented** | v8 |
| Building ruin system | **Implemented** | v8 |
| Target priority scoring | **Implemented** as utility-scored targeting | v9.1 |
| Squad behavior | **Implemented** as rank-based squads | v9 |
| Terrain movement costs | **Implemented** as weighted pathfinding | v9.3 |
| Ballistic projectiles | **Implemented** as arrow spread system | v9 |
| Flow field pathfinding | **Deferred** to Godot (NavigationServer2D) | v12 |
| Spatial hash grid | **Deferred** to Godot (built-in) | v12 |

---

## File Reference

| File | Purpose |
|---|---|
| `GDD_Current_v9.md` | Full specification of currently implemented v9.3 systems |
| `GDD_Roadmap.md` | This file — planned versions and design decisions |
| `archive/GDD_Current_v8.md` | Historical v8 spec (superseded by v9) |
| `archive/GDD_Future.md` | Original brainstorm template (ideas absorbed here) |
| `archive/GDD_Future_v11.md` | Original v11 personality design (absorbed into Section 3) |
