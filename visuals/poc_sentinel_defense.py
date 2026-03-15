"""
Proof-of-concept: Sentinel Resonance Defense System.

Demonstrates the unified Sentinel defense mechanics:
- Koch snowflake resonance field (passive aura)
- Harmonic Pulse (expanding Koch rings + ally buff)
- Lattice Amplification (merged fields along symmetry axes)
- Dissonance Absorption (spirograph trails from enemy deaths to Sentinel)
- Enemy bleaching effect inside resonance field

Controls:
  SPACE    Trigger harmonic pulse from selected Sentinel
  E        Spawn enemy wave (walks toward Sentinel)
  L        Cycle lattice order (single / D2 / D3)
  1/2      Sentinel level 1 / 2
  ESC      Quit
"""
import pygame
import math
import random
import sys


# --- palette ---
COL_BG = (20, 20, 30)
SENTINEL_STONE = (140, 130, 100)
SENTINEL_GOLD = (218, 165, 32)
RESONANCE_GLOW = (180, 160, 255)
DIVERGENT_RED = (120, 20, 40)
BOUNDARY_WHITE = (240, 235, 220)
ENEMY_COLORS = [
    (80, 80, 100),   # Hollow Warden
    (140, 0, 140),   # Fade Ranger
    (140, 100, 20),  # Thornknight
]

W, H = 1280, 720


def lerp_c(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# --- Koch snowflake ---
def _koch_pts(x1, y1, x2, y2, depth):
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(_koch_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(_koch_pts(ax, ay, px, py, depth - 1))
    pts.extend(_koch_pts(px, py, bx, by, depth - 1))
    pts.extend(_koch_pts(bx, by, x2, y2, depth - 1))
    return pts


def koch_snowflake(cx, cy, size, depth):
    r = size * 0.45
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]
    verts = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]
    all_pts = []
    for i in range(3):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 3]
        all_pts.extend(_koch_pts(x1, y1, x2, y2, depth))
    return all_pts


# --- Sentinel ---
class Sentinel:
    def __init__(self, x, y, level=1):
        self.x, self.y = x, y
        self.level = level
        self.field_radius = 120 if level == 1 else 160
        self.pulse_age = -1  # -1 = no pulse active
        self.pulse_max_age = 1.0

    def trigger_pulse(self):
        self.pulse_age = 0.0

    def update(self, dt):
        if self.pulse_age >= 0:
            self.pulse_age += dt
            if self.pulse_age > self.pulse_max_age:
                self.pulse_age = -1

    def draw(self, surf, game_time):
        # Koch resonance field
        depth = self.level
        pts = koch_snowflake(self.x, self.y, self.field_radius * 2, depth)
        if len(pts) >= 3:
            field_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            int_pts = [(int(p[0]), int(p[1])) for p in pts]
            # Breathing alpha
            breath = 0.7 + 0.3 * math.sin(game_time * math.pi)
            fill_a = int(15 * breath) if self.level == 1 else int(25 * breath)
            pygame.draw.polygon(field_surf, (*RESONANCE_GLOW, fill_a), int_pts)
            border_c = RESONANCE_GLOW if self.level == 1 else SENTINEL_GOLD
            border_a = int(60 * breath) if self.level == 1 else int(100 * breath)
            pygame.draw.polygon(field_surf, (*border_c, border_a), int_pts,
                                max(1, 2))
            surf.blit(field_surf, (0, 0))

        # Harmonic pulse (expanding Koch rings)
        if self.pulse_age >= 0:
            progress = self.pulse_age / self.pulse_max_age
            pulse_r = progress * self.field_radius * 1.5
            alpha = 1.0 - progress
            for ring_i in range(3):
                r = max(5, int(pulse_r - ring_i * 18))
                ring_pts = koch_snowflake(self.x, self.y, r * 2,
                                          2 if ring_i == 0 else 1)
                if len(ring_pts) >= 3:
                    ring_surf = pygame.Surface((W, H), pygame.SRCALPHA)
                    rpts = [(int(p[0]), int(p[1])) for p in ring_pts]
                    c = lerp_c(RESONANCE_GLOW, SENTINEL_GOLD, progress)
                    a = int(alpha * 180 * (1.0 - ring_i * 0.3))
                    w = 2 if ring_i == 0 else 1
                    pygame.draw.polygon(ring_surf, (*c, max(5, a)), rpts, w)
                    surf.blit(ring_surf, (0, 0))

        # Standing stone body
        w_s, h_s = 16, 40
        body = [(self.x - w_s // 2, self.y + h_s // 3),
                (self.x - w_s // 3, self.y - h_s // 3),
                (self.x, self.y - h_s // 2),
                (self.x + w_s // 3, self.y - h_s // 3),
                (self.x + w_s // 2, self.y + h_s // 3)]
        stone_c = SENTINEL_STONE if self.level == 1 else (160, 148, 115)
        pygame.draw.polygon(surf, stone_c, body)
        pygame.draw.polygon(surf, (0, 0, 0), body, 2)

        # Voronoi texture dots
        rng = random.Random(hash((self.x, self.y)))
        for _ in range(5):
            ox = rng.randint(-w_s // 3, w_s // 3)
            oy = rng.randint(-h_s // 3, h_s // 4)
            dot_c = tuple(min(255, c + rng.randint(-12, 12)) for c in stone_c)
            pygame.draw.circle(surf, dot_c, (self.x + ox, self.y + oy), 2)

        # Golden aura
        aura = pygame.Surface((60, 60), pygame.SRCALPHA)
        for ri in range(3):
            a = 22 - ri * 6
            pygame.draw.circle(aura, (*SENTINEL_GOLD, max(0, a)), (30, 30), 15 + ri * 4)
        surf.blit(aura, (self.x - 30, self.y - 30))


# --- Enemy ---
class Enemy:
    def __init__(self, x, y, color_idx=0):
        self.x, self.y = x, y
        self.hp = 1.0
        self.alive = True
        self.color = ENEMY_COLORS[color_idx % len(ENEMY_COLORS)]
        self.base_color = self.color
        self.speed = 30 + random.uniform(-5, 5)
        self.target_x = W // 2
        self.target_y = H // 2
        self.bleach = 0.0  # 0-1, how bleached by resonance
        self.jagged = 0.0  # jaggedness from field damage
        self.death_time = -1
        self.absorption_trail = []

    def update(self, dt, sentinels):
        if self.death_time >= 0:
            self.death_time += dt
            # Update absorption trail (contract toward nearest Sentinel)
            if self.death_time > 0.8:
                self.alive = False
            return

        # Move toward target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 5:
            self.x += dx / dist * self.speed * dt
            self.y += dy / dist * self.speed * dt

        # Check resonance field damage
        in_field = False
        nearest_sentinel = None
        nearest_dist = 9999
        for s in sentinels:
            d = math.sqrt((self.x - s.x) ** 2 + (self.y - s.y) ** 2)
            if d < s.field_radius:
                in_field = True
                field_strength = 1.0 - d / s.field_radius
                self.hp -= 0.4 * field_strength * dt
                self.bleach = min(1.0, self.bleach + 0.5 * field_strength * dt)
                self.jagged = min(1.0, self.jagged + 0.3 * field_strength * dt)
            if d < nearest_dist:
                nearest_dist = d
                nearest_sentinel = s

            # Pulse damage
            if s.pulse_age >= 0:
                pulse_r = s.pulse_age / s.pulse_max_age * s.field_radius * 1.5
                if abs(d - pulse_r) < 20:
                    self.hp -= 0.3 * dt * 10

        if not in_field:
            self.bleach = max(0, self.bleach - 0.3 * dt)
            self.jagged = max(0, self.jagged - 0.2 * dt)

        # Update color based on bleaching
        self.color = lerp_c(self.base_color, (255, 255, 255), self.bleach * 0.4)

        # Death
        if self.hp <= 0 and self.death_time < 0:
            self.death_time = 0
            # Generate absorption trail toward nearest sentinel
            if nearest_sentinel:
                for i in range(5):
                    self.absorption_trail.append({
                        "sx": self.x, "sy": self.y,
                        "tx": nearest_sentinel.x, "ty": nearest_sentinel.y,
                        "delay": i * 0.08,
                    })

    def draw(self, surf, game_time):
        if not self.alive:
            return

        # Death animation: Lissajous bloom + absorption
        if self.death_time >= 0:
            # Lissajous bloom
            n = 40
            bloom_r = 15 * (1.0 - self.death_time / 0.8)
            if bloom_r > 1:
                pts = []
                for i in range(n):
                    t = 2 * math.pi * i / n
                    bx = self.x + bloom_r * math.sin(3 * t + game_time)
                    by = self.y + bloom_r * math.sin(2 * t)
                    pts.append((int(bx), int(by)))
                alpha = int(200 * (1.0 - self.death_time / 0.8))
                bloom_surf = pygame.Surface((W, H), pygame.SRCALPHA)
                if len(pts) >= 3:
                    pygame.draw.polygon(bloom_surf, (255, 180, 80, max(5, alpha)), pts)
                    pygame.draw.polygon(bloom_surf, (255, 220, 100, max(5, alpha)), pts, 1)
                surf.blit(bloom_surf, (0, 0))

            # Spirograph absorption trails
            R, r, d = 4, 2.5, 3
            for trail in self.absorption_trail:
                t_eff = max(0, self.death_time - trail["delay"])
                if t_eff <= 0:
                    continue
                frac = min(1.0, t_eff / 0.5)
                cx = trail["sx"] + (trail["tx"] - trail["sx"]) * frac
                cy = trail["sy"] + (trail["ty"] - trail["sy"]) * frac
                t = t_eff * 15
                sx = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
                sy = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
                c = lerp_c(DIVERGENT_RED, SENTINEL_GOLD, frac)
                dot_r = max(1, int(3 * (1.0 - frac)))
                pygame.draw.circle(surf, c, (int(cx + sx), int(cy + sy)), dot_r)
            return

        # Living enemy: jagged polar shape
        n = 40
        base_r = 10
        pts = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            r = base_r
            # Jaggedness from field damage
            r += self.jagged * 3 * math.sin((17 + 8 * self.jagged) * theta)
            pts.append((int(self.x + r * math.cos(theta)),
                        int(self.y + r * math.sin(theta))))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, self.color, pts)
            # Enemy outline
            outline_c = lerp_c(self.base_color, (200, 200, 200), self.bleach * 0.5)
            pygame.draw.polygon(surf, outline_c, pts, 1)

        # Bleach shimmer
        if self.bleach > 0.2:
            shimmer = pygame.Surface((30, 30), pygame.SRCALPHA)
            a = int(self.bleach * 40)
            pygame.draw.circle(shimmer, (255, 255, 255, a), (15, 15), 12)
            surf.blit(shimmer, (int(self.x - 15), int(self.y - 15)))

        # HP bar
        bar_w = 20
        bar_h = 3
        pygame.draw.rect(surf, (40, 40, 40),
                         (int(self.x - bar_w // 2), int(self.y - 16), bar_w, bar_h))
        fill_w = int(bar_w * max(0, self.hp))
        hp_c = lerp_c((200, 40, 40), (40, 200, 40), self.hp)
        pygame.draw.rect(surf, hp_c,
                         (int(self.x - bar_w // 2), int(self.y - 16), fill_w, bar_h))


# --- Lattice configurations ---
LATTICE_CONFIGS = {
    "single": [(W // 2, H // 2)],
    "D2": [(W // 2 - 100, H // 2), (W // 2 + 100, H // 2),
           (W // 2, H // 2 - 100), (W // 2, H // 2 + 100)],
    "D3": [(W // 2 + int(130 * math.cos(2 * math.pi * i / 6 - math.pi / 2)),
            H // 2 + int(130 * math.sin(2 * math.pi * i / 6 - math.pi / 2)))
           for i in range(6)],
}
LATTICE_NAMES = ["single", "D2", "D3"]


def draw_lattice_axes(surf, sentinels, lattice_name):
    """Draw symmetry axes between Sentinels."""
    if lattice_name == "D2" and len(sentinels) >= 4:
        # Two perpendicular axes
        for i in range(2):
            p1 = sentinels[i * 2]
            p2 = sentinels[i * 2 + 1]
            pygame.draw.line(surf, SENTINEL_GOLD,
                             (p1.x, p1.y), (p2.x, p2.y), 1)
    elif lattice_name == "D3" and len(sentinels) >= 6:
        # Three axes through opposite pairs
        for i in range(3):
            p1 = sentinels[i]
            p2 = sentinels[(i + 3) % 6]
            pygame.draw.line(surf, SENTINEL_GOLD,
                             (p1.x, p1.y), (p2.x, p2.y), 1)
        # Fill zone
        hex_pts = [(s.x, s.y) for s in sentinels]
        fill_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(fill_surf, (*SENTINEL_GOLD, 12), hex_pts)
        surf.blit(fill_surf, (0, 0))


# --- main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Sentinel Resonance Defense")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    font_lg = pygame.font.SysFont(None, 32)

    lattice_idx = 0
    sentinel_level = 1
    sentinels = [Sentinel(x, y, sentinel_level)
                 for x, y in LATTICE_CONFIGS[LATTICE_NAMES[lattice_idx]]]
    enemies = []
    game_time = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        game_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    for s in sentinels:
                        s.trigger_pulse()
                elif event.key == pygame.K_e:
                    # Spawn enemy wave from random edge
                    for _ in range(5):
                        edge = random.choice(["top", "bottom", "left", "right"])
                        if edge == "top":
                            ex, ey = random.randint(100, W - 100), 20
                        elif edge == "bottom":
                            ex, ey = random.randint(100, W - 100), H - 20
                        elif edge == "left":
                            ex, ey = 20, random.randint(100, H - 100)
                        else:
                            ex, ey = W - 20, random.randint(100, H - 100)
                        enemies.append(Enemy(ex, ey, random.randint(0, 2)))
                elif event.key == pygame.K_l:
                    lattice_idx = (lattice_idx + 1) % len(LATTICE_NAMES)
                    sentinels = [Sentinel(x, y, sentinel_level)
                                 for x, y in LATTICE_CONFIGS[LATTICE_NAMES[lattice_idx]]]
                elif event.key == pygame.K_1:
                    sentinel_level = 1
                    sentinels = [Sentinel(x, y, 1)
                                 for x, y in LATTICE_CONFIGS[LATTICE_NAMES[lattice_idx]]]
                elif event.key == pygame.K_2:
                    sentinel_level = 2
                    sentinels = [Sentinel(x, y, 2)
                                 for x, y in LATTICE_CONFIGS[LATTICE_NAMES[lattice_idx]]]

        # Update
        for s in sentinels:
            s.update(dt)
        for e in enemies:
            e.update(dt, sentinels)
        enemies = [e for e in enemies if e.alive]

        # Draw
        screen.fill(COL_BG)

        # Terrain hint (subtle green)
        for ty in range(0, H, 32):
            for tx in range(0, W, 32):
                noise = random.Random(tx * 997 + ty).randint(-4, 4)
                c = tuple(max(0, min(255, 25 + noise)) for _ in range(3))
                pygame.draw.rect(screen, c, (tx, ty, 32, 32))

        # Lattice axes
        draw_lattice_axes(screen, sentinels, LATTICE_NAMES[lattice_idx])

        # Sentinels
        for s in sentinels:
            s.draw(screen, game_time)

        # Enemies
        for e in enemies:
            e.draw(screen, game_time)

        # HUD
        title = f"Sentinel Resonance Defense  |  Lattice: {LATTICE_NAMES[lattice_idx].upper()}  |  Level: {sentinel_level}  |  Enemies: {len(enemies)}"
        screen.blit(font_lg.render("Sentinel Defense PoC", True, SENTINEL_GOLD), (20, 10))
        screen.blit(font.render(title, True, (180, 180, 200)), (20, 45))
        ctrl = "SPACE: pulse  E: spawn enemies  L: lattice  1/2: level  ESC: quit"
        screen.blit(font.render(ctrl, True, (120, 120, 140)), (20, H - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
