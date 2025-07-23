from helper import calculate_distance, world_space_to_tile_space, bezier_point


def two_points_to_road(world_space_points, resolution=10, road_points=None, tile_size=25, instant=True, animated_points_per_tick=2):
    if road_points is None:
        road_points = []

    point_1, point_2 = world_space_points[0][1], world_space_points[1][1]
    dx, dy = point_2[0] - point_1[0], point_2[1] - point_1[1]

    total_distance = calculate_distance(point_1, point_2)
    point_amount = max(1, int(total_distance // resolution))  # At least one segment

    if instant:
        step = 1 / point_amount
        road_points = [(
            world_space_to_tile_space(
                (point_1[0] + dx * t, point_1[1] + dy * t),
                tile_size,
                tile_snapping=True),
            (point_1[0] + dx * t, point_1[1] + dy * t)
        ) for i in range(point_amount + 1) for t in [i * step]]
        return road_points, True

    current_index = len(road_points)-1
    for _ in range(animated_points_per_tick):
        if current_index > point_amount:
            break
        t = current_index / point_amount
        x, y = point_1[0] + dx * t, point_1[1] + dy * t
        tx, ty = world_space_to_tile_space((x, y), tile_size, tile_snapping=True)
        road_points.append(((tx, ty), (x, y)))
        current_index += 1

    return road_points, current_index > point_amount



def three_points_to_road_curve(world_space_points, resolution=10, road_points=None, tile_size=25, instant=False, animated_points_per_tick=1):
    if road_points is None:
        road_points = []

    point_1, point_2, point_3 = world_space_points[0][1], world_space_points[1][1], world_space_points[2][1]
    dx, dy = point_3[0] - point_1[0], point_3[1] - point_1[1]

    distance_point_1_to_anchor = calculate_distance(point_1, point_2)
    point_amount = max(1, int(distance_point_1_to_anchor // resolution))  # At least one segment

    if instant:
        step = 1 / point_amount
        road_points = [(
            world_space_to_tile_space(
                (point_1[0] + dx * t, point_1[1] + dy * t),
                tile_size,
                tile_snapping=True),
            (point_1[0] + dx * t, point_1[1] + dy * t)
        ) for i in range(point_amount + 1) for t in [i * step]]
        #return road_points, True
        return None

    current_index = len(road_points)-2
    for _ in range(animated_points_per_tick):
        if current_index > point_amount:
            break
        t = current_index / point_amount

        x, y = bezier_point(point_1, point_2, point_3, t)
        tx, ty = world_space_to_tile_space((x, y), tile_size, tile_snapping=True)
        road_points.append(((tx, ty), (x, y)))
        current_index += 1

    return road_points, current_index > point_amount
