"""
THE 77 - Mobile Version
A number-finding puzzle game with 2048-inspired theme
Built with Kivy for Android/iOS compatibility
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from kivy.core.text import LabelBase
from kivy.metrics import dp, sp
import random
import time
import math

# 2048 Theme Colors
COLORS = {
    'bg': '#faf8ef',
    'grid_bg': '#bbada0',
    'cell_empty': '#cdc1b4',
    'cell_closed': '#eee4da',
    'cell_closed_alt': '#ede0c8',
    'cell_hover': '#f2b179',
    'cell_correct': '#6ece7a',
    'cell_wrong': '#f67c5f',
    'cell_solved': '#edc22e',
    'text_dark': '#776e65',
    'text_light': '#f9f6f2',
    'button_new': '#8f7a66',
    'button_menu': '#bbada0',
    'overlay': '#faf8efee',
    'gold': '#edc22e',
    'progress_bg': '#bbada0',
    'progress_fill': '#f59563',
}

# Translations
TRANSLATIONS = {
    "TR": {
        "game_title": "THE 77",
        "select_game": "Oyun Seç",
        "select_difficulty": "Zorluk Seviyesi",
        "easy": "KOLAY",
        "medium": "ORTA",
        "hard": "ZOR",
        "back": "◀ Geri",
        "main_menu": "Ana Menü",
        "new_game": "Yeni Oyun",
        "pause": "⏸",
        "resume": "▶",
        "next": "Sıradaki:",
        "time": "Süre:",
        "best": "En İyi:",
        "congratulations": "TEBRİKLER!",
        "new_record": "🏆 YENİ REKOR!",
        "click_new": "Yeni oyun için butona dokun",
        "settings": "⚙ Ayarlar",
        "music": "Müzik",
        "on": "Açık",
        "off": "Kapalı",
        "language": "Dil",
        "paused": "DURAKLATILDI",
        "tap_resume": "Devam etmek için dokun",
    },
    "EN": {
        "game_title": "THE 77",
        "select_game": "Select Game",
        "select_difficulty": "Select Difficulty",
        "easy": "EASY",
        "medium": "MEDIUM",
        "hard": "HARD",
        "back": "◀ Back",
        "main_menu": "Main Menu",
        "new_game": "New Game",
        "pause": "⏸",
        "resume": "▶",
        "next": "Next:",
        "time": "Time:",
        "best": "Best:",
        "congratulations": "CONGRATULATIONS!",
        "new_record": "🏆 NEW RECORD!",
        "click_new": "Tap to play again",
        "settings": "⚙ Settings",
        "music": "Music",
        "on": "On",
        "off": "Off",
        "language": "Language",
        "paused": "PAUSED",
        "tap_resume": "Tap to resume",
    },
}

# Global settings
current_language = "TR"

def t(key):
    return TRANSLATIONS.get(current_language, TRANSLATIONS["EN"]).get(key, key)


class GameStore:
    """Handles saving/loading best scores"""
    def __init__(self):
        self.store = JsonStore('the77_scores.json')
    
    def get_best(self, total, difficulty):
        key = f"{total}_{difficulty}"
        if self.store.exists(key):
            return self.store.get(key)['time']
        return None
    
    def set_best(self, total, difficulty, time_val):
        key = f"{total}_{difficulty}"
        current = self.get_best(total, difficulty)
        if current is None or time_val < current:
            self.store.put(key, time=time_val)
            return True
        return False


game_store = GameStore()


class Cell(Button):
    """Individual cell in the game grid"""
    number = NumericProperty(0)
    is_open = BooleanProperty(False)
    is_solved = BooleanProperty(False)
    
    def __init__(self, number, row, col, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.row = row
        self.col = col
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.font_size = sp(24)
        self.bold = True
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        self.bind(is_open=self.update_canvas, is_solved=self.update_canvas)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Determine color
            if self.is_solved:
                Color(*get_color_from_hex(COLORS['cell_solved']))
            elif self.is_open:
                Color(*get_color_from_hex(COLORS['cell_correct'] if self.is_open else COLORS['cell_wrong']))
            else:
                Color(*get_color_from_hex(COLORS['cell_closed']))
            
            # Draw rounded rectangle
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        
        # Update text
        if self.is_open or self.is_solved:
            self.text = str(self.number)
            self.color = get_color_from_hex(COLORS['text_light'])
        else:
            self.text = ''
    
    def show_wrong(self):
        """Flash red for wrong answer"""
        self.is_open = True
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*get_color_from_hex(COLORS['cell_wrong']))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.text = str(self.number)
        self.color = get_color_from_hex(COLORS['text_light'])


class GameGrid(GridLayout):
    """The main game grid"""
    def __init__(self, rows, cols, total, **kwargs):
        super().__init__(**kwargs)
        self.game_rows = rows
        self.game_cols = cols
        self.total = total
        self.cols = cols
        self.rows = rows
        self.spacing = dp(6)
        self.padding = dp(8)
        self.cells = []
        
    def generate_cells(self):
        """Generate and shuffle cells"""
        self.clear_widgets()
        self.cells = []
        
        numbers = list(range(1, self.total + 1))
        random.shuffle(numbers)
        
        idx = 0
        for r in range(self.game_rows):
            row_cells = []
            for c in range(self.game_cols):
                cell = Cell(numbers[idx], r, c)
                self.add_widget(cell)
                row_cells.append(cell)
                idx += 1
            self.cells.append(row_cells)
    
    def get_cell(self, row, col):
        if 0 <= row < self.game_rows and 0 <= col < self.game_cols:
            return self.cells[row][col]
        return None
    
    def reset_all(self):
        """Reset all cells to closed state"""
        for row in self.cells:
            for cell in row:
                cell.is_open = False
                cell.is_solved = False
                cell.update_canvas()


class MenuScreen(Screen):
    """Main menu screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['bg']))
            self.bg_rect = Rectangle(pos=layout.pos, size=Window.size)
        layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Title
        title = Label(
            text="THE 77",
            font_size=sp(64),
            bold=True,
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.85}
        )
        layout.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text=t('select_game'),
            font_size=sp(24),
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.72}
        )
        layout.add_widget(subtitle)
        
        # Game buttons
        btn_33 = self.create_menu_button("33", 0.55, COLORS['cell_hover'])
        btn_33.bind(on_release=lambda x: self.select_game(33))
        layout.add_widget(btn_33)
        
        btn_55 = self.create_menu_button("55", 0.40, COLORS['progress_fill'])
        btn_55.bind(on_release=lambda x: self.select_game(55))
        layout.add_widget(btn_55)
        
        btn_77 = self.create_menu_button("77", 0.25, COLORS['cell_solved'])
        btn_77.bind(on_release=lambda x: self.select_game(77))
        layout.add_widget(btn_77)
        
        # Settings button
        settings_btn = Button(
            text=t('settings'),
            font_size=sp(18),
            size_hint=(0.4, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.10},
            background_color=get_color_from_hex(COLORS['button_menu']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        settings_btn.bind(on_release=lambda x: self.go_settings())
        layout.add_widget(settings_btn)
        
        self.add_widget(layout)
    
    def create_menu_button(self, text, y_pos, color):
        btn = Button(
            text=text,
            font_size=sp(32),
            bold=True,
            size_hint=(0.6, 0.10),
            pos_hint={'center_x': 0.5, 'center_y': y_pos},
            background_color=get_color_from_hex(color),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        return btn
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def select_game(self, total):
        app = App.get_running_app()
        app.selected_total = total
        app.sm.current = 'difficulty'
    
    def go_settings(self):
        App.get_running_app().sm.current = 'settings'


class DifficultyScreen(Screen):
    """Difficulty selection screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['bg']))
            self.bg_rect = Rectangle(pos=layout.pos, size=Window.size)
        layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Back button
        back_btn = Button(
            text=t('back'),
            font_size=sp(18),
            size_hint=(0.25, 0.06),
            pos_hint={'x': 0.02, 'top': 0.98},
            background_color=get_color_from_hex(COLORS['button_menu']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        layout.add_widget(back_btn)
        
        # Title (will show selected game number)
        self.title_label = Label(
            text="",
            font_size=sp(56),
            bold=True,
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.82}
        )
        layout.add_widget(self.title_label)
        
        # Subtitle
        subtitle = Label(
            text=t('select_difficulty'),
            font_size=sp(22),
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.70}
        )
        layout.add_widget(subtitle)
        
        # Difficulty buttons
        btn_easy = self.create_diff_button(t('easy'), 0.52, COLORS['cell_correct'])
        btn_easy.bind(on_release=lambda x: self.select_difficulty('easy'))
        layout.add_widget(btn_easy)
        
        btn_medium = self.create_diff_button(t('medium'), 0.38, COLORS['cell_hover'])
        btn_medium.bind(on_release=lambda x: self.select_difficulty('medium'))
        layout.add_widget(btn_medium)
        
        btn_hard = self.create_diff_button(t('hard'), 0.24, COLORS['cell_wrong'])
        btn_hard.bind(on_release=lambda x: self.select_difficulty('hard'))
        layout.add_widget(btn_hard)
        
        self.add_widget(layout)
    
    def create_diff_button(self, text, y_pos, color):
        btn = Button(
            text=text,
            font_size=sp(26),
            bold=True,
            size_hint=(0.65, 0.10),
            pos_hint={'center_x': 0.5, 'center_y': y_pos},
            background_color=get_color_from_hex(color),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        return btn
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_enter(self):
        app = App.get_running_app()
        self.title_label.text = str(app.selected_total)
    
    def go_back(self):
        App.get_running_app().sm.current = 'menu'
    
    def select_difficulty(self, diff):
        app = App.get_running_app()
        app.selected_difficulty = diff
        app.sm.current = 'game'


class SettingsScreen(Screen):
    """Settings screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['bg']))
            self.bg_rect = Rectangle(pos=layout.pos, size=Window.size)
        layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Title
        title = Label(
            text=t('settings'),
            font_size=sp(40),
            bold=True,
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.85}
        )
        layout.add_widget(title)
        
        # Language button
        self.lang_btn = Button(
            text=f"{t('language')}: {current_language}",
            font_size=sp(22),
            size_hint=(0.7, 0.10),
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            background_color=get_color_from_hex(COLORS['cell_hover']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        self.lang_btn.bind(on_release=lambda x: self.toggle_language())
        layout.add_widget(self.lang_btn)
        
        # Back button
        back_btn = Button(
            text=t('back'),
            font_size=sp(20),
            size_hint=(0.5, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.20},
            background_color=get_color_from_hex(COLORS['button_menu']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def toggle_language(self):
        global current_language
        langs = ["TR", "EN"]
        idx = langs.index(current_language)
        current_language = langs[(idx + 1) % len(langs)]
        self.lang_btn.text = f"{t('language')}: {current_language}"
    
    def go_back(self):
        App.get_running_app().sm.current = 'menu'


class GameScreen(Screen):
    """Main game screen"""
    next_target = NumericProperty(1)
    elapsed_time = NumericProperty(0)
    is_paused = BooleanProperty(False)
    won = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = None
        self.start_time = 0
        self.pause_time = 0
        self.total_pause = 0
        self.current_run = []
        self.checkpoint_size = 1
        self.final_time = 0
        self.is_new_record = False
        self.clock_event = None
    
    def on_enter(self):
        """Called when entering the game screen"""
        self.setup_game()
    
    def on_leave(self):
        """Called when leaving the game screen"""
        if self.clock_event:
            self.clock_event.cancel()
    
    def setup_game(self):
        app = App.get_running_app()
        total = app.selected_total
        difficulty = app.selected_difficulty
        
        # Configure grid based on total
        configs = {
            33: {'rows': 3, 'cols': 11},
            55: {'rows': 5, 'cols': 11},
            77: {'rows': 7, 'cols': 11},
        }
        cfg = configs[total]
        
        # Configure checkpoint for medium difficulty
        if difficulty == 'medium':
            self.checkpoint_size = cfg['rows']
        else:
            self.checkpoint_size = 1
        
        self.clear_widgets()
        self.build_game_ui(cfg['rows'], cfg['cols'], total)
        self.reset_game()
    
    def build_game_ui(self, rows, cols, total):
        """Build the game UI"""
        main_layout = FloatLayout()
        
        # Background
        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['bg']))
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Top bar
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'top': 1},
            padding=dp(8),
            spacing=dp(8)
        )
        
        # Back button
        back_btn = Button(
            text=t('back'),
            font_size=sp(16),
            size_hint=(0.2, 1),
            background_color=get_color_from_hex(COLORS['button_menu']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        top_bar.add_widget(back_btn)
        
        # Title
        title_label = Label(
            text=f"THE {total}",
            font_size=sp(22),
            bold=True,
            color=get_color_from_hex(COLORS['text_dark']),
            size_hint=(0.5, 1)
        )
        top_bar.add_widget(title_label)
        
        # New game button
        new_btn = Button(
            text=t('new_game'),
            font_size=sp(14),
            size_hint=(0.3, 1),
            background_color=get_color_from_hex(COLORS['button_new']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        new_btn.bind(on_release=lambda x: self.reset_game())
        top_bar.add_widget(new_btn)
        
        main_layout.add_widget(top_bar)
        
        # Info bar (next number, time, pause)
        info_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.07),
            pos_hint={'top': 0.92},
            padding=dp(12),
            spacing=dp(8)
        )
        
        # Next number
        self.next_label = Label(
            text=f"{t('next')} 1",
            font_size=sp(20),
            bold=True,
            color=get_color_from_hex(COLORS['cell_solved']),
            halign='left',
            size_hint=(0.35, 1)
        )
        info_bar.add_widget(self.next_label)
        
        # Time
        self.time_label = Label(
            text=f"{t('time')} 0s",
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text_dark']),
            size_hint=(0.35, 1)
        )
        info_bar.add_widget(self.time_label)
        
        # Pause button
        self.pause_btn = Button(
            text=t('pause'),
            font_size=sp(22),
            size_hint=(0.15, 1),
            background_color=get_color_from_hex(COLORS['progress_fill']),
            color=get_color_from_hex(COLORS['text_light']),
            background_normal='',
        )
        self.pause_btn.bind(on_release=lambda x: self.toggle_pause())
        info_bar.add_widget(self.pause_btn)
        
        main_layout.add_widget(info_bar)
        
        # Best score label
        self.best_label = Label(
            text="",
            font_size=sp(14),
            color=get_color_from_hex(COLORS['progress_fill']),
            pos_hint={'right': 0.98, 'top': 0.84},
            size_hint=(0.3, 0.04),
            halign='right'
        )
        main_layout.add_widget(self.best_label)
        
        # Grid container with background
        grid_container = FloatLayout(
            size_hint=(0.96, 0.62),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        
        with grid_container.canvas.before:
            Color(*get_color_from_hex(COLORS['grid_bg']))
            self.grid_bg = RoundedRectangle(pos=grid_container.pos, size=grid_container.size, radius=[dp(12)])
        grid_container.bind(size=self._update_grid_bg, pos=self._update_grid_bg)
        
        # Game grid
        self.grid = GameGrid(rows, cols, total, size_hint=(1, 1))
        
        # Bind cell touches
        grid_container.add_widget(self.grid)
        main_layout.add_widget(grid_container)
        
        # Progress bar background
        with main_layout.canvas:
            Color(*get_color_from_hex(COLORS['progress_bg']))
            self.progress_bg = RoundedRectangle(
                pos=(dp(20), dp(70)),
                size=(Window.width - dp(40), dp(16)),
                radius=[dp(8)]
            )
            Color(*get_color_from_hex(COLORS['progress_fill']))
            self.progress_fill = RoundedRectangle(
                pos=(dp(20), dp(70)),
                size=(0, dp(16)),
                radius=[dp(8)]
            )
        
        # Progress text
        self.progress_label = Label(
            text="0 / " + str(total),
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            size_hint=(1, 0.05)
        )
        main_layout.add_widget(self.progress_label)
        
        # Pause overlay
        self.pause_overlay = FloatLayout(size_hint=(1, 1))
        with self.pause_overlay.canvas:
            Color(0.98, 0.97, 0.94, 0.95)
            self.pause_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        pause_text = Label(
            text=t('paused'),
            font_size=sp(48),
            bold=True,
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        self.pause_overlay.add_widget(pause_text)
        
        tap_text = Label(
            text=t('tap_resume'),
            font_size=sp(20),
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.42}
        )
        self.pause_overlay.add_widget(tap_text)
        self.pause_overlay.bind(on_touch_down=lambda w, t: self.toggle_pause() if self.is_paused else None)
        self.pause_overlay.opacity = 0
        main_layout.add_widget(self.pause_overlay)
        
        # Win overlay
        self.win_overlay = FloatLayout(size_hint=(1, 1))
        with self.win_overlay.canvas:
            Color(0.98, 0.97, 0.94, 0.95)
            self.win_rect = Rectangle(pos=(0, 0), size=Window.size)
        
        self.win_text = Label(
            text=t('congratulations'),
            font_size=sp(36),
            bold=True,
            color=get_color_from_hex(COLORS['cell_correct']),
            pos_hint={'center_x': 0.5, 'center_y': 0.60}
        )
        self.win_overlay.add_widget(self.win_text)
        
        self.record_text = Label(
            text="",
            font_size=sp(24),
            color=get_color_from_hex(COLORS['cell_solved']),
            pos_hint={'center_x': 0.5, 'center_y': 0.50}
        )
        self.win_overlay.add_widget(self.record_text)
        
        self.final_time_text = Label(
            text="",
            font_size=sp(22),
            color=get_color_from_hex(COLORS['text_dark']),
            pos_hint={'center_x': 0.5, 'center_y': 0.40}
        )
        self.win_overlay.add_widget(self.final_time_text)
        
        self.win_overlay.opacity = 0
        main_layout.add_widget(self.win_overlay)
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
        
        # Generate cells
        self.grid.generate_cells()
        
        # Bind cell clicks
        for row in self.grid.cells:
            for cell in row:
                cell.bind(on_release=self.on_cell_click)
    
    def _update_bg(self, *args):
        self.bg_rect.size = Window.size
    
    def _update_grid_bg(self, widget, *args):
        self.grid_bg.pos = widget.pos
        self.grid_bg.size = widget.size
    
    def reset_game(self):
        """Reset the game state"""
        self.next_target = 1
        self.start_time = time.time()
        self.pause_time = 0
        self.total_pause = 0
        self.current_run = []
        self.won = False
        self.is_paused = False
        self.final_time = 0
        self.is_new_record = False
        
        self.grid.generate_cells()
        
        # Rebind cell clicks
        for row in self.grid.cells:
            for cell in row:
                cell.bind(on_release=self.on_cell_click)
        
        # Update UI
        self.update_ui()
        self.win_overlay.opacity = 0
        self.pause_overlay.opacity = 0
        
        # Update best score display
        app = App.get_running_app()
        best = game_store.get_best(app.selected_total, app.selected_difficulty)
        if best:
            self.best_label.text = f"{t('best')} {self.format_time(best)}"
        else:
            self.best_label.text = ""
        
        # Start clock
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self.update_time, 0.1)
    
    def update_time(self, dt):
        """Update the timer display"""
        if self.won or self.is_paused:
            return
        
        elapsed = time.time() - self.start_time - self.total_pause
        self.elapsed_time = elapsed
        self.time_label.text = f"{t('time')} {self.format_time(int(elapsed))}"
    
    def format_time(self, seconds):
        """Format seconds to display string"""
        if seconds < 60:
            return f"{seconds}s"
        else:
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}:{secs:02d}"
    
    def update_ui(self):
        """Update UI elements"""
        app = App.get_running_app()
        total = app.selected_total
        
        self.next_label.text = f"{t('next')} {self.next_target}"
        self.progress_label.text = f"{self.next_target - 1} / {total}"
        
        # Update progress bar
        progress = (self.next_target - 1) / total
        bar_width = Window.width - dp(40)
        self.progress_fill.size = (bar_width * progress, dp(16))
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.won:
            return
        
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_time = time.time()
            self.pause_overlay.opacity = 1
            self.pause_btn.text = t('resume')
        else:
            self.total_pause += time.time() - self.pause_time
            self.pause_overlay.opacity = 0
            self.pause_btn.text = t('pause')
    
    def on_cell_click(self, cell):
        """Handle cell click based on difficulty"""
        if self.won or self.is_paused:
            return
        
        if cell.is_solved:
            return
        
        app = App.get_running_app()
        difficulty = app.selected_difficulty
        
        if difficulty == 'easy':
            self.handle_easy_click(cell)
        elif difficulty == 'medium':
            self.handle_medium_click(cell)
        else:
            self.handle_hard_click(cell)
    
    def handle_easy_click(self, cell):
        """Easy mode: one number at a time"""
        # Close all open non-solved cells
        for row in self.grid.cells:
            for c in row:
                if c.is_open and not c.is_solved:
                    c.is_open = False
                    c.update_canvas()
        
        cell.is_open = True
        cell.update_canvas()
        
        if cell.number == self.next_target:
            cell.is_solved = True
            cell.update_canvas()
            self.next_target += 1
            self.update_ui()
            
            app = App.get_running_app()
            if self.next_target > app.selected_total:
                self.trigger_win()
        else:
            cell.show_wrong()
            Clock.schedule_once(lambda dt: self.close_cell(cell), 0.3)
    
    def handle_medium_click(self, cell):
        """Medium mode: checkpoint-based"""
        if (cell.row, cell.col) in self.current_run:
            return
        
        cell.is_open = True
        cell.update_canvas()
        
        if cell.number == self.next_target:
            self.current_run.append((cell.row, cell.col))
            self.next_target += 1
            self.update_ui()
            
            finished = self.next_target - 1
            block_done = (finished % self.checkpoint_size == 0) or (finished == App.get_running_app().selected_total)
            
            if block_done:
                for r, c in self.current_run:
                    self.grid.cells[r][c].is_solved = True
                    self.grid.cells[r][c].update_canvas()
                self.current_run = []
            
            app = App.get_running_app()
            if self.next_target > app.selected_total:
                self.trigger_win()
        else:
            cell.show_wrong()
            Clock.schedule_once(lambda dt: self.reset_checkpoint(cell), 0.3)
    
    def handle_hard_click(self, cell):
        """Hard mode: any mistake resets everything"""
        cell.is_open = True
        cell.update_canvas()
        
        if cell.number == self.next_target:
            cell.is_solved = True
            cell.update_canvas()
            self.next_target += 1
            self.update_ui()
            
            app = App.get_running_app()
            if self.next_target > app.selected_total:
                self.trigger_win()
        else:
            cell.show_wrong()
            Clock.schedule_once(lambda dt: self.reset_all(cell), 0.3)
    
    def close_cell(self, cell):
        """Close a single cell"""
        cell.is_open = False
        cell.update_canvas()
    
    def reset_checkpoint(self, clicked_cell):
        """Reset to last checkpoint (medium mode)"""
        for r, c in self.current_run:
            self.grid.cells[r][c].is_open = False
            self.grid.cells[r][c].update_canvas()
        self.current_run = []
        clicked_cell.is_open = False
        clicked_cell.update_canvas()
        
        last_checkpoint = ((self.next_target - 1) // self.checkpoint_size) * self.checkpoint_size
        self.next_target = last_checkpoint + 1
        self.update_ui()
    
    def reset_all(self, clicked_cell):
        """Reset all cells (hard mode)"""
        for row in self.grid.cells:
            for cell in row:
                cell.is_open = False
                cell.is_solved = False
                cell.update_canvas()
        clicked_cell.is_open = False
        clicked_cell.update_canvas()
        
        self.next_target = 1
        self.update_ui()
    
    def trigger_win(self):
        """Handle win condition"""
        self.won = True
        self.final_time = int(time.time() - self.start_time - self.total_pause)
        
        if self.clock_event:
            self.clock_event.cancel()
        
        # Check for new record
        app = App.get_running_app()
        self.is_new_record = game_store.set_best(
            app.selected_total,
            app.selected_difficulty,
            self.final_time
        )
        
        # Update win overlay
        self.win_text.text = t('congratulations')
        self.final_time_text.text = f"{t('time')} {self.format_time(self.final_time)}"
        
        if self.is_new_record:
            self.record_text.text = t('new_record')
        else:
            self.record_text.text = ""
        
        # Show win overlay with animation
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.win_overlay)
    
    def go_back(self):
        """Go back to difficulty selection"""
        if self.clock_event:
            self.clock_event.cancel()
        App.get_running_app().sm.current = 'difficulty'


class The77App(App):
    """Main application class"""
    selected_total = NumericProperty(33)
    selected_difficulty = StringProperty('easy')
    
    def build(self):
        # Set window background color
        Window.clearcolor = get_color_from_hex(COLORS['bg'])
        
        # Create screen manager
        self.sm = ScreenManager(transition=FadeTransition(duration=0.2))
        
        # Add screens
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(DifficultyScreen(name='difficulty'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(GameScreen(name='game'))
        
        return self.sm


if __name__ == '__main__':
    The77App().run()
