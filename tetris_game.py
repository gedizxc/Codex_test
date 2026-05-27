import random
import tkinter as tk
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
SIDE_PANEL_WIDTH = 180
WINDOW_WIDTH = BOARD_WIDTH * CELL_SIZE + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT * CELL_SIZE

BG_COLOR = "#101820"
BOARD_COLOR = "#0b1218"
GRID_COLOR = "#1f3140"
TEXT_COLOR = "#eef5f7"
MUTED_TEXT_COLOR = "#9fb3bd"
OVERLAY_COLOR = "#081016"

Point = Tuple[int, int]
Board = List[List[Optional[str]]]

TETROMINOES: Dict[str, List[List[Point]]] = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

COLORS = {
    "I": "#4cc9f0",
    "O": "#ffd166",
    "T": "#b5179e",
    "S": "#06d6a0",
    "Z": "#ef476f",
    "J": "#4361ee",
    "L": "#f77f00",
}

LINE_SCORE = {
    1: 100,
    2: 300,
    3: 500,
    4: 800,
}


@dataclass
class Piece:
    kind: str
    rotation: int
    x: int
    y: int


class TetrisGame:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("俄罗斯方块")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.closed = False
        self._new_game()
        self.root.bind("<KeyPress>", self._on_key_press)
        self._draw()
        self._tick()

    def _new_game(self) -> None:
        self.board: Board = [
            [None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
        ]
        self.bag: List[str] = []
        self.score = 0
        self.lines = 0
        self.level = 1
        self.paused = False
        self.game_over = False
        self.next_kind = self._take_from_bag()
        self.current = self._make_piece(self._take_from_bag())

    def _take_from_bag(self) -> str:
        if not self.bag:
            self.bag = list(TETROMINOES.keys())
            random.shuffle(self.bag)
        return self.bag.pop()

    def _make_piece(self, kind: str) -> Piece:
        return Piece(kind=kind, rotation=0, x=BOARD_WIDTH // 2 - 2, y=0)

    def _cells(self, piece: Piece) -> List[Point]:
        rotation = TETROMINOES[piece.kind][piece.rotation]
        return [(piece.x + x, piece.y + y) for x, y in rotation]

    def _is_valid(self, piece: Piece) -> bool:
        for x, y in self._cells(piece):
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return False
            if y >= 0 and self.board[y][x] is not None:
                return False
        return True

    def _on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()

        if key == "escape":
            self._close()
            return

        if key == "r":
            self._new_game()
            self._draw()
            return

        if key == "p":
            self._toggle_pause()
            return

        if self.paused or self.game_over:
            return

        if key in ("left", "a"):
            self._move_current(-1, 0)
        elif key in ("right", "d"):
            self._move_current(1, 0)
        elif key in ("down", "s"):
            self._soft_drop()
        elif key in ("up", "w", "x"):
            self._rotate_current(clockwise=True)
        elif key == "z":
            self._rotate_current(clockwise=False)
        elif key == "space":
            self._hard_drop()

        self._draw()

    def _toggle_pause(self) -> None:
        if not self.game_over:
            self.paused = not self.paused
            self._draw()

    def _tick(self) -> None:
        if self.closed:
            return

        if not self.paused and not self.game_over:
            if not self._move_current(0, 1):
                self._lock_current()
            self._draw()

        self.root.after(self._fall_delay_ms(), self._tick)

    def _fall_delay_ms(self) -> int:
        return max(90, 620 - (self.level - 1) * 45)

    def _move_current(self, dx: int, dy: int) -> bool:
        moved = replace(self.current, x=self.current.x + dx, y=self.current.y + dy)
        if self._is_valid(moved):
            self.current = moved
            return True
        return False

    def _soft_drop(self) -> None:
        if not self._move_current(0, 1):
            self._lock_current()

    def _hard_drop(self) -> None:
        while self._move_current(0, 1):
            pass
        self._lock_current()

    def _rotate_current(self, clockwise: bool) -> None:
        rotations = TETROMINOES[self.current.kind]
        step = 1 if clockwise else -1
        next_rotation = (self.current.rotation + step) % len(rotations)

        for dx, dy in ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)):
            rotated = replace(
                self.current,
                rotation=next_rotation,
                x=self.current.x + dx,
                y=self.current.y + dy,
            )
            if self._is_valid(rotated):
                self.current = rotated
                return

    def _lock_current(self) -> None:
        for x, y in self._cells(self.current):
            if y < 0:
                self.game_over = True
                return
            self.board[y][x] = self.current.kind

        self._clear_lines()
        self.current = self._make_piece(self.next_kind)
        self.next_kind = self._take_from_bag()

        if not self._is_valid(self.current):
            self.game_over = True

    def _clear_lines(self) -> None:
        remaining = [row for row in self.board if any(cell is None for cell in row)]
        cleared = BOARD_HEIGHT - len(remaining)
        if cleared == 0:
            return

        empty_rows = [
            [None for _ in range(BOARD_WIDTH)] for _ in range(cleared)
        ]
        self.board = empty_rows + remaining
        self.score += LINE_SCORE[cleared] * self.level
        self.lines += cleared
        self.level = self.lines // 10 + 1

    def _draw(self) -> None:
        self.canvas.delete("all")
        self._draw_board_background()
        self._draw_locked_blocks()
        self._draw_current_piece()
        self._draw_grid()
        self._draw_sidebar()

        if self.paused:
            self._draw_center_message("已暂停", "按 P 继续")
        elif self.game_over:
            self._draw_center_message("游戏结束", "按 R 重新开始")

    def _draw_board_background(self) -> None:
        self.canvas.create_rectangle(
            0,
            0,
            BOARD_WIDTH * CELL_SIZE,
            BOARD_HEIGHT * CELL_SIZE,
            fill=BOARD_COLOR,
            outline="",
        )

    def _draw_locked_blocks(self) -> None:
        for y, row in enumerate(self.board):
            for x, kind in enumerate(row):
                if kind is not None:
                    self._draw_cell(x, y, COLORS[kind])

    def _draw_current_piece(self) -> None:
        for x, y in self._cells(self.current):
            if y >= 0:
                self._draw_cell(x, y, COLORS[self.current.kind])

    def _draw_grid(self) -> None:
        board_width = BOARD_WIDTH * CELL_SIZE
        board_height = BOARD_HEIGHT * CELL_SIZE

        for x in range(0, board_width + 1, CELL_SIZE):
            self.canvas.create_line(x, 0, x, board_height, fill=GRID_COLOR)
        for y in range(0, board_height + 1, CELL_SIZE):
            self.canvas.create_line(0, y, board_width, y, fill=GRID_COLOR)

    def _draw_sidebar(self) -> None:
        left = BOARD_WIDTH * CELL_SIZE
        self.canvas.create_rectangle(left, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=BG_COLOR, outline="")
        self.canvas.create_text(
            left + 20,
            28,
            anchor="nw",
            fill=TEXT_COLOR,
            font=("Helvetica", 22, "bold"),
            text="俄罗斯方块",
        )

        stats = [
            ("分数", self.score),
            ("消行", self.lines),
            ("等级", self.level),
        ]
        y = 88
        for label, value in stats:
            self.canvas.create_text(
                left + 22,
                y,
                anchor="nw",
                fill=MUTED_TEXT_COLOR,
                font=("Helvetica", 12),
                text=label,
            )
            self.canvas.create_text(
                left + 22,
                y + 22,
                anchor="nw",
                fill=TEXT_COLOR,
                font=("Helvetica", 20, "bold"),
                text=str(value),
            )
            y += 62

        self.canvas.create_text(
            left + 22,
            292,
            anchor="nw",
            fill=MUTED_TEXT_COLOR,
            font=("Helvetica", 13),
            text="下一个",
        )
        self._draw_next_preview(left + 38, 326)

        controls = [
            "←/→ 或 A/D 移动",
            "↑/W/X 旋转",
            "Z 反向旋转",
            "↓/S 软降",
            "空格 硬降",
            "P 暂停  R 重开",
            "Esc 关闭",
        ]
        for index, text in enumerate(controls):
            self.canvas.create_text(
                left + 22,
                450 + index * 20,
                anchor="nw",
                fill=MUTED_TEXT_COLOR,
                font=("Helvetica", 11),
                text=text,
            )

    def _draw_next_preview(self, origin_x: int, origin_y: int) -> None:
        cells = TETROMINOES[self.next_kind][0]
        min_x = min(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        preview_size = 22

        for x, y in cells:
            left = origin_x + (x - min_x) * preview_size
            top = origin_y + (y - min_y) * preview_size
            self.canvas.create_rectangle(
                left + 2,
                top + 2,
                left + preview_size - 2,
                top + preview_size - 2,
                fill=COLORS[self.next_kind],
                outline="",
            )

    def _draw_cell(self, x: int, y: int, color: str) -> None:
        left = x * CELL_SIZE
        top = y * CELL_SIZE
        self.canvas.create_rectangle(
            left + 2,
            top + 2,
            left + CELL_SIZE - 2,
            top + CELL_SIZE - 2,
            fill=color,
            outline="",
        )

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        board_width = BOARD_WIDTH * CELL_SIZE
        center_x = board_width // 2
        center_y = WINDOW_HEIGHT // 2
        self.canvas.create_rectangle(
            36,
            center_y - 74,
            board_width - 36,
            center_y + 74,
            fill=OVERLAY_COLOR,
            outline="#2d4656",
            width=2,
        )
        self.canvas.create_text(
            center_x,
            center_y - 24,
            fill=TEXT_COLOR,
            font=("Helvetica", 27, "bold"),
            text=title,
        )
        self.canvas.create_text(
            center_x,
            center_y + 26,
            fill=MUTED_TEXT_COLOR,
            font=("Helvetica", 14),
            text=subtitle,
        )

    def _close(self) -> None:
        self.closed = True
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    TetrisGame().run()
