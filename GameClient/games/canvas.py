"""
Dynamic-layout virtual canvas (Pygame) – “Light Show” button sits
to the right of the grid.  Drag the mouse (left button) to paint
continuous strokes.
"""
from __future__ import annotations
from typing import List
import pygame, sys, random, time

# ───────────────────────── helpers ──────────────────────────
def color_to_hex(c: pygame.Color) -> str:
    return f"#{c.r:02x}{c.g:02x}{c.b:02x}"

def rand_color() -> pygame.Color:
    """Return a bright, evenly-distributed random hue."""
    c = pygame.Color(0)

    hue = random.randrange(360)          # 0 – 359 °
    sat = random.randrange(85, 101)      # keep it vivid (85-100 %)
    val = random.randrange(85, 101)      # keep it bright (85-100 %)
    c.hsva = (hue, sat, val, 100)        # last number = alpha %

    return c

# ───────────────────────── main game ────────────────────────
class CanvasGame:
    # ── spacing constants ───────────────────────────────────
    MARGIN = 40
    UI_PAD = 20
    BTN_SIZE = (200, 100)
    PICKER_W, PICKER_H = 600, 100

    def __init__(self, disp: pygame.Surface, disp_offset=(0, 0), GRID_W=10):
        self.disp, self.disp_offset = disp, disp_offset
        # grid parameters (width may be passed in)
        self.GRID_W, self.GRID_H = GRID_W, 11
        self.CELL_W, self.CELL_H = 20, 40
        if self.GRID_W >= 20:
            self.CELL_W = 10

        # ── derived geometry ────────────────────────────────
        self.gpx_w = self.GRID_W * self.CELL_W
        self.gpx_h = self.GRID_H * self.CELL_H
        self.origin = (self.MARGIN, self.MARGIN)

        # button to the right of the grid
        btn_x = self.origin[0] + self.gpx_w + self.UI_PAD
        btn_y = self.origin[1] + (self.gpx_h - self.BTN_SIZE[1]) // 2

        # colour picker centred under the grid
        picker_x = self.origin[0] + (self.gpx_w - self.PICKER_W) // 2 + 10 * self.UI_PAD
        picker_y = self.origin[1] + self.gpx_h + self.UI_PAD

        # overall window size
        self.scr_w = btn_x + self.BTN_SIZE[0] + self.MARGIN
        self.scr_h = picker_y + self.PICKER_H + self.MARGIN

        self.canvas = pygame.Surface((self.scr_w, self.scr_h))

        # ── widgets ─────────────────────────────────────────
        self.color_picker = ColorPicker(picker_x, picker_y, self.PICKER_W, self.PICKER_H)
        self.light_btn = Button(
            "Light Show", (btn_x, btn_y), self.BTN_SIZE,
            (200, 200, 200), (120, 120, 120),
            pygame.font.Font(None, 36), self.toggle_light_show
        )

        # ── game state ──────────────────────────────────────
        self.grid: list[list[pygame.Color]] = [
            [pygame.Color("black") for _ in range(self.GRID_W)]
            for _ in range(self.GRID_H)
        ]
        self.preset_display = False
        self.prev_tick = 0
        self.running = True

    # ──────────────── new helper ────────────────────────────
    def _paint_at(self, mx: int, my: int) -> None:
        """Colour the cell under a screen-space mouse coordinate."""
        gx = (mx - self.origin[0]) // self.CELL_W
        gy = (my - self.origin[1]) // self.CELL_H
        if 0 <= gx < self.GRID_W and 0 <= gy < self.GRID_H:
            self.grid[gy][gx] = self.color_picker.color

    # ───────────── event handling & painting ────────────────
    def handle_event(self, e: pygame.Event) -> None:
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            self.running = False
            return

        if self.light_btn.is_clicked(e):
            self.light_btn.callback()
        if self.color_picker.erase_btn.is_clicked(e):
            self.color_picker.erase_btn.callback()

        # single click
        if e.type == pygame.MOUSEBUTTONDOWN and not self.preset_display and e.button == 1:
            self._paint_at(*e.pos)

        # ── paint while dragging (left button held) ─────────
        if (e.type == pygame.MOUSEMOTION and not self.preset_display
                and e.buttons[0]):                         # left button pressed
            self._paint_at(*e.pos)

    # ──────────── grid drawing & game logic ─────────────────
    def draw_grid(self) -> None:
        ox, oy = self.origin
        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                rect = pygame.Rect(ox + x * self.CELL_W,
                                   oy + y * self.CELL_H,
                                   self.CELL_W, self.CELL_H)
                pygame.draw.rect(self.canvas, self.grid[y][x], rect)
                pygame.draw.rect(self.canvas, pygame.Color("white"), rect, 1)

    def toggle_light_show(self) -> None:
        if self.preset_display:
            self.grid = [[pygame.Color("black") for _ in range(self.GRID_W)]
                         for _ in range(self.GRID_H)]
            self.preset_display = False
        else:
            self.prev_tick = pygame.time.get_ticks()
            self.light_show()
            self.preset_display = True

    def light_show(self) -> None:
        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                self.grid[y][x] = rand_color()

    def run(self) -> None:
        clk = pygame.time.Clock()
        while self.running:
            for e in pygame.event.get():
                self.handle_event(e)

            if self.preset_display and pygame.time.get_ticks() - self.prev_tick >= 1000:
                self.prev_tick = pygame.time.get_ticks()
                self.light_show()

            self.color_picker.update()

            self.canvas.fill("white")
            self.draw_grid()
            self.color_picker.draw(self.canvas)
            self.light_btn.draw(self.canvas)

            self.disp.blit(self.canvas, self.disp_offset)
            pygame.display.flip()
            clk.tick(60)

    def get_board(self) -> List[List[str]]:
        return [[color_to_hex(c) for c in row] for row in self.grid]

# ───────────────────────── widgets (unchanged) ─────────────────────────
class ColorPicker:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h)); self.image.fill("white")
        rad, span = h // 2, w - h
        for i in range(span):
            c = pygame.Color(0); c.hsla = (int(360 * i / span), 100, 50, 100)
            pygame.draw.rect(self.image, c, (rad + i, h // 3, 1, h - 2 * h // 3))
        self.erase_mode, self.p = False, 0.0
        self.color = self._current()
        btn_size, btn_pos = (120, 40), (x + (w - 120) // 2, y + h + 6)
        self.erase_btn = Button("Erase", btn_pos, btn_size, (100, 100, 100),
                                (150, 150, 150), pygame.font.Font(None, 28),
                                self._toggle_erase)

    def _current(self) -> pygame.Color:
        c = pygame.Color(0)
        c.hsla = (0, 0, 0, 100) if self.erase_mode else (int(self.p * 360), 100, 50, 100)
        return c

    def _toggle_erase(self) -> None:
        self.erase_mode = not self.erase_mode; self.color = self._current()

    def update(self) -> None:
        if pygame.mouse.get_pressed(3)[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.p = ((pygame.mouse.get_pos()[0] - self.rect.left - self.rect.height // 2)
                      / (self.rect.width - self.rect.height))
            self.p = max(0.0, min(self.p, 1.0)); self.color = self._current()

    def draw(self, surf): surf.blit(self.image, self.rect); cx = self.rect.left + self.rect.height // 2 + self.p * (self.rect.width - self.rect.height); pygame.draw.circle(surf, self.color, (int(cx), self.rect.centery), self.rect.height // 2); self.erase_btn.draw(surf)

class Button:
    def __init__(self, text, pos, size, color, hover_color, font, callback):
        self.text, self.rect = text, pygame.Rect(pos, size)
        self.color, self.hover, self.font, self.callback = color, hover_color, font, callback

    def draw(self, surf):
        pygame.draw.rect(surf, self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color, self.rect)
        surf.blit(self.font.render(self.text, True, pygame.Color("white")), self.font.render(self.text, True, pygame.Color("white")).get_rect(center=self.rect.center))

    def is_clicked(self, e): return e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos)

# (bootstrap code omitted for brevity – keep using your existing launcher)
