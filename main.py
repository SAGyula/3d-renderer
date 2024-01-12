import math
import pygame

small_number: float = 0.001


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
            Face((x1, y1, z1), (x1, y2, z1), (x2, y2, z1), (x2, y1, z1), color="green"),
            Face((x1, y1, z2), (x1, y2, z2), (x2, y2, z2), (x2, y1, z2), color="blue"),
            Face((x1, y2, z1), (x1, y2, z2), (x2, y2, z2), (x2, y2, z1), color="yellow"),
            Face((x1, y1, z1), (x1, y1, z2), (x2, y1, z2), (x2, y1, z1), color="pink"),
            Face((x1, y1, z1), (x1, y1, z2), (x1, y2, z2), (x1, y2, z1), color="gray"),
            Face((x2, y1, z1), (x2, y1, z2), (x2, y2, z2), (x2, y2, z1), color="purple"),
        ]


class Camera:
    position: pygame.Vector3
    screen_distance: float
    screen: pygame.Surface
    res: tuple[float, float]

    render_queue: list[Face]

    rotation: pygame.Vector2

    def __init__(self, starting_posion: pygame.Vector3, screen_distance: float, res: tuple[float, float],
                 screen: pygame.Surface) -> None:
        self.position = starting_posion
        self.screen_distance = screen_distance
        self.res = res
        self.screen = screen
        self.rotation = pygame.Vector2(0, 0)

        self.render_queue = []

    def rotate_point(self, point: pygame.Vector3) -> tuple[float, float, float]:
        x, y, z = point
        x -= self.position.x
        y -= self.position.y
        rotation = degrees_to_radians(self.rotation.x)

        rot_x = (y * math.cos(rotation) - x * math.sin(rotation)) + self.position.x
        rot_y = (x * math.cos(rotation) + y * math.sin(rotation)) + self.position.y

        return rot_x, rot_y, z

    def init_cuboid(self, object_: Cuboid) -> None:
        for face in object_.faces:
            self.render_queue.append(face)

    def render(self) -> None:
        self.render_queue.sort(key=self.face_sort, reverse=True)

        for face in self.render_queue:
            self.render_face(face)

    def face_sort(self, a: Face) -> float:
        avg_x = sum([i.x for i in a.vertices]) / len(a.vertices)
        avg_y = sum([i.y for i in a.vertices]) / len(a.vertices)
        avg_z = sum([i.z for i in a.vertices]) / len(a.vertices)

        return math.sqrt((avg_x - self.position.x) ** 2 + (avg_y - self.position.y) ** 2 + (avg_z - self.position.z) ** 2)

    def render_face(self, face: Face):
        points: list[tuple[float, float]] = [self.get_point(i) for i in face.vertices]

        pygame.draw.polygon(self.screen, face.color, points, width=0)

    def get_point(self, point: pygame.Vector3) -> tuple[float, float]:
        x, y, z = self.rotate_point(point)

        x_dist = x - self.position.x
        y_dist = y - self.position.y
        z_dist = z - self.position.z

        y_pos = self.res[0] / 2 - (y_dist * self.screen_distance) / (x_dist + small_number)
        z_pos = self.res[1] / 2 - (z_dist * self.screen_distance) / (x_dist + small_number)

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
            self.position.x += 10 * dt * math.cos(rotation)
            self.position.y -= 10 * dt * math.sin(rotation)
        if keys[pygame.K_d]:
            self.position.x -= 10 * dt * math.cos(rotation)
            self.position.y += 10 * dt * math.sin(rotation)

        if keys[pygame.K_LEFT]:
            self.rotation.x -= 50 * dt
        if keys[pygame.K_RIGHT]:
            self.rotation.x += 50 * dt


def degrees_to_radians(degs: float) -> float:
    return degs * (math.pi / 180)


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

    camera.init_cuboid(cube)
    camera.init_cuboid(cube3)
    camera.init_cuboid(cube2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("white")

        keys = pygame.key.get_pressed()
        camera.try_move(keys, dt)

        camera.render()

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
