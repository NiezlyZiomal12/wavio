import pygame
import pygame_gui
import time
import random
from pygame_gui.elements import UIButton
from src.gameplay.weapons import WEAPON_CONFIG
from src.shop import build_weapon_shop_items
from src.core import Animation

class ShopUi:
    def __init__(self, window, width, height, player):
        self.window = window
        self.width = width
        self.height = height
        self.current_size = self.window.get_size()
        self.player = player

        self.roll_cost = 15
        self.roll_amount = 1

        self.active = False
        self.font = pygame.font.Font(None, 24)

        #popup animation
        self.animation_time = 0.2
        self.animation_start = 0
        self.scale = 0

        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")
        self.popup_rect = self._compute_popup_rect()
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/shopUI.png").convert_alpha(), 400,300,0, 2, 0.2)
        self.image = self.popupSprite.get_current_frame()

        self.close_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 34, 34),
            text="X",
            manager=self.manager,
        )
        self.reroll_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 150, 38),
            text="Reroll",
            manager=self.manager,
        )
        self._set_ui_visible(False)
        self._responsive_ui(force=True)



        self.shop_items = build_weapon_shop_items(WEAPON_CONFIG)
        self.max_visible_items = 3
        self.visible_shop_items = []
        self.item_rects = []
        self.message = ""
        self.message_timer = 0.0


    def _set_ui_visible(self, visible: bool) -> None:
        if visible:
            self.close_button.show()
            self.reroll_button.show()
        else:
            self.close_button.hide()
            self.reroll_button.hide()


    def _compute_popup_rect(self) -> pygame.Rect:
        width, height = self.current_size
        margin = max(12, int(min(width, height) * 0.05))
        popup_width = max(360, min(640, width - (2 * margin)))
        popup_height = max(280, min(460, height - (2 * margin)))
        return pygame.Rect((width - popup_width) // 2, (height - popup_height) // 2, popup_width, popup_height)


    def _responsive_ui(self, force: bool = False) -> None:
        new_size = self.window.get_size()
        if not force and new_size == self.current_size:
            return

        self.current_size = new_size
        self.width, self.height = new_size
        self.manager.set_window_resolution(self.current_size)
        self.popup_rect = self._compute_popup_rect()

        font_size = max(16, min(28, int(min(self.popup_rect.width, self.popup_rect.height) * 0.07)))
        self.font = pygame.font.Font(None, font_size)

        close_size = max(28, min(40, int(self.popup_rect.width * 0.08)))
        self.close_button.set_dimensions((close_size, close_size))
        self.close_button.set_relative_position((self.popup_rect.right - close_size - 8, self.popup_rect.top + 8))

        reroll_width = max(130, min(230, int(self.popup_rect.width * 0.38)))
        reroll_height = max(30, min(46, int(self.popup_rect.height * 0.11)))
        reroll_x = self.popup_rect.centerx - reroll_width // 2
        reroll_y = self.popup_rect.bottom - reroll_height - 12
        self.reroll_button.set_dimensions((reroll_width, reroll_height))
        self.reroll_button.set_relative_position((reroll_x, reroll_y))


    def show(self) -> None:
        self.active = True
        self.animation_start = time.time()
        self.scale = 0.5
        self._set_ui_visible(True)

    
    def hide(self) -> None:
        self.active = False
        self._set_ui_visible(False)


    def handle_event(self, event:pygame.event.Event) -> None:
        self._responsive_ui()

        if not self.active:
            return

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return
            if event.ui_element == self.reroll_button:
                self.reroll_items()
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx,my):
                    self._buy_item(i)
                    break


    def _buy_item(self, index: int) -> None:
        item = self.visible_shop_items[index]
        success, reason = self.player.buy_weapon(item.item_id, item.price)
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


    def _refresh_visible_items(self, force_new: bool = False) -> None:
        eligible_items = [
            item
            for item in self.shop_items
            if self.player.weapon_levels.get(item.item_id, 0) < item.max_level
        ]

        if not eligible_items:
            self.visible_shop_items = []
            return

        visible_count = min(self.max_visible_items, len(eligible_items))

        if force_new or not self.visible_shop_items:
            self.visible_shop_items = random.sample(eligible_items, visible_count)
            return

        eligible_ids = {item.item_id for item in eligible_items}
        retained_items = [
            item for item in self.visible_shop_items if item.item_id in eligible_ids
        ]

        if len(retained_items) < visible_count:
            retained_ids = {item.item_id for item in retained_items}
            refill_pool = [
                item for item in eligible_items if item.item_id not in retained_ids
            ]
            needed = visible_count - len(retained_items)
            retained_items.extend(random.sample(refill_pool, min(needed, len(refill_pool))))

        self.visible_shop_items = retained_items[:visible_count]


    def _current_roll_cost(self) -> int:
        return self.roll_cost + 5 * self.roll_amount


    def reroll_items(self) -> None:
        roll_cost = self._current_roll_cost()
        if self.player.gold >= roll_cost:
            self.player.spend_gold(roll_cost)
            self._refresh_visible_items(force_new=True)
            self.show()
            self.roll_amount += 1
    

    def update(self, dt:float) -> None:
        self._responsive_ui()
        self.update_animation(dt)
        self._refresh_visible_items()
        if self.active:
            self.manager.update(dt)
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)


    def draw(self):
        if not self.active:
            return

        self._responsive_ui()
        
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
        self.window.blit(gold_text, (popup_x + max(14, int(frame.get_width() * 0.04)), popup_y + max(12, int(frame.get_height() * 0.04))))

        # Draw items
        self.item_rects = []
        items_per_row = 3
        horizontal_padding = max(16, int(frame.get_width() * 0.05))
        item_gap_x = max(8, int(frame.get_width() * 0.02))
        item_gap_y = max(8, int(frame.get_height() * 0.03))
        item_width = (frame.get_width() - (2 * horizontal_padding) - (items_per_row - 1) * item_gap_x) // items_per_row
        item_height = max(72, int(frame.get_height() * 0.24))
        base_y = popup_y + max(70, int(frame.get_height() * 0.22))
        
        for i, item in enumerate(self.visible_shop_items):
            row = i // items_per_row
            col = i % items_per_row
            item_x = popup_x + horizontal_padding + col * (item_width + item_gap_x)
            item_y = base_y + row * (item_height + item_gap_y)
            
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
        current_roll_cost = self._current_roll_cost()
        self.reroll_button.set_text(f"Reroll ({current_roll_cost}g)")

        self.manager.draw_ui(self.window)

