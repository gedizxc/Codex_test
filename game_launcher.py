import subprocess
import sys
import tkinter as tk
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
BG_COLOR = "#111820"
PANEL_COLOR = "#182532"
BUTTON_COLOR = "#2c7be5"
BUTTON_ACTIVE_COLOR = "#3d8bfd"
TEXT_COLOR = "#eef5f7"
MUTED_TEXT_COLOR = "#9fb3bd"


class GameLauncher:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Python 游戏中心")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        panel = tk.Frame(self.root, bg=PANEL_COLOR, padx=34, pady=30)
        panel.pack(padx=24, pady=24)

        title = tk.Label(
            panel,
            text="Python 游戏中心",
            bg=PANEL_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 24, "bold"),
        )
        title.pack(pady=(0, 8))

        subtitle = tk.Label(
            panel,
            text="选择一个游戏开始",
            bg=PANEL_COLOR,
            fg=MUTED_TEXT_COLOR,
            font=("Helvetica", 13),
        )
        subtitle.pack(pady=(0, 24))

        self._add_button(panel, "贪吃蛇", lambda: self._launch("snake_game.py"))
        self._add_button(panel, "俄罗斯方块", lambda: self._launch("tetris_game.py"))
        self._add_button(panel, "退出", self.root.destroy, secondary=True)

    def _add_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        secondary: bool = False,
    ) -> None:
        bg = "#2b3b4b" if secondary else BUTTON_COLOR
        active_bg = "#34495e" if secondary else BUTTON_ACTIVE_COLOR
        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=18,
            bg=bg,
            activebackground=active_bg,
            fg=TEXT_COLOR,
            activeforeground=TEXT_COLOR,
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=10,
            font=("Helvetica", 15, "bold"),
        )
        button.pack(fill="x", pady=7)

    def _launch(self, script_name: str) -> None:
        script_path = BASE_DIR / script_name
        subprocess.Popen([sys.executable, str(script_path)], cwd=str(BASE_DIR))

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    GameLauncher().run()
