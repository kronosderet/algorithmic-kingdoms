import pygame
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, TOP_BAR_H, BOTTOM_PANEL_H,
                       UNIT_DEFS, BUILDING_DEFS, UNIT_COLORS, UNIT_LABELS,
                       ENEMY_COLORS, ENEMY_DEFS,
                       BUILDING_COLORS, BUILDING_LABELS, display_name,
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
                       FORMATION_POLAR_ROSE, FORMATION_GOLDEN_SPIRAL,
                       FORMATION_SIERPINSKI, FORMATION_KOCH,
                       FORMATION_NAMES,
                       RESONANCE_COLORS,
                       DISCOVERY_HINTS,
                       TOOLTIP_DATA, TOOLTIP_HOVER_DELAY, TOOLTIP_MAX_WIDTH,
                       TOOLTIP_BG, TOOLTIP_BORDER, TOOLTIP_PADDING,
                       MSG_LOG_FADE, GAME_AREA_Y, GAME_AREA_H)
from utils import draw_text, ruin_rebuild_cost
from entities import Building, Unit


class GUI:
    def __init__(self):
        # Fonts initialized lazily by init_fonts() before first draw
        self.font: pygame.font.Font = None  # type: ignore[assignment]
        self.font_sm: pygame.font.Font = None  # type: ignore[assignment]
        self.font_xs: pygame.font.Font = None  # type: ignore[assignment]
        self.font_lg: pygame.font.Font = None  # type: ignore[assignment]
        self.buttons = []  # list of (rect, label, callback, enabled)
        # Tooltip state
        self._tooltip_zones = []  # list of (rect, tooltip_key) — rebuilt each frame
        self._hover_key = None    # currently hovered tooltip key
        self._hover_time = 0.0    # seconds spent hovering on current key
        self._last_mx = 0
        self._last_my = 0

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

    def _register_tooltip(self, rect, key):
        """Register a rectangular zone with a tooltip key for this frame."""
        self._tooltip_zones.append((rect, key))

    def update_tooltip(self, dt):
        """Call once per frame to track hover timing."""
        mx, my = pygame.mouse.get_pos()
        # Check if mouse moved significantly (reset timer on large movement)
        if abs(mx - self._last_mx) > 3 or abs(my - self._last_my) > 3:
            self._hover_time = 0.0
        self._last_mx, self._last_my = mx, my

        # Find which tooltip zone the mouse is in
        current_key = None
        for rect, key in self._tooltip_zones:
            if rect.collidepoint(mx, my):
                current_key = key
                break

        if current_key != self._hover_key:
            self._hover_key = current_key
            self._hover_time = 0.0
        elif current_key is not None:
            self._hover_time += dt

        # Clear zones for next frame
        self._tooltip_zones.clear()

    def draw_tooltip(self, surf):
        """Render the active tooltip card if hover delay is met."""
        if self._hover_key is None or self._hover_time < TOOLTIP_HOVER_DELAY:
            return
        text = TOOLTIP_DATA.get(self._hover_key)
        if not text:
            return

        mx, my = self._last_mx, self._last_my
        lines = text.split("\n")
        font = self.font_xs
        if not font:
            return

        # Measure text
        line_h = font.get_height() + 2
        pad = TOOLTIP_PADDING
        max_w = 0
        for line in lines:
            w = font.size(line)[0]
            if w > max_w:
                max_w = w
        card_w = min(max_w + pad * 2, TOOLTIP_MAX_WIDTH + pad * 2)
        card_h = len(lines) * line_h + pad * 2

        # Position: prefer below-right of cursor, clamp to screen
        tx = mx + 14
        ty = my + 18
        if tx + card_w > SCREEN_WIDTH - 4:
            tx = mx - card_w - 4
        if ty + card_h > SCREEN_HEIGHT - 4:
            ty = my - card_h - 4

        # Draw card background (with alpha via surface)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill(TOOLTIP_BG)
        surf.blit(card_surf, (tx, ty))
        pygame.draw.rect(surf, TOOLTIP_BORDER, (tx, ty, card_w, card_h), 1, border_radius=3)

        # Draw text lines
        # First line is title (brighter), rest are description
        for i, line in enumerate(lines):
            col = (240, 240, 250) if i == 0 else (180, 180, 195)
            draw_text(surf, line, tx + pad, ty + pad + i * line_h, font, col)

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
            self._register_tooltip(pygame.Rect(x, 2, 76, 36), f"res_{res_type}")
            x += 80

        # --- Separator ---
        sep_x = x + 8
        pygame.draw.line(surf, COL_GUI_BORDER, (sep_x, 6), (sep_x, 34))

        # --- Population (compact) ---
        pop = len(player_units)
        pop_x = sep_x + 12
        draw_text(surf, f"Pop {pop}", pop_x, 12, self.font, (180, 200, 255))
        self._register_tooltip(pygame.Rect(pop_x, 4, 60, 30), "pop")

        # --- v10_9: Tension meter + incident state (right side) ---
        tension_x = SCREEN_WIDTH - 380
        pygame.draw.line(surf, COL_GUI_BORDER, (tension_x - 12, 6), (tension_x - 12, 34))

        # Incident counter
        inc_str = f"{enemy_ai.incident_number}/{enemy_ai.incidents_required}"
        draw_text(surf, inc_str, tension_x, 4, self.font_sm, COL_TEXT)
        self._register_tooltip(pygame.Rect(tension_x, 2, 48, 18), "incident_counter")

        # Tension bar (120px wide)
        bar_x = tension_x + 50
        bar_y = 6
        bar_w = 120
        bar_h = 12
        t = max(0.0, min(1.0, enemy_ai.tension))
        pygame.draw.rect(surf, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h))
        # Color gradient: blue → amber → red
        if t < 0.5:
            r = int(60 + t * 2 * 180)
            g = int(120 + t * 2 * 60)
            b = int(200 - t * 2 * 150)
        else:
            r = int(240)
            g = int(180 - (t - 0.5) * 2 * 150)
            b = int(50 - (t - 0.5) * 2 * 50)
        bar_col = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        fill_w = max(1, int(bar_w * t))
        if t > 0.01:
            pygame.draw.rect(surf, bar_col, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surf, COL_GUI_BORDER, (bar_x, bar_y, bar_w, bar_h), 1)
        self._register_tooltip(pygame.Rect(bar_x, bar_y, bar_w, bar_h), "tension_bar")

        # State text (narrative)
        state_text = getattr(enemy_ai, 'narrative_text', "Calm")
        # Color by FSM state
        state_colors = {
            "calm": (120, 160, 200),
            "foreboding": (200, 180, 80),
            "imminent": (255, 100, 50),
            "active": (255, 60, 60),
            "aftermath": (150, 200, 150),
        }
        state_col = state_colors.get(enemy_ai.state, COL_TEXT)
        draw_text(surf, state_text, bar_x, bar_y + bar_h + 2, self.font_xs, state_col)

    # ------------------------------------------------------------------
    # BOTTOM PANEL
    # ------------------------------------------------------------------
    def draw_bottom_panel(self, surf, selected, game, inspected_enemy=None):
        py = SCREEN_HEIGHT - BOTTOM_PANEL_H
        pygame.draw.rect(surf, COL_GUI_BG, (0, py, SCREEN_WIDTH, BOTTOM_PANEL_H))
        pygame.draw.line(surf, COL_GUI_BORDER, (0, py), (SCREEN_WIDTH, py))

        self.buttons.clear()

        # v10_8d: Squad bar only shows once squads have been discovered
        unlocks = game.unlocks
        if unlocks["has_squad"] or unlocks["has_barracks"]:
            squad_bar_h = 25
            self._draw_squad_bar(surf, py, squad_bar_h, game)
            context_py = py + squad_bar_h
        else:
            context_py = py

        # message log mini-panel (always visible, right side)
        self._draw_message_log_mini(surf, py, game)

        # v10_2: inspected enemy takes priority when nothing player-selected
        if not selected and inspected_enemy:
            self._draw_enemy_panel(surf, context_py, inspected_enemy)
            return

        if not selected:
            self._draw_global_buttons(surf, context_py, game)
            return

        entity = selected[0]

        # info section
        if isinstance(entity, Building):
            self._draw_building_panel(surf, context_py, entity, game)
        elif isinstance(entity, Unit):
            if len(selected) > 1:
                self._draw_multi_unit_panel(surf, context_py, selected, game)
            else:
                self._draw_unit_panel(surf, context_py, entity, game)

    # ------------------------------------------------------------------
    # v10_8: SQUAD BAR — horizontal strip showing all player squads
    # ------------------------------------------------------------------
    def _draw_squad_bar(self, surf, py, h, game):
        """Draw squad cards as a horizontal strip at top of bottom panel."""
        pygame.draw.rect(surf, (25, 25, 35), (0, py, SCREEN_WIDTH, h))
        pygame.draw.line(surf, (50, 50, 60), (0, py + h), (SCREEN_WIDTH, py + h))

        squads = [s for s in game.player_squad_mgr.squad_list if s.alive_count > 0]
        if not squads:
            draw_text(surf, "No squads (train Rank 1+ units to form squads)",
                      10, py + 6, self.font_xs, (80, 80, 100))
            return

        # Determine which squads are selected
        selected_squad_ids = set()
        for e in game.selected:
            if isinstance(e, Unit):
                sq = game.player_squad_mgr.get_squad(e)
                if sq:
                    selected_squad_ids.add(sq.squad_id)

        card_w = 80
        card_h = h - 4
        gap = 4
        x = 6
        for i, squad in enumerate(squads):
            is_sel = squad.squad_id in selected_squad_ids
            fmt = squad.formation
            res_color = RESONANCE_COLORS.get(fmt, (100, 100, 100))

            # card background
            bg = (50, 50, 65) if is_sel else (35, 35, 45)
            card_rect = pygame.Rect(x, py + 2, card_w, card_h)
            pygame.draw.rect(surf, bg, card_rect, border_radius=3)

            # border: bright if selected, dim if not
            border_col = res_color if is_sel else (60, 60, 70)
            pygame.draw.rect(surf, border_col, card_rect, 1 if not is_sel else 2, border_radius=3)

            # content: [index] formation_name count
            idx_label = str(i + 1)
            fname = FORMATION_NAMES[fmt][:4]  # Rose, Spir, Sier, Koch
            cnt = squad.alive_count
            draw_text(surf, idx_label, x + 3, py + 5, self.font_xs, (200, 200, 220))
            draw_text(surf, fname, x + 14, py + 5, self.font_xs, res_color)
            draw_text(surf, f"x{cnt}", x + card_w - 18, py + 5, self.font_xs, (160, 160, 180))

            # clickable: select this squad
            def _click_squad(sq=squad):
                shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
                if not shift:
                    for ee in game.selected:
                        ee.selected = False
                    game.selected.clear()
                for m in sq.members:
                    if m.alive and m not in game.selected:
                        m.selected = True
                        game.selected.append(m)
            self.buttons.append((card_rect, f"S{i+1}", _click_squad, True))

            x += card_w + gap
            if x + card_w > SCREEN_WIDTH - 10:
                break  # overflow protection

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
        self._register_tooltip(pygame.Rect(20, py + 20, 40, 40), f"enemy_{e.unit_type}")

        # "ENEMY" tag
        draw_text(surf, "ENEMY", 80, py + 8, self.font_xs, (255, 80, 80))

        # name + rank
        name = display_name(e.unit_type)
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

        # v10_8: dissonance tag
        dis_fmt = getattr(e, 'dissonant_formation', -1)
        if dis_fmt >= 0:
            from constants import RESONANCE_DISSONANCE_COLORS
            fmt_names = {0: "Rose", 1: "Spiral", 2: "Sierpinski", 3: "Koch"}
            dis_col = RESONANCE_DISSONANCE_COLORS.get(dis_fmt, (150, 50, 50))
            draw_text(surf, f"Dissonant (anti-{fmt_names.get(dis_fmt, '?')})",
                      80, ability_y + 14, self.font_xs, dis_col)

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
        self._register_tooltip(pygame.Rect(15, py + 10, 50, 50), f"bld_{b.building_type}")

        # name
        name = display_name(b.building_type)
        if b.ruined:
            name += " (RUINS)"
        elif b.building_type == "tower" and b.built:
            if b.tower_level >= 2:
                name = "Arc Sentinel (Lv.2)"
            else:
                name = "Sentinel (Lv.1)"
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
            unit_name = display_name(b.train_queue[0])
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
            self._add_button(surf, btn_x, btn_y, btn_w, btn_h, "Train Gatherer (Q)",
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
            self._add_button(surf, btn_x, btn_y, btn_w, btn_h, "Train Warden (T)",
                             lambda: b.start_train("soldier", game),
                             game.resources.can_afford(gold=ud["gold"], steel=ud["steel"]),
                             cost_text=self.unit_cost_str("soldier"))
            ud2 = UNIT_DEFS["archer"]
            self._add_button(surf, btn_x + btn_w + 8, btn_y, btn_w, btn_h, "Train Ranger (E)",
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
            upgrade_name = display_name(upgrade_type)
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
    # SINGLE UNIT PANEL (player) — v10_8c rework
    # ------------------------------------------------------------------
    def _draw_unit_panel(self, surf, py, u, game):
        import math as _m
        color = UNIT_COLORS.get(u.unit_type, (150, 150, 150))
        cx, cy = 40, py + 42
        portrait_r = 24

        # HP arc around portrait (green arc proportional to HP %)
        hp_ratio = u.hp / u.max_hp if u.max_hp > 0 else 0
        # dark bg arc
        pygame.draw.circle(surf, (30, 30, 40), (cx, cy), portrait_r + 3, 3)
        # HP arc: draw as thick arc segments
        if hp_ratio > 0:
            hp_col = (0, 200, 50) if hp_ratio > 0.5 else (220, 180, 0) if hp_ratio > 0.25 else (220, 50, 50)
            arc_r = portrait_r + 3
            segments = int(24 * hp_ratio)
            for i in range(segments):
                angle = -_m.pi / 2 + (2 * _m.pi * i / 24)
                ax = cx + int(arc_r * _m.cos(angle))
                ay = cy + int(arc_r * _m.sin(angle))
                pygame.draw.circle(surf, hp_col, (ax, ay), 2)

        # portrait fill
        pygame.draw.circle(surf, color, (cx, cy), portrait_r)
        pygame.draw.circle(surf, COL_GUI_BORDER, (cx, cy), portrait_r, 1)
        label = UNIT_LABELS.get(u.unit_type, "?")
        draw_text(surf, label, cx, cy, self.font_lg, (255, 255, 255), center=True)
        self._register_tooltip(pygame.Rect(cx - portrait_r, cy - portrait_r,
                               portrait_r * 2, portrait_r * 2), f"unit_{u.unit_type}")

        # rank stars below portrait
        if u.unit_type != "worker" and u.rank > 0:
            rank_col = RANK_COLORS.get(u.rank, (180, 180, 100))
            star_y = cy + portrait_r + 6
            for i in range(min(u.rank, 5)):
                sx = cx - (min(u.rank, 5) - 1) * 5 + i * 10
                pygame.draw.polygon(surf, rank_col, [
                    (sx, star_y - 4), (sx + 2, star_y - 1),
                    (sx + 5, star_y - 1), (sx + 3, star_y + 1),
                    (sx + 4, star_y + 4), (sx, star_y + 2),
                    (sx - 4, star_y + 4), (sx - 3, star_y + 1),
                    (sx - 5, star_y - 1), (sx - 2, star_y - 1),
                ])

        # === INFO COLUMN (75-360) ===
        ix = 78

        # Row 1: Name + rank badge
        name = display_name(u.unit_type)
        rank_col = COL_TEXT
        if u.unit_type != "worker" and u.rank < len(MILITARY_RANKS):
            rank_name = MILITARY_RANKS[u.rank]
            rank_col = RANK_COLORS.get(u.rank, COL_TEXT)
            draw_text(surf, name, ix, py + 4, self.font, rank_col)
            # rank badge
            badge_x = ix + self.font.size(name)[0] + 6
            badge_w = self.font_xs.size(rank_name)[0] + 8
            pygame.draw.rect(surf, rank_col, (badge_x, py + 5, badge_w, 14), border_radius=3)
            draw_text(surf, rank_name, badge_x + 4, py + 5, self.font_xs, (10, 10, 10))
            self._register_tooltip(pygame.Rect(badge_x, py + 5, badge_w, 14), f"rank_{u.rank}")
        elif u.unit_type == "worker":
            draw_text(surf, name, ix, py + 4, self.font, COL_TEXT)
            # worker specialty badge
            primary_skill, primary_rank = u.get_primary_skill()
            if primary_skill and primary_rank > 0:
                sc = WORKER_SKILL_COLORS.get(primary_skill, COL_TEXT)
                skill_display = WORKER_SKILL_NAMES.get(primary_skill, primary_skill)
                rank_name = WORKER_RANKS[primary_rank]
                badge_text = f"{skill_display} {rank_name}"
                badge_x = ix + self.font.size(name)[0] + 6
                badge_w = self.font_xs.size(badge_text)[0] + 8
                pygame.draw.rect(surf, (*sc, 180), (badge_x, py + 5, badge_w, 14), border_radius=3)
                draw_text(surf, badge_text, badge_x + 4, py + 5, self.font_xs, (255, 255, 255))
                self._register_tooltip(pygame.Rect(badge_x, py + 5, badge_w, 14), f"wrank_{rank_name}")
        else:
            draw_text(surf, name, ix, py + 4, self.font, rank_col)

        # Row 2: Trait dots (colored circles with tooltip-like labels)
        if u.traits:
            tx = ix
            for t in sorted(u.traits):
                td = TRAIT_DISPLAY.get(t, {})
                tc = td.get("color", (140, 140, 140))
                pygame.draw.circle(surf, tc, (tx + 5, py + 24), 4)
                trait_label = t.replace("_", " ").title()[:8]
                draw_text(surf, trait_label, tx + 12, py + 19, self.font_xs, tc)
                tw = self.font_xs.size(trait_label)[0] + 18
                self._register_tooltip(pygame.Rect(tx, py + 17, tw, 14), f"trait_{t}")
                tx += tw
                if tx > 340:
                    break

        # Row 3: HP bar (wider, with number overlay)
        hp_bar_x, hp_bar_y = ix, py + 33
        hp_bar_w, hp_bar_h = 200, 10
        pygame.draw.rect(surf, (30, 30, 40), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=2)
        hp_col = (0, 200, 50) if hp_ratio > 0.5 else (220, 180, 0) if hp_ratio > 0.25 else (220, 50, 50)
        fill_w = int(hp_bar_w * hp_ratio)
        if fill_w > 0:
            pygame.draw.rect(surf, hp_col, (hp_bar_x, hp_bar_y, fill_w, hp_bar_h), border_radius=2)
        draw_text(surf, f"{int(u.hp)}/{int(u.max_hp)}", hp_bar_x + hp_bar_w + 6, hp_bar_y - 1, self.font_xs, hp_col)

        # Row 4: Stats line with state indicator
        state_str = u.state
        state_col = (120, 200, 120)  # green = normal
        if u.state == "fleeing":
            state_str = "FLEEING"
            state_col = (255, 80, 80)
        elif u.state == "attacking":
            state_str = "FIGHTING"
            state_col = (255, 160, 60)
        elif u.state == "gathering":
            state_str = "MINING"
            state_col = (200, 180, 80)
        elif u.state == "returning":
            state_str = "HAULING"
            state_col = (100, 180, 220)
        elif u.state == "building":
            state_str = "BUILDING"
            state_col = (100, 200, 255)
        elif u.state == "idle":
            state_str = "IDLE"
            state_col = (100, 100, 130)
        elif u.state == "moving":
            state_str = "MOVING"
            state_col = (160, 160, 200)

        # state tag (rounded rect)
        tag_w = self.font_xs.size(state_str)[0] + 8
        pygame.draw.rect(surf, (*state_col[:3], 60), (ix, py + 47, tag_w, 14), border_radius=3)
        pygame.draw.rect(surf, state_col, (ix, py + 47, tag_w, 14), 1, border_radius=3)
        draw_text(surf, state_str, ix + 4, py + 48, self.font_xs, state_col)

        # stats after state tag
        stat_x = ix + tag_w + 8
        if u.stance != STANCE_AGGRESSIVE:
            stance_col = STANCE_COLORS.get(u.stance, (180, 220, 255))
            stance_name = STANCE_NAMES[u.stance]
            draw_text(surf, stance_name, stat_x, py + 48, self.font_xs, stance_col)
            stat_x += self.font_xs.size(stance_name)[0] + 8
        draw_text(surf, f"ATK:{u.attack_power}  SPD:{u.speed}", stat_x, py + 48, self.font_xs, (150, 150, 170))

        # Row 5: XP / Carrying / Skills
        row5_y = py + 65

        if u.unit_type != "worker":
            # XP progress bar (thin, under stats)
            next_rank = u.rank + 1
            if next_rank < len(RANK_XP_THRESHOLDS):
                current_threshold = RANK_XP_THRESHOLDS[u.rank]
                next_threshold = RANK_XP_THRESHOLDS[next_rank]
                xp_in_rank = u.xp - current_threshold
                xp_needed = next_threshold - current_threshold
                xp_ratio = min(1.0, xp_in_rank / xp_needed) if xp_needed > 0 else 1.0
                fill_col = RANK_COLORS.get(next_rank, (180, 180, 100))
                pygame.draw.rect(surf, (40, 40, 50), (ix, row5_y, 160, 5), border_radius=2)
                pygame.draw.rect(surf, fill_col, (ix, row5_y, int(160 * xp_ratio), 5), border_radius=2)
                draw_text(surf, f"XP {u.xp}/{next_threshold}", ix + 166, row5_y - 2,
                          self.font_xs, (140, 140, 160))
            else:
                draw_text(surf, "MAX RANK", ix, row5_y - 2, self.font_xs, (255, 215, 0))

        elif u.unit_type == "worker":
            # Carrying indicator (colored resource icon + amount)
            carry_colors = {"gold": COL_GOLD, "wood": COL_WOOD, "iron": COL_IRON_C, "stone": COL_STONE}
            if u.carry_amount > 0:
                cc = carry_colors.get(u.carry_type, COL_GOLD)
                pygame.draw.rect(surf, cc, (ix, row5_y, 8, 8), border_radius=2)
                draw_text(surf, f"{u.carry_amount} {u.carry_type}", ix + 12, row5_y - 1, self.font_xs, cc)

            # skill XP inline badges
            active_skills = [(s, u.skill_xp[s], u.skill_ranks[s])
                             for s in u.skill_xp if u.skill_xp[s] > 0]
            active_skills.sort(key=lambda t: (-t[2], -t[1]))
            skill_x = ix + (100 if u.carry_amount > 0 else 0)
            for skill_name, xp, rank in active_skills[:3]:
                sc = WORKER_SKILL_COLORS.get(skill_name, (160, 160, 180))
                skill_short = str(WORKER_SKILL_NAMES.get(skill_name, skill_name))[:4]
                rank_label = WORKER_RANKS[rank][0]
                badge_text = f"{skill_short}:{rank_label}"
                bw = self.font_xs.size(badge_text)[0] + 6
                # mini XP bar behind badge
                if rank < len(WORKER_RANK_XP) - 1:
                    cur_thresh = WORKER_RANK_XP[rank]
                    next_thresh = WORKER_RANK_XP[rank + 1]
                    xp_in_rank = xp - cur_thresh
                    xp_needed = next_thresh - cur_thresh
                    ratio = min(1.0, xp_in_rank / xp_needed) if xp_needed > 0 else 1.0
                else:
                    ratio = 1.0
                pygame.draw.rect(surf, (30, 30, 40), (skill_x, row5_y, bw, 12), border_radius=2)
                pygame.draw.rect(surf, (*sc[:3], 80), (skill_x, row5_y, int(bw * ratio), 12), border_radius=2)
                draw_text(surf, badge_text, skill_x + 3, row5_y, self.font_xs, sc)
                skill_x += bw + 4
                if skill_x > 340:
                    break

        # Row 6: Gather hint for idle workers
        if u.unit_type == "worker" and u.state == "idle":
            draw_text(surf, "RClick resource or use gather buttons →", ix, py + 80,
                      self.font_xs, (100, 100, 130))

        # === ACTION COLUMN (right side) ===
        if u.unit_type == "worker":
            self._draw_worker_action_buttons(surf, py, game)
        elif u.unit_type in ("soldier", "archer"):
            self._draw_command_buttons(surf, py, game)

    # ------------------------------------------------------------------
    # WORKER ACTION BUTTONS — v10_8c: build + gather in one panel
    # ------------------------------------------------------------------
    def _draw_worker_action_buttons(self, surf, py, game):
        """v10_8d: Build buttons + gather — progressively revealed."""
        btn_x = 400
        btn_y_start = py + 2
        btn_w, btn_h = 105, 28
        bd = BUILDING_DEFS
        unlocks = game.unlocks

        # Tree of Life: always visible (core building)
        self._add_button(surf, btn_x, btn_y_start, btn_w, btn_h, "Tree of Life(1)",
                         lambda: game.start_placement("town_hall"),
                         game.resources.can_afford(gold=bd["town_hall"]["gold"], wood=bd["town_hall"]["wood"]),
                         cost_text=self.building_cost_str("town_hall"))

        # War Nexus: visible after first wave or ~60s of play (player needs army)
        if unlocks["first_wave_cleared"] or game.game_time > 60:
            self._add_button(surf, btn_x + btn_w + 4, btn_y_start, btn_w, btn_h, "War Nexus(2)",
                             lambda: game.start_placement("barracks"),
                             game.resources.can_afford(gold=bd["barracks"]["gold"], wood=bd["barracks"]["wood"]),
                             cost_text=self.building_cost_str("barracks"))
        else:
            # teaser: locked button with hint
            self._draw_locked_button(surf, btn_x + btn_w + 4, btn_y_start, btn_w, btn_h,
                                     "???", "Survive first wave")

        # Build row 2
        r2y = btn_y_start + btn_h + 2

        # Crucible: visible after iron is discovered
        if unlocks["has_iron"]:
            self._add_button(surf, btn_x, r2y, btn_w, btn_h, "Crucible(3)",
                             lambda: game.start_placement("refinery"),
                             game.resources.can_afford(gold=bd["refinery"]["gold"], wood=bd["refinery"]["wood"], iron=bd["refinery"]["iron"]),
                             cost_text=self.building_cost_str("refinery"))
        elif game.game_time > 30:
            self._draw_locked_button(surf, btn_x, r2y, btn_w, btn_h, "???", "Mine Iron")

        # Sentinel: visible after barracks built
        if unlocks["has_barracks"]:
            self._add_button(surf, btn_x + btn_w + 4, r2y, btn_w, btn_h, "Sentinel(4)",
                             lambda: game.start_placement("tower"),
                             game.resources.can_afford(gold=bd["tower"]["gold"], iron=bd["tower"].get("iron", 0),
                                                       stone=bd["tower"].get("stone", 0)),
                             cost_text=self.building_cost_str("tower"))
        elif unlocks["has_iron"]:
            self._draw_locked_button(surf, btn_x + btn_w + 4, r2y, btn_w, btn_h, "???", "Build Barracks")

        # Gather row: 4 resource-colored buttons
        r3y = r2y + btn_h + 4
        gather_w = 52
        res_defs = [
            ("wood",  COL_WOOD,   "Wood"),
            ("gold",  COL_GOLD,   "Gold"),
            ("iron",  COL_IRON_C, "Iron"),
            ("stone", COL_STONE,  "Stone"),
        ]
        for i, (rtype, rcol, rlabel) in enumerate(res_defs):
            gx = btn_x + i * (gather_w + 3)
            self._add_button(surf, gx, r3y, gather_w, 22, rlabel,
                             lambda rt=rtype: game.command_gather_nearest_selected(rt))
            # colored underline
            pygame.draw.line(surf, rcol, (gx + 2, r3y + 21), (gx + gather_w - 2, r3y + 21), 2)
        draw_text(surf, "Gather:", btn_x - 45, r3y + 4, self.font_xs, (120, 120, 140))

        # Foreman buildings (if applicable)
        foreman_skills = set()
        workers = [u for u in game.selected if isinstance(u, Unit) and u.unit_type == "worker"]
        for w in workers:
            for skill_name in FOREMAN_BUILDINGS:
                if w.get_skill_rank(skill_name) >= 1:
                    foreman_skills.add(skill_name)
        if foreman_skills:
            r4y = r3y + 26
            fx = btn_x
            for skill_name in sorted(foreman_skills):
                btype = FOREMAN_BUILDINGS[skill_name]
                bd_new = BUILDING_DEFS[btype]
                can_afford = game.resources.can_afford(
                    gold=bd_new["gold"], wood=bd_new["wood"],
                    stone=bd_new.get("stone", 0))
                blabel = display_name(btype)
                self._add_button(surf, fx, r4y, btn_w, btn_h, blabel,
                                 lambda bt=btype: game.start_placement(bt),
                                 can_afford,
                                 cost_text=self.building_cost_str(btype))
                fx += btn_w + 4
                if fx + btn_w > SCREEN_WIDTH - 20:
                    fx = btn_x
                    r4y += btn_h + 2

    # ------------------------------------------------------------------
    # MULTI UNIT PANEL — v10_8c rework
    # ------------------------------------------------------------------
    def _draw_multi_unit_panel(self, surf, py, selected, game):
        # Group by type
        by_type = {}
        for u in selected:
            by_type.setdefault(u.unit_type, []).append(u)

        # Total count header
        draw_text(surf, f"{len(selected)} units", 20, py + 4, self.font, COL_TEXT)

        # Aggregate HP bar
        total_hp = sum(u.hp for u in selected)
        total_max = sum(u.max_hp for u in selected)
        hp_ratio = total_hp / total_max if total_max > 0 else 0
        hp_col = (0, 200, 50) if hp_ratio > 0.5 else (220, 180, 0) if hp_ratio > 0.25 else (220, 50, 50)
        self._draw_hp_bar(surf, 100, py + 7, 100, 8, total_hp, total_max, hp_col)
        draw_text(surf, f"{int(hp_ratio * 100)}%", 206, py + 4, self.font_xs, hp_col)

        # Type cards — each gets a mini row with icon, count, state breakdown bar
        card_y = py + 20
        state_colors = {
            "idle": (80, 80, 100), "moving": (100, 100, 180), "gathering": (200, 180, 60),
            "returning": (80, 160, 200), "attacking": (220, 100, 60), "fleeing": (255, 50, 50),
            "building": (80, 200, 255),
        }
        for utype in ["worker", "soldier", "archer"]:
            units = by_type.get(utype, [])
            if not units:
                continue
            color = UNIT_COLORS.get(utype, (150, 150, 150))
            cnt = len(units)

            # icon circle
            pygame.draw.circle(surf, color, (30, card_y + 8), 8)
            label = UNIT_LABELS.get(utype, "?")
            draw_text(surf, label, 30, card_y + 8, self.font_xs, (255, 255, 255), center=True)

            # count + rank summary
            rank_counts = {}
            for u in units:
                rank_counts[u.rank] = rank_counts.get(u.rank, 0) + 1
            ranked = sum(v for r, v in rank_counts.items() if r > 0)
            if ranked > 0:
                parts = [f"{v}{'*' * r}" for r, v in sorted(rank_counts.items()) if r > 0]
                count_text = f"x{cnt} ({' '.join(parts)})"
            else:
                count_text = f"x{cnt}"
            draw_text(surf, count_text, 42, card_y + 2, self.font_xs, COL_TEXT)

            # state distribution bar (stacked horizontal)
            bar_x, bar_w, bar_h = 120, 100, 6
            states = {}
            for u in units:
                states[u.state] = states.get(u.state, 0) + 1
            pygame.draw.rect(surf, (30, 30, 40), (bar_x, card_y + 10, bar_w, bar_h), border_radius=2)
            bx = bar_x
            for st, sc in states.items():
                seg_w = max(1, int(bar_w * sc / cnt))
                scol = state_colors.get(st, (100, 100, 100))
                pygame.draw.rect(surf, scol, (bx, card_y + 10, seg_w, bar_h), border_radius=1)
                bx += seg_w

            # state legend (most common state)
            top_state = max(states, key=lambda k: states[k]) if states else "idle"
            scol = state_colors.get(top_state, (100, 100, 100))
            draw_text(surf, f"{states.get(top_state, 0)} {top_state}", bar_x + bar_w + 6,
                      card_y + 6, self.font_xs, scol)

            card_y += 22

        # DPS summary for combat units
        combat = [u for u in selected if u.unit_type in ("soldier", "archer")]
        if combat:
            total_dps = sum(u.attack_power / max(0.5, getattr(u, 'attack_cooldown', 1.0)) for u in combat)
            draw_text(surf, f"~{total_dps:.0f} DPS", 20, card_y + 2, self.font_xs, (220, 160, 80))

        # v10_epsilon: Chord preview — show harmony quality per discovered formation
        # Only for free (non-squad) combat units
        soldiers = [u for u in selected if u.unit_type == "soldier"]
        archers = [u for u in selected if u.unit_type == "archer"]
        s_count = len(soldiers)
        a_count = len(archers)
        if (s_count + a_count) >= 2 and hasattr(game, 'discovered_formations'):
            free_combat = [u for u in selected
                           if u.unit_type in ("soldier", "archer")
                           and game.player_squad_mgr.is_free(u)]
            if len(free_combat) >= 2:
                from squads import compute_harmony
                from constants import HARMONY_LABELS, RESONANCE_COLORS, FORMATION_NAMES
                chord_y = card_y + 20
                draw_text(surf, f"{s_count}S {a_count}A", 20, chord_y,
                          self.font_xs, (180, 180, 200))
                chord_y += 14
                for fmt_idx in sorted(game.discovered_formations):
                    h = compute_harmony(fmt_idx, s_count, a_count)
                    h_pct = int(h * 100)
                    label = HARMONY_LABELS.get(fmt_idx, "")
                    fname = (FORMATION_NAMES[fmt_idx] if fmt_idx < len(FORMATION_NAMES) else "?")[:4]
                    res_col = RESONANCE_COLORS.get(fmt_idx, (100, 100, 100))
                    # Quality descriptor
                    if h >= 0.95:
                        qual = "perfect"
                        q_col = (255, 230, 80)
                    elif h >= 0.80:
                        qual = "rich"
                        q_col = res_col
                    elif h >= 0.60:
                        qual = "thin"
                        q_col = (160, 160, 140)
                    else:
                        qual = "weak"
                        q_col = (120, 80, 80)
                    # Compact display: "Rose ♪ 100% octave [████████]"
                    draw_text(surf, fname, 20, chord_y, self.font_xs, res_col)
                    draw_text(surf, f"{h_pct}%", 60, chord_y, self.font_xs, q_col)
                    # Mini harmony bar
                    bar_x, bar_w, bar_h = 92, 60, 5
                    pygame.draw.rect(surf, (30, 30, 40), (bar_x, chord_y + 4, bar_w, bar_h), border_radius=2)
                    fill_w = max(1, int(bar_w * max(0, h - 0.3) / 0.7))
                    pygame.draw.rect(surf, q_col, (bar_x, chord_y + 4, fill_w, bar_h), border_radius=2)
                    if label:
                        draw_text(surf, label, bar_x + bar_w + 4, chord_y, self.font_xs, (140, 140, 160))
                    chord_y += 13

        # Action buttons on right side
        all_workers = all(u.unit_type == "worker" for u in selected)
        if all_workers:
            self._draw_worker_action_buttons(surf, py, game)

        all_combat = all(u.unit_type in ("soldier", "archer") for u in selected)
        if all_combat:
            self._draw_command_buttons(surf, py, game)

    # ------------------------------------------------------------------
    # COMMAND BUTTONS (soldiers / archers)
    # ------------------------------------------------------------------
    def _draw_global_buttons(self, surf, py, game):
        """v10_8d: Global command buttons — progressively revealed."""
        unlocks = game.unlocks
        btn_w, btn_h = 120, 30
        btn_y = py + 6
        gap = 6
        btn_x = 20
        slot = 0

        # Defend/Hunt only after combat exists
        if unlocks["has_barracks"] or unlocks["has_squad"]:
            self._add_button(surf, btn_x + slot * (btn_w + gap), btn_y, btn_w, btn_h,
                             "Defend Base", lambda: game.global_defend())
            slot += 1
            self._add_button(surf, btn_x + slot * (btn_w + gap), btn_y, btn_w, btn_h,
                             "Hunt Enemies", lambda: game.global_attack())
            slot += 1

        # Town Bell: after garrison is meaningful (has workers + some economy)
        if unlocks["has_iron"] or game.game_time > 120:
            gc = GARRISON_COST
            can_bell = game.resources.can_afford(wood=gc["wood"], iron=gc["iron"], stone=gc["stone"])
            cost_str = f"{gc['wood']}W {gc['iron']}I {gc['stone']}S"
            self._add_button(surf, btn_x + slot * (btn_w + gap), btn_y, btn_w, btn_h,
                             "Town Bell", lambda: game.global_bell(),
                             enabled=can_bell, cost_text=cost_str)
            slot += 1

        # Resume: always after bell is available
        if unlocks["has_iron"] or game.game_time > 120:
            self._add_button(surf, btn_x + slot * (btn_w + gap), btn_y, btn_w, btn_h,
                             "Resume Work", lambda: game.global_resume())
            slot += 1

        # v10_8d: contextual help text — changes based on progression
        hint_y = py + 44
        if game.game_time < 30:
            hint = "Select workers and right-click resources to start gathering"
        elif not unlocks["has_barracks"] and game.game_time < 120:
            hint = "Build a War Nexus to train soldiers — enemies approach!"
        elif unlocks["has_squad"]:
            hint = "LClick: select  RClick: command  1-9: squad  Tab: cycle  A+click: atk-move  P: pause"
        else:
            hint = "LClick: select  RClick: command  Shift+click: add  P: pause"
        draw_text(surf, hint, 20, hint_y, self.font_xs, (70, 70, 90))

    # ------------------------------------------------------------------
    def _draw_command_buttons(self, surf, py, game):
        """v10_8d: Formation picker + stance picker — progressively unlocked."""
        btn_x = 400
        btn_y_start = py + 2
        unlocks = game.unlocks

        combat_sel = [e for e in game.selected
                      if hasattr(e, 'unit_type') and e.unit_type in ("soldier", "archer")]
        if not combat_sel:
            return

        # Determine current squad(s)
        squads_seen = {}
        for u in combat_sel:
            sq = game.player_squad_mgr.get_squad(u)
            if sq and sq.squad_id not in squads_seen:
                squads_seen[sq.squad_id] = sq
        primary_squad = list(squads_seen.values())[0] if squads_seen else None
        cur_fmt = primary_squad.formation if primary_squad else 0
        cur_stance = primary_squad.stance if primary_squad else 0

        # No squad yet — show hint instead of formation buttons
        if not primary_squad:
            draw_text(surf, "Units need Rank 1+ to form squads and unlock formations",
                      btn_x, btn_y_start + 6, self.font_xs, (100, 100, 140))
            draw_text(surf, "X+click: attack-move", btn_x, btn_y_start + 22,
                      self.font_xs, (70, 70, 90))
            return

        # v10_alpha: Formation row — unlock through discovery (not squad size)
        discovered = game.discovered_formations
        fmt_w = 72
        shown_fmts = 0
        # Formation order for display: Rose, Spiral, Sierpinski, Koch (indices 0,1,2,3)
        fmt_order = [FORMATION_POLAR_ROSE, FORMATION_GOLDEN_SPIRAL,
                     FORMATION_SIERPINSKI, FORMATION_KOCH]
        for display_i, fmt_idx in enumerate(fmt_order):
            fname = FORMATION_NAMES[fmt_idx]
            unlocked = fmt_idx in discovered
            fx = btn_x + shown_fmts * (fmt_w + 3)
            if not unlocked:
                # Show discovery hint
                hint = DISCOVERY_HINTS.get(fmt_idx, "?")
                pygame.draw.rect(surf, (30, 30, 40), (fx, btn_y_start, fmt_w, 24), border_radius=3)
                pygame.draw.rect(surf, (50, 50, 60), (fx, btn_y_start, fmt_w, 24), 1, border_radius=3)
                draw_text(surf, hint, fx + 4, btn_y_start + 6,
                          self.font_xs, (60, 60, 80))
                self._register_tooltip(pygame.Rect(fx, btn_y_start, fmt_w, 24), f"fmt_{fname}")
                shown_fmts += 1
                continue

            label = f"F{display_i+1}:{fname}"
            is_active = (fmt_idx == cur_fmt)
            res_color = RESONANCE_COLORS.get(fmt_idx, (100, 100, 100))
            def _set_fmt(idx=fmt_idx):
                self._set_formation(game, idx)
                game.unlocks["formations_used"].add(idx)
            self._add_button(surf, fx, btn_y_start, fmt_w, 24, label, _set_fmt,
                             enabled=True)
            if is_active:
                pygame.draw.rect(surf, res_color, (fx, btn_y_start, fmt_w, 24), 2)
            self._register_tooltip(pygame.Rect(fx, btn_y_start, fmt_w, 24), f"fmt_{fname}")
            shown_fmts += 1

        # Resonance value + harmony quality labels below formation buttons
        if primary_squad and squads_seen:
            from squads import (resonance_polar_rose_bonus, resonance_golden_spiral_miss,
                                resonance_sierpinski_aoe_factor, resonance_koch_slow,
                                compute_harmony, get_squad_composition)
            n = primary_squad.alive_count
            s_count, a_count = get_squad_composition(primary_squad)
            labels = [
                f"+{resonance_polar_rose_bonus(n)*100:.0f}% DMG",
                f"{resonance_golden_spiral_miss(n)*100:.0f}% Evade",
                f"{(1.0 - resonance_sierpinski_aoe_factor(n))*100:.0f}% AOE Red",
                f"{resonance_koch_slow(n)*100:.0f}% Slow",
            ]
            label_map = {FORMATION_POLAR_ROSE: labels[0],
                         FORMATION_GOLDEN_SPIRAL: labels[1],
                         FORMATION_SIERPINSKI: labels[2],
                         FORMATION_KOCH: labels[3]}
            for display_i, fmt_idx in enumerate(fmt_order):
                if fmt_idx not in discovered:
                    continue
                lx = btn_x + display_i * (fmt_w + 3)
                res_col = RESONANCE_COLORS.get(fmt_idx, (100, 100, 100))
                is_active = (fmt_idx == cur_fmt)
                col = res_col if is_active else (80, 80, 80)
                draw_text(surf, label_map[fmt_idx], lx + 2, btn_y_start + 24, self.font_xs, col)
                # Show harmony quality when this formation is active
                if is_active:
                    harmony = compute_harmony(fmt_idx, s_count, a_count)
                    h_pct = int(harmony * 100)
                    h_col = (255, 230, 80) if h_pct >= 100 else res_col
                    draw_text(surf, f"{h_pct}%", lx + fmt_w - 22, btn_y_start + 24,
                              self.font_xs, h_col)
                    self._register_tooltip(pygame.Rect(lx, btn_y_start + 24, fmt_w, 12), "harmony")

        # Stance row — unlock progressively
        # Aggressive: always, Defensive: rank 1+, Guard: rank 2+, Hunt: incident 3+
        max_rank = unlocks["max_rank_seen"]
        incident = game.enemy_ai.incident_number
        stance_unlock = [True, max_rank >= 1, max_rank >= 2, incident >= 3]

        stance_y = btn_y_start + 40
        stance_w = 72
        shown_stances = 0
        for i, sname in enumerate(STANCE_NAMES):
            sx = btn_x + shown_stances * (stance_w + 3)
            if not stance_unlock[i]:
                # locked stance hint
                pygame.draw.rect(surf, (30, 30, 40), (sx, stance_y, stance_w, 24), border_radius=3)
                pygame.draw.rect(surf, (50, 50, 60), (sx, stance_y, stance_w, 24), 1, border_radius=3)
                if i == 1:
                    hint = "Rank 1"
                elif i == 2:
                    hint = "Rank 2"
                else:
                    hint = "Wave 3"
                draw_text(surf, hint, sx + 10, stance_y + 6, self.font_xs, (60, 60, 80))
                self._register_tooltip(pygame.Rect(sx, stance_y, stance_w, 24), f"stance_{sname}")
                shown_stances += 1
                continue

            label = f"F{i+5}:{sname}"
            is_active = (i == cur_stance)
            s_color = STANCE_COLORS.get(i, (180, 220, 255))
            def _set_st(idx=i):
                self._set_stance(game, idx)
            self._add_button(surf, sx, stance_y, stance_w, 24, label, _set_st,
                             enabled=True)
            if is_active:
                pygame.draw.rect(surf, s_color, (sx, stance_y, stance_w, 24), 2)
            self._register_tooltip(pygame.Rect(sx, stance_y, stance_w, 24), f"stance_{sname}")
            shown_stances += 1

        # Hint: contextual based on game state
        hint_y = stance_y + 28
        if not unlocks["has_squad"]:
            draw_text(surf, "Train units to Rank 1 to unlock squads and formations",
                      btn_x, hint_y, self.font_xs, (100, 120, 80))
        else:
            draw_text(surf, "X+click: attack-move", btn_x, hint_y,
                      self.font_xs, (70, 70, 90))

    def _set_formation(self, game, fmt_idx):
        """Set formation on all selected squads (v10_8 squad-centric)."""
        seen = set()
        for e in game.selected:
            if hasattr(e, 'unit_type') and e.unit_type in ("soldier", "archer"):
                sq = game.player_squad_mgr.get_squad(e)
                if sq and sq.squad_id not in seen:
                    seen.add(sq.squad_id)
                    sq.formation = fmt_idx

    def _set_stance(self, game, stance_idx):
        """Set stance on all selected squads (v10_8 squad-centric)."""
        seen = set()
        for e in game.selected:
            if hasattr(e, 'unit_type') and e.unit_type in ("soldier", "archer"):
                sq = game.player_squad_mgr.get_squad(e)
                if sq and sq.squad_id not in seen:
                    seen.add(sq.squad_id)
                    sq.stance = stance_idx
                    for m in sq.members:
                        if m.alive:
                            m.command_set_stance(stance_idx)
                            m.stance = stance_idx

    # ------------------------------------------------------------------
    # BUTTONS
    # ------------------------------------------------------------------
    def _draw_locked_button(self, surf, x, y, w, h, label, hint):
        """v10_8d: Draw a locked/teaser button with unlock hint."""
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, (25, 25, 35), rect, border_radius=4)
        pygame.draw.rect(surf, (45, 45, 55), rect, 1, border_radius=4)
        draw_text(surf, label, x + w // 2, y + h // 2 - 5, self.font_sm, (55, 55, 70), center=True)
        draw_text(surf, hint, x + w // 2, y + h // 2 + 7, self.font_xs, (70, 60, 50), center=True)

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
        # Auto-register tooltip for buttons with matching keys
        tooltip_key = f"btn_{label.split('(')[0].strip()}"
        if tooltip_key in TOOLTIP_DATA:
            self._register_tooltip(rect, tooltip_key)

    # ------------------------------------------------------------------
    # MESSAGE LOG — mini panel in bottom-right, click to expand
    # ------------------------------------------------------------------
    def _draw_message_log_mini(self, surf, py, game):
        """Draw 3 most recent messages in the bottom-right of the panel."""
        log = game._message_log
        line_h = 15
        n_show = 3
        pad = 4
        log_w = 280
        log_h = n_show * line_h + pad * 2 + 14  # +14 for header
        log_x = SCREEN_WIDTH - log_w - 8
        log_y = py + 4

        # store rect for click detection
        self._msg_log_rect = pygame.Rect(log_x, log_y, log_w, log_h)

        # subtle background
        bg = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
        bg.fill((18, 18, 28, 160))
        surf.blit(bg, (log_x, log_y))
        pygame.draw.rect(surf, (50, 50, 65), (log_x, log_y, log_w, log_h), 1)

        # header
        header_col = (100, 100, 130) if not game.show_message_log else (160, 160, 200)
        draw_text(surf, "Messages", log_x + pad, log_y + pad, self.font_xs, header_col)
        if len(log) > n_show:
            draw_text(surf, f"({len(log)})", log_x + 62, log_y + pad,
                      self.font_xs, (70, 70, 90))

        # recent messages
        recent = log[-n_show:] if log else []
        y = log_y + pad + 14
        for text, msg_time, color in recent:
            age = game.game_time - msg_time
            if age > MSG_LOG_FADE:
                fade = max(0.3, 1.0 - (age - MSG_LOG_FADE) / MSG_LOG_FADE)
                faded = tuple(max(0, int(c * fade)) for c in color)
            else:
                faded = color
            # truncate text to fit
            max_tw = log_w - pad * 2 - 4
            txt_surf = self.font_xs.render(str(text), True, faded)
            if txt_surf.get_width() > max_tw:
                t = str(text)
                while txt_surf.get_width() > max_tw - 8 and len(t) > 5:
                    t = t[:-1]
                txt_surf = self.font_xs.render(t + "..", True, faded)
            surf.blit(txt_surf, (log_x + pad + 2, y))
            y += line_h

        if not recent:
            draw_text(surf, "-- No messages --", log_x + pad + 2, y,
                      self.font_xs, (60, 60, 80))

    def draw_message_log_full(self, surf, game):
        """Draw the full message log as a center overlay when expanded."""
        log = game._message_log
        line_h = 18
        pad = 10
        max_lines = 20
        log_w = 500
        n_lines = min(max_lines, len(log))
        log_h = n_lines * line_h + pad * 2 + 30  # +30 for header
        if n_lines == 0:
            log_h = 60

        log_x = (SCREEN_WIDTH - log_w) // 2
        log_y = GAME_AREA_Y + (GAME_AREA_H - log_h) // 2

        # dark overlay behind
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surf.blit(overlay, (0, 0))

        # panel background
        bg = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
        bg.fill((20, 20, 32, 230))
        surf.blit(bg, (log_x, log_y))
        pygame.draw.rect(surf, (80, 80, 110), (log_x, log_y, log_w, log_h), 2)

        # header
        draw_text(surf, "Message Log", log_x + pad, log_y + pad,
                  self.font_sm, (200, 200, 220))
        draw_text(surf, f"{len(log)} messages -- click or [L] to close",
                  log_x + log_w - pad - 220, log_y + pad + 2, self.font_xs, (100, 100, 130))

        if not log:
            draw_text(surf, "No messages yet.", log_x + pad, log_y + 40,
                      self.font_sm, (80, 80, 100))
            return

        # show recent messages (newest at bottom)
        recent = log[-max_lines:]
        y = log_y + pad + 24
        for text, msg_time, color in recent:
            age = game.game_time - msg_time
            if age > MSG_LOG_FADE * 2:
                fade = max(0.25, 1.0 - (age - MSG_LOG_FADE * 2) / (MSG_LOG_FADE * 2))
                faded = tuple(max(0, int(c * fade)) for c in color)
            else:
                faded = color
            # timestamp
            mins = int(msg_time) // 60
            secs = int(msg_time) % 60
            ts = f"{mins:02d}:{secs:02d}"
            draw_text(surf, ts, log_x + pad, y, self.font_xs, (70, 70, 90))
            # message
            max_tw = log_w - 60
            txt_surf = self.font_xs.render(str(text), True, faded)
            if txt_surf.get_width() > max_tw:
                t = str(text)
                while txt_surf.get_width() > max_tw - 8 and len(t) > 5:
                    t = t[:-1]
                txt_surf = self.font_xs.render(t + "..", True, faded)
            surf.blit(txt_surf, (log_x + pad + 44, y))
            y += line_h

    def handle_click(self, pos):
        # check message log mini-panel click
        if hasattr(self, '_msg_log_rect') and self._msg_log_rect.collidepoint(pos):
            return "toggle_log"
        for rect, label, callback, enabled in self.buttons:
            if rect.collidepoint(pos) and enabled:
                callback()
                return True
        return False
