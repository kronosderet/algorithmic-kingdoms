# Visual Design Document (VDD)
## Algorithmic Art Direction for the RTS

> *"No sprites. No pixel art. Every shape is grown from math —
> the same way a tree branches, a shield curves, or a fortress tessellates."*

---

## 1. Core Philosophy

### 1.1 Algorithmic Naturalism

Every visual element in the game is generated procedurally from mathematical
functions. The look is **organic geometry** — shapes that feel alive because
they emerge from the same recursive rules that create coastlines, ferns, and
crystal structures. Nothing is hand-drawn; everything is *computed*.

This serves a practical goal too: the entire game ships as a single .exe with
zero external assets. Every pixel is born at runtime.

### 1.2 The Three Pillars

| Pillar | Meaning | Math Lineage |
|---|---|---|
| **Growth** | Buildings and economy feel like living things expanding | L-systems, fractals, Fibonacci |
| **Force** | Combat units project contained violence, tension, sharpness | Lissajous curves, polar roses, spirals |
| **Order from Chaos** | The map, terrain, and fog emerge from noise into clarity | Perlin noise, Voronoi, Mandelbrot |

### 1.3 Aesthetic Targets

- **Resolution-independent**: All shapes scale with zoom via parametric math
- **Color palette**: Muted earth tones (existing palette) with mathematical
  accent glows — gold Fibonacci spirals, steel-blue interference patterns
- **No outlines**: Shapes are defined by fill, overlap, and subtle glow — not
  black edges. This is math art, not cartoons.
- **Subtle motion**: Gentle parameter oscillation gives life without frame-based
  animation. A building "breathes" by cycling a fractal depth. A soldier's
  shield slowly rotates its rose curve.

---

## 2. Main Menu — The Mandelbrot Throne

### 2.1 Concept

The main menu background is a **deep zoom into the Mandelbrot set**, rendered
in the game's color palette. Not the garish rainbow everyone has seen — instead,
a moody, desaturated render using the terrain/UI palette:

- Deep regions: `COL_BG` dark blue-black (20, 20, 30)
- Border filaments: gold (218, 165, 32) fading to bronze (205, 127, 50)
- Escape-time bands: muted greens (46, 139, 87) and stone grays (160, 150, 130)

The zoom target is a **mini-brot** in one of the seahorse valley spirals — the
self-similar copies that look like tiny fortresses within fortresses. The camera
drifts imperceptibly deeper each frame, so the background is never static but
never jarring.

### 2.2 Implementation Sketch

```
Mandelbrot(cx, cy, max_iter=256):
    z = 0+0j
    for i in range(max_iter):
        z = z*z + complex(cx, cy)
        if |z| > 4.0: return i
    return max_iter

color_map:
    0..64   -> lerp(COL_BG, terrain_gold, t)          # dark to gold filaments
    64..128 -> lerp(terrain_gold, terrain_grass, t)    # gold to muted green
    128..192-> lerp(terrain_grass, COL_STONE, t)       # green to stone
    192..256-> lerp(COL_STONE, COL_BG, t)              # stone back to darkness
    interior-> pure COL_BG (the abyss)
```

Render at half-resolution to a surface, blit scaled up. Even 320x180 at
256 iterations looks stunning. Smooth iteration count (`mu = n - log2(log2(|z|))`)
eliminates banding.

### 2.3 Menu Elements Over Fractal

- Title text: rendered in the gold palette, slight glow bloom
- Buttons: semi-transparent dark panels, border color from `COL_GUI_BORDER`
- The fractal breathes behind everything — a living, infinite world waiting

### 2.4 Stretch: Julia Set Transitions

When player selects a difficulty, the fractal morphs from Mandelbrot to the
corresponding **Julia set** (using the menu's current center as `c`). This
creates a smooth, eerie transition from menu to game loading. Each difficulty
could have a signature Julia `c` value:
- Easy: `c = -0.4 + 0.6j` (smooth, flowing — Douady rabbit)
- Medium: `c = -0.8 + 0.156j` (more fractured, jagged)
- Hard: `c = -0.7269 + 0.1889j` (dendrite — maximally chaotic)

---

## 3. Units — Polar Roses & Parametric Warriors

### 3.1 Design Language

Units are drawn as **polar curve silhouettes** filled with color. Each unit
type has a signature polar equation that evokes its role:

### 3.2 Worker — The Hexagon Bee

Workers are the industrious backbone. Their shape is a **rounded hexagon**
generated from a polar superellipse:

```
r(theta) = 1 / (|cos(theta)|^n + |sin(theta)|^n)^(1/n)
    where n = 4 (squircle → hex feel)
```

Rotated 30 degrees so a flat edge faces "forward." The hex evokes honeycomb,
industry, tiling — things that build. When carrying resources, tiny satellite
circles orbit the hex (resource color, Fibonacci-spaced angles).

**Rank variants:**
- Novice: plain hex
- Foreman: hex with one inner concentric hex (self-similar)
- Master: two inner hexes + subtle rotation offset (moire shimmer)

### 3.3 Soldier — The Rose Shield

Soldiers project **force and defense**. Their shape is a **polar rose**:

```
r(theta) = cos(k * theta)
    where k = 3/2 (three-petaled, asymmetric — like a trefoil shield)
```

The three-petaled rose looks like a round shield with a triangular brace.
Filled with soldier red `(200, 60, 60)`. Oriented so one petal points forward
(direction of travel).

**Rank variants:**
- Recruit: k = 3/2 (3 petals)
- Veteran: k = 5/2 (5 petals — more ornate, bronze tint added)
- Corporal: k = 7/2 (7 petals — silver tint, smaller inner rose overlay)
- Sergeant: k = 4 (8 petals, gold, with a central dot — "star general")
- Captain: k = 5 (10 petals, diamond blue, double-layer rose)

Each rank adds petals — literally growing more formidable.

### 3.4 Archer — The Spiral Bow

Archers are defined by the **golden spiral** and its weaponization:

```
r(theta) = a * e^(b * theta)
    where b = 0.3063... (golden spiral: b = ln(phi) / (pi/2))
```

The archer's shape is two mirrored logarithmic spiral arcs forming a **bow
shape**, with a straight line (the arrow/string) bisecting them. The spiral
evokes both the curve of a longbow and the mathematical perfection of
Fibonacci in nature.

**Rank variants:**
- Recruit: single spiral bow outline
- Veteran: bow + one Fibonacci dot on each limb (bronze)
- Higher ranks: more Fibonacci dots along the spiral, arrow tip becomes
  a small Archimedean spiral

### 3.5 Enemy Variants

Enemy units use the SAME polar equations but with:
- **Inverted** rotation (petals point backward — retreating posture)
- **Jagged perturbation**: `r(theta) += noise * sin(17 * theta)` — they look
  corrupted, unstable, dangerous
- Colors: existing enemy palette (dark reds, purples, oranges)

The visual message: *same math, but twisted*.

---

## 3B. Unit Lifecycle Animations — Idle, Move, Fight, Fall

> *"A polar rose that never moves is just a diagram. One that breathes when
> idle, warps when running, flares when it strikes, and scatters when it
> dies — that's a warrior."*

### 3B.1 Design Philosophy

Phase 2 gave every unit a mathematical identity — a shape born from polar
equations. Phase 2.5 brings those shapes to life. Instead of frame-based
sprite animation, every visual change is a **parameter oscillation** — the
same math that drew the shape now *moves* it, by shifting the function's
inputs over time.

This is animation through mathematics, not through image sequences.

| State | Animates What | Math Mechanism |
|---|---|---|
| **Idle / Guard** | Shape breathes, gently alive | Slow radius + rotation oscillation |
| **Moving** | Shape leans forward, conveys speed | Directional squash, faster phase |
| **Attacking (melee)** | Shape lunges, projects violence | Radius spike + sharpness burst |
| **Shooting (ranged)** | Bow draws and releases | Limb flex + recoil spring |
| **Taking damage** | Shape shudders, absorbs blow | White flash + vertex noise |
| **Dying** | Shape disintegrates, returns to math | Petal shed / uncoil / fragment burst |
| **Fleeing** | Shape contracts, conveys fear | Shrink + accelerated wobble |

All animations share two principles:

1. **Parametric, not positional**: We don't animate pixel positions. We animate
   the *input parameters* of the polar equations — radius multiplier, rotation
   offset, sharpness exponent, perturbation amplitude. The shape redraws
   itself each frame from the mutated equation.

2. **Timers, not frames**: Every animation uses `game_time` (continuous float)
   and smooth interpolation (`sin`, `lerp`, `exp` decay). No discrete frame
   counts. Animations scale naturally with framerate.

### 3B.2 Universal Animation State Machine

Every unit carries a lightweight animation state alongside its gameplay state:

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

These timers are updated in `update()` (cheap — just float arithmetic) and
read during `draw()` to modulate shape parameters. Total overhead: ~6 floats
per unit.

### 3B.3 Universal Animation Effects

These apply to ALL unit types as a baseline layer:

#### 3B.3.1 Damage Flash (White Strobe)

When a unit takes damage, its entire shape briefly flashes toward white:

```
on take_damage:
    self._anim_flash = 1.0    # starts at full intensity

during draw:
    if _anim_flash > 0:
        flash_t = _anim_flash ** 2    # quadratic falloff (sharp start, soft end)
        draw_color = lerp(base_color, (255, 255, 255), flash_t * 0.7)
```

The flash peaks instantly and decays over ~120ms. The `0.7` cap prevents
pure white — even at maximum flash, a ghost of the unit's color remains so
you can still tell *what* got hit.

**Enemy variant**: Enemies flash toward `(200, 40, 40)` red instead of white,
reinforcing their threatening palette.

#### 3B.3.2 Idle Breathing (Radius Pulse)

All idle units have a gentle radius oscillation — the shape "breathes":

```
if state == "idle" or state == "guard":
    breath_t = sin(_anim_time * 1.8)          # ~0.55 Hz heartbeat
    radius_mult = 1.0 + 0.03 * breath_t       # +/- 3% radius shift
```

The 1.8 Hz frequency creates a slow, organic pulse — fast enough to feel
alive, slow enough to feel calm. Combined with per-unit `_anim_time` offsets,
a group of idle units breathes in staggered waves, never in lockstep.

#### 3B.3.3 Movement Lean (Directional Squash)

Moving units lean in their direction of travel. This is done by applying an
**elliptical distortion** to the polar radius:

```
if state == "moving":
    # compute movement angle from velocity
    move_angle = atan2(vy, vx)

    # during polar point generation, stretch radius along movement axis
    for each theta:
        angle_diff = theta - move_angle
        squash = 1.0 + 0.12 * cos(angle_diff)   # 12% stretch forward
        r_final = r(theta) * radius * squash
```

The effect: the shape elongates ~12% in the travel direction and compresses
~12% perpendicular to it. A moving soldier's rose becomes egg-shaped, leaning
into the run. A moving worker's hexagon leans forward like a bee in flight.

**Speed emphasis**: The squash factor scales with movement speed:
```
squash_amount = 0.08 + 0.04 * min(1.0, speed / max_speed)
```
Faster units lean harder. A nimble-trait unit visually "leans in" more.

#### 3B.3.4 Flee Contraction

Fleeing units (morale break or low HP) shrink and wobble:

```
if state == "fleeing":
    fear_t = sin(_anim_time * 8.0)      # fast 8 Hz tremor
    radius_mult = 0.85 + 0.05 * fear_t   # 15% smaller, 5% jitter
    rotation_offset += 0.03 * fear_t      # rotation wobble
```

The contracted, shivering shape instantly communicates "this unit is
panicking" without any UI overlay. The 8 Hz tremor is deliberately
uncomfortable — faster than the idle breathing, conveying agitation.

#### 3B.3.5 Death Dissolve (Universal Framework)

When `hp <= 0`, the unit doesn't vanish instantly. Instead, a death
animation plays over `0.6 seconds` before the entity is removed:

```
on death:
    self._anim_dying = True
    self._anim_death = 0.0
    self._death_seed = hash(id(self))  # deterministic dissolve pattern
    self.alive = False  # gameplay-dead immediately
    # entity stays in draw list for 0.6 sec

during death animation (_anim_death: 0.0 → 1.0):
    alpha_global = int(255 * (1.0 - _anim_death))
    # unit-type-specific dissolve (see below)
    # when _anim_death >= 1.0: remove from render list entirely
```

The gameplay state (`alive = False`) is set immediately — the unit stops
fighting, blocking, and targeting. But the *visual* persists for 0.6 seconds,
giving the death a sense of weight and finality.

---

### 3B.4 Worker — The Humming Hive

#### Idle: Hex Breathe + Inner Rotation

The worker's hex gently pulses, and its inner concentric hexes slowly
counter-rotate — the self-similar structure "hums" like a beehive:

```
radius_mult = 1.0 + 0.025 * sin(_anim_time * 1.8)
inner_rotation_offset = _anim_time * 0.15    # 0.15 rad/sec drift
inner2_rotation_offset = -_anim_time * 0.10   # counter-rotate
```

Workers with a primary skill have their skill-color hex border pulsing at a
slightly different frequency:
```
skill_border_alpha = 180 + int(40 * sin(_anim_time * 2.5))
```

This creates a subtle "glow pulse" on the colored border — the worker's
specialization is alive, not just painted on.

#### Moving: Waddle Bounce

Workers waddle when walking. The center point oscillates vertically:

```
if state == "moving":
    waddle_y = -abs(sin(_anim_time * 6.0)) * 2.0 * z   # 6 Hz bounce
    draw_y = sy + int(waddle_y)
    # hex rotation tilts slightly with each step
    rotation_offset = 0.04 * sin(_anim_time * 6.0)
```

The bounce creates a 6 Hz vertical hop — a bee-like bobbing motion. The
hex tilts alternately left-right with each hop cycle. Combined with the
directional squash from 3B.3.3, the worker looks like an industrious insect
scurrying across the battlefield.

**Carrying resources**: When `carry_amount > 0`, the waddle frequency drops
and amplitude increases (heavier load):
```
if carry_amount > 0:
    waddle_freq = 4.5       # slower pace
    waddle_amp = 3.0 * z    # bigger bounce — carrying is hard
    orbit_wobble = sin(_anim_time * 3.0) * 0.15  # orbiting dots sway
```

#### Gathering: Rhythmic Pulse

While gathering resources, the hex performs a rhythmic "dig" animation:

```
if state == "gathering":
    # hex compresses vertically on beat, like slamming a pickaxe
    gather_phase = (_anim_time * 2.5) % (2 * pi)
    if gather_phase < 0.4:  # quick compression pulse
        vertical_squash = 0.88   # 12% vertical compression
    else:
        vertical_squash = lerp(0.88, 1.0, (gather_phase - 0.4) / 1.5)  # slow recovery

    # inner hexes flash resource color on each pulse
    flash = 1.0 if gather_phase < 0.3 else 0.0
    inner_color = lerp(base_inner_color, resource_color, flash * 0.4)
```

The beat creates a rhythmic "thunk-thunk-thunk" visual — the hex slams
downward briefly then slowly recovers, like a mining impact.

#### Building: Spinning Industry

While constructing, inner hex rings spin rapidly:

```
if state == "building":
    inner_rotation = _anim_time * 1.2     # fast inner spin
    inner2_rotation = -_anim_time * 0.9    # counter-rotate even faster
    # outer hex stays stable — the structure, not the activity
    # tool sparkle: tiny point flashes at a random edge vertex each 0.3 sec
    if int(_anim_time / 0.3) != int((_anim_time - dt) / 0.3):
        sparkle_vertex = int(_anim_time * 7) % n_pts
        draw_small_flash(pts[sparkle_vertex], color=(240, 230, 200))
```

#### Taking Damage: Hex Shatter-Snap

On damage, worker hex vertices briefly scatter outward, then snap back:

```
on take_damage:
    _anim_flash = 1.0

during draw with _anim_flash > 0:
    for each vertex (x, y) in hex_pts:
        # push vertex outward from center by flash_t amount
        dx, dy = x - cx, y - cy
        explode_t = _anim_flash ** 3  # sharp snap, then slow settle
        x += dx * 0.15 * explode_t
        y += dy * 0.15 * explode_t
```

The hex briefly "shatters" outward by 15% then snaps back to shape. The
cubic falloff (`t^3`) makes it feel like a sudden blow followed by elastic
recovery — the hex absorbs the hit and reforms.

#### Dying: Honeycomb Dissolution

The worker's death dissolves its hex into separating hexagonal fragments:

```
death animation (0.0 → 1.0 over 0.6 sec):
    # split hex into 6 triangular wedges (center to each edge)
    for i in range(6):
        wedge_pts = [center, hex_pts[i*n//6], hex_pts[(i+1)*n//6]]

        # each wedge drifts outward + rotates
        drift_angle = (2 * pi * i / 6) + death_seed_offset[i]
        drift_dist = _anim_death * 20 * z
        wedge_offset_x = drift_dist * cos(drift_angle)
        wedge_offset_y = drift_dist * sin(drift_angle)
        wedge_rotation = _anim_death * 0.8  # gentle tumble

        # alpha fades: starts fading at 40%, fully gone at 100%
        alpha = int(255 * max(0, 1.0 - _anim_death * 1.6))

        draw_wedge(translated + rotated, color, alpha)
```

The hex breaks into six pie-slice wedges that drift apart while slowly
rotating. Each wedge fades independently. The effect: the hexagonal bee
dissolves back into its component tiles, as if the honeycomb came unglued.

**Skill-color afterglow**: If the worker had a visible skill border, the
last thing to fade is a faint ring in the skill color (alpha 40→0 over the
final 0.2 seconds) — a ghost of the worker's expertise lingering briefly.

---

### 3B.5 Soldier — The Pulsing Blade

#### Idle / Guard: Rose Rotation + Petal Breathe

The soldier's blade-rose slowly rotates and gently pulses:

```
idle_rotation = _anim_time * 0.3     # 0.3 rad/sec — stately rotation
radius_mult = 1.0 + 0.03 * sin(_anim_time * 2.0)  # slightly faster than worker

# guard stance: if attack target exists but out of range, rotation quickens
if state == "idle" and target_entity:
    idle_rotation = _anim_time * 0.8  # alert, faster spin
    radius_mult = 1.0 + 0.05 * sin(_anim_time * 3.0)  # more vigorous pulse
```

The guard-mode quickened rotation communicates "ready for combat" — the
soldier is vigilant, blade spinning faster. The inner rose (rank 2+)
counter-rotates at a different speed, creating a hypnotic moire:

```
inner_rotation = -_anim_time * 0.5  # counter-rotate inner rose
```

#### Moving: Forward Lean + Trail Ghosts

The soldier leans hard into movement, petal pointing forward:

```
if state == "moving":
    # align primary petal with movement direction
    target_rotation = move_angle - pi/2  # point leading petal forward
    current_rotation = lerp(current_rotation, target_rotation, 0.15)

    # directional squash: stretch 15% along travel axis
    squash_amount = 0.15
    # speed-dependent pulse: faster movement = faster petal "flutter"
    flutter = sin(_anim_time * 8.0) * 0.03  # subtle edge shimmer
    radius_mult = 1.0 + flutter
```

**Trail ghosts** (optional, for rank 3+): High-rank soldiers leave behind
1-2 fading afterimage copies, each 0.1 sec behind, at 30% and 15% alpha:

```
if rank >= 3 and state == "moving":
    for ghost_i, ghost_age in enumerate([0.10, 0.20]):
        ghost_alpha = int(60 * (1.0 - ghost_i * 0.5))
        ghost_x = sx - vx * ghost_age
        ghost_y = sy - vy * ghost_age
        draw_soldier_shape(ghost_x, ghost_y, r * 0.95, alpha=ghost_alpha)
```

High-rank soldiers leave blade-echoes behind them when charging.

#### Attacking: Lunge + Sharpness Spike

The melee attack is a two-phase animation — **lunge** then **retract**:

```
on attack_timer reset (attack lands):
    _anim_attack = 1.0    # triggers lunge

Phase 1 — LUNGE (attack_t: 1.0 → 0.5, ~90ms):
    # radius expands toward target
    lunge_dir = atan2(target.y - self.y, target.x - self.x)
    lunge_offset_x = 6 * z * attack_t * cos(lunge_dir)
    lunge_offset_y = 6 * z * attack_t * sin(lunge_dir)

    # sharpness increases (petal tips become needle-like)
    effective_sharpness = 0.6 - 0.3 * attack_t   # 0.6 → 0.3 (sharper)
    # radius briefly spikes
    radius_mult = 1.0 + 0.15 * attack_t

Phase 2 — RETRACT (attack_t: 0.5 → 0.0, ~90ms):
    # snap back to center position
    lunge_offset *= attack_t * 2  # retract to zero
    effective_sharpness = 0.6 - 0.3 * attack_t * 2  # restore normal
    radius_mult = 1.0 + 0.15 * attack_t * 2
```

The lunge physically moves the draw center 6px toward the target, while the
blade-rose petals sharpen to needle points (sharpness exponent drops from 0.6
to 0.3). The total effect: the soldier *stabs forward* with all petals
becoming daggers, then snaps back. Combined with the damage flash on the
target, melee combat becomes a rapid exchange of lunges and flashes.

**Berserker trait** amplifies the lunge: `lunge_distance = 9 * z` and
sharpness drops to 0.15 (pure spikes). Berserkers are visually frenzied.

#### Taking Damage: Petal Buckle

On hit, petals momentarily fold inward — the rose "buckles":

```
during _anim_flash > 0:
    # radius contracts briefly (hit absorption)
    radius_mult = 1.0 - 0.12 * (_anim_flash ** 2)
    # petals wobble: k parameter gets a brief perturbation
    effective_k = k + 0.3 * sin(_anim_time * 30) * _anim_flash
```

The k perturbation briefly disrupts the petal pattern — the shape flickers
between petal counts for a split second, as if the mathematical order was
momentarily broken by the impact. It's subtle but deeply unsettling at a
subconscious level — the shape's identity briefly destabilizes.

#### Dying: Petal Shed

The soldier's death scatters its petals one by one:

```
death animation (0.0 → 1.0 over 0.6 sec):
    n_petals = int(2 * k)   # number of visible petals
    shed_interval = 0.8 / n_petals  # stagger petal release

    for petal_i in range(n_petals):
        petal_birth = petal_i * shed_interval
        if _anim_death < petal_birth:
            # petal still attached — draw normally
            draw_petal_segment(petal_i, attached=True)
        else:
            # petal detached — drift outward, rotate, fade
            petal_age = _anim_death - petal_birth
            drift = petal_age * 30 * z
            tumble = petal_age * 2.5  # rotation
            alpha = int(255 * max(0, 1.0 - petal_age * 2.5))
            draw_detached_petal(petal_i, drift, tumble, alpha)

    # center dot (rank 3+) persists longest, fading last
    if rank >= 3:
        center_alpha = int(255 * max(0, 1.0 - _anim_death * 1.2))
        draw_center_dot(alpha=center_alpha)
```

Petals shed sequentially from outermost to innermost — the rose unravels.
Each detached petal becomes an independent drifting fragment, tumbling as it
fades. The center dot (for sergeants/captains) is the last element to vanish,
like the final heartbeat of the warrior.

**High-rank death**: Rank 3+ soldiers shed petals in a spiral pattern (each
petal drifts at a golden-angle offset from the previous), creating a brief
Fibonacci-like dissolution. Rank 4 captains get a final blue flash (their
rank color) on the center dot before it fades.

---

### 3B.6 Archer — The Flexing Bow

#### Idle: Limb Sway + String Tension

The archer's bow gently flexes — limbs oscillating in and out:

```
idle_flex = sin(_anim_time * 1.5) * 0.04  # 4% limb flex
top_limb_offset = idle_flex
bot_limb_offset = -idle_flex   # mirror: when top opens, bottom closes

# bowstring tension follows limb flex
string_x_offset = -idle_flex * r * 0.3   # string moves with flex
```

The limbs open and close in opposition, creating a "breathing bow" effect.
The bowstring shifts subtly with the flex, maintaining visual connection
between string and limbs. The arrow tip bobs gently (1px vertical sine):
```
arrow_y_offset = sin(_anim_time * 2.0) * 1.0 * z
```

Fibonacci dots on higher-rank bows pulse subtly:
```
dot_brightness = 0.8 + 0.2 * sin(_anim_time * 1.2 + dot_index * 0.7)
```

Each dot pulses at a slightly offset phase (golden-ratio-like stagger),
creating a cascading ripple effect along the bow limbs.

#### Moving: Bounce + Arrow Sway

Moving archers bounce like workers but with a distinct arrow-sway:

```
if state == "moving":
    bounce_y = -abs(sin(_anim_time * 5.0)) * 1.5 * z  # lighter bounce than worker
    # arrow sways opposite to bounce (inertia simulation)
    arrow_angle_offset = sin(_anim_time * 5.0) * 0.06  # subtle tilt
    # bow tilts forward along movement direction
    bow_tilt = 0.08   # slight forward lean
```

The arrow sways in counter-phase to the body bounce — when the archer bobs
up, the arrow tip dips down. This simple inertia simulation makes the arrow
feel like it has physical weight. The bow tilts forward, conveying purpose.

#### Shooting: Full Draw-Release Cycle

The firing animation is the archer's signature — a three-phase sequence
synchronized to `attack_timer`:

```
Phase 1 — NOCK (attack_timer: 100% → 70% of attack_cd):
    # bowstring pulls backward, arrow slides back
    string_draw = lerp(0, r * 0.25, nock_t)  # string retracts
    arrow_tail_x = lerp(normal_tail, pulled_tail, nock_t)
    # limbs start to spread (stored energy)
    limb_spread = 1.0 + 0.06 * nock_t

Phase 2 — HOLD (attack_timer: 70% → 15%):
    # full draw — maximum tension
    string_draw = r * 0.25    # bowstring fully pulled
    limb_spread = 1.06         # limbs at maximum flex
    # subtle tension vibration
    tremble = sin(_anim_time * 25) * 0.01 * (1.0 - hold_t)  # increases toward release
    string_draw += tremble * r

Phase 3 — RELEASE (attack_timer: 15% → 0%, arrow fires):
    # snap! bowstring flies forward, limbs snap inward
    release_t = 1.0 - (attack_timer / (attack_cd * 0.15))
    string_draw = r * 0.25 * (1.0 - release_t ** 0.5)  # fast snap (sqrt curve)
    limb_spread = 1.06 - 0.10 * release_t   # limbs overshoot inward

    # recoil: entire bow shifts backward briefly
    recoil_x = -3 * z * (1.0 - release_t)

    # arrow disappears from bow (now a projectile entity)
    draw_nocked_arrow = False

Aftermath — SETTLE (next 0.2 sec):
    # limbs oscillate back to rest (damped spring)
    settle_t = min(1.0, time_since_release / 0.2)
    limb_spread = 1.0 + 0.04 * sin(settle_t * pi * 3) * (1.0 - settle_t)
    string_x = normal_x + 2 * sin(settle_t * pi * 4) * (1.0 - settle_t)
```

The full draw-hold-release cycle creates a satisfying archery rhythm:
steady pull, tense hold with growing tremble, then explosive snap. The
limb overshoot on release (narrowing past rest position) and damped
spring settle are the key "feel" details — without them the release looks
mechanical rather than physical.

**Sharpshooter trait**: The hold phase has reduced tremble (amplitude * 0.3)
— sharpshooter archers are visibly steadier.

#### Taking Damage: String Vibration

On hit, the bowstring vibrates rapidly:

```
during _anim_flash > 0:
    string_x_offset = sin(_anim_time * 50) * 3 * z * _anim_flash
    # the WHOLE bow vibrates (high-freq micro-shake)
    draw_x += sin(_anim_time * 35) * 1.5 * z * _anim_flash
    draw_y += cos(_anim_time * 41) * 1.0 * z * _anim_flash
```

The bowstring visibly thrums (50 Hz oscillation) while the entire bow
shakes at a different frequency (35/41 Hz Lissajous). The message: the bow
absorbed an impact and is ringing like a struck instrument.

#### Dying: Bow Uncoils

The archer's death unwinds the golden spiral back to its mathematical origin:

```
death animation (0.0 → 1.0 over 0.6 sec):
    # spiral uncoils: reduce the theta range of each limb
    effective_theta_range = (1.0 - _anim_death) * normal_theta_range
    # as theta range shrinks, the spiral collapses toward its seed point

    # bowstring snaps at 20% death progress
    if _anim_death > 0.2:
        string_break_t = (_anim_death - 0.2) / 0.3
        # string splits into two halves that curl away
        top_string_curl = string_break_t * 0.5  # curl upward
        bot_string_curl = -string_break_t * 0.5  # curl downward
        string_alpha = int(255 * max(0, 1.0 - string_break_t * 2))

    # arrow drops and falls (if still nocked)
    arrow_fall_y = _anim_death * 15 * z
    arrow_rotation = _anim_death * 1.2  # tumble as it falls

    # Fibonacci dots shed outward (golden angle spiral)
    for dot_i, dot in enumerate(fib_dots):
        dot_shed_time = 0.3 + dot_i * 0.1
        if _anim_death > dot_shed_time:
            dot_drift = (_anim_death - dot_shed_time) * 25 * z
            dot_angle = golden_angle * dot_i  # spiral outward
            dot_alpha = fading...

    # overall alpha fade
    alpha = int(255 * max(0, 1.0 - _anim_death * 1.5))
```

The bow uncoils from its full spiral back to nothing — the golden ratio
unwinding. The string snaps and curls. Fibonacci dots spiral outward along
golden-angle trajectories (visually satisfying). The arrow tumbles and falls.
The message: the mathematical beauty that defined the archer is *reversing*,
the equation returning to zero.

---

### 3B.7 Siege — The Grinding Engine

#### Idle: Spike Pulse + Inner Rotation

The siege unit idles with a menacing mechanical throb:

```
radius_mult = 1.0 + 0.04 * sin(_anim_time * 1.2)  # slow, heavy pulse
inner_gear_rotation = _anim_time * 0.4   # inner polygon rotates slowly
spike_emphasis = 1.0 + 0.06 * abs(sin(_anim_time * 0.8))  # spikes grow/shrink
```

The inner gear polygon rotates independently from the outer spike ring,
creating a "loaded weapon" impression — machinery ready to fire.

#### Moving: Rolling Advance

The entire siege shape rotates slowly in the movement direction:

```
if state == "moving":
    body_rotation += dt * 0.5   # slow roll — it's heavy
    # vertical bob: heavier, slower than unit bob
    bob_y = sin(_anim_time * 2.5) * 1.5 * z  # 2.5 Hz, slow and heavy
```

The whole spike polygon rolls like a wheel, communicating weight and
mechanical inevitability. The bob is slower and heavier than infantry.

#### Attacking: Spike Extend

On attack, spikes extend outward sharply:

```
on attack:
    _anim_attack = 1.0

during attack animation:
    spike_mult = 1.0 + 0.35 * _anim_attack ** 2   # 35% spike extension
    inner_flash = _anim_attack * 0.6    # inner gear flashes bright
    # directional: spike closest to target extends most
    for each spike_i:
        spike_angle = spike_theta(spike_i)
        angle_to_target = atan2(target.y - self.y, target.x - self.x)
        alignment = max(0, cos(spike_angle - angle_to_target))
        spike_extra = alignment * 0.2 * _anim_attack  # targeted spike extends more
```

The spike facing the target extends furthest, like a battering ram impact.

#### Dying: Implosion

Siege units die by collapsing inward — the opposite of soldier petal-shed:

```
death animation (0.0 → 1.0 over 0.8 sec):  # longer death — it's a big unit
    # spikes retract inward
    spike_mult = 1.0 - _anim_death * 0.8  # spikes shrink to stubs
    body_radius = radius * (1.0 - _anim_death * 0.7)

    # at 60%, inner gear flies apart (3-4 fragments outward)
    if _anim_death > 0.6:
        fragment_t = (_anim_death - 0.6) / 0.4
        for frag_i in range(4):
            frag_angle = 2 * pi * frag_i / 4 + death_seed_offset
            frag_drift = fragment_t * 20 * z
            # small dark triangles — broken machinery
            draw_fragment(frag_angle, frag_drift, alpha=fading)

    # final collapse: everything snaps to center point
    if _anim_death > 0.85:
        # brief bright flash at center (the engine explodes)
        flash_alpha = int(200 * (1.0 - (_anim_death - 0.85) / 0.15))
        draw_circle(center, r * 0.3, (200, 100, 20, flash_alpha))
```

The siege engine collapses like a dying star — spikes retract, body shrinks,
inner gear fragments fly outward, then a final bright flash at the center
as the whole thing implodes. Heavy and dramatic, matching the unit's
battlefield presence.

---

### 3B.8 Elite — The Unstable Star

#### Idle: Counter-Rotating Rose Orbit

The elite's dual roses counter-rotate continuously, creating mesmerizing
interference patterns:

```
outer_rotation = _anim_time * 0.25   # outer rose: slow clockwise
inner_rotation = -_anim_time * 0.35   # inner rose: faster counter-clockwise
center_glow_radius = max(2, r // 5) + sin(_anim_time * 3.0) * 1.5 * z
center_glow_alpha = 160 + int(60 * sin(_anim_time * 2.0))
```

The two roses at different speeds create continuously shifting patterns.
The central glow pulses with a heartbeat rhythm. The overall impression:
a dangerous, barely-contained energy source.

#### Moving: Rose Alignment

When moving, both roses align to point forward — the chaotic idle pattern
becomes focused, predatory:

```
if state == "moving":
    target_rotation = move_angle - pi/2
    outer_rotation = lerp(outer_rotation, target_rotation, 0.2)
    inner_rotation = lerp(inner_rotation, target_rotation + pi, 0.15)
    # roses "lock" into parallel alignment
    center_glow_alpha = 220  # brighter — focused energy
```

The transition from chaotic idle rotation to aligned forward motion
communicates intent — the elite has chosen a target and is closing in.

#### Attacking: Aura Expansion

On attack, the outer rose expands while the inner contracts:

```
on attack:
    _anim_attack = 1.0

during attack:
    outer_radius = r * (0.95 + 0.25 * _anim_attack)  # outer expands 25%
    inner_radius = r * (0.55 - 0.15 * _anim_attack)  # inner contracts
    center_glow = max(3, r // 3) * (1.0 + 0.5 * _anim_attack)  # glow swells
    # brief jagged halo flare
    halo_radius = r * (1.05 + 0.15 * _anim_attack)
```

The outer rose swells like a shockwave while the inner collapses — energy
being expelled outward. The halo ring flares. Combined effect: the elite
detonates its aura at the target.

#### Dying: Binary Fission

The elite's death splits its two roses apart — a mathematical cell division:

```
death animation (0.0 → 1.0 over 0.7 sec):
    # two roses separate along a random axis
    split_angle = death_seed * 2 * pi / 1000
    split_dist = _anim_death * 35 * z

    outer_cx = cx + split_dist * cos(split_angle)
    outer_cy = cy + split_dist * sin(split_angle)
    inner_cx = cx - split_dist * cos(split_angle)
    inner_cy = cy - split_dist * sin(split_angle)

    # each rose continues spinning but decaying
    outer_radius = r * 0.95 * (1.0 - _anim_death * 0.7)
    inner_radius = r * 0.55 * (1.0 - _anim_death * 0.6)

    # center glow splits into two dimming points
    glow_alpha = int(180 * (1.0 - _anim_death * 1.3))

    # at 80%, both roses dissolve into scattered points
    if _anim_death > 0.8:
        # each rose becomes a cloud of fading dots (rose → particle cloud)
        for i in range(8):
            dot_angle = 2 * pi * i / 8 + death_seed
            dot_drift = (_anim_death - 0.8) * 40 * z
            draw_dot(center + drift, alpha=fading)
```

The two roses tear apart like binary fission — each half carrying away part
of the elite's identity. They continue spinning as they separate, shrinking
and dimming, before dissolving into scattered point-particles. The
mathematical compound structure literally decomposes into its components.

---

### 3B.9 Implementation Details

#### 3B.9.1 Animation Timer Management

All animation timers live on the Unit instance. Initialize in `__init__`:

```python
# Animation state (visual only — no gameplay impact)
self._anim_time = random.uniform(0, 10.0)   # stagger idle phase
self._anim_flash = 0.0    # damage flash (1.0 → 0.0 over 0.12s)
self._anim_attack = 0.0   # attack lunge (1.0 → 0.0 over 0.18s)
self._anim_dying = False   # death sequence active
self._anim_death = 0.0    # death progress (0.0 → 1.0 over 0.6s)
self._death_seed = 0       # deterministic death pattern
```

Update in `update()`:
```python
self._anim_time += dt
self._anim_flash = max(0, self._anim_flash - dt / 0.12)
self._anim_attack = max(0, self._anim_attack - dt / 0.18)
if self._anim_dying:
    speed = 1.0 / 0.6   # 0.6 sec death (0.8 for siege)
    self._anim_death = min(1.0, self._anim_death + dt * speed)
```

Trigger points:
```python
# in take_damage():
self._anim_flash = 1.0

# in _do_attack() when attack lands:
self._anim_attack = 1.0

# when hp <= 0:
self._anim_dying = True
self._death_seed = hash(id(self)) % 10000
```

#### 3B.9.2 Draw Integration

The `draw()` method reads animation state and passes modifiers to the shape
draw functions. No new surfaces or caching needed — the shape functions
simply receive modified parameters:

```python
def draw(self, surf, cam):
    ...
    # compute animation modifiers
    radius_mult = 1.0
    rotation_offset = 0.0
    offset_x, offset_y = 0, 0
    sharpness_mod = 0.0
    squash_dir = None
    squash_amount = 0.0
    alpha = 255

    if self._anim_dying:
        # death animation overrides everything
        alpha = int(255 * max(0, 1.0 - self._anim_death * 1.6))
        ... unit-type-specific death
    else:
        # living animation layers
        if state == "idle":
            radius_mult += 0.03 * sin(self._anim_time * 1.8)
        if state == "moving":
            ... lean + bounce
        if self._anim_flash > 0:
            ... flash overlay
        if self._anim_attack > 0:
            ... lunge offset

    # pass modifiers to shape draw
    r = int(base_r * radius_mult)
    sx += offset_x
    sy += offset_y
    self._draw_shape(surf, sx, sy, r, z, ...)
```

#### 3B.9.3 Performance Budget

| Component | Per-Unit Cost | Notes |
|---|---|---|
| Timer updates | 4 float ops | In `update()`, negligible |
| Idle breath | 1 `sin` call | ~0 cost |
| Move lean | 1 `atan2` + 1 `cos` per vertex | Absorb into existing polar loop |
| Attack lunge | 2 `cos/sin` + lerps | Only on attacking units |
| Damage flash | 1 color lerp | Only on recently-hit units |
| Death dissolve | N fragments × transform | Only on dying units (rare, brief) |
| Trail ghosts | 1-2 extra shape draws | Rank 3+ soldiers only while moving |

Worst case: 200 units all simultaneously fighting = ~200 extra sin/cos calls
per frame. At 60 FPS on modern CPU this is **< 0.5ms** — well within budget.

Death dissolves involve extra draw calls but affect at most 5-10 units
simultaneously (death is brief). Trail ghosts are the most expensive effect
(extra shape draws) but are limited to rank 3+ soldiers while moving.

#### 3B.9.4 Enemy Animation Corruption

Enemy units use the same animation system but with parameter corruption:

```
# Enemy-specific modifiers applied on top of base animation
if is_enemy:
    # idle breathing is irregular (two competing frequencies)
    breath = sin(_anim_time * 1.8) * 0.5 + sin(_anim_time * 2.7) * 0.5
    radius_mult = 1.0 + 0.04 * breath  # slightly larger amplitude

    # movement lean is more aggressive (18% instead of 12%)
    squash_amount *= 1.5

    # attack lunge extends 20% farther
    lunge_distance *= 1.2

    # death dissolve is faster (0.4 sec instead of 0.6)
    death_speed = 1.0 / 0.4

    # jagged border perturbation increases during attack
    jagged_amplitude = base_jagged * (1.0 + 0.3 * _anim_attack)
```

The enemy's irregular breathing (two competing sine waves) creates a subtly
unsettling rhythm — the corrupted math made manifest. Their more aggressive
lean, longer lunge, and faster death reinforce the "same but twisted" theme
from Section 3.5.

#### 3B.9.5 Trait-Modified Animations

Traits from the v10_1 trait system modify animation parameters:

| Trait | Animation Effect |
|---|---|
| **Brave** | Idle pulse amplitude +50% (confident, large presence) |
| **Cowardly** | Idle pulse faster (+30% freq), smaller amplitude (nervous) |
| **Aggressive** | Attack lunge distance +30%, faster retract |
| **Cautious** | Slower idle rotation, minimal movement lean |
| **Berserker** | Below 50% HP: sharpness permanently spiked, no settle |
| **Nimble** | Movement bounce amplitude +40%, faster flutter |
| **Inspiring** | Center dot/glow pulses brighter (rank 3+ aura visible to allies) |
| **Lone Wolf** | No trail ghosts even at high rank (solitary aesthetic) |
| **Sharpshooter** | Archer hold-phase tremble reduced 70% (steady hands) |

These are simple parameter multipliers — no new animation logic needed.

---

## 4. Buildings — L-System Fortresses

### 4.1 Design Language

Buildings are drawn as **L-system branching patterns** bounded within their
tile footprint. An L-system is a recursive string-rewriting grammar that
produces tree-like or crystalline structures — perfect for "things that are
built."

### 4.2 Town Hall — The Branching Tree

The town hall is the root of your civilization. Its shape is a **symmetric
L-system tree** that fills a 2x2 tile square:

```
Axiom: F
Rules: F -> FF+[+F-F-F]-[-F+F+F]
Angle: 22.5 degrees
Iterations: 4 (grows during construction, 1 iter per 25% built)
```

This produces a bushy, symmetric canopy — a great tree sheltering your base.
Trunk color: `(139, 90, 43)` brown. Canopy tips: fade toward `(46, 139, 87)`
green.

**Construction animation**: The L-system starts at iteration 0 (a single line)
and adds one iteration each quarter of build progress. The building literally
*grows*.

**Ruin state**: Iterations drop back to 1, color desaturates to gray. The
tree is reduced to a stump.

### 4.3 Barracks — The Crystal Lattice

Military buildings are rigid, orderly, aggressive. The barracks uses a
**Sierpinski-adjacent triangle lattice**:

```
Start with an equilateral triangle filling the tile
Subdivide into 4 smaller triangles, remove the center
Repeat to depth 3
```

The result is a geometric, fortress-like pattern — triangles within triangles,
evoking sharpness and military precision. Color: `(140, 45, 45)` maroon.

**Construction**: Depth increases with build progress (depth 0 = solid
triangle, depth 3 = full Sierpinski).

### 4.4 Refinery — The Gear Spiral

The refinery transforms raw into refined. Its shape is a **gear-like
epitrochoid** (the math behind a Spirograph):

```
x(t) = (R + r) * cos(t) - d * cos((R + r) / r * t)
y(t) = (R + r) * sin(t) - d * sin((R + r) / r * t)
    where R = 5, r = 3, d = 5 (produces a star-gear with cusps)
```

The cusps look like gear teeth. When refining is active, the parameter `t`
range slowly rotates — the gear turns. Color: `(100, 100, 130)` blue-gray
with `(100, 160, 220)` steel-blue highlights on the cusps.

### 4.5 Tower — The Koch Battlement

Towers defend with fractal precision. The tower shape is a **Koch snowflake**
(or partial Koch curve applied to a square base):

```
Start with a square
Apply Koch curve subdivision to each edge:
    replace middle third with equilateral triangle bump
Repeat to depth 2-3
```

The result: a castle battlement shape with increasingly detailed crenellations.
The fractal edge literally creates the jagged defensive profile of a medieval
tower.

**Level 1 (Cannon)**: Koch depth 2, stone color `(160, 160, 140)`
**Level 2 (Explosive)**: Koch depth 3, orange accent on tips `(255, 140, 40)`

---

## 4B. Building Lifecycle Fractals — Damage, Ruin & Repair

> *"A fractal doesn't just appear — it grows, it weathers, it breaks, and
> it heals. The same math that built the fortress now tells the story of
> every blow it absorbed and every stone that was laid to restore it."*

### 4B.1 Design Philosophy

Phase 3 gave buildings their construction growth animations — fractals that
bloom from nothing as workers build. Phase 3.5 completes the lifecycle: what
happens when those fractals are **hit**, when they **fall**, and when they
**rise again**. Every building has three additional visual states layered onto
the base shape:

| State | Trigger | Visual Effect |
|---|---|---|
| **Healthy** | `hp == max_hp` | Full fractal, bright colors, active animation |
| **Damaged** | `hp < max_hp` | Progressive degradation interpolated by HP ratio |
| **Ruined** | `hp == 0, ruined=True` | Collapsed fractal, debris, desaturated palette |
| **Repairing** | Worker assigned, `build_progress` rising | Restoration glow, regrowth animation |

The key insight: **damage is not a switch, it's a gradient**. A building at
75% HP looks subtly worn. At 30% HP it's visibly crumbling. At ruin it's
a skeleton of its former self. And repair reverses the decay with its own
distinct visual language — not just "construction in reverse" but a
restoration that shows the scars of what happened.

### 4B.2 Universal Damage Language

These effects apply to ALL building types as a baseline:

#### 4B.2.1 Color Desaturation Gradient

As HP drops, building colors shift along a desaturation curve:

```
damage_ratio = 1.0 - (hp / max_hp)

For each color channel (R, G, B):
    gray = 0.299*R + 0.587*G + 0.114*B          # luminance
    damaged_c = lerp(original_c, gray, damage_ratio * 0.6)
```

At full HP the building is vivid. At 50% HP it's noticeably muted. At ruin
(10% HP) it's nearly monochrome. The `0.6` cap prevents total gray — even
ruins retain a ghost of their original hue.

#### 4B.2.2 Damage Shake (Micro-Tremor)

When a building takes a hit, its draw position gets a brief offset:

```
on_hit:
    shake_timer = 0.15 sec
    shake_amplitude = 3px * (damage / max_hp)    # bigger hits = bigger shake

during shake_timer > 0:
    draw_offset_x = shake_amplitude * sin(time * 40)  # fast oscillation
    draw_offset_y = shake_amplitude * cos(time * 53)   # slightly different freq
    shake_timer -= dt
    shake_amplitude *= 0.85                            # rapid decay
```

The two different frequencies (40 and 53 Hz) create a Lissajous-like micro-
orbit instead of a simple left-right jitter. The building "shudders" in a
figure-eight pattern that damps out in ~150ms.

#### 4B.2.3 Crack Lines (Universal)

Below 60% HP, thin dark lines appear on the building's foundation:

```
n_cracks = int((1.0 - hp_ratio) * 5)    # 0 at full, up to 3 at ruin
crack_seed = building_id * 7919          # deterministic per building

for each crack:
    # Seeded random walk from building edge toward center
    start = random_point_on_edge(seed)
    for segment in range(3 + crack_index):
        angle = seeded_noise(segment) * pi/3   # jagged, not straight
        draw_line(dark_color, start, start + polar(angle, length))
        start += polar(angle, length)
```

Cracks are deterministic (same seed = same pattern) so they don't flicker.
New cracks appear as HP drops but existing ones never move. Color: `(8, 5, 3)`
near-black with 1px width.

#### 4B.2.4 Damage Particle Debris

Below 40% HP, small fragments drift downward from the building:

```
n_particles = int((1.0 - hp_ratio) * 4)   # 0-2 particles active

each particle:
    shape: tiny triangle (3-5px), color from building palette (darkened)
    motion: slow fall (20px/sec) + sine drift (amplitude 5px, period 2sec)
    lifetime: 1.5 sec, then respawn at random building edge
    alpha: fades from 180 to 0 over lifetime
```

These are purely cosmetic — lightweight falling debris that communicate
"this building is in trouble" without any gameplay impact.

---

### 4B.3 Town Hall — The Dying & Reborn Tree

#### Damage: Autumn Decay

The L-system tree transitions through seasons as it takes damage:

```
hp_ratio > 0.75:  SUMMER — full green canopy, 4 iterations
hp_ratio > 0.50:  AUTUMN — tip color shifts green→amber→brown
                   Random 20% of terminal branches drawn shorter (pruned)
hp_ratio > 0.25:  LATE AUTUMN — tip color brown/gray, 40% branches pruned
                   Trunk color darkens: (139,90,43) → (80,50,25)
                   Iteration count drops to 3
hp_ratio ≤ 0.25:  WINTER — all tips gray, 60% branches pruned
                   Iteration count drops to 2
                   Trunk rendered with slight wobble (damage shake persists)
```

**Branch pruning** works by adding a `prune_mask` based on the building's
HP history. During L-system rendering, each `[` (branch start) has a
deterministic probability of being skipped:

```
prune_threshold = (1.0 - hp_ratio) * 0.6
for each branch_start '[':
    branch_hash = hash(branch_index + building_id)
    if (branch_hash % 1000) / 1000.0 < prune_threshold:
        skip to matching ']'   # entire sub-branch vanishes
```

The hash ensures the SAME branches prune at the same HP level — no flickering.
As HP drops, more branches fail the check and disappear.

**Leaf fall particles**: Below 50% HP, 1-3 tiny circles (3px, green fading
to amber) slowly spiral downward from the canopy using a damped pendulum:

```
x(t) = start_x + amplitude * sin(omega * t) * exp(-0.5 * t)
y(t) = start_y + fall_speed * t
color = lerp(green, amber, t / lifetime)
```

#### Ruin: The Charred Stump

When the town hall enters ruin state:

- Iteration count locked to **1** (single trunk + one branch pair)
- All colors shift to charcoal: trunk `(30, 20, 12)`, tips `(15, 12, 8)`
- A thin **smoke wisp** rises from the stump:

```
smoke: 3-4 small circles (6-10px), alpha 40-80
  y_drift: -15 px/sec (upward)
  x_drift: sin(time * 0.8 + offset) * 8px  (gentle sway)
  alpha_decay: loses 30 alpha/sec
  respawn at stump top when alpha hits 0
  color: (60, 55, 50) gray-brown
```

- Two short "ember" dots (2px, orange `(200, 80, 20)`) flicker at the
  trunk base with randomized alpha pulsing.

#### Repair: Spring Regrowth

When a worker begins repairing the ruined town hall:

- `build_progress` drives iteration count back up (same as original
  construction) BUT with a distinct **regrowth shimmer**:

```
during repair:
    tip_color = lerp(charcoal_gray, bright_spring_green, build_progress)
    spring_green = (60, 200, 70)   # brighter than normal (30, 110, 50)

    # New growth flash: freshly appearing branches pulse briefly
    if branch_just_appeared(this_iteration):
        tip_glow = lerp(spring_green, (150, 255, 120), pulse_t)
        pulse_t decays from 1.0 to 0.0 over 0.8 sec
```

- Smoke particles fade out as build_progress exceeds 25%
- Ember dots extinguish at 15% build_progress
- At 100% (fully repaired), one final "bloom" pulse: all tips flash
  bright green for 0.3 seconds, then settle to normal summer colors

The message: *the tree doesn't just rebuild — it blooms back to life*.

---

### 4B.4 Barracks — The Shattering & Reforging Lattice

#### Damage: Fracture Propagation

The Sierpinski triangle degrades through geometric disintegration:

```
hp_ratio > 0.75:  INTACT — full depth 4, crisp colors
hp_ratio > 0.50:  STRESSED — outermost sub-triangles at depth 4 get a
                   random offset (jitter 2-3px), creating a "cracked glass" look
                   Border color dims
hp_ratio > 0.25:  FRACTURING — depth drops to 3
                   Some leaf triangles (depth 0) drawn as outlines instead of
                   filled (random 30% based on building_id seed)
                   Color shifts maroon→dark brown
hp_ratio ≤ 0.25:  CRUMBLING — depth drops to 2
                   50% of leaf triangles are outlines
                   Main border flickers (alpha oscillates 120-200)
```

**Fragment jitter** at the leaf level creates the "broken stained glass"
effect. Each depth-0 triangle gets a per-vertex offset:

```
for each leaf_triangle vertex (x, y):
    jitter_seed = hash(vertex_index + building_id + damage_epoch)
    if hp_ratio < 0.5:
        offset_x = seeded_random(-3, 3) * (1.0 - hp_ratio)
        offset_y = seeded_random(-3, 3) * (1.0 - hp_ratio)
        draw_vertex = (x + offset_x, y + offset_y)
```

The `damage_epoch` increments each time the building takes a hit, causing
a brief visual "settle" — fragments shift to new positions on impact, then
hold steady until the next hit.

**Debris triangles**: Below 40% HP, 1-2 tiny triangles (4-6px) fall from the
structure. Same shape as the Sierpinski sub-triangles but darker, rotating
slowly as they fall.

#### Ruin: The Broken Frame

- Only the **outer equilateral border** remains, drawn as a dashed line
  (alternating 6px segments and 4px gaps)
- 3-5 **scattered fragment triangles** rest at the base of the building,
  drawn as small filled triangles in dark maroon, slightly rotated:

```
for i in range(n_fragments):
    frag_x = cx + seeded_offset_x(i) * half_size * 0.6
    frag_y = cy + half_size * 0.3 + seeded_offset_y(i) * 10
    frag_size = 4 + (i % 3) * 2
    frag_angle = seeded_angle(i)
    draw_rotated_triangle(surf, frag_x, frag_y, frag_size, frag_angle,
                          color=(50, 15, 15))
```

- The interior is empty — a visible void where the lattice once was
- Overall desaturated: maroon → `(50, 20, 20)` ash-brown

#### Repair: Crystallization Wave

Repairing the barracks plays the Sierpinski recursion in reverse, but
with a distinctive **crystal growth** effect:

```
during repair:
    effective_depth = int(build_progress * 4 + 0.5)  # same as construction

    # Crystallization front: newly formed triangles at the current depth
    # flash bright before settling to normal color
    for each newly_appearing_triangle:
        flash_color = (220, 100, 100)   # bright red flash
        flash_alpha = lerp(255, 0, local_age / 0.5)  # 0.5 sec decay
        draw_triangle(color=lerp(flash_color, target_color, local_age / 0.5))
```

- Scattered ruin fragments "lift" back toward the structure (reverse gravity
  during first 20% of repair progress) then disappear
- The dashed border becomes solid first (at 10% progress), establishing the
  frame before internal detail regrows
- Border color restores last (at 90% progress) — from dim to full brightness

---

### 4B.5 Refinery — The Grinding Halt & Restart

#### Damage: Wobble & Stutter

The Spirograph gear degrades through mechanical failure:

```
hp_ratio > 0.75:  RUNNING — smooth rotation, all cusps lit
hp_ratio > 0.50:  STUTTERING — rotation speed becomes irregular:
                   rotation_speed = base_speed * (0.5 + 0.5 * sin(time * 3))
                   This creates a "grinding" rhythm — fast-slow-fast
                   1-2 cusp highlight dots go dark (steel-blue → gray)
hp_ratio > 0.25:  SEIZING — rotation nearly stops (speed * 0.2)
                   Heavy wobble added to curve:
                     perturbation = sin(13 * t + time * 5) * 3px * (1 - hp_ratio)
                   50% of cusp dots dark, remaining ones flicker
                   Curve color shifts to dull brown-gray
hp_ratio ≤ 0.25:  FAILING — rotation frozen (speed = 0)
                   Perturbation amplitude maxed out — curve looks bent/warped
                   All cusp dots dark except 1 that flickers weakly
                   Occasional "spark" particle (bright yellow-white, 2px,
                     fast radial burst outward then fades, 0.2 sec lifetime)
```

**Wobble perturbation** is added to the epitrochoid parametric equations:

```
damage_wobble = (1.0 - hp_ratio) * 0.15  # max 15% radius perturbation
x(t) = (R+r)*cos(t) - d*cos((R+r)/r*t) + damage_wobble * sin(13*t + phase)
y(t) = (R+r)*sin(t) - d*sin((R+r)/r*t) + damage_wobble * cos(17*t + phase)
```

The frequencies 13 and 17 (primes) ensure the wobble pattern never repeats
cleanly, making the curve look organically damaged rather than just rescaled.

**Spark particles**: Below 25% HP, periodic sparks emitted from random cusps:

```
every 0.8-1.5 sec (random interval):
    pick random cusp point
    emit 2-3 tiny dots (2px) in random radial directions
    speed: 40-80 px/sec, lifetime: 0.15-0.25 sec
    color: (255, 240, 100) → (200, 100, 20) over lifetime
    → communicates "machinery grinding, throwing sparks"
```

#### Ruin: The Broken Gear

- Spirograph curve collapses to a **simple circle** (R+r radius) drawn as a
  thin dashed line — the gear has lost its teeth
- 4-6 **scattered cusp dots** rest below the circle at random positions,
  colored dark gray `(40, 40, 50)` — fallen gear teeth
- No rotation, no animation — the machine is dead
- A single faint circle outline in `(30, 30, 40)` where the gear used to be
- Overall palette: everything shifted to near-monochrome gray

#### Repair: The Restart Sequence

Repairing the refinery is a **mechanical restart** with a satisfying
spin-up sequence:

```
Phase 1 (0-20% progress):
    Scattered cusp dots "magnetically" pull back toward their positions
    on the circle. Simple lerp from rest position to cusp position.
    Circle transitions from dashed to solid.

Phase 2 (20-60% progress):
    Spirograph curve re-emerges from the circle, gaining complexity:
    effective_max_t = build_progress * 6 * pi   (curve grows like construction)
    Rotation begins: very slow, jerky (speed * 0.1 with stutter)
    Cusp dots begin relighting one by one (every ~8% progress)

Phase 3 (60-90% progress):
    Full curve restored. Rotation accelerates smoothly:
    speed = base_speed * smoothstep(0.6, 0.9, build_progress)
    Wobble perturbation decreases: amplitude = (1.0 - build_progress) * 0.15
    Colors transition from gray back to blue-gray → steel-blue

Phase 4 (90-100% progress):
    Final "ignition" — all cusp dots flash bright simultaneously
    Rotation reaches full speed
    One brief burst of 5-6 spark particles (celebratory, not damaged)
    Colors snap to full saturation
```

The restart sequence mirrors real machinery coming back online — hesitant at
first, then building confidence until it's humming at full speed.

---

### 4B.6 Tower — The Crumbling & Rebuilt Battlement

#### Damage: Edge Erosion

The Koch snowflake loses its fractal detail from the outside in:

```
hp_ratio > 0.75:  FORTIFIED — full Koch depth, crisp edges
                   Lv.2 orange glow dots fully bright
hp_ratio > 0.50:  WEATHERED — Koch depth drops by 1 for the outermost
                   recursion level only. Inner structure retains full depth.
                   This is achieved by passing `depth - 1` to the outer edges
                   while keeping `depth` for the inner:
                     effective_depth = base_depth  (inner Koch preserved)
                     outer_edge_depth = base_depth - 1  (edges simplify first)
                   1-2 Lv.2 glow dots dim to half brightness
hp_ratio > 0.25:  CRUMBLING — full depth drops by 1 globally
                   "Rubble rectangles" appear at base: 2-3 tiny filled
                   rectangles (3x5px) in stone color, slightly offset
                   Border line becomes thinner (1px instead of 2)
                   Lv.2 glow dots: half extinguished, rest flicker
hp_ratio ≤ 0.25:  BREACHED — depth drops by 2 total (minimum depth 1)
                   Fill color darkens heavily
                   One visible "breach" — a V-shaped notch cut from one edge:
                     pick one edge (deterministic by building_id)
                     replace Koch points along 20% of that edge with a
                     concave dent (inward triangle instead of outward)
                   All Lv.2 glow dots extinguished
                   4-5 rubble rectangles at base
```

**The breach notch** is the signature damage tell for towers. It's achieved
by modifying the Koch curve generation for one segment:

```
for the chosen edge's middle third:
    instead of: outward equilateral bump (Koch normal)
    generate: inward equilateral dent (mirror the bump direction)
    → creates a visible "V" in the wall where something punched through
```

The breach is deterministic per building (same edge every time, same location).
This means players can visually identify which towers are critically damaged
at a glance.

#### Ruin: The Rubble Mound

- Koch depth forced to **0** — just the base triangle, no fractal detail
- Fill color: desaturated `(50, 50, 45)` dark stone
- The triangle is drawn **partially open**: one vertex is offset inward,
  making it look collapsed:

```
collapsed_vertex = random_choice(3, seed=building_id)
verts[collapsed_vertex] = lerp(verts[collapsed_vertex], center, 0.3)
→ one corner of the triangle sags toward the center
```

- 5-7 **rubble fragments** scattered in and around the footprint:
  - Mix of small rectangles (stone chunks) and triangles (Koch remnants)
  - Colors: `(45, 42, 38)` to `(65, 62, 55)` — various stone shades
  - Slightly rotated, overlapping for a natural rubble pile
  - Static positions, seeded by building_id

- Lv.2 towers: one faintly glowing ember dot (orange, alpha pulsing 20-60)
  among the rubble — a dying ember from the explosive ammunition

#### Repair: The Masonry Restoration

Tower repair has a **brick-by-brick** visual feel, distinct from the original
Koch growth:

```
Phase 1 (0-15% progress):
    The collapsed vertex straightens back to its proper position:
    vert_pos = lerp(collapsed_pos, original_pos, progress / 0.15)
    Base triangle fully restored. Still no Koch detail.
    Rubble fragments begin "dissolving" (alpha fades to 0 over this phase)

Phase 2 (15-50% progress):
    Koch depth incrementally restored (same as construction).
    BUT: each newly appearing Koch bump is first drawn in bright "mortar" color:
    mortar_color = (200, 190, 160)   # fresh light stone
    After appearing, mortar fades to match the building's stone color
    over 0.6 seconds:
    edge_color = lerp(mortar_color, stone_color, age / 0.6)
    → creates a visual "fresh masonry" effect — you can briefly see where
      the new stonework was just placed

Phase 3 (50-85% progress):
    Full Koch detail restored. Mortar lines still visible but fading.
    Border line thickness restores (back to 2px).
    The breach notch smooths out (inward dent lerps back to outward bump):
    breach_depth = lerp(-1, +1, (progress - 0.5) / 0.35)

Phase 4 (85-100% progress):
    Lv.2 glow dots relight one by one (every ~3% progress)
    Final polish: all mortar lines snap to final stone color
    Brief "fortification complete" flash — border line goes bright white
    for 0.2 sec, then settles to normal color
```

---

### 4B.7 Implementation Details

#### 4B.7.1 HP-Ratio Interpolation

All damage effects use `hp_ratio = hp / max_hp` as the primary driver.
Effects should be computed in the `draw()` method (not `update()`) so they're
purely visual with zero gameplay cost. The current `draw()` already has
`build_pct` — add `hp_ratio` as a second parameter:

```python
def draw(self, surf, cam):
    ...
    hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
    is_ruin = self.ruined

    # damage-adjusted color (universal desaturation)
    damage_t = 1.0 - hp_ratio
    def damage_color(base_color):
        gray = int(0.299*base_color[0] + 0.587*base_color[1] + 0.114*base_color[2])
        return tuple(int(c + (gray - c) * damage_t * 0.6) for c in base_color)
```

#### 4B.7.2 Particle System (Lightweight)

Buildings need a simple particle system for debris, smoke, sparks, and leaves.
This should be a per-building list capped at 8-10 particles max:

```python
class BuildingParticle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life',
                 'color', 'size', 'shape')  # shape: 'circle', 'triangle', 'rect'

Building.__init__:
    self._particles = []
    self._particle_timer = 0.0

Building.update:
    # spawn new particles based on HP state, update positions, cull dead
    # MAX 8 particles per building to stay lightweight
```

Key constraint: particles are visual-only. They do NOT interact with
gameplay, pathfinding, or collision. They are drawn during `Building.draw()`
and updated during `Building.update()`.

#### 4B.7.3 Damage Shake State

Add shake state to Building:

```python
Building.__init__:
    self._shake_timer = 0.0
    self._shake_amp = 0.0

Building.take_damage:
    self._shake_timer = 0.15
    self._shake_amp = min(4.0, 3.0 * (dmg / self.max_hp))

Building.draw:
    if self._shake_timer > 0:
        ox = self._shake_amp * math.sin(game_time * 40)
        oy = self._shake_amp * math.cos(game_time * 53)
        cx += int(ox)
        cy += int(oy)
```

#### 4B.7.4 Deterministic Seeding

Damage visuals (crack patterns, breach locations, rubble positions, branch
pruning) must be **deterministic per building instance** to avoid per-frame
flickering. Use the building's grid position as a seed:

```python
damage_seed = hash((self.col, self.row, self.building_type))
```

This ensures the same building always shows the same crack pattern and the
same breach location, even across save/load. Different buildings of the
same type show different patterns.

#### 4B.7.5 Performance Budget

- **Damage color desaturation**: ~0 cost (per-pixel math on existing color)
- **Branch pruning (TH)**: Adds one `hash + compare` per `[` token — negligible
- **Wobble perturbation (Refinery)**: Two extra `sin/cos` calls per point — ~5%
- **Breach notch (Tower)**: One Koch segment direction flip — zero extra cost
- **Particles**: Max 8 per building × ~10 buildings = 80 particles total.
  Each is a single `draw.circle` or `draw.polygon` call — well under budget.
- **Shake offset**: Two trig calls per damaged building per frame — negligible

Total estimated overhead: **< 2% frame time** for a full base under attack.

#### 4B.7.6 Repair vs Construction Visual Distinction

It's important that repair looks different from first-time construction:

| Aspect | Construction | Repair |
|---|---|---|
| Color ramp | Dark → full saturation | Charcoal → *bright flash* → normal |
| Growth speed | Steady, linear | Jerky-to-smooth (mechanical restart) |
| Particle effects | None | Ruin debris dissolves, mortar/glow flashes |
| Sound cue (future) | Hammering rhythm | Crackling + hammering |
| Fractal growth | Iterations add smoothly | Iterations add with restoration shimmer |

The player should be able to glance at a building and instantly know:
"that's being built for the first time" vs "that's being repaired after
damage." The bright flash on newly restored elements is the key tell.

---

## 5. Terrain — Noise Fields & Voronoi

### 5.1 Tile Rendering

Currently tiles are flat-colored rectangles. The algorithmic upgrade:

**Grass**: Perlin noise displacement map with two octaves. Base green
`(46, 139, 87)` with `+/- 15` value noise per pixel. Creates subtle,
natural-looking grass texture without any sprite.

**Water**: Sine wave interference pattern:
```
brightness = sin(x * 0.3 + t) * sin(y * 0.2 + t * 0.7) * 0.5 + 0.5
```
Oscillating `t` makes it shimmer. Deep water uses lower frequency, shallow
uses higher. No frame animation — pure math oscillation.

**Stone/Iron/Gold deposits**: Voronoi cell pattern overlaid on the tile.
Each resource type has a distinct cell density and color jitter:
- Gold: sparse large cells, warm jitter (Voronoi seeds = 3-4)
- Iron: medium angular cells (seeds = 6-8), cool gray jitter
- Stone: dense packed cells (seeds = 10-12), warm tan jitter

**Trees**: Current circle-on-circle is fine for now. Future: recursive
branching (simplified L-system, 2 iterations only) renders a tiny tree
silhouette per tile.

### 5.2 Map Border / Fog of War (Future)

The map edge fades into a **Mandelbrot-derivative** border — the explored
world dissolves into fractal chaos at the edges, implying infinite unexplored
wilderness.

---

## 6. Projectiles & Effects

### 6.1 Arrows — Parametric Darts

Arrows in flight are drawn as a **tapered parametric curve**:

```
body: line from (x, y) to (x - dx*len, y - dy*len)
head: small triangle (3 points, delta-shaped)
fletching: two short angled lines at tail end
```

Simple, fast, but the parametric tapering (line width decreases toward tail)
gives a sense of speed. Grounded arrows keep the same shape, color shifts to
`(120, 100, 80)` brown.

### 6.2 Cannonballs — Spirograph Trails

Cannonballs are solid circles (existing), but their **trail** is drawn as a
fading **hypotrochoid** (inner Spirograph curve):

```
x(t) = (R - r) * cos(t) + d * cos((R - r) / r * t)
y(t) = (R - r) * sin(t) + d * sin((R - r) / r * t)
```

Just 4-5 trail points rendered as fading circles create a subtle "spin"
impression behind the cannonball. Explosive cannonballs use orange trail,
normal use gray.

### 6.3 Explosions — Lissajous Bloom

The current expanding ring is good. The upgrade: replace the ring with a
**Lissajous figure** that expands and rotates:

```
x(t) = A * sin(a*t + delta)
y(t) = B * sin(b*t)
    where a/b = 3/2 or 5/4 (produces pleasing star-like figures)
    A, B expand over explosion lifetime
    delta rotates
```

The explosion looks like a rapidly expanding, rotating star-flower. Fades
from bright orange-white to transparent. The mathematical regularity of the
Lissajous gives it an almost magical, alchemical feel — fitting for an
explosive cannon upgrade.

### 6.4 Selection Ring — Breathing Rose

The unit selection indicator (currently a green circle) becomes a subtle
**polar rose** that slowly rotates:

```
r(theta + t) = base_radius + amplitude * cos(n * (theta + t))
    where n = 6 (hexagonal shimmer), amplitude = 2px, t rotates slowly
```

A gently pulsing, mathematically perfect halo around selected units.

---

## 7. UI & HUD Elements

### 7.1 Health Bars — Fibonacci Segmentation

Instead of smooth bars, health is displayed as **Fibonacci-segmented blocks**:
the bar is divided into segments of widths 1, 1, 2, 3, 5, 8, 13... pixels
(scaled to total HP). Damage eats segments from right to left, and the
Fibonacci sizing means the largest segments vanish first — visually dramatic.

### 7.2 Resource Icons — Mathematical Symbols

Each resource gets a tiny algorithmic icon in the top bar:

| Resource | Shape | Math Basis |
|---|---|---|
| Gold | Fibonacci spiral | Golden ratio spiral, 3 quarter-turns |
| Wood | Binary tree | Recursive Y-branch, 3 iterations |
| Iron | Octahedron wireframe | Regular polyhedron projection |
| Steel | Reuleaux triangle | Constant-width curve (strength) |
| Stone | Voronoi cell cluster | 4-5 Voronoi cells packed tight |

### 7.3 Minimap — Heat Overlay

The minimap could overlay a **Gaussian heat kernel** showing recent combat
activity — fading red hotspots where kills occurred. Pure math: each kill
event drops a 2D Gaussian that decays over 30 seconds.

---

## 8. Color Palette — Current & Extended

### 8.1 Existing Palette (preserved)

```
DARK CORE       (20, 20, 30)      UI backgrounds, void, fractal interior
EARTH GOLD      (218, 165, 32)    Gold resource, accents, fractal filaments
BRONZE           (205, 127, 50)    Veteran rank, warm highlights
LIFE GREEN       (46, 139, 87)     Grass, health, nature
MILITARY RED     (200, 60, 60)     Soldiers, combat, danger
WORKER BLUE      (50, 130, 220)    Workers, construction, selection
STONE TAN        (160, 150, 130)   Stone, towers, stability
STEEL BLUE       (100, 160, 220)   Steel, refinement, technology
IRON GRAY        (170, 170, 185)   Iron, raw materials
ENEMY CRIMSON    (220, 20, 60)     Elite enemies, threat
SHADOW PURPLE    (140, 0, 140)     Enemy archers, corruption
```

### 8.2 Extended Palette (new for algorithmic art)

```
FRACTAL DEEP     (10, 8, 25)       Deepest Mandelbrot zones
GLOW WHITE       (240, 235, 220)   Mathematical highlights, explosion peaks
CANOPY GREEN     (30, 110, 50)     L-system branch tips, tree canopy
FORGE ORANGE     (255, 140, 40)    Explosive upgrade, fire, smelting
VOID BLUE        (15, 25, 60)      Deep water, menu background tint
CORRUPTION NOISE (120, 20, 40)     Enemy unit perturbation tint
```

---

## 9. Implementation Priority

### Phase 1 — Menu Fractal (standalone, no gameplay impact)
1. Mandelbrot renderer (half-res surface, custom palette)
2. Slow zoom drift animation
3. Integrate into existing `menu.py`

### Phase 2 — Unit Shape Upgrade (gameplay visual improvement)
1. Polar rose soldiers (replace colored circles)
2. Hex workers
3. Spiral-bow archers
4. Rank-variant petal counts

### Phase 2.5 — Unit Lifecycle Animations (Idle → Move → Fight → Die)
1. Universal animation timer system + damage flash + idle breathing
2. Per-type state animations (move lean, attack lunge, shoot cycle)
3. Death dissolve sequences for all 5 unit types
4. Trait-modified animation parameters

### Phase 3 — Building Shape Upgrade
1. L-system town hall (grow with construction)
2. Sierpinski barracks
3. Spirograph refinery
4. Koch snowflake tower

### Phase 3.5 — Building Lifecycle Fractals (Damage → Ruin → Repair)
1. HP-interpolated fractal degradation for all four building types
2. Distinct ruin-state visuals with debris particles
3. Animated repair/rebuild restoration effects
4. Damage flash and screen-shake hooks

### Phase 4 — Terrain & Effects
1. Noise-based terrain texture
2. Lissajous explosions
3. Spirograph cannonball trails
4. Water sine shimmer

### Phase 5 — UI Polish
1. Fibonacci health bars
2. Mathematical resource icons
3. Breathing selection ring
4. Minimap heat overlay

---

## 10. Technical Notes

### 10.1 Performance Budget

All algorithmic art must be **pre-rendered to surfaces** and cached. We do NOT
recompute fractals every frame. Strategy:

- **Menu Mandelbrot**: Render once at startup to a 640x360 surface (half-res).
  Update zoom target every 2-3 seconds with incremental re-render.
- **Unit shapes**: Pre-compute each unit type + rank combo as a small surface
  (32x32 or 48x48) at game start. Cache in a dict keyed by `(type, rank)`.
  Re-render only on zoom change (quantized to 0.1 steps).
- **Building L-systems**: Pre-render at each construction depth (0-4). Cache
  5 surfaces per building type. Swap surface as build progresses.
- **Terrain tiles**: Render textured tiles to a tile atlas surface on map
  generation. Never recompute unless tiles change (resource depletion).

### 10.2 Pygame Constraints

- No shader support — all math runs on CPU via Python/numpy
- `pygame.Surface` with `SRCALPHA` for transparency
- `pygame.draw` primitives for lines/circles/polygons
- `pygame.surfarray` for pixel-level Mandelbrot/noise rendering
- Consider `numpy` for vectorized fractal computation (already available)

### 10.3 Zoom Scaling

All algorithmic shapes are defined in **unit coordinates** (0.0 to 1.0) and
scaled to pixel size at render time via `size * camera.zoom`. This means:
- Zoomed out: shapes simplify (fewer fractal iterations, fewer curve points)
- Zoomed in: shapes gain detail (more iterations, smoother curves)

This is **free LOD** — the math naturally supports it.

---

## 11. Mood Board — Mathematical References

These are the visual inspirations, all computable:

1. **Mandelbrot deep zooms** — specifically the "seahorse valley" and
   "elephant valley" regions where mini-brots appear (fortress in fortress)
2. **Polar roses** `r = cos(k*theta)` — shield-like, military, ornamental
3. **L-system plants** — Lindenmayer's original algae/tree grammars
4. **Koch snowflake** — the archetype of fractal boundary (crenellation)
5. **Sierpinski gasket** — military precision, triangular lattice
6. **Spirograph / epitrochoid** — mechanical beauty, gear-like
7. **Fibonacci spiral** — nature's growth pattern, golden ratio
8. **Lissajous figures** — oscilloscope art, energy visualization
9. **Voronoi diagrams** — crystal/cell structure, territory
10. **Perlin noise** — organic texture, the math of "natural-looking random"

---

*This document is a living reference. Each phase will add implementation
details, parameter tuning notes, and screenshots as the art is realized.*
