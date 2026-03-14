import heapq
import math
from constants import TERRAIN_MOVE_COST

DIAG_COST = math.sqrt(2)


def a_star(sc, sr, ec, er, game_map, blocked_set=None, max_nodes=12000):
    if not game_map.is_passable(ec, er):
        # find nearest passable neighbor to target
        best = None
        best_d = 1e9
        for dc in range(-1, 2):
            for dr in range(-1, 2):
                nc, nr = ec + dc, er + dr
                if game_map.is_passable(nc, nr):
                    d = abs(nc - sc) + abs(nr - sr)
                    if d < best_d:
                        best_d = d
                        best = (nc, nr)
        if best is None:
            return []
        ec, er = best

    if sc == ec and sr == er:
        return [(ec, er)]

    open_set = []
    heapq.heappush(open_set, (0, sc, sr))
    came_from = {}
    g_score = {(sc, sr): 0}
    closed = set()

    while open_set:
        _, cc, cr = heapq.heappop(open_set)
        if (cc, cr) in closed:
            continue
        closed.add((cc, cr))

        if len(closed) > max_nodes:
            break
        if cc == ec and cr == er:
            path = []
            cur = (ec, er)
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path

        for dc in range(-1, 2):
            for dr in range(-1, 2):
                if dc == 0 and dr == 0:
                    continue
                nc, nr = cc + dc, cr + dr
                if not game_map.is_passable(nc, nr):
                    continue
                if blocked_set and (nc, nr) in blocked_set:
                    continue
                # v9.3: weighted terrain cost
                tile_type = game_map.get_tile(nc, nr)
                terrain_mult = TERRAIN_MOVE_COST.get(tile_type, 1.0)
                cost = (DIAG_COST if (dc != 0 and dr != 0) else 1.0) * terrain_mult
                ng = g_score[(cc, cr)] + cost
                if ng < g_score.get((nc, nr), 1e9):
                    g_score[(nc, nr)] = ng
                    h = max(abs(nc - ec), abs(nr - er))
                    heapq.heappush(open_set, (ng + h, nc, nr))
                    came_from[(nc, nr)] = (cc, cr)

    # no path found within node budget
    return []
