"""
Player bird implementation with smooth physics, rotation, animation frames, and procedural fallbacks.
"""
import os
import math
import pygame
from game.settings import (
    PLAYER_START_X, PLAYER_START_Y, BIRD_WIDTH, BIRD_HEIGHT,
    GRAVITY, FLAP_STRENGTH, MAX_FALL_SPEED, GROUND_Y, BIRD_FLAP_ANIM_SPEED
)

class Bird:
    def __init__(self, x=PLAYER_START_X, y=PLAYER_START_Y, assets_dir=None):
        self.start_x = x
        self.start_y = y
        self.x = float(x)
        self.y = float(y)
        self.width = BIRD_WIDTH
        self.height = BIRD_HEIGHT
        self.vel_y = 0.0
        self.angle = 0.0
        self.target_angle = 0.0
        
        self.is_alive = True
        self.hover_timer = 0.0
        self.anim_frame = 0.0

        if assets_dir is None:
            base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "game")
            assets_dir = os.path.join(base, "assets", "images")
        self.assets_dir = assets_dir

        self.frames = self._load_frames()
        self.current_surface = self.frames[0]

    def _load_frames(self):
        frame_names = ["bird_up.png", "bird_mid.png", "bird_down.png"]
        loaded = []
        for name in frame_names:
            path = os.path.join(self.assets_dir, name)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path)
                    if pygame.display.get_surface():
                        img = img.convert_alpha()
                    img = pygame.transform.smoothscale(img, (self.width, self.height))
                    loaded.append(img)
                except Exception as e:
                    print(f"[Bird] Could not load '{name}': {e}")
            else:
                print(f"[Bird] File not found '{name}', using procedural fallback.")

        if len(loaded) < 3:
            return self._create_procedural_frames()
        return loaded

    def _create_procedural_frames(self):
        """Creates procedural surfaces if image files are missing."""
        frames = []
        for wing_pos in ['up', 'mid', 'down']:
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Body outline and fill
            pygame.draw.ellipse(surf, (35, 35, 35), (2, 2, self.width - 4, self.height - 4))
            pygame.draw.ellipse(surf, (250, 190, 35), (4, 4, self.width - 8, self.height - 8))
            pygame.draw.ellipse(surf, (255, 230, 80), (8, 6, self.width - 16, self.height - 14))
            
            # Eye
            pygame.draw.ellipse(surf, (35, 35, 35), (int(self.width * 0.6), 6, 12, 14))
            pygame.draw.ellipse(surf, (255, 255, 255), (int(self.width * 0.6) + 1, 7, 10, 12))
            pygame.draw.circle(surf, (35, 35, 35), (int(self.width * 0.72), 12), 3)

            # Beak
            pygame.draw.polygon(surf, (245, 110, 30), [
                (int(self.width * 0.7), int(self.height * 0.45)),
                (self.width - 2, int(self.height * 0.6)),
                (int(self.width * 0.7), int(self.height * 0.75))
            ])

            # Wing
            if wing_pos == 'up':
                pygame.draw.polygon(surf, (255, 255, 255), [(10, 14), (20, 4), (24, 14)])
            elif wing_pos == 'mid':
                pygame.draw.ellipse(surf, (255, 255, 255), (8, 12, 16, 10))
            else:
                pygame.draw.polygon(surf, (255, 255, 255), [(10, 14), (20, 24), (24, 14)])
            
            frames.append(surf)
        return frames

    def reset(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.vel_y = 0.0
        self.angle = 0.0
        self.is_alive = True
        self.hover_timer = 0.0
        self.anim_frame = 0.0

    def flap(self):
        if not self.is_alive:
            return False
        self.vel_y = FLAP_STRENGTH
        self.target_angle = 28.0
        self.angle = 28.0
        return True

    def update_hover(self):
        """Used in MENU state for pleasant gentle bobbing."""
        self.hover_timer += 0.08
        self.y = self.start_y + math.sin(self.hover_timer) * 6.5
        self.angle = math.sin(self.hover_timer) * 4.0
        self.anim_frame = (self.anim_frame + BIRD_FLAP_ANIM_SPEED) % len(self.frames)
        self.current_surface = self.frames[int(self.anim_frame)]

    def update(self):
        """Physics and rotation update during gameplay."""
        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.y += self.vel_y

        # Prevent flying infinitely above screen (ceiling block)
        if self.y < -15:
            self.y = -15
            self.vel_y = max(0.0, self.vel_y)

        # Ground clamp
        if self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
            self.vel_y = 0.0
            if self.is_alive:
                self.is_alive = False

        # Smooth Rotation physics
        if self.vel_y < 0:
            # Rising: tilt up
            self.target_angle = 25.0
            self.angle += (self.target_angle - self.angle) * 0.25
        else:
            # Falling: tilt down smoothly up to -85 deg
            self.target_angle = max(-85.0, -self.vel_y * 11.0)
            self.angle += (self.target_angle - self.angle) * 0.12

        # Wing Animation
        if self.is_alive:
            self.anim_frame = (self.anim_frame + BIRD_FLAP_ANIM_SPEED) % len(self.frames)
            self.current_surface = self.frames[int(self.anim_frame)]
        else:
            # Freeze on mid frame when dead
            self.current_surface = self.frames[1]

    def get_hitbox(self):
        """Returns slightly inset rectangle for forgiving, fair collision detection."""
        inset_x = 6
        inset_y = 5
        return pygame.Rect(
            int(self.x + inset_x),
            int(self.y + inset_y),
            int(self.width - inset_x * 2),
            int(self.height - inset_y * 2)
        )

    def draw(self, surface):
        # Rotate current surface
        rotated_surf = pygame.transform.rotate(self.current_surface, self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.x + self.width / 2), int(self.y + self.height / 2)))
        surface.blit(rotated_surf, new_rect.topleft)
