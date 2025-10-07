import pygame.draw
from helper import Camera
from menu_file import MenuManager


def render_menu(screen, menu: MenuManager, camera: Camera):
    buttons = menu.current_menu.buttons
    for button in buttons:
        rect = button.rect
        x, y = camera.world_to_screen((rect[0], rect[1]))
        rect = (x, y, rect[2]*camera.zoom, rect[3]*camera.zoom)
        pygame.draw.rect(screen, button.color, rect)