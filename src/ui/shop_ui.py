import pygame
import time
from src.utils import Animation
from src.weapons import WEAPON_CONFIG
from src.shop import build_weapon_shop_items

class ShopUi:
    def __init__(self, window, width, height, player, weapon_sprites: dict[str, pygame.Surface]):
        self.window = window
        self.width = width
        self.height = height
        self.player = player
        self.weapon_sprites = weapon_sprites

        self.roll_cost = 15
        self.roll_amount = 1

        self.active = False
        self.font = pygame.font.Font(None, 24)

        #popup animation
        self.animation_time = 0.2
        self.animation_start = 0
        self.scale = 0

        self.popup_rect = pygame.Rect(width // 2 - 200, height // 2 - 150, 400, 300)
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/shopUI.png").convert_alpha(), 400,300,0, 2, 0.2)
        self.image = self.popupSprite.get_current_frame()
        self.close_button_rect = pygame.Rect(self.popup_rect.right - 40, self.popup_rect.top + 10, 30, 30)

        self.shop_items = build_weapon_shop_items(WEAPON_CONFIG)
        self.visible_shop_items = []
        self.item_rects = []
        self.message = ""
        self.message_timer = 0.0


    def show(self) -> None:
        self.active = True
        self.animation_start = time.time()
        self.scale = 0.5

    
    def hide(self) -> None:
        self.active = False


    def handle_event(self, event:pygame.event.Event) -> None:
        if not self.active:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if self.close_button_rect.collidepoint(mx,my):
                self.hide()
                return
            
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx,my):
                    self._buy_item(i)
                    break

            if self.reroll_button_rect.collidepoint(mx, my):
                self.reroll_items()


    def _buy_item(self, index: int) -> None:
        item = self.visible_shop_items[index]
        sprite_sheet = self.weapon_sprites.get(item.item_id)

        success, reason = self.player.buy_weapon(item.item_id, sprite_sheet, item.price)
        if success:
            if reason == "upgraded":
                level = self.player.weapon_levels.get(item.item_id)
                self.message = f"{item.name} upgraded to Lv.{level}"
            else:
                self.message = f"Bought {item.name}"
        else:
            if reason == "slots_full":
                self.message = "Weapon slots are full"
            elif reason == "max_level":
                self.message = f"{item.name} is at max level"
            elif reason == "not_enough_gold":
                self.message = "Not enough gold"

        self.message_timer = 1.5


    def update_animation(self, dt:float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)


    def _refresh_visible_items(self) -> None:
        self.visible_shop_items = [
            item
            for item in self.shop_items
            if self.player.weapon_levels.get(item.item_id, 0) < item.max_level
        ]


    def _current_roll_cost(self) -> int:
        return self.roll_cost + 5 * self.roll_amount


    def reroll_items(self) -> None:
        roll_cost = self._current_roll_cost()
        if self.player.gold >= roll_cost:
            self.player.spend_gold(roll_cost)
            self._refresh_visible_items()
            self.show()
            self.roll_amount += 1
    

    def update(self, dt:float) -> None:
        self.update_animation(dt)
        self._refresh_visible_items()
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)


    def draw(self):
        if not self.active:
            return
        
        # Darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.window.blit(overlay, (0, 0))
        
        # Scale animation
        elapsed = time.time() - self.animation_start
        t = min(elapsed / self.animation_time, 1)
        eased = 1 - (1 - t)**3
        self.scale = 0.5 + (0.5 * eased)
        
        # --- ANIMATED POPUP SPRITE ---
        frame = self.popupSprite.get_current_frame()
        frame = pygame.transform.scale(
            frame,
            (
                int(self.popup_rect.width * self.scale),
                int(self.popup_rect.height * self.scale)
            )
        )   

        popup_x = self.popup_rect.centerx - frame.get_width() // 2
        popup_y = self.popup_rect.centery - frame.get_height() // 2 
        
        self.window.blit(frame, (popup_x, popup_y)) 
        
        # Draw title
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("SHOP", True, (255, 255, 0))
        self.window.blit(title, (popup_x + frame.get_width() // 2 - title.get_width() // 2, popup_y + 15))

        gold_text = self.font.render(f"Gold: {self.player.gold}", True, (255, 230, 120))
        self.window.blit(gold_text, (popup_x + 20, popup_y + 20))
        
        # Draw close button
        close_button_scaled = pygame.Rect(
            popup_x + self.popup_rect.width - 40,
            popup_y + 10,
            30,
            30
        )
        pygame.draw.rect(self.window, (255, 0, 0), close_button_scaled)
        close_text = self.font.render("X", True, (255, 255, 255))
        self.window.blit(close_text, (close_button_scaled.centerx - close_text.get_width() // 2, close_button_scaled.centery - close_text.get_height() // 2))
        
        # Draw items
        self.item_rects = []
        items_per_row = 3
        item_width = (self.popup_rect.width - 40 - (items_per_row - 1) * 10) // items_per_row
        item_height = 80
        base_y = popup_y + 70
        
        for i, item in enumerate(self.visible_shop_items):
            row = i // items_per_row
            col = i % items_per_row
            item_x = popup_x + 20 + col * (item_width + 10)
            item_y = base_y + row * (item_height + 10)
            
            item_rect = pygame.Rect(item_x, item_y, item_width, item_height)
            self.item_rects.append(item_rect)
            
            pygame.draw.rect(self.window, (60, 60, 60), item_rect, border_radius=5)
            pygame.draw.rect(self.window, (100, 200, 255), item_rect, 2, border_radius=5)
            
            weapon_level = self.player.weapon_levels.get(item.item_id, 0)
            level_text = f"Lv.{weapon_level}/{item.max_level}"

            item_text = self.font.render(item.name, True, (255, 255, 255))
            price_text = self.font.render(f"{item.price} gold", True, (255, 215, 0))
            level_surface = self.font.render(level_text, True, (170, 220, 255))

            self.window.blit(item_text, (item_rect.centerx - item_text.get_width() // 2, item_rect.y + 8))
            self.window.blit(price_text, (item_rect.centerx - price_text.get_width() // 2, item_rect.y + 30))
            self.window.blit(level_surface, (item_rect.centerx - level_surface.get_width() // 2, item_rect.y + 52))

        if self.message_timer > 0 and self.message:
            msg_surface = self.font.render(self.message, True, (255, 255, 255))
            self.window.blit(msg_surface, (popup_x + frame.get_width() // 2 - msg_surface.get_width() // 2, popup_y + frame.get_height() - 28))

        # reroll button
        reroll_rect = pygame.Rect(
            popup_x + self.popup_rect.width // 2 - 60,
            popup_y + self.popup_rect.height - 40,
            120,
            30
        )

        self.reroll_button_rect = reroll_rect

        pygame.draw.rect(self.window, (70,70,70), reroll_rect, border_radius=6)
        pygame.draw.rect(self.window, (200,200,200), reroll_rect, 2, border_radius=6)

        current_roll_cost = self._current_roll_cost()
        reroll_text = self.font.render(f"Reroll ({current_roll_cost}g)", True, (255,255,255))
        self.window.blit(
            reroll_text,
            (
                reroll_rect.centerx - reroll_text.get_width() // 2,
                reroll_rect.centery - reroll_text.get_height() // 2
            )
        )
