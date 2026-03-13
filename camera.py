import pygame
from constants import (MAP_COLS, MAP_ROWS, TILE_SIZE, SCREEN_WIDTH,
                       SCREEN_HEIGHT, BOTTOM_PANEL_H, GAME_AREA_Y, GAME_AREA_H,
                       CAMERA_SPEED, EDGE_SCROLL_MARGIN, ZOOM_MIN, ZOOM_MAX)
from utils import clamp


class Camera:
    def __init__(self):
        self.zoom = 1.0
        cx = (MAP_COLS // 2) * TILE_SIZE - SCREEN_WIDTH // 2
        cy = (MAP_ROWS // 2) * TILE_SIZE - GAME_AREA_H // 2
        self.x = float(cx)
        self.y = float(cy)

    def apply_zoom(self, amount, mx, my):
        """Zoom towards/away from mouse position."""
        old_zoom = self.zoom
        self.zoom = clamp(self.zoom + amount, ZOOM_MIN, ZOOM_MAX)
        if self.zoom == old_zoom:
            return
        # adjust camera so the world point under the mouse stays fixed
        wx_mouse = self.x + (mx) / old_zoom
        wy_mouse = self.y + (my - GAME_AREA_Y) / old_zoom
        self.x = wx_mouse - (mx) / self.zoom
        self.y = wy_mouse - (my - GAME_AREA_Y) / self.zoom
        self._clamp()

    def update(self, keys, dt, mx, my, suppress_wasd=False):
        dx, dy = 0, 0
        if (not suppress_wasd and keys[pygame.K_w]) or keys[pygame.K_UP] or my < GAME_AREA_Y + EDGE_SCROLL_MARGIN:
            dy = -1
        if (not suppress_wasd and keys[pygame.K_s]) or keys[pygame.K_DOWN] or (my > GAME_AREA_Y + GAME_AREA_H - EDGE_SCROLL_MARGIN and my < SCREEN_HEIGHT - BOTTOM_PANEL_H):
            dy = 1
        if (not suppress_wasd and keys[pygame.K_a]) or keys[pygame.K_LEFT] or mx < EDGE_SCROLL_MARGIN:
            dx = -1
        if (not suppress_wasd and keys[pygame.K_d]) or keys[pygame.K_RIGHT] or mx > SCREEN_WIDTH - EDGE_SCROLL_MARGIN:
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

    def world_to_screen(self, wx, wy):
        return int((wx - self.x) * self.zoom), int((wy - self.y) * self.zoom + GAME_AREA_Y)

    def screen_to_world(self, sx, sy):
        return sx / self.zoom + self.x, (sy - GAME_AREA_Y) / self.zoom + self.y

    def visible_rect(self):
        vw = SCREEN_WIDTH / self.zoom
        vh = GAME_AREA_H / self.zoom
        return pygame.Rect(self.x, self.y, vw, vh)
