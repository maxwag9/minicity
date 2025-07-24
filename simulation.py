from generator import two_points_to_road, three_points_to_road_curve
from helper import tile_neighbor_offsets, add_to_tile_to_points_list, screen_space_to_tile_space, \
    screen_space_to_world_space, world_space_to_tile_space


def build_road(dt, road_points, tile_size):
    roads_to_build = road_points[2]
    keys = list(roads_to_build.keys())
    for key in keys:
        input_points, type, state = roads_to_build[key]
        if type == "straight_road":
            road, done, state = two_points_to_road(input_points, road_points=input_points, tile_size=tile_size, instant=False, animated_points_per_tick=2)
        else:
            road, done, state = three_points_to_road_curve(input_points, road_points=input_points, tile_size=tile_size, instant=False, animated_points_per_tick=2, state=state)
        if done:
            # Road is done, remove it from list
            roads_to_build.pop(key, None)
        else:
            # Road is not done, keep it in list
            roads_to_build[key] = road, type, state
        # Update Rendering list with new road points
        road_points[1][key] = road
        # road_points[3]: {tile_pos:{road_id:[(point_pos),...]}}
        tile_to_point = road_points[3]
        new_id = key
        add_to_tile_to_points_list(road, tile_to_point, new_id, road_points)


def find_hovered_points(tile_hovered_points, mouse_pos_world):
    hovered_points = []
    for point in tile_hovered_points:
        point_pos, point_size = point
        if abs(point_pos[0]-mouse_pos_world[0]) <= point_size*2 and abs(point_pos[1]-mouse_pos_world[1]) <= point_size*2:
            hovered_points.append(point)
    return hovered_points


def find_possible_hovered_road_points(hovered_tile, road_points):
    possible_hovered_road_points = []
    tile_to_point = road_points[3]
    hx, hy = hovered_tile

    for dx, dy in tile_neighbor_offsets:
        neighbor = (hx + dx, hy + dy)
        if neighbor in tile_to_point:
            for road in tile_to_point[neighbor].values():
                possible_hovered_road_points.extend(road)
    return possible_hovered_road_points


def tick(dt, road_points, mouse_pos, tile_size, hovered_tile, offset_x, offset_y, current_zoom):
    mouse_pos_world = screen_space_to_world_space(mouse_pos, offset_x, offset_y, current_zoom)
    mouse_pos_tile = world_space_to_tile_space(mouse_pos_world, tile_size, True)
    build_road(dt, road_points, tile_size)
    tile_hovered_points = find_possible_hovered_road_points(hovered_tile, road_points)
    hovered_points = find_hovered_points(tile_hovered_points, mouse_pos_world)

    return tile_hovered_points, hovered_points


