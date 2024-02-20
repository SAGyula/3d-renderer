import math

import pygame


class BoxCollider:
    def __init__(self, boundary: tuple[pygame.Vector3, pygame.Vector3] | list[pygame.Vector3]) -> None:
        super().__init__()

        if not isinstance(boundary, list):
            self.boundary: tuple[pygame.Vector3, pygame.Vector3] = boundary
        elif isinstance(boundary, list):
            min_x: float = min(boundary, key=lambda i: i.x).x
            min_y: float = min(boundary, key=lambda i: i.y).y
            min_z: float = min(boundary, key=lambda i: i.z).z

            max_x: float = max(boundary, key=lambda i: i.x).x
            max_y: float = max(boundary, key=lambda i: i.y).y
            max_z: float = max(boundary, key=lambda i: i.z).z

            self.boundary: tuple[pygame.Vector3, pygame.Vector3] = (pygame.Vector3(min_x, min_y, min_z),
                                                                    pygame.Vector3(max_x, max_y, max_z))

    def collide_box(self, other: "BoxCollider") -> bool:
        return (
                self.boundary[0].x <= other.boundary[1].x and
                self.boundary[1].x >= other.boundary[0].x and
                self.boundary[0].y <= other.boundary[1].y and
                self.boundary[1].y >= other.boundary[0].y and
                self.boundary[0].z <= other.boundary[1].z and
                self.boundary[1].z >= other.boundary[0].z
        )

    def collide_sphere(self, other: "SphereCollider") -> bool:
        return get_distance(other, self) < other.radius


class SphereCollider:
    def __init__(self, center: pygame.Vector3, radius: float) -> None:
        super().__init__()

        self.center: pygame.Vector3 = center
        self.radius: float = radius

    def collide_box(self, other: "BoxCollider") -> bool:
        return get_distance(self, other) < self.radius

    def collide_sphere(self, sphere: "SphereCollider") -> bool:
        distance = math.sqrt(
            (self.center.x - sphere.center.x) * (self.center.x - sphere.center.x) +
            (self.center.y - sphere.center.y) * (self.center.y - sphere.center.y) +
            (self.center.z - sphere.center.z) * (self.center.z - sphere.center.z),
        )
        return distance < self.center.radius + sphere.center.radius


def get_distance(sphere: SphereCollider, box: BoxCollider) -> float:
    x = max(box.boundary[0].x, min(sphere.center.x, box.boundary[1].x))
    y = max(box.boundary[0].y, min(sphere.center.y, box.boundary[1].y))
    z = max(box.boundary[0].z, min(sphere.center.z, box.boundary[1].z))

    return math.sqrt((x - sphere.center.x) ** 2 + (y - sphere.center.y) ** 2 + (z - sphere.center.z) ** 2)
