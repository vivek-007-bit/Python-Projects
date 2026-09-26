"""
Root entry point for Flappy Bird game.
Runs the game locally or prepares it for Pygbag browser packaging.
"""
import sys
import os
import asyncio

# Ensure game package is discoverable
root_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pygame
from game.settings import GAME_WIDTH, GAME_HEIGHT, FPS
from game.game import FlappyBirdGame

async def main():
    print("PYGBAG: ASYNC MAIN ENTERED")
    pygame.init()
    pygame.display.set_caption("Flappy Bird")

    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    clock = pygame.time.Clock()

    assets_dir = os.path.join(root_dir, "game", "assets")
    game = FlappyBirdGame(assets_dir=assets_dir)

    print("PYGBAG: STARTING GAME LOOP")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            game.handle_input_event(event)

        game.update()
        game.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()

# Run unconditionally for both native Python execution and pygbag shell.source
asyncio.run(main())
