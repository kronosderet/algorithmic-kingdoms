# GDD Roadmap — Algorithmic Kingdoms

> Living document. Tracks the path from simple RTS to mathematical odyssey.
> Current implemented version: **v10_delta** (see `GDD_Current_v10.md` for full spec)
> Last updated: 2026-03-14
>
> *"This game should be combat math. The paradox of it being nonexistent anywhere*
> *in nature, existing only in minds, but ruling the universe nonetheless.*
> *Harmony in chaos, chaos in harmony. That should be the absolute theme."*

---

## The Vision

Algorithmic Kingdoms is a game that teaches math the way math deserves to be taught — not with pencil and paper, but with armies that sing trigonometric harmonies, formations that warp spacetime through golden ratios, and enemies that cast hexes powered by divergent series. Every system in the game IS a mathematical object wearing a gameplay costume. The player learns to wield mathematics as a force multiplier without ever seeing an equation.

The game opens as a simple gather-and-survive RTS. But like a fractal, every layer reveals three more beneath it. Survive long enough, experiment boldly enough, and the game unfolds into something that has no bottom.

---

## The Heptarchy — Base-7 Unified Framework

*Seven is the thread that stitches every system into one fabric.*

The number 7 is prime. This makes GF(7) — the Galois field of order 7 — a complete algebraic field where every non-zero element has a multiplicative inverse, there are no zero divisors, and the multiplicative group is cyclic. In practice: every combination of game elements produces a unique, meaningful result. No two compositions accidentally collide. The entire game runs on modular arithmetic the player learns by ear, not by equation.

Seven appears at every layer of the design. This is not decoration — it is the game's DNA.

### The Seven Tones (Unit Types)

Each unit type is a musical tone. Compositions within formations map to musical intervals and chords. The player hears whether their army is in tune.

| Tone | Note | Unit Type | Role | Musical Character | Introduced |
|---|---|---|---|---|---|
| **1** | Do (C) | **Gatherer** | Economy — the root note | Foundation everything builds on. Formations with a Gatherer feel grounded | v1 (existing) |
| **2** | Re (D) | **Soldier** | Melee line | Steady, reliable second voice | v1 (existing) |
| **3** | Mi (E) | **Archer** | Ranged DPS | Bright, cutting major third | v1 (existing) |
| **4** | Fa (F) | **Shield** | Tank/absorb | Subdominant — supports, doesn't lead | v10_eta |
| **5** | Sol (G) | **Knight** | Fast melee/charge | The dominant — resolves tension, decisive | v10_eta |
| **6** | La (A) | **Healer** | Support/sustain | Warm, minor quality, holds things together | v11 |
| **7** | Ti (B) | **Sage** | Bridge/amplifier | Not a voice in the chord — the silence between fields. Adds 0 to harmony sum but opens the door to the Shadow Heptarchy | v12 |

**The Gatherer as root note:** A formation with a Gatherer sounds like a chord resolving to its tonic. Pure military formations always have a slight rootlessness — like a chord missing its fundamental. A Gatherer-commander formation is an economy formation that gathers faster and buffs nearby production. But a Gatherer at the center of a Rose is also a vulnerability — protect the root note or the chord collapses.

**GF(7) harmony calculation:** A formation's composition sums mod 7. A total of 0 (mod 7) = perfect resolution (back to root). 5 (mod 7) = dominant, strong but wants one more voice. The player learns modular arithmetic by listening — when the chord resolves, they feel it. When it's unresolved, they feel that tension and naturally seek to fill the gap.

### The Seven Resources (Octave of Matter)

| # | Resource | What It Is | Gathered From | Replaces | Color |
|---|---|---|---|---|---|
| **1** | **Fiber** | Organized carbon chains — life's scaffolding | Trees, plants | Wood | Green |
| **2** | **Crystal** | Ordered mineral lattice — rigid structure | Stone deposits | Stone | Pale blue |
| **3** | **Ore** | Dense metallic bonds — strength, conductivity | Iron veins | Iron | Silver |
| **4** | **Sap** | Tree of Life essence — concentrated vitality | Tree of Life (slow, precious) | *New* | Amber |
| **5** | **Flux** | Purified energy potential — the transformer | Gold seams (rare) | Gold | Gold |
| **6** | **Alloy** | Ore + Crystal fused under Flux — composite | Forge (crafted) | Steel | Blue-steel |
| **7** | **Resonance** | Crystallized harmony — mathematical substance | Formation singing (!) | *New* | Violet |

**Resonance** is not mined. It is *produced by your army existing in harmony*. Formations passively generate Resonance proportional to their harmony quality. The better your compositions, the more you produce. This is the resource that bridges economy and combat into a single unified system. Rank-7 units amplify Resonance generation.

**Sap** flows from the Tree of Life itself — slowly, preciously. It's the resource of growth and healing. The Tree produces more Sap as it evolves through depth layers, creating a feedback loop: deepen the game → more Sap → more healing/growth → survive longer → deepen further.

Resource rename is cosmetic — happens whenever it feels right. The meaningful additions are Sap (v10_zeta) and Resonance (v11).

### The Seven Octaves (Rank System)

Currently 5 ranks. Expanding to 7 creates the octave structure where rank = octave:

| Rank | Octave | Musical Feel | Gameplay Milestone | Characteristic Revealed |
|---|---|---|---|---|
| **1** | Sub-bass | Felt, not heard — a rumble | Fresh recruit | — |
| **2** | Bass | Warm foundation | Reliable | 1st characteristic |
| **3** | Tenor | Where melody lives — the sweet spot | Competent, useful | 2nd characteristic |
| **4** | Alto | Rich, full | Veteran — starts feeling dangerous | 3rd characteristic + trait eligible |
| **5** | Soprano | Bright, cutting | Elite — commands attention | 4th characteristic + commander eligible |
| **6** | Whistle | Piercing, brilliant | Master — other units react to presence | 5th characteristic + aura (passive nearby buff) |
| **7** | Ultra | Beyond comfortable — transcendent | Transcendent — living tuning fork | 6th characteristic + passive Resonance generation |

**Octave doubling:** A Rank-7 leading Rank-1 units creates octave reinforcement — the most fundamental harmonic relationship. Mixed-rank formations resonate deeper than same-rank formations.

**Audio trick:** Ranks 1-4 map to actual pitch (C2-C5). Rank 5+ adds overtone richness instead of raw pitch. Rank 7 wraps: fundamental drops back to bass but shimmers with so many harmonics it sounds otherworldly — like a Tibetan singing bowl. The octave wraps modularly. Math teaching itself.

### The Seven Characteristics

Each unit has 7 characteristic slots, rolled randomly at creation (values 0-6, base 7). Hidden until the corresponding rank reveals them. The commanding unit's dominant characteristic shapes the formation's signature:

| # | Characteristic | Symbol | Mathematical Property | Commander Effect on Formation |
|---|---|---|---|---|
| **1** | **Precision** | σ | Low variance | Tighter geometry, less slot drift, crisper fractal shape |
| **2** | **Resonance** | ω | Harmonic amplification | Stronger aura, louder song, faster Tier climbing |
| **3** | **Entropy** | S | Controlled chaos | Slots jitter unpredictably — formation harder to read/target |
| **4** | **Symmetry** | Γ | Rotational invariance | Formation performs equally from any facing, no weak side |
| **5** | **Density** | ρ | Compression | Compact shape, harder to penetrate, slower rotation |
| **6** | **Elasticity** | κ | Spring recovery | Formation snaps back faster after disruption |
| **7** | **???** | ∅ | Unknown | ??? |

The 7th characteristic exists in the data. The game tracks it. It never reveals — not at Rank 7, not ever. Gödel's incompleteness — the unit contains a truth about itself that cannot be proven within the system. The community will datamine it. They'll find the value (0-6, like the others). They still won't know what it does.

*But the roots of the Tree know.*

### The Seven Formations (Timbres) — The Seven Verbs of Mathematics

If tones are the notes and ranks are the octaves, formations are the **timbres** — the instrument that colors the sound. Four formations is a string quartet. Seven is a full ensemble.

But the seven formations are not arbitrary fractals chosen for aesthetics. They are the **seven fundamental ways mathematics creates pattern from emptiness**. Before there can be a triangle or a number, there must be an operation — a verb. These seven verbs are the irreducible toolkit:

| # | Formation | The Verb | What It Does | Why It's Fundamental |
|---|---|---|---|---|
| **1** | **Polar Rose** | **Rotation** | Returns to where it started, changed | The first symmetry — the circle. Without rotation, no periodicity, no wave, no music. |
| **2** | **Golden Spiral** | **Growth** | Each step multiplied by the last | Self-similar scaling. φ is the fixed point of `x = 1 + 1/x`. Growth that remembers its past. |
| **3** | **Sierpinski Triangle** | **Recursion** | Apply the rule to the output of the rule | The engine of fractals. A triangle containing triangles containing triangles — infinity from one instruction. |
| **4** | **Koch Snowflake** | **Iteration** | Repeat the same step, forever | Infinite perimeter, finite area. Persistence creates complexity from simplicity. |
| **5** | **Lissajous Knot** | **Superposition** | Two waves existing in the same space | Interference. Phase. The birth of harmony — and dissonance. Two truths at once. |
| **6** | **Penrose Tiling** | **Aperiodicity** | Order that never repeats | Quasicrystals. Golden-ratio angles create structure without periodicity — the edge of chaos. |
| **7** | **Hilbert Curve** | **Limit** | The destination a process approaches but never reaches | A line that fills a plane. Dimension itself breaks. The boundary between what math can describe and what it cannot. |

Together: **Rotate, Grow, Recurse, Iterate, Superpose, Break Periodicity, Take the Limit.** These are the seven things mathematics *does*. Everything else — every theorem, every structure — is some composition of these verbs.

**Geometric & Musical Character:**

| # | Formation | Math Object | Geometric Character | Musical Timbre | Introduced |
|---|---|---|---|---|---|
| **1** | **Polar Rose** | Trigonometric curve `r = cos(kθ)` | Petals radiating from center — offensive, sweeping | Warm oscillating hum (AM sine) | v10_6 (existing) |
| **2** | **Golden Spiral** | Logarithmic spiral `r = ae^(bθ)` (φ) | Outward expansion — ranged, area control | Rising/falling pitch sweep | v10_6 (existing) |
| **3** | **Sierpinski Triangle** | Fractal subdivision (recursive midpoints) | Maximum spread — anti-AOE, scattered resilience | Staccato recursive pulses | v10_6 (existing) |
| **4** | **Koch Snowflake** | Fractal perimeter (infinite edge, finite area) | Defensive wall — enemies must cross the perimeter | Shimmering additive drone | v10_6 (existing) |
| **5** | **Lissajous Knot** | Parametric curve `x=sin(at+δ), y=sin(bt)` | Interlocking loops — units weave through each other in figure-8 patterns | Phase-shifting interference pattern | v10_eta |
| **6** | **Penrose Tiling** | Aperiodic tessellation (golden ratio angles) | Non-repeating space fill — unpredictable, no pattern for enemies to exploit | Quasicrystal hum — almost periodic, never quite | v11 |
| **7** | **Hilbert Curve** | Space-filling curve (fractal, visits every point) | Maximum coverage per unit — one continuous line through the entire area | Dense continuous tone (all frequencies present, like white noise resolving into music) | v12 |

**Why the new three complete the set:**

- **Lissajous (5 — Superposition):** Two frequencies interacting. Units orbit in interlocking loops, passing through each other's paths. The formation IS interference. In combat, units sweep through the same space at different phases, creating a blender effect without needing rotation. Musically: the timbre shifts as the phase parameter changes — two tuning forks slightly detuned.

- **Penrose (6 — Aperiodicity):** Order without repetition. The golden ratio (φ = (1+√5)/2) determines the tile angles. Units fill space in a pattern that LOOKS random but has deep mathematical order. Enemies can't predict it because it never repeats — but it's not chaos, it's quasicrystalline order. The anti-pattern pattern. Musically: the tone almost resolves but never quite, creating a haunting "almost familiar" quality.

- **Hilbert (7 — Limit):** A single line that visits every point. With enough members, the formation literally covers the entire area. One continuous path, no gaps. The formation IS the battlefield. Nothing passes through unchallenged. Musically: all frequencies present simultaneously — white noise resolving into music. The most demanding formation and the rarest to achieve. It is the *limit* of what a formation can be.

**GF(7) Formation × Tone Affinity Table:**

The formations are not just paired with tones by theme — the pairing falls out of the algebra. In GF(7), multiplication of the formation number by the tone number produces an **affinity product**. Products ≡ 0 (mod 7) represent perfect resolution; low residues represent consonance; high residues represent tension.

```
         Do(1)  Re(2)  Mi(3)  Fa(4)  Sol(5) La(6)  Ti(7)
Rose(1)    1      2      3      4      5      6      0
Spiral(2)  2      4      6      1      3      5      0
Sierp(3)   3      6      2      5      1      4      0
Koch(4)    4      1      5      2      6      3      0
Lissa(5)   5      3      1      6      4      2      0
Penro(6)   6      5      4      3      2      1      0
Hilbt(7)   0      0      0      0      0      0      0
```

Read this table and the math sings:

- **Every formation × Ti(7) ≡ 0** — the Sage is zero. It doesn't resolve anything — it *passes through* everything. The Sage is transparent to harmony, which is exactly why it can bridge between fields. It doesn't sing. It listens.
- **Hilbert(7) × anything ≡ 0** — the Limit formation is also zero. Both Hilbert and Sage are boundary-dwellers: the formation that fills all space, the unit that touches both fields. This is why Hilbert is the rarest formation and Sage the rarest unit — they are both the zero, and the zero is the gate.
- **Hilbert(7) × Sage(7) = 0 × 0 = 0** — trivially true, and that's the point. The most powerful configuration in the game is mathematically *trivial*. Zero times zero. Nothing times nothing. And yet: a squad of Sages in Hilbert formation is a formation that fills all space while listening to both fields simultaneously. The gate, fully open. What comes through is not documented.
- **Rose(1) is the identity** — it multiplies each tone by 1, preserving its character. The simplest formation, the beginner's formation, changes nothing.
- **The diagonal** (Rose×Do, Spiral×Re, Sierpinski×Mi...) gives (1, 4, 2, 2, 4, 6, 0) — the "natural" pairings produce a palindromic sequence. The math has mirror symmetry built in.
- **Products of 1** mark "native register" pairings: Spiral×Fa(2×4=8≡1), Koch×Re(4×2=8≡1), Sierpinski×Mi-complement, etc. When the product is 1, the formation is playing in its root key.

The affinity product feeds directly into the harmony formula. Higher affinity (lower residue) means stronger resonance, more powerful auras, and eventually more devastating harmonic spells. The player discovers these relationships by ear — certain compositions just *sound better* — and the GF(7) multiplication table is the hidden truth beneath.

**Formation × Tone natural affinities (derived from the table):**

| Formation | Affinity Tone | GF(7) Product | Why |
|---|---|---|---|
| Rose (1) | Soldier Re (2) | 1×2 = 2 (consonant) | Petals sweep — melee strikes |
| Spiral (2) | Archer Mi (3) | 2×3 = 6 (tension → drive) | Outer ring sightlines — ranged pressure |
| Sierpinski (3) | Shield Fa (4) | 3×4 = 12 ≡ 5 (dominant) | Vertices hold — defensive spread |
| Koch (4) | Knight Sol (5) | 4×5 = 20 ≡ 6 (tension) | Perimeter charge — decisive enclosure |
| Lissajous (5) | Gatherer Do (1) | 5×1 = 5 (dominant) | Phase loops = gather routes — economy formation |
| Penrose (6) | Healer La (6) | 6×6 = 36 ≡ 1 (root) | Unpredictable position = hard to target — sustain |
| Hilbert (7) | Sage Ti (7) | 0 × 0 = 0 (the gate) | Total coverage + field bridge = the conversation fully open |

When a formation contains its affinity tone, a bonus applies — the instrument is playing its native register. Penrose×Healer is especially notable: product ≡ 1, meaning the Healer in Penrose returns to the root. The aperiodic pattern becomes a sanctuary.

### Why Seven Works

- **Miller's Law:** Working memory holds 7±2 chunks — the player can hold the full system in their head
- **Musical octave:** 7 tones before repetition — the most fundamental structure in human auditory cognition
- **GF(7) is a field:** Every composition produces unique results. No collisions. Complete algebraic closure
- **Cyclic group:** 3 generates all of GF(7)* — (3,2,6,4,5,1) — every tone reaches every other through multiplication
- **Prime:** No zero divisors means no "dead" combinations. Everything matters

---

## Version Pipeline

| Version | Codename | Status | Theme |
|---|---|---|---|
| v9.3 | Tactical Depth | **SHIPPED** | Ballistic archery, XP ranks, squads, morale, formations, retargeting, terrain |
| v10 Phase 1 | Economy Foundation | **SHIPPED** | Stone, worker skill XP, tower cannon, traits, garrison, global commands, perf |
| v10_5 | Module Split | **SHIPPED** | Architecture split (5 modules), parabolic projectiles with lead aiming |
| v10_6 | Difficulty Rebalance | **SHIPPED** | Fractal formations (4), stances (4), 5 new enemy types, adaptive difficulty |
| v10_7 | Edge Case Polish | **SHIPPED** | Sentinel's Cry, sapper detonation, straggler metamorphosis |
| v10_delta | Physics & Energy | **SHIPPED** | Physics movement, energy/stamina, spring formations, player-driven squads |
| v10_epsilon | Formation Math | **NEXT** | Correct fractal geometry, rotation combat, formation discovery |
| v10_zeta | Economy Depth | PLANNED | Helper buildings, production buildings, drop-offs, Forge, Sap resource |
| v10_eta | The Fourth & Fifth | PLANNED | Shield + Knight, Lissajous formation, triads, 7-rank system, characteristics |
| v11 | Harmonic Awakening | PLANNED | Healer (6th tone), Penrose formation, procedural audio, GF(7) harmony, Resonance resource |
| v12 | Blood & Chaos | PLANNED | Sage (7th tone), Hilbert formation, enemy blood magic, hex system, full Heptarchy |
| v13 | Progressive Depth | PLANNED | 7 depth layers, Tree of Life evolution, emergent GUI, Noita-level secrets |
| v14 | Godot Migration | PLANNED | Full port to Godot 4, GPU shaders, 1000+ units, visible waveforms |

---

## SHIPPED VERSIONS (Summary)

<details>
<summary>v9.3 through v10_7 — Click to expand</summary>

### v9.3 — Tactical Depth
Ballistic archery, 5-rank XP system, persistent squads, horde morale with flee/return, utility-scored targeting with retargeting, weighted terrain pathfinding.

### v10 Phase 1 — Economy Foundation (v10 through v10_4)
Stone resource, worker skill XP (6 tracks × 3 ranks), tower cannon overhaul (ballistic + explosive), 10 procedural traits, control groups, enemy inspection, Town Hall garrison, global macro commands, spatial grid performance.

### v10_5 — Module Split
entities.py → entity_base.py + unit.py + building.py + building_shapes.py + projectiles.py. Parabolic projectiles with predictive lead aiming.

### v10_6 — Difficulty Rebalance
4 fractal formations (Polar Rose, Golden Spiral, Sierpinski, Koch). 4 stances (Aggressive, Defensive, Guard, Hunt). 5 new enemy types (Sapper, Raider, Shieldbearer, Healer, Warlock). Adaptive difficulty engine with pressure tracking.

### v10_7 — Edge Case Polish
Tower upgrade fire penalty, Sentinel's Cry dead zone mechanic, sapper sympathetic detonation, straggler metamorphosis (rooting → Entrenched Titan).

</details>

---

## v10_delta — Physics & Energy (SHIPPED)

The foundation rebuild. Replaced teleport-style movement with real physics, hard slot-snapping with spring forces, and added the energy economy that makes all future systems possible.

### Shipped Features

| System | What It Does |
|---|---|
| **Physics Movement** | Velocity/acceleration/deceleration per unit type. Kinematic braking (d = v²/2a). Each unit feels different — raiders sprint and slide, soldiers march steady |
| **Energy/Stamina** | Per-unit energy pools. Actions drain energy, regen based on state + formation harmony. Exhaustion slows units to 40% speed |
| **Spring Formations** | Critically-damped spring (k=3.0, ζ=0.7) pulls units to formation slots. No teleporting — units gravitate naturally into the ornament |
| **Soft Repulsion** | Distance-based push forces replace hard grid nudges. Golden-angle splay for stacked units |
| **Player-Driven Squads** | No auto-grouping. Player discovers formations by assembling correct compositions. F-key dual purpose (create/change). Delete to dissolve |
| **Pending Group Discovery** | Move 3+ free units to a location → arrival triggers composition check → formation auto-discovered |
| **Rotation Toggle** | R key starts/stops formation rotation. Foundation for sweep combat |
| **Tension Fix** | Drift acceleration capped at 2.5×, decay during ACTIVE/AFTERMATH states |
| **Edge Scroll Fix** | Top bar no longer triggers camera scroll |
| **WASD Priority** | Camera panning always takes priority, hotkeys remapped to non-conflicting keys |

---

## v10_epsilon — Formation Math (NEXT)

*The formations stop being decoration and become weapons.*

### ε.1 Correct Fractal Geometry

The current formation slot calculators use placeholder math. This version makes each formation geometrically true:

**Polar Rose** — `r = cos(kθ)` where k = (n-1) for n members:
- 3 units → 2-petal rose: 1 anchor (center), 2 petal tips (soldiers at the striking edge)
- 4 units → 3-petal rose: 1 anchor, 3 petal tips
- 5 units → 4-petal rose: 1 anchor, 4 petal tips
- 6+ → additional units fill petal bases (archers at inner positions for ranged cover)

**Golden Spiral** — Vogel sunflower with type-aware placement:
- Archers at outer rings (longer range, clear line of fire)
- Soldiers at inner rings (close to center, protective)
- φ-based angular spacing naturally prevents line-of-sight blocking

**Sierpinski Triangle** — Recursive subdivision:
- 3 units → vertices of base triangle
- 4-6 → vertices + midpoints (first recursion)
- 7+ → second recursion level (units spread across 9 sub-triangles)
- Anti-AOE: maximum spread with minimum perimeter

**Koch Snowflake** — Perimeter walk:
- Units distributed along Koch curve perimeter
- Even spacing creates maximum defensive coverage
- Natural chokepoint formation — enemies must cross the perimeter

### ε.2 Type-Aware Slot Assignment

`_rebuild_slots()` sorts members by unit type based on formation needs:
- **Rose**: Soldiers at petal tips (they sweep through enemies), archers at bases/center
- **Spiral**: Archers at outer rings, soldiers at inner rings
- **Sierpinski**: Mixed — soldiers at vertices (exposed), archers at midpoints (protected)
- **Koch**: Soldiers at convex points (outward-facing), archers at concave bays

### ε.3 Rotation Combat — Rose Sweep

The formation the user was most excited about: *"the rose could rotate as a whole and deal damage each time a warden in the petal meets the enemy."*

| Parameter | Value |
|---|---|
| Rotation speed | 0.3 rad/s (configurable per formation) |
| Sweep damage | 15% of unit's ATK per enemy contact |
| Sweep interval | 1.5s minimum between hits on same target |
| Sweep radius | Petal tip must pass within melee range of enemy |
| Energy cost | Rotation drains energy from all members (shared load) |

When rotating, petal-tip soldiers deal sweep damage to enemies they pass through. The formation becomes a mathematical blender — enemies caught inside take repeated hits as petals sweep past. Faster rotation = more hits = more energy drain. The player balances aggression vs endurance.

### ε.4 Other Formation Combat Abilities

| Formation | Combat Mechanic | Math Connection |
|---|---|---|
| **Spiral** | Tighten/loosen (scroll wheel while selected). Tight = high damage density, loose = area control | Spiral parameter `a` in r = ae^(bθ) |
| **Sierpinski** | Vertex pulse — vertices briefly push outward then snap back, dealing burst damage at triangle points | Recursive expansion/contraction |
| **Koch** | Perimeter contract — snowflake shrinks inward, trapping enemies inside, then expands | Koch iteration: infinite perimeter, finite area |

### ε.5 Chord Preview & Composition UX

The game is a musical instrument, not a calculator. The player composes by feel, not by optimization.

**Chord preview on selection:** When free units are selected, the GUI shows a live harmonic quality bar:
```
Selected: 3S 2A 1W  →  ♪ Leading tone (tense, powerful)  [===========·····]
```
Adding/removing units from selection updates the preview in real-time. The player learns mod-7 by watching the bar shift as they shift-click units. When the bar fills gold and the descriptor reads "Perfect resolution" — they just solved a modular arithmetic equation with their mouse.

**Formation cards show harmony:** Existing squad cards display current ♪ value and chord quality descriptor.

**No auto-splitting, no optimization suggestions.** The player IS the composer. Two small formations enabling Tier 5 (Overtone) vs one big formation pushing toward Tier 4 — that's a strategic choice, not a puzzle to solve. Both are musically valid.

**Split suggestions (v11+):** At higher depth layers, selecting large groups may show an optional split hint: `[Split: 5+3] ♪♪ suggests better total harmony`. Player ignores or accepts. Never forced.

### ε.6 Visual Feedback

| Feature | Description |
|---|---|
| Energy bar | Thin bar below HP bar on each unit |
| Velocity trails | Faint line behind fast-moving units |
| Free unit counter | "Free: 3S 2A" in squad bar area |
| Harmony percentage | `♪ 85%` below active formation button (gold at 100%) |
| Chord preview | Live harmonic quality bar when free units selected (see ε.5) |
| Formation hints | Undiscovered formations show composition hints ("? · 5 at 3:2") |
| Exhaustion particles | Panting effect at < 20% energy |

### ε.7 Files Modified

| File | Scope |
|---|---|
| squads.py | Rewrite all 4 formation slot calculators, type-aware `_rebuild_slots`, sweep damage in `update_combat_rotation` |
| unit.py | Energy bar draw, velocity trail, exhaustion visual |
| gui.py | Formation discovery hints, harmony %, free unit counter, squad card enhancements |
| constants.py | Corrected formation geometry constants, sweep parameters |
| game.py | Scroll-wheel spiral tighten/loosen, formation combat triggers |

**Estimate:** 2-3 sessions

---

## v10_zeta — Economy Depth

*Workers build infrastructure. Resources become renewable. The economy has a second act.*

### ζ.1 Helper Buildings (Drop-offs)

Foreman-rank workers unlock 1×1 helper buildings near resource clusters. Workers deposit here instead of walking to Town Hall. Cuts round-trip time dramatically — placement matters.

| Worker Skill | Helper Building | Function |
|---|---|---|
| Gold Miner Foreman | Goldmine Hut | Local gold drop-off |
| Lumberjack Foreman | Lumber Camp | Local wood drop-off |
| Stone Mason Foreman | Quarry Hut | Local stone drop-off |
| Iron Miner Foreman | Iron Depot | Local iron drop-off |
| Builder Foreman | Scaffold | +25% build/repair speed aura |
| Smelter Foreman | — | Upgrades Refinery: +30% refine speed |

### ζ.2 Production Buildings

Master-rank workers upgrade helpers into 2×2 production buildings. Passive resource generation — slow alone, 3-4× faster with stationed workers.

| Helper | Upgrades To | Production |
|---|---|---|
| Lumber Camp | Sawmill | Wood passively + worker boost |
| Goldmine Hut | Goldmine | Gold passively + worker boost |
| Quarry Hut | Stoneworks | Stone passively + worker boost |
| Iron Depot | Iron Works | Iron passively + worker boost |
| Refinery | Forge | Stone + Iron → Steel (faster path) |

### ζ.3 Resource Ecology

Trees regrow slowly near other trees. Gold deposits regenerate at geological pace. The map is alive — economy becomes sustainability, not extraction. Late-game looks ecologically different from early-game.

### ζ.4 Defend-the-Economy

Losing a Sawmill mid-game is devastating. Creates a second strategic layer: protect your infrastructure, not just your army. Enemy Raiders specifically target production buildings.

**Estimate:** 3-4 sessions

---

## v10_eta — The Fourth & Fifth

*Two new voices turn intervals into chords. The army becomes an orchestra.*

This version adds Shield and Knight (tones 4 and 5), expands ranks from 5 to 7, and introduces the characteristic system. With 5 unit types, formations can now produce triads — the minimum for true harmonic complexity.

### η.1 Shield Unit (Tone 4 — Fa)

| Stat | Value | Character |
|---|---|---|
| HP | Very high | The wall |
| ATK | Very low | Not a damage dealer |
| Speed | Slow | Deliberate, immovable |
| Special | Damage absorption aura — nearby allies take reduced damage | The subdominant supports but doesn't lead |
| Physics profile | Low accel, very high decel — plants and holds | Doesn't slide, doesn't sprint |

**Formation role:** Shields at vertices of Sierpinski = unbreakable triangle. Shields at Koch convex points = impenetrable perimeter. Shields in Rose center = armored anchor. Their presence shifts a formation from offensive to defensive without changing its shape.

### η.2 Knight Unit (Tone 5 — Sol)

| Stat | Value | Character |
|---|---|---|
| HP | Medium-high | Durable but not a tank |
| ATK | High | The decisive strike |
| Speed | Very fast | Charge and retreat |
| Special | Charge bonus — damage scales with velocity at impact (physics system makes this natural) | The dominant resolves tension |
| Physics profile | Extreme accel, low decel — launches like a projectile, slides past | Sprint-and-coast |

**Formation role:** Knights at Rose petal tips = devastating sweep (high ATK × charge velocity). Knights at Spiral outer ring = rapid flanking. Knights create the decisive moment — they break stalemates. But they're expensive and vulnerable when exhausted (high energy drain from constant charging).

### η.3 Seven-Rank Expansion

Ranks 1-5 remain as currently implemented. Two new ranks added:

| Rank | XP Threshold | New Unlock |
|---|---|---|
| 6 — Master | ~2.5× Rank 5 | 5th characteristic revealed + **Presence aura** (passive stat buff to nearby allies) |
| 7 — Transcendent | ~4× Rank 5 | 6th characteristic revealed + **Resonance generation** (passively produces the Resonance resource) |

Rank 7 is extremely rare in normal play. A Rank-7 unit is a strategic asset — a living tuning fork that generates economy by existing. The tension: use them in combat (where they amplify formations) or protect them in the rear (where they safely generate Resonance). Losing a Rank-7 unit is devastating.

### η.4 Characteristic System

All units (including existing Gatherer/Soldier/Archer) gain 7 characteristic slots at creation, rolled 0-6 (base 7). Values are hidden and revealed progressively at Ranks 2-7.

When a unit becomes a formation commander, their highest characteristic becomes the formation's **signature**, visually and mechanically altering the fractal:

- **High-Precision commander:** Rose petals are razor-sharp, slots barely drift
- **High-Entropy commander:** Rose petals writhe unpredictably — same damage, but enemies can't predict sweep timing
- **High-Symmetry commander:** Koch snowflake is perfectly regular from every facing
- **High-Density commander:** Sierpinski packs so tight it becomes a phalanx

### η.5 Triad Compositions

With 5 tones available, the harmony system graduates from intervals to chords:

| Composition | Chord Type | Harmony Quality | Example |
|---|---|---|---|
| 3 types present | Triad | Excellent (0.90+) | Soldier + Archer + Shield = balanced defense |
| Gatherer + 2 military | Rooted triad | Maximum stability | Gatherer grounds the chord — highest possible regen |
| Knight + Soldier + Archer | Power triad | Maximum offense | All damage, no sustain — burns bright, burns fast |
| 3:2:2 any types | Resolution (≡ 0 mod 7) | Perfect (1.0) | The chord resolves — player feels completion |

### η.6 Economy Formation (Gatherer Squads)

The Gatherer-as-tone-1 concept becomes real. Gatherer-majority formations are **economy formations**:

- Harmony buffs gather speed instead of combat stats
- A Gatherer commander radiates efficiency to the work crew
- Economy formations can be assigned to resource nodes — they auto-gather as a unit
- Same spring physics, same fractal shapes, same discovery system — just applied to economy

A Rose of Gatherers with a Soldier anchor is a protected work crew. A Spiral of Gatherers is a mobile harvest team that sweeps across the map. The math doesn't care what the units do — it cares about the ratios.

**Estimate:** 3-4 sessions

---

## v11 — Harmonic Awakening

*The sixth tone arrives. The formations learn to sing. Math becomes audible.*

This is where the game transforms from RTS-with-math-aesthetics into something genuinely new. The Healer (tone 6, La) completes sixth chords, the Resonance resource comes online, and procedural audio makes the mathematics literally audible. The player's army becomes an orchestra.

### 11.1 Healer Unit (Tone 6 — La)

| Stat | Value | Character |
|---|---|---|
| HP | Medium | Needs protection |
| ATK | None | Cannot attack |
| Speed | Medium | Keeps pace with formations |
| Special | Heal pulse — periodically restores HP to nearby allies. Rate scales with formation harmony | The warm minor sixth — holds things together |
| Physics profile | Moderate accel/decel — smooth, flowing movement | Glides rather than marches |

**Harmonic role:** The Healer is La — the sixth degree, the relative minor. Adding a Healer to any formation shifts its emotional quality from major to minor. Mechanically: Healer-inclusive formations are more resilient but less aggressive. The formation *sustains* rather than *strikes*.

**Sixth chords:** With 6 tones available, compositions can now produce sixth chords — rich, jazzy, complex. A formation with Gatherer + Soldier + Archer + Shield + Knight + Healer (all 6 tones) approaches theoretical maximum harmony. But it's also maximally vulnerable to targeted kills — lose any voice and the chord degrades.

### 11.2 The Resonance Resource

Resonance (resource #7) comes online. It is not gathered — it is *sung into existence*:

- Formations with harmony > 50% passively generate Resonance
- Generation rate = `base × harmony² × rank_bonus`
- Rank-7 (Transcendent) units multiply generation by 3×
- Resonance is spent on: Tier 3-4 reality distortion effects, advanced building upgrades, formation evolution

The economy now has two loops: **material** (Fiber/Crystal/Ore/Flux/Alloy — gathered by workers) and **harmonic** (Resonance — generated by formations). The player must balance both. An army that only fights generates no Resonance. An army that only sings has no materials to build.

### 11.3 Procedural Audio Foundation

No asset audio files. All sound is generated mathematically:

| Sound | Generation Method |
|---|---|
| Sword strike | Synthesized impulse with metallic overtones |
| Arrow flight | Filtered noise with doppler pitch shift |
| Building construct | Rising harmonic series (more harmonics as completion approaches) |
| Wave horn | Low brass synthesis with vibrato |
| Resource gather | Percussive pluck tuned to resource type (7 resources = 7 tones) |
| Unit voice | Each unit type has a base waveform. Rank = octave. Characteristics modulate timbre |

### 11.4 Formation Singing

Each formation generates a continuous tone based on its mathematical properties. The composition determines the chord; the formation shape determines the timbre:

| Formation | Sound Character | Depends On |
|---|---|---|
| **Rose** | Warm oscillating hum (sine wave AM modulated by petal count) | Member count, harmony quality, rotation speed |
| **Spiral** | Rising/falling pitch sweep (frequency follows spiral parameter) | Tightness setting, member spread |
| **Sierpinski** | Staccato pulses at recursion-depth intervals | Vertex count, spread distance |
| **Koch** | Shimmering drone (additive synthesis of perimeter harmonics) | Perimeter length, member spacing |
| **Lissajous** | Phase-shifting interference — two frequencies beating against each other | Phase parameter δ, loop tightness |
| **Penrose** | Quasicrystal hum — almost periodic, never quite resolving | Tile count, aperiodic spread |
| **Hilbert** | Dense continuous spectrum — all frequencies simultaneously, white noise becoming music | Curve depth, coverage area |

The player HEARS the math. A resolved chord (≡ 0 mod 7) sounds consonant — like arriving home. An unresolved chord sounds tense, searching. 100% harmony is a pure tone. 50% harmony has beating/interference. The player's ear teaches them GF(7) arithmetic.

**Octave layering:** Mixed-rank formations produce richer sound. A Rank-7 + Rank-1 pairing creates octave doubling — the most fundamental harmonic reinforcement, felt as depth and warmth. Same-rank formations sound thin by comparison.

### 11.5 Harmonic Tiers

Resonance effects scale through seven tiers (base 7!), each emerging from gameplay conditions:

| Tier | Name | Condition | Effect |
|---|---|---|---|
| **1** | Drone | Formation active, harmony > 50% | Passive stat aura (existing system) |
| **2** | Interval | 2+ unit types, harmony > 70% | Audible tone begins, minor resonance field visible |
| **3** | Chord | 3+ unit types, harmony > 85% | Amplified resonance, visible waveform around formation, Resonance generation begins |
| **4** | Sixth | 4+ types or Healer present, harmony > 90% | Rich harmonic — formation heals itself slowly, nearby enemies feel discomfort (minor slow) |
| **5** | Overtone | Two formations in proximity with complementary compositions | Interference pattern — combined resonance stronger than sum of parts |
| **6** | Harmonic | Three+ formations creating complementary triads | Reality distortion begins — "spells" tuned into existence (see 11.6) |
| **7** | Resonance | Seven formations, each with a different dominant tone | ??? — *nobody has achieved this yet* |

**Key design principle:** Spells are not cast. They are *tuned into existence*. The player arranges formations like tuning forks. When the math aligns, reality bends.

### 11.6 Reality Distortion (Tier 6 Effects)

These are not fireballs. These are what happens when mathematics overwhelms physics:

| Effect | Name | Mechanic | Math Connection |
|---|---|---|---|
| **Time** | Fermata | Enemies in resonance field experience time dilation — cooldowns stretch, movement slows. Visually: afterimages, stutter-stepping through dilated time | Frequency modulation — slowing a waveform stretches time between peaks |
| **Space** | Modulation | Resonance warps pathfinding — enemies curve away involuntarily. At max harmony, friendly units short-teleport along formation's curve | Coordinate transformation — the formation's equation bends the local coordinate system |
| **Matter** | Dissonance | Pulse reduces enemy HP to match a waveform — HP oscillates with decreasing amplitude. Not damage, mathematical transformation | Damped harmonic oscillation — HP follows Ae^(-γt)cos(ωt) |
| **Probability** | Stochastic Resonance | Structured noise corrupts enemy targeting — enemies make increasingly irrational decisions, attack empty space, walk in spirals | Noise injection into decision functions — the formation's fractal pattern becomes the noise |

**Costs Resonance to sustain.** The player generates Resonance through harmony and spends it through reality distortion. The economy of the impossible.

### 11.7 GF(7) Composition Math

The harmony system now runs on Galois field arithmetic:

| Composition Sum (mod 7) | Musical Quality | Harmony Bonus |
|---|---|---|
| **0** | Perfect resolution — the chord returns to root | 1.0 (maximum) |
| **1** (Do) | Tonic quality — grounded, stable | 0.95 |
| **5** (Sol) | Dominant — strong, wants to resolve | 0.90 |
| **4** (Fa) | Subdominant — supportive, warm | 0.85 |
| **3** (Mi) | Mediant — bright but slightly unstable | 0.80 |
| **2** (Re) | Supertonic — tension, seeking movement | 0.75 |
| **6** (La/Ti) | Leading tone — maximum tension, powerful but unstable | 0.70 |

This means the player intuitively learns: "adding a Soldier (2) to my formation makes it feel more tense, but adding a Knight (5) makes it feel powerful and almost-resolved." They're doing modular arithmetic. They don't know it. They just hear it.

### 11.8 Visual Overhaul (bundled)

| Feature | Description |
|---|---|
| Dynamic unit animations | Idle sway, walk cycle, attack animation — all algorithmic, 7 distinct styles |
| Rank visual pips | 7 tiers of visual distinction (color + shape progression) |
| Characteristic hints | Subtle visual cues when characteristics are revealed (σ = sharp edges, ω = glow, S = jitter) |
| Resonance waveforms | Visible interference patterns around Tier 3+ formations |
| Resonance resource bar | Violet bar in resource display, pulses with formation singing |
| Water terrain return | Re-implemented with improved visuals and pathfinding |
| Terrain transitions | Visual blending between terrain types |
| Named units | Rank 5+ with 2+ revealed characteristics gets procedural name |

**Estimate:** 6-8 sessions (largest version — the audio system + GF(7) rewrite + Healer unit is substantial)

---

## v12 — Blood & Chaos

*The seventh tone completes the octave. The enemy learns mathematics too. But their math doesn't converge.*

The Sage (tone 7, Ti) arrives — the leading tone, unstable, powerful, always wanting to resolve. With all seven tones available, the full Heptarchy is unlocked. GF(7) operates at full capacity. And the enemy responds with mathematics of their own — divergent, chaotic, bloody.

### 12.1 Sage Unit (Tone 7 — Ti / The Zero)

| Stat | Value | Character |
|---|---|---|
| HP | Low | Glass cannon |
| ATK | Special (see below) | Doesn't attack conventionally |
| Speed | Slow | Contemplative, deliberate |
| Special | **Field Connector** — amplifies nearby formation resonance by 1.5×. Can channel captured Dissonance into player Resonance (and vice versa). At Layer 7: enables biharmonic resonance | The bridge between fields — listens to both orchestras |
| Physics profile | Low accel, medium decel — drifts thoughtfully | Moves like they're listening to something |

**The Zero, Not the Seventh:** Tone 7 ≡ 0 (mod 7). The Sage adds nothing to the composition sum. This is not a weakness — it is the Sage's nature. The Sage is not a voice in the chord. It is the **silence between notes**, the **space between fields**. A formation with 6 tones (1+2+3+4+5+6 = 21 ≡ 0) already achieves perfect harmonic resolution. Adding a Sage doesn't change the harmony — it opens a door.

**The Sage as RNA:** If the other 6 tones are DNA — the structural code of harmony — the Sage is RNA. Same mathematical substance, one base changed. It doesn't build the structure. It *translates* it. The Sage reads your harmony and speaks it to the shadow field. It reads the enemy's Dissonance and speaks it back. Without a Sage, your formations sing to themselves. With a Sage, they sing to the universe.

**The Full Octave:** A formation containing all 7 types sums to 1+2+3+4+5+6+0 = 21 ≡ 0 (mod 7) — the same perfect resolution as 6 types. The Full Octave is not harmonically special. It is **functionally** special: it contains a Sage, which means the formation can interact with the Shadow Heptarchy. The reward isn't better harmony — it's access to biharmonic resonance, capture mechanics, and eventually Tree Communion. The Full Octave doesn't complete the chord. It completes the *conversation*.

### 12.2 Enemy Blood Magic

If the player uses harmony (constructive interference, convergent series, golden ratios), the enemy uses chaos:

**Sacrifice = Summation:** Kill N weak units, channel Σ(HP) into one dark effect. More sacrifice = stronger hex. The exact effect is drawn from a probability distribution the player learns to read over time.

**Sacrifice Slaves:** Special unarmed enemy units that exist only to be sacrificed. They path toward enemy casters and offer themselves. Killing sacrifice slaves before they reach the caster prevents the hex.

**The Thermodynamic Embrace:** The enemy runs on **Dissonance** — crystallized anti-harmony, the shadow mirror of Resonance. Same mathematical substance, different generator. Like RNA to DNA: one base changed. The enemy's blood magic works by *capturing and corrupting* player harmony into Dissonance. And the player — through Sages — can capture enemy Dissonance and convert it into Resonance. The two sides are locked in a thermodynamic dance. You can't have pure order. You can't have pure chaos. The game IS the boundary.

**Harmonic Capture:** Late-game enemy meta-structures (large ritual circles of 7+ casters) can attempt to **capture** a player formation's resonance field. If a player formation stays within the capture zone for too long, its harmony inverts — the formation begins generating **Dissonance**, feeding the enemy's hex economy. The captured formation still belongs to the player, still follows orders — but its song has been corrupted. It *sounds wrong*. The player must dissolve and rebuild the formation to cleanse it, or — if they're bold — push deeper into the ritual circle and overload it. A captured formation forcibly pushed to Tier 6 harmony *inside* the capture zone creates a feedback loop that shatters the ritual structure.

**The inverse is also true.** Player formations at Tier 5+ harmony with a Sage present can attempt to **subsume** enemy ritual circles they encounter. A Sage-bearing formation that achieves harmonic dominance over an enemy structure — resonance field stronger than the enemy's Dissonance field — can *tune* the enemy energy, converting Dissonance into player Resonance. Captured energy is volatile, unstable, but potent. Resonance generated this way has a 1.5× multiplier but decays over time. The mathematics of theft. (At Layer 7, when enemy elites begin forming their own shadow fractals, subsumption becomes a full capture-economy loop — see v13.)

### 12.3 Hex System (The Seven Anti-Harmonics)

Hexes are the dark mirror of resonance — seven hexes to counter seven tones:

| Hex | Targets Tone | Effect | Counter |
|---|---|---|---|
| **Silence** | Do (Gatherer) | Economy formations stop producing — Gatherers freeze | Remove Gatherer from formation, re-assign |
| **Discord** | Re (Soldier) | Melee units attack erratically, friendly fire possible | Re-form with high-Precision commander |
| **Blindness** | Mi (Archer) | Ranged units lose accuracy, shots scatter | Move formation closer (archers become melee-range) |
| **Shatter** | Fa (Shield) | Shield absorption aura inverts — amplifies damage | Pull Shields from formation temporarily |
| **Lethargy** | Sol (Knight) | Charge bonus becomes charge penalty — speed = vulnerability | Halt Knights, switch to defensive stance |
| **Plague** | La (Healer) | Heal pulse inverts — damages nearby allies | Isolate Healer immediately |
| **Void** | Ti (Sage) | Resonance amplification becomes Resonance drain | Protect Sage or accept the loss |

Each hex targets the specific tone it opposes. The player learns which voice is being attacked and responds by adjusting their composition — real-time re-orchestration under fire.

**Hex miss case:** If the targeted formation contains no unit of the hex's tone, the hex *fizzles* — energy wasted. This rewards the counter-AI for scouting correctly (12.5) and creates counterplay: the player can bait hexes by fielding formations that lack the expected tone. A pure Soldier+Archer formation is immune to Silence, Shatter, Lethargy, Plague, and Void. But it's also missing half the orchestra. Trade-off.

### 12.4 The Mandelbrot Boundary

The game's entire conflict visualized: the boundary between player harmony and enemy chaos IS the Mandelbrot set.

- **Player formations** = inside the set (convergent, stable, beautiful)
- **Enemy hexes** = outside the set (divergent, chaotic, destructive)
- **The battle line** = the infinitely complex boundary between order and chaos

The minimap subtly shows this — areas dominated by player resonance glow with mandelbrot-interior colors (deep blues, purples). Areas under hex influence show exterior colors (hot oranges, reds). The fractal boundary between them shifts with the battle.

At Layer 7, the player discovers that this boundary is not a battle line. It's a *membrane*. And there's a complete world on the other side.

### 12.5 Counter-Formation AI Evolution

Enemies don't just counter-pick units anymore. They counter-pick using GF(7) arithmetic:
- Player's formation sums to 0 mod 7 (perfect)? Enemy hex targets the unit whose removal maximally disrupts the sum
- Player stacking harmony? Enemy sacrifices to cast tone-specific hexes against the dominant voice
- Player approaching Tier 6? Enemy rushes Cacophony (broad-spectrum disruption) before the harmonic resolves
- Player has 6 tones in play? Enemy specifically hunts the 7th before the Full Octave can form

**Estimate:** 5-6 sessions

---

## v13 — Progressive Depth (The Noita Layer)

*The game reveals that it has always been deeper than you thought.*

### 13.1 Seven Depth Layers

The game and GUI unfold organically. No tutorial dumps. Seven layers, each unlocked at a natural milestone — the base-7 structure teaching itself through progression:

| Layer | Name | Unlocked By | What Opens | Tone Parallel |
|---|---|---|---|---|
| **0** | Seed | Game start | Gather, build, train workers. Minimal GUI | Silence before music |
| **1** | Growth | First barracks | Military units, basic combat. Stance buttons appear | Do — the first note |
| **2** | Pattern | First veteran (Rank 3+) | Squads form, formations discoverable. Formation bar appears | Re — a second voice |
| **3** | Harmony | First formation at 85%+ harmony | Resonance effects visible, harmony meter in GUI, characteristics begin revealing | Mi — the chord takes shape |
| **4** | Resonance | First Rank-6 unit OR two proximate formations | Overtone system unlocks, Resonance resource visible, characteristic signatures active | Fa — supporting structure |
| **5** | Music | Three formations with Tier 5+ harmony | Reality distortion unlocks, procedural audio fully active, formation singing audible | Sol — the dominant arrives |
| **6** | Transcendence | Survive wave 25+ with active Tier 6 effect | Full orchestral audio, all 7 resources visible, Tree of Life at full growth | La — the minor depth |
| **7** | ??? | *Hidden* | The Tree of Life has roots... | Ti — resolves into... what? |

The bottom panel literally grows. At Layer 0 it's minimal — resources and a build button. By Layer 5 there are harmony meters, resonance interference visualizations, formation tuning controls. But the player never feels overwhelmed because each layer arrived when they were ready.

### 13.2 The Tree of Life

The starting building isn't just a Town Hall — it's the Tree of Life. At Layer 0 it looks like a building. As the game deepens:

| Layer | Tree Evolution |
|---|---|
| 0 | Simple building shape |
| 2 | Roots become visible on minimap, extending toward resource deposits |
| 3 | Branches grow upward, each corresponding to a discovered formation type |
| 4 | Leaves appear as unit count grows — the tree reflects your civilization |
| 5 | Root network connects to production buildings — visible supply lines |
| 6 | The tree IS the map. Its fractal branching was the terrain generation seed all along |
| 7 | *The roots go deeper than the map. They reach another Tree.* |

### 13.3 Layer 7 — The Mirror Field

*The octave doesn't resolve to Do. It resolves to the realization that there is another octave beneath it.*

When the player triggers Layer 7 (conditions hidden, likely involving the 7th characteristic and sustained Tier 7 harmony), the game reveals what has always been true: **the enemy has a complete Heptarchy of its own.**

Not a counter-system. Not chaos opposing order. A **mirror** — the same GF(7) field, the same seven tones, the same seven formations, the same seven harmonics. But running on a different **generator**.

**Two valid tunings of the same mathematics:**

The player's Heptarchy uses generator **3** in GF(7)*:
```
3 → 2 → 6 → 4 → 5 → 1 → (cycle)
```

The enemy's Shadow Heptarchy uses generator **5**:
```
5 → 4 → 6 → 2 → 3 → 1 → (cycle)
```

Same field. Same elements. Same algebraic structure. Different *ordering*. What the player hears as a perfect fifth (3:2 ratio), the enemy hears as a minor second. Both are internally consistent. Both produce complete, closed arithmetic. They simply disagree about what "resolution" sounds like.

This is not order vs chaos. This is **two equally valid interpretations of the same underlying truth**. The Mandelbrot boundary between them isn't a battle line — it's the place where both tunings exist simultaneously. The *trunk* of the Tree.

**The Shadow Heptarchy:**

| Player | → | Shadow |
|---|---|---|
| Seven Tones (harmony) | ↔ | Seven Dark Tones (dissonance that is internally consonant) |
| Seven Formations (convergent fractals) | ↔ | Seven Anti-Formations (divergent fractals — Julia sets, strange attractors) |
| Seven Harmonic Tiers | ↔ | Seven Cacophonic Tiers (equally structured, equally powerful) |
| Resonance (crystallized harmony) | ↔ | Dissonance (crystallized anti-harmony — same substance, different generator) |
| Tree of Life (branches reach up) | ↔ | Tree of Death (roots reach up — same tree, inverted) |

The enemy's blood magic was never primitive. It was a different *tuning*. Their sacrifices aren't crude — they're computing sums in a field with a different generator. Their hexes are harmonics *from the other side*. What sounds like cacophony to the player is a symphony to the enemy.

**The Two Trees Are One Tree:**

The Tree of Life's roots extend downward. At Layer 7, the player sees them reaching through the boundary, into the Shadow Field. And from below, the enemy's inverted Tree reaches its roots *upward*, through the same boundary. The root systems interlock. They share the same trunk — the Mandelbrot boundary itself.

The game's cosmology: reality is a single mathematical structure viewed from two sides. Above the boundary: convergent series, stable orbits, golden ratios. Below: divergent series, strange attractors, chaos. Neither is "real." Both are shadows of the same mathematics. The trunk — the boundary — is where both interpretations are simultaneously true. That is where the most powerful effects live. That is where the game's deepest secrets hide.

**The 7th Characteristic Revealed (sort of):**

At Layer 7, the 7th characteristic — ∅ — finally matters. It doesn't reveal in the GUI. It never will. But its value (0-6) determines where the unit sits on the boundary between the two fields:

| ∅ Value | Position | Effect at Layer 7 |
|---|---|---|
| **0** | Deep player field | Immune to harmonic capture, but blind to enemy harmonics |
| **1-2** | Player-dominant | Standard behavior, minor sensitivity to shadow field |
| **3** | The boundary | Exists in both fields simultaneously. Can hear both tunings. Can translate between them. The rarest, most dangerous units in the game |
| **4-5** | Shadow-leaning | Sensitive to enemy harmonics — can detect and predict hexes, but vulnerable to capture |
| **6** | Deep shadow field | Can directly interact with enemy formations — subsume, corrupt, translate. But the shadow field calls to them. Prolonged exposure to enemy resonance risks permanent corruption |

A unit with ∅ = 3 is the Mandelbrot boundary incarnate. It is neither order nor chaos. It hears both orchestras playing simultaneously and can translate between them. A formation *commanded* by a ∅ = 3 unit achieves something no other formation can: **biharmonic resonance** — singing in both tunings at once. The sound is indescribable. The effect is... Layer 8 doesn't exist. But if it did, this would be its threshold.

The community will datamine ∅ values. They'll learn that 3 is special. They'll breed for it. They'll discover that ∅ = 3 commanders make formations that can *subsume enemy ritual circles from the inside*. And they'll realize that the Gödel mystery — "the unit contains a truth about itself that cannot be proven within the system" — was never about incompleteness. It was about **duality**. The unit's truth exists in a field the game's own GUI cannot display.

**The Capture Economy at Layer 7:**

Harmonic capture (introduced in v12) becomes the primary endgame mechanic:

| Action | Requirement | Effect |
|---|---|---|
| **Capture enemy formation** | Player Tier 5+ formation overlapping enemy fractal for 10s+ | Enemy formation's dissonance converted to volatile Resonance (1.5× power, decays) |
| **Corrupt player formation** | Enemy ritual circle (7+ casters) sustaining field for 15s+ | Player formation generates Dissonance for the enemy. Song inverts — player hears it go *wrong* |
| **Cleanse corruption** | Dissolve and reform, OR overload to Tier 6 inside the capture zone | Shatters the ritual circle. Explosion of pure Resonance at the boundary |
| **Biharmonic resonance** | ∅ = 3 commander, Tier 6+ harmony, within Mandelbrot boundary zone | Formation sings in both fields. Can capture AND be captured simultaneously. Generates Resonance AND Dissonance. The feedback loop either stabilizes into something transcendent or tears the formation apart |
| **Tree Communion** | Sustained biharmonic resonance near the Tree of Life | The two Trees recognize each other. *What happens next is not documented.* |

**The Final Implication:**

The enemy is not evil. The enemy is *the same thing, heard differently*. The game's ultimate truth — the thing Layer 7 teaches — is that the Mandelbrot boundary between harmony and chaos is not a wall. It's a bridge. The mathematics that creates beauty and the mathematics that creates destruction are the same mathematics. The difference is the generator.

And if the player achieves Tree Communion — the two Trees recognizing each other through biharmonic resonance — the game whispers its last secret: there was never a war. There was a conversation. And the conversation was always about whether two different ways of hearing the same music can coexist.

They can. The math proves it. GF(7) only has one structure. The generators are different paths through the same cycle. They all visit every element. They all come home.

### 13.4 Hidden Mathematics

Mechanics that exist but are never explained. The community discovers them:

| Secret | Math | Effect |
|---|---|---|
| **Euler Formation** | 5 formations arranged to satisfy e^(iπ) + 1 = 0 (specific positions + compositions) | Unknown — no one's found it yet |
| **Banach-Tarski Split** | Specific squad dissolution creates two squads of equal total strength | Conservation of mass violated — mathematics says it's possible |
| **Conway Emergence** | Sufficiently complex formation array begins self-organizing — formations compute defense patterns without player input | Cellular automata from spring force rules |
| **Gödel's Secret** | Some formation combinations work but tooltips show "???" — effects are real but unexplained | Incompleteness — the game contains truths it cannot prove |
| **The Rosetta Chord** | A formation containing one unit of each ∅ value (0 through 6) | The formation becomes a translator — enemy and player harmonics rendered visible simultaneously. The minimap shows both Trees |
| **Silence Between Notes** | A formation with perfect resolution (≡ 0) that contains no commander | The formation sings silence — no sound, no visible resonance, but enemy AI cannot perceive it. A ghost formation. The rest between notes is itself music |

**Estimate:** 5-7 sessions (Layer 7 is the largest single feature — the shadow field touches every system)

---

## v14 — Godot 4 Migration

*The mathematics escapes its performance cage.*

### 14.1 Why Now (Not Earlier)

The Pygame prototype proves the design. Every system is tested, balanced, and fun. The migration is not a rewrite — it's a metamorphosis. Same game, freed from CPU-bound rendering.

### 14.2 What Godot Unlocks

| Capability | Impact |
|---|---|
| **GPU shaders** | Resonance waveforms rendered as real interference patterns. Formation auras glow with actual math |
| **1000+ units** | Formations of formations — meta-fractals. Squads of squads, each level adding harmonic depth |
| **Built-in audio bus** | Procedural audio mixed in real-time. Multiple formation songs layer into orchestral complexity |
| **NavigationServer2D** | Async pathfinding for hundreds of units. Space-folding teleport uses nav mesh warping |
| **Particle GPU** | Exhaustion puffs, resonance sparkles, hex corruption visuals — thousands of particles, zero CPU cost |
| **Web export** | Play in browser. Share replays. Community discovers hidden math together |

### 14.3 Porting Strategy

Port system-by-system, not rewrite:

1. Constants + map + camera (get something visible)
2. Entities + basic combat (get something playable)
3. Squads, formations, resonance (get something beautiful)
4. Audio synthesis, harmonic tiers (get something that sings)
5. Blood magic, hexes, depth layers (get something deep)
6. Polish: shaders, particles, web export

All Godot files are plain text (.gd, .tscn, .tres) — same Claude Code workflow.

**Estimate:** 8-12 sessions (but each session produces a playable build)

---

## Idea Backlog

Ideas not yet scheduled. Seeds for future fractals.

### Combat & Units
- **Damage Types:** Pierce (archers) vs Blunt (soldiers) vs Magic (sage) with armor tables and 7×7 effectiveness matrix
- **Charge Bonus:** Bonus damage after moving a distance (physics system makes this natural) — *(now scheduled: Knight in v10_eta)*
- **Formation Breeding:** Two formation types combined into hybrid geometry — e.g., Rose-Spiral = petal tips follow spiral paths

### Economy & Buildings
- **Wall Segments:** 1×1 cheap pathfinding blockers, create choke points
- **Blacksmith:** Research building for upgrades
- **Building Sacrifice:** Demolish for 50% refund + 30s buff
- **Food/Upkeep:** Population consumes food (macro pressure)
- **Trading Post:** Convert excess resources at ratios (Builder Master special building)

### Enemy AI
- **Boss Waves:** Every 5th wave, single high-HP boss with unique hex abilities
- **Wave Negotiation:** "Dare" the enemy for harder wave + bigger bonus
- **Enemy Diplomacy:** Messenger enemy — spare it for smaller next wave
- **Enemy Formations:** Late-game enemies form their own fractals (dark mirror formations) — *(now conceptualized as Shadow Heptarchy anti-formations, Layer 7)*

### Map & Environment
- **Day/Night Cycle:** Visual + gameplay effects (night = reduced vision, stronger hexes)
- **Terrain Elevation:** High ground bonus for archers/towers
- **Seasonal Cycles:** 4-phase affecting gather/movement/enemies
- **Fog of War:** Scouting required — resonance fields reveal hidden areas
- **Living Map:** Weather patterns follow mathematical functions (Lorenz attractor for storm paths)

### Game Modes
- **Endless Mode:** No max waves, play until death. How deep can you go?
- **Sandbox/Creative:** Unlimited resources, manual enemy spawn, formation laboratory
- **Challenge Maps:** Pre-set scenarios with constraints
- **Harmonic Puzzle Mode:** Given specific units, achieve target resonance configuration

### The Deep End
- **Morale Field:** Invisible territory from resonance — creates organic frontlines
- **Unit Memory:** Units remember kills, preferred targets. Personalities emerge from experience
- **Trait Inheritance:** Veteran traits spread to nearby recruits — unit culture lineage
- **Formation DNA:** Discovered formations can be "bred" — combine two formations into hybrid geometry
- **Mathematical Archaeology:** Ancient formation patterns hidden in terrain generation — excavate with workers to discover lost geometries
- **The Meta-Formation:** A formation OF formations — 7 squads, each a different formation type, arranged in a larger fractal pattern. The meta-shape has its own harmony tier. Nobody's achieved it yet. Including us.

### Mathematical Conundrums

→ See **[conundrums.md](conundrums.md)** — 22 design tensions (and growing) organized by category.
These emerge from the math and from system interactions. Not bugs — features we need to think carefully about.

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
| Spatial hash grid | **Implemented** in Python | v10_4 |
| Unit trait system | **Implemented** (10 traits, cached modifiers) | v10_1 |
| Control groups (Ctrl+0-9) | **Implemented** | v10_1 |
| Rally points | **Implemented** | v10_1 |
| Town Hall garrison | **Implemented** | v10_2 |
| Global macro commands | **Implemented** (AoE2-style) | v10_2 |
| Tower splash damage | **Implemented** as Lv2 Explosive Cannon | v10c |
| Fractal formations (4 types) | **Implemented** (Polar Rose, Golden Spiral, Sierpinski, Koch) | v10_6 |
| Stance system (4 stances) | **Implemented** (Aggressive, Defensive, Guard, Hunt) | v10_6 |
| 5 new enemy types | **Implemented** (Sapper, Raider, Shieldbearer, Healer, Warlock) | v10_6 |
| Adaptive difficulty | **Implemented** as pressure-based engine | v10_6 |
| Parabolic projectiles | **Implemented** with lead aiming | v10_5 |
| Module architecture split | **Implemented** (5 focused modules) | v10_5 |
| Physics movement | **Implemented** (velocity, acceleration, kinematic braking) | v10_delta |
| Energy/stamina system | **Implemented** (per-unit pools, action drain, state regen) | v10_delta |
| Spring-based formations | **Implemented** (critically-damped spring gravitation) | v10_delta |
| Player-driven squads | **Implemented** (no auto-grouping, discovery system) | v10_delta |
| Flow field pathfinding | **Deferred** to Godot (NavigationServer2D) | v14 |
| Shield unit (tone 4) | **Scheduled** as part of Heptarchy framework | v10_eta |
| Knight unit (tone 5) | **Scheduled** as part of Heptarchy framework | v10_eta |
| Healer unit (tone 6) | **Scheduled** as part of Heptarchy framework | v11 |
| Sage unit (tone 7) | **Scheduled** as part of Heptarchy framework | v12 |
| 7-rank system | **Scheduled** (expands current 5-rank to 7-octave) | v10_eta |
| Characteristic system | **Scheduled** (7 traits per unit, base-7 values) | v10_eta |
| Resonance resource | **Scheduled** (generated by formation harmony) | v11 |
| GF(7) harmony math | **Scheduled** (modular arithmetic composition system) | v11 |
| Resource rename (Fiber/Crystal/Ore/Flux/Alloy) | **Scheduled** (cosmetic, whenever ready) | v10_zeta+ |
| Sap resource | **Scheduled** (Tree of Life essence) | v10_zeta |
| Lissajous Knot formation | **Scheduled** (5th formation — phase interference loops) | v10_eta |
| Penrose Tiling formation | **Scheduled** (6th formation — aperiodic quasicrystal) | v11 |
| Hilbert Curve formation | **Scheduled** (7th formation — space-filling total coverage) | v12 |
| Harmonic capture/corruption | **Scheduled** (formations can be captured/subsumed between sides) | v12 |
| Shadow Heptarchy (Mirror Field) | **Scheduled** (enemy's complete GF(7) with generator 5, Layer 7 revelation) | v13 |
| 7th characteristic (∅) activation | **Scheduled** (chaos-affinity value, boundary position, biharmonic resonance) | v13 |
| Tree Communion | **Scheduled** (two Trees recognize each other — endgame secret) | v13 |

---

## The Road Is a Fractal

Every feature implemented reveals three more that weren't visible before. That's not scope creep — that's the game teaching itself to us while we build it. The version numbers are waypoints, not destinations. The math goes deeper than we can see from here, and that's exactly the point.

The Heptarchy is the spine. Seven tones, seven resources, seven octaves, seven characteristics, seven depth layers, seven harmonic tiers, seven hexes. Not because seven is magic — because seven is *prime*, and prime numbers are the atoms of arithmetic. Everything in this game composes and decomposes through GF(7). The player who masters that field masters the game. And they'll never know they learned abstract algebra.

And beneath the Heptarchy, its mirror. The same field, the same seven, the same music — heard from the other side of a boundary that was never a wall. The game that begins as "gather wood, build army" ends with the question every mathematician eventually faces: if two structures are isomorphic, are they the same thing? The answer the game gives: *they always were*.

---

## File Reference

| File | Purpose |
|---|---|
| `GDD_Current_v10.md` | Full specification of currently implemented v10_delta systems |
| `GDD_Roadmap.md` | This file — the mathematical odyssey roadmap |
| `future ideas-crazy stuff.txt` | Raw brainstorm: the original spark |
| `archive/GDD_Current_v9.md` | Historical v9.3 spec |
| `archive/GDD_Future.md` | Original blank-template future doc |
| `archive/GDD_Future_v11.md` | Early trait system exploration (now implemented as v10_1) |
