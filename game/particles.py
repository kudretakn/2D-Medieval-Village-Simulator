"""Lightweight particle effects — smoke, sparkles, leaf drift."""
import pygame
import random
import math


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life',
                 'size', 'color', 'fade', 'gravity')

    def __init__(self, x, y, vx, vy, life, size, color, fade=True, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.fade = fade
        self.gravity = gravity


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_smoke(self, wx, wy, count=2):
        """Emit smoke puffs at world position."""
        for _ in range(count):
            self.particles.append(Particle(
                x=wx + random.uniform(-4, 4),
                y=wy,
                vx=random.uniform(-3, 3),
                vy=random.uniform(-15, -8),
                life=random.uniform(1.5, 3.0),
                size=random.uniform(3, 6),
                color=(180, 170, 160),
                fade=True,
                gravity=-2,
            ))

    def emit_sparkle(self, wx, wy, color=(255, 220, 80), count=3):
        """Emit production sparkles."""
        for _ in range(count):
            a = random.uniform(0, math.pi * 2)
            spd = random.uniform(10, 30)
            self.particles.append(Particle(
                x=wx + random.uniform(-6, 6),
                y=wy + random.uniform(-6, 6),
                vx=math.cos(a) * spd,
                vy=math.sin(a) * spd,
                life=random.uniform(0.4, 0.9),
                size=random.uniform(1.5, 3),
                color=color,
                fade=True,
                gravity=0,
            ))

    def emit_leaves(self, wx, wy, count=1):
        """Emit drifting leaves near forests."""
        for _ in range(count):
            self.particles.append(Particle(
                x=wx + random.uniform(-8, 8),
                y=wy + random.uniform(-12, 0),
                vx=random.uniform(-8, 8),
                vy=random.uniform(-2, 5),
                life=random.uniform(2.0, 4.0),
                size=random.uniform(2, 3),
                color=random.choice([(80, 160, 40), (60, 140, 30),
                                     (150, 140, 40), (170, 100, 30)]),
                fade=True,
                gravity=5,
            ))

    def emit_water_ripple(self, wx, wy):
        """Emit small water surface ripple."""
        self.particles.append(Particle(
            x=wx + random.uniform(-10, 10),
            y=wy + random.uniform(-10, 10),
            vx=0, vy=0,
            life=random.uniform(0.8, 1.5),
            size=random.uniform(2, 5),
            color=(180, 210, 255),
            fade=True,
            gravity=0,
        ))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += p.gravity * dt
            if p.fade:
                p.size *= (1 - dt * 0.3)
            alive.append(p)
        self.particles = alive

    def draw(self, screen, camera):
        for p in self.particles:
            sx, sy = camera.world_to_screen(p.x, p.y)
            sz = max(1, int(p.size * camera.zoom))
            alpha = max(0, min(255, int(255 * (p.life / p.max_life))))
            if 1 <= sz <= 2:
                col = (*p.color[:3], alpha)
                s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, col, (sz, sz), sz)
                screen.blit(s, (int(sx) - sz, int(sy) - sz))
            elif sz > 2:
                col = (*p.color[:3], alpha)
                s = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(s, col, (sz + 1, sz + 1), sz)
                screen.blit(s, (int(sx) - sz - 1, int(sy) - sz - 1))
