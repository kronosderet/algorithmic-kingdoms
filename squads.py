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
    RESONANCE_ROSE_DMG_PER_PETAL, RESONANCE_KOCH_SLOW_PER_DEPTH,
    RESONANCE_MULTI_SQUAD_PENALTY,
    HARMONY_IDEAL_RATIOS,
    FORMATION_MIN_VIABLE,
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
# v10_8: Resonance Field Calculations (pure math)
# ---------------------------------------------------------------------------

def resonance_polar_rose_bonus(n):
    """Rose resonance: +3% damage per petal. Petals scale with squad size."""
    if n < 2:
        return 0.0
    petals = max(1, int(0.5 + n / 4))
    return petals * RESONANCE_ROSE_DMG_PER_PETAL

def resonance_golden_spiral_miss(n):
    """Spiral resonance: evasion = 1/phi^depth. Depth from Fibonacci thresholds."""
    if n < 2:
        return 0.0
    depth = max(1, int(math.log(max(1, n)) / math.log(_PHI)))
    return 1.0 / (_PHI ** depth)

def resonance_sierpinski_aoe_factor(n):
    """Sierpinski resonance: AOE factor = 1/3^depth. Lower = more reduction."""
    if n < 2:
        return 1.0
    depth = max(1, int(math.log(max(1, n)) / math.log(3)))
    return (1.0 / 3.0) ** depth

def resonance_koch_slow(n):
    """Koch resonance: slow = depth * 15%. Depth from size thresholds."""
    if n < 2:
        return 0.0
    if n <= 3:
        depth = 1
    elif n <= 5:
        depth = 2
    else:
        depth = 3
    return depth * RESONANCE_KOCH_SLOW_PER_DEPTH



# ---------------------------------------------------------------------------
# v10_alpha: Harmonic Resonance — composition quality multiplier
# ---------------------------------------------------------------------------

def get_squad_composition(squad):
    """Return (soldiers, archers) count from alive squad members."""
    soldiers = sum(1 for m in squad.members if m.alive and m.unit_type == "soldier")
    archers = sum(1 for m in squad.members if m.alive and m.unit_type == "archer")
    return soldiers, archers


def compute_harmony(formation, soldiers, archers):
    """Harmony quality (0.3-1.0) from unit composition vs formation's ideal ratio.

    Musical metaphor: two unit types as two tones.
    Monotone (all same) = weak. Matching the fractal's ideal ratio = perfect harmony.
    """
    majority = max(soldiers, archers)
    minority = min(soldiers, archers)
    if majority == 0:
        return 0.3  # empty squad
    if minority == 0:
        return 0.5  # monotone — single note, half power
    actual_ratio = majority / minority
    ideal = HARMONY_IDEAL_RATIOS.get(formation, 1.0)
    deviation = abs(actual_ratio - ideal) / max(ideal, 0.01)
    return max(0.3, 1.0 - deviation * 0.7)


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
        # v10_delta: rotation state
        self.rotation_angle = 0.0
        self.rotation_speed = 0.0
        self.is_rotating = False
        self.sweep_timer = 0.0

    def add_member(self, unit):
        if unit not in self.members and len(self.members) < SQUAD_MAX_SIZE:
            self.members.append(unit)
            self._rebuild_slots()
            return True
        return False

    def remove_member(self, unit):
        """v10_delta: Remove a living unit from the squad (player-initiated)."""
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

    def resonance_effectiveness(self, all_squads):
        """Returns 1.0 - (duplicate_count * 0.30), min 0.1.
        Penalizes having multiple squads with the same formation."""
        duplicates = sum(1 for s in all_squads
                         if s is not self and s.formation == self.formation
                         and s.alive_count > 0)
        return max(0.1, 1.0 - duplicates * RESONANCE_MULTI_SQUAD_PENALTY)


# ---------------------------------------------------------------------------
# SquadManager — manages persistent squads
# ---------------------------------------------------------------------------

class SquadManager:
    def __init__(self):
        self.squad_list = []        # list of Squad objects
        self._unit_to_squad = {}    # unit_eid -> Squad
        self._maintenance_timer = 0.0
        self._resonance_cache = {}  # v10_delta1: init to avoid getattr fallback

    def update(self, dt, units):
        """v10_delta: Player-driven squads — no auto-grouping.

        Only prune dead + dissolve squads below minimum viable count.
        All squad creation/joining is player-initiated.
        """
        self._maintenance_timer += dt
        if self._maintenance_timer < 1.0:
            return []
        self._maintenance_timer = 0.0

        dissolved_notifications = []

        # Prune dead members, dissolve empty/tiny squads
        to_remove = []
        for squad in self.squad_list:
            if squad.prune_dead():
                to_remove.append(squad)
            elif squad.alive_count < FORMATION_MIN_VIABLE:
                to_remove.append(squad)
                dissolved_notifications.append(
                    f"Squad dissolved — only {squad.alive_count} member(s) remain")
        for squad in to_remove:
            self._dissolve_internal(squad)

        return dissolved_notifications

    def is_free(self, unit):
        """Returns True if unit is not in any squad."""
        return unit.eid not in self._unit_to_squad

    def create_squad(self, units, formation=None):
        """Player-initiated: create a new squad from a list of free units.
        Returns the new Squad, or None if invalid."""
        if len(units) < FORMATION_MIN_VIABLE:
            return None
        # Pick highest-rank as leader
        leader = max(units, key=lambda u: (u.rank, -u.eid))
        squad = Squad(leader)
        if formation is not None:
            squad.formation = formation
        self.squad_list.append(squad)
        self._unit_to_squad[leader.eid] = squad
        for u in units:
            if u is not leader:
                squad.add_member(u)
                self._unit_to_squad[u.eid] = squad
        return squad

    def dissolve_squad(self, squad):
        """Player-initiated: dissolve a squad, freeing all members."""
        freed = [m for m in squad.members if m.alive]
        self._dissolve_internal(squad)
        return freed

    def _dissolve_internal(self, squad):
        """Remove squad and clean up mappings."""
        if squad in self.squad_list:
            self.squad_list.remove(squad)
        for eid in list(self._unit_to_squad):
            if self._unit_to_squad[eid] is squad:
                del self._unit_to_squad[eid]

    def reinforce_squad(self, squad, units, force=False):
        """Add units to an existing squad.
        force=True pulls units from other squads first."""
        added = 0
        for u in units:
            if squad.alive_count >= SQUAD_MAX_SIZE:
                break
            if not u.alive or u.unit_type == "worker":
                continue
            if u.eid in self._unit_to_squad:
                if not force:
                    continue  # skip units already in squads
                # Pull from old squad
                old_sq = self._unit_to_squad[u.eid]
                if old_sq is squad:
                    continue
                old_sq.remove_member(u)
                if old_sq.alive_count < FORMATION_MIN_VIABLE:
                    self._dissolve_internal(old_sq)
            squad.add_member(u)
            self._unit_to_squad[u.eid] = squad
            u.stance = squad.stance
            added += 1
        return added

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

    def compute_resonance_cache(self):
        """Pre-compute per-squad resonance (formation_type, effective_value).
        Called once per frame by game._update_resonance().
        v10_alpha: value now includes harmony quality multiplier."""
        _FUNCS = {
            FORMATION_POLAR_ROSE: resonance_polar_rose_bonus,
            FORMATION_GOLDEN_SPIRAL: resonance_golden_spiral_miss,
            FORMATION_SIERPINSKI: resonance_sierpinski_aoe_factor,
            FORMATION_KOCH: resonance_koch_slow,
        }
        cache = {}
        active = [s for s in self.squad_list if s.alive_count > 0]
        for squad in active:
            fn = _FUNCS.get(squad.formation)
            if fn is None:
                continue
            raw = fn(squad.alive_count)
            eff = squad.resonance_effectiveness(active)
            # v10_alpha: harmony quality scales resonance by composition match
            s, a = get_squad_composition(squad)
            harmony = compute_harmony(squad.formation, s, a)
            cache[squad.squad_id] = (squad.formation, raw * eff * harmony, harmony)
        self._resonance_cache = cache
        return cache

    def formation_move(self, squad, wx, wy, game):
        """v10_beta: Move entire squad in formation to destination.

        Leader pathfinds to (wx, wy). Each follower pathfinds to their
        formation-offset slot position around the destination.
        The squad arrives already in formation — no regrouping needed.
        """
        if not squad.leader or not squad.leader.alive:
            return

        # Compute facing direction: from leader's current pos toward destination
        ddx = wx - squad.leader.x
        ddy = wy - squad.leader.y
        dd = math.hypot(ddx, ddy)
        if dd > 1:
            front_x, front_y = ddx / dd, ddy / dd
        else:
            front_x, front_y = 0.0, -1.0

        # Leader moves to the click point
        squad.leader.command_move(wx, wy, game)

        # Each follower moves to their slot position around the destination
        for m in squad.members:
            if m is squad.leader or not m.alive:
                continue
            slot_idx = squad.get_slot_index(m)
            if slot_idx > 0:
                ox, oy = formation_slot(
                    squad.formation, squad.alive_count,
                    slot_idx, front_x, front_y)
                m.command_move(wx + ox, wy + oy, game)
            else:
                m.command_move(wx, wy, game)

    def remove_unit(self, unit):
        """Remove a unit from its squad entirely."""
        squad = self._unit_to_squad.pop(unit.eid, None)
        if squad:
            squad.remove_member(unit)
            if squad.leader is None and squad in self.squad_list:
                self.squad_list.remove(squad)
