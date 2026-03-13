import random
import math
from collections import Counter
from constants import (DIFFICULTY_PROFILES, ENEMY_DEFS, ENEMY_VETERAN_BONUS,
                       MAP_COLS, MAP_ROWS, SPAWN_MARGIN, SPAWN_RETRIES)
from utils import dist, clamp, tile_center
from entities import Unit, Building


class EnemyAI:
    def __init__(self, difficulty="medium"):
        profile = DIFFICULTY_PROFILES[difficulty]
        self.wave_number = 0
        self.wave_timer = 0.0
        self.game_won = False
        self.first_wave_sent = False

        # from difficulty profile
        self.first_wave_time = profile["first_wave_time"]
        self.wave_interval = profile["wave_interval"]
        self.max_waves = profile["max_waves"]
        self.wave_base = profile["wave_base"]
        self.wave_scale = profile["wave_scale"]
        self.hp_scale = profile["hp_scale"]
        self.atk_scale = profile["atk_scale"]
        self.archer_wave = profile["archer_wave"]
        self.siege_wave = profile["siege_wave"]
        self.elite_wave = profile["elite_wave"]
        self.multi_dir_wave = profile["multi_dir_wave"]
        self.three_dir_wave = profile["three_dir_wave"]
        self.kill_bounty_base = profile["kill_bounty_base"]
        self.wave_bonus_gold = profile["wave_bonus_gold"]
        self.wave_bonus_wood = profile["wave_bonus_wood"]
        self.wave_bonus_steel = profile["wave_bonus_steel"]

    def update(self, dt, game):
        if self.game_won:
            return
        self.wave_timer += dt

        # first wave comes at first_wave_time, subsequent at wave_interval
        threshold = self.first_wave_time if not self.first_wave_sent else self.wave_interval
        if self.wave_timer >= threshold:
            self.wave_timer = 0.0
            self.wave_number += 1
            self.first_wave_sent = True
            if self.wave_number > self.max_waves:
                self.game_won = True
                return
            self.spawn_wave(game)

    def get_wave_count(self, n):
        return int(self.wave_base + self.wave_scale * math.sqrt(n))

    def get_kill_bounty(self):
        return self.kill_bounty_base + self.wave_number

    def _pick_edges(self, n):
        """Return list of edges to spawn from based on wave number."""
        edges = ["top", "bottom", "left", "right"]
        if n >= self.three_dir_wave:
            return random.sample(edges, 3)
        elif n >= self.multi_dir_wave:
            return random.sample(edges, 2)
        else:
            return [random.choice(edges)]

    def _pick_composition(self, n, count, game):
        """Adaptive composition: reads player defenses and counter-picks."""
        # base probabilities
        p_elite = 0.10 if n >= self.elite_wave else 0
        p_siege = 0.15 if n >= self.siege_wave else 0
        p_archer = 0.30 if n >= self.archer_wave else 0

        # count player defenses for adaptation
        tower_count = sum(1 for b in game.player_buildings
                          if b.building_type == "tower" and b.built
                          and b.alive and not getattr(b, 'ruined', False))
        soldier_count = sum(1 for u in game.player_units
                            if u.unit_type == "soldier" and u.alive)
        archer_count = sum(1 for u in game.player_units
                           if u.unit_type == "archer" and u.alive)
        total_military = soldier_count + archer_count

        # adapt: more towers -> more siege
        if n >= self.siege_wave:
            if tower_count >= 2:
                p_siege += 0.10
            if tower_count >= 4:
                p_siege += 0.10

        # adapt: archer-heavy -> more elites (tanky melee counters ranged)
        if n >= self.elite_wave and total_military > 0:
            if archer_count / max(1, total_military) > 0.5:
                p_elite += 0.08

        # adapt: soldier-heavy -> more enemy archers (ranged counters melee)
        if n >= self.archer_wave and total_military > 0:
            if soldier_count / max(1, total_military) > 0.6:
                p_archer += 0.10

        # ensure soldier gets a minimum share and normalize
        p_soldier = max(0.20, 1.0 - p_elite - p_siege - p_archer)
        total = p_elite + p_siege + p_archer + p_soldier
        p_elite /= total
        p_siege /= total
        p_archer /= total
        # soldier fills remaining probability (1 - p_elite - p_siege - p_archer)

        types = []
        for _ in range(count):
            roll = random.random()
            if roll < p_elite:
                types.append("enemy_elite")
            elif roll < p_elite + p_siege:
                types.append("enemy_siege")
            elif roll < p_elite + p_siege + p_archer:
                types.append("enemy_archer")
            else:
                types.append("enemy_soldier")
        return types

    def spawn_wave(self, game):
        n = self.wave_number
        count = self.get_wave_count(n)

        hp_mult = 1.0 + self.hp_scale * n
        atk_mult = 1.0 + self.atk_scale * n

        edges = self._pick_edges(n)
        types = self._pick_composition(n, count, game)

        # log wave start
        comp = Counter(types)
        comp_str = " ".join(f"{v}x{k.replace('enemy_', '')}" for k, v in comp.items())
        edge_str = ",".join(edges)
        game.logger.log(game.game_time, "WAVE_START", n,
                        edge_str, comp_str, f"hp:{hp_mult:.2f}",
                        count, f"atk:{atk_mult:.2f}")

        # distribute enemies across edges
        per_edge = len(types) // len(edges)
        remainder = len(types) % len(edges)

        idx = 0
        for ei, edge in enumerate(edges):
            edge_count = per_edge + (1 if ei < remainder else 0)
            for _ in range(edge_count):
                if idx >= len(types):
                    break
                utype = types[idx]
                idx += 1

                c, r = self._get_spawn_pos(edge, game)
                if c is None:
                    continue

                wx, wy = tile_center(c, r)
                self._create_enemy(wx, wy, utype, hp_mult, atk_mult, game)

        # spawn escaped veterans from previous wave
        self._spawn_veterans(game, hp_mult, atk_mult)

    def _spawn_veterans(self, game, hp_mult, atk_mult):
        """Respawn enemies that escaped in previous waves as veterans.

        v9: returning veterans get +25% base stat bonus AND their accumulated
        XP applied as rank bonuses on top of wave scaling.
        """
        if not hasattr(game, 'escaped_enemies') or not game.escaped_enemies:
            return

        vet_mult = 1.0 + ENEMY_VETERAN_BONUS
        for vet in game.escaped_enemies:
            edge = random.choice(["top", "bottom", "left", "right"])
            c, r = self._get_spawn_pos(edge, game)
            if c is None:
                continue

            wx, wy = tile_center(c, r)
            enemy = self._create_enemy(wx, wy, vet["unit_type"],
                                       hp_mult * vet_mult, atk_mult * vet_mult, game)
            # preserve stored building_mult from when they fled
            enemy.building_mult = vet.get("building_mult", 1.0)

            # v9: restore accumulated XP and apply rank bonuses
            stored_xp = vet.get("xp", 0)
            if stored_xp > 0:
                enemy.xp = stored_xp
                # force rank calculation and stat application
                enemy._check_rank_up()
                enemy.force_apply_rank_bonuses()

        game.escaped_enemies.clear()

    def _create_enemy(self, wx, wy, utype, hp_mult, atk_mult, game):
        """Create a scaled enemy unit, assign it a target, and add to game."""
        enemy = Unit(wx, wy, utype, "enemy")
        enemy.max_hp = int(enemy.max_hp * hp_mult)
        enemy.hp = enemy.max_hp
        enemy.attack_power = int(enemy.attack_power * atk_mult)
        # v9: store wave-scaled values as base for rank system
        enemy._base_hp = enemy.max_hp
        enemy._base_attack = enemy.attack_power
        enemy._base_range = enemy.attack_range
        target = self._find_target(enemy, game,
                                   prefer_buildings=(enemy.building_mult > 1.0))
        if target:
            enemy.target_entity = target
            enemy.state = "attacking"
        game.enemy_units.append(enemy)
        return enemy

    def _get_spawn_pos(self, edge, game):
        m = SPAWN_MARGIN
        spawn_fn = {
            "top":    lambda: (random.randint(m, MAP_COLS - m - 1), 1),
            "bottom": lambda: (random.randint(m, MAP_COLS - m - 1), MAP_ROWS - 2),
            "left":   lambda: (1, random.randint(m, MAP_ROWS - m - 1)),
            "right":  lambda: (MAP_COLS - 2, random.randint(m, MAP_ROWS - m - 1)),
        }
        for _ in range(SPAWN_RETRIES):
            c, r = spawn_fn[edge]()

            attempts = 0
            while not game.game_map.is_walkable(c, r) and attempts < 15:
                c += random.choice([-1, 0, 1])
                r += random.choice([-1, 0, 1])
                c = clamp(c, 1, MAP_COLS - 2)
                r = clamp(r, 1, MAP_ROWS - 2)
                attempts += 1

            if game.game_map.is_walkable(c, r):
                return c, r
        return None, None

    def _find_target(self, unit, game, prefer_buildings=False):
        """v9.1: utility-scored target selection for spawned enemies."""
        best = None
        best_score = -1
        best_ruin = None
        best_ruin_score = -1

        # single pass over all buildings — categorize as normal or ruin
        for b in game.player_buildings:
            if not b.alive:
                continue
            score = unit._score_target(b)
            if getattr(b, 'ruined', False):
                if score > best_ruin_score:
                    best_ruin_score = score
                    best_ruin = b
            else:
                if score > best_score:
                    best_score = score
                    best = b

        # siege units strongly prefer non-ruined buildings
        if prefer_buildings and best:
            return best

        # also consider units
        for u in game.player_units:
            if not u.alive:
                continue
            score = unit._score_target(u)
            if score > best_score:
                best_score = score
                best = u

        # fallback to ruins
        return best if best else best_ruin
