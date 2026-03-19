import pygame
import pygame_gui
from html import escape
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextBox


class PauseMenuUi:
    def __init__(self, window, width: int, height: int, player: object):
        self.window = window
        self.width = width
        self.height = height
        self.player = player
        self.active = False
        self.manager = pygame_gui.UIManager((width, height), theme_path="src/assets/pygame_gui_styles/pause_theme.json")
        self._last_stats_text = ""

        self.popup_rect = pygame.Rect(0, 0, 720, 420)
        self.popup_rect.center = (width // 2, height // 2)

        left_panel_rect = pygame.Rect(
            28,
            28,
            290,
            self.popup_rect.height - 56,
        )
        right_panel_rect = pygame.Rect(
            left_panel_rect.right + 22,
            28,
            self.popup_rect.width - left_panel_rect.width - 78,
            self.popup_rect.height - 56,
        )

        button_width = left_panel_rect.width - 40
        button_height = 46
        start_y = 108
        gap = 14

        self.popup_panel = UIPanel(
            relative_rect=self.popup_rect,
            manager=self.manager,
            object_id="#pause_popup",
        )

        self.left_panel = UIPanel(
            relative_rect=left_panel_rect,
            manager=self.manager,
            container=self.popup_panel,
            object_id="#pause_left_panel",
        )

        self.right_panel = UIPanel(
            relative_rect=right_panel_rect,
            manager=self.manager,
            container=self.popup_panel,
            object_id="#pause_right_panel",
        )

        self.title_label = UILabel(
            relative_rect=pygame.Rect(20, 24, left_panel_rect.width - 40, 52),
            text="Paused",
            manager=self.manager,
            container=self.left_panel,
            object_id="#pause_title",
        )

        self.resume_button = UIButton(
            relative_rect=pygame.Rect(20, start_y, button_width, button_height),
            text="Resume",
            manager=self.manager,
            container=self.left_panel,
        )
        self.restart_button = UIButton(
            relative_rect=pygame.Rect(20, start_y + (button_height + gap), button_width, button_height),
            text="Restart",
            manager=self.manager,
            container=self.left_panel,
        )
        self.options_button = UIButton(
            relative_rect=pygame.Rect(20, start_y + 2 * (button_height + gap), button_width, button_height),
            text="Options",
            manager=self.manager,
            container=self.left_panel,
        )
        self.menu_button = UIButton(
            relative_rect=pygame.Rect(20, start_y + 3 * (button_height + gap), button_width, button_height),
            text="Menu",
            manager=self.manager,
            container=self.left_panel,
        )

        self.stats_title = UILabel(
            relative_rect=pygame.Rect(16, 16, right_panel_rect.width - 32, 24),
            text="Stats Dashboard",
            manager=self.manager,
            container=self.right_panel,
            object_id="#stats_title",
        )
        self.stats_hint = UILabel(
            relative_rect=pygame.Rect(16, 44, right_panel_rect.width - 32, 20),
            text="Use mouse wheel to scroll",
            manager=self.manager,
            container=self.right_panel,
            object_id="#stats_hint",
        )

        self.stats_box = UITextBox(
            html_text="",
            relative_rect=pygame.Rect(16, 72, right_panel_rect.width - 32, right_panel_rect.height - 88),
            manager=self.manager,
            container=self.right_panel,
        )

        self.ui_elements = [
            self.popup_panel,
            self.left_panel,
            self.right_panel,
            self.title_label,
            self.resume_button,
            self.restart_button,
            self.options_button,
            self.menu_button,
            self.stats_title,
            self.stats_hint,
            self.stats_box,
        ]
        self._set_visible(False)

    def show(self) -> None:
        self.active = True
        self._set_visible(True)
        self._refresh_stats_text(force=True)

    def hide(self) -> None:
        self.active = False
        self._set_visible(False)

    def toggle(self) -> None:
        if self.active:
            self.hide()
        else:
            self.show()

    def _set_visible(self, visible: bool) -> None:
        for element in self.ui_elements:
            if visible:
                element.show()
            else:
                element.hide()

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.active:
            return

        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.resume_button:
                self.hide()

    def update(self, dt: float) -> None:
        if not self.active:
            return

        self._refresh_stats_text()
        self.manager.update(dt)

    def _format_number(self, value) -> str:
        if isinstance(value, float):
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    def _build_stats_rows(self) -> list[tuple[str, str]]:
        player = self.player
        rows = [
            ("Level", self._format_number(getattr(player, "level", 0))),
            ("XP", f"{self._format_number(getattr(player, 'xp', 0))}/{self._format_number(getattr(player, 'xp_to_lvl_up', 0))}"),
            ("Gold", self._format_number(getattr(player, "gold", 0))),
            ("Current HP", self._format_number(getattr(player, "current_health", 0))),
            ("Max HP", self._format_number(getattr(player, "max_health", 0))),
            ("Speed", self._format_number(getattr(player, "speed", 0))),
            ("Damage", self._format_number(getattr(player, "damage", 0))),
            ("Armor", self._format_number(getattr(player, "armor", 0))),
            ("Crit Chance", self._format_number(getattr(player, "crit_chance", 0))),
            ("Projectile Count", self._format_number(getattr(player, "projectile_count", 0))),
            ("Cooldown Reduction", self._format_number(getattr(player, "reduce_cooldown", 0))),
            ("Pickup Range", self._format_number(getattr(player, "pickup_range", 0))),
            ("Life Steal", self._format_number(getattr(player, "lifesteal", 0))),
            ("Luck", self._format_number(getattr(player, "luck", 0))),
            ("XP Gain", self._format_number(getattr(player, "xp_gain", 0))),
            ("Coin Gain", self._format_number(getattr(player, "coin_gain", 0))),
            ("Weapons Equipped", self._format_number(len(getattr(player, "weapon_levels", {})))),
        ]

        weapon_levels = getattr(player, "weapon_levels", {})
        for weapon_name, level in weapon_levels.items():
            rows.append((f"{weapon_name} Level", self._format_number(level)))

        return rows

    def _refresh_stats_text(self, force: bool = False) -> None:
        rows = self._build_stats_rows()
        lines = []
        for label, value in rows:
            safe_label = escape(label)
            safe_value = escape(value)
            lines.append(f"<b>{safe_label}</b>: {safe_value}")

        stats_html = "<br>".join(lines)
        if force or stats_html != self._last_stats_text:
            self.stats_box.set_text(stats_html)
            self._last_stats_text = stats_html

    def draw(self) -> None:
        if not self.active:
            return

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 175))
        self.window.blit(overlay, (0, 0))
        self.manager.draw_ui(self.window)