import math

import pygame


class Face:
    vertices: list[pygame.Vector3]
    color: str

    def __init__(self, *vertices: tuple[float, float, float], color: str = "green") -> None:
        self.vertices = []

        self.color = color

        for coords in vertices:
            self.vertices.append(pygame.Vector3(coords[0], coords[1], coords[2]))

    def __str__(self) -> str:
        return str(self.vertices)

    def __repr__(self) -> str:
        return str(self.vertices)


class Cuboid:
    cor1: pygame.Vector3
    cor2: pygame.Vector3

    faces: list[Face]

    def __init__(self, cor1: tuple[float, float, float], cor2: tuple[float, float, float]) -> None:
        self.cor1 = pygame.Vector3(cor1)
        self.cor2 = pygame.Vector3(cor2)
        self.faces = []

        self.create_faces()

    def create_faces(self) -> None:
        x1, y1, z1 = self.cor1
        x2, y2, z2 = self.cor2
        self.faces = [
            Face((x1, y1, z1), (x1, y2, z1), (x2, y2, z1), (x2, y1, z1)),
            Face((x1, y1, z2), (x1, y2, z2), (x2, y2, z2), (x2, y1, z2)),
            Face((x1, y2, z1), (x1, y2, z2), (x2, y2, z2), (x2, y2, z1)),
            Face((x1, y1, z1), (x1, y1, z2), (x2, y1, z2), (x2, y1, z1)),
            Face((x1, y1, z1), (x1, y1, z2), (x1, y2, z2), (x1, y2, z1)),
            Face((x2, y1, z1), (x2, y1, z2), (x2, y2, z2), (x2, y2, z1)),
        ]


class Camera:
    position: pygame.Vector3
    screen_distance: float
    screen: pygame.Surface
    res: tuple[float, float]

    rotation: pygame.Vector2

    def __init__(self, starting_posion: pygame.Vector3, screen_distance: float, res: tuple[float, float],
                 screen: pygame.Surface) -> None:
        self.position = starting_posion
        self.screen_distance = screen_distance
        self.res = res
        self.screen = screen
        self.rotation = pygame.Vector2(0, 0)

    def rotate_point(self, point: pygame.Vector3) -> tuple[float, float, float]:
        x, y, z = point
        cam_dist: float = math.sqrt((self.position.x - x)**2 + (self.position.z - z)**2)
        rot_x = cam_dist * math.cos(x) * self.rotation.x
        rot_z = cam_dist * math.sin(z) * self.rotation.x
        return rot_x, y, rot_z

    def render_cuboid(self, object_: Cuboid) -> None:
        for face in object_.faces:
            self.render_face(face)

    def render_face(self, face: Face):
        points: list[tuple[float, float]] = [self.get_point(i) for i in face.vertices]

        pygame.draw.polygon(self.screen, "darkgreen", points, width=0)

    def get_point(self, point: pygame.Vector3) -> tuple[float, float]:
        x, y, z = self.rotate_point(point)

        x_dist = x - self.position.x
        y_dist = y - self.position.y
        z_dist = z - self.position.z

        y_pos = self.res[1] / 2 - (y_dist * self.screen_distance) / x_dist
        z_pos = self.res[0] / 2 - (z_dist * self.screen_distance) / x_dist

        return z_pos, y_pos

    def try_move(self, keys, dt):
        if keys[pygame.K_w]:
            self.position.x += 10 * dt
        if keys[pygame.K_s]:
            self.position.x -= 10 * dt
        if keys[pygame.K_a]:
            self.position.z += 10 * dt
        if keys[pygame.K_d]:
            self.position.z -= 10 * dt

        if keys[pygame.K_LEFT]:
            self.rotation.x += 10 * dt
        if keys[pygame.K_RIGHT]:
            self.rotation.x -= 10 * dt


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    dt = 0

    cube = Cuboid((1, 1, 1), (2, 2, 2))
    cube2 = Cuboid((2, 1, 2), (4, 4, 4))
    camera = Camera(pygame.Vector3(-2, 2, 0), 800, (1280, 720), screen)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("white")

        keys = pygame.key.get_pressed()
        camera.try_move(keys, dt)

        camera.render_cuboid(cube)
        camera.render_cuboid(cube2)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
