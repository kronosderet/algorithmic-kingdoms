"""Visual test for the fractal font system.

Run: python visuals/test_fractal_font.py
Shows the full glyph set at multiple sizes with serif branching.
Press any key or close window to exit.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Fractal Font Test")

from fractal_font import fractal_font

BG = (20, 20, 30)
GOLD = (255, 215, 0)
WHITE = (220, 220, 220)
CYAN = (100, 200, 255)
GREEN = (100, 220, 100)
AMBER = (220, 180, 80)

screen.fill(BG)

y = 10

# Title
fractal_font.draw(screen, "FRACTAL FONT TEST", 20, y, 36, GOLD)
y += 50

# Full alphabet at size 24 (serif depth 1)
fractal_font.draw(screen, "ABCDEFGHIJKLM", 20, y, 24, WHITE)
y += 35
fractal_font.draw(screen, "NOPQRSTUVWXYZ", 20, y, 24, WHITE)
y += 35

# Digits
fractal_font.draw(screen, "0123456789", 20, y, 24, CYAN)
y += 35

# Punctuation
fractal_font.draw(screen, ".,;:!?-+=/()[]", 20, y, 24, AMBER)
y += 35

# Symbols
fractal_font.draw(screen, "'\"#@$%^&*~<>_", 20, y, 24, AMBER)
y += 40

# Game text samples at different sizes
samples = [
    (40, GOLD, "RESONANCE"),
    (28, WHITE, "Tree of Life  Sentinel  Resonance Forge"),
    (22, CYAN, "Flux: 300  Fiber: 150  Ore: 45  Crystal: 20"),
    (18, GREEN, "Gatherer [Q]  Warden [W]  Ranger [E]"),
    (16, WHITE, "Wave 7 approaching from the NORTH"),
    (14, (160, 160, 170), "Press F1 for Polar Rose formation"),
]

for size, color, text in samples:
    fractal_font.draw(screen, text, 20, y, size, color)
    # Show size label
    fractal_font.draw(screen, f"{size}px", W - 80, y, 14, (100, 100, 120))
    y += size + 12

# Show serif depth comparison
y += 10
fractal_font.draw(screen, "SERIF DEPTH COMPARISON:", 20, y, 18, (140, 140, 160))
y += 28
# 36px = depth 2
fractal_font.draw(screen, "Depth 2 (36px): SENTINEL", 20, y, 36, GOLD)
y += 50
# 24px = depth 1
fractal_font.draw(screen, "Depth 1 (24px): SENTINEL", 20, y, 24, GOLD)
y += 38
# 20px = depth 0
fractal_font.draw(screen, "Depth 0 (20px): SENTINEL", 20, y, 20, GOLD)

pygame.display.flip()

# Wait for keypress or close
running = True
while running:
    for ev in pygame.event.get():
        if ev.type in (pygame.QUIT, pygame.KEYDOWN):
            running = False

# Save screenshot
os.makedirs("visuals/samples", exist_ok=True)
pygame.image.save(screen, "visuals/samples/fractal_font_test.png")
print("Saved visuals/samples/fractal_font_test.png")

pygame.quit()
