"""Fractal UI utilities — Koch borders, radial gradients, resource icons.

Provides the visual primitives for the Resonance fractal interface.
All heavy rendering is cached to surfaces.
"""

from __future__ import annotations

import math
from typing import Sequence

import pygame


# ---------------------------------------------------------------------------
# Koch border system
# ---------------------------------------------------------------------------

# Max perpendicular bump height in pixels (keeps Koch ornamental on any size)
_KOCH_MAX_BUMP_PX = 6.0


def _koch_subdivide(
    p1: tuple[float, float],
    p2: tuple[float, float],
    depth: int,
) -> list[tuple[float, float]]:
    """Recursively subdivide a line segment into a Koch curve.

    Bump height is capped to _KOCH_MAX_BUMP_PX pixels regardless of segment
    length, keeping the pattern ornamental on wide panels and small buttons alike.
    """
    if depth <= 0:
        return [p1, p2]

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    seg_len = math.hypot(dx, dy)

    a = (p1[0] + dx / 3, p1[1] + dy / 3)
    b = (p1[0] + dx * 2 / 3, p1[1] + dy * 2 / 3)

    # Perpendicular unit vector
    if seg_len > 0.01:
        nx = -(b[1] - a[1]) / (seg_len / 3)
        ny = (b[0] - a[0]) / (seg_len / 3)
    else:
        nx, ny = 0.0, 0.0

    # Bump height: fraction of segment but capped to max pixels
    bump = min(seg_len / 3 * 0.3, _KOCH_MAX_BUMP_PX)

    mx = (a[0] + b[0]) / 2 + nx * bump
    my = (a[1] + b[1]) / 2 + ny * bump

    pts: list[tuple[float, float]] = []
    pts.extend(_koch_subdivide(p1, a, depth - 1)[:-1])
    pts.extend(_koch_subdivide(a, (mx, my), depth - 1)[:-1])
    pts.extend(_koch_subdivide((mx, my), b, depth - 1)[:-1])
    pts.extend(_koch_subdivide(b, p2, depth - 1))
    return pts


# Cache: (x, y, w, h, depth, r, g, b, line_w) → Surface
_koch_border_cache: dict[tuple[int, int, int, int, int, int, int, int, int], pygame.Surface] = {}


def koch_border(
    surf: pygame.Surface,
    rect: tuple[int, int, int, int],
    depth: int,
    color: tuple[int, int, int],
    line_width: int = 1,
) -> None:
    """Draw a Koch snowflake border inside a rectangle.

    Koch bumps fold inward — the surface is clipped to the rect bounds.
    Cached per (rect, depth, color, line_width) tuple.
    """
    x, y, w, h = rect
    key = (x, y, w, h, depth, color[0], color[1], color[2], line_width)
    cached = _koch_border_cache.get(key)
    if cached is not None:
        surf.blit(cached, (x, y))
        return

    # Render to a surface exactly the size of the rect (natural clipping)
    border_surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Four corners in local coords
    corners = [
        (0.0, 0.0),                    # top-left
        (float(w), 0.0),               # top-right
        (float(w), float(h)),           # bottom-right
        (0.0, float(h)),               # bottom-left
    ]

    for i in range(4):
        p1 = corners[i]
        p2 = corners[(i + 1) % 4]
        pts = _koch_subdivide(p1, p2, depth)
        if len(pts) >= 2:
            # Clamp points to surface bounds
            int_pts = [
                (max(0, min(w - 1, int(px))), max(0, min(h - 1, int(py))))
                for px, py in pts
            ]
            pygame.draw.lines(border_surf, color, False, int_pts, line_width)

    # Cache and blit
    _koch_border_cache[key] = border_surf
    surf.blit(border_surf, (x, y))


def koch_border_animated(
    surf: pygame.Surface,
    rect: tuple[int, int, int, int],
    game_time: float,
    color: tuple[int, int, int],
    line_width: int = 1,
    base_depth: float = 1.0,
    breath_amp: float = 0.5,
    breath_freq: float = 0.3,
) -> None:
    """Draw a breathing Koch border.

    depth oscillates: base_depth + breath_amp * sin(game_time * breath_freq * 2pi)
    Since Koch depth must be integer, we interpolate by blending two depths.
    """
    depth_float = base_depth + breath_amp * math.sin(game_time * breath_freq * 2 * math.pi)
    depth_int = max(0, int(depth_float))
    frac = depth_float - depth_int

    # Always draw the base depth
    koch_border(surf, rect, depth_int, color, line_width)

    # If fractional part is significant and next depth exists, overlay with alpha
    if frac > 0.2 and depth_int < 3:
        # Draw the next depth at reduced alpha
        alpha = int(frac * 180)
        temp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        higher_color = (color[0], color[1], color[2])
        koch_border(temp, rect, depth_int + 1, higher_color, line_width)
        temp.set_alpha(alpha)
        surf.blit(temp, (0, 0))


# ---------------------------------------------------------------------------
# Radial gradient backgrounds
# ---------------------------------------------------------------------------

def radial_gradient(
    width: int, height: int,
    center_color: tuple[int, int, int],
    edge_color: tuple[int, int, int],
) -> pygame.Surface:
    """Generate a radial gradient surface via concentric ellipses.

    Uses concentric filled circles (fast in pygame) rather than per-pixel math.
    Call once at init, cache the result.
    """
    surf = pygame.Surface((width, height))
    surf.fill(edge_color)
    cx, cy = width // 2, height // 2
    max_r = int(math.hypot(cx, cy)) + 1
    steps = min(max_r, 64)  # 64 rings is plenty smooth

    for i in range(steps, -1, -1):
        t = i / steps
        r = int(t * max_r)
        if r < 1:
            continue
        c = tuple(
            int(center_color[ch] * (1.0 - t) + edge_color[ch] * t)
            for ch in range(3)
        )
        pygame.draw.ellipse(surf, c, (cx - r, cy - r, r * 2, r * 2))

    return surf


# ---------------------------------------------------------------------------
# Mathematical resource icons
# ---------------------------------------------------------------------------

def draw_fibonacci_spiral(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, int, int],
    turns: int = 3,
) -> None:
    """Draw a Fibonacci spiral (golden spiral) icon for Flux/Gold."""
    pts: list[tuple[int, int]] = []
    phi = (1 + math.sqrt(5)) / 2
    steps = turns * 20
    for i in range(steps):
        theta = i * (math.pi / 2) / 20  # quarter-turn per 20 steps
        r = radius * (phi ** (2 * theta / math.pi - 2))
        r = min(r, radius)
        x = cx + int(r * math.cos(theta))
        y = cy - int(r * math.sin(theta))
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, 1)


def draw_binary_tree(
    surf: pygame.Surface,
    cx: int, cy: int, size: int,
    color: tuple[int, int, int],
    depth: int = 3,
) -> None:
    """Draw a recursive Y-branch binary tree icon for Fiber/Wood."""
    def _branch(
        x: float, y: float, length: float, angle: float, d: int,
    ) -> None:
        if d <= 0 or length < 1:
            return
        ex = x + math.cos(angle) * length
        ey = y + math.sin(angle) * length
        pygame.draw.line(
            surf, color,
            (int(x), int(y)), (int(ex), int(ey)), 1,
        )
        _branch(ex, ey, length * 0.65, angle - 0.5, d - 1)
        _branch(ex, ey, length * 0.65, angle + 0.5, d - 1)

    # Trunk starts from bottom-center, grows upward
    _branch(cx, cy + size // 2, size * 0.5, -math.pi / 2, depth)


def draw_octahedron(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, int, int],
) -> None:
    """Draw an octahedron wireframe projection for Ore/Iron."""
    r = radius
    # 6 vertices of octahedron projected to 2D
    top = (cx, cy - r)
    bot = (cx, cy + r)
    left = (cx - r, cy)
    right = (cx + r, cy)
    front = (cx - r // 3, cy + r // 4)
    back = (cx + r // 3, cy - r // 4)

    edges = [
        (top, left), (top, right), (top, front), (top, back),
        (bot, left), (bot, right), (bot, front), (bot, back),
        (left, front), (front, right), (right, back), (back, left),
    ]
    for p1, p2 in edges:
        pygame.draw.line(surf, color, p1, p2, 1)


def draw_reuleaux_triangle(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, int, int],
) -> None:
    """Draw a Reuleaux triangle (constant-width curve) for Alloy/Steel."""
    # Three vertices of equilateral triangle
    verts: list[tuple[float, float]] = []
    for i in range(3):
        angle = math.pi / 2 + i * 2 * math.pi / 3
        verts.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))

    # Each arc: from vertex i+1 to vertex i+2, centered at vertex i
    # Arc radius = side length = radius * sqrt(3)
    side = radius * math.sqrt(3)
    pts: list[tuple[int, int]] = []
    for i in range(3):
        center = verts[i]
        start_v = verts[(i + 1) % 3]
        end_v = verts[(i + 2) % 3]
        start_angle = math.atan2(-(start_v[1] - center[1]), start_v[0] - center[0])
        end_angle = math.atan2(-(end_v[1] - center[1]), end_v[0] - center[0])
        # Ensure we sweep the shorter arc
        if end_angle < start_angle:
            end_angle += 2 * math.pi
        steps = 12
        for s in range(steps + 1):
            t = start_angle + (end_angle - start_angle) * s / steps
            px = center[0] + side * math.cos(t)
            py = center[1] - side * math.sin(t)
            pts.append((int(px), int(py)))

    if len(pts) >= 2:
        pygame.draw.lines(surf, color, True, pts, 1)


def draw_voronoi_cluster(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, int, int],
    cells: int = 5,
) -> None:
    """Draw a Voronoi cell cluster for Crystal/Stone."""
    # Fixed seed points in normalised space for consistent icon
    seeds = [
        (0.0, 0.0), (-0.5, -0.5), (0.5, -0.4),
        (-0.4, 0.5), (0.5, 0.5),
    ][:cells]

    # Draw cell boundaries as lines between adjacent seeds
    for i, (sx, sy) in enumerate(seeds):
        for j in range(i + 1, len(seeds)):
            ox, oy = seeds[j]
            dx, dy = ox - sx, oy - sy
            dist = math.hypot(dx, dy)
            if dist < 1.2:  # only draw edges for close neighbors
                # Perpendicular bisector segment
                mx = (sx + ox) / 2 * radius + cx
                my = (sy + oy) / 2 * radius + cy
                nx, ny = -dy / dist, dx / dist
                half = radius * 0.4
                p1 = (int(mx + nx * half), int(my + ny * half))
                p2 = (int(mx - nx * half), int(my - ny * half))
                pygame.draw.line(surf, color, p1, p2, 1)

    # Draw cell center dots
    for sx, sy in seeds:
        px = int(sx * radius + cx)
        py = int(sy * radius + cy)
        pygame.draw.circle(surf, color, (px, py), 1)


# ---------------------------------------------------------------------------
# Fractal HP / progress bars
# ---------------------------------------------------------------------------

# Cache wave textures: (h, r, g, b) → Surface (1-pixel-wide column, tiled)
_bar_wave_cache: dict[tuple[int, int, int, int], pygame.Surface] = {}


def _get_wave_column(h: int, color: tuple[int, ...]) -> pygame.Surface:
    """Get a cached 1×h column with vertical gradient in the given color."""
    key = (h, color[0], color[1], color[2])
    cached = _bar_wave_cache.get(key)
    if cached is not None:
        return cached
    col_surf = pygame.Surface((1, h), pygame.SRCALPHA)
    for py in range(h):
        t = abs(py - h / 2) / (h / 2) if h > 1 else 0
        bri = 1.0 - t * 0.5
        col_surf.set_at((0, py), (
            int(color[0] * bri),
            int(color[1] * bri),
            int(color[2] * bri),
            220,
        ))
    _bar_wave_cache[key] = col_surf
    return col_surf


def fractal_bar(
    surf: pygame.Surface,
    x: int, y: int, w: int, h: int,
    ratio: float,
    color: tuple[int, ...],
    game_time: float = 0.0,
    border: bool = True,
    border_col: tuple[int, ...] | None = None,
) -> None:
    """Draw a sine-wave textured bar with optional Koch border.

    Used for HP bars, build progress, tension meters.
    The fill has a subtle sine-wave brightness modulation.
    """
    ratio = max(0.0, min(1.0, ratio))
    # Background
    pygame.draw.rect(surf, (25, 22, 35), (x, y, w, h))

    fill_w = int(w * ratio)
    if fill_w > 0:
        # Scale cached gradient column to fill width
        col = _get_wave_column(h, color)
        bar_surf = pygame.transform.scale(col, (fill_w, h))
        surf.blit(bar_surf, (x, y))

    if border:
        if border_col is not None:
            bc = border_col
        else:
            bc = (
                min(255, color[0] // 2 + 40),
                min(255, color[1] // 2 + 35),
                min(255, color[2] // 2 + 30),
            )
        pygame.draw.rect(surf, bc, (x, y, w, h), 1)


def fractal_bar_simple(
    surf: pygame.Surface,
    x: int, y: int, w: int, h: int,
    ratio: float,
    color: tuple[int, ...],
) -> None:
    """Fast fractal bar for in-world use (no animation, no Koch border).

    Draws a gradient-filled bar suitable for overhead HP bars on units/buildings.
    Uses pygame.transform.scale on a cached 1px column for speed.
    """
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surf, (25, 22, 35), (x, y, w, h))
    fill_w = int(w * ratio)
    if fill_w > 0:
        col = _get_wave_column(h, color)
        fill_surf = pygame.transform.scale(col, (fill_w, h))
        surf.blit(fill_surf, (x, y))


# Map resource code names to icon draw functions
RESOURCE_ICON_FUNCS = {
    "gold": draw_fibonacci_spiral,
    "wood": draw_binary_tree,
    "iron": draw_octahedron,
    "steel": draw_reuleaux_triangle,
    "stone": draw_voronoi_cluster,
}


def draw_resource_icon(
    surf: pygame.Surface,
    resource: str,
    cx: int, cy: int,
    radius: int,
    color: tuple[int, int, int],
) -> None:
    """Draw the mathematical icon for a resource type."""
    func = RESOURCE_ICON_FUNCS.get(resource)
    if func is None:
        # Fallback: simple diamond
        pts = [(cx, cy - radius), (cx + radius, cy),
               (cx, cy + radius), (cx - radius, cy)]
        pygame.draw.lines(surf, color, True, pts, 1)
        return
    func(surf, cx, cy, radius, color)


# ---------------------------------------------------------------------------
# Selection rings — per-unit-type fractal selection indicators
# ---------------------------------------------------------------------------

def draw_hex_ring(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, ...],
    line_width: int = 2,
) -> None:
    """Superellipse hex ring for Gatherers (workers)."""
    pts: list[tuple[int, int]] = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3  # flat-top hex
        px = cx + int(radius * math.cos(angle))
        py = cy + int(radius * math.sin(angle))
        pts.append((px, py))
    pygame.draw.polygon(surf, color, pts, line_width)


def draw_rose_ring(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, ...],
    petals: int = 5,
    line_width: int = 2,
) -> None:
    """Polar rose ring for Wardens (soldiers). r = cos(k*theta)."""
    pts: list[tuple[int, int]] = []
    steps = petals * 20
    for i in range(steps + 1):
        theta = i * 2 * math.pi / steps
        r = radius * abs(math.cos(petals * theta / 2))
        r = max(r, radius * 0.3)  # minimum inner radius so it's always visible
        px = cx + int(r * math.cos(theta))
        py = cy + int(r * math.sin(theta))
        pts.append((px, py))
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, True, pts, line_width)


def draw_spiral_ring(
    surf: pygame.Surface,
    cx: int, cy: int, radius: int,
    color: tuple[int, ...],
    line_width: int = 2,
) -> None:
    """Golden spiral arc ring for Rangers (archers)."""
    pts: list[tuple[int, int]] = []
    phi = (1 + math.sqrt(5)) / 2
    steps = 40
    for i in range(steps + 1):
        theta = i * 1.5 * math.pi / steps  # ~270 degrees of spiral
        r = radius * 0.4 * (phi ** (2 * theta / math.pi))
        r = min(r, radius)
        px = cx + int(r * math.cos(theta))
        py = cy - int(r * math.sin(theta))
        pts.append((px, py))
    # Close with an arc back
    for i in range(steps + 1):
        theta = 1.5 * math.pi - i * 1.5 * math.pi / steps
        px = cx + int(radius * math.cos(theta))
        py = cy - int(radius * math.sin(theta))
        pts.append((px, py))
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, True, pts, line_width)


def draw_selection_ring(
    surf: pygame.Surface,
    unit_type: str,
    cx: int, cy: int, radius: int,
    color: tuple[int, ...],
    line_width: int = 2,
) -> None:
    """Draw unit-type-appropriate selection ring."""
    if unit_type == "worker":
        draw_hex_ring(surf, cx, cy, radius, color, line_width)
    elif unit_type in ("soldier", "enemy_soldier"):
        draw_rose_ring(surf, cx, cy, radius, color, 5, line_width)
    elif unit_type in ("archer", "enemy_archer"):
        draw_spiral_ring(surf, cx, cy, radius, color, line_width)
    else:
        # Default: simple circle for other types
        pygame.draw.circle(surf, color, (cx, cy), radius, line_width)
