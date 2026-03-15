"""Fractal typography — L-system rune glyphs for the Resonance GUI.

Each glyph is defined as polyline segments in normalised coords (0..1).
Monospace: char_w = font_size * 0.6, char_h = font_size.

Rendering is 2-pass: glow at 40 % alpha behind, then core at full colour.
Self-similar serifs branch at stroke endpoints for sizes >= 24 px.
"""

from __future__ import annotations

import math
from typing import Sequence

import pygame

# ---------------------------------------------------------------------------
# Glyph definitions — list of polylines, each polyline is [(x, y), ...].
# Coordinates are normalised 0..1 within the character cell.
# Design goal: angular, runic, geometric — no curves, sharp edges.
# ---------------------------------------------------------------------------

_GLYPHS: dict[str, list[list[tuple[float, float]]]] = {
    # --- UPPERCASE LETTERS ---
    "A": [
        [(0.1, 1.0), (0.5, 0.0), (0.9, 1.0)],
        [(0.25, 0.55), (0.75, 0.55)],
    ],
    "B": [
        [(0.15, 1.0), (0.15, 0.0), (0.7, 0.0), (0.85, 0.15), (0.7, 0.45),
         (0.15, 0.45)],
        [(0.7, 0.45), (0.9, 0.6), (0.85, 0.85), (0.7, 1.0), (0.15, 1.0)],
    ],
    "C": [
        [(0.85, 0.15), (0.6, 0.0), (0.3, 0.0), (0.15, 0.15), (0.15, 0.85),
         (0.3, 1.0), (0.6, 1.0), (0.85, 0.85)],
    ],
    "D": [
        [(0.15, 1.0), (0.15, 0.0), (0.6, 0.0), (0.85, 0.2), (0.85, 0.8),
         (0.6, 1.0), (0.15, 1.0)],
    ],
    "E": [
        [(0.85, 0.0), (0.15, 0.0), (0.15, 1.0), (0.85, 1.0)],
        [(0.15, 0.5), (0.7, 0.5)],
    ],
    "F": [
        [(0.85, 0.0), (0.15, 0.0), (0.15, 1.0)],
        [(0.15, 0.5), (0.7, 0.5)],
    ],
    "G": [
        [(0.85, 0.15), (0.6, 0.0), (0.3, 0.0), (0.15, 0.15), (0.15, 0.85),
         (0.3, 1.0), (0.6, 1.0), (0.85, 0.85), (0.85, 0.5), (0.55, 0.5)],
    ],
    "H": [
        [(0.15, 0.0), (0.15, 1.0)],
        [(0.85, 0.0), (0.85, 1.0)],
        [(0.15, 0.5), (0.85, 0.5)],
    ],
    "I": [
        [(0.3, 0.0), (0.7, 0.0)],
        [(0.5, 0.0), (0.5, 1.0)],
        [(0.3, 1.0), (0.7, 1.0)],
    ],
    "J": [
        [(0.4, 0.0), (0.85, 0.0)],
        [(0.65, 0.0), (0.65, 0.85), (0.5, 1.0), (0.3, 1.0), (0.15, 0.85)],
    ],
    "K": [
        [(0.15, 0.0), (0.15, 1.0)],
        [(0.85, 0.0), (0.15, 0.55)],
        [(0.35, 0.4), (0.85, 1.0)],
    ],
    "L": [
        [(0.15, 0.0), (0.15, 1.0), (0.85, 1.0)],
    ],
    "M": [
        [(0.1, 1.0), (0.1, 0.0), (0.5, 0.45), (0.9, 0.0), (0.9, 1.0)],
    ],
    "N": [
        [(0.15, 1.0), (0.15, 0.0), (0.85, 1.0), (0.85, 0.0)],
    ],
    "O": [
        [(0.5, 0.0), (0.15, 0.15), (0.15, 0.85), (0.5, 1.0),
         (0.85, 0.85), (0.85, 0.15), (0.5, 0.0)],
    ],
    "P": [
        [(0.15, 1.0), (0.15, 0.0), (0.7, 0.0), (0.85, 0.15),
         (0.85, 0.35), (0.7, 0.5), (0.15, 0.5)],
    ],
    "Q": [
        [(0.5, 0.0), (0.15, 0.15), (0.15, 0.85), (0.5, 1.0),
         (0.85, 0.85), (0.85, 0.15), (0.5, 0.0)],
        [(0.6, 0.75), (0.9, 1.0)],
    ],
    "R": [
        [(0.15, 1.0), (0.15, 0.0), (0.7, 0.0), (0.85, 0.15),
         (0.85, 0.35), (0.7, 0.5), (0.15, 0.5)],
        [(0.55, 0.5), (0.85, 1.0)],
    ],
    "S": [
        [(0.85, 0.15), (0.65, 0.0), (0.35, 0.0), (0.15, 0.15),
         (0.15, 0.35), (0.85, 0.65), (0.85, 0.85), (0.65, 1.0),
         (0.35, 1.0), (0.15, 0.85)],
    ],
    "T": [
        [(0.1, 0.0), (0.9, 0.0)],
        [(0.5, 0.0), (0.5, 1.0)],
    ],
    "U": [
        [(0.15, 0.0), (0.15, 0.8), (0.3, 1.0), (0.7, 1.0),
         (0.85, 0.8), (0.85, 0.0)],
    ],
    "V": [
        [(0.1, 0.0), (0.5, 1.0), (0.9, 0.0)],
    ],
    "W": [
        [(0.05, 0.0), (0.25, 1.0), (0.5, 0.5), (0.75, 1.0), (0.95, 0.0)],
    ],
    "X": [
        [(0.15, 0.0), (0.85, 1.0)],
        [(0.85, 0.0), (0.15, 1.0)],
    ],
    "Y": [
        [(0.1, 0.0), (0.5, 0.5), (0.9, 0.0)],
        [(0.5, 0.5), (0.5, 1.0)],
    ],
    "Z": [
        [(0.15, 0.0), (0.85, 0.0), (0.15, 1.0), (0.85, 1.0)],
    ],
    # --- DIGITS ---
    "0": [
        [(0.5, 0.0), (0.2, 0.15), (0.2, 0.85), (0.5, 1.0),
         (0.8, 0.85), (0.8, 0.15), (0.5, 0.0)],
        [(0.3, 0.75), (0.7, 0.25)],  # diagonal slash for readability
    ],
    "1": [
        [(0.3, 0.2), (0.5, 0.0), (0.5, 1.0)],
        [(0.3, 1.0), (0.7, 1.0)],
    ],
    "2": [
        [(0.15, 0.15), (0.35, 0.0), (0.65, 0.0), (0.85, 0.15),
         (0.85, 0.35), (0.15, 1.0), (0.85, 1.0)],
    ],
    "3": [
        [(0.15, 0.0), (0.85, 0.0), (0.85, 0.35), (0.5, 0.5),
         (0.85, 0.65), (0.85, 1.0), (0.15, 1.0)],
    ],
    "4": [
        [(0.7, 1.0), (0.7, 0.0), (0.1, 0.65), (0.9, 0.65)],
    ],
    "5": [
        [(0.85, 0.0), (0.15, 0.0), (0.15, 0.45), (0.7, 0.45),
         (0.85, 0.6), (0.85, 0.85), (0.7, 1.0), (0.15, 1.0)],
    ],
    "6": [
        [(0.8, 0.0), (0.4, 0.0), (0.15, 0.25), (0.15, 0.85),
         (0.35, 1.0), (0.65, 1.0), (0.85, 0.85), (0.85, 0.6),
         (0.65, 0.45), (0.15, 0.45)],
    ],
    "7": [
        [(0.15, 0.0), (0.85, 0.0), (0.4, 1.0)],
    ],
    "8": [
        [(0.5, 0.0), (0.2, 0.15), (0.2, 0.35), (0.5, 0.5),
         (0.8, 0.65), (0.8, 0.85), (0.5, 1.0),
         (0.2, 0.85), (0.2, 0.65), (0.5, 0.5),
         (0.8, 0.35), (0.8, 0.15), (0.5, 0.0)],
    ],
    "9": [
        [(0.85, 0.55), (0.65, 0.55), (0.35, 0.0), (0.15, 0.15),
         (0.15, 0.4), (0.35, 0.55), (0.85, 0.55),
         (0.85, 0.15), (0.6, 0.0), (0.35, 0.0)],
        [(0.85, 0.55), (0.85, 0.85), (0.6, 1.0), (0.2, 1.0)],
    ],
    # --- PUNCTUATION / SYMBOLS ---
    ".": [
        [(0.45, 0.9), (0.55, 0.9), (0.55, 1.0), (0.45, 1.0), (0.45, 0.9)],
    ],
    ",": [
        [(0.5, 0.85), (0.5, 0.95), (0.35, 1.1)],
    ],
    ":": [
        [(0.45, 0.25), (0.55, 0.25), (0.55, 0.35), (0.45, 0.35), (0.45, 0.25)],
        [(0.45, 0.75), (0.55, 0.75), (0.55, 0.85), (0.45, 0.85), (0.45, 0.75)],
    ],
    ";": [
        [(0.45, 0.25), (0.55, 0.25), (0.55, 0.35), (0.45, 0.35), (0.45, 0.25)],
        [(0.5, 0.75), (0.5, 0.9), (0.35, 1.05)],
    ],
    "!": [
        [(0.5, 0.0), (0.5, 0.7)],
        [(0.45, 0.9), (0.55, 0.9), (0.55, 1.0), (0.45, 1.0), (0.45, 0.9)],
    ],
    "?": [
        [(0.2, 0.15), (0.35, 0.0), (0.65, 0.0), (0.8, 0.15),
         (0.8, 0.35), (0.5, 0.55), (0.5, 0.7)],
        [(0.45, 0.9), (0.55, 0.9), (0.55, 1.0), (0.45, 1.0), (0.45, 0.9)],
    ],
    "-": [
        [(0.2, 0.5), (0.8, 0.5)],
    ],
    "+": [
        [(0.2, 0.5), (0.8, 0.5)],
        [(0.5, 0.2), (0.5, 0.8)],
    ],
    "=": [
        [(0.2, 0.4), (0.8, 0.4)],
        [(0.2, 0.6), (0.8, 0.6)],
    ],
    "/": [
        [(0.15, 1.0), (0.85, 0.0)],
    ],
    "(": [
        [(0.65, 0.0), (0.35, 0.25), (0.35, 0.75), (0.65, 1.0)],
    ],
    ")": [
        [(0.35, 0.0), (0.65, 0.25), (0.65, 0.75), (0.35, 1.0)],
    ],
    "[": [
        [(0.65, 0.0), (0.35, 0.0), (0.35, 1.0), (0.65, 1.0)],
    ],
    "]": [
        [(0.35, 0.0), (0.65, 0.0), (0.65, 1.0), (0.35, 1.0)],
    ],
    "'": [
        [(0.5, 0.0), (0.5, 0.2)],
    ],
    '"': [
        [(0.35, 0.0), (0.35, 0.2)],
        [(0.65, 0.0), (0.65, 0.2)],
    ],
    "%": [
        [(0.15, 1.0), (0.85, 0.0)],
        [(0.2, 0.1), (0.35, 0.1), (0.35, 0.25), (0.2, 0.25), (0.2, 0.1)],
        [(0.65, 0.75), (0.8, 0.75), (0.8, 0.9), (0.65, 0.9), (0.65, 0.75)],
    ],
    "#": [
        [(0.3, 0.0), (0.25, 1.0)],
        [(0.7, 0.0), (0.65, 1.0)],
        [(0.1, 0.35), (0.9, 0.35)],
        [(0.1, 0.65), (0.9, 0.65)],
    ],
    "@": [
        [(0.7, 0.55), (0.55, 0.4), (0.4, 0.55), (0.55, 0.7), (0.75, 0.55),
         (0.75, 0.2), (0.55, 0.0), (0.3, 0.0), (0.15, 0.2), (0.15, 0.8),
         (0.3, 1.0), (0.65, 1.0), (0.85, 0.85)],
    ],
    "_": [
        [(0.1, 1.0), (0.9, 1.0)],
    ],
    "*": [
        [(0.5, 0.15), (0.5, 0.65)],
        [(0.2, 0.25), (0.8, 0.55)],
        [(0.8, 0.25), (0.2, 0.55)],
    ],
    "~": [
        [(0.1, 0.55), (0.3, 0.4), (0.5, 0.55), (0.7, 0.4), (0.9, 0.55)],
    ],
    "<": [
        [(0.8, 0.15), (0.2, 0.5), (0.8, 0.85)],
    ],
    ">": [
        [(0.2, 0.15), (0.8, 0.5), (0.2, 0.85)],
    ],
    "^": [
        [(0.2, 0.35), (0.5, 0.05), (0.8, 0.35)],
    ],
    "&": [
        [(0.85, 1.0), (0.4, 0.5), (0.55, 0.2), (0.45, 0.0), (0.25, 0.0),
         (0.15, 0.15), (0.25, 0.35), (0.85, 0.75)],
    ],
    "$": [
        [(0.5, -0.05), (0.5, 1.05)],
        [(0.8, 0.15), (0.6, 0.0), (0.4, 0.0), (0.2, 0.15),
         (0.2, 0.35), (0.8, 0.65), (0.8, 0.85), (0.6, 1.0),
         (0.4, 1.0), (0.2, 0.85)],
    ],
    # lowercase — map to uppercase for runic consistency
}

# Fill lowercase → uppercase mappings
for _ch in "abcdefghijklmnopqrstuvwxyz":
    _GLYPHS[_ch] = _GLYPHS[_ch.upper()]


# ---------------------------------------------------------------------------
# Serif branching — self-similar decorations at stroke endpoints
# ---------------------------------------------------------------------------

def _draw_serif(
    surf: pygame.Surface,
    x: float, y: float,
    angle: float, length: float,
    depth: int, color: tuple[int, ...],
) -> None:
    """Recursively draw forking serif branches at a stroke endpoint."""
    if depth <= 0 or length < 1.0:
        return
    ex = x + math.cos(angle) * length
    ey = y + math.sin(angle) * length
    pygame.draw.line(surf, color, (int(x), int(y)), (int(ex), int(ey)), 1)
    _draw_serif(surf, ex, ey, angle + 0.6, length * 0.5, depth - 1, color)
    _draw_serif(surf, ex, ey, angle - 0.6, length * 0.5, depth - 1, color)


def _serif_depth(font_size: int) -> int:
    """Determine serif branching depth from font size."""
    if font_size >= 36:
        return 2
    if font_size >= 24:
        return 1
    return 0


# ---------------------------------------------------------------------------
# FractalFont — cached glyph renderer
# ---------------------------------------------------------------------------

class FractalFont:
    """L-system rune font with caching and 2-pass glow rendering."""

    def __init__(self) -> None:
        # Cache: (char, size, r, g, b) → Surface
        self._cache: dict[tuple[str, int, int, int, int], pygame.Surface] = {}
        # Fallback pygame font cache: size → Font
        self._sysfont_cache: dict[int, pygame.font.Font] = {}

    def _get_sysfont(self, size: int) -> pygame.font.Font:
        if size not in self._sysfont_cache:
            self._sysfont_cache[size] = pygame.font.SysFont(None, size)
        return self._sysfont_cache[size]

    def _render_glyph(
        self,
        char: str,
        size: int,
        color: tuple[int, ...],
    ) -> pygame.Surface:
        """Render a single glyph to a surface with glow + core + serifs."""
        cw = max(1, int(size * 0.6))
        ch = max(1, size)
        # Extra padding for serifs and glow
        pad = max(4, size // 6)
        surf_w = cw + pad * 2
        surf_h = ch + pad * 2
        surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        polylines = _GLYPHS.get(char)
        if polylines is None:
            # Unknown char — render with system font
            sf = self._get_sysfont(size)
            txt = sf.render(char, True, color)
            surf = pygame.Surface(
                (max(surf_w, txt.get_width() + pad * 2), surf_h),
                pygame.SRCALPHA,
            )
            surf.blit(txt, (pad, pad))
            return surf

        line_w = max(1, size // 14)
        glow_w = line_w + 2
        sdepth = _serif_depth(size)
        serif_len = size * 0.12

        # Compute scaled points for each polyline
        scaled_lines: list[list[tuple[int, int]]] = []
        for polyline in polylines:
            pts = [
                (int(px * cw + pad), int(py * ch + pad))
                for px, py in polyline
            ]
            if len(pts) >= 2:
                scaled_lines.append(pts)

        # Glow colour — same hue, 40 % alpha
        glow_color = (color[0], color[1], color[2], 100)

        # Pass 1: glow (skip at small sizes — just adds blur)
        if size >= 14:
            for pts in scaled_lines:
                pygame.draw.lines(surf, glow_color, False, pts, glow_w)

        # Pass 2: core strokes
        for pts in scaled_lines:
            pygame.draw.lines(surf, color, False, pts, line_w)

        # Pass 3: serifs at polyline endpoints
        if sdepth > 0:
            for pts in scaled_lines:
                for i, (px, py) in enumerate(pts):
                    if i == 0 or i == len(pts) - 1:
                        # Compute angle from/to adjacent point
                        if i == 0 and len(pts) > 1:
                            dx = pts[0][0] - pts[1][0]
                            dy = pts[0][1] - pts[1][1]
                        else:
                            dx = pts[-1][0] - pts[-2][0]
                            dy = pts[-1][1] - pts[-2][1]
                        angle = math.atan2(dy, dx)
                        _draw_serif(surf, px, py, angle, serif_len, sdepth, color)

        return surf

    def _get_glyph(
        self,
        char: str,
        size: int,
        color: tuple[int, ...],
    ) -> pygame.Surface:
        """Get cached glyph surface, rendering if needed."""
        key = (char, size, color[0], color[1], color[2])
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        surf = self._render_glyph(char, size, color)
        self._cache[key] = surf
        return surf

    def render(
        self,
        text: str,
        size: int,
        color: tuple[int, ...],
    ) -> pygame.Surface:
        """Render a full string to a surface. Cached per-glyph."""
        if not text:
            return pygame.Surface((0, 0), pygame.SRCALPHA)

        # Fallback: long strings or sub-pixel sizes use system font
        if size < 7 or len(text) > 50:
            sf = self._get_sysfont(size)
            return sf.render(text, True, color)

        cw = max(1, int(size * 0.6))
        pad = max(4, size // 6)
        total_w = cw * len(text) + pad  # slight right padding
        total_h = size + pad * 2
        result = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        x = 0
        for ch in text:
            glyph = self._get_glyph(ch, size, color)
            result.blit(glyph, (x, 0))
            x += cw

        return result

    def draw(
        self,
        surf: pygame.Surface,
        text: str,
        x: int, y: int,
        size: int,
        color: tuple[int, ...] = (220, 220, 220),
        center: bool = False,
    ) -> pygame.Rect:
        """Render text and blit onto target surface. Returns bounding rect."""
        rendered = self.render(text, size, color)
        r = rendered.get_rect()
        if center:
            r.center = (x, y)
        else:
            r.topleft = (x, y)
        surf.blit(rendered, r)
        return r

    def size(self, text: str, font_size: int) -> tuple[int, int]:
        """Return (width, height) of rendered text without actually blitting."""
        if not text:
            return (0, 0)
        if font_size < 13 or len(text) > 50:
            sf = self._get_sysfont(font_size)
            return sf.size(text)
        cw = max(1, int(font_size * 0.6))
        pad = max(4, font_size // 6)
        return (cw * len(text) + pad, font_size + pad * 2)

    def clear_cache(self) -> None:
        """Clear all cached glyph surfaces."""
        self._cache.clear()


# Module-level singleton
fractal_font = FractalFont()
