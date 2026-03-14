import math
import random
import pygame
from constants import (COL_HEALTH_BG, COL_HEALTH, COL_ENEMY_HEALTH,
                       XP_PER_HIT, XP_KILL_BONUS,
                       ENEMY_XP_PER_HIT, ENEMY_XP_KILL_BONUS,
                       MSG_COL_ATTACK, display_name)
from utils import pos_to_tile


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
        pygame.draw.rect(surf, COL_HEALTH_BG, (bx, by, w, bh))
        pygame.draw.rect(surf, col, (bx, by, int(w * ratio), bh))
