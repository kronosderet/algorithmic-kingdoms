import pygame, random
from constants import (MAP_COLS, MAP_ROWS, TILE_SIZE, SCREEN_WIDTH,
                       SCREEN_HEIGHT, BOTTOM_PANEL_H, GAME_AREA_Y, GAME_AREA_H,
                       CAMERA_SPEED, EDGE_SCROLL_MARGIN, ZOOM_MIN, ZOOM_MAX,
                       MINIMAP_X, MINIMAP_Y, MINIMAP_SIZE)
from utils import clamp


class Camera:
    def __init__(self):
        self.zoom = 1.0
        cx = (MAP_COLS // 2) * TILE_SIZE - SCREEN_WIDTH // 2
        cy = (MAP_ROWS // 2) * TILE_SIZE - GAME_AREA_H // 2
        self.x = float(cx)
        self.y = float(cy)
        # Screen shake state
        self._shake_amount = 0.0
        self._shake_timer = 0.0
        self._shake_offset_x = 0
        self._shake_offset_y = 0

    def apply_zoom(self, amount, mx, my):
        """Zoom towards/away from mouse position.
        v10_7: round zoom to nearest 0.05 to prevent float drift."""
        old_zoom = self.zoom
        new_zoom = clamp(self.zoom + amount, ZOOM_MIN, ZOOM_MAX)
        # snap to clean values to prevent float accumulation
        new_zoom = round(new_zoom * 20) / 20  # nearest 0.05
        self.zoom = clamp(new_zoom, ZOOM_MIN, ZOOM_MAX)
        if self.zoom == old_zoom:
            return
        # adjust camera so the world point under the mouse stays fixed
        # subtract shake offset so the calculation uses clean screen coords
        clean_mx = mx - self._shake_offset_x
        clean_my = my - self._shake_offset_y
        wx_mouse = self.x + clean_mx / old_zoom
        wy_mouse = self.y + (clean_my - GAME_AREA_Y) / old_zoom
        self.x = wx_mouse - clean_mx / self.zoom
        self.y = wy_mouse - (clean_my - GAME_AREA_Y) / self.zoom
        self._clamp()

    def update(self, keys, dt, mx, my, suppress_wasd=False):
        dx, dy = 0, 0
        in_game_area = GAME_AREA_Y <= my < SCREEN_HEIGHT - BOTTOM_PANEL_H
        # Exclude minimap rect from edge scroll detection
        in_minimap = (MINIMAP_X <= mx <= MINIMAP_X + MINIMAP_SIZE and
                      MINIMAP_Y <= my <= MINIMAP_Y + MINIMAP_SIZE)
        edge_ok = in_game_area and not in_minimap
        if (not suppress_wasd and keys[pygame.K_w]) or keys[pygame.K_UP] or (edge_ok and my < GAME_AREA_Y + EDGE_SCROLL_MARGIN):
            dy = -1
        if (not suppress_wasd and keys[pygame.K_s]) or keys[pygame.K_DOWN] or (edge_ok and my > GAME_AREA_Y + GAME_AREA_H - EDGE_SCROLL_MARGIN):
            dy = 1
        if (not suppress_wasd and keys[pygame.K_a]) or keys[pygame.K_LEFT] or (edge_ok and mx < EDGE_SCROLL_MARGIN):
            dx = -1
        if (not suppress_wasd and keys[pygame.K_d]) or keys[pygame.K_RIGHT] or (edge_ok and mx > SCREEN_WIDTH - EDGE_SCROLL_MARGIN):
            dx = 1
        spd = CAMERA_SPEED * dt / self.zoom
        self.x += dx * spd
        self.y += dy * spd
        self._clamp()

    def _clamp(self):
        view_w = SCREEN_WIDTH / self.zoom
        view_h = GAME_AREA_H / self.zoom
        max_x = MAP_COLS * TILE_SIZE - view_w
        max_y = MAP_ROWS * TILE_SIZE - view_h
        self.x = clamp(self.x, 0, max(0, max_x))
        self.y = clamp(self.y, 0, max(0, max_y))

    def shake(self, amount, duration):
        """Trigger screen shake (stacks by taking max)."""
        self._shake_amount = max(self._shake_amount, amount)
        self._shake_timer = max(self._shake_timer, duration)

    def update_shake(self, dt):
        """Update shake decay — call once per frame."""
        if self._shake_timer > 0:
            self._shake_timer -= dt
            intensity = max(0.0, self._shake_timer / 0.12) * self._shake_amount
            self._shake_offset_x = int(random.uniform(-intensity, intensity))
            self._shake_offset_y = int(random.uniform(-intensity, intensity))
        else:
            self._shake_offset_x = 0
            self._shake_offset_y = 0

    def world_to_screen(self, wx, wy):
        sx = int((wx - self.x) * self.zoom) + self._shake_offset_x
        sy = int((wy - self.y) * self.zoom + GAME_AREA_Y) + self._shake_offset_y
        return sx, sy

    def screen_to_world(self, sx, sy):
        # v10_7: compensate for shake offset so clicks align with visual grid
        cx = sx - self._shake_offset_x
        cy = sy - self._shake_offset_y
        return cx / self.zoom + self.x, (cy - GAME_AREA_Y) / self.zoom + self.y

    def visible_rect(self):
        vw = SCREEN_WIDTH / self.zoom
        vh = GAME_AREA_H / self.zoom
        return pygame.Rect(self.x, self.y, vw, vh)
