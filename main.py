import os
import sys
from io import BytesIO
import pygame
import pygame_gui
from api_lib import *

KEYS = (pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN)


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
        self.lon, self.lat = get_toponym_coord(get_toponym(geocode('Миасс')))
        self.point = None
        self.postal = True
        self.address = None
        self.layer = 'map'
        self.z = 17

        self.manager = pygame_gui.UIManager(SIZE)
        self.layers_select = (
            pygame_gui.elements.UIDropDownMenu(self.options, self.options[0], pygame.Rect(10, 10, 200, 30),
                                               self.manager))
        self.search_field = pygame_gui.elements.UITextEntryLine(pygame.Rect(130, 410, 300, 30), self.manager)
        self.result_field = pygame_gui.elements.UILabel(pygame.Rect(20, 380, 610, 30), '', self.manager)
        self.clear_button = pygame_gui.elements.UIButton(pygame.Rect(430, 410, 100, 30), 'Сброс', self.manager)
        self.postal_button = pygame_gui.elements.UIButton(pygame.Rect(530, 410, 100, 30), 'Скрыть', self.manager)
        self.postal_button.hide()
        self.update_map()

    def update_map(self):
        map_params = {
            "ll": ",".join(map(str, (self.lon, self.lat))),
            "z": self.z,
            "l": self.layer,
            "size": '650,450',
        }
        if self.point is not None:
            map_params["pt"] = ",".join(map(str, self.point)) + ",flag"
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
            if event.key == pygame.K_RETURN:
                self.search()
            if event.key in KEYS:
                self.update_map()
        self.manager.process_events(event)

    def search(self):
        text = self.search_field.get_text()
        if self.search_field.is_focused and text:
            try:
                toponym = get_toponym(geocode(text))
                self.lon, self.lat = get_toponym_coord(toponym)
                self.address = get_toponym_address(toponym)
                self.result_field.set_text(
                    f'{self.address[1]}, {self.address[0]}' if self.address[1] else self.address[0])
                self.postal_button.show()
                self.point = self.lon, self.lat
            except IndexError:
                self.result_field.set_text("Ничего не найдено")
                self.point = None
                self.address = None
                self.postal_button.hide()
                self.search_field.focus()

    def gui_event_handler(self, event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.layers_select:
                self.layer = event.text
                self.update_map()
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.clear_button:
                self.clear_search()
            if event.ui_element == self.postal_button and self.address:
                self.switch_postal()

    def switch_postal(self):
        self.postal = not self.postal
        self.postal_button.set_text("Скрыть" if self.postal else 'Показать')
        if self.postal:
            self.result_field.set_text(f'{self.address[1]}, {self.address[0]}' if self.address[1] else self.address[0])
        else:
            self.result_field.set_text(self.address[0])

    def clear_search(self):
        self.point = None
        self.address = None
        self.search_field.set_text('')
        self.result_field.set_text('')
        self.postal_button.hide()
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
        time_delta = clock.tick(25) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            app.event_handler(event)
            app.gui_event_handler(event)

        app.update_gui(time_delta)
        screen.fill('black')
        app.draw(screen)
        pygame.display.flip()
