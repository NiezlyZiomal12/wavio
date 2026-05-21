import random
import pygame


ACTIVE_ITEM_CONFIG = {
	"fancy_boots": {
		"name": "Fancy Boots",
		"description" : "ables you to dash once per 6 seconds",
		"icon": "src/assets/items/upgrades/active_items/fancy_boots.png",
		"cooldown": 6.0,
	},
	"lantern": {
		"name": "Lantern",
		"description" : "Creates a light that damages the enemies",
		"icon": "src/assets/items/upgrades/active_items/lantern.png",
		"cooldown": 0.0,
	},
}

def create_active_item(item_id: str) -> "ActiveItem":
	item_id = item_id.lower()
	if item_id == "fancy_boots":
		return FancyBoots()
	if item_id == "lantern":
		return Lantern()


class ActiveItem:
	def __init__(self, item_id: str, icon: pygame.Surface, cooldown: float) -> None:
		self.item_id = item_id
		self.icon = icon
		self.cooldown = cooldown
		self.cooldown_timer = 0.0
		self.cooldown_total = cooldown

	def get_cooldown(self, player: object) -> float:
		if self.cooldown <= 0:
			return 0.0
		reduction = max(0.0, min(0.9, getattr(player, "reduce_cooldown", 0.0) / 100))
		return self.cooldown * (1.0 - reduction)

	def ready(self) -> bool:
		return self.cooldown_timer <= 0.0

	def tick(self, dt: float) -> None:
		if self.cooldown_timer > 0:
			self.cooldown_timer = max(0.0, self.cooldown_timer - dt)

	def update(self, dt: float, player: object, enemies: list) -> None:
		self.tick(dt)

	def activate(self, player: object, enemies: list) -> bool:
		if not self.ready():
			return False
		if self.on_activate(player, enemies):
			self.cooldown_timer = self.get_cooldown(player)
			self.cooldown_total = self.cooldown_timer
			return True
		return False

	def on_activate(self, player: object, enemies: list) -> bool:
		return False

	def draw(self, surface: pygame.Surface, camera: object, player_pos: pygame.Vector2) -> None:
		return


class FancyBoots(ActiveItem):
	def __init__(self) -> None:
		config = ACTIVE_ITEM_CONFIG["fancy_boots"]
		icon = pygame.image.load(config["icon"]).convert_alpha()
		super().__init__("fancy_boots", icon, config["cooldown"])
		self.dash_duration = 0.25
		self.dash_speed_multiplier = 2.0

	def on_activate(self, player: object, enemies: list) -> bool:
		return player.start_dash(self.dash_duration, self.dash_speed_multiplier)


class Lantern(ActiveItem):
	def __init__(self) -> None:
		config = ACTIVE_ITEM_CONFIG["lantern"]
		icon = pygame.image.load(config['icon']).convert_alpha()
		super().__init__("lantern", icon, config["cooldown"])
		self.radius = 140
		self.damage = 10
		self.tick_rate = 0.5
		self._tick_timer = 0.0
		self._color = (255, 210, 90, 60)

	def update(self, dt: float, player: object, enemies: list) -> None:
		self._tick_timer += dt
		if self._tick_timer < self.tick_rate:
			return
		self._tick_timer = 0.0
		for enemy in enemies:
			if getattr(enemy, "dead", False) or getattr(enemy, "spawning", False):
				continue
			if enemy.position.distance_to(player.position) <= self.radius:
				enemy.take_damage(self.damage * player.damage, None)

	def draw(self, surface: pygame.Surface, camera: object, player_pos: pygame.Vector2) -> None:
		radius = int(self.radius)
		effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
		pygame.draw.circle(effect_surface, self._color, (radius, radius), radius, width=2)
		screen_pos = camera.apply(pygame.Rect(0, 0, 0, 0).move(int(player_pos.x), int(player_pos.y)))
		draw_pos = (screen_pos.centerx - radius, screen_pos.centery - radius)
		surface.blit(effect_surface, draw_pos)


class ActiveItemDrop(pygame.sprite.Sprite):

	def __init__(self, pos: pygame.Vector2, item_id: str, player: object) -> None:
		super().__init__()
		
		self.item_id = item_id.lower()
		self.player = player
		self.position = pygame.Vector2(pos)
		self.image = pygame.image.load('src/assets/items/dropable/chest.png').convert_alpha()
		self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
		self.collect_radius = 80
		self.pickup_radius = 18
		self.reveal_timer = 0.0
		self.reveal_duration = 0.2
		self.revealed = False

	def _reveal_item(self) -> None:
		item_icon = pygame.image.load(ACTIVE_ITEM_CONFIG[self.item_id]["icon"]).convert_alpha()
		self.image = item_icon
		self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))
		self.reveal_timer = self.reveal_duration
		self.revealed = True

	def _equip_player(self) -> None:
		self.player.set_active_item(create_active_item(self.item_id))
		self.kill()

	def update(self, dt: float, player: object) -> None:
		distance_to_player = self.position.distance_to(player.position)

		if not self.revealed:
			if distance_to_player <= self.pickup_radius:
				self._reveal_item()
			return

		self.reveal_timer -= dt
		if self.reveal_timer <= 0:
			self._equip_player()

	def draw(self, surface: pygame.Surface, camera: object) -> None:
		screen_rect = camera.apply(self.rect)
		surface.blit(self.image, screen_rect)


def random_active_item_id() -> str:
	return random.choice(list(ACTIVE_ITEM_CONFIG.keys()))
