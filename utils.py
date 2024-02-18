import pygame
import math


def degrees_to_radians(degs: float) -> float:
    return degs * (math.pi / 180)


def crossing_of_lines(d: pygame.Vector2, c: pygame.Vector2, p: pygame.Vector2, re: pygame.Vector2) -> float | None:
    a = (d.x - c.x) * (c.y - p.y) - (d.y - c.y) * (c.x - p.x)
    b = (d.x - c.x) * (re.y - p.y) - (d.y - c.y) * (re.x - p.x)
    c = (re.x - p.x) * (c.y - p.y) - (re.y - p.y) * (c.x - p.x)

    if b == 0:
        return None

    alpha: float = a / b
    beta: float = c / b

    if alpha >= 1 or alpha <= 0 or beta >= 1 or beta <= 0:
        return None

    return alpha
