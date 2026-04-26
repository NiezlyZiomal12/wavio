import pygame
import pygame_gui
from html import escape
from pygame_gui.elements import UIButton, UILabel, UIPanel, UITextBox


class PauseMenuUi:
    def __init__(self, window, player: object):
        self.window = window
        self.player = player
        self.active = False
        self.current_size = self.window.get_size()
        self.manager = pygame_gui.UIManager(self.current_size, theme_path="src/assets/pygame_gui_styles/pause_theme.json")
        self._last_stats_text = ""
        layout = self._compute_layout()
        self.popup_rect = layout["popup"]
        self.click_sound = pygame.mixer.Sound("src/assets/sounds/gui/click.wav")
        self.open_sound = pygame.mixer.Sound("src/assets/sounds/gui/open.wav")

        self.popup_panel = UIPanel(
            relative_rect=self.popup_rect,
            manager=self.manager,
            object_id="#pause_popup",
        )

        self.left_panel = UIPanel(
            relative_rect=layout["left_panel"],
            manager=self.manager,
            container=self.popup_panel,
            object_id="#pause_left_panel",
        )

        self.right_panel = UIPanel(
            relative_rect=layout["right_panel"],
            manager=self.manager,
            container=self.popup_panel,
            object_id="#pause_right_panel",
        )

        self.title_label = UILabel(
            relative_rect=layout["title_label"],
            text="Paused",
            manager=self.manager,
            container=self.left_panel,
            object_id="#pause_title",
        )

        self.resume_button = UIButton(
            relative_rect=layout["resume_button"],
            text="Resume",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )
        self.restart_button = UIButton(
            relative_rect=layout["restart_button"],
            text="Restart",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )
        self.options_button = UIButton(
            relative_rect=layout["options_button"],
            text="Options",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )
        self.menu_button = UIButton(
            relative_rect=layout["menu_button"],
            text="Menu",
            manager=self.manager,
            container=self.left_panel,
            object_id="#button",
        )


        self.stats_box = UITextBox(
            html_text="",
            relative_rect=layout["stats_box"],
            manager=self.manager,
            container=self.right_panel,
            object_id="#textBox",
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
            self.stats_box,
        ]
        self._set_visible(False)

    def show(self) -> None:
        self.active = True
        self.open_sound.play()
        self._set_visible(True)
        self._refresh_stats_text(force=True)

    def hide(self) -> None:
        self.open_sound.play()
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
            self.click_sound.play()
            if event.ui_element == self.resume_button:
                self.hide()

    def update(self, dt: float) -> None:
        self._sync_to_window_size()

        if not self.active:
            return

        self._refresh_stats_text()
        self.manager.update(dt)

    def _format_number(self, value) -> str:
        if isinstance(value, float):
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    def _format_stat_value(self, label: str, value) -> str:
        if label in ("Armor", "Cooldown Reduction", "Life Steal"):
            try:
                return f"{float(value) * 100:.0f}%"
            except (TypeError, ValueError):
                return "0%"
        if label == "Crit Chance":
            try:
                crit_value = float(value)
                if 0 <= crit_value <= 1:
                    crit_value *= 100
                return f"{max(0.0, min(100.0, crit_value)):.0f}%"
            except (TypeError, ValueError):
                return "0%"
        return self._format_number(value)

    def _build_stats_rows(self) -> list[tuple[str, str]]:
        player = self.player
        rows = [
            ("Level", self._format_stat_value("Level", getattr(player, "level", 0))),
            ("Gold", self._format_stat_value("Gold", getattr(player, "gold", 0))),
            ("Max HP", self._format_stat_value("Max HP", getattr(player, "max_health", 0))),
            ("Speed", self._format_stat_value("Speed", getattr(player, "speed", 0))),
            ("Damage", self._format_stat_value("Damage", getattr(player, "damage", 0))),
            ("Armor", self._format_stat_value("Armor", getattr(player, "armor", 0))),
            ("Crit Chance", self._format_stat_value("Crit Chance", getattr(player, "crit_chance", 0))),
            ("Projectile Count", self._format_stat_value("Projectile Count", getattr(player, "projectile_count", 0))),
            ("Cooldown Reduction", self._format_stat_value("Cooldown Reduction", getattr(player, "reduce_cooldown", 0))),
            ("Pickup Range", self._format_stat_value("Pickup Range", getattr(player, "pickup_range", 0))),
            ("Life Steal", self._format_stat_value("Life Steal", getattr(player, "lifesteal", 0))),
            ("Luck", self._format_stat_value("Luck", getattr(player, "luck", 0))),
            ("XP Gain", self._format_stat_value("XP Gain", getattr(player, "xp_gain", 0))),
            ("Coin Gain", self._format_stat_value("Coin Gain", getattr(player, "coin_gain", 0))),
        ]


        return rows

    def _get_icon(self, label: str) -> str:
        default_icon = '<img src="src/assets/ui/icons/sword.png">'
        icon_map = {
            "Level": '<img src="src/assets/ui/icons/level.png">',
            "Gold": '<img src="src/assets/ui/icons/gold.png">',
            "Max HP":'<img src="src/assets/ui/icons/max_hp.png">',
            "Speed": '<img src="src/assets/ui/icons/speed.png">',
            "Damage": '<img src="src/assets/ui/icons/sword.png">',
            "Armor": '<img src="src/assets/ui/icons/shield.png">',
            "Crit Chance": '<img src="src/assets/ui/icons/crit_chance.png">',
            "Projectile Count": '<img src="src/assets/ui/icons/projectile_count.png">',
            "Cooldown Reduction": '<img src="src/assets/ui/icons/cdr.png">',
            "Pickup Range": '<img src="src/assets/ui/icons/pickup_range.png">',
            "Life Steal": '<img src="src/assets/ui/icons/lifesteal.png">',
            "Luck":'<img src="src/assets/ui/icons/luck.png">',
            "XP Gain": '<img src="src/assets/ui/icons/xp_gain.png">',
            "Coin Gain": '<img src="src/assets/ui/icons/coin_gain.png">',
        }


        return icon_map[label]
    

    def _refresh_stats_text(self, force: bool = False) -> None:
        rows = self._build_stats_rows()
        lines = []
        for label, value in rows:
            icon_html = self._get_icon(label)
            safe_label = escape(label)
            safe_value = escape(value)
            lines.append(f"{icon_html} <b>{safe_label}</b>: {safe_value}")

        stats_html = "<br>".join(lines)
        if force or stats_html != self._last_stats_text:
            self.stats_box.set_text(stats_html)
            self._last_stats_text = stats_html

    def draw(self) -> None:
        if not self.active:
            return

        overlay = pygame.Surface(self.current_size, pygame.SRCALPHA)
        overlay.fill((8, 12, 18, 175))
        self.window.blit(overlay, (0, 0))
        self.manager.draw_ui(self.window)


    def _sync_to_window_size(self) -> None:
        new_size = self.window.get_size()
        if new_size == self.current_size:
            return

        self.current_size = new_size
        self.width, self.height = new_size
        self.manager.set_window_resolution(self.current_size)
        self._apply_layout()


    def _compute_layout(self) -> dict[str, pygame.Rect]:
        width, height = self.current_size

        margin = max(18, int(min(width, height) * 0.04))
        popup_width = max(520, min(920, width - (2 * margin)))
        popup_height = max(340, min(620, height - (2 * margin)))
        popup_rect = pygame.Rect((width - popup_width) // 2, (height - popup_height) // 2, popup_width, popup_height)

        inner_pad = max(14, int(popup_width * 0.03))
        column_gap = max(12, int(popup_width * 0.025))

        left_width = max(220, int(popup_width * 0.4))
        max_left_width = popup_width - (2 * inner_pad) - column_gap - 180
        left_width = min(left_width, max_left_width)

        left_panel = pygame.Rect(inner_pad, inner_pad, left_width, popup_height - (2 * inner_pad))
        right_x = left_panel.right + column_gap
        right_panel = pygame.Rect(right_x, inner_pad, popup_width - right_x - inner_pad, popup_height - (2 * inner_pad))

        left_content_pad = max(14, int(left_panel.width * 0.07))
        title_height = max(36, int(left_panel.height * 0.14))
        title_y = max(14, int(left_panel.height * 0.06))
        title_label = pygame.Rect(left_content_pad, title_y, left_panel.width - (2 * left_content_pad), title_height)

        button_width = left_panel.width - (2 * left_content_pad)
        button_height = max(36, min(56, int(left_panel.height * 0.14)))
        buttons_start_y = title_label.bottom + max(14, int(left_panel.height * 0.06))
        gap = max(10, int(left_panel.height * 0.035))

        resume_button = pygame.Rect(left_content_pad, buttons_start_y, button_width, button_height)
        restart_button = pygame.Rect(left_content_pad, buttons_start_y + (button_height + gap), button_width, button_height)
        options_button = pygame.Rect(left_content_pad, buttons_start_y + 2 * (button_height + gap), button_width, button_height)
        menu_button = pygame.Rect(left_content_pad, buttons_start_y + 3 * (button_height + gap), button_width, button_height)

        right_pad = max(12, int(right_panel.width * 0.06))
        stats_box = pygame.Rect(
            right_pad,
            8,
            right_panel.width - (2 * right_pad),
            right_panel.height - 20,
        )

        return {
            "popup": popup_rect,
            "left_panel": left_panel,
            "right_panel": right_panel,
            "title_label": title_label,
            "resume_button": resume_button,
            "restart_button": restart_button,
            "options_button": options_button,
            "menu_button": menu_button,
            "stats_box": stats_box,
        }


    def _apply_layout(self) -> None:
        layout = self._compute_layout()
        self.popup_rect = layout["popup"]

        self.popup_panel.set_dimensions((self.popup_rect.width, self.popup_rect.height))
        self.popup_panel.set_relative_position((self.popup_rect.x, self.popup_rect.y))

        self.left_panel.set_dimensions((layout["left_panel"].width, layout["left_panel"].height))
        self.left_panel.set_relative_position((layout["left_panel"].x, layout["left_panel"].y))

        self.right_panel.set_dimensions((layout["right_panel"].width, layout["right_panel"].height))
        self.right_panel.set_relative_position((layout["right_panel"].x, layout["right_panel"].y))

        self.title_label.set_dimensions((layout["title_label"].width, layout["title_label"].height))
        self.title_label.set_relative_position((layout["title_label"].x, layout["title_label"].y))

        self.resume_button.set_dimensions((layout["resume_button"].width, layout["resume_button"].height))
        self.resume_button.set_relative_position((layout["resume_button"].x, layout["resume_button"].y))

        self.restart_button.set_dimensions((layout["restart_button"].width, layout["restart_button"].height))
        self.restart_button.set_relative_position((layout["restart_button"].x, layout["restart_button"].y))

        self.options_button.set_dimensions((layout["options_button"].width, layout["options_button"].height))
        self.options_button.set_relative_position((layout["options_button"].x, layout["options_button"].y))

        self.menu_button.set_dimensions((layout["menu_button"].width, layout["menu_button"].height))
        self.menu_button.set_relative_position((layout["menu_button"].x, layout["menu_button"].y))

        self.stats_box.set_dimensions((layout["stats_box"].width, layout["stats_box"].height))
        self.stats_box.set_relative_position((layout["stats_box"].x, layout["stats_box"].y))