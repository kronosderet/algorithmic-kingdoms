"""
Proof-of-concept: Algorithmic unit shapes.

Renders the three unit types at all ranks using polar curves and parametric math.
- Worker: rounded hexagon (superellipse), rank adds inner self-similar hexes
- Soldier: polar rose r = cos(k*theta), rank adds petals
- Archer: golden spiral bow, rank adds Fibonacci dots

Run standalone. Press 1/2/3 to cycle ranks. ESC to quit.
"""
import pygame
import math
import sys

# --- Game palette ---
COL_BG = (20, 20, 30)
WORKER_BLUE = (50, 130, 220)
SOLDIER_RED = (200, 60, 60)
ARCHER_GREEN = (50, 190, 50)
RANK_COLORS = {
    0: (140, 140, 140),
    1: (205, 127, 50),
    2: (192, 192, 210),
    3: (255, 215, 0),
    4: (80, 180, 255),
}
RANK_NAMES = ["Recruit", "Veteran", "Corporal", "Sergeant", "Captain"]
WORKER_RANK_NAMES = ["Novice", "Foreman", "Master"]

# Enemy palette
ENEMY_RED = (180, 0, 0)
ENEMY_PURPLE = (140, 0, 140)


def draw_polar_shape(surf, cx, cy, radius, color, r_func, n_points=120,
                     width=0, rotation=0.0):
    """Draw a shape defined by polar function r_func(theta) -> radius multiplier."""
    points = []
    for i in range(n_points):
        theta = rotation + 2 * math.pi * i / n_points
        r = r_func(theta) * radius
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    if len(points) >= 3:
        if width == 0:
            pygame.draw.polygon(surf, color, points)
        else:
            pygame.draw.polygon(surf, color, points, width)


def hex_shape(n_power=4.0):
    """Superellipse that approximates a hexagon. Higher n = sharper corners."""
    def r_func(theta):
        ct = abs(math.cos(theta))
        st = abs(math.sin(theta))
        # Avoid division by zero
        denom = (ct ** n_power + st ** n_power)
        if denom < 1e-10:
            return 1.0
        return 1.0 / (denom ** (1.0 / n_power))
    return r_func


def rose_shape(k):
    """Polar rose: r = cos(k * theta). Returns function."""
    def r_func(theta):
        return abs(math.cos(k * theta))
    return r_func


def golden_spiral_bow(cx, cy, radius, surf, color, rank=0):
    """Draw an archer bow using two mirrored golden spiral arcs."""
    phi = (1 + math.sqrt(5)) / 2  # golden ratio
    b = math.log(phi) / (math.pi / 2)

    # Draw two spiral arcs (mirrored for bow shape)
    for mirror in [1, -1]:
        points = []
        for i in range(60):
            theta = math.pi * 0.1 + (math.pi * 1.3) * i / 59  # arc range
            r = 0.3 * math.exp(b * theta) * radius / 3.0
            x = cx + r * math.cos(theta) * 0.5
            y = cy + mirror * r * math.sin(theta) * 0.7
            points.append((x, y))
        if len(points) >= 2:
            pygame.draw.lines(surf, color, False, points, max(2, radius // 20))

    # Bowstring (straight line connecting endpoints)
    string_top = cy - radius * 0.65
    string_bot = cy + radius * 0.65
    pygame.draw.line(surf, color, (cx - radius * 0.1, string_top),
                     (cx - radius * 0.1, string_bot), max(1, radius // 30))

    # Arrow nocked on string
    arrow_tip_x = cx + radius * 0.8
    arrow_tail_x = cx - radius * 0.3
    arrow_y = cy
    pygame.draw.line(surf, (240, 235, 220), (arrow_tail_x, arrow_y),
                     (arrow_tip_x, arrow_y), max(1, radius // 25))
    # Arrowhead
    head_size = radius * 0.12
    pygame.draw.polygon(surf, (240, 235, 220), [
        (arrow_tip_x, arrow_y),
        (arrow_tip_x - head_size, arrow_y - head_size * 0.6),
        (arrow_tip_x - head_size, arrow_y + head_size * 0.6),
    ])

    # Fibonacci dots on bow limbs (rank-based)
    if rank >= 1:
        fib_angles = [0.5, 0.8, 1.1, 1.4, 1.8]  # angles along spiral
        n_dots = min(rank + 1, len(fib_angles))
        dot_color = RANK_COLORS.get(rank, (200, 200, 200))
        for i in range(n_dots):
            theta = math.pi * 0.1 + fib_angles[i]
            r = 0.3 * math.exp(b * theta) * radius / 3.0
            for mirror in [1, -1]:
                dx = cx + r * math.cos(theta) * 0.5
                dy = cy + mirror * r * math.sin(theta) * 0.7
                pygame.draw.circle(surf, dot_color, (int(dx), int(dy)),
                                   max(2, radius // 15))


def draw_worker(surf, cx, cy, radius, rank=0, enemy=False):
    """Draw a worker as a rounded hexagon with self-similar inner hexes."""
    color = (40, 80, 140) if enemy else WORKER_BLUE
    rotation = math.pi / 6  # flat edge forward

    # Outer hex
    draw_polar_shape(surf, cx, cy, radius, color, hex_shape(4.0),
                     rotation=rotation)

    # Inner self-similar hexes (rank-based)
    if rank >= 1:
        inner_r = radius * 0.55
        inner_color = tuple(min(255, c + 40) for c in color)
        draw_polar_shape(surf, cx, cy, inner_r, inner_color, hex_shape(4.0),
                         rotation=rotation + 0.05, width=max(1, radius // 15))
    if rank >= 2:
        inner_r2 = radius * 0.3
        inner_color2 = tuple(min(255, c + 70) for c in color)
        draw_polar_shape(surf, cx, cy, inner_r2, inner_color2, hex_shape(4.0),
                         rotation=rotation + 0.10, width=max(1, radius // 15))

    # Enemy perturbation: jagged overlay
    if enemy:
        def jagged(theta):
            base = hex_shape(4.0)(theta)
            return base * (1.0 + 0.08 * math.sin(17 * theta))
        draw_polar_shape(surf, cx, cy, radius * 1.05, (100, 30, 30),
                         jagged, rotation=rotation, width=2)


def draw_soldier(surf, cx, cy, radius, rank=0, enemy=False):
    """Draw a soldier as a polar rose with rank-scaling petals."""
    base_color = ENEMY_RED if enemy else SOLDIER_RED

    # Petal count increases with rank
    k_values = [1.5, 2.5, 3.5, 4.0, 5.0]  # 3, 5, 7, 8, 10 petals
    k = k_values[min(rank, len(k_values) - 1)]

    # Rank tint
    if rank >= 3:
        tint = RANK_COLORS[rank]
        color = tuple((a + b) // 2 for a, b in zip(base_color, tint))
    elif rank >= 1:
        tint = RANK_COLORS[rank]
        color = tuple((a * 3 + b) // 4 for a, b in zip(base_color, tint))
    else:
        color = base_color

    rotation = -math.pi / 2  # one petal points up (forward)

    # Main rose
    draw_polar_shape(surf, cx, cy, radius, color, rose_shape(k),
                     rotation=rotation)

    # Higher ranks get an inner rose overlay
    if rank >= 2:
        inner_k = k + 0.5
        inner_color = tuple(min(255, c + 50) for c in color)
        draw_polar_shape(surf, cx, cy, radius * 0.5, inner_color,
                         rose_shape(inner_k), rotation=rotation)

    # Central dot for sergeant+
    if rank >= 3:
        pygame.draw.circle(surf, RANK_COLORS[rank], (int(cx), int(cy)),
                           max(2, radius // 6))

    # Enemy perturbation
    if enemy:
        def jagged_rose(theta):
            base = rose_shape(k)(theta)
            return base * (1.0 + 0.12 * math.sin(13 * theta))
        draw_polar_shape(surf, cx, cy, radius * 1.08, (120, 20, 40),
                         jagged_rose, rotation=rotation, width=2)


def draw_archer(surf, cx, cy, radius, rank=0, enemy=False):
    """Draw an archer as a golden spiral bow."""
    color = ENEMY_PURPLE if enemy else ARCHER_GREEN
    golden_spiral_bow(cx, cy, radius, surf, color, rank=rank)

    # Enemy: jagged border circle
    if enemy:
        n = 40
        pts = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            r = radius * (0.85 + 0.08 * math.sin(11 * theta))
            pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        pygame.draw.polygon(surf, (120, 20, 80), pts, 2)


def main():
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("VDD PoC: Algorithmic Unit Shapes")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    font_lg = pygame.font.SysFont(None, 32)
    font_sm = pygame.font.SysFont(None, 18)

    current_rank = 0
    show_enemy = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    current_rank = min(4, current_rank + 1)
                elif event.key == pygame.K_LEFT:
                    current_rank = max(0, current_rank - 1)
                elif event.key == pygame.K_e:
                    show_enemy = not show_enemy

        screen.fill(COL_BG)

        # Title
        title = "Algorithmic Unit Shapes"
        ts = font_lg.render(title, True, (220, 220, 220))
        screen.blit(ts, (W // 2 - ts.get_width() // 2, 20))

        # Controls
        ctrl = "LEFT/RIGHT: Change rank  |  E: Toggle enemy variant  |  ESC: Quit"
        cs = font_sm.render(ctrl, True, (120, 120, 140))
        screen.blit(cs, (W // 2 - cs.get_width() // 2, 56))

        # Draw three unit types at different sizes
        unit_types = [
            ("WORKER", draw_worker, WORKER_BLUE,
             min(current_rank, 2)),  # workers max rank 2
            ("SOLDIER", draw_soldier, SOLDIER_RED, current_rank),
            ("ARCHER", draw_archer, ARCHER_GREEN, current_rank),
        ]

        col_w = W // 3
        sizes = [30, 50, 80, 120]  # different render sizes

        for col_idx, (name, draw_func, color, rank) in enumerate(unit_types):
            base_x = col_idx * col_w + col_w // 2

            # Column header
            rank_name = RANK_NAMES[rank] if name != "WORKER" else \
                WORKER_RANK_NAMES[min(rank, 2)]
            header = f"{name} - {rank_name} (rank {rank})"
            hs = font.render(header, True, color)
            screen.blit(hs, (base_x - hs.get_width() // 2, 90))

            # Draw at multiple sizes
            y = 160
            for size in sizes:
                draw_func(screen, base_x - 130, y + size, size,
                          rank=rank, enemy=False)
                if show_enemy:
                    draw_func(screen, base_x + 130, y + size, size,
                              rank=rank, enemy=True)

                # Size label
                label = f"{size}px"
                ls = font_sm.render(label, True, (100, 100, 120))
                screen.blit(ls, (base_x - 130 - ls.get_width() // 2,
                                 y + size * 2 + 5))
                if show_enemy:
                    el = font_sm.render("enemy", True, (140, 60, 60))
                    screen.blit(el, (base_x + 130 - el.get_width() // 2,
                                     y + size * 2 + 5))

                y += size * 2 + 30

        # Rank color indicator
        rc = RANK_COLORS.get(current_rank, (140, 140, 140))
        pygame.draw.circle(screen, rc, (W - 40, 40), 15)
        rl = font_sm.render(RANK_NAMES[current_rank], True, rc)
        screen.blit(rl, (W - 40 - rl.get_width() // 2, 60))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
