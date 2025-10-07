import pygame

import helper
import simulation
import tilemap
import ui
import input
from menu_file import MenuManager
from roads import RoadManager


def main():
    pygame.init()

    screen = pygame.display.set_mode((1920, 1080))

    clock = pygame.time.Clock()
    current_time = clock.get_time()
    dt = 0

    menu = MenuManager()
    menu.current_menu = menu.MenuScreen("Main Menu", [menu.Button((0, 255, 0), (500, 300), (800, 400))])
    inputmngr = input.InputManager()
    game_map = tilemap.TileMap(16)

    zoom_offset_x, zoom_offset_y = 0.0, 0.0  # modified during zooming
    pan_offset_x, pan_offset_y = 0.0, 0.0  # modified during panning

    move_speed = 10
    target_zoom = 1.0
    zoom_speed = 0.2
    zoom_anchor = (0, 0)
    world_anchor = (0, 0)

    camera = helper.Camera(offset_x = 0.0, offset_y = 0.0, zoom = 1.0, tile_size = 50)

    tool_mode = "straight_road"
    road_type = "2_lane_bidirectional"

    # current_road_points, drawing_road_points, roads_to_build, tile_to_point
    road_points = RoadManager(camera)
    possible_hovered_road_points = []
    hovered_points = []
    point_size = 5

    tick_counter = 0
    running = True
    while running:
        running = inputmngr.handle_pygame_events()
        # Fill screen gray
        screen.fill((30, 30, 30))
        offsets_to_add = [0.0, 0.0]

        # Input tick
        mouse_pos = inputmngr.get_mouse_pos()
        hovered_tile = camera.screen_to_tile(mouse_pos)
        # Simulation tick
        if (tick_counter & 0b10) == 0:
            possible_hovered_road_points, hovered_points = simulation.tick(dt, road_points, mouse_pos, hovered_tile, camera)

        move_speed_zoom = move_speed / camera.zoom
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            offsets_to_add[0] -= move_speed_zoom
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            offsets_to_add[0] += move_speed_zoom
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            offsets_to_add[1] -= move_speed_zoom
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            offsets_to_add[1] += move_speed_zoom

        if tool_mode == "delete":
            if inputmngr.mouse_buttons_pressed["left"]:
                helper.remove_tight_points(road_points=road_points, hovered_points=hovered_points)
        elif tool_mode == "zoning":
            if inputmngr.mouse_buttons_pressed["right"]:
                game_map.place_tile(hovered_tile[0], hovered_tile[1], "residential")
            if inputmngr.mouse_buttons_pressed["middle"]:
                game_map.place_tile(hovered_tile[0], hovered_tile[1], "commercial")
            if inputmngr.mouse_buttons_pressed["left"]:
                game_map.place_tile(hovered_tile[0], hovered_tile[1], "industrial")
        elif tool_mode == "straight_road":
            if inputmngr.mouse_buttons_pressed["left"]:
                road_points.build_road((tool_mode, road_type), mouse_pos, point_size, road_points, hovered_points)

        elif tool_mode == "curved_road":
            if inputmngr.mouse_buttons_pressed["left"]:
                road_points.build_road((tool_mode, road_type), mouse_pos, point_size,
                                       road_points, hovered_points)

        if inputmngr.key_released("q"):
            if tool_mode == "zoning":
                tool_mode = "straight_road"
            elif tool_mode == "straight_road":
                tool_mode = "curved_road"
            elif tool_mode == "curved_road":
                tool_mode = "delete"
            elif tool_mode == "delete":
                tool_mode = "zoning"
        if inputmngr.keys_just_released: print(inputmngr.keys_just_released)
        if inputmngr.mouse_scroll_changed:
            mouse_scroll = inputmngr.get_mouse_scroll()
            zoom_factor = 1.1 ** mouse_scroll[1]
            target_zoom *= zoom_factor
            target_zoom = max(0.1, min(5.0, target_zoom))

            # Get mouse world position BEFORE zoom
            mx, my = mouse_pos
            wx = mx / camera.zoom + zoom_offset_x
            wy = my / camera.zoom + zoom_offset_y

            zoom_anchor = (mx, my)
            world_anchor = (wx, wy)

        def lerp(a, b, t):
            return a + (b - a) * t

        # In update section
        if abs(camera.zoom - target_zoom) > 0.001:
            camera.zoom = lerp(camera.zoom, target_zoom, zoom_speed)
            mx, my = zoom_anchor
            wx, wy = world_anchor
            zoom_offset_x = wx - mx / camera.zoom
            zoom_offset_y = wy - my / camera.zoom

        pan_offset_x += offsets_to_add[0]
        pan_offset_y += offsets_to_add[1]
        camera.offset_x = zoom_offset_x + pan_offset_x
        camera.offset_y = zoom_offset_y + pan_offset_y

        # Draw screen (1 frame)
        ui.draw(screen, game_map, hovered_tile, road_points, mouse_pos,
                tool_mode, possible_hovered_road_points, hovered_points, menu, camera)

        # Get time difference between last frame and now
        last_time = current_time
        current_time = clock.get_time()
        dt = current_time - last_time
        tick_counter += 1
        pygame.display.flip()
        clock.tick(100)

        inputmngr.clear_transient_states()
    raise SystemExit


if __name__ == "__main__":
    main()

