import math
import pygame
from constants import TILE_SIZE, COL_TEXT, BUILDING_DEFS, RUIN_REBUILD_FRACTION


def dist(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def tile_center(col, row):
    return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2


def pos_to_tile(x, y):
    return int(x // TILE_SIZE), int(y // TILE_SIZE)


def draw_text(surf, text, x, y, font, color=COL_TEXT, center=False):
    s = font.render(text, True, color)
    r = s.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(s, r)
    return r


def ruin_rebuild_cost(building_type):
    """Return (gold, wood, iron, steel, stone) cost to rebuild a ruined building."""
    bdef = BUILDING_DEFS[building_type]
    return (
        int(bdef["gold"] * RUIN_REBUILD_FRACTION),
        int(bdef["wood"] * RUIN_REBUILD_FRACTION),
        int(bdef["iron"] * RUIN_REBUILD_FRACTION),
        int(bdef["steel"] * RUIN_REBUILD_FRACTION),
        int(bdef.get("stone", 0) * RUIN_REBUILD_FRACTION),
    )
