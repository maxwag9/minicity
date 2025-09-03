from helper import tile_neighbor_offsets, add_to_tile_to_points_list, screen_space_to_world_space, world_space_to_tile_space, remove_tight_points
from roads import RoadManager


def build_road(dt, road_points: RoadManager, tile_size):
    roads_to_build = road_points.to_build

    for road_id in list(roads_to_build.keys()):
        input_points, road_type, state, building_speed = roads_to_build[road_id]

        if road_type == "straight_road":
            built_road, done, state, building_speed = road_points.two_points_to_road(state=state, road_points=input_points,
                tile_size=tile_size,
                animated_points_per_tick=building_speed
            )
        else:
            built_road, done, state, building_speed = road_points.three_points_to_road_curve(
                input_points, road_points=input_points,
                tile_size=tile_size,
                animated_points_per_tick=building_speed, state=state
            )

        if done:
            del roads_to_build[road_id]
        else:
            roads_to_build[road_id] = built_road, road_type, state, building_speed

        # Update visual rendering data
        road_points.drawing[road_id] = built_road

        # Update spatial partitioning
        tile_to_point = road_points.tile_to_point
        add_to_tile_to_points_list(built_road, tile_to_point, road_id, road_points)


def find_hovered_points(points_to_check, mouse_pos_world):
    hovered = []

    for point in points_to_check:
        dx = abs(point.pos[0] - mouse_pos_world[0])
        dy = abs(point.pos[1] - mouse_pos_world[1])
        if dx <= point.point_size * 1 and dy <= point.point_size * 1:
            hovered.append(point)

    return hovered



def find_possible_hovered_road_points(hovered_tile, road_points: RoadManager):
    # Return all road points within a 3x3 area around the hovered tile
    tile_to_point = road_points.tile_to_point
    nearby_points = []

    hx, hy = hovered_tile
    for dx, dy in tile_neighbor_offsets:
        neighbor_tile = (hx + dx, hy + dy)
        if neighbor_tile in tile_to_point:
            road_dict = tile_to_point[neighbor_tile]
            for points in road_dict.values():
                nearby_points.extend(points)
    return nearby_points



def tick(dt, road_points: RoadManager, mouse_pos, tile_size, hovered_tile, offset_x, offset_y, current_zoom):
    # Convert screen → world → tile
    mouse_world_pos = screen_space_to_world_space(mouse_pos, offset_x, offset_y, current_zoom)
    mouse_tile_pos = world_space_to_tile_space(mouse_world_pos, tile_size, True)

    # Build new road segments if needed
    build_road(dt, road_points, tile_size)

    # Get possible road points near mouse
    nearby_points = find_possible_hovered_road_points(hovered_tile, road_points)

    # Check which of those the mouse is actually over
    hovered_points = find_hovered_points(nearby_points, mouse_world_pos)


    return nearby_points, hovered_points



