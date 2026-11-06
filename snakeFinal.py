import os                
import random         
import tkinter as tk     

CELL = 25            
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

WASD = {"w": "Up", "s": "Down", "a": "Left", "d": "Right"}


class SnakeGame:
    """Вся игра в одном классе. self - это сама игра, в self хранится её состояние."""

    def __init__(self, root):
        self.root = root
        root.title("Змейка")
        root.resizable(False, False)  

        self.label = tk.Label(root, font=("Arial", 14))
        self.label.pack()

        self.canvas = tk.Canvas(root, width=COLS * CELL, height=ROWS * CELL,
                                bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack()

        self.high_score = self.load_high_score()
        root.bind("<Key>", self.on_key)

        self.new_game()
        self.tick()

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

    def on_key(self, event):
        key = event.keysym
        if key.lower() in WASD:
            key = WASD[key.lower()]

        if key in DIRECTIONS:
            new_dx, new_dy = DIRECTIONS[key]
            old_dx, old_dy = DIRECTIONS[self.direction]
            if (new_dx, new_dy) != (-old_dx, -old_dy):
                self.next_direction = key
        elif key == "space" and not self.game_over:
            self.paused = not self.paused
            self.draw()
        elif key.lower() == "r" or key == "Return":
            self.new_game()

    def tick(self):
        if not self.paused and not self.game_over:
            self.step()
            self.draw()
        self.root.after(self.delay, self.tick)

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

    def draw_cell(self, cell, color):
        x, y = cell
        self.canvas.create_rectangle(x * CELL + 1, y * CELL + 1,
                                     (x + 1) * CELL - 1, (y + 1) * CELL - 1,
                                     fill=color, outline="")

    def draw(self):
        self.canvas.delete("all")
        self.label.config(text=f"Счёт: {self.score}     Рекорд: {self.high_score}")

        if self.food is not None:
            x, y = self.food
            self.canvas.create_oval(x * CELL + 3, y * CELL + 3,
                                    (x + 1) * CELL - 3, (y + 1) * CELL - 3,
                                    fill="#e74c3c", outline="")

        for i, cell in enumerate(self.snake):
            self.draw_cell(cell, "#2ecc71" if i == 0 else "#27ae60")

        text = None
        if self.game_over:
            win = self.food is None
            text = ("Победа!" if win else "Игра окончена") + "\nR - заново"
        elif self.paused:
            text = "Пауза\nПробел - продолжить"
        if text:
            self.canvas.create_text(COLS * CELL // 2, ROWS * CELL // 2, text=text,
                                    fill="white", font=("Arial", 22, "bold"),
                                    justify="center")


if __name__ == "__main__":
    window = tk.Tk()
    SnakeGame(window)
    window.mainloop()