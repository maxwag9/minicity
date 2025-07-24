import pygame

import helper

tile_types={
    "residential": (50, 255, 50),
    "commercial": (50, 200, 255),
    "industrial": (100, 255, 255),
    "asphalt": (100, 100, 100),

}


def draw(screen, game_map, tile_size, offset_x, offset_y, current_zoom, hovered_tile, road_points, mouse_pos, tool_mode, possible_hovered_road_points, hovered_points):
    all_tiles = game_map.get_all_tiles(screen)
    zoomed_tile_size = tile_size * current_zoom

    for tile in all_tiles:
        world_x, world_y= helper.tile_space_to_world_space((tile.x, tile.y), tile_size)
        screen_x = (world_x - offset_x) * current_zoom
        screen_y = (world_y - offset_y) * current_zoom
        pygame.draw.rect(screen, tile_types[tile.type], (screen_x, screen_y, zoomed_tile_size, zoomed_tile_size))
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, zoomed_tile_size, zoomed_tile_size), 1)

    if hovered_tile:
        screen_x, screen_y = helper.tile_space_to_screen_space(hovered_tile, offset_x, offset_y, current_zoom, tile_size)
        pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, zoomed_tile_size, zoomed_tile_size), 2)

    current_road_points = road_points[0]
    all_road_points = road_points[1].values()
    if current_road_points:
        for road_point in current_road_points:
            pygame.draw.circle(screen, (0, 120, 230), helper.world_space_to_screen_space(road_point, offset_x, offset_y, current_zoom), 8 * current_zoom)
    if all_road_points:
        for all_single_road_points in all_road_points:
            for single_road_point in all_single_road_points:
                road_point = single_road_point[1]
                pygame.draw.circle(screen, (20, 120, 230), helper.world_space_to_screen_space(road_point, offset_x, offset_y, current_zoom), 5 * current_zoom)
    if tool_mode == "straight_road":
        pygame.draw.circle(screen, (20, 230, 230), mouse_pos, 7 * current_zoom, 2)
    elif tool_mode == "curved_road":
        pygame.draw.circle(screen, (200, 230, 230), mouse_pos, 7 * current_zoom, 2)
    if possible_hovered_road_points:
        for world_pos, _ in possible_hovered_road_points:
            pygame.draw.circle(screen, (20, 120, 230),
                               helper.world_space_to_screen_space(world_pos, offset_x, offset_y, current_zoom),
                               8 * current_zoom)
    if hovered_points:
        for world_pos, _ in hovered_points:
            pygame.draw.circle(screen, (200, 220, 230),
                               helper.world_space_to_screen_space(world_pos, offset_x, offset_y, current_zoom),
                               8 * current_zoom)