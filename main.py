import pygame

first = True


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

        print(self.faces)


class Camera:
    position: pygame.Vector3
    screen_distance: float
    screen: pygame.Surface
    res: tuple[float, float]

    def __init__(self, starting_posion: pygame.Vector3, screen_distance: float, res: tuple[float, float],
                 screen: pygame.Surface) -> None:
        self.position = starting_posion
        self.screen_distance = screen_distance
        self.res = res
        self.screen = screen

    def render_cuboid(self, object_: Cuboid) -> None:
        for face in object_.faces:
            self.render_face(face)

    def render_face(self, face: Face):
        for i in range(len(face.vertices)):
            self.render_line(face.vertices[i - 1], face.vertices[i], face.color)
            if first:
                print(face.vertices[i - 1], face.vertices[i])

    def render_line(self, point1: pygame.Vector3, point2: pygame.Vector3, color):
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        x1_dist = x1 - self.position.x
        x2_dist = x2 - self.position.x
        y1_dist = y1 - self.position.y
        y2_dist = y2 - self.position.y
        z1_dist = z1 - self.position.z
        z2_dist = z2 - self.position.z

        y1_pos = self.res[1] / 2 - (y1_dist * self.screen_distance) / x1_dist
        z1_pos = self.res[0] / 2 - (z1_dist * self.screen_distance) / x1_dist

        y2_pos = self.res[1] / 2 - (y2_dist * self.screen_distance) / x2_dist
        z2_pos = self.res[0] / 2 - (z2_dist * self.screen_distance) / x2_dist

        if x1_dist >= 0 and x2_dist >= 0:
            pygame.draw.line(self.screen, color, (z1_pos, y1_pos), (z2_pos, y2_pos))

    def try_move(self, keys, dt):
        if keys[pygame.K_w]:
            self.position.x += 10 * dt
        if keys[pygame.K_s]:
            self.position.x -= 10 * dt
        if keys[pygame.K_a]:
            self.position.z += 10 * dt
        if keys[pygame.K_d]:
            self.position.z -= 10 * dt


def main() -> None:
    global first

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

        first = False

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
