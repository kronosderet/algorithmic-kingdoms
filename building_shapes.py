import math
import pygame

# ---------------------------------------------------------------------------
# VDD Phase 3: Algorithmic Building Shape Helpers
# ---------------------------------------------------------------------------
_TH_BROWN = (139, 90, 43)
_TH_GREEN = (30, 110, 50)
_BK_MAROON = (140, 45, 45)
_RF_GRAY = (100, 100, 130)
_TW_STONE = (160, 160, 140)
_FORGE_ORANGE = (255, 140, 40)
_STEEL_BLUE = (100, 160, 220)


def _l_system_expand(axiom, rules, iters):
    s = axiom
    for _ in range(iters):
        s = "".join(rules.get(c, c) for c in s)
    return s


def _l_system_render(surf, cx, cy, instructions, angle_deg=22.5,
                     step=8, start_angle=-90, col_trunk=_TH_BROWN,
                     col_tip=_TH_GREEN, line_width=2, furl=0.0):
    """Interpret L-system string as turtle graphics.
    furl: 0.0 = normal tree, 1.0 = fully furled protective bush.
    When furled, branches droop downward and shorten to form a shield canopy.
    """
    angle_rad = math.radians(angle_deg)
    cur_angle = math.radians(start_angle)
    x, y = float(cx), float(cy)
    stack = []
    depth = 0
    max_depth = max(1, instructions.count('['))
    for ch in instructions:
        if ch == 'F':
            # furl: deeper branches shorten and droop to form bush
            depth_frac = min(1.0, depth / max(1, max_depth * 0.5))
            furl_step = step * (1.0 - furl * 0.35 * depth_frac)
            # droop: pull branches toward ground (positive y)
            droop = furl * depth_frac * 0.6
            furled_angle = cur_angle + droop
            nx = x + furl_step * math.cos(furled_angle)
            ny = y + furl_step * math.sin(furled_angle)
            t = depth_frac
            col = tuple(int(a + (b - a) * t) for a, b in zip(col_trunk, col_tip))
            # thicken lines when furled for denser bush look
            w = max(1, line_width - depth // 3 + int(furl * 1.5))
            pygame.draw.line(surf, col, (int(x), int(y)), (int(nx), int(ny)), w)
            x, y = nx, ny
        elif ch == '+':
            # furl narrows branch spread (branches cluster inward)
            cur_angle += angle_rad * (1.0 - furl * 0.4)
        elif ch == '-':
            cur_angle -= angle_rad * (1.0 - furl * 0.4)
        elif ch == '[':
            stack.append((x, y, cur_angle, depth))
            depth += 1
        elif ch == ']':
            if stack:
                x, y, cur_angle, depth = stack.pop()


def _sierpinski(surf, x1, y1, x2, y2, x3, y3, depth, color):
    if depth == 0:
        pygame.draw.polygon(surf, color,
                            [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))])
        return
    mx1, my1 = (x1 + x2) / 2, (y1 + y2) / 2
    mx2, my2 = (x2 + x3) / 2, (y2 + y3) / 2
    mx3, my3 = (x1 + x3) / 2, (y1 + y3) / 2
    darker = tuple(max(0, c - 12 * depth) for c in color)
    _sierpinski(surf, x1, y1, mx1, my1, mx3, my3, depth - 1, color)
    _sierpinski(surf, mx1, my1, x2, y2, mx2, my2, depth - 1, darker)
    _sierpinski(surf, mx3, my3, mx2, my2, x3, y3, depth - 1, color)


def _koch_curve_pts(x1, y1, x2, y2, depth):
    if depth == 0:
        return [(x1, y1)]
    dx, dy = x2 - x1, y2 - y1
    ax, ay = x1 + dx / 3, y1 + dy / 3
    bx, by = x1 + 2 * dx / 3, y1 + 2 * dy / 3
    px = (ax + bx) / 2 + math.sqrt(3) / 6 * (y1 - y2)
    py = (ay + by) / 2 + math.sqrt(3) / 6 * (x2 - x1)
    pts = []
    pts.extend(_koch_curve_pts(x1, y1, ax, ay, depth - 1))
    pts.extend(_koch_curve_pts(ax, ay, px, py, depth - 1))
    pts.extend(_koch_curve_pts(px, py, bx, by, depth - 1))
    pts.extend(_koch_curve_pts(bx, by, x2, y2, depth - 1))
    return pts


def _koch_snowflake(cx, cy, size, depth):
    r = size * 0.45
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
              math.pi / 2 + 4 * math.pi / 3]
    verts = [(cx + r * math.cos(a), cy - r * math.sin(a)) for a in angles]
    all_pts = []
    for i in range(3):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 3]
        all_pts.extend(_koch_curve_pts(x1, y1, x2, y2, depth))
    return all_pts
