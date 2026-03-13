# ---------------------------------------------------------------------------
# Spatial Grid — O(1) neighbor lookup for unit proximity queries
# ---------------------------------------------------------------------------
import math


class SpatialGrid:
    """Uniform grid for fast spatial queries. Replaces O(n^2) all-pairs checks
    with O(n) rebuild + O(k) neighbor lookup where k = units in nearby cells."""

    __slots__ = ('cell_size', 'inv_cell', 'cells')

    def __init__(self, cell_size=80):
        self.cell_size = cell_size
        self.inv_cell = 1.0 / cell_size
        self.cells = {}  # (cx, cy) -> list of units

    def clear(self):
        self.cells.clear()

    def insert(self, unit):
        cx = int(unit.x * self.inv_cell)
        cy = int(unit.y * self.inv_cell)
        key = (cx, cy)
        bucket = self.cells.get(key)
        if bucket is None:
            self.cells[key] = [unit]
        else:
            bucket.append(unit)

    def rebuild(self, units):
        """Clear and re-insert all alive units. Call once per frame."""
        self.cells.clear()
        inv = self.inv_cell
        cells = self.cells
        for u in units:
            if not u.alive:
                continue
            key = (int(u.x * inv), int(u.y * inv))
            bucket = cells.get(key)
            if bucket is None:
                cells[key] = [u]
            else:
                bucket.append(u)

    def query_radius(self, x, y, radius):
        """Return all units within radius of (x, y). Yields units (caller filters)."""
        inv = self.inv_cell
        r_cells = int(math.ceil(radius * inv))
        cx0 = int(x * inv)
        cy0 = int(y * inv)
        cells = self.cells
        result = []
        for dcx in range(-r_cells, r_cells + 1):
            for dcy in range(-r_cells, r_cells + 1):
                bucket = cells.get((cx0 + dcx, cy0 + dcy))
                if bucket:
                    result.extend(bucket)
        return result

    def query_nearby(self, x, y):
        """Return units in the same cell and 8 neighbors (3x3 grid around point)."""
        inv = self.inv_cell
        cx = int(x * inv)
        cy = int(y * inv)
        cells = self.cells
        result = []
        for dcx in range(-1, 2):
            for dcy in range(-1, 2):
                bucket = cells.get((cx + dcx, cy + dcy))
                if bucket:
                    result.extend(bucket)
        return result
