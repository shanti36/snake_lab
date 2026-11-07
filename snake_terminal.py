import os
import random
import time
import msvcrt

COLS = 20
ROWS = 20
START_DELAY = 150
MIN_DELAY = 60
SPEEDUP = 4
HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_highscore.txt")

DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
}

WASD = {"w": "Up", "s": "Down", "a": "Left", "d": "Right",
        "ц": "Up", "ы": "Down", "ф": "Left", "в": "Right"}

ARROWS = {"H": "Up", "P": "Down", "K": "Left", "M": "Right"}

HEAD = "\033[102m  \033[0m"
BODY = "\033[42m  \033[0m"
FOOD = "\033[41m  \033[0m"
EMPTY = "  "


class SnakeGame:

    def __init__(self):
        self.high_score = self.load_high_score()
        self.quit = False
        self.new_game()

    def load_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except (OSError, ValueError):
            return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except OSError:
            pass

    def new_game(self):
        mid_x, mid_y = COLS // 2, ROWS // 2
        self.snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.delay = START_DELAY
        self.paused = False
        self.game_over = False
        self.food = self.spawn_food()
        self.draw()

    def spawn_food(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS)
                if (x, y) not in self.snake]
        return random.choice(free) if free else None

    def read_key(self):
        """Возвращает название нажатой клавиши или None."""
        if not msvcrt.kbhit():
            return None
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):      
            return ARROWS.get(msvcrt.getwch())
        if ch == " ":
            return "space"
        if ch == "\r":
            return "Return"
        if ch == "\x1b":
            return "Escape"
        return ch.lower()

    def on_key(self, key):
        if key in WASD:
            key = WASD[key]

        if key in DIRECTIONS:
            new_dx, new_dy = DIRECTIONS[key]
            old_dx, old_dy = DIRECTIONS[self.direction]
            if (new_dx, new_dy) != (-old_dx, -old_dy):
                self.next_direction = key
        elif key == "space" and not self.game_over:
            self.paused = not self.paused
            self.draw()
        elif key in ("r", "к", "Return"):
            self.new_game()
        elif key in ("q", "й", "Escape"):
            self.quit = True

    def tick(self):
        if not self.paused and not self.game_over:
            self.step()
            self.draw()

    def step(self):
        self.direction = self.next_direction
        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        out_of_field = not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS)
        if out_of_field or new_head in self.snake[:-1]:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.delay = max(MIN_DELAY, self.delay - SPEEDUP)
            self.food = self.spawn_food()
            if self.food is None:
                self.game_over = True
                self.high_score = max(self.high_score, self.score)
                self.save_high_score()
        else:
            self.snake.pop()

    def draw(self):
        lines = [f"Счёт: {self.score}     Рекорд: {self.high_score}",
                 "+" + "-" * (COLS * 2) + "+"]

        for y in range(ROWS):
            row = ""
            for x in range(COLS):
                if (x, y) == self.food:
                    row += FOOD
                elif (x, y) == self.snake[0]:
                    row += HEAD
                elif (x, y) in self.snake:
                    row += BODY
                else:
                    row += EMPTY
            lines.append("|" + row + "|")

        lines.append("+" + "-" * (COLS * 2) + "+")

        if self.game_over:
            win = self.food is None
            lines.append(("Победа!" if win else "Игра окончена") + "  R - заново")
        elif self.paused:
            lines.append("Пауза  Пробел - продолжить")
        else:
            lines.append("Стрелки/WASD - ход, Пробел - пауза, Q - выход")

        print("\033[H" + "\033[K\n".join(lines) + "\033[K", end="", flush=True)

    def run(self):
        while not self.quit:
            deadline = time.time() + self.delay / 1000
            while time.time() < deadline and not self.quit:
                key = self.read_key()
                if key:
                    self.on_key(key)
                time.sleep(0.01)
            self.tick()


if __name__ == "__main__":
    os.system("")                            
    print("\033[2J\033[?25l", end="")        
    try:
        SnakeGame().run()
    finally:
        print("\033[?25h\033[0m\n")         