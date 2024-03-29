import math
import pygame

from utils import degrees_to_radians, crossing_of_lines

small_number: float = 0.001

side_lines: list[tuple[int, int, int, int]] = [
    (1, 0, 0, 0), (1, 1, 1, 0), (1, 1, 0, 1), (0, 1, 0, 0)
]


class Face:
    vertices: list[pygame.Vector3]
    color: str

    def __init__(self, *vertices: tuple[float, float, float], color: str = "green") -> None:
        self.vertices = []

        self.color = color

        for coords in vertices:
            self.vertices.append(pygame.Vector3(coords[0], coords[1], coords[2]))


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
            Face((x1, y1, z1), (x1, y2, z1), (x2, y2, z1), (x2, y1, z1), color=self.color),
            Face((x1, y1, z2), (x1, y2, z2), (x2, y2, z2), (x2, y1, z2), color=self.color),
            Face((x1, y2, z1), (x1, y2, z2), (x2, y2, z2), (x2, y2, z1), color=self.color),
            Face((x1, y1, z1), (x1, y1, z2), (x2, y1, z2), (x2, y1, z1), color=self.color),
            Face((x1, y1, z1), (x1, y1, z2), (x1, y2, z2), (x1, y2, z1), color=self.color),
            Face((x2, y1, z1), (x2, y1, z2), (x2, y2, z2), (x2, y2, z1), color=self.color),
        ]


class Camera:
    position: pygame.Vector3
    screen_distance: float
    screen: pygame.Surface
    res: tuple[float, float]

    render_queue: list[Face]

    rotation: pygame.Vector2
    mouse_sensitivity: float

    def __init__(self, fov: float, res: tuple[float, float],
                 screen: pygame.Surface, mouse_sensitivity: float = 10) -> None:
        self.res = res
        self.screen_distance = self.calc_fov(fov)
        self.screen = screen
        self.rotation = pygame.Vector2(-90, 0)
        self.mouse_sensitivity = mouse_sensitivity

        self.render_queue = []

        self.position = pygame.Vector3(0, 0, 0)

    def calc_fov(self, deg: float) -> float:
        return (self.res[0] / 2) / (math.tan(degrees_to_radians(deg) / 2))

    def rotate_point(self, point: pygame.Vector3) -> tuple[float, float, float]:
        x, y, z = point
        x -= self.position.x
        y -= self.position.y
        z -= self.position.z
        rotation_x = degrees_to_radians(self.rotation.x)
        rotation_y = degrees_to_radians(self.rotation.y)

        mid_rot_x = y * math.cos(rotation_x) - x * math.sin(rotation_x)
        rot_y = x * math.cos(rotation_x) + y * math.sin(rotation_x)

        rot_x = mid_rot_x * math.cos(rotation_y) - z * math.sin(rotation_y)
        rot_z = mid_rot_x * math.sin(rotation_y) + z * math.cos(rotation_y)

        rot_x += self.position.x
        rot_y += self.position.y
        rot_z += self.position.z

        return rot_x, rot_y, rot_z

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

        return math.sqrt(
            (avg_x - self.position.x) ** 2 + (avg_y - self.position.y) ** 2 + (avg_z - self.position.z) ** 2)

    def render_face(self, face: Face):
        pre_points: list[tuple[float, float, int]] = [self.get_point(point_) for point_ in face.vertices]

        if not any([point[2] == 0 for point in pre_points]):
            return

        points: list[tuple[float, float]] = []
        for index, point in enumerate(pre_points):
            if point[2] == 0:
                points.append((point[0], point[1]))
                continue

            for i in [-1, 1]:
                if len(pre_points) == index + i:
                    ref_point = 0
                else:
                    ref_point = index + i

                if pre_points[ref_point][2] == 0:
                    reference: tuple[float, float, int] = pre_points[ref_point]
                else:
                    continue

                x: float = point[0]
                if point[2] & 0b001 > 0:
                    if point[2] & 0b100 == 0:
                        if x < self.res[0] / 2:
                            x *= -1
                        else:
                            x = self.res[0] + (self.res[0] - x)

                y: float = point[1]

                point: tuple[float, float, int] = (x, y, point[2])

                for side in range(4):
                    current_side: tuple[int, int, int, int] = side_lines[side]

                    projection = self.project_point_from_outside(current_side, reference, point)

                    if projection is None:
                        continue

                    points.append((projection.x, projection.y))

        while len(points) <= 2:
            points.append(points[0])

        pygame.draw.polygon(self.screen, face.color, points, width=0)

    def project_point_from_outside(self, current_side: tuple[int, int, int, int],
                                   reference: tuple[float, float, int], point: tuple[float, float, int]) \
            -> pygame.Vector2 | None:
        C: pygame.Vector2 = pygame.Vector2(self.res[0] * current_side[0], self.res[1] * current_side[1])
        D: pygame.Vector2 = pygame.Vector2(self.res[0] * current_side[2], self.res[1] * current_side[3])

        re: pygame.Vector2 = pygame.Vector2(reference[0], reference[1])
        p: pygame.Vector2 = pygame.Vector2(point[0], point[1])

        alpha: float | None = crossing_of_lines(D, C, p, re)

        if alpha is None:
            return None

        x = p.x + alpha * (p.x - re.x)
        y = p.y + alpha * (p.y - re.y)

        return pygame.Vector2(x, y)

    def get_point(self, point: pygame.Vector3) -> tuple[float, float, int]:
        x, y, z = self.rotate_point(point)

        x_dist = x - self.position.x
        y_dist = y - self.position.y
        z_dist = z - self.position.z

        y_mid = (y_dist * self.screen_distance) / (x_dist + small_number)
        z_mid = (z_dist * self.screen_distance) / (x_dist + small_number)

        if x_dist < 0:
            z_mid *= -1
            y_mid *= -1

        x_pos = (self.res[0] / 2) - y_mid
        y_pos = (self.res[1] / 2) - z_mid

        on_screen: int = 0b000

        if x_pos < 0 or x_pos > self.res[0]:
            on_screen |= 0b100
        if y_pos < 0 or y_pos > self.res[1]:
            on_screen |= 0b010
        if x_dist < 0:
            on_screen |= 0b001

        return x_pos, y_pos, on_screen

    def rotate(self, x: float, y: float) -> None:
        self.rotation.x += x * (self.mouse_sensitivity / 100)
        self.rotation.y += y * (self.mouse_sensitivity / 100)

        self.rotation.x %= 360


class Player:
    position: pygame.Vector3
    original_height: float
    height: float
    jump_height: float
    crouch_multiplier: float

    camera: Camera

    def __init__(self, starting_position: pygame.Vector3, camera: Camera):
        self.position = starting_position
        self.original_height = 1
        self.height = self.original_height
        self.jump_height = 1
        self.crouch_multiplier = 0.5

        self.camera = camera

    def move(self, keys, dt):
        rotation = degrees_to_radians(360 - self.camera.rotation.x)

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

        if keys[pygame.K_LCTRL]:
            self.height = self.original_height * self.crouch_multiplier
        else:
            self.height = self.original_height

        self.camera.position.z = self.height + self.position.z

        mouse_x, mouse_y = pygame.mouse.get_rel()

        self.camera.rotate(mouse_x, mouse_y)

        self.camera.position.x = self.position.x
        self.camera.position.y = self.position.y


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)

    dt = 0

    cube = Cuboid((1, 3, 0), (2, 4, 1), "red")
    cube2 = Cuboid((3, 1, 0), (4, 2, 1), "blue")
    cube3 = Cuboid((-1, -3, 0), (0, -2, 1), "green")
    cube4 = Cuboid((-3, -1, 0), (-2, 0, 1), "yellow")

    camera = Camera(120, (1280, 720), screen, 5)
    player: Player = Player(pygame.Vector3(0, 0, 0), camera)

    running = True
    paused = False

    camera.init_cuboid(cube)
    camera.init_cuboid(cube3)
    camera.init_cuboid(cube2)
    camera.init_cuboid(cube4)

    while running:
        pygame.event.set_grab(True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    pygame.event.set_grab(paused)
                    pygame.mouse.set_visible(paused)

                    screen.fill("lightgray")
                    pygame.display.flip()

        if paused:
            continue

        screen.fill("white")

        keys = pygame.key.get_pressed()
        player.move(keys, dt)

        camera.render()

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
