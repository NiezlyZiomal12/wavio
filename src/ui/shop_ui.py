import pygame
import pygame_gui
import random
from pygame_gui.elements import UIButton
from src.gameplay.weapons import WEAPON_CONFIG
from src.shop import build_weapon_shop_items
from src.core import Animation, wrap_text, build_random_pitch_sounds
from config import FONT, NAME_TEXT_COLOR, DESC_TEXT_COLOR, LVL_TEXT_COLOR, GOLD_TEXT_COLOR

class ShopUi:
    def __init__(self, window, width, height, player, price_multiplier: float):
        self.window = window
        self.width = width
        self.height = height
        self.current_size = self.window.get_size()
        self.player = player
        self.price_multiplier = max(0.1, price_multiplier)

        self.roll_cost = 15
        self.roll_amount = 1

        self.active = False
        self.font = pygame.font.Font(FONT, 24)

        self.click_sound = pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        self.power_up_sound = pygame.mixer.Sound("src/assets/sounds/game/power_up.wav")
        self.power_up_sound.set_volume(0.1)
        _roll_sounds = build_random_pitch_sounds("src/assets/sounds/gui/roll.wav", volume=0.10)
        self.roll_sound = _roll_sounds

        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")
        self.popup_rect = self._compute_popup_rect()
        self.popupSprite = Animation(pygame.image.load("src/assets/ui/shopUI.png").convert_alpha(), 400,300,0, 2, 0.2)
        self.image = self.popupSprite.get_current_frame()

        self.close_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 34, 34),
            text="X",
            manager=self.manager,
            object_id="#closeButton"
        )
        self.reroll_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 150, 38),
            text="Reroll",
            manager=self.manager,
            object_id="#rerollButton"
        )

        self.item_rects = []
        self.item_icon_cache = {}
        self._item_layout_dirty = True

        self._set_ui_visible(False)
        self._responsive_ui(force=True)



        self.shop_items = build_weapon_shop_items(WEAPON_CONFIG)
        self.max_visible_items = 3
        self.visible_shop_items = []


    def _set_ui_visible(self, visible: bool) -> None:
        if visible:
            self.close_button.show()
            self.reroll_button.show()
        else:
            self.close_button.hide()
            self.reroll_button.hide()


    def _get_item_icon(self, item_id: str, target_size: int) -> pygame.Surface:
        if item_id not in self.item_icon_cache:
            config = WEAPON_CONFIG.get(item_id, {})
            sprite_path = config.get("sprite_path")
            icon_surface = None

            if sprite_path:
                try:
                    loaded = pygame.image.load(sprite_path).convert_alpha()
                    anim = config.get("animation", {})
                    frame_w = int(anim.get("sprite_width", loaded.get_width()))
                    frame_h = int(anim.get("sprite_height", loaded.get_height()))
                    frame_w = max(1, min(frame_w, loaded.get_width()))
                    frame_h = max(1, min(frame_h, loaded.get_height()))
                    icon_surface = loaded.subsurface((0, 0, frame_w, frame_h)).copy()
                except (pygame.error, FileNotFoundError):
                    icon_surface = None

            if icon_surface is None:
                icon_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.rect(icon_surface, (190, 155, 75), icon_surface.get_rect(), border_radius=4)

            self.item_icon_cache[item_id] = icon_surface

        base_icon = self.item_icon_cache[item_id]
        return pygame.transform.smoothscale(base_icon, (target_size, target_size))


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
        self._item_layout_dirty = True

        font_size = max(16, min(28, int(min(self.popup_rect.width, self.popup_rect.height) * 0.07)))
        self.font = pygame.font.Font(FONT, font_size)

        close_size = max(28, min(40, int(self.popup_rect.width * 0.08)))
        self.close_button.set_dimensions((close_size, close_size))
        self.close_button.set_relative_position((self.popup_rect.right - close_size - 16, self.popup_rect.top + 16))

        reroll_width = max(130, min(230, int(self.popup_rect.width * 0.38)))
        reroll_height = max(30, min(46, int(self.popup_rect.height * 0.11)))
        reroll_x = self.popup_rect.centerx - reroll_width // 2
        reroll_y = self.popup_rect.bottom - reroll_height - 20
        self.reroll_button.set_dimensions((reroll_width, reroll_height))
        self.reroll_button.set_relative_position((reroll_x, reroll_y))


    def show(self) -> None:
        self.active = True
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
                self.click_sound.play()
                self.hide()
                return
            if event.ui_element == self.reroll_button:
                random.choice(self.roll_sound).play()
                self.reroll_items()
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(mx, my):
                    self.power_up_sound.play()
                    self._buy_item(i)
                    break


    def _buy_item(self, index: int) -> None:
        item = self.visible_shop_items[index]
        item_price = self._get_item_price(item)
        success, reason = self.player.buy_weapon(item.item_id, item_price)



    def _get_item_price(self, item) -> int:
        return max(1, int(round(item.price * self.price_multiplier)))


    def update_animation(self, dt:float) -> None:
        self.image = self.popupSprite.get_current_frame()
        self.popupSprite.update(dt)


    def _refresh_visible_items(self, force_new: bool = False) -> None:
        before_ids = [item.item_id for item in self.visible_shop_items]
        eligible_items = [
            item
            for item in self.shop_items
            if self.player.weapon_levels.get(item.item_id, 0) < item.max_level
        ]

        if not eligible_items:
            self.visible_shop_items = []
            self._item_layout_dirty = True
            return

        visible_count = min(self.max_visible_items, len(eligible_items))

        if force_new or not self.visible_shop_items:
            self.visible_shop_items = random.sample(eligible_items, visible_count)
            self._item_layout_dirty = True
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
        after_ids = [item.item_id for item in self.visible_shop_items]
        if after_ids != before_ids:
            self._item_layout_dirty = True


    def _current_roll_cost(self) -> int:
        base_cost = self.roll_cost + 5 * self.roll_amount
        return max(1, int(round(base_cost * self.price_multiplier)))


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


    def draw(self):
        if not self.active:
            return

        self._responsive_ui()
        
        # Darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.window.blit(overlay, (0, 0))
        
        # --- popup sprite ---
        frame = self.popupSprite.get_current_frame()
        frame = pygame.transform.scale(
            frame,
            (
                self.popup_rect.width,
                self.popup_rect.height
            )
        )   

        popup_x = self.popup_rect.centerx - frame.get_width() // 2
        popup_y = self.popup_rect.centery - frame.get_height() // 2 
        
        self.window.blit(frame, (popup_x, popup_y)) 

        self.item_rects = []
        base_positions = [0.22, 0.42, 0.62]

        for i, item in enumerate(self.visible_shop_items):
            if i >= len(base_positions):
                break

            base_y = int(frame.get_height() * base_positions[i])
            rect = pygame.Rect(
                popup_x + int(frame.get_width() * 0.09),
                popup_y + base_y,
                int(frame.get_width() * 0.82),
                max(54, int(frame.get_height() * 0.16))
            )
            self.item_rects.append(rect)

            card_bg = (28, 38, 44)
            card_border = (194, 167, 97)
            pygame.draw.rect(self.window, card_bg, rect, border_radius=7)
            pygame.draw.rect(self.window, card_border, rect, 2, border_radius=7)

            icon_size = max(26, int(rect.height * 0.64))
            icon = self._get_item_icon(item.item_id, icon_size)
            icon_x = rect.x + max(8, int(rect.width * 0.03))
            icon_y = rect.centery - icon.get_height() // 2
            self.window.blit(icon, (icon_x, icon_y))

            weapon_level = self.player.weapon_levels.get(item.item_id, 0)
            item_price = self._get_item_price(item)
            affordable = self.player.gold >= item_price

            name_x = icon_x + icon.get_width() + max(8, int(rect.width * 0.03))
            name_y = rect.y + max(4, int(rect.height * 0.08))

            name_surface = self.font.render(item.name, True, NAME_TEXT_COLOR)
            self.window.blit(name_surface, (name_x, name_y))

            level_text = f"Lv.{weapon_level}/{item.max_level}"
            level_surface = self.font.render(level_text, True, LVL_TEXT_COLOR)
            level_x = rect.right - level_surface.get_width() - max(8, int(rect.width * 0.03))
            self.window.blit(level_surface, (level_x, name_y))

            price_color = (145, 220, 128) if affordable else (236, 122, 122)
            price_surface = self.font.render(f"{item_price}g", True, price_color)
            price_x = rect.right - price_surface.get_width() - max(8, int(rect.width * 0.03))
            price_y = name_y + level_surface.get_height()
            self.window.blit(price_surface, (price_x, price_y))

            desc_lines = wrap_text(
                item.description,
                self.font,
                max(80, rect.width - (icon.get_width() + int(rect.width * 0.24)))
            )
            desc_y = name_y + name_surface.get_height()
            for line in desc_lines[:2]:
                desc_surface = self.font.render(line, True, DESC_TEXT_COLOR)
                self.window.blit(desc_surface, (name_x, desc_y))
                desc_y += desc_surface.get_height()
        
        # Draw title
        title_font = pygame.font.Font(FONT, 32)
        title = title_font.render("SHOP", True, NAME_TEXT_COLOR)
        self.window.blit(title, (popup_x + frame.get_width() // 2 - title.get_width() // 2, popup_y + 15))

        gold_text = self.font.render(f"Gold: {self.player.gold}", True, GOLD_TEXT_COLOR )
        self.window.blit(gold_text, (popup_x + max(14, int(frame.get_width() * 0.04)), popup_y + max(12, int(frame.get_height() * 0.04))))

        # reroll button
        current_roll_cost = self._current_roll_cost()
        self.reroll_button.set_text(f"Reroll ({current_roll_cost}g)")

        self.manager.draw_ui(self.window)

