"""
Proof-of-concept: Terrain textures & visual effects (VDD Phase 4).

- Value-noise terrain tiles (grass, stone, sand, water with shimmer)
- Parametric arrow projectiles
- Spirograph-trail cannonballs
- Lissajous bloom explosions
- Breathing polar-rose selection ring

Controls:
  1/2/3/4  Switch terrain (grass / stone / water / sand)
  A        Fire arrow projectile
  C        Fire cannonball with spirograph trail
  S        Toggle selection ring
  Click    Spawn Lissajous explosion
  ESC      Quit
"""
import pygame
import math
import random
import sys

# --- palette ---
COL_BG = (20, 20, 30)
TERRAIN_GRASS = (46, 139, 87)
TERRAIN_GRASS2 = (34, 120, 70)
WATER_BLUE = (30, 80, 160)
WATER_BLUE2 = (40, 100, 180)
STONE_GRAY = (160, 150, 130)
STONE_GRAY2 = (140, 135, 115)
SAND_TAN = (194, 178, 128)
TERRAIN_GOLD = (218, 165, 32)
FORGE_ORANGE = (255, 140, 40)
SOLDIER_RED = (200, 60, 60)
ARCHER_GREEN = (50, 190, 50)
WORKER_BLUE = (50, 130, 220)
GLOW_WHITE = (240, 235, 220)

W, H = 1280, 720
TILE = 64
COLS, ROWS = W // TILE + 1, H // TILE + 1


# ── value noise ──────────────────────────────────────────────
class ValueNoise:
    def __init__(self, seed=42):
        rng = random.Random(seed)
        self.perm = list(range(256))
        rng.shuffle(self.perm)
        self.perm *= 2
        self.grads = [rng.uniform(-1, 1) for _ in range(512)]

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def noise2d(self, x, y):
        xi, yi = int(math.floor(x)) & 255, int(math.floor(y)) & 255
        xf, yf = x - math.floor(x), y - math.floor(y)
        u, v = self._fade(xf), self._fade(yf)
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        g = self.grads
        x1 = g[aa] * (1 - u) + g[ba] * u
        x2 = g[ab] * (1 - u) + g[bb] * u
        return x1 * (1 - v) + x2 * v

    def fbm(self, x, y, octaves=4):
        val, amp, freq = 0, 1, 1
        for _ in range(octaves):
            val += self.noise2d(x * freq, y * freq) * amp
            amp *= 0.5
            freq *= 2
        return val


noise = ValueNoise()


def lerp_c(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def render_terrain_tile(surf, tx, ty, terrain, time_acc):
    """Render a single tile with noise-based texture."""
    for py in range(TILE):
        for px in range(TILE):
            sx = (tx * TILE + px) / 80.0
            sy = (ty * TILE + py) / 80.0
            n = noise.fbm(sx, sy, 3) * 0.5 + 0.5
            n = max(0, min(1, n))

            if terrain == "grass":
                c = lerp_c(TERRAIN_GRASS2, TERRAIN_GRASS, n)
            elif terrain == "stone":
                c = lerp_c(STONE_GRAY2, STONE_GRAY, n)
                # crystalline flecks
                if noise.noise2d(sx * 5, sy * 5) > 0.7:
                    c = lerp_c(c, GLOW_WHITE, 0.2)
            elif terrain == "sand":
                dark = (170, 155, 105)
                c = lerp_c(dark, SAND_TAN, n)
            elif terrain == "water":
                shimmer = math.sin(time_acc * 2.0 + sx * 3 + sy * 2) * 0.15
                n2 = max(0, min(1, n + shimmer))
                c = lerp_c(WATER_BLUE, WATER_BLUE2, n2)
            else:
                c = COL_BG
            surf.set_at((px, py), c)


# ── pre-render terrain cache ────────────────────────────────
def build_terrain_cache(terrain):
    cache = {}
    for ty in range(ROWS):
        for tx in range(COLS):
            s = pygame.Surface((TILE, TILE))
            render_terrain_tile(s, tx, ty, terrain, 0)
            cache[(tx, ty)] = s
    return cache


# ── projectiles ─────────────────────────────────────────────
class Arrow:
    def __init__(self, x, y, angle=0):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 600
        self.alive = True
        self.age = 0

    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        self.age += dt
        if self.x < -50 or self.x > W + 50 or self.y < -50 or self.y > H + 50:
            self.alive = False

    def draw(self, surf):
        tip_x = self.x + math.cos(self.angle) * 18
        tip_y = self.y + math.sin(self.angle) * 18
        tail_x = self.x - math.cos(self.angle) * 14
        tail_y = self.y - math.sin(self.angle) * 14
        # shaft
        pygame.draw.line(surf, (240, 235, 220), (int(tail_x), int(tail_y)),
                         (int(tip_x), int(tip_y)), 2)
        # arrowhead
        perp = self.angle + math.pi / 2
        hx1 = tip_x - math.cos(self.angle) * 6 + math.cos(perp) * 3
        hy1 = tip_y - math.sin(self.angle) * 6 + math.sin(perp) * 3
        hx2 = tip_x - math.cos(self.angle) * 6 - math.cos(perp) * 3
        hy2 = tip_y - math.sin(self.angle) * 6 - math.sin(perp) * 3
        pygame.draw.polygon(surf, (240, 235, 220), [
            (int(tip_x), int(tip_y)), (int(hx1), int(hy1)), (int(hx2), int(hy2))])
        # fletching
        for m in [1, -1]:
            fx = tail_x + math.cos(perp) * 4 * m
            fy = tail_y + math.sin(perp) * 4 * m
            pygame.draw.line(surf, (160, 140, 100),
                             (int(tail_x), int(tail_y)), (int(fx), int(fy)), 1)


class Cannonball:
    def __init__(self, x, y, angle=0):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 300
        self.alive = True
        self.trail = []
        self.age = 0

    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        self.age += dt
        # spirograph trail points
        R, r, d = 5, 3, 5
        t = self.age * 8
        sx = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
        sy = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
        self.trail.append((self.x + sx * 1.5, self.y + sy * 1.5, self.age))
        # trim old trail
        self.trail = [(x, y, a) for x, y, a in self.trail if self.age - a < 0.8]
        if self.x < -50 or self.x > W + 50 or self.y < -50 or self.y > H + 50:
            self.alive = False

    def draw(self, surf):
        # trail
        for tx, ty, a in self.trail:
            alpha = max(0, 1 - (self.age - a) / 0.8)
            c = lerp_c(SOLDIER_RED, FORGE_ORANGE, alpha)
            r = max(1, int(3 * alpha))
            pygame.draw.circle(surf, c, (int(tx), int(ty)), r)
        # ball
        pygame.draw.circle(surf, (80, 80, 80), (int(self.x), int(self.y)), 5)
        pygame.draw.circle(surf, (120, 120, 120), (int(self.x), int(self.y)), 5, 1)


# ── explosions ──────────────────────────────────────────────
class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.age = 0
        self.duration = 0.8
        self.alive = True
        # debris particles
        self.debris = []
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(60, 200)
            self.debris.append([self.x, self.y, math.cos(angle) * speed,
                                math.sin(angle) * speed])

    def update(self, dt):
        self.age += dt
        if self.age > self.duration:
            self.alive = False
        for p in self.debris:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[2] *= 0.95
            p[3] *= 0.95

    def draw(self, surf):
        t = self.age / self.duration
        if t >= 1:
            return
        radius = 10 + t * 60
        alpha = 1.0 - t

        # Lissajous curves (3 overlapping)
        ratios = [(3, 2, 0), (5, 4, math.pi / 4), (3, 4, math.pi / 3)]
        for a_r, b_r, phase in ratios:
            pts = []
            for i in range(80):
                th = 2 * math.pi * i / 80
                lx = self.x + radius * math.sin(a_r * th + phase) * alpha
                ly = self.y + radius * math.sin(b_r * th) * alpha
                pts.append((int(lx), int(ly)))
            # color shift: white -> orange -> red
            if t < 0.3:
                c = lerp_c(GLOW_WHITE, FORGE_ORANGE, t / 0.3)
            else:
                c = lerp_c(FORGE_ORANGE, SOLDIER_RED, (t - 0.3) / 0.7)
            if len(pts) >= 2:
                pygame.draw.lines(surf, c, True, pts, max(1, int(3 * alpha)))

        # debris
        for p in self.debris:
            d_alpha = max(0, 1 - t * 1.5)
            c = lerp_c(FORGE_ORANGE, (80, 60, 40), t)
            r = max(1, int(3 * d_alpha))
            pygame.draw.circle(surf, c, (int(p[0]), int(p[1])), r)


# ── selection ring ──────────────────────────────────────────
class SelectionRing:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.time = 0
        self.visible = True

    def update(self, dt):
        self.time += dt

    def draw(self, surf, radius=40):
        if not self.visible:
            return
        # breathing pulse
        r = radius * (1.0 + 0.08 * math.sin(self.time * 3))
        # polar rose k=3 (6 petals), slowly rotating
        rot = self.time * 0.5
        pts = []
        n = 120
        for i in range(n):
            theta = rot + 2 * math.pi * i / n
            rv = abs(math.cos(3 * theta)) * r
            x = self.x + rv * math.cos(theta)
            y = self.y + rv * math.sin(theta)
            pts.append((int(x), int(y)))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, self.color, pts, 2)


# ── main ────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Terrain & Effects (Phase 4)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    font_lg = pygame.font.SysFont(None, 32)

    terrain = "grass"
    terrain_cache = build_terrain_cache(terrain)
    water_time = 0.0
    time_acc = 0.0

    arrows = []
    cannonballs = []
    explosions = []
    sel_ring = SelectionRing(W // 2, H // 2, WORKER_BLUE)
    show_ring = True

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        time_acc += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    terrain = "grass"
                    terrain_cache = build_terrain_cache(terrain)
                elif event.key == pygame.K_2:
                    terrain = "stone"
                    terrain_cache = build_terrain_cache(terrain)
                elif event.key == pygame.K_3:
                    terrain = "water"
                    terrain_cache = {}  # water re-renders each frame
                elif event.key == pygame.K_4:
                    terrain = "sand"
                    terrain_cache = build_terrain_cache(terrain)
                elif event.key == pygame.K_a:
                    arrows.append(Arrow(50, random.randint(100, H - 100),
                                        random.uniform(-0.3, 0.3)))
                elif event.key == pygame.K_c:
                    cannonballs.append(Cannonball(50, random.randint(100, H - 100),
                                                  random.uniform(-0.2, 0.2)))
                elif event.key == pygame.K_s:
                    show_ring = not show_ring
                    sel_ring.visible = show_ring
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                explosions.append(Explosion(mx, my))

        # update
        for a in arrows:
            a.update(dt)
        arrows = [a for a in arrows if a.alive]
        for c in cannonballs:
            c.update(dt)
        cannonballs = [c for c in cannonballs if c.alive]
        for e in explosions:
            e.update(dt)
        explosions = [e for e in explosions if e.alive]
        sel_ring.update(dt)

        # draw terrain
        if terrain == "water":
            # re-render water tiles for shimmer (only visible area)
            for ty in range(ROWS):
                for tx in range(COLS):
                    s = pygame.Surface((TILE, TILE))
                    render_terrain_tile(s, tx, ty, "water", time_acc)
                    screen.blit(s, (tx * TILE, ty * TILE))
        else:
            for ty in range(ROWS):
                for tx in range(COLS):
                    if (tx, ty) in terrain_cache:
                        screen.blit(terrain_cache[(tx, ty)], (tx * TILE, ty * TILE))

        # draw entities
        for a in arrows:
            a.draw(screen)
        for c in cannonballs:
            c.draw(screen)
        for e in explosions:
            e.draw(screen)
        sel_ring.draw(screen)

        # HUD
        fps = clock.get_fps()
        info = f"Terrain: {terrain}  |  FPS: {fps:.0f}  |  Ring: {'ON' if show_ring else 'OFF'}"
        screen.blit(font_lg.render("Terrain & Effects PoC", True, TERRAIN_GOLD), (20, 10))
        screen.blit(font.render(info, True, (180, 180, 200)), (20, 45))
        ctrl = "1-4: terrain  A: arrow  C: cannonball  Click: explosion  S: ring  ESC: quit"
        screen.blit(font.render(ctrl, True, (120, 120, 140)), (20, H - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
