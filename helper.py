import math
import pygame

tile_neighbor_offsets = [
    (-1, -1), (0, -1), (1, -1),
    (-1, 0), (0, 0), (1, 0),
    (-1, 1), (0, 1), (1, 1)
]


class Camera:
    def __init__(self, offset_x=0, offset_y=0, zoom=1.0, tile_size=32):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
        self.tile_size = tile_size

    # --- conversions ---
    def screen_to_world(self, screen_pos):
        sx, sy = screen_pos
        wx = (sx / self.zoom) + self.offset_x
        wy = (sy / self.zoom) + self.offset_y
        return wx, wy

    def world_to_screen(self, world_pos):
        wx, wy = world_pos
        sx = (wx - self.offset_x) * self.zoom
        sy = (wy - self.offset_y) * self.zoom
        return sx, sy

    def world_to_tile(self, world_pos, snap=True):
        wx, wy = world_pos
        if snap:
            tx = int(wx // self.tile_size)
            ty = int(wy // self.tile_size)
        else:
            tx = wx / self.tile_size
            ty = wy / self.tile_size
        return tx, ty

    def tile_to_world(self, tile_pos):
        tx, ty = tile_pos
        wx = tx * self.tile_size
        wy = ty * self.tile_size
        return wx, wy

    def screen_to_tile(self, screen_pos, snap=True):
        world_pos = self.screen_to_world(screen_pos)
        return self.world_to_tile(world_pos, snap)

    def tile_to_screen(self, tile_pos):
        world_pos = self.tile_to_world(tile_pos)
        return self.world_to_screen(world_pos)



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


def add_to_tile_to_points_list(road, tile_to_point, new_id):
    for point in road:
        # Ensure a dict exists for this tile
        tile_dict = tile_to_point.setdefault(point.tile_pos, {})

        # Ensure a list exists for this road_id in that tile
        points_list = tile_dict.setdefault(new_id, [])

        # Append only if not already present
        if point not in points_list:
            points_list.append(point)


def replace_point_on_map(road_points, point_to_replace, point_to_add):
    prior_destinations = []
    prior_sources = []

    prior_destinations.extend(point_to_replace.destinations)
    prior_sources.extend(point_to_replace.sources)
    if point_to_replace in prior_destinations:
        prior_destinations.remove(point_to_replace)
    if point_to_replace in prior_sources:
        prior_sources.remove(point_to_replace)
    point_to_add.destinations.extend(prior_destinations)
    point_to_add.sources.extend(prior_sources)
    for source_point in prior_sources:
        source_point.destinations.append(point_to_add)
    for destination_point in prior_destinations:
        destination_point.sources.append(point_to_add)

    remove_point_from_map(road_points=road_points, point_to_remove=point_to_replace, point_to_add=point_to_add)


def remove_point_from_map(road_points, point_to_remove, point_to_add=None):
    drawing = road_points.drawing
    tile_to_point = road_points.tile_to_point

    # find road + index
    road_key, idx = None, None
    for rk, points in list(drawing.items()):
        for i, point in enumerate(points):
            if point is point_to_remove:
                road_key, idx = rk, i
                break
        if road_key is not None:
            break
    if road_key is None:
        return  # not found

    points = drawing[road_key]

    # cleanup connections
    for connected_point in point_to_remove.destinations + point_to_remove.sources:
        if point_to_remove in connected_point.sources:
            connected_point.sources.remove(point_to_remove)
        if point_to_remove in connected_point.destinations:
            connected_point.destinations.remove(point_to_remove)

    # cleanup tile mapping (by identity!)
    if point_to_remove.tile_pos in tile_to_point:
        if road_key in tile_to_point[point_to_remove.tile_pos]:
            point_list = tile_to_point[point_to_remove.tile_pos][road_key]
            if isinstance(point_list, tuple):  # (list, set)
                lst, seen = point_list
                if point_to_remove in lst:
                    lst.remove(point_to_remove)
                    seen.discard(id(point_to_remove))
            else:
                # old style plain list
                point_list[:] = [p for p in point_list if p is not point_to_remove]

            if not point_list:
                del tile_to_point[point_to_remove.tile_pos][road_key]
                if not tile_to_point[point_to_remove.tile_pos]:
                    del tile_to_point[point_to_remove.tile_pos]

    # replacement
    if point_to_add is not None:
        points[idx] = point_to_add
        if len(points) < 2:
            _delete_road(drawing, road_key)
        return

    # actually remove
    del points[idx]

    # rebuild road segments
    if len(points) < 2:
        _delete_road(drawing, road_key)
        return

    segments, cur = [], []
    for point in points:
        cur.append(point)
    if cur:
        segments.append(cur)

    # assign back
    drawing[road_key] = segments[0]
    for seg in segments[1:]:
        _create_road(drawing, seg)

















def remove_tight_points(road_points, point_to_add=None, hovered_points=None):
    #print("Hovered_points: ", hovered_points)
    if point_to_add is None:
        point_to_add = []
    point_to_remove = None
    current_road_points = road_points.current
    #print("CURRENT: ", current_road_points)
    all_road_points = road_points.drawing
    if hovered_points:
        hovered_point = hovered_points[0]
        for road_key in all_road_points:
            for point in all_road_points[road_key]:
                hovered_point_pos = hovered_point.pos
                #print(point, hovered_point)
                if point.pos == hovered_point_pos:
                    point_to_remove = point
                    print("Hover point: ", point)
                    break
            break
    else:
        for current_point in current_road_points:
            for road_key in all_road_points:
                for point in all_road_points[road_key]:
                    dx = abs(point.pos[0] - current_point.pos[0])
                    dy = abs(point.pos[1] - current_point.pos[1])
                    if dx <= point.point_size * 1 and dy <= point.point_size * 1:
                        point_to_remove = point
                        break
                break
            break

    if not point_to_remove:
        print(point_to_remove)
        print("No tight points found, skipping removal.")
        return

    if point_to_add:
        #print("Removing hovered: ", points_to_remove)
        #print("points_to_add: ", points_to_add)
        replace_point_on_map(road_points, point_to_remove, point_to_add)
    else:
        print("Removing: ", point_to_remove)
        remove_point_from_map(road_points, point_to_remove)

def _next_new_id(drawing):
    used = set(drawing.keys())
    nid = 0
    while nid in used:
        nid += 1
    return nid

def _create_road(drawing, pts):
    if len(pts) < 2:
        return None
    nid = _next_new_id(drawing)
    drawing[nid] = pts
    return nid

def _delete_road(drawing, road_key):
    if road_key in drawing:
        del drawing[road_key]
