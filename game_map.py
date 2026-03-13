import random
import math
from constants import (MAP_COLS, MAP_ROWS, TERRAIN_GRASS,
                       TERRAIN_TREE, TERRAIN_GOLD, TERRAIN_IRON,
                       TERRAIN_STONE,
                       TERRAIN_MOVE_COST, RESOURCE_CAPACITY)
from utils import clamp


class GameMap:
    def __init__(self):
        self.cols = MAP_COLS
        self.rows = MAP_ROWS
        self.tiles = [[TERRAIN_GRASS for _ in range(self.cols)] for _ in range(self.rows)]
        self.resource_remaining = {}  # (col, row) -> amount
        self.generate()

    def generate(self):
        # clear area around center for starting base
        center_c, center_r = self.cols // 2, self.rows // 2

        # tree forests
        for _ in range(random.randint(15, 22)):
            c = random.randint(3, self.cols - 4)
            r = random.randint(3, self.rows - 4)
            if abs(c - center_c) < 6 and abs(r - center_r) < 6:
                continue
            size = random.randint(8, 30)
            self._place_cluster(c, r, size, TERRAIN_TREE)

        # gold deposits
        for _ in range(random.randint(5, 8)):
            c = random.randint(5, self.cols - 6)
            r = random.randint(5, self.rows - 6)
            if abs(c - center_c) < 6 and abs(r - center_r) < 6:
                continue
            size = random.randint(3, 6)
            self._place_cluster(c, r, size, TERRAIN_GOLD)

        # iron deposits
        for _ in range(random.randint(4, 7)):
            c = random.randint(5, self.cols - 6)
            r = random.randint(5, self.rows - 6)
            if abs(c - center_c) < 6 and abs(r - center_r) < 6:
                continue
            size = random.randint(3, 6)
            self._place_cluster(c, r, size, TERRAIN_IRON)

        # v10: stone deposits
        for _ in range(random.randint(3, 5)):
            c = random.randint(5, self.cols - 6)
            r = random.randint(5, self.rows - 6)
            if abs(c - center_c) < 6 and abs(r - center_r) < 6:
                continue
            size = random.randint(4, 8)
            self._place_cluster(c, r, size, TERRAIN_STONE)

        # ensure some trees and gold near start (but not too close)
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            d = random.uniform(7, 12)
            c = int(center_c + math.cos(angle) * d)
            r = int(center_r + math.sin(angle) * d)
            self._place_cluster(c, r, random.randint(6, 15), TERRAIN_TREE)

        for _ in range(2):
            angle = random.uniform(0, 2 * math.pi)
            d = random.uniform(8, 14)
            c = int(center_c + math.cos(angle) * d)
            r = int(center_r + math.sin(angle) * d)
            self._place_cluster(c, r, random.randint(3, 5), TERRAIN_GOLD)

        # init resource remaining
        for r in range(self.rows):
            for c in range(self.cols):
                t = self.tiles[r][c]
                if t in RESOURCE_CAPACITY:
                    self.resource_remaining[(c, r)] = RESOURCE_CAPACITY[t]

        # clear starting area
        for dr in range(-4, 5):
            for dc in range(-4, 5):
                nc, nr = center_c + dc, center_r + dr
                if 0 <= nc < self.cols and 0 <= nr < self.rows:
                    if self.tiles[nr][nc] != TERRAIN_GRASS:
                        self.resource_remaining.pop((nc, nr), None)
                        self.tiles[nr][nc] = TERRAIN_GRASS

    def _place_cluster(self, sc, sr, count, terrain):
        placed = 0
        c, r = sc, sr
        for _ in range(count * 3):
            if placed >= count:
                break
            if 1 <= c < self.cols - 1 and 1 <= r < self.rows - 1:
                if self.tiles[r][c] == TERRAIN_GRASS:
                    self.tiles[r][c] = terrain
                    placed += 1
            c += random.choice([-1, 0, 1])
            r += random.choice([-1, 0, 1])
            c = clamp(c, 1, self.cols - 2)
            r = clamp(r, 1, self.rows - 2)

    def get_tile(self, c, r):
        if 0 <= c < self.cols and 0 <= r < self.rows:
            return self.tiles[r][c]
        return -1  # out of bounds — not in TERRAIN_MOVE_COST, so impassable

    def is_walkable(self, c, r):
        """Grass only — used for building placement."""
        if 0 <= c < self.cols and 0 <= r < self.rows:
            return self.tiles[r][c] == TERRAIN_GRASS
        return False

    def is_passable(self, c, r):
        """Check if tile is passable (in TERRAIN_MOVE_COST)."""
        if 0 <= c < self.cols and 0 <= r < self.rows:
            return self.tiles[r][c] in TERRAIN_MOVE_COST
        return False

    def is_buildable(self, c, r):
        return self.is_walkable(c, r)

    def harvest(self, c, r, amount):
        """Remove resources from tile, return (type_str, amount_harvested)."""
        t = self.tiles[r][c]
        if t == TERRAIN_TREE:
            rtype = "wood"
        elif t == TERRAIN_GOLD:
            rtype = "gold"
        elif t == TERRAIN_IRON:
            rtype = "iron"
        elif t == TERRAIN_STONE:
            rtype = "stone"
        else:
            return None, 0
        remaining = self.resource_remaining.get((c, r), 0)
        taken = min(amount, remaining)
        self.resource_remaining[(c, r)] = remaining - taken
        if self.resource_remaining[(c, r)] <= 0:
            self.tiles[r][c] = TERRAIN_GRASS
            del self.resource_remaining[(c, r)]
        return rtype, taken
