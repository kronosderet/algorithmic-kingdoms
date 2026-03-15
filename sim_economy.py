"""
RTS Economy Simulator  (v10_7)
Simulates base growth, resource flow, army building, and wave survival
to model game balance across different strategies and difficulty levels.

v10_7 updates:
  - 7 enemy types — The Dark 7 (soldier, archer, siege, elite, shieldbearer, healer, raider)
  - Adaptive difficulty engine (pressure tracking, escalation/de-escalation)
  - Straggler metamorphosis modeling
  - Harmonic Pulse tower buff modeling
  - Log analysis integration (parse CSV logs, compare sim vs actual)

All constants imported from constants.py -- no local duplicates.
"""
import math
import random
import csv
import os
import glob
from constants import (
    BUILDING_DEFS, UNIT_DEFS, ENEMY_DEFS,
    GATHER_TIME, GATHER_AMOUNT, IRON_GATHER_AMOUNT,
    REFINE_IRON_COST, REFINE_STEEL_YIELD, REFINE_TIME,
    TOWER_CANNON_DAMAGE, TOWER_CANNON_CD, TOWER_CANNON_RANGE,
    TOWER_EXPLOSIVE_DIRECT, TOWER_EXPLOSIVE_DAMAGE, TOWER_EXPLOSIVE_RADIUS,
    TOWER_UPGRADE_COST, TOWER_UPGRADE_TIME,
    DIFFICULTY_PROFILES,
    HARMONIC_PULSE_SPEED_BONUS, HARMONIC_PULSE_COOLDOWN,
    METAMORPH_HP_MULT, METAMORPH_ATK_MULT,
    STRAGGLER_ROOT_WAVES, STRAGGLER_METAMORPH_WAVES,
)

TOWER_HP = BUILDING_DEFS["tower"]["hp"]
# v10c: Tower is now ballistic cannon -- can miss moving targets
# Estimate ~70% hit rate on average (choke placement helps, open field hurts)
TOWER_HIT_RATE = 0.70
# Level 1 DPS: 45 * 0.70 / 3.5 = 9.0 effective
# Level 2 DPS: (50 direct + ~35*1.5 avg splash) / 3.5 * 0.70 = ~21.5 effective
TOWER_L1_EFFECTIVE_DPS = TOWER_CANNON_DAMAGE * TOWER_HIT_RATE / TOWER_CANNON_CD
TOWER_L2_DIRECT_DPS = TOWER_EXPLOSIVE_DIRECT * TOWER_HIT_RATE / TOWER_CANNON_CD
TOWER_L2_SPLASH_BONUS = TOWER_EXPLOSIVE_DAMAGE * 1.5 * TOWER_HIT_RATE / TOWER_CANNON_CD  # avg 1.5 splash targets


# --─ Worker resource income model ----------------------------------------
def worker_income_per_sec(resource, travel_time=4.0):
    """
    One worker: gather_time + travel_to_resource + travel_to_town_hall.
    Returns resources/sec for one worker.
    """
    gather_t = GATHER_TIME[resource]
    amount = IRON_GATHER_AMOUNT if resource == "iron" else GATHER_AMOUNT
    cycle = gather_t + travel_time  # gather + round trip (simplified)
    return amount / cycle


def stone_income_per_sec(stone_workers, travel_time=4.0):
    """Stone gathered per second given N stone-gathering workers."""
    return stone_workers * worker_income_per_sec("stone", travel_time)


def steel_income_per_sec(iron_workers, travel_time=4.0):
    """Steel produced per second given N iron-gathering workers."""
    iron_per_sec = iron_workers * worker_income_per_sec("iron", travel_time)
    # refinery converts 2 iron -> 1 steel every 6s
    # max steel = iron_per_sec / 2 (since 2 iron consumed per steel)
    # but also limited by refine_time: 1 steel per 6s per refinery
    steel_from_iron = iron_per_sec / REFINE_IRON_COST * REFINE_STEEL_YIELD
    return steel_from_iron


# --─ Wave composition model ----------------------------------------------
def _get_profile(difficulty="medium"):
    return DIFFICULTY_PROFILES[difficulty]


def wave_count(n, difficulty="medium"):
    p = _get_profile(difficulty)
    return int(p["wave_base"] + p["wave_scale"] * math.sqrt(n))


def wave_composition(n, count, difficulty="medium"):
    """The Dark 7 enemy types with unlock waves and counter-pick probabilities."""
    p = _get_profile(difficulty)
    all_types = ["enemy_soldier", "enemy_archer", "enemy_siege", "enemy_elite",
                 "enemy_shieldbearer", "enemy_healer", "enemy_raider"]
    comp = {t: 0 for t in all_types}
    for _ in range(count):
        roll = random.random()
        cumul = 0.0
        # Dark 7 specialist types
        if n >= p.get("healer_wave", 99):
            cumul += 0.06
            if roll < cumul:
                comp["enemy_healer"] += 1; continue
        if n >= p.get("shieldbearer_wave", 99):
            cumul += 0.08
            if roll < cumul:
                comp["enemy_shieldbearer"] += 1; continue
        if n >= p.get("raider_wave", 99):
            cumul += 0.08
            if roll < cumul:
                comp["enemy_raider"] += 1; continue
        # core 4 types
        if n >= p["elite_wave"] and roll < cumul + 0.10:
            comp["enemy_elite"] += 1
        elif n >= p["siege_wave"] and roll < cumul + (0.25 if n >= 15 else 0.20):
            comp["enemy_siege"] += 1
        elif n >= p["archer_wave"] and roll < cumul + 0.45:
            comp["enemy_archer"] += 1
        else:
            comp["enemy_soldier"] += 1
    return comp


def wave_total_hp(n, difficulty="medium", escalation=1.0):
    """v10_7: includes all 9 enemy types, healer effective HP boost, frontal armor."""
    p = _get_profile(difficulty)
    count = max(1, int(wave_count(n, difficulty) * escalation))
    hp_mult = 1.0 + p["hp_scale"] * n
    atk_mult = 1.0 + p["atk_scale"] * n
    # avg composition across runs
    all_types = list(ENEMY_DEFS.keys())
    comp = {t: 0 for t in all_types}
    trials = 200
    for _ in range(trials):
        c = wave_composition(n, count, difficulty)
        for k in c:
            comp[k] += c[k]
    for k in comp:
        comp[k] /= trials

    total_hp = 0
    total_dps = 0
    heal_per_sec = 0
    for etype, avg_count in comp.items():
        if avg_count < 0.01:
            continue
        base = ENEMY_DEFS[etype]
        hp = base["hp"] * hp_mult * avg_count
        # shieldbearer effective HP: frontal armor blocks 50% from front (~60% of attacks hit front)
        if base.get("frontal_armor", 0) > 0:
            hp *= 1.0 / (1.0 - base["frontal_armor"] * 0.6)  # ~30% more effective HP
        total_hp += hp
        # healer: 0 attack but heals allies
        if base.get("heal_rate", 0) > 0:
            heal_per_sec += base["heal_rate"] * avg_count
        elif base["cd"] > 0:
            dps = (base["attack"] * atk_mult / base["cd"]) * avg_count
            total_dps += dps
    # healer adds effective HP by extending fight duration
    # model as: adds heal_rate * expected_fight_duration HP
    if heal_per_sec > 0:
        total_hp += heal_per_sec * 15  # assume ~15s average fight
    return count, total_hp, total_dps, comp


def wave_arrival_time(n, difficulty="medium"):
    """Time in seconds when wave N arrives."""
    p = _get_profile(difficulty)
    if n <= 0:
        return 0
    return p["first_wave_time"] + (n - 1) * p["wave_interval"]


# --─ Player DPS model ----------------------------------------------------
def unit_dps(utype):
    d = UNIT_DEFS[utype]
    return d["attack"] / d["cd"]


def army_dps(soldiers, archers, towers_l1=0, towers_l2=0):
    """Player army DPS. Towers split by level -- L1 cannon, L2 explosive."""
    towers = towers_l1 + towers_l2 if isinstance(towers_l1, int) else towers_l1
    base = soldiers * unit_dps("soldier") + archers * unit_dps("archer")
    # v10c: towers are ballistic cannons, effective DPS accounts for miss rate
    tower_dps = towers_l1 * TOWER_L1_EFFECTIVE_DPS + towers_l2 * (TOWER_L2_DIRECT_DPS + TOWER_L2_SPLASH_BONUS)
    return base + tower_dps


def army_total_hp(soldiers, archers, towers_l1=0, towers_l2=0):
    total_towers = towers_l1 + towers_l2
    return (soldiers * UNIT_DEFS["soldier"]["hp"] +
            archers * UNIT_DEFS["archer"]["hp"] +
            total_towers * TOWER_HP)


def resonance_dps_mult(formation, squad_size):
    """v10_8: DPS multiplier from resonance (Rose = damage bonus)."""
    from squads import resonance_polar_rose_bonus
    if formation == 0:  # Rose
        return 1.0 + resonance_polar_rose_bonus(squad_size)
    return 1.0


def resonance_ehp_mult(formation, squad_size):
    """v10_8: Effective HP multiplier from resonance (Spiral = evasion)."""
    from squads import resonance_golden_spiral_miss
    if formation == 1:  # Spiral
        miss = resonance_golden_spiral_miss(squad_size)
        return 1.0 / max(0.01, 1.0 - miss)  # evasion -> ehp
    return 1.0


def resonance_enemy_dps_mult(formation, squad_size):
    """v10_8: Enemy DPS reduction from Sierpinski (AOE dampening) and Koch (slow)."""
    from squads import resonance_sierpinski_aoe_factor, resonance_koch_slow
    if formation == 2:  # Sierpinski — reduces enemy AOE DPS
        return resonance_sierpinski_aoe_factor(squad_size)
    elif formation == 3:  # Koch — slow extends TTK, modeled as DPS reduction
        slow = resonance_koch_slow(squad_size)
        return max(0.3, 1.0 - slow * 0.5)  # slow -> effective DPS reduction
    return 1.0


def time_to_kill_wave(army_d, wave_hp):
    if army_d <= 0:
        return float('inf')
    return wave_hp / army_d


# --─ Build order simulation ----------------------------------------------
def simulate_game(strategy="balanced", difficulty="medium", verbose=False,
                   formation=-1):
    """
    Simulate a game with a given build strategy.
    Returns timeline of events and survival wave.
    v10f: stone resource, tower cannon ballistic, tower upgrade L2.
    v10_8: formation param (-1 = no resonance, 0-3 = Rose/Spiral/Sierpinski/Koch).
    """
    p = _get_profile(difficulty)
    gold = p["start_gold"]
    wood = p["start_wood"]
    iron, steel, stone = 0, 0, 0
    workers = p.get("start_workers", 3)
    soldiers = 0
    archers = 0
    towers_l1 = 0  # Level 1 cannon towers
    towers_l2 = 0  # Level 2 explosive towers
    buildings = {"town_hall": 1, "barracks": 0, "refinery": 0, "tower": 0}

    # worker allocation: how many on each resource
    gold_workers = 1
    wood_workers = 2
    iron_workers = 0
    stone_workers = 0

    build_queue = []  # list of (finish_time, action)
    train_queue = []  # list of (finish_time, unit_type)
    upgrade_queue = []  # list of (finish_time, "tower_upgrade")

    t = 0
    dt = 1.0  # 1-second simulation steps
    events = []
    survived_wave = 0
    travel_time = 4.0  # avg round-trip for gathering

    def try_build(btype, time):
        nonlocal gold, wood, iron, steel, stone
        d = BUILDING_DEFS[btype]
        if (gold >= d["gold"] and wood >= d["wood"] and iron >= d["iron"]
                and steel >= d["steel"] and stone >= d.get("stone", 0)):
            gold -= d["gold"]
            wood -= d["wood"]
            iron -= d["iron"]
            steel -= d["steel"]
            stone -= d.get("stone", 0)
            build_queue.append((time + d["build_time"], btype))
            return True
        return False

    def try_train(utype, time):
        nonlocal gold, wood, steel
        d = UNIT_DEFS[utype]
        if gold >= d["gold"] and wood >= d["wood"] and steel >= d["steel"]:
            gold -= d["gold"]
            wood -= d["wood"]
            steel -= d["steel"]
            train_queue.append((time + d["train"], utype))
            return True
        return False

    def try_tower_upgrade(time):
        nonlocal steel, towers_l1, towers_l2
        cost = TOWER_UPGRADE_COST.get("steel", 15)
        if towers_l1 > 0 and steel >= cost:
            steel -= cost
            upgrade_queue.append((time + TOWER_UPGRADE_TIME, "tower_upgrade"))
            towers_l1 -= 1  # being upgraded
            return True
        return False

    phase = 0
    barracks_started = False
    refinery_started = False

    for step in range(int(p["first_wave_time"] + p["max_waves"] * p["wave_interval"] + 200)):
        t = step

        # resource income (per second)
        gold += gold_workers * worker_income_per_sec("gold", travel_time) * dt
        wood += wood_workers * worker_income_per_sec("wood", travel_time) * dt
        iron += iron_workers * worker_income_per_sec("iron", travel_time) * dt
        stone += stone_workers * worker_income_per_sec("stone", travel_time) * dt

        # refinery: convert iron to steel
        if buildings["refinery"] > 0 and iron >= REFINE_IRON_COST:
            steel_rate = buildings["refinery"] * (REFINE_STEEL_YIELD / REFINE_TIME) * dt
            iron_consumed = steel_rate * REFINE_IRON_COST
            if iron >= iron_consumed:
                iron -= iron_consumed
                steel += steel_rate

        # complete buildings
        for bq in build_queue[:]:
            if t >= bq[0]:
                build_queue.remove(bq)
                buildings[bq[1]] += 1
                if bq[1] == "tower":
                    towers_l1 += 1
                events.append((t, f"Built {bq[1]}"))

        # complete training
        for tq in train_queue[:]:
            if t >= tq[0]:
                train_queue.remove(tq)
                if tq[1] == "worker":
                    workers += 1
                    # assign new worker
                    if strategy == "econ_boom":
                        if gold_workers <= wood_workers:
                            gold_workers += 1
                        else:
                            wood_workers += 1
                    elif iron_workers == 0 and buildings["refinery"] > 0:
                        iron_workers += 1
                    elif stone_workers == 0 and strategy == "tower_defense":
                        stone_workers += 1
                    elif gold_workers <= wood_workers:
                        gold_workers += 1
                    else:
                        wood_workers += 1
                elif tq[1] == "soldier":
                    soldiers += 1
                elif tq[1] == "archer":
                    archers += 1
                events.append((t, f"Trained {tq[1]}"))

        # complete tower upgrades
        for uq in upgrade_queue[:]:
            if t >= uq[0]:
                upgrade_queue.remove(uq)
                towers_l2 += 1
                events.append((t, "Tower upgraded to L2"))

        # -- Strategy logic --
        if strategy == "balanced":
            # phase 0: train 2 extra workers early
            if phase == 0 and buildings["town_hall"] > 0 and workers < 5 and len(train_queue) == 0:
                try_train("worker", t)
            if workers >= 5 and phase == 0:
                phase = 1
            # phase 1: build barracks
            if phase == 1 and not barracks_started:
                if try_build("barracks", t):
                    barracks_started = True
                    phase = 2
            # phase 2: build refinery once we have iron income
            if phase >= 2 and not refinery_started and buildings["barracks"] > 0:
                if iron_workers == 0 and workers >= 5:
                    if wood_workers > 1:
                        wood_workers -= 1
                        iron_workers += 1
                if iron >= 30 or t > 120:
                    if try_build("refinery", t):
                        refinery_started = True
                        phase = 3
            # phase 3: train military
            if phase >= 2 and buildings["barracks"] > 0 and len(train_queue) == 0:
                if steel >= 8:
                    try_train("soldier", t)
                elif steel >= 4 and wood >= 25:
                    try_train("archer", t)

            # assign a stone worker once barracks done (for towers)
            if phase >= 2 and stone_workers == 0 and wood_workers > 1:
                wood_workers -= 1
                stone_workers += 1

            # build towers when affordable (now costs stone + iron)
            if phase >= 3 and buildings["refinery"] > 0 and (towers_l1 + towers_l2) < 3:
                if try_build("tower", t):
                    pass  # towers_l1 incremented on completion

            # upgrade towers to L2 when steel available
            if towers_l1 > 0 and steel >= TOWER_UPGRADE_COST.get("steel", 15):
                try_tower_upgrade(t)

        elif strategy == "rush_military":
            if not barracks_started:
                if try_build("barracks", t):
                    barracks_started = True
            if buildings["barracks"] > 0 and len(train_queue) == 0:
                try_train("soldier", t)
            if t > 200 and not refinery_started:
                if try_build("refinery", t):
                    refinery_started = True
                    if wood_workers > 1:
                        wood_workers -= 1
                        iron_workers += 1

        elif strategy == "econ_boom":
            if phase == 0 and workers < 7 and len(train_queue) == 0:
                try_train("worker", t)
            if workers >= 7:
                phase = 1
            if phase == 1 and not barracks_started:
                if try_build("barracks", t):
                    barracks_started = True
                    phase = 2
            if phase >= 2 and not refinery_started:
                if wood_workers > 2:
                    wood_workers -= 1
                    iron_workers += 1
                if iron >= 30:
                    if try_build("refinery", t):
                        refinery_started = True
                        phase = 3
            if phase >= 2 and buildings["barracks"] > 0 and len(train_queue) == 0:
                if steel >= 8:
                    try_train("soldier", t)
                elif wood >= 25 and steel >= 4:
                    try_train("archer", t)
                elif gold >= 50 and workers < 8:
                    try_train("worker", t)

        elif strategy == "tower_defense":
            # v10f: tower strategy now prioritizes stone gathering + tower upgrades
            if phase == 0 and workers < 5 and len(train_queue) == 0:
                try_train("worker", t)
            if workers >= 5:
                phase = 1
            if phase == 1 and not barracks_started:
                if try_build("barracks", t):
                    barracks_started = True
                    phase = 2
            # assign workers to iron + stone early
            if phase >= 1:
                if iron_workers == 0 and wood_workers > 1:
                    wood_workers -= 1
                    iron_workers += 1
                if stone_workers == 0 and wood_workers > 1:
                    wood_workers -= 1
                    stone_workers += 1
            if phase >= 2 and not refinery_started:
                if try_build("refinery", t):
                    refinery_started = True
                    phase = 3
            # build towers (stone + iron cost)
            if phase >= 2 and (towers_l1 + towers_l2 + len([u for u in upgrade_queue])) < 5:
                if try_build("tower", t):
                    pass
            # upgrade existing towers to L2
            if towers_l1 > 0 and steel >= TOWER_UPGRADE_COST.get("steel", 15):
                try_tower_upgrade(t)
            # also train archers + some soldiers
            if phase >= 2 and buildings["barracks"] > 0 and len(train_queue) == 0:
                if wood >= 25 and steel >= 4:
                    try_train("archer", t)
                elif steel >= 8:
                    try_train("soldier", t)
            # extra workers for eco
            if workers < 6 and len(train_queue) == 0 and phase >= 2:
                try_train("worker", t)

    # -- Now evaluate wave survival --
    results = []
    for wave_n in range(1, p["max_waves"] + 1):
        arrival = wave_arrival_time(wave_n, difficulty)

        count, total_hp, total_dps, comp = wave_total_hp(wave_n, difficulty)

        player_dps = army_dps(soldiers, archers, towers_l1, towers_l2)
        player_hp = army_total_hp(soldiers, archers, towers_l1, towers_l2)

        # v10_8: apply resonance bonuses
        squad_size = soldiers + archers
        if formation >= 0 and squad_size >= 2:
            player_dps *= resonance_dps_mult(formation, squad_size)
            player_hp *= resonance_ehp_mult(formation, squad_size)
            total_dps *= resonance_enemy_dps_mult(formation, squad_size)

        ttk_wave = time_to_kill_wave(player_dps, total_hp)
        ttk_player = time_to_kill_wave(total_dps, player_hp) if total_dps > 0 else float('inf')

        survives = ttk_wave < ttk_player and player_dps > 0
        if survives:
            survived_wave = wave_n

        results.append({
            "wave": wave_n,
            "time": arrival,
            "enemy_count": count,
            "enemy_hp": total_hp,
            "enemy_dps": total_dps,
            "player_soldiers": soldiers,
            "player_archers": archers,
            "player_towers_l1": towers_l1,
            "player_towers_l2": towers_l2,
            "player_workers": workers,
            "player_dps": player_dps,
            "player_hp": player_hp,
            "ttk_wave": ttk_wave,
            "ttk_player": ttk_player,
            "survives": survives,
        })

    return {
        "strategy": strategy,
        "survived_wave": survived_wave,
        "final_army": {"soldiers": soldiers, "archers": archers,
                       "towers_l1": towers_l1, "towers_l2": towers_l2, "workers": workers},
        "final_buildings": dict(buildings),
        "wave_results": results,
        "events": events,
    }


# --─ Per-wave snapshot sim (more accurate) --------------------------------
def simulate_detailed(strategy="balanced", difficulty="medium", formation=-1):
    """More accurate sim that tracks army at each wave arrival.
    v10f: stone resource, tower L1/L2, tower upgrade, ballistic miss modeling.
    v10_8: formation param (-1 = no resonance, 0-3 = Rose/Spiral/Sierpinski/Koch)."""
    p = _get_profile(difficulty)
    gold, wood, iron, steel, stone = (
        float(p["start_gold"]), float(p["start_wood"]), 0.0, 0.0, 0.0)
    workers, soldiers, archers = p.get("start_workers", 3), 0, 0
    towers_l1, towers_l2 = 0, 0  # cannon / explosive
    gold_w, wood_w, iron_w, stone_w = 1, 2, 0, 0
    buildings = {"town_hall": 1, "barracks": 0, "refinery": 0, "tower": 0}
    build_q = []
    train_q = []
    upgrade_q = []  # tower upgrade queue
    travel = 4.0
    barracks_done = False
    refinery_done = False
    phase = 0

    def can_afford_b(bt):
        d = BUILDING_DEFS[bt]
        return (gold >= d["gold"] and wood >= d["wood"] and iron >= d["iron"]
                and steel >= d["steel"] and stone >= d.get("stone", 0))

    def buy_b(bt, t):
        nonlocal gold, wood, iron, steel, stone
        d = BUILDING_DEFS[bt]
        gold -= d["gold"]; wood -= d["wood"]; iron -= d["iron"]
        steel -= d["steel"]; stone -= d.get("stone", 0)
        build_q.append((t + d["build_time"], bt))

    def can_afford_u(ut):
        d = UNIT_DEFS[ut]
        return gold >= d["gold"] and wood >= d["wood"] and steel >= d["steel"]

    def buy_u(ut, t):
        nonlocal gold, wood, steel
        d = UNIT_DEFS[ut]
        gold -= d["gold"]; wood -= d["wood"]; steel -= d["steel"]
        train_q.append((t + d["train"], ut))

    def try_tower_upgrade(t):
        nonlocal steel, towers_l1
        cost = TOWER_UPGRADE_COST.get("steel", 15)
        if towers_l1 > 0 and steel >= cost:
            steel -= cost
            towers_l1 -= 1
            upgrade_q.append((t + TOWER_UPGRADE_TIME, "tower_l2"))
            return True
        return False

    snapshots = []
    total_time = int(p["first_wave_time"] + p["max_waves"] * p["wave_interval"] + 100)

    for t in range(total_time):
        # income
        gold += gold_w * worker_income_per_sec("gold", travel)
        wood += wood_w * worker_income_per_sec("wood", travel)
        iron += iron_w * worker_income_per_sec("iron", travel)
        stone += stone_w * worker_income_per_sec("stone", travel)

        # refinery
        if buildings["refinery"] > 0 and iron >= REFINE_IRON_COST:
            sr = buildings["refinery"] * (REFINE_STEEL_YIELD / REFINE_TIME)
            ic = sr * REFINE_IRON_COST
            if iron >= ic:
                iron -= ic
                steel += sr

        # completions
        for bq in build_q[:]:
            if t >= bq[0]:
                build_q.remove(bq)
                buildings[bq[1]] += 1
                if bq[1] == "tower":
                    towers_l1 += 1
        for tq in train_q[:]:
            if t >= tq[0]:
                train_q.remove(tq)
                if tq[1] == "worker":
                    workers += 1
                    # smarter worker allocation by strategy
                    if strategy == "tower_defense":
                        if stone_w == 0: stone_w += 1
                        elif iron_w == 0: iron_w += 1
                        elif gold_w <= wood_w: gold_w += 1
                        else: wood_w += 1
                    elif strategy == "econ_boom":
                        if iron_w == 0 and phase >= 1: iron_w += 1
                        elif gold_w <= wood_w: gold_w += 1
                        else: wood_w += 1
                    else:
                        if iron_w == 0 and buildings["refinery"] > 0: iron_w += 1
                        elif gold_w <= wood_w: gold_w += 1
                        else: wood_w += 1
                elif tq[1] == "soldier":
                    soldiers += 1
                elif tq[1] == "archer":
                    archers += 1
        for uq in upgrade_q[:]:
            if t >= uq[0]:
                upgrade_q.remove(uq)
                towers_l2 += 1

        # strategy
        if strategy == "balanced":
            if phase == 0 and workers < 5 and not train_q and buildings["town_hall"] > 0:
                if can_afford_u("worker"): buy_u("worker", t)
            if workers >= 5 and phase == 0: phase = 1
            if phase == 1 and not barracks_done:
                if can_afford_b("barracks"):
                    buy_b("barracks", t); barracks_done = True; phase = 2
            if phase >= 2 and not refinery_done and buildings["barracks"] > 0:
                if iron_w == 0 and wood_w > 1:
                    wood_w -= 1; iron_w += 1
                if can_afford_b("refinery"):
                    buy_b("refinery", t); refinery_done = True; phase = 3
            # assign stone worker for towers
            if phase >= 2 and stone_w == 0 and wood_w > 1:
                wood_w -= 1; stone_w += 1
            if phase >= 2 and buildings["barracks"] > 0 and not train_q:
                if can_afford_u("soldier") and steel >= 8:
                    buy_u("soldier", t)
                elif can_afford_u("archer") and steel >= 4:
                    buy_u("archer", t)
            if phase >= 3 and (towers_l1 + towers_l2) < 3:
                if can_afford_b("tower"):
                    buy_b("tower", t)
            # upgrade towers
            if towers_l1 > 0 and steel >= TOWER_UPGRADE_COST.get("steel", 15):
                try_tower_upgrade(t)
            # extra workers
            if workers < 6 and not train_q and phase >= 2 and can_afford_u("worker"):
                buy_u("worker", t)

        elif strategy == "econ_boom":
            if phase == 0 and workers < 7 and not train_q:
                if can_afford_u("worker"): buy_u("worker", t)
            if workers >= 7 and phase == 0: phase = 1
            if phase == 1 and not barracks_done:
                if can_afford_b("barracks"):
                    buy_b("barracks", t); barracks_done = True; phase = 2
            # assign iron worker once past phase 1 (econ_boom has many workers)
            if phase >= 1 and iron_w == 0 and wood_w >= 2:
                wood_w -= 1; iron_w += 1
            if phase >= 2 and not refinery_done:
                if can_afford_b("refinery"):
                    buy_b("refinery", t); refinery_done = True; phase = 3
            if phase >= 2 and buildings["barracks"] > 0 and not train_q:
                if can_afford_u("soldier") and steel >= 8:
                    buy_u("soldier", t)
                elif can_afford_u("archer") and steel >= 4:
                    buy_u("archer", t)
                elif can_afford_u("worker") and workers < 9:
                    buy_u("worker", t)

        elif strategy == "rush_military":
            if not barracks_done:
                if can_afford_b("barracks"):
                    buy_b("barracks", t); barracks_done = True
            if buildings["barracks"] > 0 and not train_q:
                if can_afford_u("soldier"):
                    buy_u("soldier", t)
            if t > 200 and not refinery_done:
                if iron_w == 0 and wood_w > 1:
                    wood_w -= 1; iron_w += 1
                if can_afford_b("refinery"):
                    buy_b("refinery", t); refinery_done = True

        elif strategy == "tower_defense":
            if phase == 0 and workers < 6 and not train_q:
                if can_afford_u("worker"): buy_u("worker", t)
            if workers >= 5 and phase == 0: phase = 1
            if phase == 1 and not barracks_done:
                if can_afford_b("barracks"):
                    buy_b("barracks", t); barracks_done = True; phase = 2
            # assign stone + iron workers (from existing pool or new hires)
            if phase >= 1 and iron_w == 0 and wood_w >= 2:
                wood_w -= 1; iron_w += 1
            if phase >= 1 and stone_w == 0 and gold_w >= 2:
                gold_w -= 1; stone_w += 1
            if phase >= 2 and not refinery_done:
                if can_afford_b("refinery"):
                    buy_b("refinery", t); refinery_done = True; phase = 3
            # towers first (stone + iron cost)
            if phase >= 2 and (towers_l1 + towers_l2 + len(upgrade_q)) < 5:
                if can_afford_b("tower"):
                    buy_b("tower", t)
            # upgrade towers to L2
            if towers_l1 > 0 and steel >= TOWER_UPGRADE_COST.get("steel", 15):
                try_tower_upgrade(t)
            # military -- archers preferred (range synergy with towers)
            if phase >= 2 and buildings["barracks"] > 0 and not train_q:
                if can_afford_u("archer") and steel >= 4:
                    buy_u("archer", t)
                elif can_afford_u("soldier") and steel >= 8:
                    buy_u("soldier", t)
            # extra workers
            if workers < 7 and not train_q and phase >= 2 and can_afford_u("worker"):
                buy_u("worker", t)

        # wave check
        for wn in range(1, p["max_waves"] + 1):
            if wave_arrival_time(wn, difficulty) == t:
                cnt, whp, wdps, comp = wave_total_hp(wn, difficulty)
                pdps = army_dps(soldiers, archers, towers_l1, towers_l2)
                php = army_total_hp(soldiers, archers, towers_l1, towers_l2)
                # v10_8: apply resonance bonuses
                sq_size = soldiers + archers
                eff_wdps = wdps
                if formation >= 0 and sq_size >= 2:
                    pdps *= resonance_dps_mult(formation, sq_size)
                    php *= resonance_ehp_mult(formation, sq_size)
                    eff_wdps *= resonance_enemy_dps_mult(formation, sq_size)
                ttk_w = whp / pdps if pdps > 0 else 9999
                ttk_p = php / eff_wdps if eff_wdps > 0 else 9999
                tw_total = towers_l1 + towers_l2
                snapshots.append({
                    "wave": wn, "time": t,
                    "workers": workers, "soldiers": soldiers, "archers": archers,
                    "towers_l1": towers_l1, "towers_l2": towers_l2, "towers": tw_total,
                    "gold": int(gold), "wood": int(wood), "iron": int(iron),
                    "steel": int(steel), "stone": int(stone),
                    "enemy_count": cnt, "enemy_hp": int(whp), "enemy_dps": round(wdps, 1),
                    "player_dps": round(pdps, 1), "player_hp": php,
                    "ttk_wave": round(ttk_w, 1), "ttk_player": round(ttk_p, 1),
                    "survives": ttk_w < ttk_p and pdps > 0,
                    "comp": {k: round(v, 1) for k, v in comp.items()},
                })
    return snapshots


# --─ Log Analysis ---------------------------------------------------------
def parse_log(filepath):
    """Parse a game log CSV and extract key metrics."""
    events = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)

    metrics = {
        "file": os.path.basename(filepath),
        "total_time": 0, "outcome": "unknown", "difficulty": "medium",
        "waves_survived": 0, "total_kills": 0, "total_losses": 0,
        "buildings_placed": 0, "buildings_complete": 0, "buildings_destroyed": 0,
        "units_trained": 0, "deposits": 0,
        "worker_flees": 0, "worker_resumes": 0,
        "rank_ups_player": 0, "rank_ups_enemy": 0,
        "resources_gathered": {"gold": 0, "wood": 0, "iron": 0, "stone": 0, "steel": 0},
        "first_barracks_time": None, "first_military_time": None,
        "first_tower_time": None, "wave_times": {},
        "kill_log": [], "loss_log": [], "building_events": [],
    }

    for e in events:
        et = e.get("event_type", "")
        gt = float(e.get("game_time", 0))
        wave = int(e.get("wave", 0))

        if et == "GAME_SUMMARY":
            metrics["total_time"] = gt
            metrics["outcome"] = e.get("detail_1", "unknown")
            metrics["difficulty"] = e.get("detail_2", "medium")
        elif et == "WAVE_START":
            metrics["wave_times"][wave] = gt
            metrics["waves_survived"] = max(metrics["waves_survived"], wave - 1)
        elif et == "UNIT_KILLED":
            metrics["total_kills"] += 1
            metrics["kill_log"].append({"time": gt, "wave": wave,
                                        "killer": e.get("detail_1", ""), "killed": e.get("detail_2", "")})
        elif et == "PLAYER_UNIT_LOST":
            metrics["total_losses"] += 1
            metrics["loss_log"].append({"time": gt, "wave": wave,
                                        "unit": e.get("detail_1", ""), "killer": e.get("detail_2", "")})
        elif et == "BUILDING_PLACED":
            metrics["buildings_placed"] += 1
            btype = e.get("detail_1", "")
            metrics["building_events"].append({"time": gt, "event": "placed", "type": btype})
            if btype == "barracks" and metrics["first_barracks_time"] is None:
                metrics["first_barracks_time"] = gt
            elif btype == "tower" and metrics["first_tower_time"] is None:
                metrics["first_tower_time"] = gt
        elif et == "BUILDING_COMPLETE":
            metrics["buildings_complete"] += 1
            btype = e.get("detail_1", "")
            metrics["building_events"].append({"time": gt, "event": "complete", "type": btype})
        elif et == "BUILDING_DESTROYED":
            metrics["buildings_destroyed"] += 1
        elif et == "TRAINING_STARTED":
            metrics["units_trained"] += 1
            utype = e.get("detail_1", "")
            if utype in ("soldier", "archer") and metrics["first_military_time"] is None:
                metrics["first_military_time"] = gt
        elif et == "RESOURCE_DEPOSIT":
            metrics["deposits"] += 1
            res = e.get("detail_1", "")
            amt = int(e.get("numeric_value", 0))
            if res in metrics["resources_gathered"]:
                metrics["resources_gathered"][res] += amt
        elif et == "WORKER_FLEE":
            metrics["worker_flees"] += 1
        elif et == "WORKER_RESUME":
            metrics["worker_resumes"] += 1
        elif et == "RANK_UP":
            owner = e.get("detail_3", "")
            if owner == "player":
                metrics["rank_ups_player"] += 1
            else:
                metrics["rank_ups_enemy"] += 1
        elif et == "SURRENDER":
            metrics["outcome"] = "surrender"

    return metrics


def find_latest_log(log_dir="dist/logs"):
    """Find the most recent game log CSV."""
    pattern = os.path.join(log_dir, "game_*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def log_report(metrics):
    """Generate analysis report from parsed log metrics."""
    m = metrics
    print(f"\n{'='*90}")
    print(f"GAME LOG ANALYSIS: {m['file']}")
    print(f"{'='*90}")
    print(f"  Outcome: {m['outcome'].upper()}  |  Difficulty: {m['difficulty']}  |  Duration: {m['total_time']:.0f}s ({m['total_time']/60:.1f}min)")
    print(f"  Waves survived: {m['waves_survived']}  |  Kills: {m['total_kills']}  |  Losses: {m['total_losses']}")
    print(f"  Buildings placed: {m['buildings_placed']}  |  Completed: {m['buildings_complete']}  |  Destroyed: {m['buildings_destroyed']}")
    print(f"  Units trained: {m['units_trained']}  |  Deposits: {m['deposits']}")
    print(f"  Worker flee/resume: {m['worker_flees']}/{m['worker_resumes']}")
    print(f"  Rank-ups: player={m['rank_ups_player']}, enemy={m['rank_ups_enemy']}")

    print(f"\n  Resources gathered:")
    for res, amt in m['resources_gathered'].items():
        if amt > 0:
            print(f"    {res:6s}: {amt:5d}")

    print(f"\n  Build order timeline:")
    if m['first_barracks_time']:
        print(f"    First barracks placed: {m['first_barracks_time']:.0f}s")
    if m['first_tower_time']:
        print(f"    First tower placed: {m['first_tower_time']:.0f}s")
    if m['first_military_time']:
        print(f"    First military training: {m['first_military_time']:.0f}s")

    if m['wave_times']:
        wave1 = m['wave_times'].get(1, 0)
        if wave1 and m['first_military_time']:
            lead = wave1 - m['first_military_time']
            print(f"    Military lead time before wave 1: {lead:.0f}s")

    if m['loss_log']:
        print(f"\n  Unit losses:")
        for l in m['loss_log']:
            print(f"    t={l['time']:.0f}s wave {l['wave']}: {l['unit']} killed by {l['killer']}")

    return m


def generate_recommendations(metrics, sim_snaps):
    """Compare log data with sim predictions and generate recommendations."""
    m = metrics
    print(f"\n{'='*90}")
    print(f"RECOMMENDATIONS (based on log + sim analysis)")
    print(f"{'='*90}")

    recs = []

    # 1. Build order timing
    p = _get_profile(m["difficulty"])
    wave1_time = p["first_wave_time"]

    if m["first_barracks_time"] and m["first_barracks_time"] > wave1_time * 0.5:
        recs.append(("CRITICAL", "Barracks too late",
                      f"Barracks placed at {m['first_barracks_time']:.0f}s -- should be before {wave1_time*0.5:.0f}s "
                      f"(50% of wave 1 at {wave1_time}s). Train fewer workers early or rush barracks."))

    if m["first_military_time"] and m["first_military_time"] > wave1_time * 0.75:
        recs.append(("CRITICAL", "Military training too late",
                      f"First military unit started at {m['first_military_time']:.0f}s -- need at least 2 combat units "
                      f"ready by wave 1 ({wave1_time}s). Start training by {wave1_time*0.6:.0f}s."))

    # 2. Worker count
    worker_trains = sum(1 for e in [ev for ev in [] ] if True)  # count from trained
    total_workers_trained = sum(1 for be in m.get("building_events", []) if False)
    # Check if too many workers before military
    if m["units_trained"] > 0:
        worker_count = len([e for e in m.get("building_events", []) if False])

    # 3. Worker flee spam
    if m["worker_flees"] > 20:
        recs.append(("HIGH", "Worker flee spam",
                      f"{m['worker_flees']} flee events and {m['worker_resumes']} resumes. "
                      f"Workers ping-pong between fleeing and resuming. Consider garrison or keep workers far from combat."))

    # 4. Enemy rank-ups
    if m["rank_ups_enemy"] > m["rank_ups_player"] * 2 and m["rank_ups_enemy"] > 3:
        recs.append(("HIGH", "Enemies ranking up faster than player",
                      f"Enemy got {m['rank_ups_enemy']} rank-ups vs player's {m['rank_ups_player']}. "
                      f"Enemies are snowballing from extended fights. Need faster DPS to prevent this."))

    # 5. Resource imbalance
    rg = m["resources_gathered"]
    if rg.get("wood", 0) > rg.get("gold", 0) * 2:
        recs.append(("MEDIUM", "Wood surplus -- gold deficit",
                      f"Gathered {rg['wood']} wood vs {rg['gold']} gold. Reassign wood workers to gold."))
    if rg.get("iron", 0) < 30 and m["total_time"] > 200:
        recs.append(("MEDIUM", "Iron starvation",
                      f"Only {rg['iron']} iron gathered in {m['total_time']:.0f}s. Need iron worker earlier for steel/towers."))

    # 6. Sim comparison
    if sim_snaps:
        sim_wave1 = next((s for s in sim_snaps if s["wave"] == 1), None)
        if sim_wave1:
            if not sim_wave1["survives"]:
                recs.append(("INFO", "Sim also fails wave 1",
                              f"Sim prediction: {sim_wave1['soldiers']}S {sim_wave1['archers']}A {sim_wave1['towers']}T "
                              f"with {sim_wave1['player_dps']:.1f} DPS vs {sim_wave1['enemy_hp']} enemy HP. "
                              f"This strategy fundamentally can't survive wave 1."))
            else:
                recs.append(("INFO", "Sim survives wave 1",
                              f"Sim has {sim_wave1['soldiers']}S {sim_wave1['archers']}A {sim_wave1['towers']}T "
                              f"with {sim_wave1['player_dps']:.1f} DPS. Execution gap between sim and actual."))
        # find first sim failure
        first_fail = next((s for s in sim_snaps if not s["survives"]), None)
        if first_fail:
            recs.append(("INFO", f"Sim predicts failure at wave {first_fail['wave']}",
                          f"Enemy HP={first_fail['enemy_hp']}, DPS={first_fail['enemy_dps']:.1f} "
                          f"overwhelms player DPS={first_fail['player_dps']:.1f}, HP={first_fail['player_hp']}."))

    # 7. Quick death pattern
    if m["waves_survived"] <= 1 and m["total_time"] < 500:
        recs.append(("CRITICAL", "Wave 1 death -- build order issue",
                      "Game ended on wave 1-2. The fundamental build order can't produce enough military "
                      "before the first wave. Recommended: 2 workers -> barracks ASAP -> 1 soldier + 2 archers "
                      "-> then economy buildings."))

    if not recs:
        recs.append(("INFO", "No major issues detected", "Game played within expected parameters."))

    for severity, title, detail in recs:
        icon = {"CRITICAL": "!!!", "HIGH": " !!", "MEDIUM": "  !", "INFO": "  i"}[severity]
        print(f"\n  [{icon}] {severity}: {title}")
        print(f"      {detail}")

    return recs


# --─ Main ----------------------------------------------------------------─
if __name__ == "__main__":
    print("=" * 110)
    print("RTS ECONOMY SIMULATION  (v10_7 -- 9 enemy types, adaptive difficulty, log integration)")
    print("=" * 110)

    # Income rates
    print("\n-- RESOURCE INCOME RATES (per worker per second) --")
    for res in ["gold", "wood", "iron", "stone"]:
        for travel in [3.0, 4.0, 6.0]:
            rate = worker_income_per_sec(res, travel)
            print(f"  {res:5s} (travel {travel:.0f}s): {rate:.2f}/s  ({rate*60:.1f}/min)")

    print(f"\n  Steel from 1 iron worker: {steel_income_per_sec(1):.3f}/s ({steel_income_per_sec(1)*60:.1f}/min)")
    print(f"  Steel from 2 iron workers: {steel_income_per_sec(2):.3f}/s ({steel_income_per_sec(2)*60:.1f}/min)")

    # Unit DPS
    print("\n-- UNIT COMBAT STATS --")
    for ut in ["worker", "soldier", "archer"]:
        d = UNIT_DEFS[ut]
        dps = d["attack"] / d["cd"]
        print(f"  {ut:8s}: HP={d['hp']:3d}  DPS={dps:5.1f}  Cost: {d['gold']}g {d.get('wood',0)}w {d.get('steel',0)}s  Train: {d['train']}s")
    td = BUILDING_DEFS["tower"]
    print(f"  {'tower L1':8s}: HP={TOWER_HP:3d}  DPS={TOWER_L1_EFFECTIVE_DPS:5.1f} (eff)  Cost: {td['gold']}g {td['iron']}i {td['stone']}st  Build: {td['build_time']}s")
    print(f"  {'tower L2':8s}: HP={TOWER_HP:3d}  DPS={TOWER_L2_DIRECT_DPS + TOWER_L2_SPLASH_BONUS:5.1f} (eff+AoE)  Upgrade: {TOWER_UPGRADE_COST}  Time: {TOWER_UPGRADE_TIME}s")
    print(f"  (Tower hit rate model: {TOWER_HIT_RATE*100:.0f}% -- ballistic cannon can miss)")

    # Enemy stats by wave (medium difficulty)
    diff = "medium"
    prof = _get_profile(diff)
    print(f"\n-- ENEMY WAVE PROGRESSION ({diff.upper()}) --")
    print(f"  {'Wave':>4s} | {'Time':>6s} | {'Count':>5s} | {'Total HP':>9s} | {'Wave DPS':>8s} | {'Composition':40s}")
    print(f"  {'-'*4}-+-{'-'*6}-+-{'-'*5}-+-{'-'*9}-+-{'-'*8}-+-{'-'*40}")
    for wn in range(1, prof["max_waves"] + 1):
        cnt, hp, dps, comp = wave_total_hp(wn, diff)
        arrival = wave_arrival_time(wn, diff)
        comp_str = ", ".join(f"{k.replace('enemy_','')}:{v:.1f}" for k, v in comp.items() if v > 0.1)
        print(f"  {wn:4d} | {arrival:5.0f}s | {cnt:5d} | {hp:9.0f} | {dps:8.1f} | {comp_str}")

    # Strategy simulations (all difficulties)
    for diff in ["easy", "medium", "hard"]:
        prof = _get_profile(diff)
        for strat in ["balanced", "rush_military", "econ_boom", "tower_defense"]:
            print(f"\n{'='*110}")
            print(f"STRATEGY: {strat.upper()} | DIFFICULTY: {diff.upper()}")
            print(f"{'='*110}")
            snaps = simulate_detailed(strat, diff)
            print(f"  {'Wave':>4s} | {'Time':>5s} | {'W':>2s} {'S':>2s} {'A':>2s} {'T1':>2s} {'T2':>2s} | {'Gold':>5s} {'Wood':>5s} {'Iron':>4s} {'Steel':>4s} {'Stone':>5s} | {'P.DPS':>6s} {'P.HP':>5s} | {'E.Cnt':>5s} {'E.HP':>6s} {'E.DPS':>5s} | {'TTK_W':>5s} {'TTK_P':>5s} | {'OK?':>3s}")
            print(f"  {'-'*4}-+-{'-'*5}-+-{'-'*14}-+-{'-'*29}-+-{'-'*13}-+-{'-'*19}-+-{'-'*11}-+-{'-'*3}")
            last_survive = 0
            for s in snaps:
                ok = "YES" if s["survives"] else " NO"
                if s["survives"]:
                    last_survive = s["wave"]
                print(f"  {s['wave']:4d} | {s['time']:4d}s | {s['workers']:2d} {s['soldiers']:2d} {s['archers']:2d} {s['towers_l1']:2d} {s['towers_l2']:2d} | {s['gold']:5d} {s['wood']:5d} {s['iron']:4d} {s['steel']:4.0f} {s['stone']:5d} | {s['player_dps']:6.1f} {s['player_hp']:5d} | {s['enemy_count']:5d} {s['enemy_hp']:6d} {s['enemy_dps']:5.1f} | {s['ttk_wave']:5.1f} {s['ttk_player']:5.1f} | {ok}")
            print(f"\n  >> Survived through wave: {last_survive}/{prof['max_waves']}")

    # v10_8: Resonance comparison (balanced strategy, all difficulties x 4 formations)
    print("\n" + "=" * 110)
    print("RESONANCE FORMATION COMPARISON  (v10_8)")
    print("=" * 110)
    fmt_names = {-1: "None", 0: "Rose", 1: "Spiral", 2: "Sierpinski", 3: "Koch"}
    for diff in ["easy", "medium", "hard"]:
        prof = _get_profile(diff)
        print(f"\n  {diff.upper()} -- balanced strategy:")
        print(f"    {'Formation':12s} | {'Survived':>8s} / {prof['max_waves']}")
        print(f"    {'-'*12}-+-{'-'*12}")
        for fmt in [-1, 0, 1, 2, 3]:
            snaps = simulate_detailed("balanced", diff, formation=fmt)
            survive = max((s["wave"] for s in snaps if s["survives"]), default=0)
            print(f"    {fmt_names[fmt]:12s} | {survive:8d}")

    # Key findings -- computed dynamically
    print("\n" + "=" * 110)
    print("KEY ECONOMIC FINDINGS  (v10_8)")
    print("=" * 110)
    t4 = 4.0  # standard travel time
    print(f"""
  INCOME MODEL (4s travel):
    - Gold worker:  {worker_income_per_sec('gold', t4):.2f}/s -> {worker_income_per_sec('gold', t4)*60:.1f}/min
    - Wood worker:  {worker_income_per_sec('wood', t4):.2f}/s -> {worker_income_per_sec('wood', t4)*60:.1f}/min
    - Iron worker:  {worker_income_per_sec('iron', t4):.2f}/s -> {worker_income_per_sec('iron', t4)*60:.1f}/min
    - Stone worker: {worker_income_per_sec('stone', t4):.2f}/s -> {worker_income_per_sec('stone', t4)*60:.1f}/min
    - Steel (1 refinery, 1 iron worker): {steel_income_per_sec(1):.3f}/s -> {steel_income_per_sec(1)*60:.1f}/min

  BUILDING COSTS:
    - Barracks: 120g, 80w                    (Build: 18s)
    - Refinery: 80g, 60w, 30i                (Build: 22s)
    - Tower:    30g, 20i, 40st               (Build: 18s)  <-- now costs STONE + IRON
    - Tower L2 upgrade: 15 steel             (Build: 12s)

  TOWER COMBAT (v10c ballistic cannon):
    - Level 1: {TOWER_CANNON_DAMAGE} dmg / {TOWER_CANNON_CD}s CD = {TOWER_CANNON_DAMAGE/TOWER_CANNON_CD:.1f} raw DPS
    - Ballistic hit rate: ~{TOWER_HIT_RATE*100:.0f}% -> effective DPS: {TOWER_L1_EFFECTIVE_DPS:.1f}
    - Level 2: {TOWER_EXPLOSIVE_DIRECT} direct + {TOWER_EXPLOSIVE_DAMAGE} AoE (r={TOWER_EXPLOSIVE_RADIUS}px)
    - Level 2 effective DPS: {TOWER_L2_DIRECT_DPS:.1f} direct + {TOWER_L2_SPLASH_BONUS:.1f} splash = {TOWER_L2_DIRECT_DPS + TOWER_L2_SPLASH_BONUS:.1f} total
    - Tower range: {TOWER_CANNON_RANGE}px

  UNIT VALUE (cost-effectiveness):
    - Soldier (75g, 8s):     14.0 DPS, 130 HP
    - Archer (55g, 25w, 4s):  6.4 DPS,  75 HP + RANGE (170px)
    - Tower L1 (30g, 20i, 40st): {TOWER_L1_EFFECTIVE_DPS:.1f} eff DPS, {TOWER_HP} HP -> permanent
    - Tower L2 (+15 steel):  {TOWER_L2_DIRECT_DPS + TOWER_L2_SPLASH_BONUS:.1f} eff DPS -> devastating AoE

  STONE is now a REAL resource sink:
    - Tower costs 40 stone (only use of stone currently)
    - Stone gather: 3.5s cycle, 10 per trip -> {worker_income_per_sec('stone', t4):.2f}/s
    - 1 stone worker needs ~30s to gather enough for 1 tower
""")

    # Enemy type stats (v10_7 -- all 9 types)
    print("\n" + "=" * 110)
    print("ENEMY TYPE STATS  (v10_7 -- 9 types)")
    print("=" * 110)
    print(f"  {'Type':20s} | {'HP':>5s} | {'Spd':>4s} | {'Atk':>4s} | {'Range':>5s} | {'CD':>4s} | {'DPS':>5s} | {'Special'}")
    print(f"  {'-'*20}-+-{'-'*5}-+-{'-'*4}-+-{'-'*4}-+-{'-'*5}-+-{'-'*4}-+-{'-'*5}-+-{'-'*30}")
    for etype, d in ENEMY_DEFS.items():
        dps = d["attack"] / d["cd"] if d["cd"] > 0 else 0
        specials = []
        if d.get("self_destruct"): specials.append(f"self-destruct, bld×{d.get('building_mult',1):.0f}")
        if d.get("frontal_armor"): specials.append(f"frontal armor {d['frontal_armor']*100:.0f}%")
        if d.get("heal_rate"): specials.append(f"heal {d['heal_rate']:.0f} HP/s")
        if d.get("economy_only"): specials.append("targets economy")
        if d.get("aoe_radius"): specials.append(f"AOE r={d['aoe_radius']}px")
        spec_str = ", ".join(specials) if specials else "--"
        print(f"  {etype:20s} | {d['hp']:5d} | {d['speed']:4d} | {d['attack']:4d} | {d['range']:5d} | {d['cd']:4.1f} | {dps:5.1f} | {spec_str}")

    # Adaptive difficulty — now handled by Incident Director FSM
    print(f"\n  Adaptive Difficulty: Incident Director FSM (tension-based)")

    # --─ Log Analysis Integration ──────────────────────────────────────────
    print("\n" + "=" * 110)
    print("LOG ANALYSIS INTEGRATION")
    print("=" * 110)

    log_path = find_latest_log()
    log_metrics = None
    if log_path:
        print(f"\n  Found latest log: {log_path}")
        log_metrics = parse_log(log_path)
        log_report(log_metrics)

        # Run matching sim strategy to compare
        log_diff = log_metrics["difficulty"]
        print(f"\n  Running sim for matching difficulty ({log_diff}) -- all strategies...")
        best_strat = None
        best_survive = 0
        best_snaps = None
        for strat in ["balanced", "rush_military", "econ_boom", "tower_defense"]:
            snaps = simulate_detailed(strat, log_diff)
            survive = max((s["wave"] for s in snaps if s["survives"]), default=0)
            print(f"    {strat:16s}: survives through wave {survive}")
            if survive > best_survive:
                best_survive = survive
                best_strat = strat
                best_snaps = snaps

        print(f"\n  Best sim strategy: {best_strat} (survives wave {best_survive})")
        generate_recommendations(log_metrics, best_snaps)
    else:
        print("\n  No game logs found in dist/logs/. Play a game first to generate log data.")
