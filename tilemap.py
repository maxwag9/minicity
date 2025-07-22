from collections import defaultdict

class Tile:
    def __init__(self, x, y, tile_type):
        self.x = x
        self.y = y
        self.type = tile_type
        self.occupied = False

class TileMap:
    def __init__(self, chunk_size):
        self.loaded_chunks = defaultdict(dict)
        self.chunk_size = chunk_size
        #self.bounds = None

    def get_chunk_coords_from_tile_world_coords(self, x, y):
        return x//self.chunk_size, y//self.chunk_size

    def place_tile(self, x, y, tile_type):
        chunk_x, chunk_y = self.get_chunk_coords_from_tile_world_coords(x, y)
        cx, cy = x % self.chunk_size, y % self.chunk_size
        self.loaded_chunks[(chunk_x, chunk_y)][(cx, cy)] = Tile(x, y, tile_type)

    def get_tile_world_coords_from_chunk(self, chunk_x, chunk_y, tile_cx, tile_cy):
        return chunk_x*self.chunk_size+tile_cx, chunk_y*self.chunk_size+tile_cy

    def get_tile_world_coords_from_tile(self, tile_cx, tile_cy):
        return tile_cx, tile_cy

    def get_all_tiles(self, screen):
        #self.bounds = screen.get_size()
        all_tiles = []
        for chunk in self.loaded_chunks.values():
            for tile in chunk.values():
                all_tiles.append(tile)


        return all_tiles