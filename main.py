import os
import sys
from io import BytesIO
import pygame
import pygame_gui
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
    options = ['map', 'sat', 'sat,skl']

    def __init__(self):
        self.image = None
        self.lon, self.lat = 60.153191, 55.156353
        self.layer = 'map'
        self.z = 17

        self.manager = pygame_gui.UIManager(SIZE)
        self.layers_select = (
            pygame_gui.elements.UIDropDownMenu(self.options, self.options[0], pygame.Rect(10, 10, 200, 30),
                                               self.manager))
        self.update_map()

    def update_map(self):
        map_params = {
            "ll": ",".join(map(str, (self.lon, self.lat))),
            'z': self.z,
            "l": self.layer,
            'size': '650,450'
        }
        image = BytesIO(get_static(**map_params))
        self.image = pygame.image.load(image)

    def event_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                self.z = min(self.z + 1, 21)
            if event.key == pygame.K_PAGEDOWN:
                self.z = max(self.z - 1, 0)
            if event.key == pygame.K_LEFT:
                self.lon = (self.lon + 180 - 200 * 2 ** (-self.z)) % 360 - 180
            if event.key == pygame.K_RIGHT:
                self.lon = (self.lon + 180 + 200 * 2 ** (-self.z)) % 360 - 180
            if event.key == pygame.K_UP:
                self.lat = min(self.lat + 70 * 2 ** (-self.z), 90)
            if event.key == pygame.K_DOWN:
                self.lat = max(self.lat - 70 * 2 ** (-self.z), -90)
            self.update_map()
        self.manager.process_events(event)

    def gui_event_handler(self, event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.layers_select:
                self.layer = event.text
                self.update_map()

    def draw(self, surf):
        surf.blit(self.image, (0, 0))
        self.manager.draw_ui(surf)

    def update_gui(self, delta):
        self.manager.update(delta)


if __name__ == '__main__':
    pygame.init()
    SIZE = W, H = 650, 450
    screen = pygame.display.set_mode(SIZE)
    app = BigMap()

    clock = pygame.time.Clock()
    running = True
    while running:
        time_delta = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            app.event_handler(event)
            app.gui_event_handler(event)

        app.update_gui(time_delta)
        screen.fill('black')
        app.draw(screen)
        pygame.display.flip()
