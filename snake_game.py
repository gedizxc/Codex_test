import random
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple


CELL_SIZE = 24
GRID_WIDTH = 28
GRID_HEIGHT = 22
START_DELAY_MS = 130
MIN_DELAY_MS = 55
SPEED_STEP_MS = 3

BG_COLOR = "#101820"
GRID_COLOR = "#172632"
SNAKE_HEAD_COLOR = "#7bd389"
SNAKE_BODY_COLOR = "#42b883"
FOOD_COLOR = "#ff6b6b"
TEXT_COLOR = "#e8f1f2"
MUTED_TEXT_COLOR = "#9fb3bd"

Point = Tuple[int, int]


@dataclass
class GameState:
    snake: List[Point]
    direction: Point
    next_direction: Point
    food: Point
    score: int
    delay_ms: int
    running: bool
    paused: bool
    game_over: bool
    won: bool


class SnakeGame:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("贪吃蛇")
        self.root.resizable(False, False)

        canvas_width = GRID_WIDTH * CELL_SIZE
        canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.state = self._new_state()
        self.root.bind("<KeyPress>", self._on_key_press)
        self._draw()
        self._tick()

    def _new_state(self) -> GameState:
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        food = self._random_food(snake)
        return GameState(
            snake=snake,
            direction=(1, 0),
            next_direction=(1, 0),
            food=food,
            score=0,
            delay_ms=START_DELAY_MS,
            running=True,
            paused=False,
            game_over=False,
            won=False,
        )

    def _random_food(self, snake: List[Point]) -> Point:
        occupied = set(snake)
        open_cells = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        return random.choice(open_cells)

    def _on_key_press(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        directions = {
            "up": (0, -1),
            "w": (0, -1),
            "down": (0, 1),
            "s": (0, 1),
            "left": (-1, 0),
            "a": (-1, 0),
            "right": (1, 0),
            "d": (1, 0),
        }

        if key == "r":
            self.state = self._new_state()
            self._draw()
            return

        if key in ("p", "space"):
            if not self.state.game_over:
                self.state.paused = not self.state.paused
                self._draw()
            return

        if key not in directions or self.state.game_over:
            return

        new_direction = directions[key]
        current_x, current_y = self.state.direction
        next_x, next_y = new_direction

        if (current_x + next_x, current_y + next_y) != (0, 0):
            self.state.next_direction = new_direction

    def _tick(self) -> None:
        if self.state.running and not self.state.paused and not self.state.game_over:
            self._move_snake()
            self._draw()

        self.root.after(self.state.delay_ms, self._tick)

    def _move_snake(self) -> None:
        self.state.direction = self.state.next_direction
        head_x, head_y = self.state.snake[0]
        dx, dy = self.state.direction
        new_head = (head_x + dx, head_y + dy)
        will_grow = new_head == self.state.food

        if self._has_collision(new_head, will_grow):
            self.state.game_over = True
            return

        self.state.snake.insert(0, new_head)

        if will_grow:
            self.state.score += 1
            self.state.delay_ms = max(MIN_DELAY_MS, self.state.delay_ms - SPEED_STEP_MS)
            if len(self.state.snake) == GRID_WIDTH * GRID_HEIGHT:
                self.state.game_over = True
                self.state.won = True
                return
            self.state.food = self._random_food(self.state.snake)
        else:
            self.state.snake.pop()

    def _has_collision(self, point: Point, will_grow: bool) -> bool:
        x, y = point
        hit_wall = x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT
        body = self.state.snake if will_grow else self.state.snake[:-1]
        hit_self = point in body
        return hit_wall or hit_self

    def _draw(self) -> None:
        self.canvas.delete("all")
        self._draw_grid()
        self._draw_food()
        self._draw_snake()
        self._draw_hud()

        if self.state.paused:
            self._draw_center_message("已暂停", "按 P 或空格继续")
        elif self.state.game_over:
            title = "你赢了" if self.state.won else "游戏结束"
            self._draw_center_message(title, "按 R 重新开始")

    def _draw_grid(self) -> None:
        width = GRID_WIDTH * CELL_SIZE
        height = GRID_HEIGHT * CELL_SIZE

        for x in range(0, width, CELL_SIZE):
            self.canvas.create_line(x, 0, x, height, fill=GRID_COLOR)
        for y in range(0, height, CELL_SIZE):
            self.canvas.create_line(0, y, width, y, fill=GRID_COLOR)

    def _draw_snake(self) -> None:
        for index, point in enumerate(self.state.snake):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
            self._draw_cell(point, color, padding=2)

    def _draw_food(self) -> None:
        self._draw_cell(self.state.food, FOOD_COLOR, padding=4)

    def _draw_cell(self, point: Point, color: str, padding: int) -> None:
        x, y = point
        left = x * CELL_SIZE + padding
        top = y * CELL_SIZE + padding
        right = (x + 1) * CELL_SIZE - padding
        bottom = (y + 1) * CELL_SIZE - padding
        self.canvas.create_rectangle(left, top, right, bottom, fill=color, outline="")

    def _draw_hud(self) -> None:
        self.canvas.create_text(
            12,
            12,
            anchor="nw",
            fill=TEXT_COLOR,
            font=("Helvetica", 15, "bold"),
            text=f"分数: {self.state.score}",
        )
        self.canvas.create_text(
            GRID_WIDTH * CELL_SIZE - 12,
            12,
            anchor="ne",
            fill=MUTED_TEXT_COLOR,
            font=("Helvetica", 11),
            text="方向键/WASD 移动  P/空格 暂停  R 重开",
        )

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        width = GRID_WIDTH * CELL_SIZE
        height = GRID_HEIGHT * CELL_SIZE
        self.canvas.create_rectangle(
            width * 0.2,
            height * 0.36,
            width * 0.8,
            height * 0.64,
            fill="#0b1218",
            outline="#2d4656",
            width=2,
        )
        self.canvas.create_text(
            width // 2,
            height // 2 - 22,
            fill=TEXT_COLOR,
            font=("Helvetica", 28, "bold"),
            text=title,
        )
        self.canvas.create_text(
            width // 2,
            height // 2 + 24,
            fill=MUTED_TEXT_COLOR,
            font=("Helvetica", 14),
            text=subtitle,
        )

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    SnakeGame().run()
