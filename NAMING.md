# Resonance — Canonical Naming Convention

> Single source of truth for every named game element.
> Updated: 2026-03-15 · Version: v10_epsilon4 · Frozen for v11 baseline.
>
> **Rule:** Display names come from `constants.py` dicts (`DISPLAY_NAMES`, `RESOURCE_DISPLAY_NAMES`, etc.).
> Code never hardcodes display strings — always reference the canonical dict.

---

## Buildings

### Core (available from game start)

| Code Key | Display Name | Label | Size | Role |
|---|---|---|---|---|
| `town_hall` | **Tree of Life** | TL | 3×3 | Central hub, main drop-off, unit production |
| `barracks` | **Resonance Forge** | RF | 2×2 | Military unit training |
| `refinery` | **Harmonic Mill** | HM | 2×2 | Smelting: Crystal + Ore → Alloy |
| `tower` | **Sentinel** | SN | 1×1 | Defense tower, resonance field emitter |

**Sentinel Lv.2:** Sentinel → **Amplified Resonance** (upgrade costs 15 Alloy)

### Helper Buildings (1×1, unlocked by Foreman rank)

| Code Key | Display Name | Label | Unlock Skill | Function |
|---|---|---|---|---|
| `goldmine_hut` | **Flux Node** | FN | Flux Miner Foreman | Local Flux drop-off |
| `lumber_camp` | **Fiber Node** | BN | Fiberjack Foreman | Local Fiber drop-off |
| `quarry_hut` | **Crystal Node** | CN | Crystal Mason Foreman | Local Crystal drop-off |
| `iron_depot` | **Ore Node** | ON | Ore Miner Foreman | Local Ore drop-off |
| `scaffold` | **Lattice** | LT | Builder Foreman | +25% build/repair speed aura |

### Production Buildings (2×2, unlocked by Master rank)

| Code Key | Display Name | Label | Upgrades From | Production |
|---|---|---|---|---|
| `sawmill` | **Fiber Spire** | FS | Fiber Node | Fiber passive + worker boost |
| `goldmine` | **Flux Spire** | XS | Flux Node | Flux passive + worker boost |
| `stoneworks` | **Crystal Spire** | CS | Crystal Node | Crystal passive + worker boost |
| `iron_works` | **Ore Spire** | OS | Ore Node | Ore passive + worker boost |
| `forge` | **Fractal Forge** | FF | Harmonic Mill | Crystal + Ore → Alloy (fast) |

---

## Player Units — The Heptarchy (Tones 1-7)

| Tone | Note | Code Key | Display Name | Label | Status |
|---|---|---|---|---|---|
| 1 | Do (C) | `worker` | **Gatherer** | G | Implemented |
| 2 | Re (D) | `soldier` | **Warden** | W | Implemented |
| 3 | Mi (E) | `archer` | **Ranger** | R | Implemented |
| 4 | Fa (F) | `shield` | **Bulwark** | — | Planned (v10_eta) |
| 5 | Sol (G) | `knight` | **Lancer** | — | Planned (v10_eta) |
| 6 | La (A) | `healer` | **Mender** | — | Planned (v11) |
| 7 | Ti (B) | `sage` | **Sage** | — | Planned (v12) |

### Tone 0 — The Three Zeros

Tone 0 is the additive identity of GF(7). Three entities occupy it — one earned, one deliberate, one decayed:

| Entity | Side | Nature | How It Arrives | Version |
|---|---|---|---|---|
| **The Fundamental** | Player | Emergent ghost note | Formation sustains perfect resolution (sum ≡ 0 mod 7) | v11 |
| **Sage** (7 ≡ 0) | Player | Deliberate silence | Trained unit — the bridge between fields | v12 |
| **Bitter Root** | Enemy | Corrupted silence | Straggler metamorphosis — a note that refused to end | v10_7 (implemented) |

The Fundamental is not a unit — it is a formation state. When all tones resolve to zero, a phantom presence (Tartini's ghost note) amplifies the formation: +1 stat aura, ×3 Resonance generation, sub-bass audio tone. Lose any unit and it vanishes.

---

## Enemy Units — The Dark 7 (+1)

Each mirrors a player Heptarchy tone with a corrupted inversion.

| Tone | Code Key | Display Name | Label | Mirrors | Role |
|---|---|---|---|---|---|
| Do (1) | `enemy_raider` | **Blight Reaper** | BR | Gatherer | Economy hunter |
| Re (2) | `enemy_soldier` | **Hollow Warden** | HW | Warden | Melee aggressor |
| Mi (3) | `enemy_archer` | **Fade Ranger** | FR | Ranger | Ranged suppression |
| Fa (4) | `enemy_shieldbearer` | **Ironbark** | IB | Bulwark | Frontal armor wall |
| Sol (5) | `enemy_elite` | **Thornknight** | TK | Lancer | Fast deadly charge |
| La (6) | `enemy_healer` | **Bloodtithe** | BT | Mender | Inverted healing |
| Ti (7) | `enemy_siege` | **Hexweaver** | HX | Sage | Anti-resonance siege |
| 0 | `entrenched` | **Bitter Root** | BX | — | Straggler metamorphosis — the zero element, a dissonant tone that took root |

---

## Resources — The Octave of Matter

| # | Code Key | Display Name | Source | Status |
|---|---|---|---|---|
| 1 | `wood` | **Fiber** | Tree tiles | Implemented |
| 2 | `stone` | **Crystal** | Stone tiles | Implemented |
| 3 | `iron` | **Ore** | Iron tiles | Implemented |
| 4 | `sap` | **Tonic** | Tree of Life | Planned (v10_zeta) |
| 5 | `gold` | **Flux** | Gold tiles | Implemented |
| 6 | `steel` | **Alloy** | Smelted (Harmonic Mill) | Implemented |
| 7 | — | **Resonance** | Formation harmony | Planned (v11) |

---

## Gatherer Skill Tracks

| Code Key | Display Name | Resource | Color |
|---|---|---|---|
| `lumberjack` | **Fiberjack** | Fiber | Green |
| `gold_miner` | **Flux Miner** | Flux | Gold |
| `iron_miner` | **Ore Miner** | Ore | Silver |
| `stone_mason` | **Crystal Mason** | Crystal | Sandstone |
| `builder` | **Builder** | Construction | Cyan |
| `smelter` | **Smelter** | Alloy refining | Steel blue |

### Gatherer Ranks

| Rank | Name | Milestone |
|---|---|---|
| 0 | **Novice** | Base skills |
| 1 | **Foreman** | Unlocks helper buildings |
| 2 | **Master** | Unlocks production building upgrades |

---

## Military Ranks

Current: 5 ranks. Expanding to 7 in v10_eta.

| Rank | Name | XP Threshold |
|---|---|---|
| 0 | **Recruit** | 0 |
| 1 | **Veteran** | 10 |
| 2 | **Corporal** | 30 |
| 3 | **Sergeant** | 70 |
| 4 | **Captain** | 140 |
| 5 | **Resonant** | — (v10_eta) |
| 6 | **Transcendent** | — (v10_eta) |

---

## Formations — The Seven Verbs of Mathematics

| # | Short Name | Full Name | Math Verb | Harmony | Key | Status |
|---|---|---|---|---|---|---|
| 0 | **Rose** | Polar Rose | Rotation | Octave | F1 | Implemented |
| 1 | **Spiral** | Golden Spiral | Growth | Fifth | F2 | Implemented |
| 2 | **Sierpinski** | Sierpinski Triangle | Recursion | Major | F3 | Implemented |
| 3 | **Koch** | Koch Snowflake | Iteration | Unison | F4 | Implemented |
| 4 | **Lissajous** | Lissajous Knot | Superposition | — | F5 | Planned (v10_eta) |
| 5 | **Penrose** | Penrose Tiling | Aperiodicity | — | F6 | Planned (v11) |
| 6 | **Hilbert** | Hilbert Curve | Limit | — | F7 | Planned (v12) |

### Formation Combat Abilities

| Formation | Ability Name | Activation |
|---|---|---|
| Rose | **Rose Sweep** | R toggle |
| Spiral | **Spiral Tighten / Loosen** | Scroll wheel |
| Sierpinski | **Sierpinski Vertex Pulse** | V key |
| Koch | **Koch Perimeter Contract** | V key |

---

## Stances

| Index | Name | Key | Behavior |
|---|---|---|---|
| 0 | **Aggressive** | F5 | Chase targets, break formation |
| 1 | **Defensive** | F6 | Hold formation, weapon-range only |
| 2 | **Guard** | F7 | Protect area, return to post |
| 3 | **Hunt** | F8 | Prioritize raiders/siege |

---

## Procedural Traits

| Code Key | Display Symbol | Rarity | Conflict |
|---|---|---|---|
| `brave` | **B** | Common (30) | ↔ cowardly |
| `cowardly` | **C** | Common (30) | ↔ brave |
| `aggressive` | **A** | Common (30) | ↔ cautious |
| `cautious` | **U** | Common (30) | ↔ aggressive |
| `nimble` | **N** | Common (25) | — |
| `loyal` | **L** | Uncommon (15) | ↔ lone_wolf |
| `lone_wolf` | **W** | Uncommon (15) | ↔ loyal |
| `sharpshooter` | **X** | Rare (8) | Ranger only |
| `berserker` | **K** | Rare (8) | Warden only |
| `inspiring` | **I** | Very Rare (4) | — |

---

## Incident Flavours

| Tier | Code Key | Display Name |
|---|---|---|
| Light | `scout` | Scout |
| Light | `forager_raid` | Forager Raid |
| Light | `probe` | Probe |
| Medium | `assault` | Assault |
| Medium | `flanking` | Flanking |
| Medium | `economy_raid` | Economy Raid |
| Strong | `siege_column` | Siege Column |
| Strong | `war_party` | War Party |
| Strong | `pincer` | Pincer |
| Strong | `healer_push` | Healer Push |
| Deadly | `grand_assault` | Grand Assault |
| Deadly | `swarm` | Swarm |
| Deadly | `dark_resonance` | Dark Resonance |

### Incident Director FSM States

**Calm** → **Foreboding** → **Imminent** → **Active** → **Aftermath** → Calm

### Outcome Classifications

Dominated · Won · Costly · Devastating

---

## Global Commands

| Button Label | Hotkey | Function |
|---|---|---|
| **Defend Base** | D | All military rally to Tree of Life, Guard stance |
| **Hunt Enemies** | (button only) | All military attack-move toward nearest enemy |
| **Town Bell** | B | All Gatherers garrison in Tree of Life (costs resources) |
| **Resume Work** | N | Ungarrison Gatherers and resume previous tasks |

> **Note:** Hunt Enemies has no hotkey because H is reserved for Don't Panic advisor.

---

## Planned Systems (v10_zeta+)

### Seven Characteristics (v10_eta)

| # | Name | Symbol | Mathematical Property |
|---|---|---|---|
| 1 | **Precision** | σ | Low variance |
| 2 | **Resonance** | ω | Harmonic amplification |
| 3 | **Entropy** | S | Controlled chaos |
| 4 | **Symmetry** | Γ | Rotational invariance |
| 5 | **Density** | ρ | Compression |
| 6 | **Elasticity** | κ | Spring recovery |
| 7 | **???** | ∅ | Unknown (Godel's incompleteness) |

### Seven Hexes — Enemy Anti-Harmonics (v12)

| Hex | Targets | Mirrors |
|---|---|---|
| **Silence** | Gatherer / Do | Mutes the root note |
| **Discord** | Warden / Re | Breaks the steady second |
| **Blindness** | Ranger / Mi | Dims the bright third |
| **Shatter** | Bulwark / Fa | Cracks the subdominant |
| **Lethargy** | Lancer / Sol | Slows the dominant |
| **Plague** | Mender / La | Corrupts the sustainer |
| **Void** | Sage / Ti | Erases the bridge |

---

## Naming Principles

1. **Mathematical objects wearing gameplay costumes.** Every name should be instantly understood by a new player while hiding a deeper mathematical meaning for those who look.

2. **Code keys are internal.** They use legacy names (`gold`, `wood`, `tower`, `soldier`) for stability. Display names are resolved at runtime via `display_name()` and the canonical dicts in `constants.py`.

3. **The Heptarchy runs on 7.** Every category converges to 7 elements. Names within a category should feel like they belong to the same instrument family.

4. **The Dark 7 are corrupted mirrors.** Each enemy name contains a poetic inversion of its player counterpart's essence.

5. **Formations show the math.** Unlike units and buildings, formation names ARE their mathematical names (Rose, Sierpinski, Koch). This is intentional — formations are where the costume comes off and the player meets the math directly.

6. **Resources bridge concrete and abstract.** Fiber/Crystal/Ore are tangible. Tonic bridges biology and music. Flux bridges physics and alchemy. Alloy is composite. Resonance is pure mathematics. The resource ladder climbs from matter to math.

---

## Source of Truth

| Data | Location |
|---|---|
| Building/unit display names | `constants.py → DISPLAY_NAMES` |
| Resource display names | `constants.py → RESOURCE_DISPLAY_NAMES` |
| Gatherer skill names | `constants.py → WORKER_SKILL_NAMES` |
| Formation names | `constants.py → FORMATION_NAMES` |
| Stance names | `constants.py → STANCE_NAMES` |
| Military rank names | `constants.py → MILITARY_RANKS` |
| Gatherer rank names | `constants.py → WORKER_RANKS` |
| Trait display info | `constants.py → TRAIT_DISPLAY` |
| Building labels | `constants.py → BUILDING_LABELS` |
| Unit labels | `constants.py → UNIT_LABELS` |
| Full game spec | `GDD_Current_v10.md` |
| Future design | `GDD_Roadmap.md` |
| Visual spec | `visuals/VDD.md` |
