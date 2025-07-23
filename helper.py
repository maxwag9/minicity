import math

tile_neighbor_offsets = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0), (0,  0), (1,  0),
    (-1,  1), (0,  1), (1,  1)
]


def screen_space_to_tile_space(mouse_pos, offset_x, offset_y, zoom, tile_size):
    world_pos = screen_space_to_world_space(mouse_pos, offset_x, offset_y, zoom)
    tx, ty = world_space_to_tile_space(world_pos, tile_size, True)
    return tx, ty

def world_space_to_tile_space(world_pos,  tile_size, tile_snapping=False):
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
    sx, sy = screen_pos
    wx = (sx / zoom) + offset_x
    wy = (sy / zoom) + offset_y
    return wx, wy


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
    return p2[0] - p1[0], p2[1] - p1[1]

def bezier_point(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return x, y

def add_to_hovered_points_list(road, tile_to_point, new_id, road_points):
    for point in road:
        # road: [((tile_pos), (point_pos)),...]
        # point: ((tile_pos), (point_pos))
        tile_pos, point_pos = point
        tile_positions = tile_to_point.keys()
        # tile_positions: all tile positions (tile_pos)
        if tile_pos in tile_positions:
            road_ids = tile_to_point[tile_pos].keys()
            if new_id in road_ids:
                #print("Appended: ", (tile_pos, new_id))
                road_points[3][tile_pos][new_id].append(point_pos)
            else:
                #print("Created: ", new_id)
                road_points[3][tile_pos][new_id] = [point_pos]
        else:
            #print("Created: ", tile_pos, new_id)
            road_points[3][tile_pos] = {new_id: [point_pos]}