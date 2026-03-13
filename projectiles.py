import math
import random
import pygame
from constants import (ARROW_SPEED, ARROW_MAX_LIFETIME, ARROW_HIT_RADIUS,
                       GROUND_ARROW_LIFETIME,
                       ARROW_ARC_HEIGHT, ARROW_FLIGHT_TIME, ARROW_TRAIL_LENGTH,
                       TOWER_CANNON_SPEED, TOWER_CANNON_LIFETIME,
                       TOWER_CANNON_HIT_RADIUS,
                       TOWER_EXPLOSIVE_DAMAGE, TOWER_EXPLOSIVE_RADIUS,
                       TOWER_EXPLOSIVE_DIRECT,
                       CANNONBALL_ARC_HEIGHT, CANNONBALL_FLIGHT_TIME,
                       CRATER_DURATION, CRATER_RADIUS_NORMAL,
                       CRATER_RADIUS_EXPLOSIVE,
                       CRATER_BURN_PARTICLES, CRATER_BURN_DURATION,
                       IMPACT_SHAKE_AMOUNT, IMPACT_SHAKE_DURATION,
                       TILE_SIZE, MAP_COLS, MAP_ROWS)
from entity_base import _process_combat_hit
from utils import dist


# ---------------------------------------------------------------------------
# Shared: parabolic arc interpolation
# ---------------------------------------------------------------------------
def _arc_position(sx, sy, tx, ty, t_frac, arc_height):
    """Interpolate along a parabolic arc from (sx,sy) to (tx,ty).
    t_frac: 0.0 at launch, 1.0 at landing.
    Returns (x, y) world position.
    """
    x = sx + (tx - sx) * t_frac
    y = sy + (ty - sy) * t_frac - arc_height * 4.0 * t_frac * (1.0 - t_frac)
    return x, y


def _arc_tangent_angle(sx, sy, tx, ty, t_frac, arc_height):
    """Get the angle of the tangent at t_frac along the arc.
    Used to tilt arrows/cannonballs along their trajectory.
    """
    dx = tx - sx
    dy = (ty - sy) - arc_height * 4.0 * (1.0 - 2.0 * t_frac)
    return math.atan2(dy, dx)


# ---------------------------------------------------------------------------
# Arrow  (v10_5 — parabolic arc, elegant trajectory, option A hit detection)
# ---------------------------------------------------------------------------
class Arrow:
    def __init__(self, x, y, target_x, target_y, damage, owner,
                 source_unit=None, spread_angle=0.0):
        self.start_x, self.start_y = float(x), float(y)
        self.damage = damage
        self.owner = owner
        self.source_unit = source_unit
        self.alive = True

        # Apply spread: rotate the target point around the launch point
        dx, dy = target_x - x, target_y - y
        d = math.hypot(dx, dy)
        if spread_angle != 0.0 and d > 1:
            cos_a = math.cos(spread_angle)
            sin_a = math.sin(spread_angle)
            rdx = dx * cos_a - dy * sin_a
            rdy = dx * sin_a + dy * cos_a
            target_x = x + rdx
            target_y = y + rdy

        self.target_x, self.target_y = float(target_x), float(target_y)

        # Flight time scales with distance (farther = longer arc)
        self.flight_time = max(0.3, ARROW_FLIGHT_TIME * (d / 180.0))
        self.arc_height = ARROW_ARC_HEIGHT * min(1.5, d / 150.0)
        self.elapsed = 0.0

        # Current interpolated position
        self.x, self.y = float(x), float(y)

        # Trail: ring buffer of recent positions
        self.trail = []

        # Grounded state (stuck in ground after miss/expire)
        self.grounded = False
        self.ground_timer = 0.0
        self.impact_angle = 0.0  # angle arrow sticks at

    def update(self, dt, game):
        if self.grounded:
            self.ground_timer -= dt
            if self.ground_timer <= 0:
                self.alive = False
            return

        # store trail point
        self.trail.append((self.x, self.y))
        if len(self.trail) > ARROW_TRAIL_LENGTH:
            self.trail.pop(0)

        self.elapsed += dt
        t_frac = min(1.0, self.elapsed / self.flight_time)
        self.x, self.y = _arc_position(
            self.start_x, self.start_y,
            self.target_x, self.target_y,
            t_frac, self.arc_height)

        # Option A: check for hits along the flight path (can hit things in the way)
        if self.owner == "player":
            targets = game.enemy_units
        else:
            targets = game.player_units + game.player_buildings

        # Only check hits in the descent phase (t_frac > 0.3) to avoid hitting
        # things right at the archer's feet
        if t_frac > 0.3:
            for t in targets:
                if not t.alive:
                    continue
                if dist(self.x, self.y, t.x, t.y) < ARROW_HIT_RADIUS:
                    t.take_damage(self.damage, self.source_unit)
                    _process_combat_hit(self.source_unit, t, game, "arrow")
                    self.alive = False
                    return

        # Landed (reached target) or expired
        if t_frac >= 1.0 or self.elapsed > ARROW_MAX_LIFETIME:
            self.impact_angle = _arc_tangent_angle(
                self.start_x, self.start_y,
                self.target_x, self.target_y,
                min(1.0, t_frac), self.arc_height)
            self.grounded = True
            self.ground_timer = GROUND_ARROW_LIFETIME

        # Off map check
        if (self.x < 0 or self.x > MAP_COLS * TILE_SIZE
                or self.y < 0 or self.y > MAP_ROWS * TILE_SIZE):
            self.impact_angle = _arc_tangent_angle(
                self.start_x, self.start_y,
                self.target_x, self.target_y,
                t_frac, self.arc_height)
            self.grounded = True
            self.ground_timer = GROUND_ARROW_LIFETIME

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom

        if self.grounded:
            # Arrow stuck in ground at impact angle
            length = max(4, int(8 * z))
            color = (120, 100, 80)
            cos_a = math.cos(self.impact_angle)
            sin_a = math.sin(self.impact_angle)
            ex = sx + int(cos_a * length)
            ey = sy + int(sin_a * length)
            pygame.draw.line(surf, color, (sx, sy), (ex, ey), max(1, int(z)))
            # fletching nock at the back
            bx = sx - int(cos_a * length * 0.3)
            by = sy - int(sin_a * length * 0.3)
            pygame.draw.circle(surf, (90, 75, 60), (bx, by), max(1, int(z)))
        else:
            # In flight: tilted along arc tangent
            t_frac = min(1.0, self.elapsed / self.flight_time) if self.flight_time > 0 else 0
            angle = _arc_tangent_angle(
                self.start_x, self.start_y,
                self.target_x, self.target_y,
                t_frac, self.arc_height)
            length = max(5, int(12 * z))
            color = (255, 240, 120) if self.owner == "player" else (255, 120, 120)

            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # tip
            hx = sx + int(cos_a * length * 0.5)
            hy = sy + int(sin_a * length * 0.5)
            # tail
            tx = sx - int(cos_a * length * 0.5)
            ty = sy - int(sin_a * length * 0.5)
            pygame.draw.line(surf, color, (tx, ty), (hx, hy), max(1, int(2 * z)))
            # arrowhead
            pygame.draw.circle(surf, color, (hx, hy), max(1, int(2 * z)))

            # Afterimage trail (fading ghost points)
            if self.trail:
                for i, (px, py) in enumerate(self.trail):
                    tpx, tpy = cam.world_to_screen(px, py)
                    alpha_frac = (i + 1) / (len(self.trail) + 1)
                    fade = int(alpha_frac * 120)
                    trail_col = (fade, fade, int(fade * 0.6))
                    r = max(1, int(z * alpha_frac * 1.5))
                    pygame.draw.circle(surf, trail_col, (tpx, tpy), r)


# ---------------------------------------------------------------------------
# Cannonball  (v10_5 — low parabolic arc, option B hit detection, craters)
# ---------------------------------------------------------------------------
class Cannonball:
    def __init__(self, x, y, target_x, target_y, damage, owner, explosive=False):
        self.start_x, self.start_y = float(x), float(y)
        self.target_x, self.target_y = float(target_x), float(target_y)
        self.damage = damage
        self.owner = owner
        self.explosive = explosive
        self.alive = True

        d = math.hypot(target_x - x, target_y - y)
        self.flight_time = max(0.15, CANNONBALL_FLIGHT_TIME * (d / 180.0))
        self.arc_height = CANNONBALL_ARC_HEIGHT
        self.elapsed = 0.0

        self.x, self.y = float(x), float(y)

    def update(self, dt, game):
        self.elapsed += dt
        t_frac = min(1.0, self.elapsed / self.flight_time)
        self.x, self.y = _arc_position(
            self.start_x, self.start_y,
            self.target_x, self.target_y,
            t_frac, self.arc_height)

        # Option B: damage on landing — check target proximity at impact point
        if t_frac >= 1.0:
            self._on_impact(game)
            return

        # Lifetime safety
        if self.elapsed > TOWER_CANNON_LIFETIME:
            self._on_impact(game)
            return

        # Off map
        if (self.x < 0 or self.x > MAP_COLS * TILE_SIZE
                or self.y < 0 or self.y > MAP_ROWS * TILE_SIZE):
            self._on_impact(game)

    def _on_impact(self, game):
        """Cannonball lands — deal damage, create crater, shake camera."""
        targets = game.enemy_units
        hit_anyone = False

        if self.explosive:
            # Check for direct hit (anything at landing spot)
            for t in targets:
                if not t.alive:
                    continue
                if dist(self.x, self.y, t.x, t.y) < TOWER_CANNON_HIT_RADIUS:
                    t.take_damage(TOWER_EXPLOSIVE_DIRECT)
                    _process_combat_hit(None, t, game, "tower")
                    hit_anyone = True
            # AoE splash
            for e in targets:
                if not e.alive:
                    continue
                if dist(self.x, self.y, e.x, e.y) < TOWER_EXPLOSIVE_RADIUS:
                    e.take_damage(TOWER_EXPLOSIVE_DAMAGE)
                    _process_combat_hit(None, e, game, "tower")
                    hit_anyone = True
            # Explosion VFX + crater
            game.explosions.append(Explosion(self.x, self.y))
            game.craters.append(Crater(self.x, self.y, explosive=True))
            # Screen shake
            if hasattr(game, 'camera') and hasattr(game.camera, 'shake'):
                game.camera.shake(IMPACT_SHAKE_AMOUNT, IMPACT_SHAKE_DURATION)
        else:
            # Normal cannonball: check landing proximity
            for t in targets:
                if not t.alive:
                    continue
                if dist(self.x, self.y, t.x, t.y) < TOWER_CANNON_HIT_RADIUS:
                    t.take_damage(self.damage)
                    _process_combat_hit(None, t, game, "tower")
                    hit_anyone = True
                    break  # single-target
            # Always leave a crater (miss or hit)
            game.craters.append(Crater(self.x, self.y, explosive=False))
            # Subtle shake for normal cannonball
            if hasattr(game, 'camera') and hasattr(game.camera, 'shake'):
                game.camera.shake(IMPACT_SHAKE_AMOUNT * 0.5, IMPACT_SHAKE_DURATION * 0.6)

        self.alive = False

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        t_frac = min(1.0, self.elapsed / self.flight_time) if self.flight_time > 0 else 0

        # Heavy dark sphere
        r = max(3, int(6 * z))
        color = (60, 55, 50) if not self.explosive else (160, 80, 20)
        pygame.draw.circle(surf, color, (sx, sy), r)

        # Darker core for weight
        core_r = max(2, int(r * 0.5))
        pygame.draw.circle(surf, (30, 28, 25), (sx, sy), core_r)

        # Thick motion blur trail — heavier and darker than arrows
        angle = _arc_tangent_angle(
            self.start_x, self.start_y,
            self.target_x, self.target_y,
            t_frac, self.arc_height)
        trail_len = max(4, int(r * 3))
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        tx = sx - int(cos_a * trail_len)
        ty = sy - int(sin_a * trail_len)
        pygame.draw.line(surf, (50, 45, 40), (tx, ty), (sx, sy), max(2, int(3 * z)))

        # Explosive: faint orange glow halo
        if self.explosive:
            glow_r = max(4, int(r * 1.8))
            pygame.draw.circle(surf, (120, 60, 15), (sx, sy), glow_r, max(1, int(z)))


# ---------------------------------------------------------------------------
# Crater VFX  (v10_5 — ground scar with optional burning embers)
# ---------------------------------------------------------------------------
class Crater:
    def __init__(self, x, y, explosive=False):
        self.x, self.y = x, y
        self.explosive = explosive
        self.timer = 0.0
        self.duration = CRATER_DURATION
        self.alive = True
        self.radius = CRATER_RADIUS_EXPLOSIVE if explosive else CRATER_RADIUS_NORMAL

        # Burning embers for explosive craters
        self.embers = []
        if explosive:
            for _ in range(CRATER_BURN_PARTICLES):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(8, 25)
                self.embers.append({
                    'x': x, 'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed - random.uniform(5, 15),  # slight upward
                    'life': CRATER_BURN_DURATION * random.uniform(0.5, 1.0),
                    'max_life': CRATER_BURN_DURATION,
                    'size': random.uniform(1.5, 3.5),
                })

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.alive = False
            return
        # Update burning embers
        for e in self.embers:
            if e['life'] > 0:
                e['x'] += e['vx'] * dt
                e['y'] += e['vy'] * dt
                e['vy'] += 30 * dt  # gravity pulls embers down
                e['vx'] *= 0.97     # air drag
                e['life'] -= dt

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        progress = self.timer / self.duration
        fade = max(0.0, 1.0 - progress)

        # Scorched ground circle
        r = max(2, int(self.radius * z))
        if fade > 0.05:
            # Dark brown/black scar
            darkness = int(30 * fade)
            scar_col = (darkness, int(darkness * 0.7), int(darkness * 0.3))
            pygame.draw.circle(surf, scar_col, (sx, sy), r)
            # Slightly lighter rim
            rim_col = (int(50 * fade), int(35 * fade), int(15 * fade))
            pygame.draw.circle(surf, rim_col, (sx, sy), r, max(1, int(z)))

        # Burning embers (explosive only)
        for e in self.embers:
            if e['life'] <= 0:
                continue
            ex, ey = cam.world_to_screen(e['x'], e['y'])
            ember_fade = e['life'] / e['max_life']
            # orange → dark red as they cool
            er = min(255, int(255 * ember_fade))
            eg = min(255, int(140 * ember_fade * ember_fade))  # fades faster
            eb = min(255, int(20 * ember_fade))
            esize = max(1, int(e['size'] * z * ember_fade))
            pygame.draw.circle(surf, (er, eg, eb), (ex, ey), esize)


# ---------------------------------------------------------------------------
# Explosion VFX  (v10_1 — Lissajous bloom, v10_5 — leaves crater underneath)
# ---------------------------------------------------------------------------
class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.timer = 0.0
        self.duration = 0.5
        self.alive = True
        self._phase = random.uniform(0, math.pi)  # visual variety

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.duration:
            self.alive = False

    def draw(self, surf, cam):
        sx, sy = cam.world_to_screen(self.x, self.y)
        z = cam.zoom
        progress = self.timer / self.duration
        fade = max(0.0, 1.0 - progress)
        max_r = TOWER_EXPLOSIVE_RADIUS * z

        # Lissajous figure: expanding, rotating star-flower
        a_ratio, b_ratio = 3, 2  # 3:2 produces a trefoil-like figure
        delta = self._phase + progress * math.pi * 2
        n_pts = 48
        A = max_r * progress
        B = A * 0.85
        pts = []
        for i in range(n_pts):
            t = 2 * math.pi * i / n_pts
            lx = A * math.sin(a_ratio * t + delta)
            ly = B * math.sin(b_ratio * t)
            pts.append((sx + int(lx), sy + int(ly)))

        if len(pts) >= 3:
            # bright core → fading outer
            r_val = min(255, int(255 * fade))
            g_val = min(255, int(180 * fade + 60 * progress))
            b_val = min(255, int(40 * fade))
            color = (r_val, g_val, b_val)
            width = max(1, int(3 * z * fade))
            pygame.draw.polygon(surf, color, pts, width)

        # inner ring for extra glow
        if progress < 0.6:
            inner_r = max(2, int(max_r * progress * 0.4))
            pygame.draw.circle(surf, (255, min(255, 200 + int(55 * progress)), 80),
                               (sx, sy), inner_r, max(1, int(2 * z * fade)))
