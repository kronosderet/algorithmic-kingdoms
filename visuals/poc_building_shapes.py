"""
Proof-of-concept: Algorithmic building shapes.

- Town Hall: L-system branching tree (grows with construction %)
- Barracks: Sierpinski triangle lattice
- Refinery: Spirograph epitrochoid gear
- Tower: Koch snowflake battlement (Lv.1 vs Lv.2)

Run standalone. Arrow keys cycle building type. UP/DOWN adjusts construction %.
ESC to quit.
"""
import pygame
import math
import sys

# --- Game palette ---
COL_BG = (20, 20, 30)
TOWN_HALL_BROWN = (139, 90, 43)
BARRACKS_MAROON = (140, 45, 45)
REFINERY_GRAY = (100, 100, 130)
TOWER_STONE = (160, 160, 140)
FORGE_ORANGE = (255, 140, 40)
CANOPY_GREEN = (30, 110, 50)
TERRAIN_GRASS = (46, 139, 87)


# =========================================================
# L-SYSTEM: Town Hall tree
# =========================================================

def l_system_expand(axiom, rules, iterations):
    """Expand an L-system string."""
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(c, c) for c in s)
    return s


def l_system_draw(surf, cx, cy, instruction_str, angle_deg=22.5,
                  step=8, start_angle=-90, trunk_color=TOWN_HALL_BROWN,
                  tip_color=CANOPY_GREEN, line_width=2):
    """Interpret L-system string as turtle graphics."""
    angle_rad = math.radians(angle_deg)
    current_angle = math.radians(start_angle)
    x, y = float(cx), float(cy)
    stack = []
    depth = 0
    max_depth = instruction_str.count('[')  # rough estimate

    for ch in instruction_str:
        if ch == 'F':
            nx = x + step * math.cos(current_angle)
            ny = y + step * math.sin(current_angle)
            # Color gradient: trunk near base, green at tips
            t = min(1.0, depth / max(1, max_depth * 0.5))
            color = tuple(int(a + (b - a) * t)
                          for a, b in zip(trunk_color, tip_color))
            w = max(1, line_width - depth // 3)
            pygame.draw.line(surf, color, (int(x), int(y)),
                             (int(nx), int(ny)), w)
            x, y = nx, ny
        elif ch == '+':
            current_angle += angle_rad
        elif ch == '-':
            current_angle -= angle_rad
        elif ch == '[':
            stack.append((x, y, current_angle, depth))
            depth += 1
        elif ch == ']':
            if stack:
                x, y, current_angle, depth = stack.pop()


def draw_town_hall(surf, cx, cy, size, build_pct=1.0):
    """Draw town hall as L-system tree. Iterations scale with build progress."""
    axiom = "F"
    rules = {"F": "FF+[+F-F-F]-[-F+F+F]"}
    # Iterations: 0-4 based on build progress
    iters = max(0, min(4, int(build_pct * 4 + 0.5)))
    if iters == 0:
        # Just a single line (foundation)
        pygame.draw.line(surf, TOWN_HALL_BROWN,
                         (cx, cy), (cx, cy - size // 3), 3)
        return

    instructions = l_system_expand(axiom, rules, iters)
    step = size / (3.0 * (1.5 ** iters))  # scale step to fit
    l_system_draw(surf, cx, cy, instructions, angle_deg=22.5,
                  step=step, line_width=max(1, 4 - iters))


# =========================================================
# SIERPINSKI: Barracks
# =========================================================

def sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color):
    """Recursively draw Sierpinski triangle."""
    if depth == 0:
        pygame.draw.polygon(surf, color, [(x1, y1), (x2, y2), (x3, y3)])
        return

    # Midpoints
    mx1 = (x1 + x2) / 2
    my1 = (y1 + y2) / 2
    mx2 = (x2 + x3) / 2
    my2 = (y2 + y3) / 2
    mx3 = (x1 + x3) / 2
    my3 = (y1 + y3) / 2

    # Three sub-triangles (skip center)
    darker = tuple(max(0, c - 15 * depth) for c in color)
    sierpinski(surf, x1, y1, mx1, my1, mx3, my3, depth - 1, color)
    sierpinski(surf, mx1, my1, x2, y2, mx2, my2, depth - 1, darker)
    sierpinski(surf, mx3, my3, mx2, my2, x3, y3, depth - 1, color)


def draw_barracks(surf, cx, cy, size, build_pct=1.0):
    """Draw barracks as Sierpinski triangle. Depth scales with build progress."""
    depth = max(0, min(4, int(build_pct * 4 + 0.5)))
    half = size * 0.45
    # Equilateral triangle centered at (cx, cy)
    h = half * math.sqrt(3)
    x1 = cx
    y1 = cy - h * 0.6
    x2 = cx - half
    y2 = cy + h * 0.4
    x3 = cx + half
    y3 = cy + h * 0.4
    sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, BARRACKS_MAROON)

    # Border
    border_color = tuple(min(255, c + 40) for c in BARRACKS_MAROON)
    pygame.draw.polygon(surf, border_color,
                        [(int(x1), int(y1)), (int(x2), int(y2)),
                         (int(x3), int(y3))], 2)


# =========================================================
# SPIROGRAPH: Refinery
# =========================================================

def draw_refinery(surf, cx, cy, size, build_pct=1.0, rotation=0.0):
    """Draw refinery as epitrochoid (Spirograph gear)."""
    if build_pct < 0.1:
        # Foundation: just a circle outline
        pygame.draw.circle(surf, REFINERY_GRAY, (int(cx), int(cy)),
                           int(size * 0.4), 2)
        return

    R, r, d = 5.0, 3.0, 5.0  # gear parameters
    scale = size * 0.35 / (R + r + d)  # fit to size

    # How much of the curve to draw scales with build progress
    max_t = build_pct * 6 * math.pi
    n_points = int(max_t * 20)

    points = []
    for i in range(n_points):
        t = rotation + max_t * i / max(1, n_points - 1)
        x = (R + r) * math.cos(t) - d * math.cos((R + r) / r * t)
        y = (R + r) * math.sin(t) - d * math.sin((R + r) / r * t)
        points.append((cx + x * scale, cy + y * scale))

    if len(points) >= 2:
        pygame.draw.lines(surf, REFINERY_GRAY, build_pct >= 0.95,
                          points, max(1, size // 40))

    # Cusp highlights (steel blue accents at gear teeth)
    if build_pct >= 0.5:
        steel_blue = (100, 160, 220)
        for i in range(0, len(points), max(1, len(points) // 8)):
            pygame.draw.circle(surf, steel_blue,
                               (int(points[i][0]), int(points[i][1])),
                               max(2, size // 25))


# =========================================================
# KOCH SNOWFLAKE: Tower
# =========================================================

def koch_curve_points(x1, y1, x2, y2, depth):
    """Generate points along a Koch curve from (x1,y1) to (x2,y2)."""
    if depth == 0:
        return [(x1, y1)]

    dx = x2 - x1
    dy = y2 - y1

    # Divide into thirds
    ax = x1 + dx / 3
    ay = y1 + dy / 3
    bx = x1 + 2 * dx / 3
    by = y1 + 2 * dy / 3

    # Peak of equilateral triangle
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)

    # Recurse
    pts = []
    pts.extend(koch_curve_points(x1, y1, ax, ay, depth - 1))
    pts.extend(koch_curve_points(ax, ay, px, py, depth - 1))
    pts.extend(koch_curve_points(px, py, bx, by, depth - 1))
    pts.extend(koch_curve_points(bx, by, x2, y2, depth - 1))
    return pts


def koch_snowflake(cx, cy, size, depth):
    """Generate Koch snowflake points centered at (cx, cy)."""
    # Start with equilateral triangle
    r = size * 0.45
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]
    vertices = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]

    all_points = []
    for i in range(3):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % 3]
        # Koch curve goes OUTWARD (swap direction for snowflake)
        all_points.extend(koch_curve_points(x1, y1, x2, y2, depth))
    return all_points


def draw_tower(surf, cx, cy, size, build_pct=1.0, level=1):
    """Draw tower as Koch snowflake. Level 2 = more detail + orange."""
    depth = max(0, min(3, int(build_pct * 3 + 0.5)))
    if level >= 2:
        depth = min(4, depth + 1)  # extra detail for upgraded tower

    if depth == 0:
        # Foundation: square outline
        half = size * 0.35
        pygame.draw.rect(surf, TOWER_STONE,
                         (cx - half, cy - half, half * 2, half * 2), 2)
        return

    points = koch_snowflake(cx, cy, size, depth)
    int_points = [(int(p[0]), int(p[1])) for p in points]

    if len(int_points) >= 3:
        color = TOWER_STONE if level == 1 else (180, 160, 120)
        pygame.draw.polygon(surf, color, int_points)

        # Border
        border = (200, 200, 180) if level == 1 else FORGE_ORANGE
        pygame.draw.polygon(surf, border, int_points, max(1, size // 30))

    # Level 2: orange glow dots on Koch tips
    if level >= 2 and len(points) > 10:
        step = max(1, len(points) // 12)
        for i in range(0, len(points), step):
            pygame.draw.circle(surf, FORGE_ORANGE,
                               (int(points[i][0]), int(points[i][1])),
                               max(2, size // 20))


# =========================================================
# MAIN
# =========================================================

def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Algorithmic Building Shapes")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 32)
    font_sm = pygame.font.SysFont(None, 18)

    build_pct = 1.0
    tower_level = 1
    time_acc = 0.0

    building_types = ["Town Hall", "Barracks", "Refinery",
                      "Tower Lv.1", "Tower Lv.2"]
    current_type = 0

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
                    current_type = (current_type - 1) % len(building_types)
                elif event.key == pygame.K_RIGHT:
                    current_type = (current_type + 1) % len(building_types)
                elif event.key == pygame.K_UP:
                    build_pct = min(1.0, build_pct + 0.1)
                elif event.key == pygame.K_DOWN:
                    build_pct = max(0.0, build_pct - 0.1)

        screen.fill(COL_BG)

        # Title
        title = f"Building: {building_types[current_type]}  |  Construction: {int(build_pct * 100)}%"
        ts = font_lg.render(title, True, (220, 220, 220))
        screen.blit(ts, (W // 2 - ts.get_width() // 2, 20))

        ctrl = "LEFT/RIGHT: Change type  |  UP/DOWN: Build progress  |  ESC: Quit"
        cs = font_sm.render(ctrl, True, (120, 120, 140))
        screen.blit(cs, (W // 2 - cs.get_width() // 2, 56))

        # Draw current building at multiple sizes
        sizes = [60, 100, 160, 250]
        x_pos = [W * 0.15, W * 0.38, W * 0.62, W * 0.85]

        for i, size in enumerate(sizes):
            cx = int(x_pos[i])
            cy = H // 2 + 40

            if current_type == 0:  # Town Hall
                draw_town_hall(screen, cx, cy + size // 4, size, build_pct)
            elif current_type == 1:  # Barracks
                draw_barracks(screen, cx, cy, size, build_pct)
            elif current_type == 2:  # Refinery
                draw_refinery(screen, cx, cy, size, build_pct,
                              rotation=time_acc * 0.3)
            elif current_type == 3:  # Tower Lv.1
                draw_tower(screen, cx, cy, size, build_pct, level=1)
            elif current_type == 4:  # Tower Lv.2
                draw_tower(screen, cx, cy, size, build_pct, level=2)

            # Size label
            label = f"{size}px"
            ls = font_sm.render(label, True, (100, 100, 120))
            screen.blit(ls, (cx - ls.get_width() // 2, cy + size // 2 + 20))

        # Construction progress visualization
        bar_x = 50
        bar_y = H - 80
        bar_w = W - 100
        bar_h = 16
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * build_pct)
        fill_color = (0, 180, 255) if build_pct < 1.0 else (0, 220, 100)
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_w, bar_h))
        pct_label = font_sm.render(f"{int(build_pct * 100)}% built", True,
                                   (200, 200, 220))
        screen.blit(pct_label, (bar_x + bar_w // 2 - pct_label.get_width() // 2,
                                bar_y - 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
