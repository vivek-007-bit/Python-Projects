"""
Main game loop and entry point with responsive viewport scaling and Pygbag async compatibility.
"""
import sys
import os
import asyncio
import pygame

# Ensure project root is in sys.path when running from inside game/
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "game")
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from game.settings import GAME_WIDTH, GAME_HEIGHT, FPS
from game.game import FlappyBirdGame

def get_viewport_transform(window_size):
    """Calculates scaling and letterboxing offset to maintain 400x700 aspect ratio."""
    win_w, win_h = window_size
    scale = min(win_w / GAME_WIDTH, win_h / GAME_HEIGHT)
    scaled_w = int(GAME_WIDTH * scale)
    scaled_h = int(GAME_HEIGHT * scale)
    offset_x = (win_w - scaled_w) // 2
    offset_y = (win_h - scaled_h) // 2
    return scale, scaled_w, scaled_h, offset_x, offset_y

def window_to_logical_pos(pos, scale, offset_x, offset_y):
    """Converts window pixel coordinates to logical 400x700 game coordinates."""
    wx, wy = pos
    if scale <= 0:
        return 0, 0
    lx = (wx - offset_x) / scale
    ly = (wy - offset_y) / scale
    return lx, ly

async def main():
    pygame.init()
    pygame.display.set_caption("Flappy Bird")

    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    clock = pygame.time.Clock()

    assets_dir = os.path.join(current_dir, "assets")
    game = FlappyBirdGame(assets_dir=assets_dir)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
            game.handle_input_event(event)

        # 1. Update Game
        game.update()

        # 2. Render directly to display surface
        game.draw(screen)

        # 3. Flush display
        pygame.display.flip()
        
        # 4. FPS sync & WebAssembly event loop yield
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
