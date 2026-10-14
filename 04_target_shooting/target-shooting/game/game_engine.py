"""
GameEngine: owns the targets and handles player clicks.

Starter version: a few static targets that respawn elsewhere when
clicked (correctly or not, depending on the hit-detection bug) - no
movement, no score/combo, no timer yet. That's Tasks 2-4.
"""

import math
import random

from game.target import Target
from game.hit_detection import check_hit
from game.renderer import WIDTH, HEIGHT

NUM_TARGETS = 3
TARGET_RADIUS = 28
# TASK 2 UPDATE: targets are assigned one of several visibly different speeds.
TARGET_VELOCITIES = [(-2, 2), (3, 1), (-1, -4), (4, -3)]
# TASK 3 UPDATE: every successful shot is worth this many base points.
BASE_HIT_POINTS = 100
# TASK 4 UPDATE: each shooting round lasts for thirty real-time seconds.
ROUND_DURATION_SECONDS = 30


class GameEngine:
    def __init__(self):
        # TASK 4 UPDATE: initialise all round state in one reusable reset method.
        self.reset_round()

    def reset_round(self):
        """Start a fresh timed round with new targets and scoring state."""
        # TASK 4 UPDATE: reset the timer, result state, and every round statistic.
        self.targets = [self._random_target() for _ in range(NUM_TARGETS)]
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.combo_multiplier = 1
        self.time_remaining = ROUND_DURATION_SECONDS
        self.round_over = False

    def _random_target(self):
        x = random.randint(TARGET_RADIUS + 10, WIDTH - TARGET_RADIUS - 10)
        y = random.randint(TARGET_RADIUS + 10, HEIGHT - TARGET_RADIUS - 10)
        # TASK 2 UPDATE: a respawned target receives a random movement pattern.
        velocity = random.choice(TARGET_VELOCITIES)
        return Target(x, y, radius=TARGET_RADIUS, velocity=velocity)

    def handle_click(self, pos):
        # TASK 4 UPDATE: no shots count once the countdown has finished.
        if self.round_over:
            return

        target = check_hit(self.targets, pos)
        if target is not None:
            self.hits += 1
            # TASK 3 UPDATE: award the current combo value, then grow the streak.
            self.score += BASE_HIT_POINTS * self.combo_multiplier
            self.combo_multiplier += 1
            self.targets.remove(target)
            self.targets.append(self._random_target())
        else:
            self.misses += 1
            # TASK 3 UPDATE: any missed shot breaks the current combo.
            self.combo_multiplier = 1

    def update(self, delta_time):
        # TASK 4 UPDATE: reduce the countdown using elapsed real time.
        if self.round_over:
            return

        self.time_remaining = max(0, self.time_remaining - delta_time)
        if self.time_remaining == 0:
            self.round_over = True
            return

        # TASK 2 UPDATE: update every target once per frame.
        for target in self.targets:
            target.move(WIDTH, HEIGHT)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.targets)
        renderer.draw_text(surface, font, f"Hits: {self.hits}  Misses: {self.misses}", (10, 10))
        # TASK 3 UPDATE: keep score and the next-hit combo multiplier visible.
        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}  Combo: {self.combo_multiplier}x",
            (10, 38),
        )
        # TASK 4 UPDATE: show a whole-second countdown while the round is active.
        renderer.draw_text(surface, font, f"Time: {math.ceil(self.time_remaining)}s", (10, 66))
        if self.round_over:
            # TASK 4 UPDATE: make the result and restart control clear at round end.
            renderer.draw_banner(surface, font, f"Round over! Final score: {self.score}")
            renderer.draw_text(surface, font, "Press R to play again", (245, 280))
