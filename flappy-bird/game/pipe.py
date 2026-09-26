"""
Pipe obstacle system with randomized gap placement, movement, and collision detection.
"""
import os
import random
import pygame
from game.settings import (
    GAME_WIDTH, GROUND_Y, PIPE_WIDTH, PIPE_GAP, PIPE_SPEED,
    PIPE_MIN_TOP_HEIGHT, PIPE_MAX_TOP_HEIGHT, PIPE_SPAWN_DISTANCE
)

class PipePair:
    def __init__(self, x, top_height, pipe_img_down, pipe_img_up, gap=PIPE_GAP):
        self.x = float(x)
        self.top_height = top_height
        self.gap = gap
        self.width = PIPE_WIDTH
        self.speed = PIPE_SPEED
        self.passed = False
        
        self.pipe_img_down = pipe_img_down  # Top pipe (inverted)
        self.pipe_img_up = pipe_img_up      # Bottom pipe

        # Calculate bounding boxes
        self.top_rect = pygame.Rect(int(self.x), 0, self.width, int(self.top_height))
        bottom_y = self.top_height + self.gap
        bottom_h = GROUND_Y - bottom_y
        self.bottom_rect = pygame.Rect(int(self.x), int(bottom_y), self.width, int(bottom_h))

    def update(self):
        self.x -= self.speed
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)

    @property
    def is_offscreen(self):
        return self.x + self.width < -10

    def collides_with(self, rect):
        """Check collision with tight bounding box for fair gameplay."""
        # Top pipe check (inset slightly for forgiving corners)
        top_box = self.top_rect.inflate(-4, 0)
        bottom_box = self.bottom_rect.inflate(-4, 0)
        return top_box.colliderect(rect) or bottom_box.colliderect(rect)

    def check_passed(self, player_x):
        """Returns True once when player crosses the middle of the pipe."""
        if not self.passed and player_x > self.x + self.width / 2:
            self.passed = True
            return True
        return False

    def draw(self, surface):
        # Draw top pipe (hanging down from top)
        if self.pipe_img_down is not None:
            # Clip surface or position so cap is at bottom of top pipe
            img_h = self.pipe_img_down.get_height()
            top_y = self.top_height - img_h
            surface.blit(self.pipe_img_down, (int(self.x), int(top_y)))
        else:
            # Procedural fallback
            pygame.draw.rect(surface, (115, 190, 45), self.top_rect)
            pygame.draw.rect(surface, (35, 65, 15), self.top_rect, 3)

        # Draw bottom pipe (standing up from ground)
        if self.pipe_img_up is not None:
            bottom_y = self.top_height + self.gap
            surface.blit(self.pipe_img_up, (int(self.x), int(bottom_y)))
        else:
            # Procedural fallback
            pygame.draw.rect(surface, (115, 190, 45), self.bottom_rect)
            pygame.draw.rect(surface, (35, 65, 15), self.bottom_rect, 3)


class PipeManager:
    def __init__(self, assets_dir=None):
        if assets_dir is None:
            base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "game")
            assets_dir = os.path.join(base, "assets", "images")
        self.assets_dir = assets_dir
        
        self.pipe_img_up, self.pipe_img_down = self._load_pipe_images()
        self.pipes = []
        self.last_spawn_x = 0.0

    def _load_pipe_images(self):
        pipe_path = os.path.join(self.assets_dir, "pipe.png")
        if os.path.exists(pipe_path):
            try:
                base_img = pygame.image.load(pipe_path)
                if pygame.display.get_surface():
                    base_img = base_img.convert_alpha()
                # Ensure width is PIPE_WIDTH
                if base_img.get_width() != PIPE_WIDTH:
                    base_img = pygame.transform.smoothscale(base_img, (PIPE_WIDTH, base_img.get_height()))
                
                # Top pipe inverted vertically
                img_down = pygame.transform.flip(base_img, False, True)
                img_up = base_img
                return img_up, img_down
            except Exception as e:
                print(f"[PipeManager] Failed to load pipe image: {e}")
        return None, None

    def reset(self):
        self.pipes.clear()
        self.last_spawn_x = 0.0

    def spawn_pipe(self, x=None):
        if x is None:
            x = GAME_WIDTH + 20
        top_height = random.randint(PIPE_MIN_TOP_HEIGHT, PIPE_MAX_TOP_HEIGHT)
        pipe = PipePair(x, top_height, self.pipe_img_down, self.pipe_img_up)
        self.pipes.append(pipe)
        self.last_spawn_x = x

    def update(self, player_x):
        """
        Updates pipe movement, spawns new pipes, recycles offscreen pipes,
        and returns the number of newly passed pipes (score increments).
        """
        # Spawning logic: spawn when last pipe has moved sufficiently left
        if not self.pipes:
            self.spawn_pipe(GAME_WIDTH + 60)
        else:
            rightmost_x = max(p.x for p in self.pipes)
            if rightmost_x <= GAME_WIDTH + 60 - PIPE_SPAWN_DISTANCE:
                self.spawn_pipe(GAME_WIDTH + 60)

        score_inc = 0
        for pipe in self.pipes:
            pipe.update()
            if pipe.check_passed(player_x):
                score_inc += 1

        # Remove offscreen pipes
        self.pipes = [p for p in self.pipes if not p.is_offscreen]

        return score_inc

    def check_collision(self, bird_hitbox):
        for pipe in self.pipes:
            if pipe.collides_with(bird_hitbox):
                return True
        return False

    def draw(self, surface):
        for pipe in self.pipes:
            pipe.draw(surface)
