"""
Core Game class managing game states, scoring, UI rendering, collisions, and visual polish.
"""
import os
import json
import math
import random
import pygame

from game.settings import (
    GAME_WIDTH, GAME_HEIGHT, FPS, GROUND_Y, GROUND_HEIGHT,
    GROUND_SPEED, BG_SPEED, STATE_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER,
    WHITE, BLACK, GOLD, BRONZE, SILVER, PLATINUM, CARD_BG, CARD_BORDER,
    SCORE_FILE
)
from game.player import Bird
from game.pipe import PipeManager
from game.sound_manager import SoundManager
from game.particles import ParticleManager

class FlappyBirdGame:
    def __init__(self, assets_dir=None):
        if assets_dir is None:
            base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "game")
            assets_dir = os.path.join(base, "assets")
        self.assets_dir = assets_dir
        self.img_dir = os.path.join(assets_dir, "images")
        self.snd_dir = os.path.join(assets_dir, "sounds")

        # Core subsystems
        self.sound = SoundManager(self.snd_dir)
        self.particles = ParticleManager()
        self.bird = Bird(assets_dir=self.img_dir)
        self.pipe_manager = PipeManager(assets_dir=self.img_dir)

        # State and Scoring
        self.state = STATE_MENU
        self.score = 0
        self.best_score = self._load_high_score()
        self.is_new_high_score = False

        # Visuals & Animation
        self.bg_x = 0.0
        self.ground_x = 0.0
        self.score_scale_timer = 0
        self.screen_shake = 0
        self.flash_alpha = 0
        self.menu_pulse_timer = 0.0
        self.game_over_timer = 0

        # Load environment textures
        self.bg_img = self._load_background()
        self.ground_img = self._load_ground()

        # Fonts
        self._init_fonts()

        # UI Buttons (in logical coordinates 400x700)
        self.btn_sound = pygame.Rect(GAME_WIDTH - 48, 16, 34, 34)
        self.btn_pause = pygame.Rect(14, 16, 34, 34)

    def _init_fonts(self):
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 52)
        self.font_large = pygame.font.Font(None, 42)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        self.font_score = pygame.font.Font(None, 56)

    def _load_background(self):
        path = os.path.join(self.img_dir, "background.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                if pygame.display.get_surface():
                    img = img.convert()
                return pygame.transform.scale(img, (GAME_WIDTH, GAME_HEIGHT))
            except Exception as e:
                print(f"[Game] Failed to load background: {e}")
        # Procedural fallback
        surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        surf.fill((100, 195, 220))
        return surf

    def _load_ground(self):
        path = os.path.join(self.img_dir, "ground.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
                if pygame.display.get_surface():
                    img = img.convert()
                return img
            except Exception as e:
                print(f"[Game] Failed to load ground: {e}")
        # Procedural fallback
        surf = pygame.Surface((480, GROUND_HEIGHT))
        surf.fill((222, 215, 150))
        pygame.draw.rect(surf, (115, 190, 45), (0, 0, 480, 14))
        return surf

    def _load_high_score(self):
        try:
            if os.path.exists(SCORE_FILE):
                with open(SCORE_FILE, "r") as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
        except Exception as e:
            print(f"[Game] Could not read score file: {e}")
        return 0

    def _save_high_score(self):
        try:
            with open(SCORE_FILE, "w") as f:
                json.dump({"high_score": self.best_score}, f)
        except Exception as e:
            print(f"[Game] Could not save score file: {e}")

    def reset_game(self):
        self.bird.reset()
        self.pipe_manager.reset()
        self.particles.clear()
        self.score = 0
        self.is_new_high_score = False
        self.flash_alpha = 0
        self.screen_shake = 0
        self.score_scale_timer = 0
        self.game_over_timer = 0

    def trigger_flap(self):
        if self.state == STATE_MENU:
            self.state = STATE_PLAYING
            self.reset_game()
            if self.bird.flap():
                self.sound.play_flap()
                self.particles.emit_flap(self.bird.x, self.bird.y + self.bird.height / 2)
        elif self.state == STATE_PLAYING:
            if self.bird.flap():
                self.sound.play_flap()
                self.particles.emit_flap(self.bird.x, self.bird.y + self.bird.height / 2)
        elif self.state == STATE_GAME_OVER:
            # Prevent accidental immediate restart
            if self.game_over_timer > 25:
                self.state = STATE_PLAYING
                self.reset_game()
                if self.bird.flap():
                    self.sound.play_flap()
                    self.particles.emit_flap(self.bird.x, self.bird.y + self.bird.height / 2)

    def toggle_pause(self):
        if self.state == STATE_PLAYING:
            self.state = STATE_PAUSED
        elif self.state == STATE_PAUSED:
            self.state = STATE_PLAYING

    def handle_input_event(self, event, logical_mouse_pos=None):
        """Processes keyboard, mouse, and touch events mapped to logical coordinates."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                self.trigger_flap()
            elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                self.toggle_pause()
            elif event.key == pygame.K_m:
                self.sound.toggle_mute()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mx, my = logical_mouse_pos if logical_mouse_pos else event.pos
                # Check Sound button click
                if self.btn_sound.collidepoint(mx, my):
                    self.sound.toggle_mute()
                    return
                # Check Pause button click
                if self.state in (STATE_PLAYING, STATE_PAUSED) and self.btn_pause.collidepoint(mx, my):
                    self.toggle_pause()
                    return

                if self.state == STATE_PAUSED:
                    self.toggle_pause()
                else:
                    self.trigger_flap()

        elif event.type == pygame.FINGERDOWN:
            # Pygame touch event (touch coords normalized 0.0 to 1.0)
            mx = int(event.x * GAME_WIDTH)
            my = int(event.y * GAME_HEIGHT)
            if self.btn_sound.collidepoint(mx, my):
                self.sound.toggle_mute()
                return
            if self.state in (STATE_PLAYING, STATE_PAUSED) and self.btn_pause.collidepoint(mx, my):
                self.toggle_pause()
                return

            if self.state == STATE_PAUSED:
                self.toggle_pause()
            else:
                self.trigger_flap()

    def update(self):
        """Main gameplay logic update at 60 FPS."""
        self.menu_pulse_timer += 0.06

        # Decay visual effects
        if self.screen_shake > 0:
            self.screen_shake -= 1
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 18)
        if self.score_scale_timer > 0:
            self.score_scale_timer -= 1

        if self.state == STATE_MENU:
            # Hover bird and scroll background
            self.bird.update_hover()
            self.ground_x = (self.ground_x - GROUND_SPEED) % self.ground_img.get_width()
            self.bg_x = (self.bg_x - BG_SPEED) % GAME_WIDTH

        elif self.state == STATE_PLAYING:
            # Scroll environment
            self.ground_x = (self.ground_x - GROUND_SPEED) % self.ground_img.get_width()
            self.bg_x = (self.bg_x - BG_SPEED) % GAME_WIDTH

            # Update Bird
            self.bird.update()

            # Update Pipes
            score_inc = self.pipe_manager.update(self.bird.x)
            if score_inc > 0:
                self.score += score_inc
                self.sound.play_point()
                self.particles.emit_score(self.bird.x + self.bird.width / 2, self.bird.y, self.font_small)
                self.score_scale_timer = 12

                if self.score > self.best_score:
                    self.best_score = self.score
                    self.is_new_high_score = True
                    self._save_high_score()

            # Collision Detection
            bird_hitbox = self.bird.get_hitbox()
            hit_pipe = self.pipe_manager.check_collision(bird_hitbox)
            hit_ground = (self.bird.y + self.bird.height >= GROUND_Y)

            if hit_pipe or hit_ground:
                self._handle_game_over(hit_ground)

            # Particles
            self.particles.update()

        elif self.state == STATE_GAME_OVER:
            self.game_over_timer += 1
            # Let bird fall to ground if in mid-air
            if self.bird.y + self.bird.height < GROUND_Y:
                self.bird.update()
            self.particles.update()

        elif self.state == STATE_PAUSED:
            # In paused state, do not advance physics or particles
            pass

    def _handle_game_over(self, hit_ground):
        self.state = STATE_GAME_OVER
        self.bird.is_alive = False
        self.screen_shake = 10
        self.flash_alpha = 180
        self.particles.emit_death(self.bird.x + self.bird.width / 2, self.bird.y + self.bird.height / 2)
        
        self.sound.play_hit()
        if not hit_ground:
            self.sound.play_die()

        if self.score > self.best_score:
            self.best_score = self.score
            self.is_new_high_score = True
            self._save_high_score()

    def draw(self, surface):
        """Renders the game scene onto the logical 400x700 surface."""
        # Screen Shake offset
        shake_ox = 0
        shake_oy = 0
        if self.screen_shake > 0:
            shake_ox = random.randint(-self.screen_shake, self.screen_shake)
            shake_oy = random.randint(-self.screen_shake, self.screen_shake)

        temp_surface = surface
        if shake_ox != 0 or shake_oy != 0:
            temp_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

        # 1. Background (Parallax)
        temp_surface.blit(self.bg_img, (-int(self.bg_x), 0))
        temp_surface.blit(self.bg_img, (GAME_WIDTH - int(self.bg_x), 0))

        # 2. Pipes
        self.pipe_manager.draw(temp_surface)

        # 3. Ground (Seamless scrolling)
        gw = self.ground_img.get_width()
        temp_surface.blit(self.ground_img, (-int(self.ground_x), GROUND_Y))
        temp_surface.blit(self.ground_img, (gw - int(self.ground_x), GROUND_Y))
        temp_surface.blit(self.ground_img, (gw * 2 - int(self.ground_x), GROUND_Y))

        # 4. Particles
        self.particles.draw(temp_surface)

        # 5. Bird
        self.bird.draw(temp_surface)

        # 6. UI Overlays by State
        if self.state == STATE_MENU:
            self._draw_menu(temp_surface)
        elif self.state == STATE_PLAYING:
            self._draw_playing_ui(temp_surface)
        elif self.state == STATE_PAUSED:
            self._draw_playing_ui(temp_surface)
            self._draw_paused(temp_surface)
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over(temp_surface)

        # 7. Screen Shake Blit
        if shake_ox != 0 or shake_oy != 0:
            surface.fill(BLACK)
            surface.blit(temp_surface, (shake_ox, shake_oy))

        # 8. Hit Flash Overlay
        if self.flash_alpha > 0:
            flash_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, self.flash_alpha))
            surface.blit(flash_surf, (0, 0))

        # 9. Top Icons (Sound & Pause)
        self._draw_top_buttons(surface)

    def _draw_top_buttons(self, surface):
        # Sound button
        pygame.draw.rect(surface, (25, 35, 45), self.btn_sound, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.btn_sound, 2, border_radius=8)
        
        # Speaker icon
        sx, sy = self.btn_sound.centerx, self.btn_sound.centery
        # speaker cone
        speaker_pts = [(sx - 8, sy - 4), (sx - 4, sy - 4), (sx + 2, sy - 9), (sx + 2, sy + 9), (sx - 4, sy + 4), (sx - 8, sy + 4)]
        pygame.draw.polygon(surface, WHITE, speaker_pts)
        if self.sound.muted:
            # Red slash
            pygame.draw.line(surface, (235, 60, 60), (sx - 9, sy - 9), (sx + 9, sy + 9), 3)
        else:
            # Sound waves
            pygame.draw.arc(surface, WHITE, (sx + 1, sy - 7, 8, 14), -math.pi / 2.5, math.pi / 2.5, 2)

        # Pause button (visible in PLAYING & PAUSED)
        if self.state in (STATE_PLAYING, STATE_PAUSED):
            pygame.draw.rect(surface, (25, 35, 45), self.btn_pause, border_radius=8)
            pygame.draw.rect(surface, WHITE, self.btn_pause, 2, border_radius=8)
            px, py = self.btn_pause.centerx, self.btn_pause.centery
            if self.state == STATE_PAUSED:
                # Play triangle
                pygame.draw.polygon(surface, WHITE, [(px - 4, py - 7), (px + 6, py), (px - 4, py + 7)])
            else:
                # Double bar
                pygame.draw.rect(surface, WHITE, (px - 6, py - 6, 4, 12), border_radius=1)
                pygame.draw.rect(surface, WHITE, (px + 2, py - 6, 4, 12), border_radius=1)

    def _draw_text_with_shadow(self, surface, text, font, color, pos, shadow_color=BLACK, offset=(2, 2), center=True):
        txt = font.render(text, True, color)
        shd = font.render(text, True, shadow_color)
        if center:
            rect = txt.get_rect(center=pos)
            surface.blit(shd, (rect.x + offset[0], rect.y + offset[1]))
            surface.blit(txt, rect)
            return rect
        else:
            surface.blit(shd, (pos[0] + offset[0], pos[1] + offset[1]))
            surface.blit(txt, pos)
            return txt.get_rect(topleft=pos)

    def _draw_menu(self, surface):
        # Title with double-layer outline
        title_y = 150 + int(math.sin(self.menu_pulse_timer) * 4)
        self._draw_text_with_shadow(surface, "FLAPPY BIRD", self.font_title, GOLD, (GAME_WIDTH // 2, title_y), shadow_color=(50, 30, 0), offset=(3, 3))

        # Best Score in Menu
        if self.best_score > 0:
            badge_rect = pygame.Rect(GAME_WIDTH // 2 - 70, 360, 140, 32)
            pygame.draw.rect(surface, (25, 35, 45), badge_rect, border_radius=16)
            pygame.draw.rect(surface, GOLD, badge_rect, 2, border_radius=16)
            self._draw_text_with_shadow(surface, f"BEST: {self.best_score}", self.font_small, WHITE, (GAME_WIDTH // 2, 376))

        # Pulsing Start Prompt
        pulse_alpha = int(180 + 75 * math.sin(self.menu_pulse_timer * 2.5))
        prompt_surf = self.font_medium.render("TAP / PRESS SPACE", True, WHITE)
        prompt_shadow = self.font_medium.render("TAP / PRESS SPACE", True, BLACK)
        prompt_surf.set_alpha(pulse_alpha)
        prompt_shadow.set_alpha(pulse_alpha)
        
        pr_rect = prompt_surf.get_rect(center=(GAME_WIDTH // 2, 440))
        surface.blit(prompt_shadow, (pr_rect.x + 2, pr_rect.y + 2))
        surface.blit(prompt_surf, pr_rect)

        # Instructions / Control hints
        self._draw_text_with_shadow(surface, "Desktop: Space / Up / Click", self.font_small, (240, 240, 240), (GAME_WIDTH // 2, 490))
        self._draw_text_with_shadow(surface, "Mobile: Tap Anywhere", self.font_small, (240, 240, 240), (GAME_WIDTH // 2, 514))
        self._draw_text_with_shadow(surface, "P: Pause | M: Mute", self.font_small, (220, 220, 220), (GAME_WIDTH // 2, 538))

    def _draw_playing_ui(self, surface):
        # Current Score (top center)
        scale_bonus = 4 if self.score_scale_timer > 0 else 0
        font = self.font_score if scale_bonus == 0 else self.font_title
        self._draw_text_with_shadow(surface, str(self.score), font, WHITE, (GAME_WIDTH // 2, 60), shadow_color=(20, 30, 40), offset=(3, 3))

    def _draw_paused(self, surface):
        # Translucent dark overlay
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        # Pause Box Card
        card_rect = pygame.Rect(GAME_WIDTH // 2 - 110, GAME_HEIGHT // 2 - 80, 220, 160)
        pygame.draw.rect(surface, CARD_BG, card_rect, border_radius=12)
        pygame.draw.rect(surface, CARD_BORDER, card_rect, 4, border_radius=12)

        self._draw_text_with_shadow(surface, "PAUSED", self.font_large, (80, 50, 20), (GAME_WIDTH // 2, GAME_HEIGHT // 2 - 40), shadow_color=(200, 190, 150), offset=(2, 2))
        self._draw_text_with_shadow(surface, "Tap / Press P to Resume", self.font_small, (100, 70, 40), (GAME_WIDTH // 2, GAME_HEIGHT // 2 + 10), shadow_color=WHITE, offset=(1, 1))
        self._draw_text_with_shadow(surface, f"Score: {self.score}", self.font_medium, (60, 40, 15), (GAME_WIDTH // 2, GAME_HEIGHT // 2 + 45), shadow_color=WHITE, offset=(1, 1))

    def _draw_game_over(self, surface):
        # Banner "GAME OVER"
        self._draw_text_with_shadow(surface, "GAME OVER", self.font_title, (245, 80, 60), (GAME_WIDTH // 2, 160), shadow_color=(60, 15, 10), offset=(3, 3))

        # Score Card Box
        card_w, card_h = 280, 170
        card_rect = pygame.Rect((GAME_WIDTH - card_w) // 2, 215, card_w, card_h)
        pygame.draw.rect(surface, CARD_BG, card_rect, border_radius=14)
        pygame.draw.rect(surface, CARD_BORDER, card_rect, 4, border_radius=14)

        # Medal section (left of card)
        medal_cx, medal_cy = card_rect.left + 58, card_rect.centery + 6
        self._draw_text_with_shadow(surface, "MEDAL", self.font_small, (120, 90, 60), (medal_cx, card_rect.top + 32), shadow_color=WHITE, offset=(1, 1))
        
        # Draw Medal circle
        medal_color = None
        if self.score >= 40:
            medal_color = PLATINUM
            medal_name = "PLATINUM"
        elif self.score >= 30:
            medal_color = GOLD
            medal_name = "GOLD"
        elif self.score >= 20:
            medal_color = SILVER
            medal_name = "SILVER"
        elif self.score >= 10:
            medal_color = BRONZE
            medal_name = "BRONZE"

        pygame.draw.circle(surface, (180, 165, 125), (medal_cx, medal_cy), 26)
        pygame.draw.circle(surface, (115, 80, 40), (medal_cx, medal_cy), 26, 3)
        if medal_color:
            pygame.draw.circle(surface, medal_color, (medal_cx, medal_cy), 23)
            pygame.draw.circle(surface, (255, 255, 255, 180), (medal_cx - 6, medal_cy - 6), 6) # shine

        # Score & Best labels (right of card)
        right_x = card_rect.right - 24
        
        # SCORE
        self._draw_text_with_shadow(surface, "SCORE", self.font_small, (150, 100, 50), (right_x - 30, card_rect.top + 28), shadow_color=WHITE, offset=(1, 1))
        self._draw_text_with_shadow(surface, str(self.score), self.font_large, (50, 40, 30), (right_x - 30, card_rect.top + 60), shadow_color=WHITE, offset=(1, 1))

        # BEST
        self._draw_text_with_shadow(surface, "BEST", self.font_small, (150, 100, 50), (right_x - 30, card_rect.top + 98), shadow_color=WHITE, offset=(1, 1))
        self._draw_text_with_shadow(surface, str(self.best_score), self.font_large, (50, 40, 30), (right_x - 30, card_rect.top + 130), shadow_color=WHITE, offset=(1, 1))

        # NEW badge if new high score
        if self.is_new_high_score and self.score > 0:
            new_badge = pygame.Rect(right_x - 92, card_rect.top + 88, 38, 18)
            pygame.draw.rect(surface, (245, 60, 40), new_badge, border_radius=4)
            self._draw_text_with_shadow(surface, "NEW", self.font_small, WHITE, (new_badge.centerx, new_badge.centery), shadow_color=(60, 10, 10), offset=(1, 1))

        # Pulsing Restart Button
        pulse = int(180 + 75 * math.sin(self.menu_pulse_timer * 3))
        res_surf = self.font_medium.render("TAP / SPACE TO RESTART", True, WHITE)
        res_shadow = self.font_medium.render("TAP / SPACE TO RESTART", True, BLACK)
        res_surf.set_alpha(pulse)
        res_shadow.set_alpha(pulse)
        
        rs_rect = res_surf.get_rect(center=(GAME_WIDTH // 2, 435))
        surface.blit(res_shadow, (rs_rect.x + 2, rs_rect.y + 2))
        surface.blit(res_surf, rs_rect)
