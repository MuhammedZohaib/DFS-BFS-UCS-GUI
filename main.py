import tkinter as tk
import random
import time
import heapq
from collections import deque, defaultdict


class Graph:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.adj_list = defaultdict(list)
        self.grid = [[0] * cols for _ in range(rows)]
        self.start = None
        self.goal = None

    def add_edge(self, u, v, cost=1):
        self.adj_list[u].append((v, cost))

    def set_start(self, row, col):
        self.start = (row, col)

    def set_goal(self, row, col):
        self.goal = (row, col)

    def clear_grid(self):
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.adj_list.clear()

    def generate_random_grid(self):
        self.clear_grid()

        # Place obstacles randomly
        for row in range(self.rows):
            for col in range(self.cols):
                if random.random() < 0.2:  # 20% chance of obstacle
                    self.grid[row][col] = 1  # Obstacle

        # Choose random start and goal positions (avoid obstacles)
        while True:
            start_row, start_col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if self.grid[start_row][start_col] == 0:  # Ensure it's not an obstacle
                self.set_start(start_row, start_col)
                break

        while True:
            goal_row, goal_col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if (goal_row != start_row or goal_col != start_col) and self.grid[goal_row][goal_col] == 0:
                self.set_goal(goal_row, goal_col)
                break

        # Build graph connectivity (4-connected grid)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 0:  # Not an obstacle
                    current_node = (row, col)
                    for dr, dc in directions:
                        new_row, new_col = row + dr, col + dc
                        if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.grid[new_row][new_col] == 0:
                            # Valid neighboring cell (not obstacle)
                            neighbor_node = (new_row, new_col)
                            self.add_edge(current_node, neighbor_node)

    def dfs(self):
        return self._run_algorithm(self.start, self.goal, self._dfs)

    def bfs(self):
        return self._run_algorithm(self.start, self.goal, self._bfs)

    def ucs(self):
        return self._run_algorithm(self.start, self.goal, self._ucs)

    def _run_algorithm(self, start, goal, algorithm_func):
        if not start or not goal:
            return None, 0.0  # No start or goal set

        start_time = time.time()
        result = algorithm_func(start, goal)
        execution_time = time.time() - start_time
        return result, execution_time

    def _dfs(self, start, goal):
        visited = set()
        stack = [(start, [start])]

        while stack:
            node, path = stack.pop()
            if node not in visited:
                if node == goal:
                    return path
                visited.add(node)
                for neighbor in self.adj_list[node]:
                    if neighbor[0] not in visited:
                        stack.append((neighbor[0], path + [neighbor[0]]))

        return None

    def _bfs(self, start, goal):
        visited = set()
        queue = deque([(start, [start])])

        while queue:
            node, path = queue.popleft()
            if node not in visited:
                if node == goal:
                    return path
                visited.add(node)
                for neighbor in self.adj_list[node]:
                    if neighbor[0] not in visited:
                        queue.append((neighbor[0], path + [neighbor[0]]))

        return None

    def _ucs(self, start, goal):
        priority_queue = [(0, start, [start])]
        visited = set()

        while priority_queue:
            current_cost, node, path = heapq.heappop(priority_queue)
            if node not in visited:
                if node == goal:
                    return path
                visited.add(node)
                for neighbor in self.adj_list[node]:
                    if neighbor[0] not in visited:
                        heapq.heappush(priority_queue, (current_cost + neighbor[1], neighbor[0], path + [neighbor[0]]))

        return None


# Create the GUI
class PathfindingGUI:
    def __init__(self, master, rows, cols):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.graph = Graph(rows, cols)
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, width=self.cols * 10, height=self.rows * 10, bg='white')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.place_start)
        self.canvas.bind("<Button-3>", self.place_goal)

        self.generate_button = tk.Button(self.master, text="Generate New Puzzle", command=self.generate_new_puzzle)
        self.generate_button.pack(pady=10)

        self.generate_new_puzzle()  # Generate initial random puzzle
        self.draw_grid()

        frame = tk.Frame(self.master)
        frame.pack(pady=10)

        algorithms = [("DFS", self.graph.dfs), ("BFS", self.graph.bfs), ("UCS", self.graph.ucs)]

        for algo_name, algo_func in algorithms:
            tk.Button(frame, text=algo_name, command=lambda func=algo_func: self.run_algorithm(func)).pack(side=tk.LEFT, padx=10)

    def draw_grid(self):
        self.canvas.delete("all")
        for row in range(self.rows):
            for col in range(self.cols):
                color = 'black' if self.graph.grid[row][col] == 1 else 'white'
                self.canvas.create_rectangle(col * 10, row * 10, (col + 1) * 10, (row + 1) * 10, fill=color)

        if self.graph.start:
            row, col = self.graph.start
            self.canvas.create_rectangle(col * 10, row * 10, (col + 1) * 10, (row + 1) * 10, fill='green')

        if self.graph.goal:
            row, col = self.graph.goal
            self.canvas.create_rectangle(col * 10, row * 10, (col + 1) * 10, (row + 1) * 10, fill='red')

    def generate_new_puzzle(self):
        self.graph.generate_random_grid()
        self.draw_grid()

    def place_start(self, event):
        self.graph.clear_grid()
        row, col = event.y // 10, event.x // 10
        self.graph.set_start(row, col)
        self.draw_grid()

    def place_goal(self, event):
        row, col = event.y // 10, event.x // 10
        self.graph.set_goal(row, col)
        self.draw_grid()

    def run_algorithm(self, algorithm_func):
        result, execution_time = algorithm_func()
        if result:
            self.highlight_path(result)
            print(f"Execution Time: {execution_time:.6f} seconds")
        else:
            print("No path found!")

    def highlight_path(self, path):
        self.canvas.delete("path")
        for row, col in path:
            if (row, col) != self.graph.start and (row, col) != self.graph.goal:
                self.canvas.create_rectangle(col * 10, row * 10, (col + 1) * 10, (row + 1) * 10, fill='yellow', tags="path")


# Main function to start the GUI
def main():
    root = tk.Tk()
    root.title("Pathfinding GUI")
    rows, cols = 80, 150
    gui = PathfindingGUI(root, rows, cols)
    root.mainloop()


if __name__ == "__main__":
    main()
