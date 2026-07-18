import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIImage
from src.gameplay.player.characters_config import CHARACTERS
from src.core.audio import apply_sfx_volume
from src.core import Animation
from config import FONT


STAT_LABELS = {
    "max_health":       "Health",
    "damage":           "Damage",
    "armor":            "Armor",
    "speed":            "Speed",
    "reduce_cooldown":  "CD Reduction",
    "projectile_count": "Projectiles",
    "crit_chance":      "Crit Chance",
    "pickup_range":     "Pickup Range",
}

PASSIVE_LABELS = {
    "hp_mult":              "HP Multiplier",
    "armor_mult":           "Armor Multiplier",
    "cd_mult":              "CD Multiplier",
    "dmg_mult":             "Damage Multiplier",
    "speed_mult":           "Speed Multiplier",
    "crit_mult":            "Crit Multiplier",
    "xp_gain_mult":         "XP Gain Multiplier",
    "xp_damage_per_point":  "XP to Damage",
    "item_stat_mult":       "Item Stat Multiplier",
}


def _load_character_surface(name: str, size: tuple[int, int]) -> pygame.Surface:
    path = CHARACTERS[name]["Image_path"]
    surface = pygame.image.load(path).convert_alpha()
    frame_w, frame_h = CHARACTERS[name]["animation_config"]["frame_size"]
    img = Animation(surface, frame_w, frame_h, 0, 2, 1)
    single_image = img.get_current_frame()
    return pygame.transform.scale(single_image, size)

class Character_select_scene:
    def __init__(self, window: pygame.Surface):
        self.window = window
        self.running = True
        self.start_game = False
        self.back_requested = False
        self.selected_character = "Mage"
        self.click_sound = apply_sfx_volume(
            pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        )

        self.current_size = self.window.get_size()
        self.manager = pygame_gui.UIManager(
            self.current_size,
            theme_path="src/assets/pygame_gui_styles/pause_theme.json"
        )

        self.title_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 440, 40),
            text="Choose Your Character",
            manager=self.manager,
            object_id="#label"
        )

        self.info_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 760, 200),
            starting_height=1,
            manager=self.manager,
        )

        self._portrait_rect = pygame.Rect(0, 0, 1, 1)
        self._portrait_surf: pygame.Surface | None = None

        self.info_name_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 34),
            text=self.selected_character,
            manager=self.manager,
            container=self.info_panel,
            object_id="#label"
        )
        self.info_weapon_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 22),
            text="",
            manager=self.manager,
            container=self.info_panel,
            object_id="#label"
        )

        # Stats section header
        self.stats_header_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 160, 22),
            text="Stats",
            manager=self.manager,
            container=self.info_panel,
            object_id="#label"
        )

        MAX_STATS = 6
        self._stat_row_labels: list[UILabel] = []
        for _ in range(MAX_STATS):
            lbl = UILabel(
                relative_rect=pygame.Rect(0, 0, 200, 20),
                text="",
                manager=self.manager,
                container=self.info_panel,
                object_id="#label"
            )
            self._stat_row_labels.append(lbl)

        # Passive section header
        self.passive_header_label = UILabel(
            relative_rect=pygame.Rect(0, 0, 160, 22),
            text="Passives",
            manager=self.manager,
            container=self.info_panel,
            object_id="#label"
        )

        MAX_PASSIVES = 3
        self._passive_row_labels: list[UILabel] = []
        for _ in range(MAX_PASSIVES):
            lbl = UILabel(
                relative_rect=pygame.Rect(0, 0, 200, 20),
                text="",
                manager=self.manager,
                container=self.info_panel,
                object_id="#label"
            )
            self._passive_row_labels.append(lbl)

        self.container_panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, 600, 180),
            starting_height=1,
            manager=self.manager,
        )

        self.character_buttons: dict[str, UIButton] = {}
        for name in CHARACTERS:
            btn = UIButton(
                relative_rect=pygame.Rect(0, 0, 100, 120),
                text="",
                manager=self.manager,
                container=self.container_panel,
                object_id="#button"
            )
            self.character_buttons[name] = btn

        self.start_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 160, 56),
            text="Battle",
            manager=self.manager,
            object_id="#button"
        )
        self.back_button = UIButton(
            relative_rect=pygame.Rect(0, 0, 160, 56),
            text="Back",
            manager=self.manager,
            object_id="#button"
        )

        self._card_portrait_surfs: dict[str, pygame.Surface] = {}
        self._last_card_size: tuple[int, int] = (0, 0)
        self._btn_positions: dict[str, pygame.Rect] = {}

        # Cached layout values shared between _responsive_ui and _update_info_panel
        self._info_col_x: int = 0
        self._info_w: int = 0
        self._info_x: int = 0
        self._info_y: int = 0
        self._info_h: int = 0

        self._responsive_ui()
        self._update_info_panel()


    def get_selected_character(self) -> str:
        return self.selected_character


    def _responsive_ui(self) -> None:
        width, height = self.current_size

        # Title
        title_w = max(280, min(520, int(width * 0.55)))
        self.title_label.set_dimensions((title_w, 40))
        self.title_label.set_relative_position(((width - title_w) // 2, int(height * 0.04)))

        # ── Info panel (top)
        info_w = max(440, min(width - 80, 860))
        info_h = max(200, min(int(height * 0.40), 300))
        info_x = (width - info_w) // 2
        info_y = int(height * 0.11)
        self.info_panel.set_dimensions((info_w, info_h))
        self.info_panel.set_relative_position((info_x, info_y))

        # Cache for _update_info_panel
        self._info_w  = info_w
        self._info_h  = info_h
        self._info_x  = info_x
        self._info_y  = info_y

        # Portrait: left column, square, ~28% panel width
        portrait_size = min(info_h - 30, int(info_w * 0.20))
        portrait_size = max(40, portrait_size)
        self._portrait_rect = pygame.Rect(
            info_x + 30,
            info_y + (info_h - portrait_size) // 2,
            portrait_size,
            portrait_size,
        )
        self._portrait_surf = _load_character_surface(
            self.selected_character, (portrait_size, portrait_size)
        )

        # Text area starts after portrait
        col_x = portrait_size + 28    # left edge of text area inside panel
        self._info_col_x = col_x

        # Split text area into left (stats) and right (passives) halves
        text_w = info_w - col_x - 12   # total text area width
        left_w = int(text_w * 0.52)    # stats column width
        right_x = col_x + left_w + 8    # passives column x inside panel
        right_w = text_w - left_w - 8

        ROW_H  = 20
        GAP    = 3
        PAD_T  = 12

        # Name + weapon span the full text width
        self.info_name_label.set_dimensions((text_w, 30))
        self.info_name_label.set_relative_position((col_x, PAD_T))

        self.info_weapon_label.set_dimensions((text_w, 20))
        self.info_weapon_label.set_relative_position((col_x, PAD_T + 32))

        # Stats header + rows (left column)
        stats_start_y = PAD_T + 58
        self.stats_header_label.set_dimensions((left_w, ROW_H))
        self.stats_header_label.set_relative_position((col_x, stats_start_y))

        for i, lbl in enumerate(self._stat_row_labels):
            y = stats_start_y + ROW_H + GAP + i * (ROW_H + GAP)
            lbl.set_dimensions((left_w, ROW_H))
            lbl.set_relative_position((col_x, y))

        # Passives header + rows (right column, same top baseline)
        self.passive_header_label.set_dimensions((right_w, ROW_H))
        self.passive_header_label.set_relative_position((right_x, stats_start_y))

        for i, lbl in enumerate(self._passive_row_labels):
            y = stats_start_y + ROW_H + GAP + i * (ROW_H + GAP)
            lbl.set_dimensions((right_w, ROW_H))
            lbl.set_relative_position((right_x, y))

        # ── Selection panel (bottom)
        
        panel_w = max(300, min(width - 80, 760))
        panel_h = 150                       
        panel_x = (width - panel_w) // 2
        panel_y = info_y + info_h + max(8, int(height * 0.015))
        self.container_panel.set_dimensions((panel_w, panel_h))
        self.container_panel.set_relative_position((panel_x, panel_y))

        count = max(1, len(self.character_buttons))
        side_pad = max(10, int(panel_w * 0.04))
        avail_w = panel_w - 2 * side_pad

        # Cards
        btn_w = 90
        btn_h = 110
        total_btn_w = count * btn_w
        gap = max(8, (avail_w - total_btn_w) // (count + 1))
        start_x = side_pad + gap
        btn_y = (panel_h - btn_h) // 2

        # Image inside button
        img_inset = 6
        card_img_w = btn_w - img_inset * 2
        card_img_h = btn_h - img_inset * 2
        card_size = (card_img_w, card_img_h)

        if card_size != self._last_card_size:
            self._last_card_size = card_size
            self._card_portrait_surfs = {
                name: _load_character_surface(name, card_size)
                for name in CHARACTERS
            }

        self._btn_positions = {}
        for i, (name, btn) in enumerate(self.character_buttons.items()):
            x = start_x + i * (btn_w + gap)
            btn.set_dimensions((btn_w, btn_h))
            btn.set_relative_position((x, btn_y))
            self._btn_positions[name] = pygame.Rect(
                panel_x + x + img_inset,
                panel_y + btn_y + img_inset,
                card_img_w,
                card_img_h,
            )

        # ── Nav buttons
        nav_w = max(140, min(200, int(width * 0.17)))
        nav_h = max(44, min(58, int(height * 0.07)))
        self.start_button.set_dimensions((nav_w, nav_h))
        self.start_button.set_relative_position((width - nav_w - 24, height - nav_h - 20))
        self.back_button.set_dimensions((nav_w, nav_h))
        self.back_button.set_relative_position((24, height - nav_h - 20))


    def _update_info_panel(self) -> None:
        char_data = CHARACTERS.get(self.selected_character, {})
        stats = char_data["Stats"]
        passives = char_data["Passive"]
        weapon = char_data["Starting_weapon"]

        self.info_name_label.set_text(self.selected_character)
        self.info_weapon_label.set_text(f"Weapon: {weapon}")

        # Reload portrait at current size
        portrait_size = self._portrait_rect.width
        if portrait_size > 1:
            self._portrait_surf = _load_character_surface(
                self.selected_character, (portrait_size, portrait_size)
            )

        # Stat rows
        stat_items = list(stats.items())
        for i, lbl in enumerate(self._stat_row_labels):
            if i < len(stat_items):
                key, val = stat_items[i]
                name_str = STAT_LABELS.get(key, key.replace("_", " ").title())
                lbl.set_text(f"{name_str}:  {val}")
                lbl.show()
            else:
                lbl.set_text("")
                lbl.hide()

        # Passive rows
        passive_items = list(passives.items())
        for i, lbl in enumerate(self._passive_row_labels):
            if i < len(passive_items):
                key, val = passive_items[i]
                name_str = PASSIVE_LABELS.get(key, key.replace("_", " ").title())
                lbl.set_text(f"{name_str}:  {val}")
                lbl.show()
            else:
                lbl.set_text("")
                lbl.hide()

        if passive_items:
            self.passive_header_label.show()
        else:
            self.passive_header_label.hide()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.VIDEORESIZE:
                self.current_size = (event.w, event.h)
                self.manager.set_window_resolution(self.current_size)
                self._responsive_ui()

            self.manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                self.click_sound.play()
                if event.ui_element == self.start_button:
                    self.start_game = True
                elif event.ui_element == self.back_button:
                    self.back_requested = True
                else:
                    for name, btn in self.character_buttons.items():
                        if event.ui_element == btn:
                            self.selected_character = name
                            self._update_info_panel()
                            break

    def update(self, dt: float) -> None:
        new_size = self.window.get_size()
        if new_size != self.current_size:
            self.current_size = new_size
            self.manager.set_window_resolution(self.current_size)
            self._responsive_ui()
        self.manager.update(dt)

    def render(self) -> None:
        self.window.fill((26, 37, 37))
        self.manager.draw_ui(self.window)

        # Portrait in info panel
        if self._portrait_surf is not None:
            self.window.blit(self._portrait_surf, self._portrait_rect)

        # Card portraits + selection highlight
        font = pygame.font.Font(FONT)
        for name, rect in self._btn_positions.items():
            surf = self._card_portrait_surfs.get(name)
            if surf is not None:
                if surf.get_size() != (rect.width, rect.height):
                    surf = pygame.transform.scale(surf, (rect.width, rect.height))
                    self._card_portrait_surfs[name] = surf
                self.window.blit(surf, rect)

            if name == self.selected_character:
                pygame.draw.rect(
                    self.window,
                    (220, 180, 60),
                    rect.inflate(12, 12),
                    3,
                    border_radius=5,
                )