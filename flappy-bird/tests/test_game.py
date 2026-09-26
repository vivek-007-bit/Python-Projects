"""
Comprehensive test suite for Flappy Bird game mechanics, physics, and states.
"""
import os
import sys
import unittest
import pygame

# Headless video driver for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from game.settings import (
    GAME_WIDTH, GAME_HEIGHT, GROUND_Y, GRAVITY, FLAP_STRENGTH,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER
)
from game.player import Bird
from game.pipe import PipePair, PipeManager
from game.sound_manager import SoundManager
from game.particles import ParticleManager
from game.game import FlappyBirdGame
from game.main import get_viewport_transform, window_to_logical_pos

class TestFlappyBird(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_settings_validity(self):
        self.assertEqual(GAME_WIDTH, 400)
        self.assertEqual(GAME_HEIGHT, 700)
        self.assertGreater(GROUND_Y, 0)
        self.assertLess(GROUND_Y, GAME_HEIGHT)
        self.assertLess(FLAP_STRENGTH, 0)
        self.assertGreater(GRAVITY, 0)

    def test_bird_physics_and_flap(self):
        assets_img = os.path.join(root_dir, "game", "assets", "images")
        bird = Bird(x=100, y=300, assets_dir=assets_img)
        self.assertEqual(bird.x, 100)
        self.assertEqual(bird.y, 300)
        self.assertTrue(bird.is_alive)

        # Update without flap (falling due to gravity)
        bird.update()
        self.assertGreater(bird.y, 300)
        self.assertGreater(bird.vel_y, 0)

        # Flap
        flap_result = bird.flap()
        self.assertTrue(flap_result)
        self.assertEqual(bird.vel_y, FLAP_STRENGTH)
        self.assertGreater(bird.angle, 0) # Upward tilt

        # Multiple updates to verify ground collision
        bird.y = GROUND_Y - 5
        bird.vel_y = 10
        bird.update()
        self.assertEqual(bird.y, GROUND_Y - bird.height)
        self.assertFalse(bird.is_alive)

    def test_pipe_mechanics(self):
        assets_img = os.path.join(root_dir, "game", "assets", "images")
        pipe_mgr = PipeManager(assets_dir=assets_img)
        pipe_mgr.reset()
        self.assertEqual(len(pipe_mgr.pipes), 0)

        # Spawn a pipe
        pipe_mgr.spawn_pipe(x=300)
        self.assertEqual(len(pipe_mgr.pipes), 1)
        pipe = pipe_mgr.pipes[0]

        # Check collision with bird inside top pipe
        hit_rect = pygame.Rect(310, 20, 30, 30)
        self.assertTrue(pipe.collides_with(hit_rect))

        # Bird in the middle of gap should NOT collide
        gap_center_y = pipe.top_height + pipe.gap / 2
        safe_rect = pygame.Rect(310, int(gap_center_y - 10), 20, 20)
        self.assertFalse(pipe.collides_with(safe_rect))

        # Check passing and scoring
        self.assertFalse(pipe.passed)
        scored = pipe.check_passed(player_x=300 + pipe.width + 10)
        self.assertTrue(scored)
        self.assertTrue(pipe.passed)
        # Should not score a second time
        self.assertFalse(pipe.check_passed(player_x=300 + pipe.width + 20))

    def test_particle_manager(self):
        pm = ParticleManager()
        pm.emit_flap(100, 200)
        self.assertGreater(len(pm.particles), 0)
        pm.emit_score(150, 250)
        pm.emit_death(100, 200)
        initial_count = len(pm.particles)

        # Update particles
        pm.update()
        self.assertEqual(len(pm.particles), initial_count)
        
        pm.clear()
        self.assertEqual(len(pm.particles), 0)

    def test_sound_manager_safe_operations(self):
        snd = SoundManager()
        # Safe triggers without raising errors
        snd.play_flap()
        snd.play_point()
        snd.play_hit()
        snd.play_die()
        
        # Mute toggle
        self.assertFalse(snd.muted)
        snd.toggle_mute()
        self.assertTrue(snd.muted)
        snd.toggle_mute()
        self.assertFalse(snd.muted)

    def test_game_states_and_flow(self):
        assets_dir = os.path.join(root_dir, "game", "assets")
        game = FlappyBirdGame(assets_dir=assets_dir)
        self.assertEqual(game.state, STATE_MENU)

        # Flap to start
        game.trigger_flap()
        self.assertEqual(game.state, STATE_PLAYING)
        self.assertEqual(game.score, 0)

        # Pause toggle
        game.toggle_pause()
        self.assertEqual(game.state, STATE_PAUSED)
        game.toggle_pause()
        self.assertEqual(game.state, STATE_PLAYING)

        # Simulate game over by forcing bird to ground
        game.bird.y = GROUND_Y + 10
        game.update()
        self.assertEqual(game.state, STATE_GAME_OVER)

        # Allow restart after timer
        game.game_over_timer = 30
        game.trigger_flap()
        self.assertEqual(game.state, STATE_PLAYING)

    def test_viewport_scaling_and_touch_translation(self):
        # Window size 800x1400 (exact 2x scale)
        scale, sw, sh, ox, oy = get_viewport_transform((800, 1400))
        self.assertEqual(scale, 2.0)
        self.assertEqual(sw, 800)
        self.assertEqual(sh, 1400)
        self.assertEqual(ox, 0)
        self.assertEqual(oy, 0)

        # Mouse click at (400, 700) in 800x1400 window should map to (200, 350)
        lx, ly = window_to_logical_pos((400, 700), scale, ox, oy)
        self.assertEqual(lx, 200.0)
        self.assertEqual(ly, 350.0)

        # Window size 1200x700 (wide letterboxing)
        scale2, sw2, sh2, ox2, oy2 = get_viewport_transform((1200, 700))
        self.assertEqual(scale2, 1.0)
        self.assertEqual(sw2, 400)
        self.assertEqual(sh2, 700)
        self.assertEqual(ox2, 400)
        self.assertEqual(oy2, 0)

        # Click at (ox2 + 100, 200) -> (100, 200)
        lx2, ly2 = window_to_logical_pos((500, 200), scale2, ox2, oy2)
        self.assertEqual(lx2, 100.0)
        self.assertEqual(ly2, 200.0)

if __name__ == "__main__":
    unittest.main()
