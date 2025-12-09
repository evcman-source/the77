"""
THE 77 - Mobile Responsive Game
Tested for all screen sizes
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp, sp
import random
import time as pytime

THEME = "light"
LANG = "TR"

COLORS = {
    "light": {"bg": "#FAF8EF", "bg2": "#EDE4D4", "grid": "#BBADA0", "cell": "#CDC1B4",
              "correct": "#6ECE7A", "wrong": "#F65E3B", "solved": "#EDC22E",
              "t1": "#776E65", "t2": "#A09588", "tw": "#FFFFFF", "b2": "#BBADA0",
              "bok": "#6ECE7A", "bwarn": "#F59563", "bdanger": "#F65E3B"},
    "dark": {"bg": "#1A1A2E", "bg2": "#16213E", "grid": "#2D2D44", "cell": "#4A4A6A",
             "correct": "#4ADE80", "wrong": "#F87171", "solved": "#FACC15",
             "t1": "#E2E8F0", "t2": "#94A3B8", "tw": "#FFFFFF", "b2": "#3D3D5C",
             "bok": "#4ADE80", "bwarn": "#FB923C", "bdanger": "#F87171"}
}

TEXTS = {
    "TR": {"select": "Oyun Sec", "diff": "Zorluk Sec", "easy": "KOLAY", "medium": "ORTA",
           "hard": "ZOR", "back": "<", "newgame": "Yeni", "next": "Sira:", "time": "Sure:",
           "congrats": "TEBRIKLER!", "record": "YENI REKOR!", "settings": "Ayarlar",
           "theme": "Tema", "dark": "Koyu", "light": "Acik", "lang": "Dil"},
    "EN": {"select": "Select Game", "diff": "Select Difficulty", "easy": "EASY",
           "medium": "MEDIUM", "hard": "HARD", "back": "<", "newgame": "New",
           "next": "Next:", "time": "Time:", "congrats": "CONGRATULATIONS!",
           "record": "NEW RECORD!", "settings": "Settings", "theme": "Theme",
           "dark": "Dark", "light": "Light", "lang": "Language"}
}

def C(k): return get_color_from_hex(COLORS[THEME][k])
def T(k): return TEXTS.get(LANG, TEXTS["EN"]).get(k, k)

class DataStore:
    def __init__(self):
        self.db = JsonStore('the77data.json')
    def get_best(self, t, d):
        k = f"{t}_{d}"
        return self.db.get(k)['v'] if self.db.exists(k) else None
    def set_best(self, t, d, v):
        k = f"{t}_{d}"
        old = self.get_best(t, d)
        if old is None or v < old:
            self.db.put(k, v=v)
            return True
        return False
    def load(self):
        global THEME, LANG
        if self.db.exists('cfg'):
            c = self.db.get('cfg')
            THEME = c.get('theme', 'light')
            LANG = c.get('lang', 'TR')
    def save(self):
        self.db.put('cfg', theme=THEME, lang=LANG)

DB = DataStore()

# ============== MENU ==============
class MenuScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = FloatLayout()
        with root.canvas.before:
            Color(*C('bg'))
            self.bg = Rectangle(size=Window.size)
        root.bind(size=lambda w, s: setattr(self.bg, 'size', s))
        
        root.add_widget(Label(text="THE 77", font_size=sp(48), bold=True, color=C('t1'),
                              pos_hint={'center_x': 0.5, 'center_y': 0.8}))
        root.add_widget(Label(text=T('select'), font_size=sp(18), color=C('t2'),
                              pos_hint={'center_x': 0.5, 'center_y': 0.7}))
        
        for n, c, y in [(33, 'bok', 0.55), (55, 'bwarn', 0.42), (77, 'bdanger', 0.29)]:
            b = Button(text=str(n), font_size=sp(26), bold=True, background_normal='',
                      background_color=C(c), color=C('tw'), size_hint=(0.4, 0.08),
                      pos_hint={'center_x': 0.5, 'center_y': y})
            b.bind(on_release=lambda x, num=n: self.go(num))
            root.add_widget(b)
        
        sb = Button(text=T('settings'), font_size=sp(16), background_normal='',
                   background_color=C('b2'), color=C('tw'), size_hint=(0.3, 0.06),
                   pos_hint={'center_x': 0.5, 'center_y': 0.12})
        sb.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'settings'))
        root.add_widget(sb)
        self.add_widget(root)
    
    def go(self, n):
        App.get_running_app().gtotal = n
        App.get_running_app().sm.current = 'diff'

# ============== DIFFICULTY ==============
class DiffScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = FloatLayout()
        with root.canvas.before:
            Color(*C('bg'))
            self.bg = Rectangle(size=Window.size)
        root.bind(size=lambda w, s: setattr(self.bg, 'size', s))
        
        bb = Button(text=T('back'), font_size=sp(16), bold=True, background_normal='',
                   background_color=C('b2'), color=C('tw'), size_hint=(0.15, 0.05),
                   pos_hint={'x': 0.02, 'top': 0.98})
        bb.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'menu'))
        root.add_widget(bb)
        
        root.add_widget(Label(text=str(App.get_running_app().gtotal), font_size=sp(50),
                              bold=True, color=C('t1'), pos_hint={'center_x': 0.5, 'center_y': 0.78}))
        root.add_widget(Label(text=T('diff'), font_size=sp(18), color=C('t2'),
                              pos_hint={'center_x': 0.5, 'center_y': 0.68}))
        
        for d, txt, c, y in [('easy', T('easy'), 'bok', 0.52),
                              ('medium', T('medium'), 'bwarn', 0.38),
                              ('hard', T('hard'), 'bdanger', 0.24)]:
            b = Button(text=txt, font_size=sp(22), bold=True, background_normal='',
                      background_color=C(c), color=C('tw'), size_hint=(0.45, 0.08),
                      pos_hint={'center_x': 0.5, 'center_y': y})
            b.bind(on_release=lambda x, df=d: self.go(df))
            root.add_widget(b)
        self.add_widget(root)
    
    def go(self, d):
        App.get_running_app().gdiff = d
        App.get_running_app().sm.current = 'game'

# ============== SETTINGS ==============
class SettingsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        root = FloatLayout()
        with root.canvas.before:
            Color(*C('bg'))
            self.bg = Rectangle(size=Window.size)
        root.bind(size=lambda w, s: setattr(self.bg, 'size', s))
        
        root.add_widget(Label(text=T('settings'), font_size=sp(36), bold=True,
                              color=C('t1'), pos_hint={'center_x': 0.5, 'center_y': 0.8}))
        
        ttxt = f"{T('theme')}: {T('dark') if THEME == 'light' else T('light')}"
        tb = Button(text=ttxt, font_size=sp(18), background_normal='',
                   background_color=C('b2'), color=C('tw'), size_hint=(0.5, 0.07),
                   pos_hint={'center_x': 0.5, 'center_y': 0.55})
        tb.bind(on_release=lambda x: self.toggle_theme())
        root.add_widget(tb)
        
        lb = Button(text=f"{T('lang')}: {LANG}", font_size=sp(18), background_normal='',
                   background_color=C('bwarn'), color=C('tw'), size_hint=(0.5, 0.07),
                   pos_hint={'center_x': 0.5, 'center_y': 0.42})
        lb.bind(on_release=lambda x: self.toggle_lang())
        root.add_widget(lb)
        
        bb = Button(text=T('back'), font_size=sp(16), background_normal='',
                   background_color=C('b2'), color=C('tw'), size_hint=(0.3, 0.06),
                   pos_hint={'center_x': 0.5, 'center_y': 0.2})
        bb.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'menu'))
        root.add_widget(bb)
        self.add_widget(root)
    
    def toggle_theme(self):
        global THEME
        THEME = 'dark' if THEME == 'light' else 'light'
        DB.save()
        self.on_enter()
    
    def toggle_lang(self):
        global LANG
        LANG = 'EN' if LANG == 'TR' else 'TR'
        DB.save()
        self.on_enter()

# ============== GAME ==============
class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.grid = None
        self.container = None
        self.cells = []
        self.next_num = 1
        self.start_t = 0
        self.pause_t = 0
        self.total_p = 0
        self.paused = False
        self.won = False
        self.timer = None
        self.run = []
        self.cp = 1
        self.total = 0
        self.current_rows = 0
        self.current_cols = 0
    
    def on_enter(self):
        app = App.get_running_app()
        self.total = app.gtotal
        self.cp = {33: 3, 55: 5, 77: 7}.get(self.total, 3) if app.gdiff == 'medium' else 1
        self.make_ui()
        Clock.schedule_once(lambda dt: self.new_game(), 0.1)
    
    def on_leave(self):
        if self.timer:
            self.timer.cancel()
    
    def make_ui(self):
        self.clear_widgets()
        
        root = BoxLayout(orientation='vertical')
        with root.canvas.before:
            Color(*C('bg'))
            self.bgr = Rectangle(size=Window.size)
        root.bind(size=lambda w, s: setattr(self.bgr, 'size', s))
        
        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(44), padding=dp(5), spacing=dp(5))
        with top.canvas.before:
            Color(*C('bg2'))
            self.topr = Rectangle()
        top.bind(size=lambda w, s: setattr(self.topr, 'size', s),
                pos=lambda w, p: setattr(self.topr, 'pos', p))
        
        bb = Button(text=T('back'), font_size=sp(14), bold=True, background_normal='',
                   background_color=C('b2'), color=C('tw'), size_hint_x=0.15)
        bb.bind(on_release=lambda x: self.go_back())
        top.add_widget(bb)
        
        top.add_widget(Label(text=f"THE {self.total}", font_size=sp(20), bold=True, color=C('t1')))
        
        nb = Button(text=T('newgame'), font_size=sp(13), background_normal='',
                   background_color=C('bok'), color=C('tw'), size_hint_x=0.18)
        nb.bind(on_release=lambda x: self.new_game())
        top.add_widget(nb)
        root.add_widget(top)
        
        # Info bar
        info = BoxLayout(size_hint_y=None, height=dp(36), padding=[dp(10), 0])
        self.next_lbl = Label(text=f"{T('next')} 1", font_size=sp(16), bold=True,
                              color=C('solved'), size_hint_x=0.35)
        info.add_widget(self.next_lbl)
        
        self.time_lbl = Label(text=f"{T('time')} 0s", font_size=sp(15), color=C('t1'))
        info.add_widget(self.time_lbl)
        
        self.pause_btn = Button(text="||", font_size=sp(16), bold=True, background_normal='',
                                background_color=C('bwarn'), color=C('tw'), size_hint_x=0.12)
        self.pause_btn.bind(on_release=lambda x: self.toggle_pause())
        info.add_widget(self.pause_btn)
        root.add_widget(info)
        
        # Grid container
        self.container = FloatLayout()
        with self.container.canvas.before:
            Color(*C('grid'))
            self.grid_bg = RoundedRectangle(pos=(0,0), size=(100,100), radius=[dp(8)])
        
        self.grid = GridLayout(cols=6, spacing=dp(2), padding=dp(6), size_hint=(None, None))
        self.container.add_widget(self.grid)
        self.container.bind(size=self._on_container_resize, pos=self._on_container_resize)
        root.add_widget(self.container)
        
        # Progress
        prog = BoxLayout(size_hint_y=None, height=dp(32), padding=[dp(15), dp(8)])
        prog_bg = Widget()
        with prog_bg.canvas:
            Color(*C('b2'))
            self.pbg = RoundedRectangle(radius=[dp(5)])
            Color(*C('bwarn'))
            self.pfill = RoundedRectangle(radius=[dp(5)])
        
        def upd_prog(w, s):
            self.pbg.size = (s[0], dp(12))
            self.pbg.pos = (w.pos[0], w.pos[1])
            self.pfill.pos = self.pbg.pos
            self._upd_progress()
        prog_bg.bind(size=upd_prog, pos=lambda w, p: upd_prog(w, w.size))
        prog.add_widget(prog_bg)
        root.add_widget(prog)
        
        self.prog_lbl = Label(text=f"0/{self.total}", font_size=sp(13), color=C('t2'),
                              size_hint_y=None, height=dp(24))
        root.add_widget(self.prog_lbl)
        
        self.add_widget(root)
    
    def _get_best_grid(self, cw, ch):
        """Get best rows/cols for screen size"""
        base = {33: (3, 11), 55: (5, 11), 77: (7, 11)}
        base_rows, base_cols = base[self.total]
        
        spacing = dp(2)
        padding = dp(6)
        margin = dp(8)
        
        def calc_cell_sizes(rows, cols):
            avail_w = cw - margin*2 - padding*2 - spacing*(cols-1)
            avail_h = ch - margin*2 - padding*2 - spacing*(rows-1)
            return avail_w / cols, avail_h / rows
        
        # Try both orientations
        w1, h1 = calc_cell_sizes(base_rows, base_cols)
        w2, h2 = calc_cell_sizes(base_cols, base_rows)
        
        # Pick orientation with better aspect ratio (closer to square)
        ratio1 = max(w1/h1, h1/w1) if min(w1, h1) > 0 else 999
        ratio2 = max(w2/h2, h2/w2) if min(w2, h2) > 0 else 999
        
        if ratio1 <= ratio2:
            return base_rows, base_cols, w1, h1
        else:
            return base_cols, base_rows, w2, h2
    
    def _on_container_resize(self, widget, value):
        """Resize and reposition grid when container changes"""
        if not self.container or self.container.width <= 1 or self.container.height <= 1:
            return
        if not self.cells:
            return
        
        cw = self.container.width
        ch = self.container.height
        
        rows, cols, cell_w, cell_h = self._get_best_grid(cw, ch)
        
        # Golden ratio limit (1.618)
        GOLDEN = 1.618
        ratio = max(cell_w/cell_h, cell_h/cell_w) if min(cell_w, cell_h) > 0 else 1
        
        if ratio > GOLDEN:
            # Limit to golden ratio
            if cell_w > cell_h:
                cell_w = cell_h * GOLDEN
            else:
                cell_h = cell_w * GOLDEN
        
        # Only rebuild if grid shape changed
        if rows != self.current_rows or cols != self.current_cols:
            self._rebuild_grid(rows, cols)
        
        spacing = dp(2)
        padding = dp(6)
        
        # Apply cell sizes to grid (can be rectangular now!)
        self.grid.cols = cols
        self.grid.row_force_default = True
        self.grid.col_force_default = True
        self.grid.row_default_height = cell_h
        self.grid.col_default_width = cell_w
        
        # Calculate grid size
        grid_w = cell_w * cols + spacing * (cols - 1) + padding * 2
        grid_h = cell_h * rows + spacing * (rows - 1) + padding * 2
        
        self.grid.size = (grid_w, grid_h)
        
        # Center in container
        self.grid.pos = (
            self.container.x + (cw - grid_w) / 2,
            self.container.y + (ch - grid_h) / 2
        )
        
        # Update background
        self.grid_bg.pos = self.grid.pos
        self.grid_bg.size = self.grid.size
        
        # Update font sizes (based on smaller dimension)
        font_size = min(cell_w, cell_h) * 0.45
        for btn in self.cells:
            btn.font_size = font_size
    
    def _rebuild_grid(self, new_rows, new_cols):
        """Rebuild grid when orientation changes"""
        if not self.cells:
            return
        
        self.current_rows = new_rows
        self.current_cols = new_cols
        
        # Save cell data
        cell_data = [(c.num, c.is_open, c.is_solved) for c in self.cells]
        
        # Clear and rebuild
        self.grid.clear_widgets()
        self.grid.cols = new_cols
        self.cells = []
        
        for i, (num, is_open, is_solved) in enumerate(cell_data):
            btn = Button(
                text=str(num) if (is_open or is_solved) else '',
                background_normal='',
                background_color=C('solved') if is_solved else (C('correct') if is_open else C('cell')),
                color=C('tw'),
                bold=True
            )
            btn.idx = i
            btn.num = num
            btn.is_open = is_open
            btn.is_solved = is_solved
            btn.bind(on_release=self._on_cell)
            self.grid.add_widget(btn)
            self.cells.append(btn)
    
    def new_game(self):
        self.next_num = 1
        self.start_t = pytime.time()
        self.pause_t = 0
        self.total_p = 0
        self.paused = False
        self.won = False
        self.run = []
        self.current_rows = 0
        self.current_cols = 0
        
        # Remove win overlay
        for child in self.children[:]:
            if isinstance(child, FloatLayout) and child != self.container:
                self.remove_widget(child)
        
        # Clear old cells
        self.grid.clear_widgets()
        self.cells = []
        
        # Generate shuffled numbers
        nums = list(range(1, self.total + 1))
        random.shuffle(nums)
        
        # Create cells
        for i in range(self.total):
            btn = Button(
                text='',
                background_normal='',
                background_color=C('cell'),
                color=C('tw'),
                bold=True
            )
            btn.idx = i
            btn.num = nums[i]
            btn.is_open = False
            btn.is_solved = False
            btn.bind(on_release=self._on_cell)
            self.grid.add_widget(btn)
            self.cells.append(btn)
        
        # Trigger layout
        Clock.schedule_once(lambda dt: self._on_container_resize(None, None), 0.05)
        
        self._upd_ui()
        
        if self.timer:
            self.timer.cancel()
        self.timer = Clock.schedule_interval(self._tick, 0.1)
    
    def _set_cell(self, btn, state):
        btn.is_open = state in ('open', 'solved', 'wrong')
        btn.is_solved = state == 'solved'
        
        if state == 'closed':
            btn.background_color = C('cell')
            btn.text = ''
        elif state == 'open':
            btn.background_color = C('correct')
            btn.text = str(btn.num)
        elif state == 'solved':
            btn.background_color = C('solved')
            btn.text = str(btn.num)
        elif state == 'wrong':
            btn.background_color = C('wrong')
            btn.text = str(btn.num)
    
    def _tick(self, dt):
        if self.won or self.paused:
            return
        e = pytime.time() - self.start_t - self.total_p
        self.time_lbl.text = f"{T('time')} {self._fmt(int(e))}"
    
    def _fmt(self, s):
        return f"{s}s" if s < 60 else f"{s//60}:{s%60:02d}"
    
    def _upd_ui(self):
        self.next_lbl.text = f"{T('next')} {self.next_num}"
        self.prog_lbl.text = f"{self.next_num - 1}/{self.total}"
        self._upd_progress()
    
    def _upd_progress(self):
        if hasattr(self, 'pbg') and self.pbg.size[0] > 0:
            p = (self.next_num - 1) / self.total
            self.pfill.size = (self.pbg.size[0] * p, dp(12))
    
    def toggle_pause(self):
        if self.won:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_t = pytime.time()
            self.pause_btn.text = ">"
        else:
            self.total_p += pytime.time() - self.pause_t
            self.pause_btn.text = "||"
    
    def _on_cell(self, btn):
        if self.won or self.paused or btn.is_solved:
            return
        
        diff = App.get_running_app().gdiff
        if diff == 'easy':
            self._do_easy(btn)
        elif diff == 'medium':
            self._do_medium(btn)
        else:
            self._do_hard(btn)
    
    def _do_easy(self, btn):
        for c in self.cells:
            if c.is_open and not c.is_solved:
                self._set_cell(c, 'closed')
        
        self._set_cell(btn, 'open')
        
        if btn.num == self.next_num:
            self._set_cell(btn, 'solved')
            self.next_num += 1
            self._upd_ui()
            if self.next_num > self.total:
                self._win()
        else:
            self._set_cell(btn, 'wrong')
            Clock.schedule_once(lambda dt: self._set_cell(btn, 'closed'), 0.35)
    
    def _do_medium(self, btn):
        if btn.idx in self.run:
            return
        
        self._set_cell(btn, 'open')
        
        if btn.num == self.next_num:
            self.run.append(btn.idx)
            self.next_num += 1
            self._upd_ui()
            
            done = self.next_num - 1
            if (done % self.cp == 0) or (done == self.total):
                for idx in self.run:
                    self._set_cell(self.cells[idx], 'solved')
                self.run = []
            
            if self.next_num > self.total:
                self._win()
        else:
            self._set_cell(btn, 'wrong')
            Clock.schedule_once(lambda dt: self._reset_cp(btn), 0.35)
    
    def _do_hard(self, btn):
        self._set_cell(btn, 'open')
        
        if btn.num == self.next_num:
            self._set_cell(btn, 'solved')
            self.next_num += 1
            self._upd_ui()
            if self.next_num > self.total:
                self._win()
        else:
            self._set_cell(btn, 'wrong')
            Clock.schedule_once(lambda dt: self._reset_all(btn), 0.35)
    
    def _reset_cp(self, clicked):
        for idx in self.run:
            self._set_cell(self.cells[idx], 'closed')
        self.run = []
        self._set_cell(clicked, 'closed')
        
        last = ((self.next_num - 1) // self.cp) * self.cp
        self.next_num = last + 1
        self._upd_ui()
    
    def _reset_all(self, clicked):
        for c in self.cells:
            self._set_cell(c, 'closed')
        self.next_num = 1
        self._upd_ui()
    
    def _win(self):
        self.won = True
        if self.timer:
            self.timer.cancel()
        
        final = int(pytime.time() - self.start_t - self.total_p)
        rec = DB.set_best(self.total, App.get_running_app().gdiff, final)
        
        ov = FloatLayout()
        with ov.canvas:
            Color(*C('bg')[:3], 0.93)
            Rectangle(size=Window.size)
        
        ov.add_widget(Label(text=T('congrats'), font_size=sp(32), bold=True,
                           color=C('correct'), pos_hint={'center_x': 0.5, 'center_y': 0.55}))
        if rec:
            ov.add_widget(Label(text=T('record'), font_size=sp(22),
                               color=C('solved'), pos_hint={'center_x': 0.5, 'center_y': 0.45}))
        ov.add_widget(Label(text=f"{T('time')} {self._fmt(final)}", font_size=sp(20),
                           color=C('t1'), pos_hint={'center_x': 0.5, 'center_y': 0.35}))
        self.add_widget(ov)
    
    def go_back(self):
        if self.timer:
            self.timer.cancel()
        App.get_running_app().sm.current = 'diff'

# ============== APP ==============
class The77App(App):
    gtotal = NumericProperty(33)
    gdiff = StringProperty('easy')
    
    def build(self):
        DB.load()
        Window.clearcolor = C('bg')
        
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(DiffScreen(name='diff'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(GameScreen(name='game'))
        return self.sm

if __name__ == '__main__':
    The77App().run()
