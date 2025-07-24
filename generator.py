from helper import calculate_distance, world_space_to_tile_space, bezier_point


def two_points_to_road(world_space_points, resolution=30, road_points=None, tile_size=25, instant=True, animated_points_per_tick=2):
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
        return road_points, True, None

    current_index = len(road_points)-1
    for _ in range(animated_points_per_tick):
        if current_index > point_amount:
            break
        t = current_index / point_amount
        x, y = point_1[0] + dx * t, point_1[1] + dy * t
        tx, ty = world_space_to_tile_space((x, y), tile_size, tile_snapping=True)
        road_points.append(((tx, ty), (x, y)))
        current_index += 1

    return road_points, current_index > point_amount, None



def three_points_to_road_curve(world_space_points,
                               distance_to_last_point=30,
                               road_points=None,
                               tile_size=25,
                               instant=False,
                               animated_points_per_tick=2,
                               state=None):
    if road_points is None:
        road_points = []
    done = False

    p0 = world_space_points[0][1]
    p1 = world_space_points[1][1]
    p2 = world_space_points[2][1]

    # === INSTANT MODE ===
    if instant:
        t = 0.0
        candidate_t = t
        result = []
        last_pt = bezier_point(p0, p1, p2, t)
        result.append((world_space_to_tile_space(last_pt, tile_size, True), last_pt))

        min_dist = distance_to_last_point * 0.75
        max_step = 0.25

        while t < 1.0:
            dt = 0.001
            iteration = 0
            max_iterations = 100
            while dt < max_step and iteration < max_iterations:
                iteration += 1
                candidate_t = t + dt
                if candidate_t > 1.0:
                    candidate_t = 1.0
                candidate_pt = bezier_point(p0, p1, p2, candidate_t)
                dist = calculate_distance(last_pt, candidate_pt)
                if dist >= distance_to_last_point:
                    break
                elif dist < min_dist:
                    dt *= 1.5
                else:
                    break

            if candidate_t > 1.0:
                break

            pt = bezier_point(p0, p1, p2, candidate_t)
            result.append((world_space_to_tile_space(pt, tile_size, True), pt))
            last_pt = pt
            t = candidate_t

        return result, True, None

    # === ANIMATED MODE ===
    if state is None:
        t = 0.0
        last_pt = bezier_point(p0, p1, p2, 0)
        road_points.append((world_space_to_tile_space(last_pt, tile_size, True), last_pt))
    else:
        t, last_pt = state

    added = 0
    min_dist = distance_to_last_point * 0.75
    max_step = 0.25
    min_step = 1e-5
    candidate_t = min_step

    while t < 1.0 and added < animated_points_per_tick:
        dt = 0.001
        candidate_pt = (0, 0)
        iteration = 0
        max_iterations = 100

        while dt < max_step and iteration < max_iterations:
            iteration += 1
            candidate_t = t + dt
            if candidate_t > 1.0:
                candidate_t = 1.0
            candidate_pt = bezier_point(p0, p1, p2, candidate_t)
            dist = calculate_distance(last_pt, candidate_pt)
            if dist >= distance_to_last_point:
                break
            elif dist < min_dist:
                dt *= 1.5
            else:
                break

        if candidate_t > 1.0:
            done = True
            break

        pt = candidate_pt
        t = candidate_t
        road_points.append((world_space_to_tile_space(pt, tile_size, True), pt))
        last_pt = pt
        added += 1

    if t >= 1.0:
        done = True

    return road_points, done, (t, last_pt)

