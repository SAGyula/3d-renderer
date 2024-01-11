import math
import pygame

small_number: float = 0.001


def degrees_to_radians(degs: float) -> float:
    return degs * (math.pi / 180)


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

    color: str

    faces: list[Face]

    def __init__(self, cor1: tuple[float, float, float], cor2: tuple[float, float, float], color: str) -> None:
        self.cor1 = pygame.Vector3(cor1)
        self.cor2 = pygame.Vector3(cor2)
        self.faces = []
        self.color = color

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
        x -= self.position.x
        y -= self.position.y
        rotation = degrees_to_radians(self.rotation.x)

        rot_x = (y * math.cos(rotation) - x * math.sin(rotation)) + self.position.x
        rot_y = (x * math.cos(rotation) + y * math.sin(rotation)) + self.position.y

        return rot_x, rot_y, z

    def render_cuboid(self, object_: Cuboid) -> None:
        for face in object_.faces:
            self.render_face(face, object_.color)

    def render_face(self, face: Face, color: str):
        points: list[tuple[float, float]] = [self.get_point(i) for i in face.vertices]

        pygame.draw.polygon(self.screen, color, points, width=0)

    def get_point(self, point: pygame.Vector3) -> tuple[float, float]:
        x, y, z = self.rotate_point(point)

        x_dist = x - self.position.x
        y_dist = y - self.position.y
        z_dist = z - self.position.z

        y_pos = self.res[1] / 2 - (y_dist * self.screen_distance) / (x_dist + small_number)
        z_pos = self.res[0] / 2 - (z_dist * self.screen_distance) / (x_dist + small_number)

        return y_pos, z_pos

    def try_move(self, keys, dt):
        rotation = degrees_to_radians(360 - self.rotation.x)

        if keys[pygame.K_w]:
            self.position.x += 10 * dt * math.sin(rotation)
            self.position.y += 10 * dt * math.cos(rotation)
        if keys[pygame.K_s]:
            self.position.x -= 10 * dt * math.sin(rotation)
            self.position.y -= 10 * dt * math.cos(rotation)
        if keys[pygame.K_a]:
            self.position.y += 10 * dt
        if keys[pygame.K_d]:
            self.position.y -= 10 * dt

        if keys[pygame.K_LEFT]:
            self.rotation.x -= 50 * dt
        if keys[pygame.K_RIGHT]:
            self.rotation.x += 50 * dt


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    dt = 0

    cube = Cuboid((1, 1, 1), (3, 2, 2), "blue")
    cube2 = Cuboid((1, 1, 1), (2, 3, 2), "green")
    cube3 = Cuboid((1, 1, 1), (2, 2, 3), "yellow")
    camera = Camera(pygame.Vector3(-2, 0, 1), 800, (1280, 720), screen)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("white")

        keys = pygame.key.get_pressed()
        camera.try_move(keys, dt)

        camera.render_cuboid(cube)
        camera.render_cuboid(cube3)
        camera.render_cuboid(cube2)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()