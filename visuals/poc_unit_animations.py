"""
Proof-of-concept: Unit lifecycle animations (VDD Phase 2.5).

Demonstrates parametric animation of unit shapes through math-driven
parameter oscillation: idle breathing, movement lean, attack lunge,
damage flash, and death dissolve sequences.

Controls:
  1/2/3       Select unit type (worker / soldier / archer)
  SPACE       Cycle state (idle -> move -> attack -> hit -> die -> idle)
  R           Reset current animation
  E           Toggle enemy variant
  LEFT/RIGHT  Change rank
  ESC         Quit
"""
import pygame
import math
import random
import sys

# --- palette ---
COL_BG = (20, 20, 30)
WORKER_BLUE = (50, 130, 220)
SOLDIER_RED = (200, 60, 60)
ARCHER_GREEN = (50, 190, 50)
RANK_COLORS = {
    0: (140, 140, 140), 1: (205, 127, 50), 2: (192, 192, 210),
    3: (255, 215, 0), 4: (80, 180, 255),
}
ENEMY_WORKER = (25, 35, 55)
ENEMY_SOLDIER = (35, 12, 12)
ENEMY_ARCHER = (35, 10, 30)
GLOW_WHITE = (240, 235, 220)

W, H = 1280, 720


def lerp_c(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ── shape helpers ────────────────────────────────────────────
def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=120,
                     width=0, rotation=0.0, squash_angle=None, squash_amt=0.0):
    points = []
    for i in range(n_points):
        theta = rotation + 2 * math.pi * i / n_points
        r = r_func(theta) * radius
        if squash_angle is not None:
            angle_diff = theta - squash_angle
            r *= (1.0 + squash_amt * math.cos(angle_diff))
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    if len(points) >= 3:
        if width == 0:
            pygame.draw.polygon(surf, color, points)
        else:
            pygame.draw.polygon(surf, color, points, width)
    return points


def hex_shape(n_power=4.0):
    def r_func(theta):
        ct, st = abs(math.cos(theta)), abs(math.sin(theta))
        d = ct ** n_power + st ** n_power
        return 1.0 / (d ** (1.0 / n_power)) if d > 1e-10 else 1.0
    return r_func


def blade_shape(k, sharpness=0.6):
    def r_func(theta):
        v = abs(math.cos(k * theta))
        return v ** sharpness if v > 1e-10 else 0.0
    return r_func


def rose_shape(k):
    def r_func(theta):
        return abs(math.cos(k * theta))
    return r_func


# ── animated unit class ─────────────────────────────────────
STATES = ["idle", "moving", "attacking", "hit", "dying"]


class AnimatedUnit:
    def __init__(self, unit_type, x, y):
        self.unit_type = unit_type
        self.x, self.y = x, y
        self.rank = 0
        self.enemy = False
        self.state = "idle"
        self._anim_time = random.uniform(0, 10)
        self._anim_flash = 0.0
        self._anim_attack = 0.0
        self._anim_death = 0.0
        self._anim_dying = False
        self._death_fragments = []
        self._move_angle = 0.3  # demo angle

    def set_state(self, state):
        self.state = state
        if state == "hit":
            self._anim_flash = 1.0
        elif state == "attacking":
            self._anim_attack = 1.0
        elif state == "dying":
            self._anim_dying = True
            self._anim_death = 0.0
            self._generate_death_fragments()

    def reset(self):
        self._anim_flash = 0.0
        self._anim_attack = 0.0
        self._anim_death = 0.0
        self._anim_dying = False
        self._death_fragments = []

    def _generate_death_fragments(self):
        self._death_fragments = []
        n = 12 if self.unit_type == "worker" else 8
        for i in range(n):
            angle = 2 * math.pi * i / n + random.uniform(-0.3, 0.3)
            speed = random.uniform(30, 100)
            self._death_fragments.append({
                "x": self.x, "y": self.y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "rot": random.uniform(0, math.pi),
                "rot_speed": random.uniform(-5, 5),
                "size": random.uniform(4, 12),
            })

    def update(self, dt):
        self._anim_time += dt
        if self._anim_flash > 0:
            self._anim_flash = max(0, self._anim_flash - dt / 0.12)
        if self._anim_attack > 0:
            self._anim_attack = max(0, self._anim_attack - dt / 0.18)
        if self._anim_dying:
            self._anim_death = min(1.0, self._anim_death + dt / 0.6)
            for f in self._death_fragments:
                f["x"] += f["vx"] * dt
                f["y"] += f["vy"] * dt
                f["vx"] *= 0.96
                f["vy"] *= 0.96
                f["rot"] += f["rot_speed"] * dt
        # auto-transition from hit back to idle
        if self.state == "hit" and self._anim_flash <= 0:
            self.state = "idle"

    def draw(self, surf, radius=80):
        if self._anim_dying and self._anim_death >= 1.0:
            return

        # base color
        if self.unit_type == "worker":
            base_color = ENEMY_WORKER if self.enemy else WORKER_BLUE
        elif self.unit_type == "soldier":
            base_color = ENEMY_SOLDIER if self.enemy else SOLDIER_RED
        else:
            base_color = ENEMY_ARCHER if self.enemy else ARCHER_GREEN

        # damage flash
        color = base_color
        if self._anim_flash > 0:
            flash_t = self._anim_flash ** 2
            flash_target = (200, 40, 40) if self.enemy else (255, 255, 255)
            color = lerp_c(base_color, flash_target, flash_t * 0.7)

        # death alpha
        if self._anim_dying:
            alpha = 1.0 - self._anim_death
        else:
            alpha = 1.0

        # radius mods
        r_mult = 1.0
        rot_offset = 0.0
        squash_angle = None
        squash_amt = 0.0

        if self.state == "idle" and not self._anim_dying:
            breath = math.sin(self._anim_time * 1.8)
            r_mult = 1.0 + 0.03 * breath
            rot_offset = 0.01 * math.sin(self._anim_time * 0.7)
        elif self.state == "moving":
            squash_angle = self._move_angle
            squash_amt = 0.12
            r_mult = 1.0 + 0.02 * math.sin(self._anim_time * 6)
            if self.unit_type == "worker":
                rot_offset = 0.04 * math.sin(self._anim_time * 6)
        elif self.state == "attacking":
            lunge = self._anim_attack
            r_mult = 1.0 + 0.15 * lunge
        elif self.state == "dying":
            r_mult = 1.0 - 0.3 * self._anim_death

        eff_radius = radius * r_mult * alpha

        if self.unit_type == "worker":
            self._draw_worker(surf, eff_radius, color, rot_offset, squash_angle, squash_amt)
        elif self.unit_type == "soldier":
            self._draw_soldier(surf, eff_radius, color, rot_offset, squash_angle, squash_amt)
        else:
            self._draw_archer(surf, eff_radius, color, rot_offset, squash_angle, squash_amt)

        # death fragments
        if self._anim_dying:
            frag_alpha = max(0, 1.0 - self._anim_death * 1.5)
            for f in self._death_fragments:
                c = lerp_c(color, COL_BG, 1 - frag_alpha)
                sz = max(1, int(f["size"] * frag_alpha))
                if self.unit_type == "worker":
                    # triangular fragments
                    pts = []
                    for j in range(3):
                        a = f["rot"] + 2 * math.pi * j / 3
                        pts.append((int(f["x"] + sz * math.cos(a)),
                                    int(f["y"] + sz * math.sin(a))))
                    pygame.draw.polygon(surf, c, pts)
                elif self.unit_type == "soldier":
                    # petal-like curved fragments
                    pts = []
                    for j in range(20):
                        a = f["rot"] + math.pi * j / 20
                        r = sz * abs(math.cos(1.5 * a))
                        pts.append((int(f["x"] + r * math.cos(a)),
                                    int(f["y"] + r * math.sin(a))))
                    if len(pts) >= 3:
                        pygame.draw.polygon(surf, c, pts, 1)
                else:
                    # arc fragments for archer
                    pygame.draw.circle(surf, c, (int(f["x"]), int(f["y"])), sz, 1)

    def _draw_worker(self, surf, radius, color, rot_offset, sq_angle, sq_amt):
        rotation = math.pi / 6 + rot_offset
        # inner rotation for idle animation
        inner_rot = self._anim_time * 0.15
        pts = draw_polar_shape(surf, self.x, self.y, radius, color,
                               hex_shape(4.0), rotation=rotation,
                               squash_angle=sq_angle, squash_amt=sq_amt)
        if not self.enemy and pts and len(pts) >= 3:
            pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
        if self.rank >= 1:
            c2 = tuple(min(255, c + 40) for c in color)
            draw_polar_shape(surf, self.x, self.y, radius * 0.55, c2,
                             hex_shape(4.0), rotation=rotation + inner_rot, width=2)
        if self.rank >= 2:
            c3 = tuple(min(255, c + 70) for c in color)
            draw_polar_shape(surf, self.x, self.y, radius * 0.3, c3,
                             hex_shape(4.0), rotation=rotation - inner_rot * 0.7, width=2)

    def _draw_soldier(self, surf, radius, color, rot_offset, sq_angle, sq_amt):
        k_values = [1.5, 2.5, 3.5, 4.0, 5.0]
        k = k_values[min(self.rank, len(k_values) - 1)]
        # attack sharpness boost
        sharpness = 0.6
        if self._anim_attack > 0:
            sharpness = 0.6 - 0.3 * self._anim_attack  # sharper during lunge
            # k perturbation during damage
        if self._anim_flash > 0:
            k += 0.3 * math.sin(self._anim_time * 30) * self._anim_flash
        rotation = -math.pi / 2 + rot_offset
        pts = draw_polar_shape(surf, self.x, self.y, radius, color,
                               blade_shape(k, sharpness), rotation=rotation,
                               squash_angle=sq_angle, squash_amt=sq_amt)
        if not self.enemy and pts and len(pts) >= 3:
            pygame.draw.polygon(surf, (0, 0, 0), pts, 2)
        if self.rank >= 2:
            c2 = tuple(min(255, c + 50) for c in color)
            draw_polar_shape(surf, self.x, self.y, radius * 0.5, c2,
                             blade_shape(k + 0.5, sharpness), rotation=rotation, width=1)
        if self.rank >= 3:
            pygame.draw.circle(surf, RANK_COLORS.get(self.rank, (200, 200, 200)),
                               (int(self.x), int(self.y)), max(2, int(radius / 6)))

    def _draw_archer(self, surf, radius, color, rot_offset, sq_angle, sq_amt):
        phi = (1 + math.sqrt(5)) / 2
        b = math.log(phi) / (math.pi / 2)
        cx, cy = self.x, self.y

        # bow flex during attack
        bow_flex = 1.0
        if self._anim_attack > 0:
            phase = self._anim_attack
            if phase > 0.5:
                bow_flex = 1.0 + 0.15 * (phase - 0.5) * 2  # draw back
            else:
                bow_flex = 1.0 - 0.1 * (0.5 - phase) * 2  # release snap

        top_pts, bot_pts = [], []
        for i in range(60):
            theta = math.pi * 0.1 + (math.pi * 1.3) * i / 59
            r = 0.3 * math.exp(b * theta) * radius / 3.0 * bow_flex
            x = cx + r * math.cos(theta) * 0.5
            top_pts.append((x, cy - r * math.sin(theta) * 0.7))
            bot_pts.append((x, cy + r * math.sin(theta) * 0.7))

        bow_poly = top_pts + bot_pts[::-1]
        if len(bow_poly) >= 3:
            fill_c = tuple(max(0, c - 40) for c in color)
            pygame.draw.polygon(surf, fill_c, bow_poly)
            pygame.draw.polygon(surf, color, bow_poly, 2)

        for pts in [top_pts, bot_pts]:
            if len(pts) >= 2:
                pygame.draw.lines(surf, color, False, pts, max(2, int(radius / 12)))

        # string
        string_x = cx - radius * 0.1
        string_pull = 0
        if self._anim_attack > 0.5:
            string_pull = (self._anim_attack - 0.5) * 2 * radius * 0.2
        pygame.draw.line(surf, color,
                         (int(string_x), int(cy - radius * 0.65)),
                         (int(string_x - string_pull), int(cy)), 1)
        pygame.draw.line(surf, color,
                         (int(string_x - string_pull), int(cy)),
                         (int(string_x), int(cy + radius * 0.65)), 1)

        # arrow (moves forward during release)
        arrow_offset = 0
        if self._anim_attack > 0 and self._anim_attack <= 0.5:
            arrow_offset = (0.5 - self._anim_attack) * 2 * radius * 0.5
        tip_x = cx + radius * 0.8 + arrow_offset
        tail_x = cx - radius * 0.3 + arrow_offset
        pygame.draw.line(surf, GLOW_WHITE, (int(tail_x), int(cy)),
                         (int(tip_x), int(cy)), 2)
        hs = radius * 0.12
        pygame.draw.polygon(surf, GLOW_WHITE, [
            (int(tip_x), int(cy)),
            (int(tip_x - hs), int(cy - hs * 0.6)),
            (int(tip_x - hs), int(cy + hs * 0.6))])


# ── main ─────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Unit Lifecycle Animations (Phase 2.5)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 36)
    font_sm = pygame.font.SysFont(None, 20)

    units = [
        AnimatedUnit("worker", W // 4, H // 2),
        AnimatedUnit("soldier", W // 2, H // 2),
        AnimatedUnit("archer", 3 * W // 4, H // 2),
    ]
    selected = 1  # soldier
    state_idx = 0

    running = True
    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    selected = 0
                elif event.key == pygame.K_2:
                    selected = 1
                elif event.key == pygame.K_3:
                    selected = 2
                elif event.key == pygame.K_SPACE:
                    state_idx = (state_idx + 1) % len(STATES)
                    for u in units:
                        u.reset()
                        u.set_state(STATES[state_idx])
                elif event.key == pygame.K_r:
                    for u in units:
                        u.reset()
                        u.set_state(STATES[state_idx])
                elif event.key == pygame.K_e:
                    for u in units:
                        u.enemy = not u.enemy
                elif event.key == pygame.K_LEFT:
                    for u in units:
                        u.rank = max(0, u.rank - 1)
                elif event.key == pygame.K_RIGHT:
                    for u in units:
                        u.rank = min(4, u.rank + 1)

        # update
        for u in units:
            u.update(dt)

        # draw
        screen.fill(COL_BG)

        # title
        screen.blit(font_lg.render("Unit Lifecycle Animations (Phase 2.5)", True,
                                    (218, 165, 32)), (20, 15))

        # state indicator
        state_name = STATES[state_idx].upper()
        sc = (100, 255, 100) if state_idx < 3 else (255, 100, 100)
        screen.blit(font.render(f"State: {state_name}  |  Rank: {units[0].rank}  |  "
                                f"Enemy: {units[0].enemy}", True, sc), (20, 55))

        # labels
        labels = ["WORKER", "SOLDIER", "ARCHER"]
        colors = [WORKER_BLUE, SOLDIER_RED, ARCHER_GREEN]
        for i, u in enumerate(units):
            lx = u.x
            c = colors[i] if i == selected else (100, 100, 120)
            label = f"{'> ' if i == selected else ''}{labels[i]}"
            ls = font.render(label, True, c)
            screen.blit(ls, (int(lx - ls.get_width() // 2), 100))

        # draw units
        for u in units:
            u.draw(screen, radius=80)

        # anim timers display
        u = units[selected]
        info_lines = [
            f"_anim_time: {u._anim_time:.2f}",
            f"_anim_flash: {u._anim_flash:.3f}",
            f"_anim_attack: {u._anim_attack:.3f}",
            f"_anim_death: {u._anim_death:.3f}",
            f"_anim_dying: {u._anim_dying}",
        ]
        for i, line in enumerate(info_lines):
            screen.blit(font_sm.render(line, True, (140, 140, 160)),
                         (20, H - 130 + i * 20))

        # controls
        ctrl = "1/2/3: select  SPACE: cycle state  R: reset  E: enemy  L/R: rank  ESC: quit"
        screen.blit(font_sm.render(ctrl, True, (120, 120, 140)), (20, H - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
