"""
Target: a circular target the player clicks on. (x, y) is the CENTER
of the circle - this matters for how it's drawn vs. how it's hit-tested.
"""

import pygame


class Target:
    def __init__(self, x, y, radius=28, color=(230, 90, 70), velocity=(0, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        # TASK 2 UPDATE: each target stores its own movement direction and speed.
        self.velocity_x, self.velocity_y = velocity

    def move(self, play_width, play_height):
        """Move one frame and bounce when the circle reaches an edge."""
        # TASK 2 UPDATE: move the circle's center using its assigned velocity.
        self.x += self.velocity_x
        self.y += self.velocity_y

        # TASK 2 UPDATE: keep the whole circle on-screen and reverse at edges.
        if self.x - self.radius < 0 or self.x + self.radius > play_width:
            self.x = max(self.radius, min(self.x, play_width - self.radius))
            self.velocity_x *= -1
        if self.y - self.radius < 0 or self.y + self.radius > play_height:
            self.y = max(self.radius, min(self.y, play_height - self.radius))
            self.velocity_y *= -1

    def get_bounding_rect(self):
        """A square bounding box around the circle - NOT the same
        shape as the actual circle, and easy to build incorrectly."""
        return pygame.Rect(self.x, self.y, self.radius * 2, self.radius * 2)
