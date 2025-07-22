from helper import calculate_distance

roads_to_build = []


def two_points_to_road(world_space_points, resolution=10, instant=True, road_points=None):
    if road_points is None:
        road_points = []

    point_1, point_2 = world_space_points
    total_distance = calculate_distance(point_1, point_2)
    point_amount = int(total_distance // resolution)

    if instant:
        for i in range(point_amount + 1):
            t = i / point_amount
            x = point_1[0] + (point_2[0] - point_1[0]) * t
            y = point_1[1] + (point_2[1] - point_1[1]) * t
            road_points.append((x, y))
    else:
        i = len(road_points)
        t = i / point_amount
        x = point_1[0] + (point_2[0] - point_1[0]) * t
        y = point_1[1] + (point_2[1] - point_1[1]) * t
        road_points.append((x, y))

    return road_points


def three_points_to_road_curve(world_space_points, resolution=10, instant=True, road_points=None):
    if road_points is None:
        road_points = []

    point_1, point_2 = world_space_points
    total_distance = calculate_distance(point_1, point_2)
    point_amount = int(total_distance // resolution)

    if instant:
        for i in range(point_amount + 1):
            t = i / point_amount
            x = point_1[0] + (point_2[0] - point_1[0]) * t
            y = point_1[1] + (point_2[1] - point_1[1]) * t
            road_points.append((x, y))
    else:
        i = len(road_points)
        t = i / point_amount
        x = point_1[0] + (point_2[0] - point_1[0]) * t
        y = point_1[1] + (point_2[1] - point_1[1]) * t
        road_points.append((x, y))

    return road_points
