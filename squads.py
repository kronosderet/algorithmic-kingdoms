"""
SquadManager — lightweight squad coordination (v9).

Periodically rebuilds squads so rank>=1 leaders command nearby lower-rank
units.  Followers receive cohesion/follow forces from their leader.
"""
from constants import SQUAD_MAX_SIZE, SQUAD_REASSIGN_INTERVAL
from utils import dist


class SquadManager:
    def __init__(self):
        self.squads = {}       # leader_eid -> [follower_units]
        self.leader_of = {}    # unit_eid -> leader_unit
        self.timer = 0.0

    def update(self, dt, units):
        self.timer += dt
        if self.timer < SQUAD_REASSIGN_INTERVAL:
            return
        self.timer = 0.0
        self._rebuild(units)

    def _rebuild(self, units):
        self.squads.clear()
        self.leader_of.clear()

        # filter alive military units (not workers)
        military = [u for u in units if u.alive and u.unit_type != "worker"]
        if not military:
            return

        # sort by rank desc, then xp desc — highest ranks pick first
        military.sort(key=lambda u: (u.rank, u.xp), reverse=True)

        # leaders are units with rank >= 1 (Veteran+)
        leaders = [u for u in military if u.rank >= 1]
        assigned = set()

        for leader in leaders:
            assigned.add(leader.eid)
            self.squads[leader.eid] = []
            self.leader_of[leader.eid] = leader  # leader is their own leader

        # assign followers to nearest leader
        unassigned = [u for u in military if u.eid not in assigned]

        for u in unassigned:
            best_leader = None
            best_d = 1e9
            for leader in leaders:
                if len(self.squads[leader.eid]) >= SQUAD_MAX_SIZE - 1:
                    continue
                d = dist(u.x, u.y, leader.x, leader.y)
                if d < best_d:
                    best_d = d
                    best_leader = leader
            if best_leader:
                self.squads[best_leader.eid].append(u)
                self.leader_of[u.eid] = best_leader
                assigned.add(u.eid)
            # else: no room / no leaders — unit acts independently

    def get_leader(self, unit):
        """Return the squad leader for this unit, or None if unassigned."""
        leader = self.leader_of.get(unit.eid)
        if leader and leader.alive and leader is not unit:
            return leader
        return None

    def get_followers(self, unit):
        """Return list of followers for this leader, or empty list."""
        return [u for u in self.squads.get(unit.eid, []) if u.alive]
