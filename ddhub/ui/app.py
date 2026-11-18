"""Fullscreen, controller-first hub: browse -> details -> play -> back to the hub."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
# Let the hub see the quit combo while a game window has focus.
os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")

import pygame  # noqa: E402

from .. import actions  # noqa: E402
from ..backends import Context  # noqa: E402
from ..launcher import LaunchError, Session, build_plan  # noqa: E402
from ..library import KIND_LABELS, Game, Library  # noqa: E402
from ..readiness import READY, SETUP, UNSUPPORTED, UNTESTED, Readiness, evaluate  # noqa: E402
from ..saves import backup  # noqa: E402
from ..settings import Settings  # noqa: E402
from .input import InputMapper  # noqa: E402

W, H = 1280, 720
BG = (14, 16, 22)
PANEL = (28, 32, 42)
PANEL_HI = (44, 50, 66)
TEXT = (232, 235, 240)
DIM = (150, 156, 170)
ACCENT = (90, 170, 255)
STATUS_COLORS = {READY: (60, 190, 110), SETUP: (235, 170, 50), UNTESTED: (120, 150, 200), UNSUPPORTED: (210, 80, 80)}
KIND_SHORT = {"emulated": "EMULATED", "native": "NATIVE", "streaming": "STREAM"}
FEATURE_LABELS = {"save_states": "Save states", "rewind": "Rewind", "netplay": "Netplay",
                  "screenshots": "Screenshots", "local_multiplayer": "Local multiplayer"}

COLS, CARD_W, CARD_H, GAP = 5, 212, 268, 24
GRID_X, GRID_Y = (W - (COLS * CARD_W + (COLS - 1) * GAP)) // 2, 132
KEYBOARD = ["abcdefghij", "klmnopqrst", "uvwxyz0123", "456789 -.'"]


def hex_color(s: str, default=(70, 80, 100)):
    try:
        s = s.lstrip("#")
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, AttributeError):
        return default


@dataclass
class Tab:
    key: str
    label: str


class HubApp:
    def __init__(self, windowed: bool = False):
        self.settings = Settings()
        self.ctx = Context(self.settings)
        self.lib = Library()
        pygame.init()
        pygame.display.set_caption("DD Hub")
        self.windowed = windowed or not self.settings.get("fullscreen", True)
        self.window = self._make_window()
        self.canvas = pygame.Surface((W, H))
        self.font = {s: pygame.font.Font(None, s) for s in (20, 24, 28, 34, 44, 60)}
        self.input = InputMapper(self.settings["controls"])
        self.clock = pygame.time.Clock()
        self.covers: dict[tuple, pygame.Surface | None] = {}
        self.ready_cache: dict[tuple, Readiness] = {}
        self.screen = "library"
        self.tab_i = 0
        self.sel = 0
        self.scroll = 0
        self.query = ""
        self.kb = (0, 0)
        self.detail_i = 0
        self.dialog: dict | None = None
        self.menu_i = 0
        self.post_i = 0
        self.session: Session | None = None
        self.session_backend = ""
        self.session_msg = ""
        self.last_result = None
        self.combo_since = 0.0
        self.toasts: list[tuple[float, str]] = []
        self.running = True
        self.state_file = os.environ.get("DDHUB_STATE_FILE")
        self._last_state = None
        self.rebuild()

    # --- window --------------------------------------------------------------------------------
    def _make_window(self):
        if self.windowed:
            return pygame.display.set_mode((W, H), pygame.RESIZABLE)
        return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def present(self):
        ww, wh = self.window.get_size()
        if (ww, wh) == (W, H):
            self.window.blit(self.canvas, (0, 0))
        else:
            scale = min(ww / W, wh / H)
            sw, sh = int(W * scale), int(H * scale)
            self.window.fill((0, 0, 0))
            self.window.blit(pygame.transform.smoothscale(self.canvas, (sw, sh)), ((ww - sw) // 2, (wh - sh) // 2))
        pygame.display.flip()

    def bring_to_front(self):
        """Return keyboard focus to the hub after a game exits. Without this, a window manager (or
        none at all, under Xvfb) may leave focus on the closed game's window and the hub looks frozen."""
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                win = pygame.Window.from_display_module()
            win.restore()
            win.focus()
            win.focus(input_only=True)
        except (AttributeError, pygame.error):
            self.window = self._make_window()

    # --- data ----------------------------------------------------------------------------------
    def rebuild(self):
        plats = self.lib.platforms()
        self.tabs = [Tab("all", "All"), Tab("fav", "Favorites"), Tab("recent", "Recent")] + \
                    [Tab("p:" + p, self.ctx.catalog.platform_name(p)) for p in plats]
        self.tab_i = min(self.tab_i, len(self.tabs) - 1)
        self.ready_cache.clear()
        self.refilter()

    def refilter(self):
        key = self.tabs[self.tab_i].key
        if key == "fav":
            pool = self.lib.favorites()
        elif key == "recent":
            pool = self.lib.recent()
        else:
            pool = self.lib.sorted()
        plat = key[2:] if key.startswith("p:") else None
        self.items: list[Game] = self.lib.search(self.query, plat, pool)
        self.sel = max(0, min(self.sel, len(self.items) - 1))

    def readiness(self, g: Game) -> Readiness:
        k = (g.id, g.backend, json.dumps(g.local_test, sort_keys=True))
        if k not in self.ready_cache:
            self.ready_cache[k] = evaluate(g, self.ctx)
        return self.ready_cache[k]

    def current(self) -> Game | None:
        return self.items[self.sel] if self.items else None

    def toast(self, msg: str):
        self.toasts.append((time.monotonic() + 3.5, msg))

    def show_dialog(self, title: str, lines: list[str], color=ACCENT):
        self.dialog = {"title": title, "lines": lines, "color": color, "return": self.screen}
        self.screen = "dialog"

    # --- drawing helpers ------------------------------------------------------------------------
    def text(self, s, size, color, pos, anchor="topleft", max_w=None):
        f = self.font[size]
        if max_w:
            while s and f.size(s)[0] > max_w:
                s = s[:-4] + "..." if len(s) > 4 else ""
        surf = f.render(s, True, color)
        r = surf.get_rect(**{anchor: pos})
        self.canvas.blit(surf, r)
        return r

    def wrap(self, s, size, max_w):
        words, lines, cur = s.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.font[size].size(t)[0] <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def badge(self, status, pos, size=20):
        col = STATUS_COLORS.get(status, DIM)
        f = self.font[size]
        tw, th = f.size(status)
        r = pygame.Rect(pos[0], pos[1], tw + 16, th + 6)
        pygame.draw.rect(self.canvas, col, r, border_radius=8)
        self.canvas.blit(f.render(status, True, (12, 12, 16)), (r.x + 8, r.y + 4))
        return r

    def cover(self, g: Game, size):
        k = (g.cover, g.platform, g.title, size)
        if k in self.covers:
            return self.covers[k]
        surf = None
        if g.cover and Path(g.cover).is_file():
            try:
                img = pygame.image.load(g.cover).convert_alpha()
                iw, ih = img.get_size()
                scale = min(size[0] / iw, size[1] / ih)
                if scale > 2:  # pixel art / small icons: integer scaling keeps it crisp
                    scale = int(scale)
                    img = pygame.transform.scale(img, (iw * scale, ih * scale))
                else:
                    img = pygame.transform.smoothscale(img, (max(1, int(iw * scale)), max(1, int(ih * scale))))
                surf = pygame.Surface(size)
                surf.fill(hex_color(self.ctx.catalog.platforms.get(g.platform, {}).get("color", "")))
                surf.blit(img, img.get_rect(center=(size[0] // 2, size[1] // 2)))
            except (pygame.error, OSError):
                surf = None
        if surf is None:
            surf = pygame.Surface(size)
            base = hex_color(self.ctx.catalog.platforms.get(g.platform, {}).get("color", ""))
            surf.fill(base)
            pygame.draw.rect(surf, tuple(min(255, c + 40) for c in base), surf.get_rect(), 6)
            initials = "".join(w[0] for w in g.title.split()[:3]).upper()
            t = self.font[60].render(initials, True, (255, 255, 255))
            surf.blit(t, t.get_rect(center=(size[0] // 2, size[1] // 2 - 10)))
            p = self.font[20].render(self.ctx.catalog.platform_name(g.platform), True, (235, 235, 235))
            surf.blit(p, p.get_rect(center=(size[0] // 2, size[1] - 24)))
        self.covers[k] = surf
        return surf

    # --- screens -------------------------------------------------------------------------------
    def draw_header(self):
        self.text("DD HUB", 44, ACCENT, (GRID_X, 26))
        x = GRID_X + 170
        for i, t in enumerate(self.tabs):
            f = self.font[28]
            w = f.size(t.label)[0] + 24
            if x + w > W - 60:
                self.text("...", 28, DIM, (x, 34))
                break
            r = pygame.Rect(x, 28, w, 36)
            if i == self.tab_i:
                pygame.draw.rect(self.canvas, ACCENT, r, border_radius=18)
                self.text(t.label, 28, (10, 14, 20), r.center, "center")
            else:
                self.text(t.label, 28, DIM, r.center, "center")
            x += w + 6
        info = f"Search: \"{self.query}\"   " if self.query else ""
        self.text(info + time.strftime("%H:%M"), 24, DIM, (W - 40, 92), "topright")
        n = len(self.items)
        self.text(f"{n} game{'s' if n != 1 else ''}", 24, DIM, (GRID_X, 92))

    def draw_footer(self, hints):
        pygame.draw.rect(self.canvas, PANEL, (0, H - 44, W, 44))
        x = 40
        for btn, label in hints:
            r = self.text(btn, 24, ACCENT, (x, H - 32))
            r2 = self.text(label, 24, TEXT, (r.right + 8, H - 32))
            x = r2.right + 30

    def draw_library(self):
        self.draw_header()
        if not self.items:
            if not self.lib.games:
                lines = ["Your library is empty.", "",
                         "Add games from a terminal:",
                         "  ddhub install-bundled          (free sample games)",
                         "  ddhub import-folder <rom folder> [--platform gb]",
                         "  ddhub import-steam   |   ddhub import-desktop (Linux)",
                         "", "Then press Start > Reload library."]
            else:
                lines = ["Nothing matches this view.", "Press LB/RB to change tab, or Y to change the search."]
            for i, l in enumerate(lines):
                self.text(l, 28, TEXT if i == 0 else DIM, (GRID_X, 200 + i * 36))
        rows_visible = 2
        row = self.sel // COLS
        if row < self.scroll:
            self.scroll = row
        elif row >= self.scroll + rows_visible:
            self.scroll = row - rows_visible + 1
        for i, g in enumerate(self.items):
            r_, c_ = divmod(i, COLS)
            if not (self.scroll <= r_ < self.scroll + rows_visible):
                continue
            x = GRID_X + c_ * (CARD_W + GAP)
            y = GRID_Y + (r_ - self.scroll) * (CARD_H + GAP)
            selected = i == self.sel
            card = pygame.Rect(x, y, CARD_W, CARD_H)
            pygame.draw.rect(self.canvas, PANEL_HI if selected else PANEL, card, border_radius=12)
            self.canvas.blit(self.cover(g, (CARD_W - 16, 188)), (x + 8, y + 8))
            self.text(g.title, 24, TEXT, (x + 10, y + 204), max_w=CARD_W - 20)
            rd = self.readiness(g)
            col = STATUS_COLORS.get(rd.status, DIM)
            pygame.draw.circle(self.canvas, col, (x + 17, y + 245), 6)
            self.text(rd.status, 20, col, (x + 28, y + 238))
            self.text(KIND_SHORT.get(g.kind, ""), 20, DIM, (x + CARD_W - 10, y + 238), "topright")
            if g.favorite:
                draw_star(self.canvas, (x + CARD_W - 30, y + 30), 16)
            if selected:
                pygame.draw.rect(self.canvas, ACCENT, card, 4, border_radius=12)
        if len(self.items) > rows_visible * COLS:
            total_rows = (len(self.items) + COLS - 1) // COLS
            self.text(f"row {row + 1}/{total_rows}", 20, DIM, (W - 40, H - 70), "topright")
        self.draw_footer([("A", "Details"), ("X", "Favorite"), ("Y", "Search"), ("LB/RB", "Tabs"), ("Start", "Menu")])

    def detail_rows(self, g: Game) -> list[tuple[str, str]]:
        rows = [("play", "Play"), ("backend", "Launch method"), ("fav", "Remove favorite" if g.favorite else "Add to favorites"),
                ("backup", "Back up saves now"), ("works", "Mark: plays correctly here"),
                ("problems", "Mark: has problems here")]
        if g.local_test:
            rows.append(("clear", "Clear test result"))
        return rows

    def draw_details(self):
        g = self.current()
        if not g:
            self.screen = "library"
            return
        rd = self.readiness(g)
        self.canvas.fill(BG)
        self.canvas.blit(self.cover(g, (360, 360)), (60, 70))
        x = 460
        self.text(g.title, 44, TEXT, (x, 60), max_w=W - x - 40)
        self.text(f"{self.ctx.catalog.platform_name(g.platform)}  ·  {KIND_LABELS.get(g.kind, g.kind)}", 28, DIM, (x, 106))
        r = self.badge(rd.status, (x, 142), 28)
        self.text(f"Upstream: {rd.upstream}  (reported by emulator projects, not tested here)", 20, DIM, (r.right + 14, 150))
        t = g.local_test
        tested = (f"Tested here: {'plays correctly' if t['result'] == 'works' else 'had problems'} - {t.get('date')} - {t.get('backend_version')}"
                  if t else "Not tested on this machine yet.")
        self.text(tested, 24, TEXT if t else DIM, (x, 186), max_w=W - x - 40)
        y = 226
        rows = self.detail_rows(g)
        self.detail_i = min(self.detail_i, len(rows) - 1)
        for i, (key, label) in enumerate(rows):
            rr = pygame.Rect(x, y, 560, 38)
            if i == self.detail_i:
                pygame.draw.rect(self.canvas, PANEL_HI, rr, border_radius=8)
                pygame.draw.rect(self.canvas, ACCENT, rr, 2, border_radius=8)
            if key == "backend":
                b = self.ctx.catalog.backends.get(rd.backend, {})
                n_opts = len(actions.backend_choices(g, self.ctx))
                arrows = ("< ", " >") if n_opts > 1 else ("", "")
                self.text(f"{label}:  {arrows[0]}{b.get('name', 'none')}{arrows[1]}", 24, TEXT, (x + 12, y + 10), max_w=540)
            elif key == "play":
                self.text("Play" if rd.launchable else "Play (unavailable)", 28, TEXT if rd.launchable else DIM, (x + 12, y + 8))
            else:
                self.text(label, 24, TEXT, (x + 12, y + 10))
            y += 42
        y += 6
        feats = ctx_features(self.ctx, rd.backend)
        if feats:
            for line in self.wrap("Backend features: " + " · ".join(feats), 20, W - x - 40):
                self.text(line, 20, DIM, (x, y))
                y += 22
        for p in rd.problems[:3]:
            for line in self.wrap("! " + p.message, 24, W - x - 40)[:2]:
                self.text(line, 24, STATUS_COLORS[SETUP] if rd.status == SETUP else STATUS_COLORS[UNSUPPORTED], (x, y))
                y += 24
            for line in self.wrap("-> " + p.action, 20, W - x - 40)[:3]:
                self.text(line, 20, TEXT, (x + 16, y))
                y += 22
        for n in rd.notes[:2]:
            for line in self.wrap(n, 20, W - x - 40)[:2]:
                if y < H - 70:
                    self.text(line, 20, DIM, (x, y))
                    y += 22
        meta = g.meta
        info = [f"{k}: {meta[k]}" for k in ("developer", "year", "code_license", "asset_license") if meta.get(k)]
        yy = 446
        for line in info:
            self.text(line, 20, DIM, (60, yy), max_w=360)
            yy += 22
        if meta.get("description"):
            for line in self.wrap(meta["description"], 20, 360)[:5]:
                self.text(line, 20, DIM, (60, yy))
                yy += 22
        if g.playtime_s:
            self.text(f"Played {g.play_count}x · {fmt_time(g.playtime_s)} total", 20, DIM, (60, yy + 6))
        self.draw_footer([("A", "Select"), ("Left/Right", "Change launch method"), ("B", "Back")])

    def draw_search(self):
        self.draw_library()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.canvas.blit(overlay, (0, 0))
        panel = pygame.Rect(240, 250, 800, 360)
        pygame.draw.rect(self.canvas, PANEL, panel, border_radius=16)
        self.text("Search: " + self.query + "_", 34, TEXT, (panel.x + 30, panel.y + 24))
        for r, row in enumerate(KEYBOARD):
            for c, ch in enumerate(row):
                rect = pygame.Rect(panel.x + 30 + c * 74, panel.y + 80 + r * 56, 66, 48)
                sel = self.kb == (r, c)
                pygame.draw.rect(self.canvas, ACCENT if sel else PANEL_HI, rect, border_radius=8)
                self.text("SPC" if ch == " " else ch.upper(), 34, (10, 14, 20) if sel else TEXT, rect.center, "center")
        r = len(KEYBOARD)
        for c, label in enumerate(["Delete", "Clear", "Done"]):
            rect = pygame.Rect(panel.x + 30 + c * 246, panel.y + 80 + r * 56, 234, 48)
            sel = self.kb == (r, c)
            pygame.draw.rect(self.canvas, ACCENT if sel else PANEL_HI, rect, border_radius=8)
            self.text(label, 28, (10, 14, 20) if sel else TEXT, rect.center, "center")
        self.draw_footer([("A", "Type"), ("B", "Delete"), ("Y/Start", "Done"), ("Keyboard", "type directly")])

    def draw_playing(self):
        self.canvas.fill(BG)
        g = self.session.game if self.session else None
        if not g:
            return
        self.text("Now playing", 34, DIM, (W // 2, 220), "center")
        self.text(g.title, 60, TEXT, (W // 2, 280), "center", max_w=W - 120)
        el = time.time() - self.session.started
        self.text(fmt_time(el), 34, DIM, (W // 2, 340), "center")
        if self.session.plan.tracking == "manual":
            self.text("This is a streaming session - the hub cannot see when it ends.", 28, TEXT, (W // 2, 420), "center")
            self.text("Press A here when you have finished playing.", 28, ACCENT, (W // 2, 460), "center")
        else:
            combo = " + ".join(b.capitalize() for b in self.settings["quit_combo"])
            self.text("Use the game's own quit option to return here.", 28, TEXT, (W // 2, 420), "center")
            self.text(f"Stuck? Hold {combo} for {self.settings['quit_hold_seconds']:.0f} s to close the game.", 24, DIM, (W // 2, 460), "center")
            if self.combo_since:
                frac = min(1.0, (time.monotonic() - self.combo_since) / self.settings["quit_hold_seconds"])
                pygame.draw.rect(self.canvas, ACCENT, (W // 2 - 200, 500, int(400 * frac), 10), border_radius=5)

    def draw_post(self):
        self.canvas.fill(BG)
        g = self.lib.get(self.last_result[0]) if self.last_result else None
        if not g:
            self.screen = "library"
            return
        res = self.last_result[1]
        self.text(f"Back from {g.title}", 44, TEXT, (W // 2, 170), "center", max_w=W - 100)
        self.text(f"Session: {fmt_time(res.duration)}   ·   Total: {fmt_time(g.playtime_s)}", 28, DIM, (W // 2, 230), "center")
        if self.session_msg:
            self.text(self.session_msg, 24, DIM, (W // 2, 266), "center")
        self.text("Did it play correctly on this machine?", 34, TEXT, (W // 2, 340), "center")
        self.text("Your answer sets its readiness here. Launching is not the same as playable.", 20, DIM, (W // 2, 378), "center")
        opts = ["Yes - it plays correctly", "No - there were problems", "Skip"]
        for i, o in enumerate(opts):
            rr = pygame.Rect(W // 2 - 220, 420 + i * 56, 440, 46)
            pygame.draw.rect(self.canvas, ACCENT if i == self.post_i else PANEL_HI, rr, border_radius=10)
            self.text(o, 28, (10, 14, 20) if i == self.post_i else TEXT, rr.center, "center")
        self.draw_footer([("A", "Choose"), ("B", "Skip")])

    def menu_items(self):
        return [("reload", "Reload library"), ("rescan", "Rescan ROM folders"), ("steam", "Import Steam games"),
                ("desktop", "Import installed games (Linux)"), ("bundled", "Add bundled free games"),
                ("full", "Switch to windowed" if not self.windowed else "Switch to fullscreen"), ("quit", "Quit DD Hub")]

    def draw_menu(self):
        self.draw_library()
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.canvas.blit(overlay, (0, 0))
        items = self.menu_items()
        panel = pygame.Rect(W // 2 - 240, 140, 480, 70 + len(items) * 50)
        pygame.draw.rect(self.canvas, PANEL, panel, border_radius=16)
        self.text("Menu", 34, TEXT, (panel.x + 24, panel.y + 18))
        for i, (_, label) in enumerate(items):
            rr = pygame.Rect(panel.x + 20, panel.y + 60 + i * 50, panel.w - 40, 42)
            if i == self.menu_i:
                pygame.draw.rect(self.canvas, ACCENT, rr, border_radius=8)
            self.text(label, 28, (10, 14, 20) if i == self.menu_i else TEXT, (rr.x + 14, rr.y + 10))

    def draw_dialog(self):
        self.canvas.fill(BG)
        d = self.dialog
        panel = pygame.Rect(140, 150, W - 280, 420)
        pygame.draw.rect(self.canvas, PANEL, panel, border_radius=16)
        pygame.draw.rect(self.canvas, d["color"], (panel.x, panel.y, panel.w, 8), border_radius=4)
        self.text(d["title"], 44, TEXT, (panel.x + 30, panel.y + 30), max_w=panel.w - 60)
        y = panel.y + 90
        for line in d["lines"]:
            for wl in self.wrap(line, 24, panel.w - 60) or [""]:
                if y < panel.bottom - 70:
                    self.text(wl, 24, TEXT if not line.startswith("->") else ACCENT, (panel.x + 30, y))
                y += 28
        rr = pygame.Rect(panel.centerx - 80, panel.bottom - 64, 160, 44)
        pygame.draw.rect(self.canvas, ACCENT, rr, border_radius=10)
        self.text("OK", 28, (10, 14, 20), rr.center, "center")

    def draw_toasts(self):
        now = time.monotonic()
        self.toasts = [(t, m) for t, m in self.toasts if t > now]
        for i, (_, m) in enumerate(self.toasts[-3:]):
            f = self.font[24]
            w = f.size(m)[0] + 30
            r = pygame.Rect(W - w - 30, H - 100 - i * 44, w, 36)
            pygame.draw.rect(self.canvas, PANEL_HI, r, border_radius=10)
            self.text(m, 24, TEXT, (r.x + 15, r.y + 9))

    # --- actions -------------------------------------------------------------------------------
    def on_library(self, a):
        n = len(self.items)
        if a in ("left", "right", "up", "down") and n:
            step = {"left": -1, "right": 1, "up": -COLS, "down": COLS}[a]
            nxt = self.sel + step
            if a in ("left", "right") and nxt // COLS != self.sel // COLS:
                nxt = self.sel
            self.sel = max(0, min(n - 1, nxt)) if 0 <= nxt < n or a in ("down",) else self.sel
        elif a in ("prev_tab", "next_tab"):
            self.tab_i = (self.tab_i + (1 if a == "next_tab" else -1)) % len(self.tabs)
            self.sel = 0
            self.refilter()
        elif a == "accept" and n:
            self.screen, self.detail_i = "details", 0
        elif a == "favorite" and n:
            g = self.current()
            g.favorite = not g.favorite
            self.lib.save()
            self.toast(("Added to" if g.favorite else "Removed from") + " favorites")
            if self.tabs[self.tab_i].key == "fav":
                self.refilter()
        elif a == "search":
            self.screen, self.kb = "search", (0, 0)
        elif a == "menu":
            self.screen, self.menu_i = "menu", 0
        elif a == "back" and self.query:
            self.query = ""
            self.refilter()

    def on_details(self, a):
        g = self.current()
        rows = self.detail_rows(g)
        key = rows[self.detail_i][0]
        if a == "up":
            self.detail_i = max(0, self.detail_i - 1)
        elif a == "down":
            self.detail_i = min(len(rows) - 1, self.detail_i + 1)
        elif a == "back":
            self.screen = "library"
        elif a in ("left", "right") and key == "backend":
            opts = actions.backend_choices(g, self.ctx)
            if opts:
                cur = self.readiness(g).backend
                i = opts.index(cur) if cur in opts else 0
                g.backend = opts[(i + (1 if a == "right" else -1)) % len(opts)]
                self.lib.save()
        elif a == "accept":
            if key == "play":
                self.launch(g)
            elif key == "backend":
                self.on_details("right")
            elif key == "fav":
                g.favorite = not g.favorite
                self.lib.save()
            elif key == "backup":
                info = backup(g, self.ctx, label="manual")
                self.toast(f"Backed up {info.files} file(s)" if info else "No save files found yet for this game")
            elif key in ("works", "problems"):
                actions.record_test(g, self.ctx, self.readiness(g).backend, key)
                self.lib.save()
                self.toast("Test result recorded")
            elif key == "clear":
                g.local_test = {}
                self.lib.save()
                self.detail_i = 0

    def on_search(self, a, char=None):
        r, c = self.kb
        rows = len(KEYBOARD) + 1
        if char is not None:
            self.query += char
        elif a in ("up", "down"):
            r = (r + (1 if a == "down" else -1)) % rows
            c = min(c, (len(KEYBOARD[r]) - 1) if r < len(KEYBOARD) else 2)
        elif a in ("left", "right"):
            width = len(KEYBOARD[r]) if r < len(KEYBOARD) else 3
            c = (c + (1 if a == "right" else -1)) % width
        elif a == "accept":
            if r < len(KEYBOARD):
                self.query += KEYBOARD[r][c]
            elif c == 0:
                self.query = self.query[:-1]
            elif c == 1:
                self.query = ""
            else:
                self.screen = "library"
        elif a == "back":
            if self.query:
                self.query = self.query[:-1]
            else:
                self.screen = "library"
        elif a in ("search", "menu"):
            self.screen = "library"
        self.kb = (r, c)
        self.sel = 0
        self.refilter()

    def on_menu(self, a):
        items = self.menu_items()
        if a == "up":
            self.menu_i = (self.menu_i - 1) % len(items)
        elif a == "down":
            self.menu_i = (self.menu_i + 1) % len(items)
        elif a in ("back", "menu"):
            self.screen = "library"
        elif a == "accept":
            key = items[self.menu_i][0]
            self.screen = "library"
            if key == "quit":
                self.running = False
                return
            if key == "full":
                self.windowed = not self.windowed
                self.window = self._make_window()
                return
            try:
                if key == "reload":
                    self.lib = Library()
                    self.ctx.invalidate()
                    msg = "Library reloaded"
                elif key == "rescan":
                    s, _ = actions.rescan(self.lib, self.ctx)
                    msg = f"Rescan: {s['added']} new, {s['updated']} updated"
                elif key == "steam":
                    s, _ = actions.import_steam(self.lib)
                    msg = f"Steam: {s['added']} new, {s['updated']} updated" if any(s.values()) else "No Steam library found"
                elif key == "desktop":
                    s, _ = actions.import_desktop(self.lib)
                    msg = f"Installed games: {s['added']} new, {s['updated']} updated"
                else:
                    msg = "Added: " + (", ".join(actions.install_bundled(self.lib)) or "nothing")
            except OSError as e:
                msg = f"Import failed: {e}"
            self.rebuild()
            self.toast(msg)

    def on_post(self, a):
        if a == "up":
            self.post_i = (self.post_i - 1) % 3
        elif a == "down":
            self.post_i = (self.post_i + 1) % 3
        elif a == "back":
            self.screen = "details"
        elif a == "accept":
            g = self.lib.get(self.last_result[0])
            if self.post_i < 2 and g:
                actions.record_test(g, self.ctx, self.session_backend, "works" if self.post_i == 0 else "problems")
                self.lib.save()
                self.toast("Thanks - test result recorded")
            self.screen = "details"
            self.refilter()

    def launch(self, g: Game):
        try:
            plan, rd = build_plan(g, self.ctx)
            s = Session(g, plan, self.ctx)
            s.start()
        except LaunchError as e:
            g.last_error = e.message
            self.lib.save()
            self.show_dialog(f"Can't start {g.title}", [e.message, "", "-> " + e.action], STATUS_COLORS[SETUP])
            return
        self.session, self.session_backend = s, rd.backend
        if g.backend != rd.backend:  # pin the method actually used so saves keep loading from it
            g.backend = rd.backend
            self.lib.save()
        self.screen = "playing"
        self.combo_since = 0.0
        self.write_state(force=True)
        if plan.tracking != "manual":
            try:
                pygame.display.iconify()
            except pygame.error:
                pass

    def end_session(self, res):
        g = self.session.game
        self.session = None
        self.combo_since = 0.0
        self.bring_to_front()
        self.session_msg = actions.after_session(self.lib, self.ctx, g, res.started, res.ended, self.session_backend)
        self.ready_cache.clear()
        if res.error:
            self.last_result = (g.id, res)
            self.screen = "details"
            g.last_error = res.error
            self.lib.save()
            self.show_dialog(f"{g.title} stopped unexpectedly", res.error.splitlines() + ["", "-> " + res.action],
                             STATUS_COLORS[UNSUPPORTED])
            return
        self.last_result = (g.id, res)
        self.post_i = 0
        self.screen = "post"

    def tick_session(self):
        s = self.session
        held = self.input.held_buttons()
        combo = set(self.settings["quit_combo"])
        if combo and combo <= held:
            if not self.combo_since:
                self.combo_since = time.monotonic()
            elif time.monotonic() - self.combo_since >= self.settings["quit_hold_seconds"]:
                self.toast("Closing game...")
                s.stop()
        else:
            self.combo_since = 0.0
        res = s.poll()
        if res:
            self.end_session(res)

    # --- loop ----------------------------------------------------------------------------------
    def write_state(self, force=False):
        if not self.state_file:
            return
        g = self.current()
        state = {"screen": self.screen, "tab": self.tabs[self.tab_i].key, "selected": g.title if g else None,
                 "selected_status": self.readiness(g).status if g else None, "query": self.query,
                 "items": [x.title for x in self.items],
                 "playing": self.session.game.title if self.session else None,
                 "dialog": self.dialog["title"] if self.screen == "dialog" and self.dialog else None,
                 "detail_row": self.detail_rows(g)[min(self.detail_i, len(self.detail_rows(g)) - 1)][0] if g else None}
        if force or state != self._last_state:
            self._last_state = state
            tmp = self.state_file + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(state, fh)
            os.replace(tmp, self.state_file)

    def dispatch(self, a, char=None):
        if self.screen == "library":
            self.on_library(a)
        elif self.screen == "details":
            self.on_details(a)
        elif self.screen == "search":
            self.on_search(a, char)
        elif self.screen == "menu":
            self.on_menu(a)
        elif self.screen == "post":
            self.on_post(a)
        elif self.screen == "dialog" and a in ("accept", "back"):
            self.screen = self.dialog.get("return", "library") if self.dialog else "library"
            if self.screen in ("dialog", "playing"):
                self.screen = "details"
        elif self.screen == "playing" and a == "accept" and self.session and self.session.plan.tracking == "manual":
            self.end_session(self.session.finish())

    def run(self) -> int:
        pygame.key.stop_text_input()
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    if self.session:
                        self.toast("A game is still running - close it first")
                    else:
                        self.running = False
                    continue
                if self.screen == "search" and ev.type == pygame.KEYDOWN and ev.unicode and ev.unicode.isprintable() \
                        and ev.unicode not in "/" and ev.key not in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self.dispatch(None, ev.unicode.lower())
                    continue
                a = self.input.handle(ev)
                if a:
                    self.dispatch(a)
            a = self.input.repeat()
            if a and self.screen != "playing":
                self.dispatch(a)
            for m in self.input.messages:
                self.toast(m)
            self.input.messages.clear()
            if self.session:
                self.tick_session()
            self.canvas.fill(BG)
            {"library": self.draw_library, "details": self.draw_details, "search": self.draw_search,
             "playing": self.draw_playing, "post": self.draw_post, "menu": self.draw_menu,
             "dialog": self.draw_dialog}[self.screen]()
            self.draw_toasts()
            self.present()
            self.write_state()
            self.clock.tick(10 if self.session else 30)
        self.lib.save()
        pygame.quit()
        return 0


def draw_star(surf, center, r, color=(255, 210, 80)):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((center[0] + rad * math.cos(ang), center[1] + rad * math.sin(ang)))
    pygame.draw.polygon(surf, (20, 20, 20), [(px + 2, py + 2) for px, py in pts])
    pygame.draw.polygon(surf, color, pts)


def ctx_features(ctx: Context, backend_id: str) -> list[str]:
    feats = ctx.catalog.backends.get(backend_id, {}).get("features", {})
    out = [FEATURE_LABELS.get(k, k) for k, v in feats.items() if v is True and k in FEATURE_LABELS]
    if isinstance(feats.get("achievements"), str):
        out.append("Achievements: " + feats["achievements"])
    return out


def fmt_time(s: float) -> str:
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h {m:02d}m" if h else f"{m}m {sec:02d}s"


def run(windowed: bool = False) -> int:
    return HubApp(windowed).run()
