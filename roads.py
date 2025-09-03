from helper import get_vector, world_space_to_tile_space, bezier_point, calculate_distance, screen_space_to_world_space, \
    add_to_tile_to_points_list, remove_tight_points



class RoadManager:
    def __init__(self):
        self.all_points = []
        self.current = []
        self.drawing = {}
        self.to_build = {}
        self.tile_to_point = {}

    def build_road(self, road_type, mouse_pos, offset_x, offset_y, current_zoom, tile_size, point_size, road_points, hovered_points, building_speed=0):
        pos = screen_space_to_world_space(mouse_pos, offset_x, offset_y, current_zoom)
        anchor_point_amount = 0
        # Build road with 2 points; A -> B
        if len(self.current) == 0:
            # Point A
            self.current.append(Point(world_space_to_tile_space(pos, tile_size, True), pos, point_size, vector=None))
            anchor_point_amount = 1
        elif len(self.current) == 1:
            # Point B
            self.current.append(Point(world_space_to_tile_space(pos, tile_size, True), pos, point_size, vector=None))
            anchor_point_amount = 2
        elif len(self.current) == 2:
            if road_type == "curved_road":
                # Point C
                self.current.append(Point(world_space_to_tile_space(pos, tile_size, True), pos, point_size, vector=None))
                anchor_point_amount = 3


        if anchor_point_amount == 2 and road_type == "straight_road":
            used_ids = set(self.drawing.keys())
            new_id = 0
            while new_id in used_ids:
                new_id += 1
            temp_road_points = []
            for point in self.current:
                temp_road_points.append(Point(point.tile_pos, point.pos, point.point_size, None))

            road, done, state, building_speed = self.two_points_to_road(state=(True, 0, temp_road_points.copy()), road_points=None, tile_size=tile_size, point_size=point_size, animated_points_per_tick=building_speed)
            self.drawing[new_id] = road
            if not done:
                self.to_build[new_id] = road, "straight_road", state, building_speed

            # road_points[3]: {tile_pos:{road_id:[(point_pos),...]}}
            tile_to_point = self.tile_to_point
            add_to_tile_to_points_list(road, tile_to_point, new_id, road_points)
            self.current = []

        elif anchor_point_amount == 3 and road_type == "curved_road":
            used_ids = set(self.drawing.keys())
            new_id = 0
            while new_id in used_ids:
                new_id += 1
            temp_road_points = []
            for point in self.current:
                temp_road_points.append(Point(point.tile_pos, point.pos, point.point_size, None))
            road, done, state, building_speed = self.three_points_to_road_curve(temp_road_points, road_points=temp_road_points, tile_size=tile_size, point_size=point_size, animated_points_per_tick=building_speed)
            self.drawing[new_id] = road
            if not done:
                self.to_build[new_id] = road, "curved_road", state, building_speed

            # road_points[3]: {tile_pos:{road_id:[(point_pos),...]}}
            tile_to_point = self.tile_to_point
            add_to_tile_to_points_list(road, tile_to_point, new_id, road_points)
            self.current = []
        remove_tight_points(road_points, )

    def find_all_point_vectors_for_all_roads(self):
        for road in self.drawing:
            self.find_all_point_vectors_per_road(road)
            print(road)

    @staticmethod
    def find_all_point_vectors_per_road(road):
        road_length = len(road)
        for i in range(road_length):
            if i+1<=road_length:
                p1 = road[i][1]
                p2 = road[i+1][1]
                vector = get_vector(p1, p2)
                road[i][3] = vector
                road[i][4] = -vector

    @staticmethod
    def two_points_to_road(
            state=(True, 0, []),
            resolution=30,
            road_points=None,
            tile_size=25,
            animated_points_per_tick=2,
            point_size=5
    ):
        if road_points is None:
            road_points = []

        start, current_index, two_points = state
        current_index = max(0, current_index)  # clamp to zero

        # Unpack points and calculate segment info
        p1, p2 = two_points[0].pos, two_points[1].pos
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]

        total_distance = calculate_distance(p1, p2)
        segment_count = max(1, int(total_distance // resolution))

        def interpolate_point(t: float) -> tuple[float, float]:
            """Linear interpolation between p1 and p2."""
            return p1[0] + dx * t, p1[1] + dy * t

        def add_point(pos, with_vector_from=None):
            """Helper: create and append a Point, update previous vector if needed."""
            tile_pos = world_space_to_tile_space(pos, tile_size, tile_snapping=True)
            new_point = Point(tile_pos, pos, point_size, None)
            road_points.append(new_point)

            if with_vector_from is not None:
                prev_point = road_points[with_vector_from]
                vec = get_vector(prev_point.pos, new_point.pos)
                road_points[with_vector_from].vector = vec

        # -----------------
        # Instant building
        # -----------------
        if animated_points_per_tick == 0:
            step = 1 / segment_count
            road_points.clear()

            for i in range(segment_count + 1):
                pos = interpolate_point(i * step)
                add_point(pos, with_vector_from=i - 1 if i > 0 else None)

            # Copy vector into last point so it isn't left empty
            if len(road_points) >= 2:
                road_points[-1].vector = road_points[-2].vector

            return road_points, True, None, animated_points_per_tick

        # -----------------
        # Animated building
        # -----------------
        if len(road_points) == 2 and start:
            start = False

        steps = 0
        while steps < animated_points_per_tick and current_index <= segment_count:
            t = current_index / segment_count
            pos = interpolate_point(t)

            add_point(
                pos,
                with_vector_from=len(road_points) - 1 if road_points else None
            )

            current_index += 1
            steps += 1

        done = current_index > segment_count
        if done and len(road_points) >= 2:
            road_points[-1].vector = road_points[-2].vector

        return road_points, done, (start, current_index, two_points), animated_points_per_tick

    @staticmethod
    def three_points_to_road_curve(world_space_points,
                                   distance_to_last_point=30,
                                   road_points = None,
                                   tile_size=25,
                                   animated_points_per_tick=2,
                                   state=None,
                                   point_size=5):
        if road_points is None:
            road_points = []
        done = False

        p0 = world_space_points[0].pos
        p1 = world_space_points[1].pos
        p2 = world_space_points[2].pos

        # === INSTANT MODE ===
        if animated_points_per_tick==0:
            t = 0.0
            candidate_t = t
            result = []
            last_pt = bezier_point(p0, p1, p2, t)
            result.append(Point(world_space_to_tile_space(last_pt, tile_size, True), last_pt, point_size, None))

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
                previous_point = result[len(result) - 1]
                vector = get_vector(previous_point.pos, pt)
                result[len(result) - 1] = Point(previous_point.tile_pos, previous_point.pos, previous_point.point_size, vector)
                del previous_point
                result.append(Point(world_space_to_tile_space(pt, tile_size, True), pt, point_size, None))
                last_pt = pt
                t = candidate_t
            result.pop(1)
            return result, True, None, animated_points_per_tick

        # === ANIMATED MODE ===
        if state is None:
            t = 0.0
            last_pt = bezier_point(p0, p1, p2, 0)
            road_points.append(Point(world_space_to_tile_space(last_pt, tile_size, True), last_pt, point_size, None))
        else:
            t, last_pt = state

        added = 0
        min_dist = distance_to_last_point
        max_step = 0.75
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
                if dist >= distance_to_last_point * 1.2:
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
            previous_point = road_points[len(road_points) - 1]
            vector = get_vector(previous_point.pos, pt)
            road_points[len(road_points) - 1] = Point(previous_point.tile_pos, previous_point.pos, previous_point.point_size, vector)
            del previous_point
            road_points.append(Point(world_space_to_tile_space(pt, tile_size, True), pt, point_size, None))
            last_pt = pt
            added += 1

        if t >= 1.0:
            done = True
            road_points.pop(1)
        return road_points, done, (t, last_pt), animated_points_per_tick


    def reset(self):
        pass

class Road:
    last_id = -1

    def __init__(self, tile_pos, pos, point_size, vector):
        Road.last_id += 1
        self.road_id = Road.last_id
        self.invisible = False

class Point:
    last_id = -1

    def __init__(self, tile_pos, pos, point_size, vector):
        Point.last_id += 1
        self.point_id = Point.last_id
        self.vector = vector
        self.point_size = point_size
        self.pos = pos
        self.tile_pos = tile_pos

        self.surrounding_points = []
        self.invisible = False
        self.no_vector_calculation = False

