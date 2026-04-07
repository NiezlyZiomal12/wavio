import pygame
from .weapon import Weapon

class Boomerang(Weapon):
    def __init__(self, config, start_pos,target_pos, player):
        super().__init__(config, start_pos, player)

        self.start_pos = pygame.Vector2(start_pos)
        #player prop for returning to player 
        self.player = player
        self.pierce_count = config['special']['pierce_count']
        self.return_speed = config['special']['return_speed']

        self.max_range = 360.0
        self.max_return_speed = 800

        direction = target_pos - start_pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.Vector2(0,0)

        self.returning = False
        self.facing_left = direction.x > 0
        self.should_destroy_on_hit = False
        self.distance_traveled = 0.0
        #Adding hit cooldown so that dont hit each frame (too much dmg)
        self.hit_cooldown = 0.15
        self.recent_hits = {}
        self.life = 0
        self.lifetime = config['special']['lifetime']


    def update(self, dt:float) -> None:
        super().update(dt)

        if self.velocity.length() > self.max_return_speed:
            self.velocity = self.velocity.normalize() * self.max_return_speed

        #calculating hit cooldown for each enemy
        enemies_to_remove = []
        for enemy, timer in self.recent_hits.items():
            timer -= dt
            if timer <= 0:
                enemies_to_remove.append(enemy)
            else:
                self.recent_hits[enemy] = timer
        for enemy in enemies_to_remove:
            del self.recent_hits[enemy]

        if not self.returning:
            self.distance_traveled = (self.position - self.start_pos).length()
            if self.distance_traveled >= self.max_range:
                self.returning = True

        if self.returning:
            to_player = (pygame.Vector2(self.player.rect.center) - pygame.Vector2(self.rect.center))
            if to_player.length() > 5:
                acceleration = to_player.normalize() * self.return_speed * 40
                self.velocity += acceleration * dt 
            else:
                self.kill()
        
        self.life += dt
        if self.life >= self.lifetime:
            self.kill()
            self.life = 0

        self.position += self.velocity * dt
        self.rect.center = self.position

        
    def on_hit_enemy(self, enemy:object) -> bool:
        """Function that does pierce damage"""
        if enemy in self.recent_hits:
            return False
        self.recent_hits[enemy] = self.hit_cooldown
        self.pierce_count -= 1
        if self.pierce_count <= 0:
            self.returning = True
        return True