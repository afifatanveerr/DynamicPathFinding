import tkinter as tk
import random
import heapq
import time
import math


CELL_SIZE = 30
SPAWN_PROBABILITY = 0.03

COLORS = {
    "empty": "#FDF6EC",
    "wall": "#4A4A4A",
    "start": "#4ECDC4",
    "goal": "#C77DFF",
    "frontier": "#FFE66D",
    "visited": "#FF6B6B",
    "path": "#95D5B2"
}

#heurics
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

#map
class PathfindingApp:
    def __init__(self, root):
        self.root = root

        #taking inputs
        self.rows = int(input("Enter rows: "))
        self.cols = int(input("Enter cols: "))
        self.density = float(input("Obstacle density (0-0.4): "))
        dynamic_input = input("Enable Dynamic Mode? (y/n): ")
        self.dynamic_mode = True if dynamic_input.lower() == "y" else False

        self.canvas = tk.Canvas(root,
                                width=self.cols*CELL_SIZE,
                                height=self.rows*CELL_SIZE,
                                bg="white")
        self.canvas.pack()

        self.info = tk.Label(root, text="", font=("Arial", 12))
        self.info.pack()

        self.grid = []
        self.start = (0, 0)
        self.goal = (self.rows-1, self.cols-1)

        self.algorithm = tk.StringVar(value="A*")
        self.heuristic = tk.StringVar(value="Manhattan")

        self.controls()
        self.create_grid()
        self.canvas.bind("<Button-1>", self.toggle_wall)

    #ui
    def controls(self):
        frame = tk.Frame(self.root)
        frame.pack()

        tk.OptionMenu(frame, self.algorithm, "A*", "GBFS").pack(side="left")
        tk.OptionMenu(frame, self.heuristic,
                      "Manhattan", "Euclidean").pack(side="left")

        tk.Button(frame, text="Start Search",
                  command=self.start_search).pack(side="left")

    #grid
    def create_grid(self):
        self.grid = [["empty" for _ in range(self.cols)]
                     for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < self.density and (r, c) not in (self.start, self.goal):
                    self.grid[r][c] = "wall"

        self.grid[self.start[0]][self.start[1]] = "start"
        self.grid[self.goal[0]][self.goal[1]] = "goal"

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                color = COLORS[self.grid[r][c]]
                self.canvas.create_rectangle(
                    c*CELL_SIZE, r*CELL_SIZE,
                    (c+1)*CELL_SIZE, (r+1)*CELL_SIZE,
                    fill=color, outline="#E0E0E0"
                )

    def toggle_wall(self, event):
        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if (r, c) not in (self.start, self.goal):
            self.grid[r][c] = "wall" if self.grid[r][c] == "empty" else "empty"
            self.draw()

    #search
    def start_search(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] not in ("start", "goal", "wall"):
                    self.grid[r][c] = "empty"

        heuristic_func = manhattan if self.heuristic.get() == "Manhattan" else euclidean

        start_time = time.time()
        visited, cost = self.search(heuristic_func)
        end_time = time.time()

        self.info.config(
            text=f"Visited: {visited} | Cost: {cost} | Time: {round((end_time-start_time)*1000,2)} ms"
        )

    def search(self, heuristic_func):
        open_list = []
        heapq.heappush(open_list, (0, self.start))
        g_cost = {self.start: 0}
        parent = {}
        visited_count = 0

        while open_list:
            _, current = heapq.heappop(open_list)

            if current == self.goal:
                self.reconstruct(parent)
                return visited_count, g_cost[current]

            if current not in (self.start, self.goal):
                self.grid[current[0]][current[1]] = "visited"

            visited_count += 1
            self.draw()
            self.root.update()
            time.sleep(0.02)

            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = current[0]+dr, current[1]+dc
                neighbor = (nr, nc)

                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc] != "wall":

                        new_g = g_cost[current] + 1

                        if neighbor not in g_cost or new_g < g_cost[neighbor]:
                            g_cost[neighbor] = new_g
                            parent[neighbor] = current
                            h = heuristic_func(neighbor, self.goal)

                            if self.algorithm.get() == "GBFS":
                                priority = h
                            else:
                                priority = new_g + h

                            heapq.heappush(open_list, (priority, neighbor))

                            if self.grid[nr][nc] not in ("goal"):
                                self.grid[nr][nc] = "frontier"

            #dynamic
            if self.dynamic_mode:
                self.spawn_obstacle()

        return visited_count, -1

    def reconstruct(self, parent):
        node = self.goal
        while node in parent:
            node = parent[node]
            if node != self.start:
                self.grid[node[0]][node[1]] = "path"
            self.draw()
            self.root.update()
            time.sleep(0.02)

    def spawn_obstacle(self):
        if random.random() < SPAWN_PROBABILITY:
            r = random.randint(0, self.rows-1)
            c = random.randint(0, self.cols-1)
            if (r, c) not in (self.start, self.goal):
                if self.grid[r][c] == "empty":
                    self.grid[r][c] = "wall"


root = tk.Tk()
root.title("Dynamic Pathfinding Agent")
app = PathfindingApp(root)
root.mainloop()