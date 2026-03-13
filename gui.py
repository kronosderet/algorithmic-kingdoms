import pygame
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, TOP_BAR_H, BOTTOM_PANEL_H,
                       UNIT_DEFS, BUILDING_DEFS, UNIT_COLORS, UNIT_LABELS,
                       ENEMY_COLORS, ENEMY_DEFS,
                       BUILDING_COLORS, BUILDING_LABELS,
                       COL_GUI_BG, COL_GUI_BORDER, COL_TEXT, COL_GOLD,
                       COL_WOOD, COL_IRON_C, COL_STEEL, COL_STONE, COL_BTN,
                       COL_BTN_HOVER, COL_BTN_DISABLED, COL_BTN_TEXT,
                       REFINE_TIME,
                       MILITARY_RANKS, RANK_XP_THRESHOLDS, RANK_COLORS,
                       WORKER_RANKS, WORKER_RANK_XP, WORKER_SKILL_NAMES,
                       WORKER_SKILL_COLORS, WORKER_RANK_SPEED_BONUS,
                       RESOURCE_TO_SKILL,
                       TOWER_UPGRADE_COST, TOWER_CANNON_DAMAGE,
                       TOWER_CANNON_CD, TOWER_EXPLOSIVE_DIRECT,
                       TOWER_UPGRADE_TIME,
                       TRAIT_DISPLAY,
                       GARRISON_COST, GARRISON_MAX_WORKERS,
                       FOREMAN_BUILDINGS, DROPOFF_BUILDING_TYPES,
                       UPGRADE_PATH, PRODUCTION_RATES,
                       PRODUCTION_TICK_INTERVAL, BUILD_PROXIMITY,
                       FORGE_TIME, SMELTER_REFINERY_BONUS,
                       STANCE_AGGRESSIVE, STANCE_NAMES, STANCE_COLORS,
                       FORMATION_NAMES)
from utils import draw_text, ruin_rebuild_cost
from entities import Building, Unit


class GUI:
    def __init__(self):
        self.font = None
        self.font_sm = None
        self.font_xs = None
        self.font_lg = None
        self.buttons = []  # list of (rect, label, callback, enabled)

    def init_fonts(self):
        self.font = pygame.font.SysFont(None, 22)
        self.font_sm = pygame.font.SysFont(None, 18)
        self.font_xs = pygame.font.SysFont(None, 15)
        self.font_lg = pygame.font.SysFont(None, 28)

    @staticmethod
    def _draw_clipped(surf, text, x, y, font, color=None, max_width=260):
        """Draw text truncated with '...' if it exceeds max_width."""
        if color is None:
            color = COL_TEXT
        rendered = font.render(text, True, color)
        if rendered.get_width() <= max_width:
            surf.blit(rendered, (x, y))
        else:
            while len(text) > 1:
                text = text[:-1]
                rendered = font.render(text + "..", True, color)
                if rendered.get_width() <= max_width:
                    surf.blit(rendered, (x, y))
                    return
            surf.blit(font.render("..", True, color), (x, y))

    @staticmethod
    def cost_str(gold=0, wood=0, iron=0, steel=0, stone=0):
        parts = []
        if gold:
            parts.append(f"{gold}g")
        if wood:
            parts.append(f"{wood}w")
        if iron:
            parts.append(f"{iron}i")
        if steel:
            parts.append(f"{steel}s")
        if stone:
            parts.append(f"{stone}st")
        return " ".join(parts)

    @staticmethod
    def unit_cost_str(unit_type):
        d = UNIT_DEFS[unit_type]
        return GUI.cost_str(gold=d["gold"], wood=d["wood"], steel=d["steel"])

    @staticmethod
    def building_cost_str(btype):
        d = BUILDING_DEFS[btype]
        return GUI.cost_str(gold=d["gold"], wood=d["wood"], iron=d.get("iron", 0),
                            steel=d.get("steel", 0), stone=d.get("stone", 0))

    # ------------------------------------------------------------------
    # Inline HP bar helper (used by both player + enemy panels)
    # ------------------------------------------------------------------
    def _draw_hp_bar(self, surf, x, y, w, h, hp, max_hp, color_fill, color_bg=(40, 10, 10)):
        """Draw a filled HP bar with numeric overlay."""
        ratio = max(0.0, min(1.0, hp / max_hp)) if max_hp > 0 else 0
        pygame.draw.rect(surf, color_bg, (x, y, w, h))
        fill_w = int(w * ratio)
        if fill_w > 0:
            pygame.draw.rect(surf, color_fill, (x, y, fill_w, h))
        pygame.draw.rect(surf, COL_GUI_BORDER, (x, y, w, h), 1)
        hp_text = f"{int(hp)}/{max_hp}"
        draw_text(surf, hp_text, x + w // 2, y + h // 2, self.font_xs, (255, 255, 255), center=True)

    # ------------------------------------------------------------------
    # Resource icon shapes (VDD: distinct per resource)
    # ------------------------------------------------------------------
    @staticmethod
    def _draw_res_icon(surf, cx, cy, res_type):
        """Draw a small distinctive shape per resource type."""
        if res_type == "gold":
            # diamond
            pts = [(cx, cy - 7), (cx + 6, cy), (cx, cy + 7), (cx - 6, cy)]
            pygame.draw.polygon(surf, COL_GOLD, pts)
            pygame.draw.polygon(surf, (180, 150, 0), pts, 1)
        elif res_type == "wood":
            # triangle (tree)
            pts = [(cx, cy - 7), (cx + 6, cy + 6), (cx - 6, cy + 6)]
            pygame.draw.polygon(surf, COL_WOOD, pts)
            pygame.draw.polygon(surf, (20, 120, 20), pts, 1)
        elif res_type == "iron":
            # pentagon
            import math
            pts = []
            for i in range(5):
                a = math.radians(90 + 72 * i)
                pts.append((cx + int(7 * math.cos(a)), cy - int(7 * math.sin(a))))
            pygame.draw.polygon(surf, COL_IRON_C, pts)
            pygame.draw.polygon(surf, (130, 130, 145), pts, 1)
        elif res_type == "steel":
            # hexagon
            import math
            pts = []
            for i in range(6):
                a = math.radians(60 * i)
                pts.append((cx + int(7 * math.cos(a)), cy - int(7 * math.sin(a))))
            pygame.draw.polygon(surf, COL_STEEL, pts)
            pygame.draw.polygon(surf, (70, 120, 180), pts, 1)
        elif res_type == "stone":
            # square rotated 45°
            s = 5
            pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
            pygame.draw.polygon(surf, COL_STONE, pts)
            pygame.draw.polygon(surf, (120, 110, 100), pts, 1)

    # ------------------------------------------------------------------
    # TOP BAR
    # ------------------------------------------------------------------
    def draw_top_bar(self, surf, resources, enemy_ai, player_units):
        pygame.draw.rect(surf, COL_GUI_BG, (0, 0, SCREEN_WIDTH, TOP_BAR_H))
        pygame.draw.line(surf, COL_GUI_BORDER, (0, TOP_BAR_H), (SCREEN_WIDTH, TOP_BAR_H))

        # --- Resources (left side) ---
        res_list = [
            ("gold", resources.gold, COL_GOLD),
            ("wood", resources.wood, COL_WOOD),
            ("iron", resources.iron, COL_IRON_C),
            ("steel", resources.steel, COL_STEEL),
            ("stone", resources.stone, COL_STONE),
        ]
        x = 12
        for res_type, amount, color in res_list:
            self._draw_res_icon(surf, x + 8, 20, res_type)
            draw_text(surf, str(int(amount)), x + 20, 12, self.font, color)
            x += 80

        # --- Separator ---
        sep_x = x + 8
        pygame.draw.line(surf, COL_GUI_BORDER, (sep_x, 6), (sep_x, 34))

        # --- Population (compact) ---
        pop = len(player_units)
        pop_x = sep_x + 12
        draw_text(surf, f"Pop {pop}", pop_x, 12, self.font, (180, 200, 255))

        # --- Wave info (right side, with visual timer bar) ---
        wave_x = SCREEN_WIDTH - 380
        pygame.draw.line(surf, COL_GUI_BORDER, (wave_x - 12, 6), (wave_x - 12, 34))

        wave_str = f"Wave {enemy_ai.wave_number}/{enemy_ai.max_waves}"
        draw_text(surf, wave_str, wave_x, 4, self.font_sm, COL_TEXT)

        # next wave timer bar
        threshold = enemy_ai.first_wave_time if not enemy_ai.first_wave_sent else enemy_ai.wave_interval
        time_left = max(0, threshold - enemy_ai.wave_timer)
        timer_ratio = 1.0 - min(1.0, enemy_ai.wave_timer / threshold) if threshold > 0 else 0
        bar_x = wave_x
        bar_y = 20
        bar_w = 100
        bar_h = 10
        pygame.draw.rect(surf, (40, 25, 25), (bar_x, bar_y, bar_w, bar_h))
        # color transitions from green (safe) to red (imminent)
        if timer_ratio > 0.5:
            bar_col = (60, 180, 60)
        elif timer_ratio > 0.2:
            bar_col = (200, 180, 40)
        else:
            bar_col = (220, 60, 40)
        fill_w = int(bar_w * timer_ratio)
        if fill_w > 0:
            pygame.draw.rect(surf, bar_col, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surf, COL_GUI_BORDER, (bar_x, bar_y, bar_w, bar_h), 1)
        draw_text(surf, f"{int(time_left)}s", bar_x + bar_w + 6, bar_y - 1, self.font_xs, COL_TEXT)

        # enemy estimate
        est_x = wave_x + bar_w + 40
        if enemy_ai.wave_number > 0 and enemy_ai.wave_number < enemy_ai.max_waves:
            next_count = enemy_ai.get_wave_count(enemy_ai.wave_number + 1)
            draw_text(surf, f"~{next_count}", est_x, 12, self.font_sm, (180, 100, 100))

    # ------------------------------------------------------------------
    # BOTTOM PANEL
    # ------------------------------------------------------------------
    def draw_bottom_panel(self, surf, selected, game, inspected_enemy=None):
        py = SCREEN_HEIGHT - BOTTOM_PANEL_H
        pygame.draw.rect(surf, COL_GUI_BG, (0, py, SCREEN_WIDTH, BOTTOM_PANEL_H))
        pygame.draw.line(surf, COL_GUI_BORDER, (0, py), (SCREEN_WIDTH, py))

        self.buttons.clear()

        # v10_2: inspected enemy takes priority when nothing player-selected
        if not selected and inspected_enemy:
            self._draw_enemy_panel(surf, py, inspected_enemy)
            return

        if not selected:
            self._draw_global_buttons(surf, py, game)
            return

        entity = selected[0]

        # info section
        if isinstance(entity, Building):
            self._draw_building_panel(surf, py, entity, game)
        elif isinstance(entity, Unit):
            if len(selected) > 1:
                self._draw_multi_unit_panel(surf, py, selected, game)
            else:
                self._draw_unit_panel(surf, py, entity, game)

    # ------------------------------------------------------------------
    # ENEMY INSPECTION PANEL (v10_2)
    # ------------------------------------------------------------------
    def _draw_enemy_panel(self, surf, py, e):
        """Show enemy unit info — read-only, no action buttons."""
        # red accent stripe at top of panel
        pygame.draw.rect(surf, (80, 20, 20), (0, py, SCREEN_WIDTH, 3))

        # icon circle with enemy color
        color = ENEMY_COLORS.get(e.unit_type, (80, 20, 20))
        # brighten for visibility on dark panel
        bright = tuple(min(255, c + 80) for c in color)
        pygame.draw.circle(surf, bright, (40, py + 40), 20)
        pygame.draw.circle(surf, (200, 60, 60), (40, py + 40), 20, 2)
        label = UNIT_LABELS.get(e.unit_type, "?")
        draw_text(surf, label, 40, py + 40, self.font_lg, (255, 255, 255), center=True)

        # "ENEMY" tag
        draw_text(surf, "ENEMY", 80, py + 8, self.font_xs, (255, 80, 80))

        # name + rank
        name = e.unit_type.replace("enemy_", "").replace("_", " ").title()
        if e.rank > 0 and e.rank < len(MILITARY_RANKS):
            rank_name = MILITARY_RANKS[e.rank]
            name += f" [{rank_name}]"
        draw_text(surf, name, 115, py + 7, self.font, COL_TEXT)

        # traits
        trait_y = py + 22
        if e.traits:
            trait_names = ", ".join(t.replace("_", " ").title() for t in sorted(e.traits))
            trait_cols = [TRAIT_DISPLAY.get(t, {}).get("color", COL_TEXT) for t in sorted(e.traits)]
            self._draw_clipped(surf, trait_names, 80, trait_y,
                               self.font_xs, trait_cols[0] if trait_cols else (180, 140, 140),
                               max_width=240)

        # HP bar (prominent, red)
        self._draw_hp_bar(surf, 80, py + 38, 160, 14, e.hp, e.max_hp, (200, 50, 50))

        # stats line
        draw_text(surf, f"ATK: {e.attack_power}   SPD: {e.speed}   RNG: {e.attack_range}",
                  80, py + 58, self.font_sm, (200, 180, 180))

        # state
        state_str = e.state
        if e.state == "fleeing":
            state_str = "fleeing!"
        draw_text(surf, f"State: {state_str}", 80, py + 76, self.font_sm, (180, 120, 120))

        # XP / rank info
        if e.rank > 0:
            rank_col = RANK_COLORS.get(e.rank, (180, 180, 180))
            draw_text(surf, f"Rank {e.rank} — XP: {e.xp}", 80, py + 94, self.font_xs, rank_col)

        # special info for siege and v10_6 types
        ability_y = py + 108
        if e.unit_type == "enemy_siege":
            draw_text(surf, "Siege: 2x damage to buildings", 80, ability_y, self.font_xs, (220, 160, 60))
        elif e.unit_type == "enemy_sapper":
            draw_text(surf, f"Sapper: {e.building_mult:.0f}x building dmg, self-destruct", 80, ability_y, self.font_xs, (200, 200, 60))
        elif e.unit_type == "enemy_shieldbearer":
            draw_text(surf, f"Frontal Armor: {int(e.frontal_armor*100)}% — flank to bypass!", 80, ability_y, self.font_xs, (140, 160, 200))
        elif e.unit_type == "enemy_healer":
            draw_text(surf, f"Healer: {e.heal_rate:.0f} HP/s to allies", 80, ability_y, self.font_xs, (80, 220, 120))
        elif e.unit_type == "enemy_raider":
            draw_text(surf, "Raider: targets workers & economy", 80, ability_y, self.font_xs, (220, 100, 150))
        elif e.unit_type == "enemy_warlock":
            draw_text(surf, f"Warlock: AOE {e.aoe_radius}px splash damage", 80, ability_y, self.font_xs, (180, 100, 220))

        # right-side hint
        draw_text(surf, "Right-click with units to attack", SCREEN_WIDTH - 250, py + 100,
                  self.font_xs, (100, 80, 80))

    # ------------------------------------------------------------------
    # BUILDING PANEL
    # ------------------------------------------------------------------
    def _draw_building_panel(self, surf, py, b, game):
        # icon
        color = BUILDING_COLORS.get(b.building_type, (100, 100, 100))
        if b.ruined:
            color = tuple(c // 3 for c in color)
        pygame.draw.rect(surf, color, (15, py + 10, 50, 50), border_radius=4)
        pygame.draw.rect(surf, COL_GUI_BORDER, (15, py + 10, 50, 50), 1, border_radius=4)
        label = BUILDING_LABELS.get(b.building_type, "??")
        draw_text(surf, label, 40, py + 35, self.font_lg, (255, 255, 255), center=True)

        # name
        name = b.building_type.replace("_", " ").title()
        if b.ruined:
            name += " (RUINS)"
        elif b.building_type == "tower" and b.built:
            if b.tower_level >= 2:
                name = "Explosive Cannon (Lv.2)"
            else:
                name = "Cannon Tower (Lv.1)"
        draw_text(surf, name, 80, py + 10, self.font)

        # HP bar (visual instead of text)
        hp_col = (60, 60, 60) if b.ruined else (0, 170, 0)
        self._draw_hp_bar(surf, 80, py + 30, 160, 12, b.hp, b.max_hp, hp_col)

        if b.ruined:
            gold_c, wood_c, iron_c, steel_c, stone_c = ruin_rebuild_cost(b.building_type)
            cost = self.cost_str(gold=gold_c, wood=wood_c, iron=iron_c, steel=steel_c, stone=stone_c)
            self._draw_clipped(surf, f"Right-click workers to rebuild ({cost})",
                              80, py + 50, self.font_sm, (180, 140, 80), max_width=260)
            return

        if not b.built:
            pct = int(100 * b.build_progress / b.build_time) if b.build_time > 0 else 0
            # construction progress bar
            bar_x, bar_y, bar_w, bar_h = 80, py + 50, 160, 10
            pygame.draw.rect(surf, (30, 30, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surf, (0, 140, 255), (bar_x, bar_y, int(bar_w * pct / 100), bar_h))
            pygame.draw.rect(surf, COL_GUI_BORDER, (bar_x, bar_y, bar_w, bar_h), 1)
            draw_text(surf, f"Building {pct}%", bar_x + bar_w + 8, bar_y - 1, self.font_xs, (0, 180, 255))
            return

        # status line (training / refinery / tower stats)
        status_y = py + 50
        if b.train_queue:
            pct = int(100 * b.train_progress / b.train_time) if b.train_time > 0 else 0
            bar_x, bar_w, bar_h = 80, 140, 10
            pygame.draw.rect(surf, (30, 30, 50), (bar_x, status_y, bar_w, bar_h))
            pygame.draw.rect(surf, (200, 180, 0), (bar_x, status_y, int(bar_w * pct / 100), bar_h))
            pygame.draw.rect(surf, COL_GUI_BORDER, (bar_x, status_y, bar_w, bar_h), 1)
            unit_name = b.train_queue[0].replace("_", " ").title()
            draw_text(surf, f"{unit_name} ({pct}%)", bar_x + bar_w + 8, status_y - 1,
                      self.font_xs, (255, 200, 0))
            if len(b.train_queue) > 1:
                draw_text(surf, f"+{len(b.train_queue) - 1} queued", bar_x + bar_w + 8, status_y + 12,
                          self.font_xs, (160, 150, 80))

        elif b.building_type == "refinery":
            if b.refine_active:
                pct = int(100 * b.refine_progress / REFINE_TIME)
                bar_x, bar_w, bar_h = 80, 140, 10
                pygame.draw.rect(surf, (30, 30, 50), (bar_x, status_y, bar_w, bar_h))
                pygame.draw.rect(surf, (100, 160, 220), (bar_x, status_y, int(bar_w * pct / 100), bar_h))
                pygame.draw.rect(surf, COL_GUI_BORDER, (bar_x, status_y, bar_w, bar_h), 1)
                draw_text(surf, f"Refining {pct}%", bar_x + bar_w + 8, status_y - 1,
                          self.font_xs, (100, 160, 220))
            else:
                draw_text(surf, "Idle — needs 2 Iron", 80, status_y, self.font_sm, (100, 100, 120))

        elif b.building_type == "tower":
            if b.tower_upgrading:
                pct = int(100 * b.tower_upgrade_progress / TOWER_UPGRADE_TIME)
                draw_text(surf, f"Upgrading... {pct}%", 80, status_y, self.font_sm, (255, 140, 40))
            else:
                dmg = TOWER_EXPLOSIVE_DIRECT if b.tower_level >= 2 else TOWER_CANNON_DAMAGE
                tag = "AoE" if b.tower_level >= 2 else "Single"
                draw_text(surf, f"DMG {dmg} ({tag})  CD {TOWER_CANNON_CD:.1f}s",
                          80, status_y, self.font_sm, (180, 180, 160))

        # v10.2: drop-off building status
        elif b.building_type in DROPOFF_BUILDING_TYPES:
            res = DROPOFF_BUILDING_TYPES[b.building_type].title()
            draw_text(surf, f"{res} Drop-off Point", 80, status_y, self.font_sm, (160, 180, 140))
            if b.upgrading_to:
                pct = int(100 * b.upgrade_progress / b.upgrade_time) if b.upgrade_time > 0 else 0
                draw_text(surf, f"Upgrading... {pct}%", 80, status_y + 16, self.font_sm, (255, 140, 40))

        # v10.2: production building status
        elif b.building_type in PRODUCTION_RATES:
            pconfig = PRODUCTION_RATES[b.building_type]
            n_workers = len(b.stationed_workers)
            rate = pconfig["base_rate"] + pconfig["worker_rate"] * n_workers
            res_name = pconfig["resource"].title()
            draw_text(surf, f"Producing {res_name}: {rate:.1f}/{PRODUCTION_TICK_INTERVAL:.0f}s  Workers: {n_workers}/{pconfig['max_workers']}",
                      80, status_y, self.font_sm, (180, 200, 160))

        # v10.2: forge status (like refinery)
        elif b.building_type == "forge":
            if b.refine_active:
                pct = int(100 * b.refine_progress / FORGE_TIME)
                bar_x, bar_w, bar_h = 80, 140, 10
                pygame.draw.rect(surf, (30, 30, 50), (bar_x, status_y, bar_w, bar_h))
                pygame.draw.rect(surf, (180, 100, 50), (bar_x, status_y, int(bar_w * pct / 100), bar_h))
                pygame.draw.rect(surf, COL_GUI_BORDER, (bar_x, status_y, bar_w, bar_h), 1)
                draw_text(surf, f"Forging {pct}%", bar_x + bar_w + 8, status_y - 1,
                          self.font_xs, (180, 100, 50))
            else:
                draw_text(surf, "Idle — needs 2 Stone + 1 Iron", 80, status_y, self.font_sm, (100, 100, 120))
            n_workers = len(b.stationed_workers)
            if n_workers > 0:
                draw_text(surf, f"Workers: {n_workers}", 80, status_y + 16, self.font_sm, (160, 140, 100))

        # action buttons (moved further right for cleaner spacing)
        btn_x = 360
        btn_y = py + 8
        btn_w, btn_h = 140, 48

        if b.building_type == "town_hall":
            ud = UNIT_DEFS["worker"]
            self._add_button(surf, btn_x, btn_y, btn_w, btn_h, "Train Worker (Q)",
                             lambda: b.start_train("worker", game),
                             game.resources.can_afford(gold=ud["gold"]),
                             cost_text=self.unit_cost_str("worker"))
            # v10_2: garrison display + ungarrison button
            if b.garrison:
                g_count = len(b.garrison)
                draw_text(surf, f"Garrison: {g_count}/{GARRISON_MAX_WORKERS}",
                          btn_x, btn_y + btn_h + 8, self.font_sm, (220, 180, 80))
                self._add_button(surf, btn_x + btn_w + 8, btn_y, btn_w, btn_h,
                                 "Ungarrison",
                                 lambda bld=b: [w.command_ungarrison(game) for w in list(bld.garrison)])
        elif b.building_type == "barracks":
            ud = UNIT_DEFS["soldier"]
            self._add_button(surf, btn_x, btn_y, btn_w, btn_h, "Train Soldier (W)",
                             lambda: b.start_train("soldier", game),
                             game.resources.can_afford(gold=ud["gold"], steel=ud["steel"]),
                             cost_text=self.unit_cost_str("soldier"))
            ud2 = UNIT_DEFS["archer"]
            self._add_button(surf, btn_x + btn_w + 8, btn_y, btn_w, btn_h, "Train Archer (E)",
                             lambda: b.start_train("archer", game),
                             game.resources.can_afford(gold=ud2["gold"], wood=ud2["wood"], steel=ud2["steel"]),
                             cost_text=self.unit_cost_str("archer"))
        elif b.building_type == "tower" and b.can_upgrade_tower():
            cost = TOWER_UPGRADE_COST
            self._add_button(surf, btn_x, btn_y, btn_w + 20, btn_h, "Upgrade (U)",
                             lambda bld=b, g=game: g.start_tower_upgrade(bld),
                             game.resources.can_afford(steel=cost["steel"]),
                             cost_text=self.cost_str(steel=cost["steel"]))

        # v10.2: helper building upgrade button
        elif b.building_type in UPGRADE_PATH and b.built and not b.ruined and not b.upgrading_to:
            upgrade_type = UPGRADE_PATH[b.building_type]
            upgrade_def = BUILDING_DEFS[upgrade_type]
            upgrade_name = upgrade_type.replace("_", " ").title()
            can_afford = game.resources.can_afford(
                gold=upgrade_def["gold"], stone=upgrade_def.get("stone", 0),
                iron=upgrade_def.get("iron", 0))
            can_expand = b._can_upgrade_at(game)
            self._add_button(surf, btn_x, btn_y, btn_w + 20, btn_h,
                             f"→ {upgrade_name}",
                             lambda: game.start_upgrade(b),
                             can_afford and can_expand,
                             cost_text=self.building_cost_str(upgrade_type))
            if not can_expand and can_afford:
                draw_text(surf, "No space!", btn_x, btn_y + btn_h + 4,
                          self.font_xs, (220, 80, 80))

        # v10.2: production building — station/unstation buttons
        elif b.building_type in PRODUCTION_RATES or b.building_type == "forge":
            if b.stationed_workers:
                n = len(b.stationed_workers)
                pconfig = PRODUCTION_RATES.get(b.building_type, {})
                max_w = pconfig.get("max_workers", 3)
                draw_text(surf, f"Stationed: {n}/{max_w}",
                          btn_x, btn_y + 4, self.font_sm, (220, 180, 80))
                self._add_button(surf, btn_x + btn_w + 8, btn_y, btn_w, btn_h,
                                 "Unstation",
                                 lambda: game.unstation_workers(b))

        # v10.2: smelter boost on refinery
        elif b.building_type == "refinery" and b.built and not b.ruined:
            # check if any player worker has Smelter Foreman rank
            has_smelter = any(
                u.get_skill_rank("smelter") >= 1
                for u in game.player_units
                if u.alive and u.unit_type == "worker")
            if has_smelter:
                label = "Boosted +30%" if b.smelter_boosted else "Boost (+30%)"
                self._add_button(surf, btn_x, btn_y + btn_h + 4, btn_w, btn_h // 2 + 8,
                                 label,
                                 lambda: setattr(b, 'smelter_boosted', not b.smelter_boosted))

    # ------------------------------------------------------------------
    # SINGLE UNIT PANEL (player)
    # ------------------------------------------------------------------
    def _draw_unit_panel(self, surf, py, u, game):
        color = UNIT_COLORS.get(u.unit_type, (150, 150, 150))
        pygame.draw.circle(surf, color, (40, py + 35), 20)
        pygame.draw.circle(surf, COL_GUI_BORDER, (40, py + 35), 20, 1)
        label = UNIT_LABELS.get(u.unit_type, "?")
        draw_text(surf, label, 40, py + 35, self.font_lg, (255, 255, 255), center=True)

        # name + rank
        name = u.unit_type.replace("_", " ").title()
        if u.unit_type != "worker" and u.rank < len(MILITARY_RANKS):
            rank_name = MILITARY_RANKS[u.rank]
            rank_col = RANK_COLORS.get(u.rank, COL_TEXT)
            name += f" [{rank_name}]"
        else:
            rank_col = COL_TEXT
        draw_text(surf, name, 80, py + 8, self.font, rank_col)

        # traits (inline, compact)
        if u.traits:
            trait_names = ", ".join(t.replace("_", " ").title() for t in sorted(u.traits))
            trait_cols = [TRAIT_DISPLAY.get(t, {}).get("color", COL_TEXT) for t in sorted(u.traits)]
            self._draw_clipped(surf, trait_names, 80, py + 22,
                               self.font_xs, trait_cols[0] if trait_cols else COL_TEXT, max_width=240)

        # HP bar (visual, green)
        self._draw_hp_bar(surf, 80, py + 36, 160, 12, u.hp, u.max_hp, (0, 180, 0))

        # stats + state on same line
        state_str = u.state
        if u.state == "fleeing" and u.owner == "player":
            state_str = "fleeing!"
        if u.stance != STANCE_AGGRESSIVE:
            state_str += f" [{STANCE_NAMES[u.stance]}]"
        draw_text(surf, f"ATK: {u.attack_power}  SPD: {u.speed}  |  {state_str}",
                  80, py + 54, self.font_sm, (180, 180, 200))

        # XP bar for military
        if u.unit_type != "worker":
            next_rank = u.rank + 1
            if next_rank < len(RANK_XP_THRESHOLDS):
                current_threshold = RANK_XP_THRESHOLDS[u.rank]
                next_threshold = RANK_XP_THRESHOLDS[next_rank]
                xp_in_rank = u.xp - current_threshold
                xp_needed = next_threshold - current_threshold
                xp_ratio = min(1.0, xp_in_rank / xp_needed) if xp_needed > 0 else 1.0
                bar_x, bar_y = 80, py + 72
                bar_w, bar_h = 120, 6
                pygame.draw.rect(surf, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h))
                fill_col = RANK_COLORS.get(next_rank, (180, 180, 100))
                pygame.draw.rect(surf, fill_col, (bar_x, bar_y, int(bar_w * xp_ratio), bar_h))
                draw_text(surf, f"XP {u.xp}/{next_threshold}",
                          bar_x + bar_w + 6, bar_y - 2, self.font_xs, (140, 140, 160))
            else:
                draw_text(surf, f"XP {u.xp} (MAX)", 80, py + 72, self.font_xs, (255, 215, 0))

        # carrying
        if u.carry_amount > 0:
            carry_colors = {"gold": COL_GOLD, "wood": COL_WOOD, "iron": COL_IRON_C, "stone": COL_STONE}
            cc = carry_colors.get(u.carry_type, COL_GOLD)
            draw_text(surf, f"Carrying {u.carry_amount} {u.carry_type}", 80, py + 84, self.font_sm, cc)

        # worker skill info (compact)
        if u.unit_type == "worker":
            primary_skill, primary_rank = u.get_primary_skill()
            if primary_skill and primary_rank > 0:
                skill_display = WORKER_SKILL_NAMES.get(primary_skill, primary_skill)
                rank_name = WORKER_RANKS[primary_rank]
                bonus = int(WORKER_RANK_SPEED_BONUS.get(primary_rank, 0) * 100)
                sc = WORKER_SKILL_COLORS.get(primary_skill, COL_TEXT)
                draw_text(surf, f"{skill_display} {rank_name} (+{bonus}%)",
                          80, py + 84, self.font_sm, sc)
            # skill XP bars (up to 2, more compact)
            bar_y = py + 100
            active_skills = [(s, u.skill_xp[s], u.skill_ranks[s])
                             for s in u.skill_xp if u.skill_xp[s] > 0]
            active_skills.sort(key=lambda t: (-t[2], -t[1]))
            for skill_name, xp, rank in active_skills[:2]:
                skill_short = WORKER_SKILL_NAMES.get(skill_name, skill_name)[:6]
                sc = WORKER_SKILL_COLORS.get(skill_name, (160, 160, 180))
                draw_text(surf, skill_short, 80, bar_y, self.font_xs, sc)
                bar_x = 130
                bar_w, bar_h = 70, 5
                pygame.draw.rect(surf, (40, 40, 50), (bar_x, bar_y + 3, bar_w, bar_h))
                if rank < len(WORKER_RANK_XP) - 1:
                    cur_thresh = WORKER_RANK_XP[rank]
                    next_thresh = WORKER_RANK_XP[rank + 1]
                    xp_in_rank = xp - cur_thresh
                    xp_needed = next_thresh - cur_thresh
                    ratio = min(1.0, xp_in_rank / xp_needed) if xp_needed > 0 else 1.0
                else:
                    ratio = 1.0
                pygame.draw.rect(surf, sc, (bar_x, bar_y + 3, int(bar_w * ratio), bar_h))
                rank_label = WORKER_RANKS[rank][0]
                draw_text(surf, rank_label, bar_x + bar_w + 4, bar_y, self.font_xs, sc)
                bar_y += 13

        # build buttons for workers
        if u.unit_type == "worker":
            self._draw_build_buttons(surf, py, game)

        # command buttons for combat units
        if u.unit_type in ("soldier", "archer"):
            self._draw_command_buttons(surf, py, game)

    # ------------------------------------------------------------------
    # MULTI UNIT PANEL
    # ------------------------------------------------------------------
    def _draw_multi_unit_panel(self, surf, py, selected, game):
        draw_text(surf, f"{len(selected)} units selected", 20, py + 8, self.font)

        # aggregate HP
        total_hp = sum(u.hp for u in selected)
        total_max = sum(u.max_hp for u in selected)
        self._draw_hp_bar(surf, 20, py + 28, 120, 10, total_hp, total_max, (0, 170, 0))

        # unit type icons with counts
        x = 20
        counts = {}
        rank_counts = {}
        for u in selected:
            counts[u.unit_type] = counts.get(u.unit_type, 0) + 1
            if u.unit_type not in rank_counts:
                rank_counts[u.unit_type] = {}
            rank_counts[u.unit_type][u.rank] = rank_counts[u.unit_type].get(u.rank, 0) + 1
        y = py + 48
        for utype, cnt in counts.items():
            color = UNIT_COLORS.get(utype, (150, 150, 150))
            pygame.draw.circle(surf, color, (x + 10, y + 10), 10)
            pygame.draw.circle(surf, COL_GUI_BORDER, (x + 10, y + 10), 10, 1)
            label = UNIT_LABELS.get(utype, "?")
            draw_text(surf, label, x + 10, y + 10, self.font_sm, (255, 255, 255), center=True)
            rc = rank_counts.get(utype, {})
            ranked = sum(v for r, v in rc.items() if r > 0)
            if ranked > 0:
                rank_parts = []
                for r in sorted(rc.keys()):
                    if r > 0:
                        rank_parts.append(f"{rc[r]}{'*' * r}")
                count_text = f"x{cnt} ({' '.join(rank_parts)})"
            else:
                count_text = f"x{cnt}"
            draw_text(surf, count_text, x + 25, y + 3, self.font_sm)
            x += 90

        # build buttons for all-worker selection
        all_workers = all(u.unit_type == "worker" for u in selected)
        if all_workers:
            self._draw_build_buttons(surf, py, game)

        # command buttons for all-combat selection
        all_combat = all(u.unit_type in ("soldier", "archer") for u in selected)
        if all_combat:
            self._draw_command_buttons(surf, py, game)

    # ------------------------------------------------------------------
    # BUILD BUTTONS
    # ------------------------------------------------------------------
    def _draw_build_buttons(self, surf, py, game):
        btn_x = 400
        btn_y_start = py + 5
        btn_w, btn_h = 140, 38
        bd = BUILDING_DEFS
        self._add_button(surf, btn_x, btn_y_start, btn_w, btn_h, "Town Hall (1)",
                         lambda: game.start_placement("town_hall"),
                         game.resources.can_afford(gold=bd["town_hall"]["gold"], wood=bd["town_hall"]["wood"]),
                         cost_text=self.building_cost_str("town_hall"))
        self._add_button(surf, btn_x + btn_w + 6, btn_y_start, btn_w, btn_h, "Barracks (2)",
                         lambda: game.start_placement("barracks"),
                         game.resources.can_afford(gold=bd["barracks"]["gold"], wood=bd["barracks"]["wood"]),
                         cost_text=self.building_cost_str("barracks"))
        self._add_button(surf, btn_x, btn_y_start + btn_h + 4, btn_w, btn_h, "Refinery (3)",
                         lambda: game.start_placement("refinery"),
                         game.resources.can_afford(gold=bd["refinery"]["gold"], wood=bd["refinery"]["wood"], iron=bd["refinery"]["iron"]),
                         cost_text=self.building_cost_str("refinery"))
        self._add_button(surf, btn_x + btn_w + 6, btn_y_start + btn_h + 4, btn_w, btn_h, "Tower (4)",
                         lambda: game.start_placement("tower"),
                         game.resources.can_afford(gold=bd["tower"]["gold"], iron=bd["tower"].get("iron", 0),
                                                   stone=bd["tower"].get("stone", 0)),
                         cost_text=self.building_cost_str("tower"))

        # v10.2: Foreman helper building buttons (conditional on worker rank)
        foreman_skills = set()
        workers = [u for u in game.selected if isinstance(u, Unit) and u.unit_type == "worker"]
        for w in workers:
            for skill_name in FOREMAN_BUILDINGS:
                if w.get_skill_rank(skill_name) >= 1:  # Foreman+
                    foreman_skills.add(skill_name)
        if foreman_skills:
            row3_y = btn_y_start + 2 * (btn_h + 4)
            fx = btn_x
            for skill_name in sorted(foreman_skills):
                btype = FOREMAN_BUILDINGS[skill_name]
                bd_new = BUILDING_DEFS[btype]
                can_afford = game.resources.can_afford(
                    gold=bd_new["gold"], wood=bd_new["wood"],
                    stone=bd_new.get("stone", 0))
                label = btype.replace("_", " ").title()
                self._add_button(surf, fx, row3_y, btn_w, btn_h, label,
                                 lambda bt=btype: game.start_placement(bt),
                                 can_afford,
                                 cost_text=self.building_cost_str(btype))
                fx += btn_w + 6
                if fx + btn_w > SCREEN_WIDTH - 20:
                    fx = btn_x
                    row3_y += btn_h + 4

    # ------------------------------------------------------------------
    # COMMAND BUTTONS (soldiers / archers)
    # ------------------------------------------------------------------
    def _draw_global_buttons(self, surf, py, game):
        btn_w, btn_h = 140, 38
        btn_y = py + 10
        gap = 8
        # center 4 buttons
        total_w = 4 * btn_w + 3 * gap
        btn_x = (SCREEN_WIDTH - total_w) // 2

        self._add_button(surf, btn_x, btn_y, btn_w, btn_h,
                         "Defend Base", lambda: game.global_defend())

        self._add_button(surf, btn_x + btn_w + gap, btn_y, btn_w, btn_h,
                         "Hunt Enemies", lambda: game.global_attack())

        # Town Bell — costs resources
        gc = GARRISON_COST
        can_bell = game.resources.can_afford(wood=gc["wood"], iron=gc["iron"], stone=gc["stone"])
        cost_str = f"{gc['wood']}W {gc['iron']}I {gc['stone']}S"
        self._add_button(surf, btn_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h,
                         "Town Bell", lambda: game.global_bell(),
                         enabled=can_bell, cost_text=cost_str)

        self._add_button(surf, btn_x + 3 * (btn_w + gap), btn_y, btn_w, btn_h,
                         "Resume Work", lambda: game.global_resume())

        # help text below
        draw_text(surf, "Click to select  |  Right-click to command  |  1-4: Build  |  Q/W/E: Train",
                  20, py + 60, self.font_xs, (70, 70, 90))

    # ------------------------------------------------------------------
    def _draw_command_buttons(self, surf, py, game):
        btn_x = 400
        btn_y_start = py + 5
        btn_w, btn_h = 140, 38

        combat_sel = [e for e in game.selected
                      if hasattr(e, 'unit_type') and e.unit_type in ("soldier", "archer")]

        self._add_button(surf, btn_x, btn_y_start, btn_w, btn_h, "Attack Move",
                         lambda: setattr(game, 'attack_move_mode', True))

        # Stance cycle button
        if combat_sel:
            cur_stance = combat_sel[0].stance
            stance_label = STANCE_NAMES[cur_stance]
            self._add_button(surf, btn_x + btn_w + 6, btn_y_start, btn_w, btn_h, stance_label,
                             lambda: self._cycle_stance(game))

            # Formation row: F1-F4 buttons
            fmt_y = btn_y_start + btn_h + 4
            fmt_w = 68
            squad = game.player_squad_mgr.get_squad(combat_sel[0])
            cur_fmt = squad.formation if squad else 0
            for i, fname in enumerate(FORMATION_NAMES):
                fx = btn_x + i * (fmt_w + 4)
                label = f"F{i+1}:{fname}"
                is_active = (i == cur_fmt)
                def _set_fmt(idx=i):
                    self._set_formation(game, idx)
                self._add_button(surf, fx, fmt_y, fmt_w, 28, label, _set_fmt,
                                 enabled=True)
                if is_active:
                    pygame.draw.rect(surf, (180, 220, 255),
                                     (fx, fmt_y, fmt_w, 28), 2)

    def _cycle_stance(self, game):
        for e in game.selected:
            if hasattr(e, 'unit_type') and e.unit_type in ("soldier", "archer"):
                next_stance = (e.stance + 1) % 4
                e.command_set_stance(next_stance)
                squad_mgr = game.player_squad_mgr
                squad_mgr.set_stance(e, next_stance)

    def _set_formation(self, game, fmt_idx):
        for e in game.selected:
            if hasattr(e, 'unit_type') and e.unit_type in ("soldier", "archer"):
                game.player_squad_mgr.set_formation(e, fmt_idx)

    # ------------------------------------------------------------------
    # BUTTONS
    # ------------------------------------------------------------------
    def _add_button(self, surf, x, y, w, h, label, callback, enabled=True, cost_text=None):
        rect = pygame.Rect(x, y, w, h)
        mx, my = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mx, my)
        if enabled:
            color = COL_BTN_HOVER if hovered else COL_BTN
        else:
            color = COL_BTN_DISABLED
        pygame.draw.rect(surf, color, rect, border_radius=4)
        pygame.draw.rect(surf, COL_GUI_BORDER, rect, 1, border_radius=4)
        text_col = COL_BTN_TEXT if enabled else (80, 80, 90)

        if cost_text:
            draw_text(surf, label, x + w // 2, y + h // 2 - 7, self.font_sm, text_col, center=True)
            cost_col = (180, 180, 100) if enabled else (70, 70, 60)
            draw_text(surf, cost_text, x + w // 2, y + h // 2 + 9, self.font_xs, cost_col, center=True)
        else:
            draw_text(surf, label, x + w // 2, y + h // 2, self.font_sm, text_col, center=True)

        self.buttons.append((rect, label, callback, enabled))

    def handle_click(self, pos):
        for rect, label, callback, enabled in self.buttons:
            if rect.collidepoint(pos) and enabled:
                callback()
                return True
        return False
