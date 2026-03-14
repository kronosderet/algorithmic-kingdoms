"""
Simple RTS Game - Python/Pygame
Gather resources, build a base, train units, survive enemy waves!
"""

import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from menu import MainMenu
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Resonance")

    while True:
        menu = MainMenu(screen)
        result = menu.run()
        if result == "exit":
            break
        elif result in ("easy", "medium", "hard"):
            game = Game(screen, difficulty=result)
            game.run()
            # game.run() returns when game ends (ESC on game over/win)
            # loop back to menu

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
