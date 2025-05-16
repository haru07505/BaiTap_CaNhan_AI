# gui.py
from collections import deque
import heapq
import time

from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
from sensorless_ui import Ui_Sensorless
import random

moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def is_solvable(puzzle):
    flat = [num for row in puzzle for num in row if num != 0]
    inv_count = sum(1 for i in range(len(flat)) for j in range(i+1, len(flat)) if flat[i] > flat[j])
    return inv_count % 2 == 0

def random_puzzle():
    while True:
        nums = list(range(9))
        random.shuffle(nums)
        puzzle = tuple(tuple(nums[i*3:(i+1)*3]) for i in range(3))
        if is_solvable(puzzle):
            return puzzle

def random_belief_set(n=3):
    belief = set()
    while len(belief) < n:
        belief.add(random_puzzle())
    return list(belief)

def move_blank(state, action):
    dx = {'U': -1, 'D': 1, 'L': 0, 'R': 0}
    dy = {'U': 0, 'D': 0, 'L': -1, 'R': 1}
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                x, y = i + dx[action], j + dy[action]
                if 0 <= x < 3 and 0 <= y < 3:
                    new = [list(row) for row in state]
                    new[i][j], new[x][y] = new[x][y], new[i][j]
                    return tuple(tuple(row) for row in new)
    return None
def manhattan(state, goal):
    pos = {val: (i, j) for i, row in enumerate(goal) for j, val in enumerate(row)}
    dist = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                gi, gj = pos[val]
                dist += abs(i - gi) + abs(j - gj)
    return dist

def heuristic(belief, goal):
    return max(manhattan(state, goal) for state in belief)

def sensorless_solve_astar(belief, goal):
    visited = set()
    heap = []
    #start = tuple(belief)
    heapq.heappush(heap, (heuristic(belief, goal), 0, belief, []))

    while heap:
        _, cost, current, path = heapq.heappop(heap)
        current_set = set(current)

        if all(state == goal for state in current):
            return path + [current]

        for action in ['U', 'D', 'L', 'R']:
            next_states = []
            seen = set()
            for state in current_set:
                new_state = move_blank(state, action)
                if new_state and new_state not in seen:
                    seen.add(new_state)
                    next_states.append(new_state)
            
            if next_states:      
                next_tuple = tuple(sorted(next_states)) 
                if next_tuple not in visited:
                    visited.add(next_tuple)
                    g = cost + 1
                    h = heuristic(next_states, goal)
                    heapq.heappush(heap, (g + h, g, next_states, path + [current]))

    return ["Không tìm thấy lời giải!"]

class SensorlessApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Sensorless()
        self.ui.setupUi(self)

        #self.belief = random_belief_set(3)
        self.belief = [
            ((1, 2, 3), (4, 5, 6), (7, 0, 8)),
            ((1, 2, 3), (4, 5, 6), (0, 7, 8)),
            ((1, 2, 3), (4, 5, 6), (7, 8, 0))
        ]
        self.current_belief = list()
        self.goal = ((1,2,3),(4,5,6),(7,8,0))
        #self.timer = QTimer()
        self.solution = []
        self.current_step = 0
        # Gán chức năng cho các nút
        self.ui.randomButton.clicked.connect(self.handle_random)
        self.ui.solveButton.clicked.connect(self.handle_solve)
        self.ui.resetButton.clicked.connect(self.handle_reset)
        self.ui.exitButton.clicked.connect(self.close)

        self.update_belief_view()

    def update_belief_view(self):
        for idx, state in enumerate(self.belief):
            self.draw_state(state, idx)
        #self.ui.listPath.clear()

    def handle_random(self):
        self.belief = random_belief_set(3)
        self.update_belief_view()

    def handle_solve(self):
        self.current_belief = self.belief
        self.solution = sensorless_solve_astar(self.belief, self.goal)
        self.ui.listPath.clear()
        if self.solution:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_grid)
            self.current_step = 0
            self.timer.start(500)
            self.start_time = time.time()
        else:
            QMessageBox.warning(self, "Thất bại", "Không tìm thấy lời giải!")

    def update_grid(self):
        if self.current_step < len(self.solution):
            action = self.solution[self.current_step]
            self.ui.listPath.addItem(str(action))
            #print(action)
            self.belief = action
            self.update_belief_view()
            # for state in self.belief:
            #     self.ui.listPath.addItem(str(state))
            self.ui.listPath.addItem("\n")
            self.current_step += 1
        else:
            self.timer.stop()
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            QMessageBox.information(self, "Thành công", f"Thời gian thực hiện: {self.elapsed_time}s")
    
    def handle_reset(self):
        self.belief = self.current_belief
        self.update_belief_view()
        self.timer.stop()
        self.solution = []
        self.current_step = 0
        self.ui.listPath.clear()
    
    def draw_state(self, state, board_idx):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                name = f"label_{board_idx+1}_{i}_{j}"
                label = getattr(self.ui, name)
                label.setText("" if val == 0 else str(val))