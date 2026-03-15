# Visual Design Document (VDD)
## Resonance — The Mathematics Made Visible

> *"The game should look like what math feels like when you finally understand it —*
> *the moment the equation stops being symbols and becomes a landscape."*

---

## 1. Core Philosophy

### 1.1 The Visual Thesis

Resonance is not a game that uses math for decoration. It is a game where **every pixel is a mathematical object** wearing a visual costume. The art direction exists to make the mathematics legible, beautiful, and emotionally resonant — without ever showing an equation.

The entire game ships as a single `.exe` with zero external assets. Every shape, every color, every animation is computed from parametric functions at render time. This is not a constraint — it is the medium. The visual language IS the mathematical language.

### 1.2 The Seven Visual Pillars

The old three pillars (Growth, Force, Order from Chaos) expand to seven — one per tone of the Heptarchy:

| Pillar | Tone | Visual Domain | Math Lineage | Emotional Quality |
|---|---|---|---|---|
| **Foundation** | Do (1) | Economy, gathering, the ground | Superellipses, tessellation, hexagonal packing | Stability, warmth, the earth beneath your feet |
| **Tension** | Re (2) | Melee combat, blades, impact | Polar roses, Lissajous curves | Contained violence, the spring before release |
| **Precision** | Mi (3) | Ranged combat, trajectories, sight lines | Golden spirals, Fibonacci lattices, parabolic arcs | Sharpness, elegance, the arrow in flight |
| **Endurance** | Fa (4) | Defense, absorption, immovability | Voronoi cells, Reuleaux curves, convex hulls | Weight, solidity, the mountain that does not move |
| **Velocity** | Sol (5) | Charge, momentum, decisive action | Cycloids, involutes, velocity fields | Lightning, the moment of commitment |
| **Sustain** | La (6) | Healing, sustenance, the warm minor | Sinusoidal envelopes, Gaussian distributions | Warmth that holds, the note that refuses to end |
| **Transcendence** | Ti (7) | The bridge, the boundary, the zero | Mandelbrot boundary, strange attractors, Julia sets | The uncanny — beautiful and terrifying simultaneously |

### 1.3 The Visual Duality — Convergence and Divergence

The game's deepest visual principle: **player = convergent, enemy = divergent**.

| Aspect | Player (Convergent) | Enemy (Divergent) |
|---|---|---|
| **Fractal type** | Mandelbrot interior — bounded, stable, rich | Mandelbrot exterior — escaping, chaotic, burning |
| **Color temperature** | Cool blues, warm golds, deep greens | Hot reds, acid greens, bruised purples |
| **Shape character** | Smooth curves, completed symmetries, closed forms | Jagged perturbations, broken symmetries, open wounds |
| **Motion quality** | Breathing (sine), spring-damped, gravitational | Twitching (noise), jerky, repulsive |
| **Sound parallel** | Consonance, resolution, the chord coming home | Dissonance, divergence, the series that never sums |

This duality is not binary. The **Mandelbrot boundary** — the infinitely complex edge between interior and exterior — is where the most visually complex events occur: harmonic capture, biharmonic resonance, the conversation between fields. At the boundary, convergent and divergent visual languages interleave. The player literally sees order and chaos superimposed.

### 1.4 Aesthetic Targets

- **Resolution-independent**: All shapes scale with zoom via parametric math
- **Color palette**: Seven-tone chromatic system with convergent/divergent variants
- **No outlines**: Shapes defined by fill, overlap, and mathematical glow
- **Subtle motion**: Parameter oscillation at ~0.3-2.0 Hz gives life without frame-based animation
- **Earned complexity**: Visual richness scales with gameplay depth. Layer 0 is spare. Layer 7 is overwhelming. The eye learns to read the math the same way the ear learns to hear it
- **The silence matters**: Empty space, darkness, the gaps between shapes — these are as designed as the shapes themselves. A formation with perfect harmony surrounded by void should feel like a candle in a cathedral

### 1.5 Code ↔ UI Name Mapping

The codebase uses pragmatic internal names. The UI displays Heptarchy-themed names. This table is the **canonical mapping** — if code and UI disagree, this table wins.

#### Buildings

| Code Name | UI Name (Heptarchy) | Class/Variable | Role |
|---|---|---|---|
| `town_hall` | **Tree of Life** | `Building(type="town_hall")` | Economy root, sap source, L-system tree |
| `barracks` | **Resonance Forge** | `Building(type="barracks")` | Unit training, Sierpinski lattice |
| `refinery` | **Harmonic Mill** | `Building(type="refinery")` | Resource processing, spirograph |
| `sentinel` | **Sentinel** | `Building(type="sentinel")` | Lattice anchor + resonance defense (was `tower`) |

> **Migration note**: Code currently uses `tower` in many places. The rename `tower` → `sentinel` is pending in the codebase. Until complete, `tower` in code = Sentinel in design. The old Tower concept (Koch snowflake turret firing cannonballs) no longer exists as a separate building — its defense role is absorbed into Sentinel via resonance fields, and its Koch snowflake shape becomes the Sentinel's aura geometry.

#### Units

| Code Name | UI Name (Heptarchy) | Tone | Dark Mirror |
|---|---|---|---|
| `worker` / `gatherer` | **Gatherer** | Do (1) | Blight Reaper |
| `soldier` | **Warden** | Re (2) | Hollow Warden |
| `archer` | **Ranger** | Mi (3) | Fade Ranger |
| `shield` | **Bulwark** | Fa (4) | Ironbark |
| `knight` | **Lancer** | Sol (5) | Thornknight |
| `healer` | **Mender** | La (6) | Bloodtithe |
| `sage` | **Sage** | Ti (7) | Hexweaver |

> **Current state**: Only Gatherer, Warden (Soldier), and Ranger (Archer) exist in code. Shield through Sage are v10_eta+ additions. The code name `soldier` displays as "Warden" in UI strings only — the class remains `Soldier` internally.

#### Resources

| Code Name | UI Name | Icon Shape |
|---|---|---|
| `gold` | **Flux** | Fibonacci spiral |
| `wood` | **Fiber** | Binary tree |
| `iron` | **Ore** | Octahedron wireframe |
| `steel` | **Alloy** | Reuleaux triangle |
| `stone` | **Crystal** | Voronoi cell cluster |
| `sap` | **Tonic** | Bifurcating root |

---

## 2. The Visual Depth Ladder

The game's visuals are **depth-layer gated**. What the player sees depends on how deep they've gone. This is not just UI — the world itself reveals more at higher layers.

| Layer | What's Visible | Visual Density | Emotional Read |
|---|---|---|---|
| **0 — Seed** | Terrain, units as simple shapes, basic HP bars, minimal HUD | Sparse, clean, comprehensible | "I can see everything. I understand this." |
| **1 — Growth** | Military unit detail (roses, spirals), building fractals at depth 2-3, stance indicators | Moderate | "The shapes are alive." |
| **2 — Pattern** | Formation geometry visible (spring connections, slot positions), squad borders, chord preview | Rich | "The patterns connect." |
| **3 — Harmony** | Resonance auras (faint waveform halos), terrain resonance scars visible, characteristic hints on units | Dense | "The world is responding to my math." |
| **4 — Resonance** | Interference patterns between formations, Sentinel symmetry axes, orbital shell visualization | Very dense | "Everything is connected to everything." |
| **5 — Music** | Reality distortion effects, visible waveforms, formation singing particles, Lorenz weather trails | Overwhelming to the uninitiated | "The math has become weather." |
| **6 — Transcendence** | Full orchestral visualization, Tree of Life root network, Mandelbrot boundary on minimap | Maximum | "I am inside the equation." |
| **7 — ???** | The Mirror Field. Both visual languages simultaneously. The palimpsest. | Beyond | "There is another side." |

**Key principle**: No visual element from Layer N+1 ever appears at Layer N. The world visually *unfolds*. A screenshot at Layer 0 looks like a clean RTS. A screenshot at Layer 6 looks like a mathematical hallucination rendered in real-time. Both are the same game.

---

## 3. Main Menu — The Mandelbrot Throne

**IMPLEMENTED in `menu.py`**

The main menu IS the game's cosmological thesis: the Mandelbrot set as the boundary between the player's world and the enemy's. The camera drifts toward the seahorse valley — the most complex region of the boundary — because that's where the game lives.

Key parameters:
- Mandelbrot renderer at half-resolution, max_iter=256
- Color map: COL_BG → gold → muted green → stone → COL_BG; interior = COL_BG
- Smooth iteration count: `mu = n - log2(log2(|z|))`
- Slow zoom drift toward mini-brot in seahorse valley
- Julia set transitions per difficulty:
  - Easy: `c = -0.4 + 0.6j` (Douady rabbit — friendly, rounded)
  - Medium: `c = -0.8 + 0.156j` (complex but navigable)
  - Hard: `c = -0.7269 + 0.1889j` (dendrite — sharp, unforgiving)
- Difficulty buttons framed with polar roses (3/5/7 petals matching leaf_k)
- Golden ratio positioning: title at h/φ³, buttons at h/φ²

**Future (v12+):** The menu fractal subtly reflects the player's highest achieved Layer. A Layer 0 player sees the standard Mandelbrot. A Layer 5 player sees deeper zoom with richer color banding. A Layer 7 player sees the boundary *from both sides* — interior and exterior simultaneously visible, the fractal becoming a window rather than a wall.

---

## 4. Units — The Seven Voices Made Flesh

### 4.1 The Visual Grammar

Every unit is a **polar equation in motion**. The equation defines the shape; the state modifies the parameters; the rank deepens the complexity. Enemy variants use the same equations with **divergent perturbation** — the same math, corrupted.

| Tone | Unit | Polar Equation | Key Param | Visual Spirit |
|---|---|---|---|---|
| **Do (1)** | Gatherer | Superellipse `r = 1/(|cos|^n + |sin|^n)^(1/n)` | n=4, rotated 30° | The hex — nature's tiling choice, the worker bee |
| **Re (2)** | Soldier | Rose `r = cos(kθ)` | k=3/2 (recruit) → k=5 (captain) | Petals that cut — each rank adds a blade |
| **Mi (3)** | Archer | Golden spiral `r = ae^(bθ)`, mirrored | b=0.3063 (ln(φ)/(π/2)) | The bow IS a spiral. Fibonacci dots mark the aim |
| **Fa (4)** | Shield | Reuleaux triangle / constant-width curve | width parameter scales with HP ratio | Curves that cannot be penetrated — same width from every angle |
| **Sol (5)** | Knight | Cycloid `x = r(t - sin t), y = r(1 - cos t)` | Phase velocity determines charge visual | The wheel of war — rolling thunder, ground contact at every point |
| **La (6)** | Healer | Gaussian bell curve envelope on sine carrier | σ (spread) scales with heal range | The warmth distribution — strongest at center, fading gently |
| **Ti (7)** | Sage | Julia set boundary points (sampled) | c parameter from unit's hidden ∅ value | Not a shape — a boundary. Never the same twice. |

**Enemy variants**: Same base equations + jagged high-frequency perturbation:
```
r_enemy = r_base + noise * sin(17θ) * (1 + 0.3 * anim_attack)
```
Inverted rotation direction. Dual-frequency breathing (corrupted heartbeat). The enemy doesn't have different math — it has the same math *out of tune*.

Rank variants:
- **Gatherers**: Add concentric hexes (rank 2+), inner counter-rotation (rank 3+), skill-color border glow
- **Soldiers**: Add petals (k increases with rank), trail ghosts at rank 3+ while moving
- **Archers**: Add Fibonacci dots along spiral limbs, limb count increases with rank
- **Shields** (v10_eta): Reuleaux curve becomes n-gon constant-width (3 → 5 → 7 sides with rank)
- **Knights** (v10_eta): Cycloid gains more lobes, motion blur intensity scales with rank
- **Healers** (v11): Gaussian envelope widens, concentric heal rings appear
- **Sages** (v12): Julia set boundary becomes more detailed (higher iteration count) with rank

### 4.2 Characteristic Visual Signatures (v10_eta+)

When a unit's characteristics are revealed through rank, subtle visual modifiers appear:

| Characteristic | Symbol | Visual Effect |
|---|---|---|
| **Precision (σ)** | Sharp edges | Polar equation exponent increases — shapes become crisper, points sharper |
| **Resonance (ω)** | Glow pulse | Faint aura oscillation at the unit's natural frequency |
| **Entropy (S)** | Jitter | Vertex positions gain low-amplitude noise — shape shimmers unpredictably |
| **Symmetry (Γ)** | Perfect form | Rotational symmetry enforced — shape is mathematically exact |
| **Density (ρ)** | Compact fill | Shape radius slightly reduced, fill opacity increased |
| **Elasticity (κ)** | Spring bounce | Shape overshoots and settles on state transitions |
| **??? (∅)** | *Nothing visible* | The 7th characteristic has no visual. It was never meant to be seen. |

---

## 4B. Unit Lifecycle Animations — Idle, Move, Fight, Fall

### 4B.1 Animation Principles

| State | Animates What | Math Mechanism |
|---|---|---|
| **Idle / Guard** | Shape breathes | Slow radius + rotation oscillation |
| **Moving** | Shape leans forward | Directional squash, faster phase |
| **Attacking (melee)** | Shape lunges | Radius spike + sharpness burst |
| **Shooting (ranged)** | Bow draws and releases | Limb flex + recoil spring |
| **Taking damage** | Shape shudders | White flash + vertex noise |
| **Dying** | Shape disintegrates | Petal shed / uncoil / fragment burst |
| **Fleeing** | Shape contracts | Shrink + accelerated wobble |

1. **Parametric, not positional**: Animate input parameters of polar equations (radius multiplier, rotation offset, sharpness exponent, perturbation amplitude).
2. **Timers, not frames**: Uses `game_time` (continuous float) and smooth interpolation. No discrete frame counts.

### 4B.2 Universal Animation State Machine

```python
Unit.__init__:
    self._anim_time = random.uniform(0, 10)  # desync idle phase per unit
    self._anim_flash = 0.0      # damage flash timer (decay to 0)
    self._anim_attack = 0.0     # attack lunge timer (decay to 0)
    self._anim_death = 0.0      # death dissolve progress (0→1 over lifetime)
    self._anim_dying = False     # death animation active
    self._death_seed = 0         # deterministic death pattern seed

Unit.update:
    self._anim_time += dt
    if self._anim_flash > 0:
        self._anim_flash = max(0, self._anim_flash - dt / 0.12)
    if self._anim_attack > 0:
        self._anim_attack = max(0, self._anim_attack - dt / 0.18)
```

### 4B.3 Universal Animation Effects

#### Damage Flash (White Strobe)

```
on take_damage:
    self._anim_flash = 1.0

during draw:
    if _anim_flash > 0:
        flash_t = _anim_flash ** 2    # quadratic falloff
        draw_color = lerp(base_color, (255, 255, 255), flash_t * 0.7)
```

Enemy variant: flash toward `(200, 40, 40)` red instead of white.

#### Idle Breathing (Radius Pulse)

```
if state == "idle" or state == "guard":
    breath_t = sin(_anim_time * 1.8)          # ~0.55 Hz heartbeat
    radius_mult = 1.0 + 0.03 * breath_t       # +/- 3% radius shift
```

Per-unit `_anim_time` offsets create staggered breathing across groups.

#### Movement Lean (Directional Squash)

```
if state == "moving":
    move_angle = atan2(vy, vx)
    for each theta:
        angle_diff = theta - move_angle
        squash = 1.0 + 0.12 * cos(angle_diff)   # 12% stretch forward
        r_final = r(theta) * radius * squash

squash_amount = 0.08 + 0.04 * min(1.0, speed / max_speed)
```

#### Flee Contraction

```
if state == "fleeing":
    fear_t = sin(_anim_time * 8.0)      # fast 8 Hz tremor
    radius_mult = 0.85 + 0.05 * fear_t   # 15% smaller, 5% jitter
    rotation_offset += 0.03 * fear_t
```

#### Death Dissolve (Universal Framework)

```
on death:
    self._anim_dying = True
    self._anim_death = 0.0
    self._death_seed = hash(id(self))
    self.alive = False  # gameplay-dead immediately
    # entity stays in draw list for 0.6 sec

during death animation (_anim_death: 0.0 → 1.0):
    alpha_global = int(255 * (1.0 - _anim_death))
    # unit-type-specific dissolve (see below)
    # when _anim_death >= 1.0: remove from render list
```

---

### 4B.4 Gatherer — The Humming Hive

#### Idle: Hex Breathe + Inner Rotation
```
radius_mult = 1.0 + 0.025 * sin(_anim_time * 1.8)
inner_rotation_offset = _anim_time * 0.15
inner2_rotation_offset = -_anim_time * 0.10
skill_border_alpha = 180 + int(40 * sin(_anim_time * 2.5))
```

#### Moving: Waddle Bounce
```
if state == "moving":
    waddle_y = -abs(sin(_anim_time * 6.0)) * 2.0 * z
    draw_y = sy + int(waddle_y)
    rotation_offset = 0.04 * sin(_anim_time * 6.0)

if carry_amount > 0:
    waddle_freq = 4.5; waddle_amp = 3.0 * z
    orbit_wobble = sin(_anim_time * 3.0) * 0.15
```

#### Gathering: Rhythmic Pulse
```
if state == "gathering":
    gather_phase = (_anim_time * 2.5) % (2 * pi)
    if gather_phase < 0.4:
        vertical_squash = 0.88
    else:
        vertical_squash = lerp(0.88, 1.0, (gather_phase - 0.4) / 1.5)
    flash = 1.0 if gather_phase < 0.3 else 0.0
    inner_color = lerp(base_inner_color, resource_color, flash * 0.4)
```

#### Building: Spinning Industry
```
if state == "building":
    inner_rotation = _anim_time * 1.2
    inner2_rotation = -_anim_time * 0.9
    if int(_anim_time / 0.3) != int((_anim_time - dt) / 0.3):
        sparkle_vertex = int(_anim_time * 7) % n_pts
        draw_small_flash(pts[sparkle_vertex], color=(240, 230, 200))
```

#### Dying: Honeycomb Dissolution
```
death animation (0.0 → 1.0 over 0.6 sec):
    for i in range(6):
        wedge_pts = [center, hex_pts[i*n//6], hex_pts[(i+1)*n//6]]
        drift_angle = (2 * pi * i / 6) + death_seed_offset[i]
        drift_dist = _anim_death * 20 * z
        wedge_rotation = _anim_death * 0.8
        alpha = int(255 * max(0, 1.0 - _anim_death * 1.6))
        draw_wedge(translated + rotated, color, alpha)
```

---

### 4B.5 Soldier — The Pulsing Blade

#### Idle / Guard: Rose Rotation + Petal Breathe
```
idle_rotation = _anim_time * 0.3
radius_mult = 1.0 + 0.03 * sin(_anim_time * 2.0)

if state == "idle" and target_entity:
    idle_rotation = _anim_time * 0.8  # alert, faster spin
    radius_mult = 1.0 + 0.05 * sin(_anim_time * 3.0)

inner_rotation = -_anim_time * 0.5  # counter-rotate inner rose
```

#### Moving: Forward Lean + Trail Ghosts
```
if state == "moving":
    target_rotation = move_angle - pi/2
    current_rotation = lerp(current_rotation, target_rotation, 0.15)
    squash_amount = 0.15
    flutter = sin(_anim_time * 8.0) * 0.03

if rank >= 3 and state == "moving":
    for ghost_i, ghost_age in enumerate([0.10, 0.20]):
        ghost_alpha = int(60 * (1.0 - ghost_i * 0.5))
        draw_soldier_shape(ghost_x, ghost_y, r * 0.95, alpha=ghost_alpha)
```

#### Attacking: Lunge + Sharpness Spike
```
on attack_timer reset:
    _anim_attack = 1.0

Phase 1 — LUNGE (attack_t: 1.0 → 0.5, ~90ms):
    lunge_offset = 6 * z * attack_t * toward_target
    effective_sharpness = 0.6 - 0.3 * attack_t
    radius_mult = 1.0 + 0.15 * attack_t

Phase 2 — RETRACT (attack_t: 0.5 → 0.0, ~90ms):
    lunge_offset *= attack_t * 2
```

Berserker trait: `lunge_distance = 9 * z`, sharpness drops to 0.15.

#### Dying: Petal Shed
```
death animation (0.0 → 1.0 over 0.6 sec):
    n_petals = int(2 * k)
    shed_interval = 0.8 / n_petals
    for petal_i in range(n_petals):
        petal_birth = petal_i * shed_interval
        if _anim_death >= petal_birth:
            drift = (anim_death - petal_birth) * 30 * z
            tumble = (anim_death - petal_birth) * 2.5
            alpha = int(255 * max(0, 1.0 - (anim_death - petal_birth) * 2.5))
            draw_detached_petal(petal_i, drift, tumble, alpha)
```

Rank 3+: petals shed in golden-angle spiral. Rank 4: final blue flash on center dot.

---

### 4B.6 Archer — The Flexing Bow

#### Idle: Limb Sway + String Tension
```
idle_flex = sin(_anim_time * 1.5) * 0.04
string_x_offset = -idle_flex * r * 0.3
arrow_y_offset = sin(_anim_time * 2.0) * 1.0 * z
dot_brightness = 0.8 + 0.2 * sin(_anim_time * 1.2 + dot_index * 0.7)
```

#### Shooting: Full Draw-Release Cycle
```
Phase 1 — NOCK (100% → 70% of attack_cd):
    string_draw = lerp(0, r * 0.25, nock_t)
    limb_spread = 1.0 + 0.06 * nock_t

Phase 2 — HOLD (70% → 15%):
    string_draw = r * 0.25
    tremble = sin(_anim_time * 25) * 0.01 * (1.0 - hold_t)

Phase 3 — RELEASE (15% → 0%):
    string_draw = r * 0.25 * (1.0 - release_t ** 0.5)  # fast sqrt snap
    limb_spread = 1.06 - 0.10 * release_t   # overshoot inward
    recoil_x = -3 * z * (1.0 - release_t)

Aftermath — SETTLE (0.2 sec):
    limb_spread = 1.0 + 0.04 * sin(settle_t * pi * 3) * (1.0 - settle_t)
    string_x = normal_x + 2 * sin(settle_t * pi * 4) * (1.0 - settle_t)
```

#### Dying: Bow Uncoils
```
death animation (0.0 → 1.0 over 0.6 sec):
    effective_theta_range = (1.0 - _anim_death) * normal_theta_range
    if _anim_death > 0.2:
        string_break_t = (_anim_death - 0.2) / 0.3
        string_alpha = int(255 * max(0, 1.0 - string_break_t * 2))
    arrow_fall_y = _anim_death * 15 * z
    for dot_i, dot in enumerate(fib_dots):
        dot_shed_time = 0.3 + dot_i * 0.1
        if _anim_death > dot_shed_time:
            dot_drift = (_anim_death - dot_shed_time) * 25 * z
```

---

### 4B.7 Siege — The Grinding Engine

#### Idle: Spike Pulse + Inner Rotation
```
radius_mult = 1.0 + 0.04 * sin(_anim_time * 1.2)  # slow, heavy
inner_gear_rotation = _anim_time * 0.4
spike_emphasis = 1.0 + 0.06 * abs(sin(_anim_time * 0.8))
```

#### Attacking: Spike Extend
```
spike_mult = 1.0 + 0.35 * _anim_attack ** 2
for each spike_i:
    alignment = max(0, cos(spike_angle - angle_to_target))
    spike_extra = alignment * 0.2 * _anim_attack
```

#### Dying: Implosion
```
death animation (0.0 → 1.0 over 0.8 sec):
    spike_mult = 1.0 - _anim_death * 0.8
    body_radius = radius * (1.0 - _anim_death * 0.7)
    if _anim_death > 0.6:
        fragments burst outward with orange flash
```

---

### 4B.8 Elite — The Unstable Star

#### Idle: Counter-Rotating Rose Orbit
```
outer_rotation = _anim_time * 0.25
inner_rotation = -_anim_time * 0.35
center_glow_radius = max(2, r // 5) + sin(_anim_time * 3.0) * 1.5 * z
```

#### Dying: Binary Fission
```
death animation (0.0 → 1.0 over 0.7 sec):
    outer and inner roses drift apart along death_seed angle
    radii shrink, glow fades
    final dot burst at 80% progress
```

---

### 4B.9 Animation Implementation Details

#### Timer Management
```python
self._anim_time = random.uniform(0, 10.0)  # desync
self._anim_flash = 0.0    # 1.0 → 0.0 over 0.12s
self._anim_attack = 0.0   # 1.0 → 0.0 over 0.18s
self._anim_dying = False
self._anim_death = 0.0    # 0.0 → 1.0 over 0.6s
```

#### Enemy Animation Corruption
```
if is_enemy:
    breath = sin(t * 1.8) * 0.5 + sin(t * 2.7) * 0.5  # irregular dual-freq
    squash_amount *= 1.5    # 18% lean instead of 12%
    lunge_distance *= 1.2   # 20% farther attack
    death_speed = 1.0 / 0.4  # faster death (0.4s vs 0.6s)
    jagged_amplitude = base * (1.0 + 0.3 * _anim_attack)
```

#### Trait-Modified Animations

| Trait | Animation Effect |
|---|---|
| **Brave** | Idle pulse amplitude +50% |
| **Aggressive** | Attack lunge +30%, faster retract |
| **Berserker** | Below 50% HP: sharpness permanently spiked |
| **Nimble** | Movement bounce +40%, faster flutter |
| **Sharpshooter** | Hold-phase tremble reduced 70% |

#### Performance Budget
Worst case: 200 units all fighting = ~200 extra sin/cos calls/frame. At 60 FPS: **< 0.5ms**.

---

## 5. Buildings — L-System Fortresses

### 5.1 Current Building Shapes

**IMPLEMENTED in `building.py` / `building_shapes.py`**

| Building | Shape | Equation/Grammar | Key Params |
|---|---|---|---|
| **Town Hall / Tree of Life** | L-system tree | `F -> FF+[+F-F-F]-[-F+F+F]`, angle=22.5° | Iter 0-4, grows with construction |
| **Barracks** | Sierpinski triangle | Subdivide equilateral, remove center | Depth 0-3 |
| **Refinery** | Spirograph (epitrochoid) | `x=(R+r)cos(t)-d*cos((R+r)/r*t)` | R=5, r=3, d=5 |
| **Sentinel** | Standing stone + Koch aura | Reuleaux monolith body, Koch-curve resonance field | Voronoi texture, D1-D8 symmetry anchoring |

Construction: fractal depth/iterations increase with build_progress.
Ruin state: iterations drop to minimum, colors desaturate.

### 5.2 The Sentinel — Lattice Anchor & Resonance Defense (v10_zeta+)

The Sentinel is the unified defense and geometry building. It replaces the old "Tower" concept entirely — there are no cannonballs, no turrets. Defense comes from **harmonic resonance**: the Sentinel projects a field that damages divergent (enemy) entities passing through its symmetry zone. The more Sentinels form dihedral symmetry, the stronger and wider the resonance field becomes.

Sentinels are the visual backbone of base-building. They are **standing stones** — visually distinct from all functional buildings. They anchor the geometry within which everything else gains meaning, AND they protect the base through the mathematics of their arrangement.

#### Sentinel Shape

```
Standing stone: tall Reuleaux triangle (constant-width curve)
    aspect ratio 1:2.5 (tall, monolithic)
    base color: (140, 130, 100) warm stone
    surface: Voronoi cell texture (5-7 cells, deterministic per position)
    glow: faint aura whose color matches tuned tone (v10_eta+)
    animation: slow 0.2 Hz vertical pulse (breathing monolith)

Resonance field (Koch aura):
    Koch snowflake outline centered on Sentinel, radius = defense_range
    depth: scales with Sentinel level (depth 1 at Lv.1, depth 2 at Lv.2)
    color: (180, 160, 255) resonance glow at 30% alpha, pulses at 0.5 Hz
    when enemies inside field: Koch outline brightens, pulse accelerates to 2 Hz
    field overlaps: where two Sentinel Koch fields intersect, interference
        pattern appears (constructive = bright nodes, destructive = dark)
```

#### Resonance Defense Mechanics (Visual)

The Sentinel does not fire projectiles. It **resonates**. Defense is expressed visually through:

1. **Passive Field**: Koch snowflake outline at defense range, faintly pulsing. Enemies entering the field take continuous damage — visualized as their divergent perturbation increasing (shapes become more jagged, colors destabilize toward white noise).

2. **Harmonic Pulse** (replaces old "Sentinel's Cry"): When triggered (cooldown-based), a circular resonance wave expands outward from the Sentinel. Visual: concentric Koch rings expanding and fading, color shifts from resonance glow to gold at the wavefront. Damages enemies, buffs allies.

3. **Lattice Amplification**: When Sentinels form symmetry groups (D2+), the resonance fields merge along symmetry axes. Visual: Koch outlines connect into a unified boundary. Interior becomes a **resonance zone** — faint golden wash, visible standing wave pattern at Layer 4+. Enemies inside the unified zone take amplified damage.

4. **Dissonance Absorption**: When an enemy dies inside a Sentinel's field, the death energy is visually drawn toward the Sentinel as contracting spirograph trails (the old cannonball trail math, repurposed). The Sentinel's Voronoi texture briefly flickers with absorbed color before returning to stone.

```
Field damage visual on enemy:
    perturbation_amp += 0.15 * field_strength    # shapes become more jagged
    color = lerp(base_color, (255, 255, 255), field_strength * 0.3)  # bleaching
    vertex_noise_freq = 17 + 8 * field_strength  # higher frequency corruption

Harmonic pulse visual:
    for ring_i in range(3):
        ring_radius = pulse_progress * max_range - ring_i * 15
        koch_depth = 2 if ring_i == 0 else 1
        alpha = int(200 * (1.0 - pulse_progress) * (1.0 - ring_i * 0.3))
        draw_koch_circle(center, ring_radius, koch_depth, RESONANCE_GLOW, alpha)
```

#### Symmetry Axis Visualization

When Sentinels form dihedral symmetry groups, the axes become visible:

| State | Visual |
|---|---|
| **Complete axis** | Gold line `(218, 165, 32)`, 1px, full opacity, faint glow |
| **Broken axis** (Sentinel missing) | Dashed line `(180, 80, 40)`, flickering at 2 Hz, gap pulses red |
| **Potential axis** (one more Sentinel needed) | Dotted line `(80, 75, 55)`, 30% alpha, slow fade pulse |
| **Corrupted axis** (Bloodtithe corruption) | Axis color inverts to `(120, 20, 60)`, dark undertone glow, particles drift downward |

#### Ghost Placement Guides

When placing a Sentinel:
- **Mirror ghosts**: Translucent Sentinel outlines at positions that would complete the next symmetry order
- **Fill zone**: Interior area shaded by completion percentage (0% = transparent, 100% = faint gold wash)
- **Harmonic preview**: If tuning is available (v10_eta), ghost shows what tone each position would optimally hold

#### Base Symmetry Visual Progression

| Order | Geometry | Visual Character |
|---|---|---|
| **D1** (2 Sentinels) | Mirror line | Single gold axis, simple bilateral glow |
| **D2** (4 Sentinels) | Cross | Perpendicular axes, quadrant shading |
| **D3** (6 Sentinels) | Triangle | Three axes forming Star of David pattern |
| **D4** (8 Sentinels) | Square | Four axes, strong grid feel, visible mirror zones |
| **D6** (12 Sentinels) | Hexagon | Six axes, honeycomb interior glow, nature's tiling |
| **Fractal L1+** | Meta-structure | Outer axes connect to inner, self-similar glow pattern |

---

## 5B. Building Lifecycle Fractals — Damage, Ruin & Repair

### 5B.1 Universal Damage Language

#### Color Desaturation Gradient
```
damage_ratio = 1.0 - (hp / max_hp)
For each channel: damaged_c = lerp(original_c, gray, damage_ratio * 0.6)
```
0.6 cap prevents total gray — ruins retain ghost of original hue.

#### Damage Shake (Micro-Tremor)
Two frequencies (40/53 Hz) create Lissajous micro-orbit, damps in ~150ms.

#### Crack Lines (Deterministic)
```
n_cracks = int((1.0 - hp_ratio) * 5)
crack_seed = building_id * 7919
Color: (8, 5, 3) near-black, 1px width
```

### 5B.2 Per-Building Damage, Ruin & Repair

**Town Hall — The Dying & Reborn Tree:**
- Damage: Autumn decay (green → amber → brown → gray). Branch pruning by hash threshold
- Ruin: Charred stump, iter 1, smoke wisps, two ember dots
- Repair: Spring regrowth — tips flash bright green, bloom pulse at 100%

**Barracks — The Shattering & Reforging Lattice:**
- Damage: Fracture propagation (jittering sub-triangles, depth reduction)
- Ruin: Outer border only (dashed), scattered fragment triangles
- Repair: Crystallization wave — triangles flash and snap into place

**Refinery — The Grinding Halt & Restart:**
- Damage: Wobble & stutter (rotation speed modulated by sin(t×3), cusp dots dim)
- Ruin: Simple dashed circle, scattered cusp dots
- Repair: 4-phase restart sequence — dots return, curve re-emerges, rotation accelerates

**Sentinel — The Cracking & Retuned Monolith:**
- Damage: Voronoi fracture propagation (cells crack apart, resonance field flickers and shrinks). Koch aura depth reduces (2→1→0). Stone color desaturates toward gray
- Ruin: Cracked monolith leaning 15°, Voronoi cells fully separated with dark gaps, Koch aura gone, faint residual glow at base (the stone remembers)
- Repair: Harmonic retuning — Voronoi cells knit back together with gold flash at seams, Koch aura re-emerges ring by ring (depth 0→1→2), final pulse wave on full repair

### 5B.3 Performance Budget
Total: **< 2% frame time** for full base under attack. Max 8 particles per building.

---

## 6. Terrain — Noise Fields, Voronoi & Living Strata

### 6.1 Current Terrain Rendering

**Grass**: Perlin noise, two octaves. Base green `(46,139,87)` with ±15 value noise.

**Water** (future): Sine wave interference:
```
brightness = sin(x * 0.3 + t) * sin(y * 0.2 + t * 0.7) * 0.5 + 0.5
```

**Resource deposits**: Voronoi cell overlay per tile:
- Gold: sparse large cells (3-4 seeds), warm jitter
- Iron: medium angular cells (6-8 seeds), cool gray
- Stone: dense packed cells (10-12 seeds), warm tan

**Trees**: Current circle-on-circle. Future: simplified 2-iter L-system.

### 6.2 Living Strata Visual Layers (v11+)

The seven geological epochs leave visual marks that reveal progressively with depth layer:

| Epoch | What's Visible | First Visible At |
|---|---|---|
| **1 — Stone** | Mountain elevation (already visible as terrain height shading) | Layer 0 |
| **2 — Water** | River paths, lake surfaces, moisture gradient on tiles | Layer 0 |
| **3 — Green** | Forest density, grassland variation | Layer 0 |
| **4 — Crystal** | Resource deposit coloring (geological motivation visible in clustering patterns) | Layer 0 |
| **5 — Ruin** | Ancient structure foundations, broken walls, formation glyphs | Layer 3 (faint outlines at Layer 2) |
| **6 — Scar** | Resonance scars (warm golden shimmer), dissonance wounds (dark bruise-purple desaturation) | Layer 3 |
| **7 — Silence** | The palimpsest — all layers simultaneously, history written in terrain | Layer 7 |

#### Resonance Weathering (v11+)
Tiles near high-harmony formations slowly shift toward resonance-positive terrain:
- Color: subtle golden warmth creeps into tile base color
- Texture: Voronoi cells become more regular (ordered by resonance)
- Tile near dissonance: darkens, cells become jagged

#### Ruin Visual Types (v12+)

| Ruin | Visual | Discovery Hint |
|---|---|---|
| **Broken Sentinel Ring** | 3-5 stone shapes in partial symmetry, ghost axes faintly visible at Layer 3+ | Ancient base geometry |
| **Overgrown Barracks** | Stone rectangles under grass overlay, excavatable | Building patterns |
| **Resonance Obelisk** | Single standing stone with persistent glow — activates when player builds nearby | Free Sentinel position |
| **Formation Glyph** | Partial fractal etched in ground (Rose/Spiral/Koch recognizable) | Formation discovery hint |
| **Dissonance Crater** | Darkened terrain, warped Voronoi cells, enemy spawn bias | Warning: this place attracted darkness before |

### 6.3 Map Border

Map edge fades into Mandelbrot-derivative border — explored world dissolves into fractal chaos at edges. At Layer 5+, the border shows the actual Mandelbrot boundary, visually connecting the menu fractal to the game world.

---

## 7. Projectiles & Effects

### 7.1 Arrows — Parametric Darts
```
body: line from (x, y) to (x - dx*len, y - dy*len)
head: small delta-shaped triangle
fletching: two short angled lines at tail
```
Parametric tapering (line width decreases toward tail). Grounded: `(120,100,80)`.

### 7.2 Sentinel Resonance Pulse — Koch Wave

The Sentinel's active defense ability (replaces cannonballs). A harmonic pulse wave expanding from the Sentinel:

```
Expanding Koch ring:
    radius = pulse_age * expansion_speed    # 250 px/s
    koch_depth = 2 (wavefront) → 1 (trailing rings)
    color = lerp(RESONANCE_GLOW, EARTH_GOLD, pulse_age / max_age)
    alpha = int(220 * (1.0 - pulse_age / max_age))
    line_width = 2 at wavefront, 1 for trails

Trailing spirograph absorption (on enemy hit):
    hypotrochoid trail drawn FROM enemy position TOWARD nearest Sentinel
    4-5 trail points as fading circles (reuses old spirograph math)
    color: enemy's divergent color → desaturated → absorbed into stone
    duration: 0.3s
```

Ally buff visual: units inside pulse radius get a brief golden outline flash (0.2s).

### 7.3 Resonance Field Damage — Dissonance Bloom

When enemies take continuous damage inside a Sentinel's passive Koch field, the damage manifests as:

```
Per-enemy inside field:
    Lissajous bloom at enemy position (a/b = 3/2)
    Very small (8-12px radius), rapidly rotating
    Color: enemy's base color → white → transparent
    Duration: 0.15s per damage tick, overlapping creates shimmer

On enemy death inside field:
    Larger Lissajous bloom (a/b = 5/4, 20-30px)
    Color: bright orange-white → Sentinel's resonance glow → transparent
    Contracting spirograph trail from death position to nearest Sentinel
    Sentinel's Voronoi cells flash with absorbed energy color (0.3s)
```

The old spirograph trail and Lissajous bloom math is preserved — it just flows *toward* Sentinels instead of *away from* towers.

### 7.4 Selection Ring — Breathing Rose
```
r(θ + t) = base_radius + amplitude * cos(n * (θ + t))
    n = 6, amplitude = 2px, t rotates slowly
```

### 7.5 Resonance Effects (v11+)

| Effect | Visual | Layer |
|---|---|---|
| **Formation aura** | Faint waveform halo matching formation shape. Rose = petal shimmer, Koch = perimeter glow | 3+ |
| **Harmonic interference** | Where two formation auras overlap: constructive = bright nodes, destructive = dark anti-nodes | 4+ |
| **Reality distortion** | Coordinate warp — pixels near the formation visually bend. Fermata: afterimages. Modulation: path curvature | 5+ |
| **Tier 6 Harmonic** | Full visible standing wave pattern. Air between formations shimmers with mathematical interference | 5+ |
| **Hex effects** | Dark inverse of resonance — anti-glow, pixel repulsion, color inversion in hex radius | 5+ |

### 7.6 The Mandelbrot Boundary Visualization (v12+)

On the minimap and (at Layer 6+) in the game world:
- **Player-controlled areas**: Mandelbrot interior colors (deep blue, violet, black)
- **Enemy-influenced areas**: Exterior colors (orange, red, hot white)
- **The boundary between them**: Infinitely detailed fractal edge, rendered at minimap resolution
- Shifts in real-time as harmony and dissonance territories change

---

## 8. Color Language — The Chromatic Heptarchy

### 8.1 The Seven Tone Colors

Each tone has a primary color that pervades everything associated with it:

| Tone | Unit | Primary Color | Accent | Emotional Read |
|---|---|---|---|---|
| **Do (1)** | Gatherer | `(50, 130, 220)` Worker Blue | `(80, 180, 255)` | Reliable, present |
| **Re (2)** | Soldier | `(200, 60, 60)` Military Red | `(255, 100, 80)` | Dangerous, contained |
| **Mi (3)** | Archer | `(140, 100, 200)` Precision Purple | `(180, 130, 255)` | Sharp, elegant |
| **Fa (4)** | Shield | `(160, 150, 130)` Stone Tan | `(200, 190, 170)` | Immovable, ancient |
| **Sol (5)** | Knight | `(218, 165, 32)` Earth Gold | `(255, 200, 60)` | Decisive, brilliant |
| **La (6)** | Healer | `(46, 139, 87)` Life Green | `(80, 200, 120)` | Warm, sustaining |
| **Ti (7)** | Sage | `(100, 50, 150)` Void Violet | `(150, 80, 220)` | Uncanny, liminal |

### 8.2 The Dark 7 — Enemy Tone Colors

Each Dark 7 enemy mirrors a player tone with a divergent color shift:

| Player Tone | Dark Mirror | Color | Shift Description |
|---|---|---|---|
| Do → Blight Reaper | `(20, 80, 20)` | Green desaturated to fungal |
| Re → Hollow Warden | `(80, 80, 100)` | Red drained to hollow gray-blue |
| Mi → Fade Ranger | `(140, 0, 140)` | Purple shifted to aggressive magenta |
| Fa → Ironbark | `(90, 70, 40)` | Tan darkened to bark brown |
| Sol → Thornknight | `(140, 100, 20)` | Gold tarnished to rust |
| La → Bloodtithe | `(55, 10, 15)` | Green inverted to dark blood red |
| Ti → Hexweaver | `(40, 15, 60)` | Violet deepened to abyss purple |

### 8.3 System Colors

```
DARK CORE       (20, 20, 30)      UI backgrounds, void, fractal interior
EARTH GOLD      (218, 165, 32)    Gold resource, accents, symmetry axes
BRONZE          (205, 127, 50)    Veteran rank, warm highlights
CONVERGENT BLUE (15, 25, 60)      Player territory, Mandelbrot interior
DIVERGENT RED   (120, 20, 40)     Enemy territory, Mandelbrot exterior
RESONANCE GLOW  (180, 160, 255)   Harmony effects, Tier 3+ auras
DISSONANCE BURN (200, 80, 40)     Hex effects, enemy ritual glow
BOUNDARY WHITE  (240, 235, 220)   Mathematical highlights, transitions
FRACTAL DEEP    (10, 8, 25)       Deepest Mandelbrot, maximum depth
GHOST STONE     (80, 75, 60)      Ancient ruins, unrevealed elements
```

### 8.4 Resonance Color Spectrum

Harmony quality maps to a color ramp used throughout the UI:

| Quality | Range | Color | Feel |
|---|---|---|---|
| **Weak** | 0-50% | `(120, 80, 80)` muted red | Unresolved, tense |
| **Thin** | 50-70% | `(160, 160, 140)` pale | Searching |
| **Rich** | 70-90% | Formation's resonance color | Singing |
| **Perfect** | 90-100% | `(255, 230, 80)` blazing gold | Resolution |

---

## 9. The Fractal Interface — GUI as Living Organism

The GUI is not chrome bolted onto the game. It is **another mathematical organism** that grows with the player. At Layer 0, the GUI is nearly invisible. By Layer 6, it is a fractal cathedral of information.

### 9.1 Design Principles

1. **Fractal Coherence**: UI elements use the same math as the game world (Koch borders, rose decorations, spiral fills)
2. **Organic Geometry**: No flat rectangles — fractal borders, parametric outlines, fading edges
3. **Animated but Calm**: ~0.3 Hz pulse, Koch depth modulation, polar rose bloom on hover
4. **Earned Complexity**: Simple states = simple visuals; complex states = fractal richness
5. **Progressive Revelation**: The GUI literally grows new panels, indicators, and decorations as depth layers unlock

### 9.2 Fractal Typography — Self-Similar Glyphs

L-system rune font. Each glyph is polyline segments in normalized coords (0..1). Monospace: `char_w = font_size * 0.6`, `char_h = font_size`.

Stroke rendering: 2-pass (glow at 40% alpha + core at full color). Self-similar serifs at size ≥24px (depth 1), ≥36px (depth 2):

```python
def _draw_serif(surf, x, y, angle, length, depth, color):
    if depth <= 0 or length < 1:
        return
    ex = x + math.cos(angle) * length
    ey = y + math.sin(angle) * length
    pygame.draw.line(surf, color, (int(x), int(y)), (int(ex), int(ey)), 1)
    _draw_serif(surf, ex, ey, angle + 0.6, length * 0.5, depth - 1, color)
    _draw_serif(surf, ex, ey, angle - 0.6, length * 0.5, depth - 1, color)
```

| Context | Size | Serif Depth | Glow |
|---|---|---|---|
| Hero title | 40px | 2 | Strong |
| Panel titles | 28px | 1 | Yes |
| Body text | 20px | 0 | Yes |
| Small labels | 16px | 0 | Subtle |
| Tiny | 13px | 0 | No |

Fallback: `pygame.font.SysFont(None, size)` for sizes <13px or strings >50 chars.

### 9.3 Panel Frames — Koch Border System

```python
def koch_border(surf, rect, depth, color, line_width=1):
    corners = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    for i in range(4):
        points = _koch_side(corners[i], corners[(i+1)%4], depth)
        pygame.draw.lines(surf, color, False, points, line_width)
```

Animated depth: `depth_float = 1.0 + 0.5 * sin(game_time * 0.3)`

Panel background: radial gradient center `(35,32,50)` → edge `(20,18,30)`.

| Panel | Border Color | Border Depth | Background |
|---|---|---|---|
| Top bar | `(80,75,55)` gold-gray | 1 | Horizontal Mandelbrot strip |
| Bottom info | `(80,80,100)` | 1-2 breathing | Radial gradient |
| Building panel | Building's own color | 1 | Faint shape echo |
| Unit panel | Unit type color | 1 | Faint polar rose echo |
| Tooltip | `(100,90,60)` gold | 1 (static) | Solid dark |
| Game-over | Outcome color | 2 | Deep radial gradient |
| Don't Panic | `(60, 80, 120)` calm blue | 1 | Gentle blue wash |

### 9.4 Buttons — Polar Rose Bloom

- **Idle**: Koch depth-1 border `(60,55,45)`, radial gradient fill, gold text
- **Hover**: Koch depth-2, brighter fill, tiny 3-petal roses at corners, bright gold text
- **Pressed**: Koch depth-1, darker fill, text offset +1px down
- **Disabled**: Simple rect `(40,38,45)`, flat fill, muted text
- Cost display: resource-colored fractal font below. Affordable: subtle pulse glow

### 9.5 Resource Display — Fibonacci Counter

Resource icons:
| Resource | Shape | Math Basis |
|---|---|---|
| Gold/Flux | Fibonacci spiral | 3 quarter-turns |
| Wood/Fiber | Binary tree | Recursive Y-branch, 3 iterations |
| Iron/Ore | Octahedron wireframe | Polyhedron projection |
| Steel/Alloy | Reuleaux triangle | Constant-width curve |
| Stone/Crystal | Voronoi cell cluster | 4-5 cells packed |
| Tonic (v10_zeta) | Bifurcating root | Downward L-system, 2 iterations |
| Resonance (v11) | Standing wave | Sine envelope with nodes |

Animations: idle pulse (1.0 + 0.03 × sin(t × 1.5)), income flash to 1.15×, depletion warning wobble.

### 9.6 HP & Progress Bars — Spirograph Fills

Pre-rendered wave pattern cached surface; blit width slice per frame:
- Build progress: blue `(0,180,255)` wave, frequency increases with completion
- Train progress: gold wave. Lissajous bloom on completion
- HP: Fibonacci-segmented (largest segments vanish first on damage)

### 9.7 Selection System — Rose Rings

- Worker: superellipse hex ring
- Soldier: 5-petal rose ring at r+3
- Archer: golden spiral arc ring
- Buildings: Koch-curve rectangle outline, breathing depth
- Multi-select box: Koch-bordered, depth increases with box size

### 9.8 Minimap Frame

- Border: Koch depth-2 frame, `(80,75,55)` gold-gray
- Camera viewport: golden Koch depth-1 rectangle
- Combat heat: Lissajous bloom marks (fading trefoils)
- Attack flash: Red edge pulse during active incidents (Phase 2 UX — implemented)
- Mandelbrot overlay (v12+): Interior/exterior coloring showing harmony/dissonance territory

### 9.9 Notifications — Dissolving Runes

FractalFont with Koch-bordered pill shape. Fade-out as fractal dissolution:
1. Serif branches disappear (depth decreases)
2. Koch border depth 1 → 0
3. Random character strokes disappear
4. Final: just dots where text was, then gone

### 9.10 Progressive GUI Growth — The Depth Ladder in Practice

| Layer | Top Bar | Bottom Panel | Minimap | World Overlays |
|---|---|---|---|---|
| **0** | Resources (5), build timer | Selected unit/building info, build buttons | Terrain + units | HP bars, selection rings |
| **1** | + Tension meter, incident counter | + Stance buttons, formation bar (locked icons) | + Combat heat | + Damage numbers, command rings |
| **2** | + Harmony % on formations | + Chord preview, squad cards, "Form Squad (F)" button | + Squad indicators | + Formation slot positions (springs visible) |
| **3** | + Resonance counter | + Characteristic hints, harmony quality descriptors | + Resonance scar overlay | + Faint formation auras |
| **4** | + Orbital shell indicators | + Sentinel symmetry info, mirror bonus display | + Symmetry axis overlay | + Interference patterns |
| **5** | + Reality distortion meter | + Tier 6 effect controls, singing frequency display | + Mandelbrot boundary begins | + Visible waveforms, distortion fields |
| **6** | + Full harmonic dashboard | + Tree of Life root display, full orchestral UI | + Full Mandelbrot territory | + Everything |
| **7** | + Shadow field indicators | + Both orchestras visible | + Both Trees visible | + The Mirror Field |

---

## 10. The Game-Over Canvas

The game-over screen (Phase 1 UX overhaul — implemented) is the player's **report card rendered as visual art**:

### Victory
- Background: dark overlay with faint golden radial gradient (the harmony that won)
- Title: "VICTORY!" in formation's resonance color
- Stats panel: Koch-bordered, gold axes
- Grade (S/A/B/C): rendered large in resonance spectrum color
- Tip: warm gold, encouraging

### Defeat
- Background: dark overlay with faint red radial gradient (the dissonance that killed)
- Title: "DEFEAT" in enemy crimson
- Stats panel: Koch-bordered, muted gray
- Contextual tip: golden, specific to failure mode
- Difficulty suggestion: green, gentle

### Surrender
- Background: neutral dark overlay
- Title: "SURRENDERED" in amber
- Stats: as defeat but with no judgment tone

---

## 11. Technical Notes

### 11.1 Performance Budget

All algorithmic art must be pre-rendered to surfaces and cached:
- **Menu Mandelbrot**: Render once at startup to 640×360 surface. Update zoom every 2-3s
- **Unit shapes**: Pre-compute per (type, rank) as 32×32/48×48 surfaces. Re-render on zoom change (quantized to 0.1 steps)
- **Building L-systems**: Pre-render at each depth (0-4). Cache 5 surfaces per type
- **Terrain tiles**: Render to tile atlas on map generation. Never recompute unless tiles change
- **Koch borders**: Cache per (width, height, depth, color) tuple. Invalidate on resize
- **Fractal font**: Cache per (character, size, color) tuple. ~80 glyphs × 5 sizes = 400 cached surfaces

### 11.2 Pygame Constraints

- No shader support — all math on CPU via Python/numpy
- `pygame.Surface` with `SRCALPHA` for transparency
- `pygame.draw` primitives for lines/circles/polygons
- `pygame.surfarray` for pixel-level Mandelbrot/noise
- `numpy` for vectorized fractal computation

### 11.3 Zoom Scaling

All shapes defined in unit coordinates (0.0-1.0), scaled at render time via `size * camera.zoom`. Zoomed out: fewer iterations/points. Zoomed in: more detail. Free LOD.

### 11.4 Godot Migration Visual Targets (v14)

| Capability | What It Unlocks Visually |
|---|---|
| **GPU shaders** | Real-time Mandelbrot boundary, resonance waveform interference, Julia set Sage shapes |
| **Particle GPU** | Thousands of resonance sparkles, hex corruption particles, formation singing visualization |
| **Custom render passes** | Coordinate warp for reality distortion, bloom for harmony, chromatic aberration for dissonance |
| **Dynamic lighting** | Sentinel glow, resonance scar luminescence, the Trees casting light |

---

## 12. GUI Remake Run — Implementation Plan

This plan turns the current functional-but-flat GUI into the fractal interface described above. Scoped to what's achievable NOW (v10_epsilon), with hooks for future depth-layer gating.

### Phase A: Fractal Font Foundation

| Task | File | Effort |
|---|---|---|
| Define `FRACTAL_GLYPHS` dict (A-Z, 0-9, punctuation — ~80 entries) | `fractal_font.py` (new) | 2 sessions |
| `FractalFont` class with glyph cache + 2-pass rendering (glow + core) | `fractal_font.py` | 1 session |
| Serif branching system (depth 0/1/2 based on size) | `fractal_font.py` | 0.5 session |
| Replace `draw_text()` calls in top bar, bottom panel titles, notifications | `gui.py` | 1 session |
| Benchmark: must stay under 2ms/frame for all text rendering | `fractal_font.py` | 0.5 session |

### Phase B: Koch Border & Panel Overhaul

| Task | File | Effort |
|---|---|---|
| `koch_border()` utility function with depth + animation support | `gui.py` or `fractal_ui.py` (new) | 0.5 session |
| Radial gradient panel backgrounds (replace flat fills) | `gui.py` | 1 session |
| Koch-bordered buttons with hover bloom (rose corners) | `gui.py` | 1 session |
| Bottom panel: Koch frame, type-colored accent, shape echo background | `gui.py` | 0.5 session |
| Top bar: Mandelbrot micro-strip background at 5% alpha | `gui.py` | 0.5 session |

### Phase C: Bars, Selection, Polish

| Task | File | Effort |
|---|---|---|
| `fractal_bar()` for HP/progress/train (pre-rendered wave slices) | `gui.py`, `unit.py`, `building.py` | 1 session |
| Rose/hex/spiral selection rings per unit type | `unit.py` | 1 session |
| Koch minimap border + golden viewport rectangle | `game.py` | 0.5 session |
| Notification dissolution animation (serif→border→strokes→dots→gone) | `gui.py` | 0.5 session |
| Game-over panel: Koch borders, radial gradient, grade rendering | `gui.py` | 0.5 session |

### Phase D: Integration & Performance

| Task | File | Effort |
|---|---|---|
| Profile full render pass: must stay under 16ms @ 60 FPS | all | 0.5 session |
| Glyph surface caching validation (memory < 10MB for full glyph set) | `fractal_font.py` | 0.5 session |
| Koch border caching (avoid re-rendering static panels every frame) | `gui.py` | 0.5 session |
| Visual QA pass: readability at all zoom levels, colorblind-safe contrast | all | 1 session |
| Fallback testing: SysFont graceful degradation for edge cases | `fractal_font.py` | 0.5 session |

### Total Estimate: ~13 sessions across 4 phases

### Implementation Order

```
Phase A (font) → Phase B (panels) → Phase C (bars/selection) → Phase D (QA)
```

Each phase is independently shippable. Phase A alone transforms the game's typographic identity. Phase B makes it feel like a fractal world. Phase C and D polish.

---

## The Visual Road Ahead

The VDD, like the game, is a fractal. Every section described here contains three more sections not yet written. The Sentinel glow animations, the Tree of Life root network rendering, the Mandelbrot boundary real-time computation, the hex effect distortion shaders, the procedural audio waveform visualization — all live in the space between these words, waiting for the version that calls them into existence.

What's written here is enough to build the next three versions. What's implied is enough to build the next ten. The math goes deeper than the document can see from here.

And that's exactly the point.

---

## File Reference

| File | Purpose |
|---|---|
| `visuals/VDD.md` | This file — visual design authority |
| `GDD_Roadmap.md` | The mathematical odyssey roadmap (gameplay + systems design) |
| `GDD_Current_v10.md` | Full spec of currently implemented v10 systems |
| `UX_Test_Matrix.md` | 3×3 user journey test scenarios |
| `visuals/*.py` | Visual proof-of-concept scripts |
