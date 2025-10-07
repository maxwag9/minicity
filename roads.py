from helper import *



class RoadManager:
    def __init__(self, camera):
        self.all_points = []
        self.current = []
        self.drawing = {}
        self.to_build = {}
        self.tile_to_point = {}
        self.camera = camera

    def build_road(self, road_type, mouse_pos, point_size, road_points, hovered_points, building_speed=0):
        pos = self.camera.screen_to_world(mouse_pos)
        point_to_add = None
        anchor_point_amount = 0
        # Build road with 2 points; A -> B
        if len(self.current) == 0:
            # Point A
            point_a = Point(self.camera.world_to_tile(pos), pos, point_size, vector=None)
            self.current.append(point_a)
            anchor_point_amount = 1
            point_to_add = self.current[0]
        elif len(self.current) == 1:
            # Point B
            point_b = Point(self.camera.world_to_tile(pos), pos, point_size, vector=None)
            self.current.append(point_b)
            anchor_point_amount = 2
            if self.current[0].pos != self.current[1].pos:
                point_to_add = point_b
        elif len(self.current) == 2:
            if road_type[0] == "curved_road":
                # Point C
                point_c = Point(self.camera.world_to_tile(pos), pos, point_size, vector=None)
                self.current.append(point_c)
                anchor_point_amount = 3
                point_to_add = point_c


        if anchor_point_amount == 2 and road_type[0] == "straight_road":
            used_ids = set(self.drawing.keys())
            new_id = 0
            while new_id in used_ids:
                new_id += 1

            temp_road_points = self.current.copy()

            road, done, state, building_speed = self.two_points_to_road(state=(True, 0, temp_road_points), point_size=point_size, animated_points_per_tick=building_speed)
            self.drawing[new_id] = road
            if not done:
                self.to_build[new_id] = road, road_type, state, building_speed

            # road_points[3]: {tile_pos:{road_id:[(point_pos),...]}}
            tile_to_point = self.tile_to_point
            add_to_tile_to_points_list(road, tile_to_point, new_id)
            self.current = []

        elif anchor_point_amount == 3 and road_type[0] == "curved_road":
            used_ids = set(self.drawing.keys())
            new_id = 0
            while new_id in used_ids:
                new_id += 1
            temp_road_points = self.current.copy()
            road, done, state, building_speed = self.three_points_to_road_curve(state=(True, 0, temp_road_points), point_size=point_size, animated_points_per_tick=building_speed)
            self.drawing[new_id] = road
            if not done:
                self.to_build[new_id] = road, road_type, state, building_speed

            # road_points[3]: {tile_pos:{road_id:[(point_pos),...]}}
            tile_to_point = self.tile_to_point
            add_to_tile_to_points_list(road, tile_to_point, new_id)
            self.current = []
        remove_tight_points(road_points, point_to_add=point_to_add, hovered_points=hovered_points)


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

    def two_points_to_road(self,
            state=(True, 0, []),
            resolution=25,
            built_road_points=None,
            animated_points_per_tick=2,
            point_size=5):
        if built_road_points is None:
            built_road_points = []

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
            tile_pos = self.camera.world_to_tile(pos)
            new_point = Point(tile_pos, pos, point_size, None)
            built_road_points.append(new_point)
            add_vectors_from(with_vector_from, new_point)

            #remove_tight_points(road_manager, [new_point])

        def add_vectors_from(with_vector_from, point):
            if with_vector_from is not None:
                prev_point = built_road_points[with_vector_from]
                prev_point.destinations.append(point)
                point.sources.append(prev_point)
            return point

        # -----------------
        # Instant building
        # -----------------
        if animated_points_per_tick == 0:
            step = 1 / segment_count
            built_road_points.clear()

            built_road_points.append(two_points[0]) # Putting the first point in immediately
            point_amount = 0
            if segment_count > 2:
                for i in range(1, segment_count): # +2 to skip making the first point again
                    point_amount = i
                    pos = interpolate_point(i * step)
                    add_point(pos, with_vector_from=i - 1 if i > 0 else None)
                built_road_points.append(add_vectors_from(point_amount, two_points[1]))  # Putting in the last point!
            elif segment_count == 2:
                built_road_points.append(add_vectors_from(point_amount, two_points[1]))  # Putting in the last point!

            return built_road_points, True, None, animated_points_per_tick

        # -----------------
        # Animated building
        # -----------------
        if len(built_road_points) == 1 and start:
            start = False

        steps = 0
        done = current_index > segment_count-1
        if segment_count > 1:
            if start:
                built_road_points.append(two_points[0])  # Putting the first point in immediately
                steps += 1
                current_index += 1
            elif done:
                built_road_points.append(add_vectors_from(segment_count-1, two_points[1]))  # Putting in the last point!
                current_index += 1
            else:
                while steps < animated_points_per_tick and current_index <= segment_count:
                    t = current_index / segment_count
                    pos = interpolate_point(t)

                    add_point(
                        pos,
                        with_vector_from=len(built_road_points) - 1 if built_road_points else None
                    )

                    current_index += 1
                    steps += 1
        else:
            built_road_points.append(two_points[0])  # Putting the first point in immediately
            done = True

        return built_road_points, done, (start, current_index, two_points), animated_points_per_tick


    def three_points_to_road_curve(self,
                                   state=(True, 0, []),
                                   resolution=30,
                                   built_road_points=None,
                                   animated_points_per_tick=2,
                                   point_size=5
                                   ):
        """
        Builds a quadratic Bezier road between three control points.
        state = (start, current_index, three_points)
        """
        if built_road_points is None:
            built_road_points = []

        start, current_index, three_points = state
        current_index = max(0, current_index)  # clamp to zero
        p0, p1, p2 = three_points[0].pos, three_points[1].pos, three_points[2].pos

        # --- curve length estimate (linear sampling for now) ---
        # we divide into segments similar to two_points_to_road
        total_distance = 0
        last_pt = bezier_point(p0, p1, p2, 0.0)
        samples = 50
        for i in range(1, samples + 1):
            t = i / samples
            pt = bezier_point(p0, p1, p2, t)
            total_distance += calculate_distance(last_pt, pt)
            last_pt = pt

        segment_count = max(1, int(total_distance // resolution))

        def interpolate_point(t: float) -> tuple[float, float]:
            return bezier_point(p0, p1, p2, t)

        def add_point(pos, with_vector_from=None):
            """Helper: create and append a Point, update previous vector if needed."""
            tile_pos = self.camera.world_to_tile(pos)
            new_point = Point(tile_pos, pos, point_size, None)
            built_road_points.append(new_point)
            add_vectors_from(with_vector_from, new_point)

            #remove_tight_points(road_manager, [new_point])

        def add_vectors_from(with_vector_from, point):
            if with_vector_from is not None:
                prev_point = built_road_points[with_vector_from]
                prev_point.destinations.append(point)
                point.sources.append(prev_point)
            return point

        # -----------------
        # Instant building
        # -----------------
        if animated_points_per_tick == 0:
            step = 1 / segment_count
            built_road_points.clear()

            built_road_points.append(three_points[0]) # Putting the first point in immediately
            point_amount = 1

            for i in range(1, segment_count + 1):
                point_amount = i
                pos = interpolate_point(i * step)
                add_point(pos, with_vector_from=i - 1 if i > 0 else None)

            built_road_points.append(add_vectors_from(point_amount, three_points[2])) # Putting in the last point!

            return built_road_points, True, None, animated_points_per_tick

        # -----------------
        # Animated building
        # -----------------
        if len(built_road_points) == 2 and start:
            start = False

        steps = 0
        while steps < animated_points_per_tick and current_index <= segment_count:
            t = current_index / segment_count
            pos = interpolate_point(t)

            add_point(
                pos,
                with_vector_from=len(built_road_points) - 1 if built_road_points else None
            )

            current_index += 1
            steps += 1

        done = current_index > segment_count
        if done and len(built_road_points) >= 2:
            built_road_points[-1].vector = built_road_points[-2].vector

        return built_road_points, done, (start, current_index, three_points), animated_points_per_tick

    def reset(self):
        pass

class Road:
    last_id = -1

    def __init__(self, tile_pos, pos, point_size):
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

        self.sources = []
        self.destinations = []
        self.invisible = False
        self.no_vector_calculation = False

