"""
Proof-of-concept: Building lifecycle fractals (VDD Phase 3.5).

HP-based fractal degradation, ruin states, repair animation, damage flash.

Controls:
  LEFT/RIGHT  Select building type
  UP/DOWN     Adjust HP (10% increments)
  SPACE       Cycle preset HP values (100, 75, 50, 25, 0)
  R           Toggle repair animation (restore to 100%)
  D           Trigger damage flash
  ESC         Quit
"""
import pygame
import math
import random
import sys

# --- palette ---
COL_BG = (20, 20, 30)
TH_BROWN = (139, 90, 43)
TH_GREEN = (30, 110, 50)
BK_MAROON = (140, 45, 45)
RF_GRAY = (100, 100, 130)
TW_STONE = (160, 160, 140)
FORGE_ORANGE = (255, 140, 40)
STEEL_BLUE = (100, 160, 220)
RUIN_GRAY = (80, 75, 65)
RUIN_DARK = (50, 45, 40)
REPAIR_GOLD = (218, 165, 32)   # Earth Gold (system color)
SENTINEL_STONE = (140, 130, 100)

W, H = 1280, 720


def lerp_c(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ── L-system ─────────────────────────────────────────────────
def l_expand(axiom, rules, iters):
    s = axiom
    for _ in range(iters):
        s = "".join(rules.get(c, c) for c in s)
    return s


def l_render(surf, cx, cy, instr, angle_deg=22.5, step=8,
             start_angle=-90, col_trunk=(139, 90, 43),
             col_tip=(30, 110, 50), line_width=2, hp_pct=1.0):
    angle_rad = math.radians(angle_deg)
    cur_angle = math.radians(start_angle)
    x, y = float(cx), float(cy)
    stack = []
    depth = 0
    max_depth = max(1, instr.count('['))
    char_idx = 0
    total = len(instr)
    # only render portion based on HP
    render_limit = int(total * max(0.1, hp_pct))

    for ch in instr[:render_limit]:
        if ch == 'F':
            nx = x + step * math.cos(cur_angle)
            ny = y + step * math.sin(cur_angle)
            t = min(1.0, depth / max(1, max_depth * 0.5))
            col = lerp_c(col_trunk, col_tip, t)
            # desaturate at low HP
            if hp_pct < 0.5:
                gray_t = 1.0 - hp_pct * 2
                col = lerp_c(col, RUIN_GRAY, gray_t * 0.6)
            w = max(1, line_width - depth // 3)
            pygame.draw.line(surf, col, (int(x), int(y)), (int(nx), int(ny)), w)
            x, y = nx, ny
        elif ch == '+':
            cur_angle += angle_rad
        elif ch == '-':
            cur_angle -= angle_rad
        elif ch == '[':
            stack.append((x, y, cur_angle, depth))
            depth += 1
        elif ch == ']':
            if stack:
                x, y, cur_angle, depth = stack.pop()


# ── Sierpinski ───────────────────────────────────────────────
def sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color, hp_pct=1.0):
    if depth == 0:
        col = color
        if hp_pct < 0.5:
            col = lerp_c(color, RUIN_GRAY, (0.5 - hp_pct) * 1.5)
        pygame.draw.polygon(surf, col,
                            [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])
        return
    # skip sub-triangles randomly at low HP (gaps = damage)
    skip_chance = max(0, (1.0 - hp_pct) * 0.4)
    mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
    mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2
    mx3, my3 = (x1 + x3) / 2, (y1 + y3) / 2
    darker = tuple(max(0, c - 12 * depth) for c in color)
    if random.random() > skip_chance:
        sierpinski(surf, x1, y1, mx1, my1, mx3, my3, depth - 1, color, hp_pct)
    if random.random() > skip_chance:
        sierpinski(surf, mx1, my1, x2, y2, mx2, my2, depth - 1, darker, hp_pct)
    if random.random() > skip_chance:
        sierpinski(surf, mx3, my3, mx2, my2, x3, y3, depth - 1, color, hp_pct)


# ── Koch snowflake ───────────────────────────────────────────
def koch_pts(x1, y1, x2, y2, depth):
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(koch_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(koch_pts(ax, ay, px, py, depth - 1))
    pts.extend(koch_pts(px, py, bx, by, depth - 1))
    pts.extend(koch_pts(bx, by, x2, y2, depth - 1))
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
        all_pts.extend(koch_pts(x1, y1, x2, y2, depth))
    return all_pts


# ── debris particles ─────────────────────────────────────────
class Debris:
    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        self.x, self.y = x + random.uniform(-20, 20), y + random.uniform(-20, 20)
        self.vx = math.cos(angle) * random.uniform(5, 20)
        self.vy = math.sin(angle) * random.uniform(5, 20) - 10
        self.color = lerp_c(color, RUIN_DARK, random.uniform(0, 0.5))
        self.size = random.randint(2, 5)
        self.life = random.uniform(0.5, 2.0)
        self.age = 0

    def update(self, dt):
        self.age += dt
        self.vy += 30 * dt  # gravity
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surf):
        alpha = max(0, 1 - self.age / self.life)
        c = lerp_c(self.color, COL_BG, 1 - alpha)
        pygame.draw.rect(surf, c,
                         (int(self.x), int(self.y), self.size, self.size))


# ── building renderers ───────────────────────────────────────
def draw_town_hall(surf, cx, cy, size, hp_pct=1.0, flash=0.0, repairing=False):
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))

    iters = max(1, int(hp_pct * 4 + 0.5))
    if hp_pct <= 0.05:
        iters = 0
    instr = l_expand("F", {"F": "FF+[+F-F-F]-[-F+F+F]"}, max(1, iters))
    step = size / (3.0 * (1.5 ** max(1, iters)))
    col_trunk = TH_BROWN if not flash else lerp_c(TH_BROWN, (255, 255, 255), flash)
    l_render(surf, cx, cy + half - 4, instr, step=step,
             col_trunk=col_trunk, col_tip=TH_GREEN,
             line_width=max(1, 4 - iters), hp_pct=hp_pct)
    if repairing:
        pygame.draw.circle(surf, REPAIR_GOLD, (int(cx), int(cy)),
                           int(size * 0.5), 1)


def draw_barracks(surf, cx, cy, size, hp_pct=1.0, flash=0.0, repairing=False):
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))

    depth = max(0, int(hp_pct * 4 + 0.5))
    color = BK_MAROON if not flash else lerp_c(BK_MAROON, (255, 255, 255), flash)
    h_tri = half * math.sqrt(3)
    x1, y1 = cx, cy - h_tri * 0.6
    x2, y2 = cx - half, cy + h_tri * 0.4
    x3, y3 = cx + half, cy + h_tri * 0.4
    random.seed(42)  # deterministic gaps
    sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color, hp_pct)
    random.seed()
    border_c = tuple(min(255, c + 40) for c in color)
    pygame.draw.polygon(surf, border_c,
                        [(int(x1), int(y1)), (int(x2), int(y2)),
                         (int(x3), int(y3))], 2)
    if repairing:
        pygame.draw.circle(surf, REPAIR_GOLD, (int(cx), int(cy)),
                           int(size * 0.5), 1)


def draw_refinery(surf, cx, cy, size, hp_pct=1.0, flash=0.0, repairing=False):
    half = int(size * 0.45)
    foundation = pygame.Surface((half * 2, half * 2), pygame.SRCALPHA)
    foundation.fill((15, 15, 20, 80))
    surf.blit(foundation, (cx - half, cy - half))

    color = RF_GRAY if not flash else lerp_c(RF_GRAY, (255, 255, 255), flash)
    R, r, d = 5.0, 3.0, 5.0
    scale = size * 0.35 / (R + r + d)
    max_t = hp_pct * 6 * math.pi
    n_points = max(20, int(max_t * 15))
    points = []
    for i in range(n_points):
        t = max_t * i / max(1, n_points - 1)
        x = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
        y = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
        # jitter at low HP
        if hp_pct < 0.5:
            jit = (0.5 - hp_pct) * 3
            x += random.uniform(-jit, jit)
            y += random.uniform(-jit, jit)
        points.append((cx + x * scale, cy + y * scale))
    if len(points) >= 2:
        draw_color = color
        if hp_pct < 0.3:
            draw_color = lerp_c(color, RUIN_GRAY, (0.3 - hp_pct) * 3)
        pygame.draw.lines(surf, draw_color, hp_pct >= 0.95,
                          points, max(1, size // 40))
    if repairing:
        pygame.draw.circle(surf, REPAIR_GOLD, (int(cx), int(cy)),
                           int(size * 0.5), 1)


def draw_sentinel(surf, cx, cy, size, hp_pct=1.0, level=1, flash=0.0, repairing=False):
    """Sentinel lifecycle: Voronoi fracture on damage, Koch aura degrades, repair retuning."""
    SENTINEL_STONE_C = (140, 130, 100)
    RESONANCE_GLOW_C = (180, 160, 255)
    SENTINEL_GOLD_C = (218, 165, 32)

    half = int(size * 0.45)

    # Koch resonance field — degrades with HP
    if hp_pct > 0.15:
        koch_depth = 2 if hp_pct > 0.66 else (1 if hp_pct > 0.33 else 0)
        if level >= 2:
            koch_depth = min(3, koch_depth + 1)
        field_r = size * 0.42 * max(0.3, hp_pct)
        if koch_depth > 0 and field_r > 5:
            points = koch_snowflake(cx, cy, field_r * 2, koch_depth)
            if len(points) >= 3:
                field_surf = pygame.Surface((int(size * 1.2), int(size * 1.2)), pygame.SRCALPHA)
                shifted = [(int(p[0] - cx + size * 0.6), int(p[1] - cy + size * 0.6))
                           for p in points]
                alpha = int(50 * hp_pct)
                pygame.draw.polygon(field_surf, (*RESONANCE_GLOW_C, max(5, alpha // 3)), shifted)
                pygame.draw.polygon(field_surf, (*RESONANCE_GLOW_C, max(10, alpha)), shifted,
                                    max(1, size // 40))
                surf.blit(field_surf, (int(cx - size * 0.6), int(cy - size * 0.6)))

    # Ruin state: cracked monolith leaning
    if hp_pct <= 0.0:
        lean = 15  # degrees
        rng = random.Random(42)
        for _ in range(5):
            rx = cx + rng.randint(-half // 2, half // 2)
            ry = cy + rng.randint(-half // 3, half // 3)
            pygame.draw.line(surf, RUIN_GRAY, (rx, ry),
                             (rx + rng.randint(-8, 8), ry + rng.randint(-8, 8)), 2)
        # Residual glow at base
        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*SENTINEL_GOLD_C, 15), (20, 20), 18)
        surf.blit(glow_surf, (cx - 20, cy + half // 3 - 20))
        return

    # Standing stone body
    w_s = int(size * 0.3)
    h_s = int(size * 0.7)
    body = [(cx - w_s // 2, cy + h_s // 3),
            (cx - w_s // 3, cy - h_s // 3),
            (cx, cy - h_s // 2),
            (cx + w_s // 3, cy - h_s // 3),
            (cx + w_s // 2, cy + h_s // 3)]
    stone_c = SENTINEL_STONE_C if level == 1 else (160, 148, 115)
    if flash:
        stone_c = lerp_c(stone_c, (255, 255, 255), flash)
    if hp_pct < 0.5:
        stone_c = lerp_c(stone_c, RUIN_GRAY, (0.5 - hp_pct) * 1.5)
    pygame.draw.polygon(surf, stone_c, body)
    pygame.draw.polygon(surf, (0, 0, 0), body, 2)

    # Voronoi dots — crack apart as damage increases
    rng = random.Random(137)
    crack_spread = (1.0 - hp_pct) * 4  # cells drift apart
    for _ in range(7):
        ox = rng.randint(-w_s // 3, w_s // 3) + int(rng.uniform(-crack_spread, crack_spread))
        oy = rng.randint(-h_s // 3, h_s // 4) + int(rng.uniform(-crack_spread, crack_spread))
        dot_c = tuple(min(255, c + rng.randint(-12, 12)) for c in stone_c)
        pygame.draw.circle(surf, dot_c, (cx + ox, cy + oy), max(1, size // 25))
    # Crack lines between cells
    if hp_pct < 0.75:
        n_cracks = int((1.0 - hp_pct) * 5)
        for _ in range(n_cracks):
            cx1 = cx + rng.randint(-w_s // 3, w_s // 3)
            cy1 = cy + rng.randint(-h_s // 3, h_s // 4)
            cx2 = cx1 + rng.randint(-8, 8)
            cy2 = cy1 + rng.randint(-8, 8)
            pygame.draw.line(surf, (8, 5, 3), (cx1, cy1), (cx2, cy2), 1)

    # Golden aura
    aura_alpha = int(25 * hp_pct)
    aura = pygame.Surface((size, size), pygame.SRCALPHA)
    for ri in range(3):
        a = max(0, aura_alpha - ri * 7)
        pygame.draw.circle(aura, (*SENTINEL_GOLD_C, a),
                           (size // 2, size // 2), int(size * 0.25) + ri * 5)
    surf.blit(aura, (cx - size // 2, cy - size // 2))

    # Repair: gold flash at seams
    if repairing:
        repair_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(repair_surf, (*SENTINEL_GOLD_C, 30),
                           (size // 2, size // 2), int(size * 0.35), 1)
        surf.blit(repair_surf, (cx - size // 2, cy - size // 2))


# ── main ─────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Building Lifecycle (Phase 3.5)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 36)
    font_sm = pygame.font.SysFont(None, 20)

    building_names = ["Town Hall", "Barracks", "Refinery", "Sentinel Lv.1", "Sentinel Lv.2"]
    current = 0
    hp_pct = 1.0
    preset_idx = 0
    presets = [1.0, 0.75, 0.5, 0.25, 0.0]
    flash = 0.0
    repairing = False
    repair_target = 1.0
    debris_list = []
    time_acc = 0

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
                elif event.key == pygame.K_LEFT:
                    current = (current - 1) % len(building_names)
                elif event.key == pygame.K_RIGHT:
                    current = (current + 1) % len(building_names)
                elif event.key == pygame.K_UP:
                    hp_pct = min(1.0, hp_pct + 0.1)
                    repairing = False
                elif event.key == pygame.K_DOWN:
                    old_hp = hp_pct
                    hp_pct = max(0.0, hp_pct - 0.1)
                    repairing = False
                    if hp_pct < old_hp:
                        for _ in range(3):
                            debris_list.append(Debris(W // 2, H // 2 + 40,
                                                      TW_STONE))
                elif event.key == pygame.K_SPACE:
                    preset_idx = (preset_idx + 1) % len(presets)
                    hp_pct = presets[preset_idx]
                    repairing = False
                elif event.key == pygame.K_r:
                    repairing = not repairing
                    repair_target = 1.0
                elif event.key == pygame.K_d:
                    flash = 1.0
                    for _ in range(5):
                        debris_list.append(Debris(W // 2, H // 2 + 40, BK_MAROON))

        # update
        if flash > 0:
            flash = max(0, flash - dt / 0.15)
        if repairing and hp_pct < repair_target:
            hp_pct = min(repair_target, hp_pct + dt * 0.3)
        for d in debris_list:
            d.update(dt)
        debris_list = [d for d in debris_list if d.age < d.life]

        # draw
        screen.fill(COL_BG)

        screen.blit(font_lg.render("Building Lifecycle (Phase 3.5)", True,
                                    (218, 165, 32)), (20, 15))

        info = f"Building: {building_names[current]}  |  HP: {int(hp_pct * 100)}%"
        if repairing:
            info += "  |  REPAIRING"
        screen.blit(font.render(info, True, (180, 180, 200)), (20, 55))

        # draw building large in center
        cx, cy = W // 2, H // 2 + 40
        size = 250

        if current == 0:
            draw_town_hall(screen, cx, cy, size, hp_pct, flash, repairing)
        elif current == 1:
            draw_barracks(screen, cx, cy, size, hp_pct, flash, repairing)
        elif current == 2:
            draw_refinery(screen, cx, cy, size, hp_pct, flash, repairing)
        elif current == 3:
            draw_sentinel(screen, cx, cy, size, hp_pct, level=1, flash=flash, repairing=repairing)
        elif current == 4:
            draw_sentinel(screen, cx, cy, size, hp_pct, level=2, flash=flash, repairing=repairing)

        # debris
        for d in debris_list:
            d.draw(screen)

        # HP bar
        bar_x, bar_y, bar_w, bar_h = 50, H - 80, W - 100, 20
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * hp_pct)
        if hp_pct > 0.5:
            bc = (0, 200, 80)
        elif hp_pct > 0.25:
            bc = (220, 180, 0)
        else:
            bc = (200, 40, 40)
        pygame.draw.rect(screen, bc, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(screen, (80, 80, 100), (bar_x, bar_y, bar_w, bar_h), 1)

        ctrl = "L/R: building  UP/DN: HP  SPACE: presets  R: repair  D: damage flash  ESC: quit"
        screen.blit(font_sm.render(ctrl, True, (120, 120, 140)), (20, H - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
