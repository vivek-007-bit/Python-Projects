"""
Lightweight particle system for flap puffs, score bursts, and impact effects.
"""
import random
import math
import pygame
from game.settings import WHITE, GOLD

class Particle:
    def __init__(self, x, y, vx, vy, size, color, lifetime, shrink=True, gravity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.size = float(size)
        self.max_size = float(size)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.shrink = shrink
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        if self.shrink and self.max_lifetime > 0:
            self.size = max(0.5, self.max_size * (self.lifetime / self.max_lifetime))

    @property
    def is_alive(self):
        return self.lifetime > 0 and self.size > 0.4

    def draw(self, surface):
        if not self.is_alive:
            return
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        if len(self.color) == 4:
            c = (self.color[0], self.color[1], self.color[2], int(self.color[3] * (self.lifetime / self.max_lifetime)))
        else:
            c = (self.color[0], self.color[1], self.color[2], alpha)
        
        radius = int(self.size)
        if radius < 1:
            return
        
        # Draw on an alpha surface for smooth fading
        particle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, c, (radius, radius), radius)
        surface.blit(particle_surf, (int(self.x - radius), int(self.y - radius)))

class FloatingText:
    def __init__(self, text, x, y, font, color=GOLD, lifetime=35):
        self.text = text
        self.x = float(x)
        self.y = float(y)
        self.font = font
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.y -= 1.2
        self.lifetime -= 1

    @property
    def is_alive(self):
        return self.lifetime > 0

    def draw(self, surface):
        if not self.is_alive:
            return
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        txt_surf = self.font.render(self.text, True, self.color)
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        
        # Alpha rendering
        txt_surf.set_alpha(alpha)
        shadow_surf.set_alpha(alpha)
        
        w, h = txt_surf.get_size()
        pos = (int(self.x - w / 2), int(self.y - h / 2))
        surface.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
        surface.blit(txt_surf, pos)

class ParticleManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []

    def clear(self):
        self.particles.clear()
        self.floating_texts.clear()

    def emit_flap(self, x, y):
        # White / soft translucent dust puff behind bird
        for _ in range(4):
            vx = random.uniform(-2.5, -0.5)
            vy = random.uniform(0.5, 2.5)
            size = random.uniform(3.0, 6.0)
            color = (255, 255, 255, 180)
            lifetime = random.randint(12, 20)
            self.particles.append(Particle(x - 12, y + 6, vx, vy, size, color, lifetime, shrink=True))

    def emit_score(self, x, y, font=None):
        # Golden stars / sparkles
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 5.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2.5, 5.0)
            color = random.choice([GOLD, (255, 255, 150), (255, 240, 200)])
            lifetime = random.randint(18, 30)
            self.particles.append(Particle(x, y, vx, vy, size, color, lifetime, shrink=True, gravity=0.15))
        
        if font:
            self.floating_texts.append(FloatingText("+1", x, y - 10, font, color=GOLD))

    def emit_death(self, x, y):
        # Feather burst & impact particles
        colors = [(255, 200, 35), (240, 140, 30), (255, 255, 255), (210, 50, 40)]
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 6.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(3.0, 6.5)
            color = random.choice(colors)
            lifetime = random.randint(20, 38)
            self.particles.append(Particle(x, y, vx, vy, size, color, lifetime, shrink=True, gravity=0.2))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive]

        for ft in self.floating_texts:
            ft.update()
        self.floating_texts = [ft for ft in self.floating_texts if ft.is_alive]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface)
