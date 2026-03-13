# Visual Design Document (VDD)
## Algorithmic Art Direction for the RTS

---

## 1. Core Philosophy

### 1.1 Algorithmic Naturalism

Every visual element is generated procedurally from mathematical functions.
The look is organic geometry — shapes that emerge from recursive rules
(coastlines, ferns, crystals). Nothing is hand-drawn; everything is computed.

The entire game ships as a single .exe with zero external assets.

### 1.2 The Three Pillars

| Pillar | Meaning | Math Lineage |
|---|---|---|
| **Growth** | Buildings/economy feel like living things expanding | L-systems, fractals, Fibonacci |
| **Force** | Combat units project contained violence, tension | Lissajous curves, polar roses, spirals |
| **Order from Chaos** | Map, terrain, fog emerge from noise into clarity | Perlin noise, Voronoi, Mandelbrot |

### 1.3 Aesthetic Targets

- **Resolution-independent**: All shapes scale with zoom via parametric math
- **Color palette**: Muted earth tones with mathematical accent glows
- **No outlines**: Shapes defined by fill, overlap, and subtle glow
- **Subtle motion**: Gentle parameter oscillation gives life without frame-based animation

---

## 2. Main Menu — The Mandelbrot Throne

**IMPLEMENTED in `menu.py`**

Key parameters:
- Mandelbrot renderer at half-resolution, max_iter=256
- Color map: COL_BG → gold → muted green → stone → COL_BG; interior = COL_BG
- Smooth iteration count: `mu = n - log2(log2(|z|))`
- Slow zoom drift toward mini-brot in seahorse valley
- Julia set transitions per difficulty:
  - Easy: `c = -0.4 + 0.6j` (Douady rabbit)
  - Medium: `c = -0.8 + 0.156j`
  - Hard: `c = -0.7269 + 0.1889j` (dendrite)

---

## 3. Units — Polar Roses & Parametric Warriors

**IMPLEMENTED in `entities.py`** (unit shape drawing)

Key shape parameters:

| Unit | Polar Equation | Key Param |
|---|---|---|
| **Worker** | Superellipse `r = 1/(|cos|^n + |sin|^n)^(1/n)` | n=4, rotated 30deg |
| **Soldier** | Rose `r = cos(k*theta)` | k=3/2 (recruit) → k=5 (captain) |
| **Archer** | Golden spiral `r = a*e^(b*theta)`, mirrored | b=0.3063 (ln(phi)/(pi/2)) |
| **Enemy** | Same equations + jagged perturbation | `r += noise*sin(17*theta)`, inverted rotation |

Rank variants: Workers add concentric hexes; Soldiers add petals (k increases); Archers add Fibonacci dots along spiral limbs.

---

## 3B. Unit Lifecycle Animations — Idle, Move, Fight, Fall

### 3B.1 Animation Principles

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

### 3B.2 Universal Animation State Machine

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

### 3B.3 Universal Animation Effects

#### 3B.3.1 Damage Flash (White Strobe)

```
on take_damage:
    self._anim_flash = 1.0

during draw:
    if _anim_flash > 0:
        flash_t = _anim_flash ** 2    # quadratic falloff
        draw_color = lerp(base_color, (255, 255, 255), flash_t * 0.7)
```

Enemy variant: flash toward `(200, 40, 40)` red instead of white.

#### 3B.3.2 Idle Breathing (Radius Pulse)

```
if state == "idle" or state == "guard":
    breath_t = sin(_anim_time * 1.8)          # ~0.55 Hz heartbeat
    radius_mult = 1.0 + 0.03 * breath_t       # +/- 3% radius shift
```

Per-unit `_anim_time` offsets create staggered breathing across groups.

#### 3B.3.3 Movement Lean (Directional Squash)

```
if state == "moving":
    move_angle = atan2(vy, vx)
    for each theta:
        angle_diff = theta - move_angle
        squash = 1.0 + 0.12 * cos(angle_diff)   # 12% stretch forward
        r_final = r(theta) * radius * squash

squash_amount = 0.08 + 0.04 * min(1.0, speed / max_speed)
```

#### 3B.3.4 Flee Contraction

```
if state == "fleeing":
    fear_t = sin(_anim_time * 8.0)      # fast 8 Hz tremor
    radius_mult = 0.85 + 0.05 * fear_t   # 15% smaller, 5% jitter
    rotation_offset += 0.03 * fear_t
```

#### 3B.3.5 Death Dissolve (Universal Framework)

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

### 3B.4 Worker — The Humming Hive

#### Idle: Hex Breathe + Inner Rotation

```
radius_mult = 1.0 + 0.025 * sin(_anim_time * 1.8)
inner_rotation_offset = _anim_time * 0.15    # 0.15 rad/sec drift
inner2_rotation_offset = -_anim_time * 0.10   # counter-rotate

skill_border_alpha = 180 + int(40 * sin(_anim_time * 2.5))
```

#### Moving: Waddle Bounce

```
if state == "moving":
    waddle_y = -abs(sin(_anim_time * 6.0)) * 2.0 * z   # 6 Hz bounce
    draw_y = sy + int(waddle_y)
    rotation_offset = 0.04 * sin(_anim_time * 6.0)

if carry_amount > 0:
    waddle_freq = 4.5       # slower pace
    waddle_amp = 3.0 * z    # bigger bounce
    orbit_wobble = sin(_anim_time * 3.0) * 0.15
```

#### Gathering: Rhythmic Pulse

```
if state == "gathering":
    gather_phase = (_anim_time * 2.5) % (2 * pi)
    if gather_phase < 0.4:  # quick compression pulse
        vertical_squash = 0.88   # 12% vertical compression
    else:
        vertical_squash = lerp(0.88, 1.0, (gather_phase - 0.4) / 1.5)

    flash = 1.0 if gather_phase < 0.3 else 0.0
    inner_color = lerp(base_inner_color, resource_color, flash * 0.4)
```

#### Building: Spinning Industry

```
if state == "building":
    inner_rotation = _anim_time * 1.2     # fast inner spin
    inner2_rotation = -_anim_time * 0.9    # counter-rotate
    if int(_anim_time / 0.3) != int((_anim_time - dt) / 0.3):
        sparkle_vertex = int(_anim_time * 7) % n_pts
        draw_small_flash(pts[sparkle_vertex], color=(240, 230, 200))
```

#### Taking Damage: Hex Shatter-Snap

```
on take_damage:
    _anim_flash = 1.0

during draw with _anim_flash > 0:
    for each vertex (x, y) in hex_pts:
        dx, dy = x - cx, y - cy
        explode_t = _anim_flash ** 3  # sharp snap, then slow settle
        x += dx * 0.15 * explode_t
        y += dy * 0.15 * explode_t
```

#### Dying: Honeycomb Dissolution

```
death animation (0.0 → 1.0 over 0.6 sec):
    for i in range(6):
        wedge_pts = [center, hex_pts[i*n//6], hex_pts[(i+1)*n//6]]
        drift_angle = (2 * pi * i / 6) + death_seed_offset[i]
        drift_dist = _anim_death * 20 * z
        wedge_offset_x = drift_dist * cos(drift_angle)
        wedge_offset_y = drift_dist * sin(drift_angle)
        wedge_rotation = _anim_death * 0.8
        alpha = int(255 * max(0, 1.0 - _anim_death * 1.6))
        draw_wedge(translated + rotated, color, alpha)
```

Skill-color afterglow: faint ring in skill color (alpha 40→0 over final 0.2s).

---

### 3B.5 Soldier — The Pulsing Blade

#### Idle / Guard: Rose Rotation + Petal Breathe

```
idle_rotation = _anim_time * 0.3     # 0.3 rad/sec
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
    radius_mult = 1.0 + flutter

if rank >= 3 and state == "moving":
    for ghost_i, ghost_age in enumerate([0.10, 0.20]):
        ghost_alpha = int(60 * (1.0 - ghost_i * 0.5))
        ghost_x = sx - vx * ghost_age
        ghost_y = sy - vy * ghost_age
        draw_soldier_shape(ghost_x, ghost_y, r * 0.95, alpha=ghost_alpha)
```

#### Attacking: Lunge + Sharpness Spike

```
on attack_timer reset (attack lands):
    _anim_attack = 1.0

Phase 1 — LUNGE (attack_t: 1.0 → 0.5, ~90ms):
    lunge_dir = atan2(target.y - self.y, target.x - self.x)
    lunge_offset_x = 6 * z * attack_t * cos(lunge_dir)
    lunge_offset_y = 6 * z * attack_t * sin(lunge_dir)
    effective_sharpness = 0.6 - 0.3 * attack_t   # 0.6 → 0.3 (sharper)
    radius_mult = 1.0 + 0.15 * attack_t

Phase 2 — RETRACT (attack_t: 0.5 → 0.0, ~90ms):
    lunge_offset *= attack_t * 2
    effective_sharpness = 0.6 - 0.3 * attack_t * 2
    radius_mult = 1.0 + 0.15 * attack_t * 2
```

Berserker trait: `lunge_distance = 9 * z`, sharpness drops to 0.15.

#### Taking Damage: Petal Buckle

```
during _anim_flash > 0:
    radius_mult = 1.0 - 0.12 * (_anim_flash ** 2)
    effective_k = k + 0.3 * sin(_anim_time * 30) * _anim_flash
```

#### Dying: Petal Shed

```
death animation (0.0 → 1.0 over 0.6 sec):
    n_petals = int(2 * k)
    shed_interval = 0.8 / n_petals

    for petal_i in range(n_petals):
        petal_birth = petal_i * shed_interval
        if _anim_death < petal_birth:
            draw_petal_segment(petal_i, attached=True)
        else:
            petal_age = _anim_death - petal_birth
            drift = petal_age * 30 * z
            tumble = petal_age * 2.5
            alpha = int(255 * max(0, 1.0 - petal_age * 2.5))
            draw_detached_petal(petal_i, drift, tumble, alpha)

    if rank >= 3:
        center_alpha = int(255 * max(0, 1.0 - _anim_death * 1.2))
        draw_center_dot(alpha=center_alpha)
```

Rank 3+: petals shed in golden-angle spiral pattern. Rank 4: final blue flash on center dot.

---

### 3B.6 Archer — The Flexing Bow

#### Idle: Limb Sway + String Tension

```
idle_flex = sin(_anim_time * 1.5) * 0.04  # 4% limb flex
top_limb_offset = idle_flex
bot_limb_offset = -idle_flex
string_x_offset = -idle_flex * r * 0.3
arrow_y_offset = sin(_anim_time * 2.0) * 1.0 * z

dot_brightness = 0.8 + 0.2 * sin(_anim_time * 1.2 + dot_index * 0.7)
```

#### Moving: Bounce + Arrow Sway

```
if state == "moving":
    bounce_y = -abs(sin(_anim_time * 5.0)) * 1.5 * z
    arrow_angle_offset = sin(_anim_time * 5.0) * 0.06
    bow_tilt = 0.08
```

#### Shooting: Full Draw-Release Cycle

```
Phase 1 — NOCK (attack_timer: 100% → 70% of attack_cd):
    string_draw = lerp(0, r * 0.25, nock_t)
    arrow_tail_x = lerp(normal_tail, pulled_tail, nock_t)
    limb_spread = 1.0 + 0.06 * nock_t

Phase 2 — HOLD (attack_timer: 70% → 15%):
    string_draw = r * 0.25
    limb_spread = 1.06
    tremble = sin(_anim_time * 25) * 0.01 * (1.0 - hold_t)
    string_draw += tremble * r

Phase 3 — RELEASE (attack_timer: 15% → 0%, arrow fires):
    release_t = 1.0 - (attack_timer / (attack_cd * 0.15))
    string_draw = r * 0.25 * (1.0 - release_t ** 0.5)  # fast snap (sqrt curve)
    limb_spread = 1.06 - 0.10 * release_t   # limbs overshoot inward
    recoil_x = -3 * z * (1.0 - release_t)
    draw_nocked_arrow = False

Aftermath — SETTLE (next 0.2 sec):
    settle_t = min(1.0, time_since_release / 0.2)
    limb_spread = 1.0 + 0.04 * sin(settle_t * pi * 3) * (1.0 - settle_t)
    string_x = normal_x + 2 * sin(settle_t * pi * 4) * (1.0 - settle_t)
```

Sharpshooter trait: hold-phase tremble amplitude * 0.3.

#### Taking Damage: String Vibration

```
during _anim_flash > 0:
    string_x_offset = sin(_anim_time * 50) * 3 * z * _anim_flash
    draw_x += sin(_anim_time * 35) * 1.5 * z * _anim_flash
    draw_y += cos(_anim_time * 41) * 1.0 * z * _anim_flash
```

#### Dying: Bow Uncoils

```
death animation (0.0 → 1.0 over 0.6 sec):
    effective_theta_range = (1.0 - _anim_death) * normal_theta_range

    if _anim_death > 0.2:
        string_break_t = (_anim_death - 0.2) / 0.3
        top_string_curl = string_break_t * 0.5
        bot_string_curl = -string_break_t * 0.5
        string_alpha = int(255 * max(0, 1.0 - string_break_t * 2))

    arrow_fall_y = _anim_death * 15 * z
    arrow_rotation = _anim_death * 1.2

    for dot_i, dot in enumerate(fib_dots):
        dot_shed_time = 0.3 + dot_i * 0.1
        if _anim_death > dot_shed_time:
            dot_drift = (_anim_death - dot_shed_time) * 25 * z
            dot_angle = golden_angle * dot_i

    alpha = int(255 * max(0, 1.0 - _anim_death * 1.5))
```

---

### 3B.7 Siege — The Grinding Engine

#### Idle: Spike Pulse + Inner Rotation

```
radius_mult = 1.0 + 0.04 * sin(_anim_time * 1.2)  # slow, heavy pulse
inner_gear_rotation = _anim_time * 0.4
spike_emphasis = 1.0 + 0.06 * abs(sin(_anim_time * 0.8))
```

#### Moving: Rolling Advance

```
if state == "moving":
    body_rotation += dt * 0.5   # slow roll
    bob_y = sin(_anim_time * 2.5) * 1.5 * z
```

#### Attacking: Spike Extend

```
on attack:
    _anim_attack = 1.0

during attack animation:
    spike_mult = 1.0 + 0.35 * _anim_attack ** 2
    inner_flash = _anim_attack * 0.6
    for each spike_i:
        spike_angle = spike_theta(spike_i)
        angle_to_target = atan2(target.y - self.y, target.x - self.x)
        alignment = max(0, cos(spike_angle - angle_to_target))
        spike_extra = alignment * 0.2 * _anim_attack
```

#### Dying: Implosion

```
death animation (0.0 → 1.0 over 0.8 sec):
    spike_mult = 1.0 - _anim_death * 0.8
    body_radius = radius * (1.0 - _anim_death * 0.7)

    if _anim_death > 0.6:
        fragment_t = (_anim_death - 0.6) / 0.4
        for frag_i in range(4):
            frag_angle = 2 * pi * frag_i / 4 + death_seed_offset
            frag_drift = fragment_t * 20 * z
            draw_fragment(frag_angle, frag_drift, alpha=fading)

    if _anim_death > 0.85:
        flash_alpha = int(200 * (1.0 - (_anim_death - 0.85) / 0.15))
        draw_circle(center, r * 0.3, (200, 100, 20, flash_alpha))
```

---

### 3B.8 Elite — The Unstable Star

#### Idle: Counter-Rotating Rose Orbit

```
outer_rotation = _anim_time * 0.25
inner_rotation = -_anim_time * 0.35
center_glow_radius = max(2, r // 5) + sin(_anim_time * 3.0) * 1.5 * z
center_glow_alpha = 160 + int(60 * sin(_anim_time * 2.0))
```

#### Moving: Rose Alignment

```
if state == "moving":
    target_rotation = move_angle - pi/2
    outer_rotation = lerp(outer_rotation, target_rotation, 0.2)
    inner_rotation = lerp(inner_rotation, target_rotation + pi, 0.15)
    center_glow_alpha = 220
```

#### Attacking: Aura Expansion

```
on attack:
    _anim_attack = 1.0

during attack:
    outer_radius = r * (0.95 + 0.25 * _anim_attack)
    inner_radius = r * (0.55 - 0.15 * _anim_attack)
    center_glow = max(3, r // 3) * (1.0 + 0.5 * _anim_attack)
    halo_radius = r * (1.05 + 0.15 * _anim_attack)
```

#### Dying: Binary Fission

```
death animation (0.0 → 1.0 over 0.7 sec):
    split_angle = death_seed * 2 * pi / 1000
    split_dist = _anim_death * 35 * z

    outer_cx = cx + split_dist * cos(split_angle)
    outer_cy = cy + split_dist * sin(split_angle)
    inner_cx = cx - split_dist * cos(split_angle)
    inner_cy = cy - split_dist * sin(split_angle)

    outer_radius = r * 0.95 * (1.0 - _anim_death * 0.7)
    inner_radius = r * 0.55 * (1.0 - _anim_death * 0.6)
    glow_alpha = int(180 * (1.0 - _anim_death * 1.3))

    if _anim_death > 0.8:
        for i in range(8):
            dot_angle = 2 * pi * i / 8 + death_seed
            dot_drift = (_anim_death - 0.8) * 40 * z
            draw_dot(center + drift, alpha=fading)
```

---

### 3B.9 Implementation Details

#### 3B.9.1 Animation Timer Management

```python
# Init in __init__:
self._anim_time = random.uniform(0, 10.0)
self._anim_flash = 0.0    # 1.0 → 0.0 over 0.12s
self._anim_attack = 0.0   # 1.0 → 0.0 over 0.18s
self._anim_dying = False
self._anim_death = 0.0    # 0.0 → 1.0 over 0.6s
self._death_seed = 0

# Update in update():
self._anim_time += dt
self._anim_flash = max(0, self._anim_flash - dt / 0.12)
self._anim_attack = max(0, self._anim_attack - dt / 0.18)
if self._anim_dying:
    speed = 1.0 / 0.6   # 0.8 for siege
    self._anim_death = min(1.0, self._anim_death + dt * speed)

# Triggers:
# in take_damage(): self._anim_flash = 1.0
# in _do_attack():  self._anim_attack = 1.0
# when hp <= 0:     self._anim_dying = True; self._death_seed = hash(id(self)) % 10000
```

#### 3B.9.2 Draw Integration

```python
def draw(self, surf, cam):
    radius_mult = 1.0
    rotation_offset = 0.0
    offset_x, offset_y = 0, 0
    sharpness_mod = 0.0
    squash_dir = None
    squash_amount = 0.0
    alpha = 255

    if self._anim_dying:
        alpha = int(255 * max(0, 1.0 - self._anim_death * 1.6))
        ... # unit-type-specific death
    else:
        if state == "idle":
            radius_mult += 0.03 * sin(self._anim_time * 1.8)
        if state == "moving":
            ... # lean + bounce
        if self._anim_flash > 0:
            ... # flash overlay
        if self._anim_attack > 0:
            ... # lunge offset

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
| Death dissolve | N fragments x transform | Only on dying units (rare, brief) |
| Trail ghosts | 1-2 extra shape draws | Rank 3+ soldiers only while moving |

Worst case: 200 units all fighting = ~200 extra sin/cos calls/frame. At 60 FPS: **< 0.5ms**.

#### 3B.9.4 Enemy Animation Corruption

```
if is_enemy:
    breath = sin(_anim_time * 1.8) * 0.5 + sin(_anim_time * 2.7) * 0.5
    radius_mult = 1.0 + 0.04 * breath  # irregular dual-frequency breathing
    squash_amount *= 1.5               # 18% lean instead of 12%
    lunge_distance *= 1.2              # 20% farther attack lunge
    death_speed = 1.0 / 0.4            # faster death (0.4s vs 0.6s)
    jagged_amplitude = base_jagged * (1.0 + 0.3 * _anim_attack)
```

#### 3B.9.5 Trait-Modified Animations

| Trait | Animation Effect |
|---|---|
| **Brave** | Idle pulse amplitude +50% |
| **Cowardly** | Idle pulse faster (+30% freq), smaller amplitude |
| **Aggressive** | Attack lunge distance +30%, faster retract |
| **Cautious** | Slower idle rotation, minimal movement lean |
| **Berserker** | Below 50% HP: sharpness permanently spiked, no settle |
| **Nimble** | Movement bounce amplitude +40%, faster flutter |
| **Inspiring** | Center dot/glow pulses brighter (rank 3+ aura) |
| **Lone Wolf** | No trail ghosts even at high rank |
| **Sharpshooter** | Archer hold-phase tremble reduced 70% |

---

## 4. Buildings — L-System Fortresses

**IMPLEMENTED in `entities.py`** (building shape drawing)

Key shape parameters:

| Building | Shape | Equation/Grammar | Key Params |
|---|---|---|---|
| **Town Hall** | L-system tree | `F -> FF+[+F-F-F]-[-F+F+F]`, angle=22.5deg | Iter 0-4, grows with construction |
| **Barracks** | Sierpinski triangle | Subdivide equilateral, remove center | Depth 0-3 |
| **Refinery** | Spirograph (epitrochoid) | `x=(R+r)cos(t)-d*cos((R+r)/r*t)` | R=5, r=3, d=5 |
| **Tower** | Koch snowflake | Koch curve on square base | Depth 2-3, Lv.2 gets orange tips |

Construction: fractal depth/iterations increase with build_progress.
Ruin state: iterations drop to minimum, colors desaturate.

---

## 4B. Building Lifecycle Fractals — Damage, Ruin & Repair

### 4B.1 Visual States

| State | Trigger | Visual Effect |
|---|---|---|
| **Healthy** | `hp == max_hp` | Full fractal, bright colors, active animation |
| **Damaged** | `hp < max_hp` | Progressive degradation interpolated by HP ratio |
| **Ruined** | `hp == 0, ruined=True` | Collapsed fractal, debris, desaturated palette |
| **Repairing** | Worker assigned, `build_progress` rising | Restoration glow, regrowth animation |

Damage is a gradient, not a switch.

### 4B.2 Universal Damage Language

#### 4B.2.1 Color Desaturation Gradient

```
damage_ratio = 1.0 - (hp / max_hp)

For each color channel (R, G, B):
    gray = 0.299*R + 0.587*G + 0.114*B
    damaged_c = lerp(original_c, gray, damage_ratio * 0.6)
```

0.6 cap prevents total gray — ruins retain ghost of original hue.

#### 4B.2.2 Damage Shake (Micro-Tremor)

```
on_hit:
    shake_timer = 0.15 sec
    shake_amplitude = 3px * (damage / max_hp)

during shake_timer > 0:
    draw_offset_x = shake_amplitude * sin(time * 40)
    draw_offset_y = shake_amplitude * cos(time * 53)
    shake_timer -= dt
    shake_amplitude *= 0.85
```

Two frequencies (40/53 Hz) create Lissajous micro-orbit, damps in ~150ms.

#### 4B.2.3 Crack Lines (Universal)

```
n_cracks = int((1.0 - hp_ratio) * 5)    # 0 at full, up to 3 at ruin
crack_seed = building_id * 7919          # deterministic per building

for each crack:
    start = random_point_on_edge(seed)
    for segment in range(3 + crack_index):
        angle = seeded_noise(segment) * pi/3
        draw_line(dark_color, start, start + polar(angle, length))
        start += polar(angle, length)
```

Color: `(8, 5, 3)` near-black, 1px width. Deterministic (same seed = same pattern).

#### 4B.2.4 Damage Particle Debris

Below 40% HP, small fragments drift downward:
- Shape: tiny triangle (3-5px), darkened building palette color
- Motion: 20px/sec fall + sine drift (5px amplitude, 2sec period)
- Lifetime: 1.5 sec, respawn at random building edge
- Alpha: 180 → 0 over lifetime

---

### 4B.3 Town Hall — The Dying & Reborn Tree

#### Damage: Autumn Decay

```
hp_ratio > 0.75:  SUMMER — full green canopy, 4 iterations
hp_ratio > 0.50:  AUTUMN — tips green→amber→brown, 20% branches pruned
hp_ratio > 0.25:  LATE AUTUMN — tips brown/gray, 40% pruned, iter→3
                   Trunk: (139,90,43) → (80,50,25)
hp_ratio ≤ 0.25:  WINTER — all tips gray, 60% pruned, iter→2
```

Branch pruning:
```
prune_threshold = (1.0 - hp_ratio) * 0.6
for each branch_start '[':
    branch_hash = hash(branch_index + building_id)
    if (branch_hash % 1000) / 1000.0 < prune_threshold:
        skip to matching ']'
```

Leaf fall particles (below 50% HP): damped pendulum spiraling down:
```
x(t) = start_x + amplitude * sin(omega * t) * exp(-0.5 * t)
y(t) = start_y + fall_speed * t
color = lerp(green, amber, t / lifetime)
```

#### Ruin: The Charred Stump

- Iter locked to 1, colors → charcoal: trunk `(30,20,12)`, tips `(15,12,8)`
- Smoke wisp: 3-4 circles (6-10px), alpha 40-80, y_drift -15px/s, x_drift sin sway, color `(60,55,50)`
- Two ember dots (2px, `(200,80,20)`) flicker at trunk base

#### Repair: Spring Regrowth

```
during repair:
    tip_color = lerp(charcoal_gray, bright_spring_green, build_progress)
    spring_green = (60, 200, 70)   # brighter than normal

    if branch_just_appeared(this_iteration):
        tip_glow = lerp(spring_green, (150, 255, 120), pulse_t)
        pulse_t decays 1.0 → 0.0 over 0.8 sec
```

- Smoke fades at 25% progress, embers extinguish at 15%
- At 100%: bloom pulse — all tips flash bright green for 0.3s

---

### 4B.4 Barracks — The Shattering & Reforging Lattice

#### Damage: Fracture Propagation

```
hp_ratio > 0.75:  INTACT — full depth 4, crisp colors
hp_ratio > 0.50:  STRESSED — outermost sub-triangles jitter 2-3px
hp_ratio > 0.25:  FRACTURING — depth→3, 30% leaf triangles outlines only
hp_ratio ≤ 0.25:  CRUMBLING — depth→2, 50% outlines, border flickers
```

Fragment jitter:
```
for each leaf_triangle vertex (x, y):
    jitter_seed = hash(vertex_index + building_id + damage_epoch)
    if hp_ratio < 0.5:
        offset_x = seeded_random(-3, 3) * (1.0 - hp_ratio)
        offset_y = seeded_random(-3, 3) * (1.0 - hp_ratio)
```

`damage_epoch` increments per hit — fragments shift on impact, then hold.

#### Ruin: The Broken Frame

- Only outer equilateral border remains (dashed: 6px segments, 4px gaps)
- 3-5 scattered fragment triangles at base, dark maroon `(50,15,15)`, slightly rotated
- Interior empty

#### Repair: Crystallization Wave

```
during repair:
    effective_depth = int(build_progress * 4 + 0.5)
    for each newly_appearing_triangle:
        flash_color = (220, 100, 100)
        flash_alpha = lerp(255, 0, local_age / 0.5)
        draw_triangle(color=lerp(flash_color, target_color, local_age / 0.5))
```

- Ruin fragments lift back during first 20% of repair
- Dashed border becomes solid at 10%, border color restores at 90%

---

### 4B.5 Refinery — The Grinding Halt & Restart

#### Damage: Wobble & Stutter

```
hp_ratio > 0.75:  RUNNING — smooth rotation, all cusps lit
hp_ratio > 0.50:  STUTTERING — rotation_speed = base * (0.5 + 0.5*sin(time*3))
                   1-2 cusp dots go dark
hp_ratio > 0.25:  SEIZING — speed * 0.2, heavy wobble:
                   perturbation = sin(13*t + time*5) * 3px * (1-hp_ratio)
                   50% cusp dots dark
hp_ratio ≤ 0.25:  FAILING — rotation frozen, perturbation maxed
                   1 flickering cusp dot, occasional spark particles
```

Wobble perturbation (primes 13/17 for non-repeating pattern):
```
damage_wobble = (1.0 - hp_ratio) * 0.15
x(t) = (R+r)*cos(t) - d*cos((R+r)/r*t) + damage_wobble * sin(13*t + phase)
y(t) = (R+r)*sin(t) - d*sin((R+r)/r*t) + damage_wobble * cos(17*t + phase)
```

Spark particles (below 25% HP):
```
every 0.8-1.5 sec: emit 2-3 dots (2px) from random cusp
speed: 40-80 px/sec, lifetime: 0.15-0.25 sec
color: (255, 240, 100) → (200, 100, 20)
```

#### Ruin: The Broken Gear

- Curve collapses to simple circle (dashed), 4-6 scattered cusp dots at base
- No rotation, no animation; near-monochrome gray

#### Repair: The Restart Sequence

```
Phase 1 (0-20%): Cusp dots pull back to positions, circle dashed→solid
Phase 2 (20-60%): Spirograph re-emerges, slow jerky rotation (speed*0.1)
                   Cusp dots relight one per ~8% progress
Phase 3 (60-90%): Full curve, rotation accelerates via smoothstep
                   Wobble decreases: amp = (1.0-progress)*0.15
                   Colors gray → blue-gray → steel-blue
Phase 4 (90-100%): All cusps flash bright, full speed, celebratory sparks
```

---

### 4B.6 Tower — The Crumbling & Rebuilt Battlement

#### Damage: Edge Erosion

```
hp_ratio > 0.75:  FORTIFIED — full Koch depth, Lv.2 glow dots bright
hp_ratio > 0.50:  WEATHERED — outer_edge_depth = base-1 (inner preserved)
                   1-2 glow dots dim
hp_ratio > 0.25:  CRUMBLING — global depth-1, rubble rects at base
                   Border 1px, glow dots half extinguished + flicker
hp_ratio ≤ 0.25:  BREACHED — depth-2 (min 1), V-shaped notch in one edge:
                   replace Koch middle-third with inward dent
                   All glow dots extinguished, 4-5 rubble rects
```

Breach notch (deterministic per building_id):
```
for chosen edge's middle third:
    instead of outward equilateral bump → inward equilateral dent
```

#### Ruin: The Rubble Mound

- Koch depth 0 (base triangle only), fill `(50,50,45)`
- One vertex collapsed inward: `verts[i] = lerp(verts[i], center, 0.3)`
- 5-7 rubble fragments (mix rects + triangles), stone shades `(45,42,38)` to `(65,62,55)`
- Lv.2 towers: faint ember dot (orange, alpha 20-60 pulsing)

#### Repair: The Masonry Restoration

```
Phase 1 (0-15%): Collapsed vertex straightens, rubble dissolves
Phase 2 (15-50%): Koch depth restores; new bumps flash mortar color:
    mortar_color = (200, 190, 160)
    edge_color = lerp(mortar_color, stone_color, age / 0.6)
Phase 3 (50-85%): Full detail, breach notch lerps back to outward bump:
    breach_depth = lerp(-1, +1, (progress - 0.5) / 0.35)
    Border 2px restored
Phase 4 (85-100%): Glow dots relight, mortar snaps to final color
    Brief white border flash (0.2s)
```

---

### 4B.7 Implementation Details

#### 4B.7.1 HP-Ratio Interpolation

```python
def draw(self, surf, cam):
    hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 1.0
    is_ruin = self.ruined
    damage_t = 1.0 - hp_ratio
    def damage_color(base_color):
        gray = int(0.299*base_color[0] + 0.587*base_color[1] + 0.114*base_color[2])
        return tuple(int(c + (gray - c) * damage_t * 0.6) for c in base_color)
```

#### 4B.7.2 Particle System (Lightweight)

```python
class BuildingParticle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life',
                 'color', 'size', 'shape')  # shape: 'circle', 'triangle', 'rect'

Building.__init__:
    self._particles = []
    self._particle_timer = 0.0
    # MAX 8 particles per building
```

#### 4B.7.3 Damage Shake State

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
        cx += int(ox); cy += int(oy)
```

#### 4B.7.4 Deterministic Seeding

```python
damage_seed = hash((self.col, self.row, self.building_type))
```

Same building always shows same crack/breach pattern, even across save/load.

#### 4B.7.5 Performance Budget

| Effect | Cost |
|---|---|
| Color desaturation | ~0 (per-pixel on existing color) |
| Branch pruning (TH) | 1 hash+compare per `[` token |
| Wobble (Refinery) | 2 extra sin/cos per point (~5%) |
| Breach notch (Tower) | 1 Koch segment flip (zero extra) |
| Particles | Max 80 total (8/building x ~10 buildings) |
| Shake offset | 2 trig calls per damaged building |

Total: **< 2% frame time** for full base under attack.

#### 4B.7.6 Repair vs Construction Visual Distinction

| Aspect | Construction | Repair |
|---|---|---|
| Color ramp | Dark → full saturation | Charcoal → bright flash → normal |
| Growth speed | Steady, linear | Jerky-to-smooth (mechanical restart) |
| Particles | None | Ruin debris dissolves, mortar/glow flashes |
| Fractal growth | Iterations add smoothly | Iterations add with restoration shimmer |

---

## 5. Terrain — Noise Fields & Voronoi

### 5.1 Tile Rendering

**Grass**: Perlin noise, two octaves. Base green `(46,139,87)` with +/-15 value noise.

**Water**: Sine wave interference:
```
brightness = sin(x * 0.3 + t) * sin(y * 0.2 + t * 0.7) * 0.5 + 0.5
```

**Stone/Iron/Gold deposits**: Voronoi cell overlay per tile:
- Gold: sparse large cells (3-4 seeds), warm jitter
- Iron: medium angular cells (6-8 seeds), cool gray
- Stone: dense packed cells (10-12 seeds), warm tan

**Trees**: Current circle-on-circle. Future: simplified 2-iter L-system.

### 5.2 Map Border / Fog of War (Future)

Map edge fades into Mandelbrot-derivative border — explored world dissolves
into fractal chaos at edges.

---

## 6. Projectiles & Effects

### 6.1 Arrows — Parametric Darts

```
body: line from (x, y) to (x - dx*len, y - dy*len)
head: small delta-shaped triangle
fletching: two short angled lines at tail
```

Parametric tapering (line width decreases toward tail). Grounded: `(120,100,80)`.

### 6.2 Cannonballs — Spirograph Trails

Trail as fading hypotrochoid:
```
x(t) = (R - r) * cos(t) + d * cos((R - r) / r * t)
y(t) = (R - r) * sin(t) + d * sin((R - r) / r * t)
```
4-5 trail points as fading circles. Explosive = orange trail, normal = gray.

### 6.3 Explosions — Lissajous Bloom

Expanding rotating Lissajous figure:
```
x(t) = A * sin(a*t + delta)
y(t) = B * sin(b*t)
    a/b = 3/2 or 5/4; A,B expand; delta rotates
```
Fades from bright orange-white to transparent.

### 6.4 Selection Ring — Breathing Rose

```
r(theta + t) = base_radius + amplitude * cos(n * (theta + t))
    n = 6, amplitude = 2px, t rotates slowly
```

---

## 7. UI & HUD Elements

### 7.1 Health Bars — Fibonacci Segmentation

Bar divided into Fibonacci-width segments (1,1,2,3,5,8,13... px scaled to HP).
Largest segments vanish first on damage.

### 7.2 Resource Icons — Mathematical Symbols

| Resource | Shape | Math Basis |
|---|---|---|
| Gold | Fibonacci spiral | 3 quarter-turns |
| Wood | Binary tree | Recursive Y-branch, 3 iterations |
| Iron | Octahedron wireframe | Polyhedron projection |
| Steel | Reuleaux triangle | Constant-width curve |
| Stone | Voronoi cell cluster | 4-5 cells packed |

### 7.3 Minimap — Heat Overlay

Gaussian heat kernel per kill event, decays over 30 seconds.

---

## 8. Color Palette — Current & Extended

### 8.1 Existing Palette

```
DARK CORE       (20, 20, 30)      UI backgrounds, void, fractal interior
EARTH GOLD      (218, 165, 32)    Gold resource, accents, fractal filaments
BRONZE          (205, 127, 50)    Veteran rank, warm highlights
LIFE GREEN      (46, 139, 87)     Grass, health, nature
MILITARY RED    (200, 60, 60)     Soldiers, combat, danger
WORKER BLUE     (50, 130, 220)    Workers, construction, selection
STONE TAN       (160, 150, 130)   Stone, towers, stability
STEEL BLUE      (100, 160, 220)   Steel, refinement, technology
IRON GRAY       (170, 170, 185)   Iron, raw materials
ENEMY CRIMSON   (220, 20, 60)     Elite enemies, threat
SHADOW PURPLE   (140, 0, 140)     Enemy archers, corruption
```

### 8.2 Extended Palette (for algorithmic art)

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

### Phase 1 — Menu Fractal (standalone)
1. Mandelbrot renderer (half-res, custom palette)
2. Slow zoom drift
3. Integrate into `menu.py`

### Phase 2 — Unit Shape Upgrade
1. Polar rose soldiers
2. Hex workers
3. Spiral-bow archers
4. Rank-variant petal counts

### Phase 2.5 — Unit Lifecycle Animations
1. Universal animation timer system + damage flash + idle breathing
2. Per-type state animations (move lean, attack lunge, shoot cycle)
3. Death dissolve sequences for all 5 unit types
4. Trait-modified animation parameters

### Phase 3 — Building Shape Upgrade
1. L-system town hall
2. Sierpinski barracks
3. Spirograph refinery
4. Koch snowflake tower

### Phase 3.5 — Building Lifecycle Fractals
1. HP-interpolated fractal degradation for all building types
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

All algorithmic art must be pre-rendered to surfaces and cached:
- **Menu Mandelbrot**: Render once at startup to 640x360 surface. Update zoom every 2-3s.
- **Unit shapes**: Pre-compute per (type, rank) as 32x32/48x48 surfaces. Re-render on zoom change (quantized to 0.1 steps).
- **Building L-systems**: Pre-render at each depth (0-4). Cache 5 surfaces per type.
- **Terrain tiles**: Render to tile atlas on map generation. Never recompute unless tiles change.

### 10.2 Pygame Constraints

- No shader support — all math on CPU via Python/numpy
- `pygame.Surface` with `SRCALPHA` for transparency
- `pygame.draw` primitives for lines/circles/polygons
- `pygame.surfarray` for pixel-level Mandelbrot/noise
- `numpy` for vectorized fractal computation

### 10.3 Zoom Scaling

All shapes defined in unit coordinates (0.0-1.0), scaled at render time via `size * camera.zoom`.
Zoomed out: fewer iterations/points. Zoomed in: more detail. Free LOD.

---

## Phase 4: GUI Overhaul — The Fractal Interface (v11)

### 4.1 Design Principles

1. **Fractal Coherence**: UI elements use same math as game world (Koch for buildings, roses for units)
2. **Organic Geometry**: No flat rectangles — fractal borders, parametric outlines, fading edges
3. **Animated but Calm**: ~0.3 Hz pulse, Koch depth modulation, polar rose bloom on hover
4. **Earned Complexity**: Simple states = simple visuals; complex states = fractal richness

---

### 4.2 Fractal Typography — Self-Similar Glyphs

L-system rune font. Each glyph is polyline segments in normalized coords (0..1).
Monospace: `char_w = font_size * 0.6`, `char_h = font_size`.

Stroke rendering: 2-pass (glow at 40% alpha + core at full color).

```python
FRACTAL_GLYPHS = {
    "A": [[(0.1,1), (0.5,0), (0.9,1)], [(0.25,0.6), (0.75,0.6)]],
    "B": [[(0.15,0), (0.15,1)], [(0.15,0), (0.7,0), (0.8,0.12), (0.8,0.38),
           (0.7,0.5), (0.15,0.5)], [(0.15,0.5), (0.75,0.5), (0.85,0.62),
           (0.85,0.88), (0.75,1), (0.15,1)]],
    "C": [[(0.85,0.15), (0.6,0), (0.3,0), (0.15,0.15), (0.15,0.85),
           (0.3,1), (0.6,1), (0.85,0.85)]],
    # ... ~80 entries total (A-Z, a-z, 0-9, punctuation)
}
```

Self-similar serifs at font size >= 24px (depth 1), >= 36px (depth 2):

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

#### Font Rendering Pipeline

```python
class FractalFont:
    def __init__(self, size, color=(230, 205, 90)):
        self.size = size
        self.char_w = int(size * 0.6)
        self.char_h = size
        self.color = color
        self.glow_color = tuple(max(0, c - 80) for c in color)
        self.serif_depth = 0 if size < 24 else (1 if size < 36 else 2)
        self._cache = {}

    def render_text(self, surf, text, x, y, center=False):
        total_w = len(text) * self.char_w
        if center:
            x -= total_w // 2
        for ch in text:
            self._render_glyph(surf, ch, x, y)
            x += self.char_w
        return total_w

    def _render_glyph(self, surf, ch, x, y):
        if ch == " ":
            return
        key = (ch, self.size, self.color)
        if key not in self._cache:
            self._cache[key] = self._build_glyph_surface(ch)
        surf.blit(self._cache[key], (x, y))

    def _build_glyph_surface(self, ch):
        s = pygame.Surface((self.char_w + 4, self.char_h + 4), pygame.SRCALPHA)
        strokes = FRACTAL_GLYPHS.get(ch.upper(), FRACTAL_GLYPHS.get(ch, None))
        if not strokes:
            return s
        ox, oy = 2, 2
        # pass 1: glow
        for polyline in strokes:
            pts = [(int(p[0]*self.char_w+ox), int(p[1]*self.char_h+oy)) for p in polyline]
            if len(pts) >= 2:
                pygame.draw.lines(s, (*self.glow_color, 100), False, pts,
                                  max(2, self.size//10+1))
        # pass 2: core
        for polyline in strokes:
            pts = [(int(p[0]*self.char_w+ox), int(p[1]*self.char_h+oy)) for p in polyline]
            if len(pts) >= 2:
                pygame.draw.lines(s, (*self.color, 255), False, pts,
                                  max(1, self.size//14))
        # pass 3: serifs
        if self.serif_depth > 0:
            for polyline in strokes:
                for p in [polyline[0], polyline[-1]]:
                    px = int(p[0]*self.char_w+ox)
                    py = int(p[1]*self.char_h+oy)
                    _draw_serif(s, px, py, -math.pi/4,
                               self.size*0.08, self.serif_depth, self.color)
        return s
```

#### Font Size Tiers

| Context | Size | Serif Depth | Glow |
|---|---|---|---|
| Panel titles | 28px | 1 | Yes |
| Body text | 20px | 0 | Yes |
| Small labels | 16px | 0 | Subtle |
| Tiny | 13px | 0 | No |
| Hero title | 40px | 2 | Strong |
| Building label (world) | 16-20*z | 0 | No |

#### Color Variants

| Context | Color |
|---|---|
| Default | `(230, 205, 90)` gold |
| Warning | `(220, 80, 40)` red-orange |
| Disabled | `(80, 75, 60)` muted |
| Building label | `(255, 255, 255)` white |
| Enemy info | `(200, 80, 80)` hostile red |

Fallback: `pygame.font.SysFont(None, size)` for sizes <13px or strings >50 chars.

---

### 4.3 Panel Frames — Koch Border System

```python
def koch_border(surf, rect, depth, color, line_width=1):
    x, y, w, h = rect
    corners = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        points = _koch_side(p1, p2, depth)
        if len(points) >= 2:
            pygame.draw.lines(surf, color, False, points, line_width)
```

Animated depth: `depth_float = 1.0 + 0.5 * sin(game_time * 0.3)`

Panel background: radial gradient center `(35,32,50)` → edge `(20,18,30)`.
Optional: 20x15 Mandelbrot micro-render at 5% alpha as texture.

#### Panel Types

| Panel | Border Color | Border Depth | Background |
|---|---|---|---|
| Top bar | `(80,75,55)` gold-gray | 1 | Horizontal Mandelbrot strip |
| Bottom info | `(80,80,100)` | 1-2 breathing | Radial gradient |
| Building panel | Building's own color | 1 | Faint building shape echo |
| Unit panel | Unit type color | 1 | Faint polar rose echo |
| Tooltip | `(100,90,60)` gold | 1 (static) | Solid dark |
| Notification | Event color | 0 | Translucent |

---

### 4.4 Buttons — Polar Rose Bloom

**Idle**: Koch depth-1 border `(60,55,45)`, radial gradient fill, gold text `(200,185,80)`
**Hover**: Koch depth-2 `(120,100,50)`, brighter fill, tiny 3-petal roses at corners, bright gold text `(240,220,110)`
**Pressed**: Koch depth-1 `(80,70,40)`, darker fill, text offset +1px down
**Disabled**: Simple rect `(40,38,45)`, flat fill, muted text `(70,65,50)`

Cost display: resource-colored fractal font below button. Not affordable: dimmed + "x". Affordable: subtle pulse glow.

---

### 4.5 Resource Display — Fibonacci Counter

Resource icons enhanced with:
- Idle pulse: `1.0 + 0.03 * sin(time * 1.5)`
- Income flash: scale to 1.15x with bright flash
- Depletion warning (<=10% of peak): slow wobble rotation + dim

Number display: FractalFont with resource color.
- Tick-up: digits grow from 0-height over 0.15s
- Tick-down: digits dissolve as Koch-fragmented outlines

Optional supply bar: 3px fractal progress bar using micro-spirograph fill:
```
fill_t = resource_amount / peak_amount
spirograph_t = fill_t * 4 * math.pi
```

---

### 4.6 HP & Progress Bars — Spirograph Fills

```python
def fractal_bar(surf, x, y, w, h, ratio, color, bg_color):
    pygame.draw.rect(surf, bg_color, (x, y, w, h))
    fill_w = int(w * ratio)
    for px in range(fill_w):
        wave = math.sin(px * 0.3 + game_time * 2.0) * (h * 0.15)
        top = max(0, int(h / 2 - h / 2 + wave))
        bot = min(h, int(h / 2 + h / 2 + wave))
        for py in range(top, bot):
            t = py / h
            c = _lerp_color(color, (color[0]//2, color[1]//2, color[2]//2), t)
            surf.set_at((x + px, y + py), c)
```

Pre-render wave pattern to cached surface; blit appropriate width slice per frame.

Build progress: blue `(0,180,255)` wave, frequency increases with completion.
Train progress: gold wave. Lissajous bloom (tiny, gold, 0.3s) on completion.

---

### 4.7 Selection System — Rose Rings

```python
def _draw_selection_rose(surf, sx, sy, r, k, rotation, color):
    pts = []
    for i in range(60):
        theta = rotation + 2 * math.pi * i / 60
        rv = (r + 4) * abs(math.cos(k * theta)) ** 0.5
        rv = max(rv, r * 0.7)
        pts.append((sx + rv * math.cos(theta), sy + rv * math.sin(theta)))
    pygame.draw.lines(surf, color, True, pts, 1)
```

- Worker: superellipse hex ring
- Soldier: 5-petal rose ring at r+3
- Archer: golden spiral arc ring
- Buildings: Koch-curve rectangle outline, breathing depth
- Multi-select box: Koch-bordered, depth increases with box size

---

### 4.8 Minimap Frame

- Border: Koch depth-2 frame, `(80,75,55)` gold-gray
- Camera viewport: golden Koch depth-1 rectangle
- Combat heat: Lissajous bloom marks (fading trefoils) instead of red circles

---

### 4.9 Notifications — Dissolving Runes

FractalFont with Koch-bordered pill shape. Fade-out as fractal dissolution:
1. Serif branches disappear (depth decreases)
2. Koch border depth 1 → 0
3. Random character strokes disappear
4. Final: just dots where text was, then gone

---

### 4.10 Wave Timer — Breathing Arc

```python
def _draw_wave_timer(surf, cx, cy, radius, ratio, color):
    pygame.draw.circle(surf, (30, 30, 40), (cx, cy), radius, 2)
    arc_end = 2 * math.pi * ratio
    pts = [(cx, cy)]
    for i in range(int(60 * ratio) + 1):
        theta = -math.pi / 2 + arc_end * i / max(1, int(60 * ratio))
        pts.append((cx + radius * math.cos(theta),
                     cy + radius * math.sin(theta)))
    if len(pts) >= 3:
        pygame.draw.polygon(surf, color, pts)
    # inner rose decoration (5-petal, within filled arc)
    for i in range(48):
        theta = 2 * math.pi * i / 48
        rv = (radius - 4) * abs(math.cos(2.5 * theta))
        if theta - math.pi / 2 > arc_end:
            continue
        pygame.draw.circle(surf, (255, 255, 255, 40),
                           (int(cx + rv * math.cos(theta - math.pi/2)),
                            int(cy + rv * math.sin(theta - math.pi/2))), 1)
```

---

### 4.11 Implementation Plan

#### Phase 4A: Fractal Font

| Task | File | Effort |
|---|---|---|
| Define FRACTAL_GLYPHS dict | `fractal_font.py` (new) | 2 sessions |
| FractalFont class + glyph cache | `fractal_font.py` | 1 session |
| Serif branching system | `fractal_font.py` | 0.5 session |
| Replace all `draw_text()` calls | `gui.py`, `entities.py` | 1 session |
| Benchmark (<2ms/frame) | `fractal_font.py` | 0.5 session |

#### Phase 4B: Panel & Button Overhaul

| Task | File | Effort |
|---|---|---|
| `koch_border()` utility | `gui.py` or `fractal_ui.py` (new) | 0.5 session |
| Radial gradient panel backgrounds | `gui.py` | 1 session |
| Koch-bordered button system | `gui.py` | 1 session |
| Button hover bloom (rose corners) | `gui.py` | 0.5 session |
| Animated panel borders | `gui.py` | 0.5 session |

#### Phase 4C: Bars, Selection, Polish

| Task | File | Effort |
|---|---|---|
| `fractal_bar()` HP/progress/train | `gui.py`, `entities.py` | 1 session |
| Rose/hex/spiral selection rings | `entities.py` | 1 session |
| Minimap border + viewport | `game.py` | 0.5 session |
| Notification dissolution | `gui.py` | 0.5 session |
| Wave timer circular arc | `gui.py` | 0.5 session |

#### Phase 4D: Integration & Performance

| Task | File | Effort |
|---|---|---|
| Profile render pass (<16ms @ 60 FPS) | all | 0.5 session |
| Glyph surface caching | `fractal_font.py` | 0.5 session |
| Koch border caching | `gui.py` | 0.5 session |
| Visual QA (readability) | all | 1 session |

**Total estimate: 12-14 sessions**

---

### 4.12 Critical Files

| File | Changes |
|---|---|
| `fractal_font.py` (NEW) | FractalFont class, glyph defs, serif system, caching |
| `fractal_ui.py` (NEW) | koch_border(), radial_gradient(), fractal_bar(), rose_selection() |
| `gui.py` | Replace all panel/button/bar rendering |
| `entities.py` | Selection ring, building label rendering |
| `game.py` | Minimap frame, select box, wave timer |
| `utils.py` | `draw_text()` → FractalFont, add `draw_text_fractal()` |

---

### 4.13 Performance Budget

**Target**: All UI rendering <= 4ms/frame (25% of 16ms budget)

| Component | Budget | Strategy |
|---|---|---|
| Fractal font | <= 1.5ms | Cache glyph surfaces per (char, size, color) |
| Koch borders | <= 0.5ms | Cache border polylines per (rect, depth) |
| Fractal bars | <= 0.5ms | Pre-render wave pattern, blit slice |
| Rose selections | <= 0.5ms | 60-point polygon per selected unit |
| Gradients | <= 0.5ms | Pre-render gradient surfaces at init |
| Headroom | 0.5ms | Animation parameter updates |

---

### 4.14 Visual Reference Summary

| Current Element | v11 Replacement | Math Basis |
|---|---|---|
| SysFont text | FractalFont runes | L-system strokes + recursive serifs |
| Flat rect panels | Koch-bordered gradient panels | Koch curve (depth 1-2) |
| Flat rect buttons | Koch-bordered bloom buttons | Koch + polar rose corners |
| Flat HP bars | Sine-wave filled bars | Parametric wave modulation |
| Circle selection | Rose/hex/spiral selection rings | Polar curves matching unit type |
| Rect minimap border | Koch-framed minimap | Koch curve depth 2 |
| Flat notifications | Dissolving rune text | Fractal decomposition |
| Rect wave timer | Circular rose-arc timer | Polar rose + pie arc |
| Plain resource icons | Breathing pulse icons | Scale oscillation |
