import pygame

import helper
import simulation
import tilemap
import ui
from generator import two_points_to_road


def main():
    pygame.init()


    screen = pygame.display.set_mode((1920, 1080))

    clock = pygame.time.Clock()
    current_time = clock.get_time(); dt = 0

    game_map = tilemap.TileMap(16)

    tool_state = "road_building"
    # current_road_points, drawing_road_points
    road_points = ([], {})

    offset_x, offset_y = 0.0, 0.0
    move_speed = 5
    current_zoom = 1.0
    target_zoom = 1.0
    zoom_speed = 0.2
    zoom_anchor = (0, 0)
    world_anchor = (0, 0)
    tile_size = 50

    tick_counter = 0
    running = True
    while running:
        # Fill screen gray
        screen.fill((10, 10, 10))

        # Input tick
        mouse_pos = pygame.mouse.get_pos()
        hovered_tile = helper.screen_space_to_tile_space(mouse_pos, offset_x, offset_y, current_zoom, tile_size)

        # Simulation tick
        if (tick_counter & 0b10) == 0:
            simulation.tick(dt)




        # Draw screen (1 frame)
        ui.draw(screen, game_map, tile_size, offset_x, offset_y, current_zoom, hovered_tile, road_points)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            offset_x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            offset_x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            offset_y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            offset_y += move_speed

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tool_state == "zoning":
                    if event.button == 3:
                        game_map.place_tile(hovered_tile[0], hovered_tile[1], "residential")
                    elif event.button == 2:
                        game_map.place_tile(hovered_tile[0], hovered_tile[1], "commercial")
                    elif event.button == 1:
                        game_map.place_tile(hovered_tile[0], hovered_tile[1], "industrial")
                elif tool_state == "road_building":
                    if event.button == 1:
                        pos = helper.screen_space_to_world_space(mouse_pos, offset_x, offset_y, current_zoom)
                        # Build road with 2 points; A -> B
                        if len(road_points[0]) == 0:
                            # Point A
                            road_points[0].append(pos)
                        elif len(road_points[0]) == 1:
                            # Point B
                            road_points[0].append(pos)

                            used_ids = set(road_points[1].keys())
                            new_id = 0
                            while new_id in used_ids:
                                new_id += 1

                            road_points[1][new_id] = two_points_to_road(road_points[0])
                            road_points[0].clear()


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    if tool_state == "zoning":
                        tool_state = "road_building"
                    elif tool_state == "road_building":
                        tool_state = "zoning"

                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEWHEEL:
                zoom_factor = 1.1 ** event.y
                target_zoom *= zoom_factor
                target_zoom = max(0.1, min(5.0, target_zoom))

                # Get mouse world position BEFORE zoom
                mx, my = mouse_pos
                wx = mx / current_zoom + offset_x
                wy = my / current_zoom + offset_y

                zoom_anchor = (mx, my)
                world_anchor = (wx, wy)

        def lerp(a, b, t):
            return a + (b - a) * t

        # In update section
        if abs(current_zoom - target_zoom) > 0.001:
            current_zoom = lerp(current_zoom, target_zoom, zoom_speed)
            mx, my = zoom_anchor
            wx, wy = world_anchor
            offset_x = wx - mx / current_zoom
            offset_y = wy - my / current_zoom

        # Get time difference between last frame and now
        last_time = current_time
        current_time = clock.get_time()
        dt = current_time - last_time
        tick_counter += 1
        pygame.display.flip()
        clock.tick(100)

if __name__ == "__main__":
    main()
