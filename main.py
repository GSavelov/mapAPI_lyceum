import os
import sys
from io import BytesIO
import pygame
from api_lib import get_static


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class BigMap:
    def __init__(self):
        self.image = None
        self.ll = 60.153191, 55.156353
        self.layer = 'map'
        self.z = 17
        self.update_map()

    def update_map(self):
        map_params = {
            "ll": ",".join(map(str, self.ll)),
            'z': self.z,
            "l": "map",
            'size': '650,450'
        }
        image = BytesIO(get_static(**map_params))
        self.image = pygame.image.load(image)

    def event_handler(self, event):
        pass

    def draw(self, surf):
        surf.blit(self.image, (0, 0))


if __name__ == '__main__':
    pygame.init()
    SIZE = W, H = 650, 450
    screen = pygame.display.set_mode(SIZE)
    app = BigMap()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            app.event_handler(event)

        screen.fill('black')
        app.draw(screen)
        pygame.display.flip()
