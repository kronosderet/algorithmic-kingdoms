import math
import random
import pygame
from constants import (COL_HEALTH_BG, COL_HEALTH, COL_ENEMY_HEALTH,
                       XP_PER_HIT, XP_KILL_BONUS,
                       ENEMY_XP_PER_HIT, ENEMY_XP_KILL_BONUS,
                       MSG_COL_ATTACK, display_name)
from utils import pos_to_tile
from fractal_ui import fractal_bar_simple


# ---------------------------------------------------------------------------
# Shared combat helper  (deduplicates melee & arrow post-damage logic)
# ---------------------------------------------------------------------------
def _process_combat_hit(attacker, target, game, source_label):
    """Handle post-damage XP, rank-up, bounty, and building ruin/destroy logging.

    Args:
        attacker: Unit that dealt damage (or None for sourceless hits).
        target:   Entity that was damaged.
        game:     Game instance for logger, resources, enemy_ai.
        source_label: e.g. "melee" or "arrow" (appears in log).
    """
    # Avoid circular import: check class name by string instead of isinstance
    is_building = type(target).__name__ == "Building"
    is_unit = type(target).__name__ == "Unit"

    # v10_zeta.1: telemetry — record damage dealt/taken
    hub = getattr(game, 'telemetry', None)
    if hub is not None:
        actual_dmg = getattr(target, '_last_damage_taken', 0)
        if actual_dmg > 0:
            a_eid = attacker.eid if attacker else 0
            a_type = getattr(attacker, 'unit_type', source_label) if attacker else source_label
            a_stance = getattr(attacker, 'stance', "")
            # Check if attacker is in a formation (has a squad)
            in_fmt = False
            if attacker and hasattr(game, 'player_squad_mgr') and attacker.owner == "player":
                in_fmt = game.player_squad_mgr.get_squad(attacker) is not None
            hub.record_damage_dealt(game.game_time, a_eid, actual_dmg,
                                    in_formation=in_fmt, attacker_type=a_type,
                                    attacker_stance=str(a_stance))
            t_type = getattr(target, 'unit_type', '') or getattr(target, 'building_type', '')
            hub.record_damage_taken(game.game_time, target.eid, actual_dmg,
                                    target_type=t_type)
            if is_building and target.alive and not getattr(target, 'ruined', False):
                if target.hp < target.max_hp * 0.7:
                    hub.record_building_damaged()

    # building ruin/destroy logging
    if is_building and (target.ruined or not target.alive):
        evt = "BUILDING_RUINED" if target.alive else "BUILDING_DESTROYED"
        game.logger.log(game.game_time, evt,
                        game.enemy_ai.wave_number,
                        target.building_type, source_label)
    # XP for non-workers
    if attacker and attacker.alive and attacker.unit_type != "worker":
        old_rank = attacker.rank
        xp_hit = XP_PER_HIT if attacker.owner == "player" else ENEMY_XP_PER_HIT
        xp_kill = XP_KILL_BONUS if attacker.owner == "player" else ENEMY_XP_KILL_BONUS
        attacker.grant_xp(xp_hit)
        if not target.alive and target.owner != attacker.owner:
            attacker.grant_xp(xp_kill)
        if attacker.rank > old_rank:
            game.logger.log(game.game_time, "RANK_UP",
                            game.enemy_ai.wave_number,
                            attacker.unit_type, str(attacker.rank),
                            attacker.owner)
    # kill bounty (player kills enemy)
    if not target.alive and target.owner == "enemy":
        owner = attacker.owner if attacker else "player"
        if owner == "player":
            bounty = game.enemy_ai.get_kill_bounty()
            game.resources.gold += bounty
            game.logger.log(game.game_time, "UNIT_KILLED",
                            game.enemy_ai.wave_number,
                            attacker.unit_type if attacker else source_label,
                            target.unit_type,
                            f"rank_{attacker.rank}" if attacker else "",
                            bounty, f"{source_label} {owner}")
            game.add_message(f"Enemy {display_name(target.unit_type)} slain (+{bounty}g)",
                             MSG_COL_ATTACK)
            # v10_zeta.1: telemetry kill + death
            if hub is not None:
                killer_t = attacker.unit_type if attacker else source_label
                hub.record_kill(killer_t, target.unit_type, target.owner,
                                killer_stance=str(getattr(attacker, 'stance', '')))
                hub.record_unit_death(game.game_time, target.eid)
    # player unit lost (enemy kills player unit)
    if not target.alive and target.owner == "player" and is_unit:
        killer = attacker.unit_type if attacker else source_label
        game.logger.log(game.game_time, "PLAYER_UNIT_LOST",
                        game.enemy_ai.wave_number,
                        target.unit_type, killer,
                        f"rank_{target.rank}",
                        target.xp, source_label)
        game.add_message(f"{display_name(target.unit_type)} lost to {display_name(killer)}",
                         MSG_COL_ATTACK)
        # v10_zeta.1: telemetry kill + death
        if hub is not None:
            hub.record_kill(killer, target.unit_type, target.owner,
                            killer_stance=str(getattr(attacker, 'stance', '') if attacker else ''))
            hub.record_unit_death(game.game_time, target.eid)
    # building destroyed message
    if is_building and not target.alive:
        game.add_message(f"{display_name(target.building_type)} destroyed!",
                         MSG_COL_ATTACK)


# ---------------------------------------------------------------------------
# Entity base
# ---------------------------------------------------------------------------
class Entity:
    _next_id = 0

    def __init__(self, x, y, hp, owner):
        Entity._next_id += 1
        self.eid = Entity._next_id
        self.x, self.y = float(x), float(y)
        self.hp = hp
        self.max_hp = hp
        self.owner = owner
        self.selected = False
        self.alive = True
        self.last_attacker = None  # v9.3: who last hit us
        # v10_delta: physics velocity
        self.vx = 0.0
        self.vy = 0.0
        self.facing_angle = 0.0

    def get_tile(self):
        return pos_to_tile(self.x, self.y)

    def take_damage(self, dmg, attacker=None):
        # v10_8: Golden Spiral resonance evasion
        miss = getattr(self, '_spiral_miss_chance', 0.0)
        if miss > 0 and not getattr(self, '_dissonance_nullified', False):
            if random.random() < miss:
                return  # evaded
        # v10_6: frontal armor (Shieldbearer) — reduce damage from the front
        armor = getattr(self, 'frontal_armor', 0.0)
        if armor > 0 and attacker is not None:
            ax = getattr(attacker, 'x', self.x) - self.x
            ay = getattr(attacker, 'y', self.y) - self.y
            facing = getattr(self, 'facing_angle', 0.0)
            attack_angle = math.atan2(ay, ax)
            diff = abs(attack_angle - facing)
            if diff > math.pi:
                diff = 2 * math.pi - diff
            if diff < math.pi / 2:  # within ±90° of front
                dmg = int(dmg * (1.0 - armor))
        self.hp -= dmg
        # v10_zeta.1: store actual damage for telemetry pickup
        self._last_damage_taken = dmg
        if attacker is not None:
            self.last_attacker = attacker
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw_health_bar(self, surf, cam, width=24):
        if self.hp >= self.max_hp:
            return
        z = cam.zoom
        w = max(4, int(width * z))
        sx, sy = cam.world_to_screen(self.x, self.y)
        bx = sx - w // 2
        by = sy - int(20 * z)
        bh = max(2, int(4 * z))
        ratio = self.hp / self.max_hp
        col = COL_HEALTH if self.owner == "player" else COL_ENEMY_HEALTH
        fractal_bar_simple(surf, bx, by, w, bh, ratio, col)

    def draw_energy_bar(self, surf, cam, width=24):
        """Draw thin energy bar below the HP bar. Only shown when energy < max."""
        max_e = getattr(self, 'max_energy', 0)
        if max_e <= 0:
            return
        cur_e = getattr(self, 'energy', max_e)
        if cur_e >= max_e:
            return
        z = cam.zoom
        w = max(4, int(width * z))
        sx, sy = cam.world_to_screen(self.x, self.y)
        bx = sx - w // 2
        # position just below the HP bar (HP bar is at y - 20*z, height ~4*z)
        by = sy - int(20 * z) + max(2, int(4 * z)) + 1
        bh = max(1, int(2 * z))
        ratio = cur_e / max_e
        # yellow when OK, orange-red when exhausted
        if ratio >= 0.2:
            col = (220, 200, 60)
        else:
            col = (220, 100, 30)
        fractal_bar_simple(surf, bx, by, w, bh, ratio, col)
