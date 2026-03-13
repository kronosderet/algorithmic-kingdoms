"""
SquadManager — persistent squads with fractal formations (v10_6).

Squads persist until leader dies (with promotion). Four mathematical
formation types that echo the game's algorithmic art identity:
  - Polar Rose:      r = cos(kθ) — soldiers on petal tips, archers in valleys
  - Golden Spiral:   Vogel sunflower — Fibonacci-spaced assault formation
  - Sierpinski:      Recursive triangles — anti-AOE spread
  - Koch Snowflake:  Perimeter distribution — guard/defensive ring
"""
import math
from constants import (
    SQUAD_MAX_SIZE, SQUAD_FOLLOW_DIST,
    STANCE_AGGRESSIVE,
    FORMATION_POLAR_ROSE, FORMATION_GOLDEN_SPIRAL,
    FORMATION_SIERPINSKI, FORMATION_KOCH,
    FORMATION_ROSE_SPACING, FORMATION_SPIRAL_C,
    FORMATION_SIERPINSKI_SPACING, FORMATION_KOCH_RADIUS,
)
from utils import dist

# Golden ratio
_PHI = (1.0 + math.sqrt(5.0)) / 2.0
_GOLDEN_ANGLE = 2.0 * math.pi / (_PHI * _PHI)  # ~137.508 degrees


# ---------------------------------------------------------------------------
# Formation Slot Calculators (pure math — no unit imports)
# ---------------------------------------------------------------------------

def _polar_rose_slot(n, slot_index, front_dx, front_dy):
    """Polar rose: r = cos(k*theta). k scales with squad size.

    Self-similar — same math as soldier unit shapes. 3 units → 2 petals,
    6 → 3 petals, 10 → 5 petals. Leader at center.
    """
    if slot_index == 0:
        return (0.0, 0.0)
    spacing = FORMATION_ROSE_SPACING
    k = 0.5 + n / 4.0  # petal count scales with squad size
    # Distribute followers around rose curve
    followers = max(1, n - 1)
    theta = (2.0 * math.pi * (slot_index - 1)) / followers
    r = abs(math.cos(k * theta)) * spacing + spacing * 0.4
    # Rotate by front direction
    angle = math.atan2(front_dy, front_dx)
    x = r * math.cos(theta + angle)
    y = r * math.sin(theta + angle)
    return (x, y)


def _golden_spiral_slot(n, slot_index, front_dx, front_dy):
    """Vogel sunflower: θ_n = n * golden_angle, r_n = c * sqrt(n).

    Fibonacci-spaced — same golden ratio as archer bow shapes.
    Natural flanking: outer slots wrap around obstacles.
    """
    if slot_index == 0:
        return (0.0, 0.0)
    c = FORMATION_SPIRAL_C
    theta = slot_index * _GOLDEN_ANGLE
    r = c * math.sqrt(slot_index)
    angle = math.atan2(front_dy, front_dx)
    x = r * math.cos(theta + angle)
    y = r * math.sin(theta + angle)
    return (x, y)


def _sierpinski_points(depth, spacing):
    """Generate vertex positions for Sierpinski triangle at given depth.

    Same fractal as barracks building shape. Self-similar recursive
    triangles that naturally spread units to counter AOE.
    """
    h = spacing * math.sqrt(3.0) / 2.0
    base = [(-spacing / 2.0, h / 3.0), (spacing / 2.0, h / 3.0), (0.0, -2.0 * h / 3.0)]
    if depth <= 1:
        return base
    sub = _sierpinski_points(depth - 1, spacing / 2.0)
    result = []
    for bx, by in base:
        for sx, sy in sub:
            result.append((bx + sx, by + sy))
    return result


def _sierpinski_slot(n, slot_index, front_dx, front_dy):
    """Sierpinski triangle: recursive triangular clusters.

    depth = floor(log3(n)). 3 units → triangle. 9 → depth-2 fractal.
    Soldiers on vertices, archers at centroids.
    """
    if slot_index == 0:
        return (0.0, 0.0)
    spacing = FORMATION_SIERPINSKI_SPACING
    depth = max(1, int(math.log(max(3, n)) / math.log(3)))
    positions = _sierpinski_points(depth, spacing)
    if slot_index - 1 < len(positions):
        px, py = positions[slot_index - 1]
    else:
        # Overflow: pack extra units in a ring
        theta = 2.0 * math.pi * slot_index / max(1, n)
        ring_r = spacing * depth
        px = ring_r * math.cos(theta)
        py = ring_r * math.sin(theta)
    angle = math.atan2(front_dy, front_dx)
    rx = px * math.cos(angle) - py * math.sin(angle)
    ry = px * math.sin(angle) + py * math.cos(angle)
    return (rx, ry)


def _koch_perimeter(depth, radius):
    """Generate points along a Koch snowflake perimeter.

    Same fractal as tower building shape. Each segment subdivides into
    the classic 1/3 + peak + 1/3 Koch pattern. Expanding defensive ring.
    """
    # Start with equilateral triangle
    pts = []
    for i in range(3):
        theta = -math.pi / 2.0 + i * 2.0 * math.pi / 3.0
        pts.append((radius * math.cos(theta), radius * math.sin(theta)))
    for _ in range(depth):
        new_pts = []
        for i in range(len(pts)):
            p1 = pts[i]
            p2 = pts[(i + 1) % len(pts)]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            a = (p1[0] + dx / 3.0, p1[1] + dy / 3.0)
            b = (p1[0] + 2.0 * dx / 3.0, p1[1] + 2.0 * dy / 3.0)
            # Peak: rotate middle third 60° outward
            mx = (a[0] + b[0]) / 2.0
            my = (a[1] + b[1]) / 2.0
            nx = -(b[1] - a[1]) * math.sqrt(3.0) / 2.0
            ny = (b[0] - a[0]) * math.sqrt(3.0) / 2.0
            peak = (mx + nx, my + ny)
            new_pts.extend([p1, a, peak, b])
        pts = new_pts
    return pts


def _koch_slot(n, slot_index, front_dx, front_dy):
    """Koch snowflake: units along perimeter curve.

    Depth scales with count: <4 → triangle, 4-12 → depth-1, 13+ → depth-2.
    Creates expanding defensive ring around guard point.
    """
    if slot_index == 0:
        return (0.0, 0.0)
    radius = FORMATION_KOCH_RADIUS
    depth = 0
    if n >= 4:
        depth = 1
    if n >= 13:
        depth = 2
    perimeter = _koch_perimeter(depth, radius)
    if not perimeter:
        return (0.0, 0.0)
    # Distribute units evenly along perimeter
    total_slots = max(1, n - 1)
    frac = (slot_index - 1) / total_slots
    point_idx = int(frac * (len(perimeter) - 1))
    point_idx = min(point_idx, len(perimeter) - 1)
    px, py = perimeter[point_idx]
    angle = math.atan2(front_dy, front_dx)
    rx = px * math.cos(angle) - py * math.sin(angle)
    ry = px * math.sin(angle) + py * math.cos(angle)
    return (rx, ry)


def formation_slot(formation_type, squad_size, slot_index, front_dx, front_dy):
    """Dispatch to the right formation calculator.

    Args:
        formation_type: FORMATION_POLAR_ROSE, etc.
        squad_size: total alive members in squad
        slot_index: 0 = leader, 1+ = followers
        front_dx, front_dy: unit vector pointing toward threat/movement
    Returns:
        (x_offset, y_offset) from leader position
    """
    if formation_type == FORMATION_POLAR_ROSE:
        return _polar_rose_slot(squad_size, slot_index, front_dx, front_dy)
    elif formation_type == FORMATION_GOLDEN_SPIRAL:
        return _golden_spiral_slot(squad_size, slot_index, front_dx, front_dy)
    elif formation_type == FORMATION_SIERPINSKI:
        return _sierpinski_slot(squad_size, slot_index, front_dx, front_dy)
    elif formation_type == FORMATION_KOCH:
        return _koch_slot(squad_size, slot_index, front_dx, front_dy)
    return (0.0, 0.0)


# ---------------------------------------------------------------------------
# Squad Class — persistent squad with formation and stance state
# ---------------------------------------------------------------------------

class Squad:
    """A persistent squad with a leader, members, formation, and stance."""
    _next_id = 0

    def __init__(self, leader):
        Squad._next_id += 1
        self.squad_id = Squad._next_id
        self.leader = leader
        self.members = [leader]     # leader always at index 0
        self.formation = FORMATION_POLAR_ROSE
        self.stance = STANCE_AGGRESSIVE
        self.guard_position = None  # (x, y) for Guard stance
        self.guard_entity = None    # Building reference for Guard stance
        self._slot_cache = {}       # member_eid -> slot_index

    def add_member(self, unit):
        if unit not in self.members and len(self.members) < SQUAD_MAX_SIZE:
            self.members.append(unit)
            self._rebuild_slots()
            return True
        return False

    def remove_member(self, unit):
        if unit in self.members:
            self.members.remove(unit)
            if unit is self.leader:
                self._promote_new_leader()
            self._rebuild_slots()

    def _promote_new_leader(self):
        """Highest rank follower becomes leader. Squad dissolves if empty."""
        alive = [m for m in self.members if m.alive]
        if not alive:
            self.leader = None
            return
        alive.sort(key=lambda u: (u.rank, u.xp), reverse=True)
        self.leader = alive[0]
        # Ensure leader is at index 0
        if self.leader in self.members:
            self.members.remove(self.leader)
            self.members.insert(0, self.leader)

    def _rebuild_slots(self):
        """Assign slot indices to alive members."""
        self._slot_cache.clear()
        alive = [m for m in self.members if m.alive]
        for i, m in enumerate(alive):
            self._slot_cache[m.eid] = i
            m._formation_slot_index = i

    def get_slot_index(self, unit):
        return self._slot_cache.get(unit.eid, -1)

    @property
    def alive_count(self):
        return sum(1 for m in self.members if m.alive)

    def prune_dead(self):
        """Remove dead members. Returns True if squad should be dissolved."""
        before = len(self.members)
        self.members = [m for m in self.members if m.alive]
        if not self.members:
            self.leader = None
            return True
        if self.leader and not self.leader.alive:
            self._promote_new_leader()
        if len(self.members) != before:
            self._rebuild_slots()
        return self.leader is None


# ---------------------------------------------------------------------------
# SquadManager — manages persistent squads
# ---------------------------------------------------------------------------

class SquadManager:
    def __init__(self):
        self.squad_list = []        # list of Squad objects
        self._unit_to_squad = {}    # unit_eid -> Squad
        self._maintenance_timer = 0.0

    def update(self, dt, units):
        """Maintenance pass: prune dead, promote leaders, assign orphans."""
        self._maintenance_timer += dt
        if self._maintenance_timer < 1.0:  # check every 1s (was 2s rebuild)
            return
        self._maintenance_timer = 0.0

        # Prune dead members, dissolve empty squads
        dissolved = []
        for squad in self.squad_list:
            if squad.prune_dead():
                dissolved.append(squad)
        for squad in dissolved:
            self.squad_list.remove(squad)
            # Clean up mapping
            for eid in list(self._unit_to_squad):
                if self._unit_to_squad[eid] is squad:
                    del self._unit_to_squad[eid]

        # Promote new leaders: military units reaching rank 1 without a squad
        military = [u for u in units if u.alive and u.unit_type != "worker"
                    and not u.unit_type.startswith("enemy_")]
        for u in military:
            if u.rank >= 1 and u.eid not in self._unit_to_squad:
                # Create new squad with this unit as leader
                squad = Squad(u)
                self.squad_list.append(squad)
                self._unit_to_squad[u.eid] = squad

        # Assign orphan military units to nearest squad with room
        orphans = [u for u in military if u.eid not in self._unit_to_squad]
        for u in orphans:
            best_squad = None
            best_d = 1e9
            for squad in self.squad_list:
                if squad.alive_count >= SQUAD_MAX_SIZE:
                    continue
                if not squad.leader or not squad.leader.alive:
                    continue
                d = dist(u.x, u.y, squad.leader.x, squad.leader.y)
                if d < best_d:
                    best_d = d
                    best_squad = squad
            if best_squad and best_d < SQUAD_FOLLOW_DIST * 4:
                best_squad.add_member(u)
                self._unit_to_squad[u.eid] = best_squad

    def get_squad(self, unit):
        """Return the Squad object for this unit, or None."""
        return self._unit_to_squad.get(unit.eid)

    def get_leader(self, unit):
        """Backward-compatible: return squad leader, or None."""
        squad = self._unit_to_squad.get(unit.eid)
        if squad and squad.leader and squad.leader.alive and squad.leader is not unit:
            return squad.leader
        return None

    def get_followers(self, unit):
        """Backward-compatible: return followers for this leader."""
        squad = self._unit_to_squad.get(unit.eid)
        if squad and squad.leader is unit:
            return [m for m in squad.members if m.alive and m is not unit]
        return []

    def set_formation(self, unit, formation_type):
        """Set formation for the unit's squad."""
        squad = self._unit_to_squad.get(unit.eid)
        if squad:
            squad.formation = formation_type

    def set_stance(self, unit, stance):
        """Set stance for the unit's squad. Also updates all members."""
        squad = self._unit_to_squad.get(unit.eid)
        if squad:
            squad.stance = stance
            for m in squad.members:
                if m.alive:
                    m.stance = stance

    def set_guard_position(self, unit, x, y, entity=None):
        """Set guard position for the unit's squad."""
        squad = self._unit_to_squad.get(unit.eid)
        if squad:
            squad.guard_position = (x, y)
            squad.guard_entity = entity

    def create_squad(self, leader, members=None):
        """Explicitly create a squad (e.g., from control group assignment)."""
        # Remove from existing squads first
        all_units = [leader] + (members or [])
        for u in all_units:
            old_squad = self._unit_to_squad.get(u.eid)
            if old_squad:
                old_squad.remove_member(u)
                if old_squad.leader is None:
                    if old_squad in self.squad_list:
                        self.squad_list.remove(old_squad)

        squad = Squad(leader)
        for m in (members or []):
            squad.add_member(m)
        self.squad_list.append(squad)
        for u in all_units:
            self._unit_to_squad[u.eid] = squad
        return squad

    def remove_unit(self, unit):
        """Remove a unit from its squad entirely."""
        squad = self._unit_to_squad.pop(unit.eid, None)
        if squad:
            squad.remove_member(unit)
            if squad.leader is None and squad in self.squad_list:
                self.squad_list.remove(squad)
