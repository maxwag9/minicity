import math

import pygame

import helper
from helper import screen_space_to_world_space, world_space_to_screen_space, get_vector
from roads import RoadManager

tile_types = {
    "residential": (50, 255, 50),
    "commercial": (50, 200, 255),
    "industrial": (100, 255, 255),
    "asphalt": (100, 100, 100),

}


def draw(screen, game_map, tile_size, offset_x, offset_y, current_zoom, hovered_tile, road_points: RoadManager,
         mouse_pos, tool_mode, possible_hovered_road_points, hovered_points):
    all_tiles = game_map.get_all_tiles(screen)
    zoomed_tile_size = tile_size * current_zoom
    def draw_vectors(point):
        point_pos_screen = helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom)
        def draw_arrow(arrow_vector, color, offset=0):
            start = pygame.Vector2(point_pos_screen)
            direction = pygame.Vector2(arrow_vector) * current_zoom
            end_point = start + direction

            if direction.length() == 0:
                direction = pygame.Vector2(1, 0)  # fallback
            else:
                direction = direction.normalize()

            # Perpendicular vector
            perp = pygame.Vector2(-direction.y, direction.x)

            offset *= current_zoom
            # Apply offset to both start & end
            start += perp * offset
            end_point += perp * offset

            # Draw shaft
            pygame.draw.line(screen, color, start, end_point, width=2)

            # Arrowhead size
            arrow_size = 6 * current_zoom

            # Arrowhead wings
            left_point = end_point - direction * arrow_size + perp * (arrow_size / 2)
            right_point = end_point - direction * arrow_size - perp * (arrow_size / 2)

            pygame.draw.polygon(screen, color, [end_point, left_point, right_point])
            # pygame.draw.circle(screen, (200, 220, 230), start, int(3 * current_zoom), int(1 * current_zoom))

        for other_point in point.sources:
            vector = pygame.Vector2(other_point.pos) - pygame.Vector2(point.pos)
            draw_arrow(vector, (255, 0, 0), offset=5)  # red arrow shifted right

        for other_point in point.destinations:
            vector = pygame.Vector2(other_point.pos) - pygame.Vector2(point.pos)
            draw_arrow(vector, (0, 255, 0), offset=10)  # green arrow shifted left

    for tile in all_tiles:
        world_x, world_y = helper.tile_space_to_world_space((tile.x, tile.y), tile_size)
        screen_x = (world_x - offset_x) * current_zoom
        screen_y = (world_y - offset_y) * current_zoom
        pygame.draw.rect(screen, tile_types[tile.type], (screen_x, screen_y, zoomed_tile_size, zoomed_tile_size))
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, screen_y, zoomed_tile_size, zoomed_tile_size), 1)

    if hovered_tile:
        screen_x, screen_y = helper.tile_space_to_screen_space(hovered_tile, offset_x, offset_y, current_zoom,
                                                               tile_size)
        pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, zoomed_tile_size, zoomed_tile_size), 2)

    current_road_points = road_points.current
    all_road_points = road_points.drawing.values()
    if current_road_points:
        for point in current_road_points:
            pygame.draw.circle(screen, (0, 120, 230),
                               helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom),
                               20 * current_zoom)
            draw_vectors(point)

    if all_road_points:
        # Precompute set of hovered world positions for fast lookup
        hovered_set = {p.pos for p in possible_hovered_road_points}
        # Render all road points
        for all_single_road_points in all_road_points:
            #print("all road points before function:", road_points)
            draw_road(screen, all_single_road_points, current_zoom, offset_x, offset_y)
            for point in all_single_road_points:

                # Use smaller radius if hovered
                radius = 4 if point.pos in hovered_set else point.point_size

                point_pos_screen = helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom)

                #pygame.draw.circle(screen, (20, 120, 230), point_pos_screen, radius * current_zoom)
                #draw_vectors(point)


    if tool_mode == "straight_road":
        pygame.draw.circle(screen, (20, 230, 230), mouse_pos, 7 * current_zoom, 2)
        pygame.draw.line(screen, (100, 100, 230), (mouse_pos[0]+40*current_zoom, mouse_pos[1]-35*current_zoom), (mouse_pos[0]+40*current_zoom, mouse_pos[1]+35*current_zoom), int(3*current_zoom))
    elif tool_mode == "curved_road":
        pygame.draw.circle(screen, (200, 230, 230), mouse_pos, 3 * current_zoom, 2)
        size = 80*current_zoom
        rect = (mouse_pos[0] - size*0.5, mouse_pos[1] - size*0.5, size, size)
        pygame.draw.arc(screen, (100, 100, 230), rect, math.radians(350), math.radians(100), int(2*current_zoom))

    if hovered_points:
        for point in hovered_points:
            pygame.draw.circle(screen, (200, 220, 230),
                               helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom),
                               3 * current_zoom)


def draw_road(screen, road_points, current_zoom, offset_x, offset_y, color=(55, 55, 50), half_width=15):
    if len(road_points) < 2:
        return

    left_side_collective = []
    right_side_collective = []
    median_collective = []
    for i, road_point in enumerate(road_points):
        for destination_point in road_point.destinations:
            vector = get_vector(road_point.pos, destination_point.pos)
            if vector.length() == 0:
                continue

            start = pygame.Vector2(helper.world_space_to_screen_space(
                road_point.pos, offset_x, offset_y, current_zoom
            ))
            end = pygame.Vector2(helper.world_space_to_screen_space(
                destination_point.pos, offset_x, offset_y, current_zoom
            ))

            direction = (end - start).normalize()
            perp = pygame.Vector2(-direction.y, direction.x) * half_width * current_zoom

            left_side = [start + perp, end + perp]
            right_side = [start - perp, end - perp]
            left_side_collective.extend(left_side)
            right_side_collective.extend(right_side)
            if (i & 0b01) == 0:
                median_collective.append([start, end])
            road_polygon = left_side + right_side[::-1]
            pygame.draw.polygon(screen, color, road_polygon)

    if len(left_side_collective) > 2 and len(right_side_collective) > 2:
        pygame.draw.polygon(screen, (233, 233, 233), left_side_collective, int(2*current_zoom))
        pygame.draw.polygon(screen, (233, 233, 233), right_side_collective, int(2*current_zoom))
        for center_point_pair in median_collective:
            pygame.draw.lines(screen, (233, 233, 233), False, center_point_pair, int(2*current_zoom))
