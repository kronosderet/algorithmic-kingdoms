"""Visual test for the full fractal GUI system.

Run: python visuals/test_fractal_gui.py
Renders font, Koch borders, resource icons, and radial gradients.
Auto-saves screenshot and exits (no interaction needed).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Fractal GUI Test")

from fractal_font import fractal_font
from fractal_ui import (
    koch_border, radial_gradient,
    draw_fibonacci_spiral, draw_binary_tree, draw_octahedron,
    draw_reuleaux_triangle, draw_voronoi_cluster, draw_resource_icon,
    fractal_bar, fractal_bar_simple,
)

BG = (20, 20, 30)
GOLD = (255, 215, 0)
WHITE = (220, 220, 220)
CYAN = (100, 200, 255)
GREEN = (100, 220, 100)
AMBER = (220, 180, 80)
PANEL_BG_CENTER = (35, 32, 50)
PANEL_BG_EDGE = (20, 18, 30)
GHOST_STONE = (80, 75, 55)
GUI_BORDER = (80, 80, 100)

# --- Background ---
screen.fill(BG)

# --- Radial gradient panel backgrounds ---
top_bar_grad = radial_gradient(W, 40, PANEL_BG_CENTER, PANEL_BG_EDGE)
screen.blit(top_bar_grad, (0, 0))

bot_grad = radial_gradient(W, 130, PANEL_BG_CENTER, PANEL_BG_EDGE)
screen.blit(bot_grad, (0, 590))

# --- Koch borders on panels ---
koch_border(screen, (0, 0, W, 40), 1, GHOST_STONE)
koch_border(screen, (0, 590, W, 130), 1, GUI_BORDER)

# Minimap area
mm_x, mm_y, mm_size = 1100, 50, 160
mm_grad = radial_gradient(mm_size, mm_size, (30, 40, 35), (15, 20, 15))
screen.blit(mm_grad, (mm_x, mm_y))
koch_border(screen, (mm_x, mm_y, mm_size, mm_size), 2, GHOST_STONE)

# Camera viewport Koch rect inside minimap
koch_border(screen, (mm_x + 20, mm_y + 30, 60, 45), 1, GOLD)

# --- Fractal font on top bar ---
y_top = 8
fractal_font.draw(screen, "RESONANCE", 15, y_top, 28, GOLD)

# --- Resource icons + labels in top bar ---
res_x = 250
resources = [
    ("gold", "Flux: 342", (255, 215, 0)),
    ("wood", "Fiber: 187", (34, 180, 34)),
    ("iron", "Ore: 56", (170, 170, 185)),
    ("steel", "Alloy: 12", (100, 160, 220)),
    ("stone", "Crystal: 29", (160, 150, 130)),
]
for res_code, label, color in resources:
    draw_resource_icon(screen, res_code, res_x + 8, 20, 7, color)
    fractal_font.draw(screen, label, res_x + 20, y_top, 16, color)
    res_x += 120

# Pop counter
fractal_font.draw(screen, "Pop 7/25", res_x + 20, y_top, 16, WHITE)

# Tension meter area
fractal_font.draw(screen, "CALM", W - 160, y_top, 16, (80, 160, 200))
pygame.draw.rect(screen, (40, 40, 60), (W - 260, 14, 90, 12))
pygame.draw.rect(screen, (60, 140, 180), (W - 260, 14, 25, 12))

# --- Bottom panel content ---
bot_y = 600

# Building selection example
fractal_font.draw(screen, "SENTINEL", 20, bot_y, 24, CYAN)
fractal_font.draw(screen, "Level 2  HP: 180/220", 20, bot_y + 30, 16, WHITE)
fractal_font.draw(screen, "Resonance field active", 20, bot_y + 50, 14, (100, 200, 100))

# Build buttons with Koch borders
btn_labels = [
    ("Tree of Life [1]", (80, 200, 80)),
    ("Res. Forge [2]", (200, 120, 80)),
    ("Harm. Mill [3]", (100, 160, 220)),
    ("Sentinel [4]", (100, 200, 255)),
]
bx = 350
for label, color in btn_labels:
    # Button background
    pygame.draw.rect(screen, (40, 38, 55), (bx, bot_y + 5, 110, 40))
    koch_border(screen, (bx, bot_y + 5, 110, 40), 1, color)
    fractal_font.draw(screen, label, bx + 8, bot_y + 14, 14, color)
    bx += 120

# --- Game area: demo Koch border panels at different depths ---
demo_y = 80
fractal_font.draw(screen, "KOCH BORDER DEPTHS:", 30, demo_y, 20, AMBER)
demo_y += 35

for depth in range(4):
    x_off = 30 + depth * 250
    pygame.draw.rect(screen, (30, 30, 45), (x_off, demo_y, 200, 80))
    koch_border(screen, (x_off, demo_y, 200, 80), depth, GUI_BORDER)
    fractal_font.draw(screen, f"Depth {depth}", x_off + 60, demo_y + 30, 18, WHITE)

# --- Resource icon gallery ---
icon_y = demo_y + 120
fractal_font.draw(screen, "RESOURCE ICONS:", 30, icon_y, 20, AMBER)
icon_y += 35

icon_data = [
    ("Flux", "gold", (255, 215, 0)),
    ("Fiber", "wood", (34, 180, 34)),
    ("Ore", "iron", (170, 170, 185)),
    ("Alloy", "steel", (100, 160, 220)),
    ("Crystal", "stone", (160, 150, 130)),
]
ix = 60
for name, code, color in icon_data:
    # Draw at 3 sizes
    for r, oy in [(6, 0), (10, 0), (16, 0)]:
        draw_resource_icon(screen, code, ix, icon_y + 20, r, color)
        ix += r * 3 + 10
    fractal_font.draw(screen, name, ix - 10, icon_y + 10, 16, color)
    ix += 80

# --- Font showcase ---
font_y = icon_y + 70
fractal_font.draw(screen, "FRACTAL TYPOGRAPHY:", 30, font_y, 20, AMBER)
font_y += 30
fractal_font.draw(screen, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 30, font_y, 22, WHITE)
font_y += 30
fractal_font.draw(screen, "0123456789  .,;:!?-+=/()[]", 30, font_y, 22, CYAN)
font_y += 35

# Fractal bars showcase
fractal_font.draw(screen, "FRACTAL BARS:", 30, font_y, 20, AMBER)
font_y += 28
bar_data = [
    ("HP 100%", 1.0, (0, 200, 50)),
    ("HP  75%", 0.75, (0, 200, 50)),
    ("HP  50%", 0.5, (220, 180, 0)),
    ("HP  25%", 0.25, (220, 50, 50)),
    ("Build progress", 0.6, (0, 180, 255)),
    ("Train progress", 0.4, (255, 200, 0)),
]
for label, ratio, color in bar_data:
    fractal_font.draw(screen, label, 30, font_y, 14, WHITE)
    fractal_bar(screen, 180, font_y, 200, 12, ratio, color, border=True)
    # Small in-world style bar
    fractal_bar_simple(screen, 400, font_y + 2, 30, 4, ratio, color)
    font_y += 18

# --- Finish ---
pygame.display.flip()

# Save screenshot
os.makedirs("visuals/samples", exist_ok=True)
out_path = "visuals/samples/fractal_gui_test.png"
pygame.image.save(screen, out_path)
print(f"Saved {out_path}")

pygame.quit()
