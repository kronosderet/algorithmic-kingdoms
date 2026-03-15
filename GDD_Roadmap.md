# GDD Roadmap — Resonance

> Living document. Tracks the path from simple RTS to mathematical odyssey.
> Current implemented version: **v10_epsilon3** (see `GDD_Current_v10.md` for full spec)
> Last updated: 2026-03-15
>
> *"This game should be combat math. The paradox of it being nonexistent anywhere*
> *in nature, existing only in minds, but ruling the universe nonetheless.*
> *Harmony in chaos, chaos in harmony. That should be the absolute theme."*

---

## The Vision

Resonance is a game that teaches math the way math deserves to be taught — not with pencil and paper, but with armies that sing trigonometric harmonies, formations that warp spacetime through golden ratios, and enemies that cast hexes powered by divergent series. Every system in the game IS a mathematical object wearing a gameplay costume. The player learns to wield mathematics as a force multiplier without ever seeing an equation.

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
| **2** | Re (D) | **Warden** | Melee line | Steady, reliable second voice | v1 (existing) |
| **3** | Mi (E) | **Ranger** | Ranged DPS | Bright, cutting major third | v1 (existing) |
| **4** | Fa (F) | **Bulwark** | Tank/absorb | Subdominant — supports, doesn't lead | v10_eta |
| **5** | Sol (G) | **Lancer** | Fast melee/charge | The dominant — resolves tension, decisive | v10_eta |
| **6** | La (A) | **Mender** | Support/sustain | Warm, minor quality, holds things together | v11 |
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
| Rose (1) | Warden Re (2) | 1×2 = 2 (consonant) | Petals sweep — melee strikes |
| Spiral (2) | Ranger Mi (3) | 2×3 = 6 (tension → drive) | Outer ring sightlines — ranged pressure |
| Sierpinski (3) | Bulwark Fa (4) | 3×4 = 12 ≡ 5 (dominant) | Vertices hold — defensive spread |
| Koch (4) | Lancer Sol (5) | 4×5 = 20 ≡ 6 (tension) | Perimeter charge — decisive enclosure |
| Lissajous (5) | Gatherer Do (1) | 5×1 = 5 (dominant) | Phase loops = gather routes — economy formation |
| Penrose (6) | Mender La (6) | 6×6 = 36 ≡ 1 (root) | Unpredictable position = hard to target — sustain |
| Hilbert (7) | Sage Ti (7) | 0 × 0 = 0 (the gate) | Total coverage + field bridge = the conversation fully open |

When a formation contains its affinity tone, a bonus applies — the instrument is playing its native register. Penrose×Mender is especially notable: product ≡ 1, meaning the Mender in Penrose returns to the root. The aperiodic pattern becomes a sanctuary.

### Why Seven Works

- **Miller's Law:** Working memory holds 7±2 chunks — the player can hold the full system in their head
- **Musical octave:** 7 tones before repetition — the most fundamental structure in human auditory cognition
- **GF(7) is a field:** Every composition produces unique results. No collisions. Complete algebraic closure
- **Cyclic group:** 3 generates all of GF(7)* — (3,2,6,4,5,1) — every tone reaches every other through multiplication
- **Prime:** No zero divisors means no "dead" combinations. Everything matters

---

## The Sentinel Lattice — Base as Instrument

*If formations are the melody, the base is the instrument that plays it.*

The grid dies. Base-building becomes **symmetry-building**. The player doesn't place buildings on a coordinate grid — they construct dihedral symmetries out of **Sentinels** (standing-stone anchor structures) and fill the interior with functional buildings. A symmetric base resonates. An asymmetric base improvises. Both are valid. Both have consequences.

### Why "Sentinels"

Not scaffolds (temporary), not pylons (borrowed), not anchors (passive). Sentinels are **standing stones that watch over the geometry they define**. They are permanent. They are aware. They hum at the frequency of the symmetry they create. Like Stonehenge — they don't *do* anything mechanically. They create the **sacred structure** within which meaning happens.

### Dihedral Symmetry Progression

Sentinels define **dihedral groups** — the mathematical symmetries of regular polygons. Placing Sentinels unlocks progressively richer symmetry orders:

| Order | Geometry | Sentinels | Structure | Musical Foundation |
|---|---|---|---|---|
| **D1** | Mirror axis | 2 | A line — bilateral symmetry, the simplest | Unison drone — one sustained note |
| **D2** | Cross | 4 | Two perpendicular axes — quadrilateral foundation | Root + fifth — a power chord |
| **D3** | Triangle | 6 | Three axes — the first polygon, Sierpinski's seed | Triad — the minimum chord |
| **D4** | Square | 8 | Four axes — the classic base layout | Tetrachord — four-voice voicing |
| **D6** | Hexagon | 12 | Six axes — the honeycomb, nature's tiling choice | Hexatonic scale — rich harmonic texture |
| **D8** | Octagon | 16 | Eight axes — maximum practical symmetry | Full chromatic coverage |

Higher orders (D3, D6) create triangular and hexagonal lattices that tile space perfectly — bases that can expand fractally without gaps. The choice between D4 (square) and D6 (hex) is itself a strategic decision: square bases have orthogonal sight lines (good for ranged defense), hex bases have more axes of symmetry (stronger resonance bonuses).

### Self-Similar Extension — Fractal Bases

The killer step. Once a D4 square of Sentinels is complete, the entire square can serve as one "super-Sentinel" vertex in a larger D4 structure. Sentinels of Sentinels. The base becomes a fractal — the same recursive self-similarity as Sierpinski and Koch formations, but built from stone instead of Wardens.

```
Level 0:  S · · S       (4 Sentinels, basic D4 square)
          · · · ·
          · · · ·
          S · · S

Level 1:  [L0] · · · [L0]     (4 Level-0 squares arranged in a larger D4)
           · · · · · · ·
           · · · · · · ·
          [L0] · · · [L0]
```

Each recursion level deepens the base's harmonic foundation — more overtones, richer drone, stronger resonance bonuses. The base *is* a formation, just built from architecture instead of Wardens.

### Filling the Lattice — Functional Buildings

Sentinels define the skeleton. Other buildings fill the interior:

| Building | Role | Symmetry Interaction |
|---|---|---|
| **Harmonic Mill** (Refinery) | Resource processing | Paired Harmonic Mills across a symmetry axis refine 30% faster |
| **Resonance Forge** | Unit training | Mirrored Resonance Forges train in rhythmic alternation — one finishes as the other starts |
| **Sentinel** | Defense + Geometry | Sentinels ARE the lattice anchors — their resonance fields merge along symmetry axes for amplified area defense |
| **Fiber Spire/Flux Spire/etc.** | Production | Symmetric production buildings pulse together — visible rhythm |
| **Tree of Life** | Center | The natural center of any symmetry — the origin point all axes pass through |

**Key rule:** A building placed on one side of a symmetry axis gains a bonus when its mirror position is also filled. The bonus scales with the symmetry order — D6 mirror bonuses are stronger than D2. The player is rewarded for *completing the pattern*, never forced.

### The Base as Key Signature

The base doesn't play notes — it determines **what key the world is in**.

**Symmetric base → Tonal center established:**
- A complete D6 hex of Sentinels with buildings filling the interior = a clear key signature
- The background music has a **drone root** — a bass note that everything relates to
- Formations singing over a tonal center = classical harmony — structured, powerful, reinforcing
- Buildings inside the symmetry resonate with each other: Harmonic Mills refine faster, Resonance Forges train in rhythm, the Tree of Life pulses on the downbeat

**Asymmetric base → Atonal / free jazz:**
- Buildings placed without symmetry = no tonal center
- Background music becomes **polytonal wandering** — not silence, not chaos, but restless searching
- Individual buildings still function, but they're all playing in different keys
- No resonance bonuses — but not purely a penalty (see "The Jazz Choice" below)

**Partial symmetry → Detuned tension:**
- An almost-complete D6 with one missing Sentinel = five voices where six should be
- The drone has a gap — audible as beating, dissonance, yearning
- Rebuilding the missing Sentinel resolves the tension — the player *hears* the base heal

### Procedural Base Music

| Base State | Music Character |
|---|---|
| No Sentinels | Silence / ambient wind |
| D1 (2 Sentinels) | Single sustained drone note |
| D2 (4 Sentinels) | Drone + fifth — power chord pad |
| D3 (6 Sentinels) | Three-voice chord, slow arpeggiation |
| D4 complete | Four-voice chord, gentle pulse |
| D6 complete | Six-voice voicing, rich harmonic warmth |
| Partial symmetry | Notes present but some detuned — beats and tension |
| Fractal Level 1 | Overtones appear — the drone develops shimmer |
| Fractal Level 2+ | Cathedral organ — deep fundamental with full overtone series |
| Asymmetric sprawl | Free jazz — all the notes but no tonal gravity, walking bass |

Formations then play **over** the base drone. A Rose squad's melody sounds like a violin solo over the base's organ chord. If the formation's geometry resonates with the base's symmetry group (see below), it's consonant. If not, it's tension — not bad, just *yearning to resolve*.

### The Jazz Choice — Strategic Asymmetry

Asymmetry is not purely a penalty. It is a **strategic alternative**:

| Symmetric Base | Asymmetric Base |
|---|---|
| Production bonuses (mirror buildings) | No production bonuses |
| Strong tonal center (formations sing louder) | No tonal center |
| Predictable — enemies can read the geometry | **Unpredictable** — enemy AI cannot optimize against it |
| Cathedral: structured, reinforcing, crescendo | Jazz club: improvisational, adaptive, chaotic beauty |
| Weak to symmetry-breaking attacks (lose one Sentinel, key collapses) | **Resilient** — no single point of failure |

A perfectly symmetric base is a cathedral — powerful but brittle. An asymmetric base is a jazz ensemble — less raw power but impossible to siege efficiently because there's no pattern to exploit. The player chooses: harmonic power or structural resilience. Or — most interesting — they build a symmetric core with asymmetric outer defenses, creating a musical texture where the tonal center holds but the edges improvise.

### Formation × Base Resonance

The base's symmetry group **interacts** with formation geometry. When they match, resonance cascades — formation sings louder, base hums deeper, bonuses stack:

| Formation | Resonant Base Symmetry | Why |
|---|---|---|
| **Polar Rose** | D6 / D8 | Circular harmonics — Rose is polar, high-order dihedral approaches circular |
| **Golden Spiral** | D1 / self-similar | Spiral symmetry is growth, not reflection — matches bilateral + fractal depth |
| **Sierpinski Triangle** | D3 / D6 | Triangle-based recursion — Sierpinski IS D3 |
| **Koch Snowflake** | D6 | Koch IS a hexagonal fractal — D6 is its native symmetry |
| **Lissajous Knot** | D4 | Phase interference in orthogonal axes — square symmetry |
| **Penrose Tiling** | D5 (!) | The only formation that demands a pentagonal base — 5-fold symmetry, the quasicrystal's fingerprint. D5 is impossible to tile perfectly, which is the point |
| **Hilbert Curve** | D4 / fractal D4 | Space-filling curve on a square grid — Hilbert IS recursive D4 |

When a formation operates within a base whose symmetry matches, the Formation × Base resonance product applies:
- **Matched:** Formation harmony bonus ×1.3, base production bonus ×1.2, combined audio = consonant layering
- **Neutral:** Standard bonuses, no interaction
- **Clashing:** Slight detuning — audible but not mechanically punishing. A hint to the player, not a trap

### Sentinel Placement UX

When placing a Sentinel, **ghost lines** appear showing:
- **Symmetry axes** the new Sentinel would create or complete
- **Mirror ghosts** — translucent Sentinel outlines showing where paired Sentinels should go to complete the next symmetry order
- **Fill zone** — the interior area where buildings would gain symmetry bonuses, shaded by completion percentage
- **Color coding:** Complete axes glow gold. Broken/incomplete axes flicker. Potential axes (one more Sentinel needed) pulse faintly

Players naturally discover dihedral symmetry by following the guides. They don't need to understand group theory — the ghosts teach it visually. A player who places 4 Sentinels in a square *sees* the D4 axes light up and *hears* the drone deepen. They know they did something right. Mathematics taught by architecture.

### Symmetry Breaking as Warfare

The Dark 7 don't just kill units — they try to **break the base's symmetry**:

- **Hexweaver** (anti-Sage) specifically targets Sentinels — destroying one collapses the symmetry order. A D6 hex losing one Sentinel drops to broken-D6: the music *lurches*, the drone acquires a painful beat, mirror bonuses on that axis vanish
- **Blight Reaper** (anti-Gatherer) targets production buildings, breaking fill symmetry — the interior pattern degrades
- **Bloodtithe** (anti-Mender) sacrifices allied units near Sentinels to corrupt them — a corrupted Sentinel still stands but its axis produces Dissonance instead of harmony. The base's drone acquires a dark undertone on that axis

Rebuilding isn't just repair — it's **restoring the music**. The moment a replacement Sentinel completes a broken axis, the drone resolves and the player feels the relief physically. Defending your symmetry becomes as visceral as defending your army.

### Sentinel Lattice × Heptarchy Integration

The Sentinel system locks into the Heptarchy at every level:

| Heptarchy Layer | Sentinel Connection |
|---|---|
| **7 Tones** | Each Sentinel could be *tuned* to a tone — D6 base with each axis tuned to a different tone creates a six-voice chord infrastructure |
| **7 Resources** | Sentinels cost Resonance to place (the 7th resource), creating a feedback loop: formations generate Resonance → Resonance builds Sentinels → Sentinels amplify formations |
| **7 Ranks** | Rank-7 (Transcendent) units near Sentinels amplify the base drone — living tuning forks enhancing standing stones |
| **7 Characteristics** | Symmetry (Γ) characteristic directly affects Sentinel placement — high-Symmetry commanders reveal optimal Sentinel positions |
| **7 Formations** | Formation × Base symmetry resonance (table above) |
| **7 Depth Layers** | Sentinel system unlocks progressively: D1-D2 visible at Layer 1, D3-D4 at Layer 3, D6+ at Layer 5, fractal extension at Layer 6 |
| **7 Harmonic Tiers** | Base symmetry order feeds into tier calculation — a D6 base lowers the threshold for Tier 4+ effects |

### Scheduled Introduction

The Sentinel Lattice spans multiple versions, each adding depth:

| Version | What's Added |
|---|---|
| **v10_zeta** | Sentinels as placeable structures. D1-D4 symmetry detection. Mirror building bonuses. Ghost placement guides |
| **v10_eta** | D6 symmetry. Sentinel tuning (tone assignment). Formation × Base resonance interaction |
| **v11** | Base drone audio. Symmetry-dependent procedural music. Asymmetric jazz mode. Sentinel corruption mechanic |
| **v12** | Hexweaver targeting Sentinels. Symmetry-breaking warfare. Self-similar fractal extension (Level 1+) |
| **v13** | Shadow Sentinels (enemy equivalent). Fractal Level 2+. Full Heptarchy integration. Layer-gated progression |

---

## The Living Strata — Map as Fossil Record

*The terrain is not a stage. It is the oldest character in the story.*

Current map generation places resources and terrain types procedurally but statically — the map is born and never changes. The Living Strata system replaces this with **temporal map generation**: the map simulates compressed geological and historical time before the player arrives. Every river, ruin, and resource deposit is the fossil of a mathematical process that ran for simulated millennia. The player who learns to read the land reads the past — and infers the future.

### The Principle

The map is not a function of space. It is a function of **space and time**: `f(x, y, t)`.

At game start, the generator runs a compressed simulation across seven geological epochs. Each epoch applies mathematical processes — erosion, plate drift, ecological succession, civilizational rise and fall — that leave permanent marks on the terrain. The final state `f(x, y, T)` is what the player sees. But every feature on that map is an artifact of a specific epoch, and a player who understands the processes can reverse-engineer *why* a gold vein runs along that fault line, *why* the forest is thickest near the old river delta, and *why* those ruins form a hexagonal pattern.

### The Seven Epochs

Each epoch corresponds to a process class. The generator runs them sequentially, each building on the output of the last — stratigraphy, but for mathematics:

| Epoch | Name | Process | What It Leaves Behind |
|---|---|---|---|
| **1 — Stone** | Tectonics | Voronoi cell boundaries drift and collide. Collision zones uplift into mountains; divergence zones sink into valleys. Elevation field emerges from plate dynamics | Mountain ranges, valleys, continental shapes. **Flux and Ore deposits form along fault lines** (collision stress zones) — the player learns that resources cluster at geological boundaries |
| **2 — Water** | Hydrological erosion | Gradient descent on the elevation field. Water flows downhill, carves channels, deposits sediment in low areas. Diffusion equation smooths terrain over time | Rivers (solutions to ∇²h = 0 with boundary conditions), lakes in local minima, fertile deltas where sediment accumulates. **River paths are mathematically optimal** — the shortest path water found downhill |
| **3 — Green** | Ecological succession | Cellular automata: bare soil → grass → shrubs → forest. Growth rates depend on water proximity, elevation, soil fertility (sediment from Epoch 2). Fire/disease as periodic reset | Forests densest near rivers and deltas. Grasslands on high plateaus. **Tree distribution follows a logistic growth curve** — the player notices forests are thickest where three conditions overlap (water, low elevation, sediment) |
| **4 — Crystal** | Mineral crystallization | Crystal and Stone deposits form through simulated pressure and time. Volcanic regions (tectonic hotspots from Epoch 1) produce rare minerals. Deeper deposits require more digging | **Resource distribution is geologically motivated** — Ore near volcanic soil, Crystal in mountain roots, Crystal in pressure zones. The player who reads the terrain finds resources faster than one who searches blindly |
| **5 — Ruin** | Civilizational echoes | Seed 1-3 "ancient civilizations" with simple expansion rules. They build, grow, conflict, and collapse. Their remains persist as ruins on the map | Ruined walls (old perimeters), overgrown foundations (building footprints), broken Sentinel lattices (partial symmetry groups — see below). **Ruins are archaeological hints** — the geometry of a ruin tells you what the ancients knew |
| **6 — Scar** | Resonance residue | Ancient civilizations that achieved high harmony leave **resonance scars** — areas where the terrain itself hums faintly. Ancient battles leave **dissonance wounds** — terrain that feels wrong, where pathfinding costs are slightly higher | Resonance scars glow faintly at night (or at high depth layers). Dissonance wounds darken terrain. **These are the first hints that the mathematics of harmony predates the player** — someone sang here before |
| **7 — Silence** | Entropic rest | Time passes. Some ruins erode further. Some scars fade. Others crystallize into permanence. The world settles into the state the player inherits | The final map — scarred, storied, alive with compressed history. Not random. *Authored by time* |

### Ruins as Archaeological Puzzles

The Epoch 5 civilizations are simple procedural agents, but their remains are rich:

| Ruin Type | What It Was | What the Player Finds | What It Teaches |
|---|---|---|---|
| **Broken Sentinel Ring** | An ancient D4 or D6 base | 3-5 standing stones in partial symmetry. One or two missing. Ghost axes faintly visible at Layer 3+ | The ancients knew about Sentinel symmetry. The player learns formation geometry from ruins before discovering it themselves |
| **Overgrown Resonance Forge** | Military training site | Stone foundations in a rectangular pattern. Excavate with Gatherers to recover a small resource cache | Building placement patterns — the player sees how the ancients organized their base |
| **Collapsed Harmonic Mill** | Refinery/forge | Cracked stone with mineral residue. May contain an Alloy cache. Located near ancient resource routes | Resource processing infrastructure — hints at the forge chain |
| **Resonance Obelisk** | A single Sentinel that survived | A standing stone that still hums. If the player builds their own Sentinel nearby, the obelisk activates and contributes to the symmetry lattice | **The most valuable ruin** — a free Sentinel in a location chosen by ancient mathematics. The player who builds around it inherits the ancients' geometry |
| **Shattered Formation Glyph** | A carved pattern in stone | A partial fractal etched into the ground — recognizable as a Rose, Spiral, or Koch fragment. Counts as a formation discovery hint | The ancients used the same formations. The math is universal. The player feels less alone |
| **Dissonance Crater** | An ancient battle site | Darkened terrain, slightly warped. Enemy spawn bias toward this location (the darkness remembers). Faint anti-harmonic hum at Layer 4+ | **Where the ancients fell.** The terrain warns: this place attracted darkness before, and it will again |

### Reading the Land — Environmental Literacy

The map teaches the player to think like a geologist, an ecologist, and an archaeologist:

**Geological reading:**
- Flux veins follow tectonic fault lines → find the mountain range, trace its edge, find Flux
- Ore clusters near volcanic soil (dark terrain) → look for the hot spots
- Rivers carve toward the sea by gradient descent → follow a river upstream to find highlands with Crystal deposits

**Ecological reading:**
- Dense forest = water + sediment + time → fertile land, good for Fiber economy
- Sparse highland grass = thin soil + wind exposure → poor gathering, good defensive positions
- Forest gaps = ancient fire or disease → may regrow, may indicate underlying geology

**Archaeological reading:**
- Hexagonal ruin pattern = ancient D6 Sentinel base → the ancients chose this spot for a reason (resource convergence, defensible terrain, resonance-positive ground)
- Linear ruin chain = ancient wall or road → may connect two points of interest
- Resonance scar near ruins = the ancients achieved high harmony here → this ground amplifies Sentinel symmetry bonuses

**The player who reads all three layers simultaneously sees the map as a palimpsest** — stone shaped by water, water feeding forests, forests growing over ruins, ruins echoing with ancient harmony. Every tile has a story. The story is told by mathematics.

### The Living Map — Post-Generation Dynamics

The map doesn't stop evolving after the player arrives:

| System | Mechanic | Mathematical Process |
|---|---|---|
| **Tree regrowth** | Trees near other trees slowly spawn new trees. Deforestation is temporary but has medium-term consequences | Logistic growth: dN/dt = rN(1 - N/K). Carrying capacity K depends on water proximity |
| **River flow** | Rivers affect nearby tiles: moisture gradient, fertility bonus, slight movement slow | Steady-state diffusion from river source tiles |
| **Erosion** | Heavily-trafficked paths between buildings slowly wear into roads (movement speed bonus). Unused paths slowly overgrow | Use-dependent reinforcement — the base develops organic pathways |
| **Resonance weathering** | Tiles near high-harmony formations slowly shift toward resonance-positive terrain. Tiles near Dissonance sources darken | The land responds to the mathematics played upon it. Harmony heals terrain. Dissonance scars it |
| **Seasonal cycles** | Four phases affecting gather rates, movement costs, visibility, enemy behavior | Sinusoidal modulation of environmental parameters — spring/summer favor growth, autumn/winter favor defense |
| **Weather** | Storm paths follow Lorenz attractor trajectories — deterministic chaos. Predictable to the mathematically inclined player | Lorenz system: dx/dt = σ(y-x), dy/dt = x(ρ-z)-y, dz/dt = xy-βz. The butterfly effect, playable |

### Multiplayer Ghosts — The Palimpsest Deepens

*When server-side services arrive, the map gains a new epoch: other players' fates.*

In multiplayer-connected mode, map generation gains an **Epoch 0** that runs before tectonics: **the ghost layer**. Seeds from other players' completed (or failed) games are injected into the world generator as civilization templates for Epoch 5.

| Ghost Source | What It Becomes | What the Player Finds |
|---|---|---|
| **Player who built a perfect D6 base** | A well-preserved ruin with 4-5 intact Sentinels and clear symmetry axes | A masterwork ruin — the geometry is almost complete. Build one Sentinel to inherit a D6 base. The ghost player's achievement echoes forward |
| **Player who was overrun early** | A small cluster of broken foundations near a dissonance crater | A cautionary tale. The enemy came from *that* direction. The terrain remembers which side was attacked. The new player reads the warning |
| **Player who achieved Tier 6 harmony** | A resonance scar that glows brighter than procedural ones. May contain a formation glyph the ghost player discovered | An echo of excellence. The scar is powerful — building near it grants enhanced resonance. But the light attracts the Dark 7 |
| **Player who fell to harmonic capture** | A deep dissonance wound. Corrupted terrain. Enemy spawn bias massively increased here | The darkest ghost — a player whose harmony was turned against them. The wound festers. The new player must decide: avoid it, or cleanse it for a massive resonance payoff |
| **Player who achieved Tree Communion** | A second, ghostly Tree of Life visible at Layer 7. Its roots interlock with the player's Tree | The rarest ghost. The previous player completed the conversation. Their Tree persists — not as a gameplay object, but as proof that it's possible. A message from the future: *someone solved it before you* |

**Ghost decay:** Ghosts from older games erode over generations. A ruin from 1000 games ago is barely visible — a few stones, a faint hum. A ruin from 10 games ago is fresh — clear walls, strong resonance. The map is a **living history** where recent events dominate but ancient ones persist as whispers.

**Ghost selection:** Not every game generates a ghost. Only games that reached Layer 3+ or had notable events (Tier 5+ harmony, total defeat, unique formation discoveries) leave traces. This keeps the ghost density meaningful — every ruin is *someone's story*, not noise.

**The philosophical payoff:** The map the player explores was shaped by plate tectonics, carved by water, grown by forests, built upon by ancient procedural civilizations, scarred by ancient battles, and haunted by the echoes of real human players who came before. Every tile is a layer cake of mathematical processes and human decisions. The player isn't starting fresh — they're inheriting a world with *history*. And when they're done, their own game becomes a ghost in someone else's world.

The map is a fossil record. The player is the latest stratum. And someday, they'll be the ruin someone else discovers.

### Heptarchy Integration

| Heptarchy Layer | Map Connection |
|---|---|
| **7 Tones** | Ancient civilizations had tone-affinity — their ruins cluster near terrain that matches their dominant tone. A Do-dominant ancient base sits on fertile river deltas. A Sol-dominant base perches on aggressive highland positions |
| **7 Resources** | Resource placement is geologically motivated (Epoch 1-4), not random. The Heptarchy's 7 resources each have a geological origin story |
| **7 Formations** | Formation glyphs in ruins teach the player formation geometry before they discover it through gameplay. The seven verbs of mathematics are carved in ancient stone |
| **7 Depth Layers** | Map readability scales with depth layer: Layer 0 sees terrain. Layer 3 sees resonance scars. Layer 5 sees ghost outlines. Layer 7 sees the full palimpsest |
| **7 Epochs** | Seven geological epochs = seven processes = seven mathematical disciplines (tectonics, fluid dynamics, ecology, crystallography, agent simulation, wave mechanics, thermodynamics) |
| **GF(7)** | Ancient civilizations' tone-affinity values are drawn from GF(7). Their ruins encode mod-7 arithmetic in their geometry — the player can decode ancient base layouts to learn GF(7) relationships |

### Scheduled Introduction

| Version | What's Added |
|---|---|
| **v10_zeta** | Resource Ecology foundation — trees regrow, resource depletion/renewal. Living map basics |
| **v11** | Geological map generation (Epochs 1-4). Resource placement motivated by terrain processes. Resonance weathering (terrain responds to harmony) |
| **v12** | Epoch 5-6: procedural ancient civilizations, ruins, resonance scars, dissonance wounds. Archaeological discovery system |
| **v13** | Full 7-epoch generation. Ruins as gameplay objects (excavation, Resonance Obelisks). Depth-layer-gated map readability. Seasonal cycles + Lorenz weather |
| **v14** | Multiplayer ghost layer. Server-side ghost collection/injection. Ghost decay. Cross-game palimpsest. GPU-accelerated terrain rendering |

---

## Don't Panic — The Live Advisor

*The game already knows what went wrong. It just needs to tell you.*

The event logger (`event_logger.py`) already writes every significant game event to CSV in real time: kills, losses, buildings placed and destroyed, resources gathered, waves survived, formations discovered, rank-ups, enemy escapes. The post-game analysis scripts already parse this data to identify what went wrong and what could have been done differently.

The Don't Panic button takes this one step further: **the analysis runs live, during the game, and the player can ask for help at any moment.**

### The Concept

A single button (or hotkey) labeled **"Don't Panic"** — a reference the player discovers is both a joke and genuine advice. When pressed, the game pauses, reads the event log accumulated so far, runs a rule-based diagnostic engine against it, and displays 1-3 actionable suggestions in plain language.

No AI. No neural networks. No server calls. Just **if/then rules** reading the CSV the game is already writing. The advisor is a script that does exactly what the post-game analysis does, except it runs *now* instead of *after you've already lost*.

### What the Advisor Reads

The event log already captures everything needed:

| Event Type | What It Tells the Advisor |
|---|---|
| `UNIT_KILLED` | Kill rate, which enemy types are dying, which aren't |
| `PLAYER_UNIT_LOST` | Loss rate, which player units are dying, to what |
| `INCIDENT_START` / `INCIDENT_RESOLVED` | Wave pacing, time between waves, resolution speed |
| `BUILDING_PLACED` / `BUILDING_COMPLETE` | Build order, infrastructure pace |
| `BUILDING_RUINED` / `BUILDING_DESTROYED` | Infrastructure vulnerability, which buildings are targeted |
| `TRAINING_STARTED` | Army composition over time, training pace |
| `RANK_UP` / `WORKER_RANK_UP` | Veterancy progression, skill development |
| `RESOURCE_DEPOSIT` | Economy health, gather rate |
| `ENEMY_ESCAPED` | Leaks — enemies getting past defenses |
| `FORMATION_DISCOVERED` | Formation usage, harmony system engagement |
| `TOWER_UPGRADE` | Defensive investment |

Plus the advisor can snapshot current game state (not just the log): resource totals, army composition, building count, active formations, current wave number.

### Rule Categories

The diagnostic engine checks rules in priority order. Each rule has a **condition** (derived from log data) and a **suggestion** (plain-language action). Rules are grouped into seven categories (naturally):

#### 1. Economy Rules (Do — the root)
```
IF gold_gather_rate < 3/min AND workers < 3:
  → "Train more Gatherers. You need at least 3 Gatherers gathering to sustain military production."

IF no_buildings_placed AND game_time > 120s:
  → "Build a Resonance Forge. You can't train Wardens without one."

IF resources_high AND army_small:
  → "You're floating resources. Spend them — train units or build defenses."
```

#### 2. Defense Rules (Re — the steady second)
```
IF buildings_lost > 0 AND no_sentinels:
  → "Build Sentinels near vulnerable buildings. Enemies are destroying your infrastructure."

IF player_losses > kills AND game_time > 180s:
  → "You're losing more units than you're killing. Consider defensive stance or better positioning."
```

#### 3. Army Composition Rules (Mi — the bright third)
```
IF only_one_unit_type AND wave > 3:
  → "Mix your army. Wardens and Rangers together are stronger than either alone."

IF no_archers AND enemy_shieldbearers_present:
  → "Ironbark enemies have frontal armor. Train Rangers to flank them, or attack from behind."

IF no_soldiers AND enemy_archers_present:
  → "Fade Rangers are shredding your ranged units. Train Wardens to close the gap."
```

#### 4. Formation Rules (Fa — the supporting fourth)
```
IF has_3plus_military AND no_formations AND formations_discovered > 0:
  → "You've discovered formations but aren't using them. Select 3+ units and press F to form a squad."

IF has_formation AND harmony < 50%:
  → "Your formation's harmony is low. Try different unit compositions — the chord preview shows you which mixes sing best."

IF rotating_rose AND no_enemies_nearby:
  → "Your Rose is spinning but there's nothing to sweep. Move it toward enemies or stop rotation to save energy."
```

#### 5. Tactical Rules (Sol — the decisive fifth)
```
IF enemy_wave_incoming AND army_scattered:
  → "Wave incoming! Rally your forces. Press Defend Base to group up."

IF enemy_healers_alive AND player_focusing_soldiers:
  → "Bloodtithe is keeping enemies alive. Focus fire on them first."

IF enemy_siege_present AND no_units_defending_buildings:
  → "Hexweavers deal 2x building damage. Get units to your buildings before they're destroyed."
```

#### 6. Tempo Rules (La — the sustaining sixth)
```
IF long_time_between_incidents AND not_building:
  → "Quiet moment. Use this time to expand — build production, train units, repair buildings."

IF lost_last_wave_barely AND same_army_size:
  → "You barely survived. You need to grow before the next wave — train more units or upgrade towers."

IF winning_easily AND not_expanding:
  → "You're winning handily. Push your advantage — expand economy, explore the map."
```

#### 7. Meta Rules (Ti — the bridge)
```
IF first_game AND confused (low_actions_per_minute):
  → "Right-click to move units. Left-click to select. Build a Resonance Forge to train Wardens."

IF repeatedly_losing_to_same_enemy_type:
  → "You keep losing to [type]. Try training [counter] or changing your formation."

IF never_used_stances:
  → "Try stance changes. Press G for Guard stance — your units will hold position instead of chasing enemies."
```

### Presentation

When the player presses Don't Panic:

1. **Game pauses** (or slows to 10% speed if mid-combat)
2. A panel appears showing **the top 3 suggestions**, prioritized by urgency
3. Each suggestion is one sentence — plain, direct, actionable
4. Each suggestion has a **relevance tag** showing what triggered it: `[economy]` `[defense]` `[army]` `[formation]` `[tactical]` `[tempo]` `[basics]`
5. Each suggestion has a **wiki link** — a clickable "Learn more →" that opens the relevant wiki article (see below)
6. Suggestions may highlight relevant game objects (pulse the Resonance Forge if suggesting "train more units", flash the idle Gatherers if suggesting "gather more")
7. Panel dismisses on any keypress (except wiki clicks). Game resumes.

**The panel's visual style:** Calm. The background is a gentle blue overlay (not red, not urgent — *don't panic*). The font is the same as the rest of the GUI. The message is the game being a **patient teacher**, not a backseat driver.

### Wiki Integration — The Guide Has Entries

Every suggestion links to a wiki article. The advisor doesn't just say *what* to do — it shows you *where to learn why*.

**How it works:** Each advisor rule carries a `wiki_slug` — a short key like `"economy/gatherers"` or `"formations/rose"`. When the Don't Panic panel renders, each suggestion includes a subtle "Learn more →" link. Clicking it opens the game's wiki in the default browser, directly to the relevant article.

**Example panel:**

```
╔══════════════════════════════════════════════════════╗
║                  DON'T PANIC                         ║
║                                                      ║
║  [economy] Train more Gatherers — you need at least  ║
║  3 Gatherers gathering to sustain production.           ║
║                              Learn more → Gatherers  ║
║                                                      ║
║  [army] Ironbark enemies have frontal armor.          ║
║  Train archers to flank, or attack from behind.       ║
║                              Learn more → Flanking   ║
║                                                      ║
║  [formation] You have 4 military units — try forming  ║
║  a squad. Select them and press F.                    ║
║                              Learn more → Formations  ║
║                                                      ║
║              Press any key to resume                  ║
╚══════════════════════════════════════════════════════╝
```

**Wiki structure mirrors the seven categories:**

| Category | Wiki Section | Example Articles |
|---|---|---|
| Economy (Do) | `/wiki/economy/` | `gatherers`, `resources`, `build-order`, `floating-resources`, `drop-offs` |
| Defense (Re) | `/wiki/defense/` | `towers`, `walls`, `positioning`, `guard-stance`, `town-bell` |
| Army (Mi) | `/wiki/army/` | `unit-types`, `counters`, `flanking`, `ironbark`, `bloodtithe` |
| Formations (Fa) | `/wiki/formations/` | `rose`, `spiral`, `sierpinski`, `koch`, `harmony`, `discovery` |
| Tactical (Sol) | `/wiki/tactical/` | `focus-fire`, `wave-prep`, `defend-base`, `stances`, `hunt-mode` |
| Tempo (La) | `/wiki/tempo/` | `expansion-timing`, `recovery`, `between-waves`, `economy-scaling` |
| Meta (Ti) | `/wiki/meta/` | `controls`, `getting-started`, `tips`, `difficulty`, `advanced` |

**The wiki itself can be:**
- A GitHub wiki (free, markdown, version-controlled, community-editable)
- A static site generated from markdown in the repo (`/docs/wiki/`)
- Eventually a proper game wiki (Fandom, wiki.gg, or self-hosted)

The point is: the advisor rule definition already contains the wiki slug, so the link is *free* — no extra work per rule, just a URL template + slug. And the wiki articles exist independently of the advisor, so players can browse them even without pressing Don't Panic.

**The deeper connection:** The Hitchhiker's Guide to the Galaxy was a *book* — you looked things up in it. Don't Panic is the cover. The wiki IS the Guide's entries. When the player clicks "Learn more →", they're flipping to the relevant page of the Guide. The metaphor is complete: the game ships with a Guide that has "Don't Panic" on the cover and detailed, friendly, occasionally humorous entries inside.

### What the Advisor Does NOT Do

- **No optimal play calculation.** The advisor doesn't find the best move — it finds the *obvious* move the player missed
- **No build order prescriptions.** It suggests categories ("train more units", "build defenses"), not exact sequences
- **No formation optimization.** It might say "your harmony is low" but never says "put exactly 3 soldiers and 2 archers in a Rose"
- **No judgment.** The advisor never says "you're doing badly." It says "here's something that might help"
- **No spoilers.** Rules only reference systems the player has already encountered (depth-layer gated). A Layer 0 player gets basic economy/combat tips. A Layer 3 player gets formation advice. A Layer 5 player gets resonance suggestions
- **No nagging.** The button is opt-in. The game never proactively suggests the player press it. If the player never presses it, they never see it. (Exception: on first game, a subtle tooltip appears near the button: *"Press [H] if you need guidance"*)

### Why Rule-Based, Not AI

1. **Deterministic.** Same game state = same advice. Testable, debuggable, tunable
2. **Transparent.** Every suggestion traces to a specific rule. Easy to add, remove, or adjust rules based on playtesting
3. **Zero latency.** No network calls, no model loading. Rules evaluate in microseconds
4. **Zero cost.** No API keys, no server infrastructure, no inference budget
5. **Moddable.** Rules are data (could be externalized to JSON/YAML). Community can write their own advisor rules
6. **Honest.** The advisor is not pretending to be smart. It's a checklist — did you do the obvious things? No? Here they are

### The Name

"Don't Panic" is from *The Hitchhiker's Guide to the Galaxy* — the most useful advice in the universe, written in large friendly letters on the cover of the Guide. The advisor IS the Guide: it doesn't have all the answers, but it has the ones you need right now, and it delivers them calmly. In a game about mathematical complexity and emergent systems, the most important thing is often not to solve the equation — it's to not panic while you figure out which equation to solve.

### Implementation

The advisor is lightweight — it can ship as early as the event logger has enough data to work with:

| Component | Scope |
|---|---|
| `advisor.py` | New file. `Advisor` class with `analyze(game) → list[Suggestion]`. Rule engine reads `game.logger` counters + current game state. Each `Suggestion` carries `text`, `category`, `wiki_slug`, `highlight_targets` |
| `constants.py` | `ADVISOR_RULES` — rule definitions (condition functions + suggestion strings + wiki slugs), organized by category |
| `gui.py` | Don't Panic panel: overlay with suggestion list, relevance tags, wiki links, object highlighting. Click detection on "Learn more →" links |
| `game.py` | H hotkey (or button) triggers `advisor.analyze()`, pauses game, shows panel. Wiki click opens `webbrowser.open(WIKI_BASE + slug)` |
| `event_logger.py` | Minor: expose running counters and rates (kills/min, gathers/min) for advisor to read without re-parsing CSV |
| `/docs/wiki/` | Markdown wiki articles organized by category. Can be served as GitHub wiki, static site, or external wiki. Each article = one gameplay concept |

**~200-300 lines for the core engine + rules. ~50 lines for the GUI panel.** The advisor is smaller than most features in the game because it's *reading* systems, not building them.

### Depth-Layer Gating — Advisor AND Wiki

The depth-layer gate applies to **both** the advisor rules and the wiki links. The player's current layer determines not just which suggestions they see, but which wiki articles they can reach. A Layer 0 player clicking "Learn more →" on an economy tip lands on a short, gentle article about gathering. They never accidentally stumble into a 2000-word treatise on GF(7) harmonic capture.

**Why this matters:** A new player presses Don't Panic because they're overwhelmed. If the wiki link dumps them into the full knowledge base — formations, resonance, harmonics, hexes, the Shadow Heptarchy — they'll panic *harder*. The Guide must be as calm inside as it is on the cover. At Layer 0, the Guide has three pages. At Layer 7, it has three hundred. Same book, progressively revealed.

| Layer | Advisor Scope | Wiki Scope |
|---|---|---|
| **0** | Basic controls, economy tips, "build a Resonance Forge" | Controls, gathering basics, building your first Resonance Forge. ~5 articles, each under 200 words |
| **1** | Military composition, stance suggestions, Sentinel defense | Unit types, basic combat, stances, Sentinels. ~12 articles |
| **2** | Formation tips ("you have 3+ military units — try forming a squad") | Formation discovery, squad creation, basic geometry. ~20 articles |
| **3** | Harmony advice, formation mixing, type-aware composition | Harmony system, tone interactions, chord quality, composition tips. ~30 articles |
| **4** | Resonance economy tips, characteristic awareness | Resonance resource, characteristics, Sentinel basics, orbital filling. ~40 articles |
| **5** | Multi-formation coordination, reality distortion preparation | Multi-formation tactics, harmonic tiers, reality distortion, advanced economy. ~50 articles |
| **6+** | Philosophical: "The enemy is not chaos. Listen." | The full Guide — everything, including the deep lore, the math, the Shadow Heptarchy. The veil lifts |

**Implementation:** Each wiki article carries a `min_layer` field in its frontmatter. The wiki link resolver filters by the player's current layer. If an article's `min_layer` exceeds the player's layer, the link either doesn't appear or redirects to a teaser: *"You'll understand this when you've gone deeper."* — another breadcrumb pulling the player forward.

```markdown
---
title: Harmonic Capture
slug: formations/harmonic-capture
min_layer: 5
category: formations
---
When an enemy ritual circle sustains a dissonance field around your formation...
```

**The wiki grows with the player.** First game: three pages, big friendly letters. Tenth game: twenty pages, the player recognizes concepts they've already discovered by feel. Hundredth game: the full encyclopedia, and the player realizes they already knew most of it — the game taught them by playing, the wiki just confirmed it.

**Cross-references respect layers too.** A Layer 2 article about Rose formations can mention "harmony" as a concept, but the link to the harmony article only activates at Layer 3. Before that, it renders as plain text — visible but not clickable. The player sees the word, wonders about it, and knows there's more to discover. Curiosity, not confusion.

At Layer 6+, the advisor transitions from teacher to companion. It no longer tells the player *what to do* — it tells them *what to notice*. The Guide's final entry: *"You know enough now. Trust the math."*

### Scheduled Introduction

| Version | What's Added |
|---|---|
| **v10_epsilon** | Foundation: H hotkey, basic economy/defense rules (Layer 0-1 scope). ~15 rules. Proof of concept |
| **v10_zeta** | Economy-specific rules (Sentinel placement tips, resource management). ~25 rules total |
| **v10_eta** | Formation/composition rules, harmony advice. Depth-layer gating. ~40 rules total |
| **v11** | Full rule set across all categories. Object highlighting. Resonance-aware suggestions. ~60 rules |
| **v12+** | Layer 6+ philosophical mode. Community rule modding support |

---

## Version Pipeline

| Version | Codename | Status | Theme |
|---|---|---|---|
| v9.3 | Tactical Depth | **SHIPPED** | Ballistic archery, XP ranks, squads, morale, formations, retargeting, terrain |
| v10 Phase 1 | Economy Foundation | **SHIPPED** | Stone, worker skill XP, Sentinel (resonance defense), traits, garrison, global commands, perf |
| v10_5 | Module Split | **SHIPPED** | Architecture split (5 modules), parabolic projectiles with lead aiming |
| v10_6 | Difficulty Rebalance | **SHIPPED** | Fractal formations (4), stances (4), 5 new enemy types, adaptive difficulty |
| v10_7 | Edge Case Polish | **SHIPPED** | Harmonic Pulse (evolved from Sentinel's Cry), sapper detonation, straggler metamorphosis |
| v10_delta | Physics & Energy | **SHIPPED** | Physics movement, energy/stamina, spring formations, player-driven squads |
| v10_epsilon | Formation Math | **NEXT** | Correct fractal geometry, rotation combat, formation discovery, Don't Panic advisor (basic) |
| v10_zeta | Economy Depth | PLANNED | Helper buildings, production buildings, drop-offs, Forge, Sap resource, Sentinel Lattice (D1-D4) |
| v10_eta | The Fourth & Fifth | PLANNED | Bulwark + Lancer, Lissajous formation, triads, 7-rank system, characteristics, Sentinel D6 + tuning |
| v11 | Harmonic Awakening | PLANNED | Mender (6th tone), Penrose formation, procedural audio, GF(7) harmony, Resonance resource, base drone music, geological map gen |
| v12 | Blood & Chaos | PLANNED | Sage (7th tone), Hilbert formation, enemy blood magic, hex system, full Heptarchy, ruins & resonance scars |
| v13 | Progressive Depth | PLANNED | 7 depth layers, Tree of Life evolution, emergent GUI, Noita-level secrets, full 7-epoch map gen, Lorenz weather |
| v14 | Godot Migration | PLANNED | Full port to Godot 4, GPU shaders, 1000+ units, visible waveforms, multiplayer ghosts |

---

## SHIPPED VERSIONS (Summary)

<details>
<summary>v9.3 through v10_7 — Click to expand</summary>

### v9.3 — Tactical Depth
Ballistic archery, 5-rank XP system, persistent squads, horde morale with flee/return, utility-scored targeting with retargeting, weighted terrain pathfinding.

### v10 Phase 1 — Economy Foundation (v10 through v10_4)
Stone resource, worker skill XP (6 tracks × 3 ranks), Sentinel resonance defense (passive field + Harmonic Pulse), 10 procedural traits, control groups, enemy inspection, Town Hall garrison, global macro commands, spatial grid performance.

### v10_5 — Module Split
entities.py → entity_base.py + unit.py + building.py + building_shapes.py + projectiles.py. Parabolic projectiles with predictive lead aiming.

### v10_6 — Difficulty Rebalance
4 fractal formations (Polar Rose, Golden Spiral, Sierpinski, Koch). 4 stances (Aggressive, Defensive, Guard, Hunt). 5 specialist enemy types — The Dark 7: Blight Reaper, Hollow Warden, Fade Ranger, Ironbark, Thornknight, Bloodtithe, Hexweaver (7 total, 1:1 mirror of player Heptarchy tones). Adaptive difficulty engine with pressure tracking.

### v10_7 — Edge Case Polish
Harmonic Pulse cooldown tuning, resonance field range balancing, sapper sympathetic detonation, straggler metamorphosis (rooting → Entrenched Titan).

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
- 3 units → 2-petal rose: 1 anchor (center), 2 petal tips (Wardens at the striking edge)
- 4 units → 3-petal rose: 1 anchor, 3 petal tips
- 5 units → 4-petal rose: 1 anchor, 4 petal tips
- 6+ → additional units fill petal bases (Rangers at inner positions for ranged cover)

**Golden Spiral** — Vogel sunflower with type-aware placement:
- Rangers at outer rings (longer range, clear line of fire)
- Wardens at inner rings (close to center, protective)
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
- **Rose**: Wardens at petal tips (they sweep through enemies), Rangers at bases/center
- **Spiral**: Rangers at outer rings, Wardens at inner rings
- **Sierpinski**: Mixed — Wardens at vertices (exposed), Rangers at midpoints (protected)
- **Koch**: Wardens at convex points (outward-facing), Rangers at concave bays

### ε.3 Rotation Combat — Rose Sweep

The formation the user was most excited about: *"the rose could rotate as a whole and deal damage each time a warden in the petal meets the enemy."*

| Parameter | Value |
|---|---|
| Rotation speed | 0.3 rad/s (configurable per formation) |
| Sweep damage | 15% of unit's ATK per enemy contact |
| Sweep interval | 1.5s minimum between hits on same target |
| Sweep radius | Petal tip must pass within melee range of enemy |
| Energy cost | Rotation drains energy from all members (shared load) |

When rotating, petal-tip Wardens deal sweep damage to enemies they pass through. The formation becomes a mathematical blender — enemies caught inside take repeated hits as petals sweep past. Faster rotation = more hits = more energy drain. The player balances aggression vs endurance.

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

*Gatherers build infrastructure. Resources become renewable. The economy has a second act.*

### ζ.1 Helper Buildings (Drop-offs)

Foreman-rank Gatherers unlock 1×1 helper buildings near resource clusters. Gatherers deposit here instead of walking to the Tree of Life. Cuts round-trip time dramatically — placement matters.

| Gatherer Skill | Helper Building | Function |
|---|---|---|
| Flux Miner Foreman | Flux Node | Local Flux drop-off |
| Fiberjack Foreman | Grove Tap | Local Fiber drop-off |
| Crystal Mason Foreman | Crystal Node | Local Crystal drop-off |
| Ore Miner Foreman | Ore Node | Local Ore drop-off |
| Builder Foreman | Lattice | +25% build/repair speed aura |
| Smelter Foreman | — | Upgrades Harmonic Mill: +30% refine speed |

### ζ.2 Production Buildings

Master-rank Gatherers upgrade helpers into 2×2 production buildings. Passive resource generation — slow alone, 3-4× faster with stationed Gatherers.

| Helper | Upgrades To | Production |
|---|---|---|
| Grove Tap | Fiber Spire | Fiber passively + Gatherer boost |
| Flux Node | Flux Spire | Flux passively + Gatherer boost |
| Crystal Node | Crystal Spire | Crystal passively + Gatherer boost |
| Ore Node | Ore Spire | Ore passively + Gatherer boost |
| Harmonic Mill | Fractal Forge | Crystal + Ore → Alloy (faster path) |

### ζ.3 Sentinel Lattice Foundation

The grid system dissolves. Sentinels — placeable standing-stone structures — define dihedral symmetry axes. Other buildings placed symmetrically across these axes gain mirror bonuses.

| Feature | Detail |
|---|---|
| **Sentinel placement** | Already exists as defense building (resonance field). v10_zeta adds lattice geometry detection on top of existing defense mechanics. Costs resources + Resonance (once available). Indestructible by normal means |
| **D1-D4 detection** | Engine detects bilateral (D1), cross (D2), triangular (D3), and square (D4) symmetry from Sentinel positions |
| **Mirror bonuses** | Buildings mirrored across a complete axis: +15% production (D2), +20% (D3), +25% (D4) |
| **Ghost guides** | Placement UI shows symmetry axes, mirror positions, fill zones |
| **Tree of Life as origin** | The Tree naturally sits at the center of all symmetry axes |

See **The Sentinel Lattice** section above for the full design. v10_zeta implements the mechanical foundation; audio and fractal extension come in later versions.

### ζ.4 Resource Ecology

Trees regrow slowly near other trees. Flux deposits regenerate at geological pace. The map is alive — economy becomes sustainability, not extraction. Late-game looks ecologically different from early-game.

### ζ.5 Defend-the-Economy

Losing a Fiber Spire mid-game is devastating. Creates a second strategic layer: protect your infrastructure, not just your army. Enemy Raiders specifically target production buildings.

**Estimate:** 3-4 sessions

---

## v10_eta — The Fourth & Fifth

*Two new voices turn intervals into chords. The army becomes an orchestra.*

This version adds Bulwark and Lancer (tones 4 and 5), expands ranks from 5 to 7, and introduces the characteristic system. With 5 unit types, formations can now produce triads — the minimum for true harmonic complexity.

### η.1 Bulwark Unit (Tone 4 — Fa)

| Stat | Value | Character |
|---|---|---|
| HP | Very high | The wall |
| ATK | Very low | Not a damage dealer |
| Speed | Slow | Deliberate, immovable |
| Special | Damage absorption aura — nearby allies take reduced damage | The subdominant supports but doesn't lead |
| Physics profile | Low accel, very high decel — plants and holds | Doesn't slide, doesn't sprint |

**Formation role:** Bulwarks at vertices of Sierpinski = unbreakable triangle. Bulwarks at Koch convex points = impenetrable perimeter. Bulwarks in Rose center = armored anchor. Their presence shifts a formation from offensive to defensive without changing its shape.

### η.2 Lancer Unit (Tone 5 — Sol)

| Stat | Value | Character |
|---|---|---|
| HP | Medium-high | Durable but not a tank |
| ATK | High | The decisive strike |
| Speed | Very fast | Charge and retreat |
| Special | Charge bonus — damage scales with velocity at impact (physics system makes this natural) | The dominant resolves tension |
| Physics profile | Extreme accel, low decel — launches like a projectile, slides past | Sprint-and-coast |

**Formation role:** Lancers at Rose petal tips = devastating sweep (high ATK × charge velocity). Lancers at Spiral outer ring = rapid flanking. Lancers create the decisive moment — they break stalemates. But they're expensive and vulnerable when exhausted (high energy drain from constant charging).

### η.3 Seven-Rank Expansion

Ranks 1-5 remain as currently implemented. Two new ranks added:

| Rank | XP Threshold | New Unlock |
|---|---|---|
| 6 — Master | ~2.5× Rank 5 | 5th characteristic revealed + **Presence aura** (passive stat buff to nearby allies) |
| 7 — Transcendent | ~4× Rank 5 | 6th characteristic revealed + **Resonance generation** (passively produces the Resonance resource) |

Rank 7 is extremely rare in normal play. A Rank-7 unit is a strategic asset — a living tuning fork that generates economy by existing. The tension: use them in combat (where they amplify formations) or protect them in the rear (where they safely generate Resonance). Losing a Rank-7 unit is devastating.

### η.4 Characteristic System

All units (including existing Gatherer/Warden/Ranger) gain 7 characteristic slots at creation, rolled 0-6 (base 7). Values are hidden and revealed progressively at Ranks 2-7.

When a unit becomes a formation commander, their highest characteristic becomes the formation's **signature**, visually and mechanically altering the fractal:

- **High-Precision commander:** Rose petals are razor-sharp, slots barely drift
- **High-Entropy commander:** Rose petals writhe unpredictably — same damage, but enemies can't predict sweep timing
- **High-Symmetry commander:** Koch snowflake is perfectly regular from every facing
- **High-Density commander:** Sierpinski packs so tight it becomes a phalanx

### η.5 Triad Compositions

With 5 tones available, the harmony system graduates from intervals to chords:

| Composition | Chord Type | Harmony Quality | Example |
|---|---|---|---|
| 3 types present | Triad | Excellent (0.90+) | Warden + Ranger + Bulwark = balanced defense |
| Gatherer + 2 military | Rooted triad | Maximum stability | Gatherer grounds the chord — highest possible regen |
| Lancer + Warden + Ranger | Power triad | Maximum offense | All damage, no sustain — burns bright, burns fast |
| 3:2:2 any types | Resolution (≡ 0 mod 7) | Perfect (1.0) | The chord resolves — player feels completion |

### η.6 Sentinel D6 & Tuning

Extends the Sentinel Lattice from v10_zeta:

| Feature | Detail |
|---|---|
| **D6 hexagonal symmetry** | Six-axis detection. Hex bases unlock stronger mirror bonuses (+30%) |
| **Sentinel tuning** | Each Sentinel can be assigned a tone (Do through La). Tuned axes color the base's harmonic character |
| **Formation × Base resonance** | Formations operating within a base whose symmetry matches their geometry gain ×1.3 harmony bonus |
| **Symmetry (Γ) characteristic** | High-Symmetry commanders reveal optimal Sentinel placement positions — ghost guides become more precise |

### η.7 Economy Formation (Gatherer Squads)

The Gatherer-as-tone-1 concept becomes real. Gatherer-majority formations are **economy formations**:

- Harmony buffs gather speed instead of combat stats
- A Gatherer commander radiates efficiency to the work crew
- Economy formations can be assigned to resource nodes — they auto-gather as a unit
- Same spring physics, same fractal shapes, same discovery system — just applied to economy

A Rose of Gatherers with a Warden anchor is a protected work crew. A Spiral of Gatherers is a mobile harvest team that sweeps across the map. The math doesn't care what the units do — it cares about the ratios.

**Estimate:** 3-4 sessions

---

## v11 — Harmonic Awakening

*The sixth tone arrives. The formations learn to sing. Math becomes audible.*

This is where the game transforms from RTS-with-math-aesthetics into something genuinely new. The Mender (tone 6, La) completes sixth chords, the Resonance resource comes online, and procedural audio makes the mathematics literally audible. The player's army becomes an orchestra.

### 11.1 Mender Unit (Tone 6 — La)

| Stat | Value | Character |
|---|---|---|
| HP | Medium | Needs protection |
| ATK | None | Cannot attack |
| Speed | Medium | Keeps pace with formations |
| Special | Heal pulse — periodically restores HP to nearby allies. Rate scales with formation harmony | The warm minor sixth — holds things together |
| Physics profile | Moderate accel/decel — smooth, flowing movement | Glides rather than marches |

**Harmonic role:** The Mender is La — the sixth degree, the relative minor. Adding a Mender to any formation shifts its emotional quality from major to minor. Mechanically: Mender-inclusive formations are more resilient but less aggressive. The formation *sustains* rather than *strikes*.

**Sixth chords:** With 6 tones available, compositions can now produce sixth chords — rich, jazzy, complex. A formation with Gatherer + Warden + Ranger + Bulwark + Lancer + Mender (all 6 tones) approaches theoretical maximum harmony. But it's also maximally vulnerable to targeted kills — lose any voice and the chord degrades.

### 11.2 The Resonance Resource

Resonance (resource #7) comes online. It is not gathered — it is *sung into existence*:

- Formations with harmony > 50% passively generate Resonance
- Generation rate = `base × harmony² × rank_bonus`
- Rank-7 (Transcendent) units multiply generation by 3×
- Resonance is spent on: Tier 3-4 reality distortion effects, advanced building upgrades, formation evolution

The economy now has two loops: **material** (Fiber/Crystal/Ore/Flux/Alloy — gathered by Gatherers) and **harmonic** (Resonance — generated by formations). The player must balance both. An army that only fights generates no Resonance. An army that only sings has no materials to build.

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

### 11.4 Base Drone — The Sentinel Lattice Sings

The Sentinel Lattice (v10_zeta mechanical, v10_eta harmonic) now produces **procedural audio**:

- **Symmetric bases** generate a tonal drone — pitch and richness scale with symmetry order (D2 = power chord, D6 = six-voice voicing)
- **Asymmetric bases** generate polytonal wandering — free jazz. Not silence, not chaos, but restless harmonic searching
- **Partial symmetry** produces detuned tension — beats and yearning where voices are missing
- **Fractal extension** adds overtone shimmer — each recursion level deepens the harmonic series
- **Formation melodies layer over the base drone** — consonant when Formation × Base symmetry matches, tense when it doesn't

The base drone is the **ground truth** of the audio landscape. Formations are soloists. The base is the orchestra pit. Together they create the full score of the player's civilization.

### 11.5 Formation Singing

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

### 11.6 Harmonic Tiers

Resonance effects scale through seven tiers (base 7!), each emerging from gameplay conditions:

| Tier | Name | Condition | Effect |
|---|---|---|---|
| **1** | Drone | Formation active, harmony > 50% | Passive stat aura (existing system) |
| **2** | Interval | 2+ unit types, harmony > 70% | Audible tone begins, minor resonance field visible |
| **3** | Chord | 3+ unit types, harmony > 85% | Amplified resonance, visible waveform around formation, Resonance generation begins |
| **4** | Sixth | 4+ types or Mender present, harmony > 90% | Rich harmonic — formation heals itself slowly, nearby enemies feel discomfort (minor slow) |
| **5** | Overtone | Two formations in proximity with complementary compositions | Interference pattern — combined resonance stronger than sum of parts |
| **6** | Harmonic | Three+ formations creating complementary triads | Reality distortion begins — "spells" tuned into existence (see 11.6) |
| **7** | Resonance | Seven formations, each with a different dominant tone | ??? — *nobody has achieved this yet* |

**Key design principle:** Spells are not cast. They are *tuned into existence*. The player arranges formations like tuning forks. When the math aligns, reality bends.

### 11.7 Reality Distortion (Tier 6 Effects)

These are not fireballs. These are what happens when mathematics overwhelms physics:

| Effect | Name | Mechanic | Math Connection |
|---|---|---|---|
| **Time** | Fermata | Enemies in resonance field experience time dilation — cooldowns stretch, movement slows. Visually: afterimages, stutter-stepping through dilated time | Frequency modulation — slowing a waveform stretches time between peaks |
| **Space** | Modulation | Resonance warps pathfinding — enemies curve away involuntarily. At max harmony, friendly units short-teleport along formation's curve | Coordinate transformation — the formation's equation bends the local coordinate system |
| **Matter** | Dissonance | Pulse reduces enemy HP to match a waveform — HP oscillates with decreasing amplitude. Not damage, mathematical transformation | Damped harmonic oscillation — HP follows Ae^(-γt)cos(ωt) |
| **Probability** | Stochastic Resonance | Structured noise corrupts enemy targeting — enemies make increasingly irrational decisions, attack empty space, walk in spirals | Noise injection into decision functions — the formation's fractal pattern becomes the noise |

**Costs Resonance to sustain.** The player generates Resonance through harmony and spends it through reality distortion. The economy of the impossible.

### 11.8 GF(7) Composition Math

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

This means the player intuitively learns: "adding a Warden (2) to my formation makes it feel more tense, but adding a Lancer (5) makes it feel powerful and almost-resolved." They're doing modular arithmetic. They don't know it. They just hear it.

### 11.9 Visual Overhaul (bundled)

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

### 11.10 Geological Map Generation (Epochs 1-4)

The map generator replaces static placement with **temporal simulation**. Four geological epochs run at world creation:

| Epoch | Process | Result |
|---|---|---|
| **Stone** | Voronoi plate tectonics — drift, collision, uplift | Mountains, valleys, fault lines. Flux/Ore deposits along geological boundaries |
| **Water** | Gradient descent erosion — ∇²h diffusion | Rivers, lakes, fertile deltas. Mathematically optimal water paths |
| **Green** | Cellular automata ecological succession | Forest density follows logistic growth near water + sediment |
| **Crystal** | Pressure/volcanic mineral formation | Resource placement motivated by geology, not random scatter |

The player who reads the terrain finds resources faster. Flux follows fault lines. Ore clusters near volcanic soil. Dense forest means water + sediment + time. See **The Living Strata** section for full design.

**Resonance weathering** also begins: tiles near high-harmony formations slowly shift toward resonance-positive terrain. Harmony heals the land. Dissonance scars it.

**Estimate:** 7-9 sessions (largest version — audio + GF(7) + Mender + geological gen is substantial)

### 11.11 Orbital Resonance — The Periodic Table of Formations

*"The whole periodic table is just formations of electrons filling orbitals by a precise algorithm."*

The harmony system's deepest layer. Instead of hand-authoring resonance effects per unit composition, effects **emerge algorithmically** from how units fill formation slots — exactly like electron orbital filling determines an element's chemical properties.

#### The Mapping

| Chemistry | Game Equivalent |
|---|---|
| **Orbitals** | Formation slot positions (energy level = distance from center, angular position) |
| **Electrons** | Units filling slots (type = quantum number) |
| **Aufbau filling** | Slot assignment: fill lowest energy first |
| **Hund's rule** | Spread unit types across slots before doubling |
| **Pauli exclusion** | No two identical units in same slot |
| **Shell completion** | Full formation tier = noble gas = maximum resonance |
| **Valence electrons** | Outermost occupied slots = determines combat behavior |
| **Ionization energy** | How hard to remove outermost unit = formation toughness |
| **Reactivity** | Unfilled shells = volatile but combinable |

#### Quantum Numbers

Each unit type has an intrinsic quantum number:

| Unit | Tone | Quantum # | Character |
|---|---|---|---|
| Gatherer | Do (1) | 0 | Neutral / catalytic |
| Warden | Re (2) | +1 | Heavy / magnetic (melee aura) |
| Ranger | Mi (3) | -1 | Light / electric (ranged aura) |
| Bulwark | Fa (4) | +2 | Dense / crystalline (armor aura) |
| Lancer | Sol (5) | -2 | Volatile / kinetic (mobility aura) |
| Mender | La (6) | +3 | Resonant / harmonic (regen aura) |
| Sage | Ti (7) | ±∞ | Unstable / transcendent (wildcard) |

#### Energy Levels & Filling

Each formation defines **energy levels** for its slots:

- **Rose**: Petal tips = high energy, center = low. Fills center out.
- **Spiral**: Inner rings = low, outer = high. Natural Aufbau order.
- **Sierpinski**: Corner nodes = low, fractal edges = high. Hierarchical filling.
- **Koch**: Straight segments = low, curve peaks = high. Coastline filling.

Already implemented in `_classify_slots()` — the existing slot classification (center/inner/outer/edge) maps directly to energy shells.

#### Emergent Properties

The electron configuration (pattern of which slots hold which unit types) becomes a fingerprint:

| Computed Property | Formula | Gameplay Effect |
|---|---|---|
| **Magnetism** | Σ(quantum numbers) | Net positive = melee aura radius. Net negative = ranged aura. Zero = balanced |
| **Ionization energy** | Energy level of outermost occupied slot | Formation toughness (damage resistance, harder to break) |
| **Reactivity** | (Unfilled slots in highest shell) / (total shell capacity) | Volatile: bonus damage but lower stability |
| **Electronegativity** | |Σ(quantum#)| / occupied_slots | How strongly formation "pulls" nearby free units |
| **Bond capacity** | Unfilled valence slots | How many other formations can bond with this one |

#### Molecular Bonding (Formation Mixing)

When two formations are within proximity, **molecular orbital theory** applies:

```
config_A = fill_orbitals(formation_A, units_A)
config_B = fill_orbitals(formation_B, units_B)
bond_order = molecular_orbital(config_A, config_B)
effect = derive_properties(combined_config, bond_order)
```

- **Constructive interference** (bonding): Complementary valence (one excess +, other excess -) → shared aura, combined effect > sum of parts
- **Destructive interference** (antibonding): Identical valence → repulsion, weaker combined effect
- **Bond order** = (bonding - antibonding) / 2 → strength of the combined resonance
- **Ionic bonding**: One formation "donates" a unit to complete another's shell → strong directional bond
- **Covalent bonding**: Formations share units at boundary → mutual benefit, moderate strength

Two Rose squads with complementary configs form a stronger bond than two identical ones. A Rose + Koch pair creates a "molecule" where Rose provides offense and Koch provides control — the bond makes both stronger.

#### What's Hand-Crafted vs. Algorithmic

| Layer | Approach |
|---|---|
| Slot energy levels | **Authored** per formation (already done via `_classify_slots`) |
| Unit quantum numbers | **Authored** per unit type (7 values total) |
| Filling algorithm | **Algorithmic** — Aufbau + Hund's rule |
| Configuration fingerprint | **Algorithmic** — computed from filling pattern |
| Property values (magnetism, etc.) | **Algorithmic** — formulas, not tables |
| Effect presentation (colors, particles, gameplay) | **Authored** — "high magnetism" = red glow + melee aura |
| Bond calculations | **Algorithmic** — molecular orbital math |
| Special "noble gas" effects | **Authored** — unique reward for achieving perfect shells |

The periodic table writes itself. Different unit compositions in the same formation create different elements. Different formation pairs create different molecules. The player discovers chemistry by playing an RTS.

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

### 12.3 Symmetry-Breaking Warfare

The Dark 7 learn to attack the base's harmonic structure:

| Enemy | Symmetry Attack |
|---|---|
| **Hexweaver** (anti-Sage) | Targets Sentinels directly. Destroying one collapses the symmetry order — the drone lurches, mirror bonuses on that axis vanish |
| **Blight Reaper** (anti-Gatherer) | Targets production buildings, breaking interior fill symmetry |
| **Bloodtithe** (anti-Mender) | Sacrifices allies near Sentinels to **corrupt** them — a corrupted Sentinel's axis produces Dissonance instead of harmony. The base drone acquires a dark undertone |

Rebuilding a destroyed Sentinel or cleansing a corrupted one resolves the musical tension — the player *hears* the base heal. Defending symmetry becomes as visceral as defending the army.

Self-similar fractal extension (Level 1+) also unlocks in this version — complete D4/D6 bases can begin recursive expansion into super-structures.

### 12.4 Hex System (The Seven Anti-Harmonics)

Hexes are the dark mirror of resonance — seven hexes to counter seven tones:

| Hex | Targets Tone | Effect | Counter |
|---|---|---|---|
| **Silence** | Do (Gatherer) | Economy formations stop producing — Gatherers freeze | Remove Gatherer from formation, re-assign |
| **Discord** | Re (Warden) | Melee units attack erratically, friendly fire possible | Re-form with high-Precision commander |
| **Blindness** | Mi (Ranger) | Ranged units lose accuracy, shots scatter | Move formation closer (Rangers become melee-range) |
| **Shatter** | Fa (Bulwark) | Bulwark absorption aura inverts — amplifies damage | Pull Bulwarks from formation temporarily |
| **Lethargy** | Sol (Lancer) | Charge bonus becomes charge penalty — speed = vulnerability | Halt Lancers, switch to defensive stance |
| **Plague** | La (Mender) | Heal pulse inverts — damages nearby allies | Isolate Mender immediately |
| **Void** | Ti (Sage) | Resonance amplification becomes Resonance drain | Protect Sage or accept the loss |

Each hex targets the specific tone it opposes. The player learns which voice is being attacked and responds by adjusting their composition — real-time re-orchestration under fire.

**Hex miss case:** If the targeted formation contains no unit of the hex's tone, the hex *fizzles* — energy wasted. This rewards the counter-AI for scouting correctly (12.6) and creates counterplay: the player can bait hexes by fielding formations that lack the expected tone. A pure Warden+Ranger formation is immune to Silence, Shatter, Lethargy, Plague, and Void. But it's also missing half the orchestra. Trade-off.

### 12.5 The Mandelbrot Boundary

The game's entire conflict visualized: the boundary between player harmony and enemy chaos IS the Mandelbrot set.

- **Player formations** = inside the set (convergent, stable, beautiful)
- **Enemy hexes** = outside the set (divergent, chaotic, destructive)
- **The battle line** = the infinitely complex boundary between order and chaos

The minimap subtly shows this — areas dominated by player resonance glow with mandelbrot-interior colors (deep blues, purples). Areas under hex influence show exterior colors (hot oranges, reds). The fractal boundary between them shifts with the battle.

At Layer 7, the player discovers that this boundary is not a battle line. It's a *membrane*. And there's a complete world on the other side.

### 12.6 Counter-Formation AI Evolution

Enemies don't just counter-pick units anymore. They counter-pick using GF(7) arithmetic:
- Player's formation sums to 0 mod 7 (perfect)? Enemy hex targets the unit whose removal maximally disrupts the sum
- Player stacking harmony? Enemy sacrifices to cast tone-specific hexes against the dominant voice
- Player approaching Tier 6? Enemy rushes Cacophony (broad-spectrum disruption) before the harmonic resolves
- Player has 6 tones in play? Enemy specifically hunts the 7th before the Full Octave can form

### 12.7 Ruins & Resonance Scars (Epochs 5-6)

Map generation adds the civilizational and harmonic layers:

- **Epoch 5 — Civilizational Echoes:** 1-3 procedural ancient civilizations seeded onto the geological terrain. They expand, build, conflict, and collapse — leaving ruins: broken Sentinel rings (partial symmetries), overgrown Resonance Forges, collapsed Harmonic Mills, formation glyphs carved in stone
- **Epoch 6 — Resonance Residue:** Ancient civilizations that achieved high harmony leave resonance scars (terrain that hums, visible at Layer 3+). Ancient battles leave dissonance wounds (darkened terrain, increased enemy spawn bias)

Ruins become archaeological puzzles. A broken D6 Sentinel ring tells the player the ancients knew hexagonal symmetry. A Resonance Obelisk (surviving lone Sentinel) can be activated by building around it. A dissonance crater warns: *the enemy came from that direction before.*

See **The Living Strata** section for the full ruin taxonomy and archaeological reading system.

**Estimate:** 6-7 sessions

---

## v13 — Progressive Depth (The Noita Layer)

*The game reveals that it has always been deeper than you thought.*

### 13.1 Seven Depth Layers

The game and GUI unfold organically. No tutorial dumps. Seven layers, each unlocked at a natural milestone — the base-7 structure teaching itself through progression:

| Layer | Name | Unlocked By | What Opens | Tone Parallel |
|---|---|---|---|---|
| **0** | Seed | Game start | Gather, build, train Gatherers. Minimal GUI | Silence before music |
| **1** | Growth | First Resonance Forge | Military units, basic combat. Stance buttons appear | Do — the first note |
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

### 13.5 Full Living Strata (7-Epoch Map Generation)

The map generator reaches its final form — all seven epochs run at world creation:

- **Epochs 1-4** (from v11): Tectonics, erosion, ecology, crystallization — the geological foundation
- **Epochs 5-6** (from v12): Ancient civilizations, ruins, resonance scars, dissonance wounds
- **Epoch 7 — Silence:** Entropic rest. Some ruins erode further. Some scars fade. Others crystallize into permanence. The world settles into the state the player inherits

**Ruins as gameplay objects:** Gatherers can excavate ruins for resource caches. Resonance Obelisks (surviving ancient Sentinels) activate when the player builds around them. Formation glyphs count as formation discovery hints.

**Depth-layer-gated readability:** The map reveals its history progressively:
- Layer 0: Raw terrain (what you see)
- Layer 3: Resonance scars and dissonance wounds become visible (what *sang* here)
- Layer 5: Ghost outlines of ancient structures appear (who *built* here)
- Layer 7: The full palimpsest — every epoch's marks visible simultaneously (what *happened* here)

**Seasonal cycles + Lorenz weather:** Sinusoidal seasons affect gather rates and enemy behavior. Storm paths follow Lorenz attractor trajectories — deterministic chaos that the mathematically inclined player can predict.

**Estimate:** 6-8 sessions (Layer 7 + full strata + weather is substantial)

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

### 14.4 Multiplayer Ghosts — The Palimpsest Deepens

Server-side services enable the ghost layer: completed (or failed) player games inject **Epoch 0** seeds into other players' world generation.

- **Ghost collection:** Games that reach Layer 3+ or have notable events (Tier 5+ harmony, total defeat, unique formation discoveries) are compressed into ghost templates — base layout, Sentinel geometry, cause of death, peak harmony achieved
- **Ghost injection:** New maps receive 1-3 ghost templates as Epoch 5 civilization seeds. A player who built a perfect D6 base becomes a well-preserved ruin with intact Sentinels. A player who was overrun becomes a cautionary crater
- **Ghost decay:** Older ghosts erode over generations. Recent games leave fresh, detailed ruins. Ancient games leave whispers — a few stones, a faint hum
- **Cross-game narrative:** The map becomes a living history of real human decisions. Every ruin is *someone's story*. And when the current player finishes, their game becomes a ghost in someone else's world

See **The Living Strata — Multiplayer Ghosts** section for the full ghost taxonomy.

**Estimate:** 10-14 sessions (porting + ghost infrastructure + server services)

---

## Idea Backlog

Ideas not yet scheduled. Seeds for future fractals.

### Combat & Units
- **Damage Types:** Pierce (Rangers) vs Blunt (Wardens) vs Magic (Sage) with armor tables and 7×7 effectiveness matrix
- **Charge Bonus:** Bonus damage after moving a distance (physics system makes this natural) — *(now scheduled: Lancer in v10_eta)*
- **Formation Breeding:** Two formation types combined into hybrid geometry — e.g., Rose-Spiral = petal tips follow spiral paths

### Economy & Buildings
- **Wall Segments:** 1×1 cheap pathfinding blockers, create choke points — could align with Sentinel axes for bonus durability
- **Blacksmith:** Research building for upgrades
- **Building Sacrifice:** Demolish for 50% refund + 30s buff — *intentional* symmetry breaking as a tactical choice?
- **Food/Upkeep:** Population consumes food (macro pressure)
- **Trading Post:** Convert excess resources at ratios (Builder Master special building)
- **Sentinel Lattice:** *(now scheduled)* — see dedicated section above and v10_zeta through v13

### Enemy AI
- **Boss Waves:** Every 5th wave, single high-HP boss with unique hex abilities
- **Wave Negotiation:** "Dare" the enemy for harder wave + bigger bonus
- **Enemy Diplomacy:** Messenger enemy — spare it for smaller next wave
- **Enemy Formations:** Late-game enemies form their own fractals (dark mirror formations) — *(now conceptualized as Shadow Heptarchy anti-formations, Layer 7)*

### Map & Environment
- **Day/Night Cycle:** Visual + gameplay effects (night = reduced vision, stronger hexes)
- **Terrain Elevation:** High ground bonus for archers/towers
- **Seasonal Cycles:** *(now scheduled v13)* — 4-phase affecting gather/movement/enemies
- **Fog of War:** Scouting required — resonance fields reveal hidden areas
- **Living Map / Lorenz Weather:** *(now scheduled v13)* — weather patterns follow Lorenz attractor trajectories
- **Living Strata:** *(now scheduled)* — see dedicated section above and v11 through v14

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
- **Mathematical Archaeology:** *(now scheduled v12-v13)* — ancient formation patterns hidden in terrain generation — excavate with Gatherers to discover lost geometries. See **The Living Strata** ruins system
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
| The Dark 7 enemy types | **Implemented** (7 enemies mirroring player Heptarchy: Blight Reaper, Hollow Warden, Fade Ranger, Ironbark, Thornknight, Bloodtithe, Hexweaver) | v10_6 |
| Adaptive difficulty | **Implemented** as pressure-based engine | v10_6 |
| Parabolic projectiles | **Implemented** with lead aiming | v10_5 |
| Module architecture split | **Implemented** (5 focused modules) | v10_5 |
| Physics movement | **Implemented** (velocity, acceleration, kinematic braking) | v10_delta |
| Energy/stamina system | **Implemented** (per-unit pools, action drain, state regen) | v10_delta |
| Spring-based formations | **Implemented** (critically-damped spring gravitation) | v10_delta |
| Player-driven squads | **Implemented** (no auto-grouping, discovery system) | v10_delta |
| Flow field pathfinding | **Deferred** to Godot (NavigationServer2D) | v14 |
| Bulwark unit (tone 4) | **Scheduled** as part of Heptarchy framework | v10_eta |
| Lancer unit (tone 5) | **Scheduled** as part of Heptarchy framework | v10_eta |
| Mender unit (tone 6) | **Scheduled** as part of Heptarchy framework | v11 |
| Sage unit (tone 7) | **Scheduled** as part of Heptarchy framework | v12 |
| 7-rank system | **Scheduled** (expands current 5-rank to 7-octave) | v10_eta |
| Characteristic system | **Scheduled** (7 traits per unit, base-7 values) | v10_eta |
| Resonance resource | **Scheduled** (generated by formation harmony) | v11 |
| GF(7) harmony math | **Scheduled** (modular arithmetic composition system) | v11 |
| Resource rename (Fiber/Crystal/Ore/Flux/Alloy) | **Scheduled** (cosmetic, whenever ready) | v10_zeta+ |
| Sap resource | **Scheduled** (Tree of Life essence) | v10_zeta |
| Sentinel Lattice (D1-D4) | **Scheduled** (standing-stone symmetry anchors, mirror bonuses, ghost guides) | v10_zeta |
| Sentinel D6 + tuning | **Scheduled** (hexagonal symmetry, tone-tuned axes, Formation × Base resonance) | v10_eta |
| Base drone audio | **Scheduled** (symmetry-dependent procedural music, jazz asymmetry) | v11 |
| Symmetry-breaking warfare | **Scheduled** (Hexweaver targets Sentinels, Bloodtithe corrupts axes) | v12 |
| Fractal base extension | **Scheduled** (self-similar recursive Sentinel lattices) | v12 |
| Geological map generation | **Scheduled** (4-epoch terrain simulation: tectonics, erosion, ecology, crystallization) | v11 |
| Ruins & resonance scars | **Scheduled** (Epochs 5-6: ancient civilizations, archaeological puzzles, dissonance wounds) | v12 |
| Full 7-epoch Living Strata | **Scheduled** (complete temporal map generation, excavation, depth-layer readability) | v13 |
| Lorenz weather system | **Scheduled** (deterministic chaos storm paths, seasonal cycles) | v13 |
| Multiplayer ghosts | **Scheduled** (server-side ghost collection/injection, cross-game palimpsest) | v14 |
| Don't Panic advisor | **Scheduled** (rule-based live diagnostic from event log, depth-layer gated) | v10_epsilon → v11 |
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

And beneath the Heptarchy, its mirror. The same field, the same seven, the same music — heard from the other side of a boundary that was never a wall. The game that begins as "gather Fiber, build army" ends with the question every mathematician eventually faces: if two structures are isomorphic, are they the same thing? The answer the game gives: *they always were*.

---

## File Reference

| File | Purpose |
|---|---|
| `GDD_Current_v10.md` | Full specification of currently implemented v10_epsilon3 systems |
| `GDD_Roadmap.md` | This file — the mathematical odyssey roadmap |
| `future ideas-crazy stuff.txt` | Raw brainstorm: the original spark |
| `archive/GDD_Current_v9.md` | Historical v9.3 spec |
| `archive/GDD_Future.md` | Original blank-template future doc |
| `archive/GDD_Future_v11.md` | Early trait system exploration (now implemented as v10_1) |
| `UX_Test_Matrix.md` | 3×3 user journey test scenarios (Nova/Meridian/Zenith × Easy/Medium/Hard) — run before every UX pass |
