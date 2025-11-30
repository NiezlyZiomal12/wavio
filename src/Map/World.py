import pygame
import pytmx
from config import WIDTH, HEIGHT

class World:
    def __init__(self, width: int, height : int):
        self.width = width
        self.height = height
        self.collision_rects = []

    def clamp_pos(self, vector : pygame.Vector2) -> pygame.Vector2:
        vector.x = max(0, min(vector.x, self.width))
        vector.y = max(0, min(vector.y, self.height))
        return vector
    
    def clamp_camera(self, offset: pygame.Vector2, screen_w : int, screen_h : int) -> pygame.Vector2:
        offset.x = max(0, min(offset.x, self.width - screen_w))
        offset.y = max(0, min(offset.y, self.height - screen_h))
        return offset
    

    def load_collisions(self, level:pytmx.TiledMap)-> None:
        for obj in level.objects:
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            self.collision_rects.append(rect)


    def draw_tilemap(self,camera: object, level: pytmx.TiledMap, window: pygame.Surface) -> None:
        cam_x, cam_y = camera.offset
        tile_w = level.tilewidth
        tile_h = level.tileheight
        start_x = max(int(cam_x // tile_w) - 2, 0)
        end_x   = min(int((cam_x + WIDTH) // tile_w) + 2, level.width)
        start_y = max(int(cam_y // tile_h) - 2, 0)
        end_y   = min(int((cam_y + HEIGHT) // tile_h) + 2, level.height)
        for layer in level.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x in range(start_x, end_x):
                    for y in range(start_y, end_y):
                        gid = layer.data[y][x]
                        tile = level.get_tile_image_by_gid(gid)
                        if tile:
                            world_x = x * tile_w
                            world_y = y * tile_h
                            screen_pos = camera.apply(pygame.Rect(world_x, world_y, tile_w, tile_h))
                            window.blit(tile, screen_pos)