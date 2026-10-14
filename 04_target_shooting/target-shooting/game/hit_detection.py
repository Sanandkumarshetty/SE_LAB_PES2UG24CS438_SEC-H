"""
hit_detection: figures out whether a click landed on a target.
"""


def check_hit(targets, click_pos):
    """
    Returns the target that was clicked, or None if the click missed
    every target.
    """
    for target in targets:
        # TASK 1 UPDATE: test the click's distance from the circle's center.
        # This accepts only points inside the visible circular target.
        offset_x = click_pos[0] - target.x
        offset_y = click_pos[1] - target.y
        if offset_x ** 2 + offset_y ** 2 <= target.radius ** 2:
            return target
    return None
