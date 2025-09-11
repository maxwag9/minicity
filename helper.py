import math
import pygame

tile_neighbor_offsets = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (0, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1)
]


def screen_space_to_tile_space(mouse_pos, offset_x, offset_y, zoom, tile_size):
    world_pos = screen_space_to_world_space(mouse_pos, offset_x, offset_y, zoom)
    tx, ty = world_space_to_tile_space(world_pos, tile_size, True)
    return tx, ty


def world_space_to_tile_space(world_pos, tile_size, tile_snapping=False):
    wx, wy = world_pos
    if tile_snapping:
        tx = wx // tile_size
        ty = wy // tile_size
    else:
        tx = wx / tile_size
        ty = wy / tile_size
    return tx, ty


def tile_space_to_world_space(tile_pos, tile_size):
    tx, ty = tile_pos
    wx = tx * tile_size
    wy = ty * tile_size
    return wx, wy


def screen_space_to_world_space(screen_pos, offset_x, offset_y, zoom):
    if type(screen_pos) == tuple:
        sx, sy = screen_pos
        wx = (sx / zoom) + offset_x
        wy = (sy / zoom) + offset_y
        return wx, wy
    else:
        ws = (screen_pos / zoom) + offset_x
        return ws


def world_space_to_screen_space(world_pos, offset_x, offset_y, zoom):
    wx, wy = world_pos
    sx = (wx - offset_x) * zoom
    sy = (wy - offset_y) * zoom
    return sx, sy


def tile_space_to_screen_space(tile_pos, offset_x, offset_y, zoom, tile_size):
    world_pos = tile_space_to_world_space(tile_pos, tile_size)
    screen_pos = world_space_to_screen_space(world_pos, offset_x, offset_y, zoom)
    return screen_pos[0], screen_pos[1]


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def get_vector(p1, p2):
    vector = pygame.Vector2(p2[0] - p1[0], p2[1] - p1[1])
    return vector


def bezier_point(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return x, y


def add_to_tile_to_points_list(road, tile_to_point, new_id, road_points):
    for point in road:
        # road: [((tile_pos), (point_pos)),...]
        # point: ((tile_pos), (point_pos))
        tile_positions = tile_to_point.keys()
        # tile_positions: all tile positions (tile_pos)
        if point.tile_pos in tile_positions:
            road_ids = tile_to_point[point.tile_pos].keys()
            if new_id in road_ids:
                #print("Appended: ", (tile_pos, new_id))
                road_points.tile_to_point[point.tile_pos][new_id].append(point)
            else:
                #print("Created: ", new_id)
                road_points.tile_to_point[point.tile_pos][new_id] = [point]
        else:
            #print("Created: ", tile_pos, new_id)
            road_points.tile_to_point[point.tile_pos] = {new_id: [point]}

def replace_point_on_map(road_points, point_to_replace, points_to_add):
    for point in points_to_add:
        prior_destinations = []
        prior_sources = []

        for replaced_point in point_to_replace:
            prior_destinations.extend(replaced_point.destinations)
            prior_sources.extend(replaced_point.sources)
        for replaced_point in point_to_replace:
            if replaced_point in prior_destinations:
                prior_destinations.remove(replaced_point)
            if replaced_point in prior_sources:
                prior_sources.remove(replaced_point)
        point.destinations.extend(prior_destinations)
        point.sources.extend(prior_sources)
        for source_point in prior_sources:
            source_point.destinations.append(point)
        for destination_point in prior_destinations:
            destination_point.sources.append(point)

    remove_point_from_map(road_points=road_points, points=point_to_replace)


def remove_point_from_map(road_points, points):
    drawing = road_points.drawing  # road_id → list of (tile_pos, point_object)
    tile_to_point = road_points.tile_to_point  # tile_pos → {road_id: [(world_pos, size)]}

    for point_to_remove in points:
        for road_id, road in drawing.items():
            for i, point in enumerate(road):
                if point_to_remove.pos == point.pos:
                    connected_points = []
                    connected_points.extend(road[i].destinations)
                    connected_points.extend(road[i].sources)
                    for connected_point in connected_points:
                        if point in connected_point.sources:
                            connected_point.sources.remove(point)
                        if point in connected_point.destinations:
                            connected_point.destinations.remove(point)
                    # remove from drawing road
                    del road[i]

                    if point.tile_pos in tile_to_point:
                        if road_id in tile_to_point[point.tile_pos]:
                            point_list = tile_to_point[point.tile_pos][road_id]
                            point_list[:] = [p for p in point_list if p.pos != point.pos]

                            # Clean up empty containers
                            if not point_list:
                                del tile_to_point[point.tile_pos][road_id]
                                if not tile_to_point[point.tile_pos]:
                                    del tile_to_point[point.tile_pos]
                    break  # Only remove once per hovered_pos


def remove_tight_points(road_points, points_to_add=None, hovered_points=None):
    if points_to_add is None:
        points_to_add = []
    points_to_remove = []
    current_road_points = road_points.current
    #print("CURRENT: ", current_road_points)
    all_road_points = road_points.drawing
    if hovered_points:
        for hovered_point in hovered_points:
            for road_key in all_road_points:
                for point in all_road_points[road_key]:
                    hovered_point_pos = hovered_point.pos
                    if point.pos == hovered_point_pos:
                        points_to_remove.append(point)
    else:
        for current_point in current_road_points:
            for road_key in all_road_points:
                for point in all_road_points[road_key]:
                    dx = abs(point.pos[0] - current_point.pos[0])
                    dy = abs(point.pos[1] - current_point.pos[1])
                    if dx <= point.point_size * 1 and dy <= point.point_size * 1:
                        points_to_remove.append(point)
    if not points_to_remove:
        #print("No tight points found, skipping removal.")
        return

    if points_to_add:
        #print("Removing hovered: ", points_to_remove)
        #print("points_to_add: ", points_to_add)
        replace_point_on_map(road_points, points_to_remove, points_to_add)
    else:
        #print("Removing: ", points_to_remove)
        remove_point_from_map(road_points, points_to_remove)
