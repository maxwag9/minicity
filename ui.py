import pygame

import helper
from helper import screen_space_to_world_space, world_space_to_screen_space
from roads import RoadManager

tile_types={
    "residential": (50, 255, 50),
    "commercial": (50, 200, 255),
    "industrial": (100, 255, 255),
    "asphalt": (100, 100, 100),

}


def draw(screen, game_map, tile_size, offset_x, offset_y, current_zoom, hovered_tile, road_points: RoadManager, mouse_pos, tool_mode, possible_hovered_road_points, hovered_points):
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

    current_road_points = road_points.current
    all_road_points = road_points.drawing.values()
    if current_road_points:
        for point in current_road_points:
            pygame.draw.circle(screen, (0, 120, 230), helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom), 3 * current_zoom)



    if all_road_points:
        # Precompute set of hovered world positions for fast lookup
        hovered_set = {p.pos for p in possible_hovered_road_points}
        prev_vector = None
        # Render all road points
        for all_single_road_points in all_road_points:
            draw_road(screen, all_single_road_points, current_zoom, offset_x, offset_y)
            prev_vector = None
            for point in all_single_road_points:

                # Use smaller radius if hovered
                radius = 4 if point.pos in hovered_set else point.point_size

                point_pos_screen = helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom)

                pygame.draw.circle(
                    screen,
                    (20, 120, 230), point_pos_screen, radius * current_zoom
                )

                def draw_vector_and_sides(vector, reversed):
                    color = (255, 0, 000)
                    if reversed:
                        color = (255, 255, 000)
                    point_pos_world_start = point.pos
                    world_direction = pygame.Vector2(vector)
                    point_pos_world_end = point_pos_world_start + world_direction
                    # Convert to Vector2 for easier math
                    start = pygame.Vector2(point_pos_screen)
                    direction = pygame.Vector2(vector) * current_zoom

                    end_point = start + direction

                    # Draw shaft line
                    #if point.vector.x > 100:

                    pygame.draw.line(screen, color, start, end_point, width=2)

                    # Arrowhead size (adjust as needed)
                    arrow_size = 6 * current_zoom

                    # Normalize vector for consistent arrow size
                    if direction.length() == 0:
                        direction = pygame.Vector2(1, 0)  # fallback direction

                    direction = direction.normalize()

                    # Perpendicular vectors for arrow wings
                    perp = pygame.Vector2(-direction.y, direction.x)

                    # Two points for the arrowhead triangle wings
                    left_point = end_point - direction * arrow_size + perp * (arrow_size / 2)
                    right_point = end_point - direction * arrow_size - perp * (arrow_size / 2)

                    # Draw the arrowhead triangle
                    pygame.draw.polygon(screen, color, [end_point, left_point, right_point])

                if point.vector:
                    #print(point.vector, -point.vector)
                    draw_vector_and_sides(point.vector, False)
                    if prev_vector:
                        draw_vector_and_sides(-prev_vector, True)
                    prev_vector = point.vector



    if tool_mode == "straight_road":
        pygame.draw.circle(screen, (20, 230, 230), mouse_pos, 7 * current_zoom, 2)
    elif tool_mode == "curved_road":
        pygame.draw.circle(screen, (200, 230, 230), mouse_pos, 3 * current_zoom, 2)
    if hovered_points:
        for point in hovered_points:
            pygame.draw.circle(screen, (200, 220, 230),
                               helper.world_space_to_screen_space(point.pos, offset_x, offset_y, current_zoom),
                               3 * current_zoom)

def draw_road(screen, road_points, current_zoom, offset_x, offset_y, color=(155, 155, 155), half_width=15):
    if len(road_points) < 2:
        return  # not enough points for a road

    left_side = []
    right_side = []

    for road_point in road_points:
        if not road_point.vector:
            continue  # skip first point until it has a vector

        start = pygame.Vector2(helper.world_space_to_screen_space(road_point.pos, offset_x, offset_y, current_zoom))
        direction = pygame.Vector2(road_point.vector).normalize()

        # perpendicular vector
        perp = pygame.Vector2(-direction.y, direction.x) * half_width * current_zoom

        left_side.append(start + perp)
        right_side.append(start - perp)

    if len(left_side) < 2 or len(right_side) < 2:
        return

    # build polygon by going down left side, then back along right side reversed
    road_polygon = left_side + right_side[::-1]

    pygame.draw.polygon(screen, color, road_polygon)