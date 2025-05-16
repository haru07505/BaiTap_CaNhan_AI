import heapq
import itertools
import random
import time
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
from partial_ob import Ui_Form
import random

# Kiểm tra trạng thái có solvable không
def is_solvable(state):
    flat = [val for row in state for val in row if val != 0]
    inversions = sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])
    blank_row = next(i for i, row in enumerate(state) for j, val in enumerate(row) if val == 0)
    return (inversions % 2) == (blank_row % 2)

# Di chuyển ô trống
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

# Hàm kiểm tra 1 state có phù hợp quan sát không
def match_observation(state, observation):
    for (i, j), val in observation.items():
        if state[i][j] != val:
            return False
    return True

# Tạo belief ban đầu từ observation
def generate_initial_belief(observation, max_states=100):
    all_values = set(range(9))
    known_values = set(observation.values())
    unknown_values = list(all_values - known_values)
    unknown_positions = [(i, j) for i in range(3) for j in range(3) if (i, j) not in observation]
    
    belief = []
    for _ in range(max_states):
        perm = random.sample(unknown_values, len(unknown_values))
        state = [[-1]*3 for _ in range(3)]
        for (i, j), val in observation.items():
            state[i][j] = val
        for idx, (i, j) in enumerate(unknown_positions):
            state[i][j] = perm[idx]
        state_tuple = tuple(tuple(row) for row in state)
        if is_solvable(state_tuple) and state_tuple not in belief:
            belief.append(state_tuple)
    return belief

# Heuristic max của các belief state
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

# Filter belief theo quan sát
def filter_belief_with_observation(belief, observation):
    return [s for s in belief if match_observation(s, observation)]

# Hàm chính: giải bài toán 8-Puzzle với Partial Observation
def solve_partial_observation_8puzzle(initial_observation, goal):
    belief = generate_initial_belief(initial_observation)
    print(belief)
    #print(belief)
    visited = set()
    heap = []
    max_steps = 10000

    step = 0
    heapq.heappush(heap, (heuristic(belief, goal), 0, belief, []))

    while heap:
        _, cost, current_belief, path = heapq.heappop(heap)
        #print(current_belief)
        # Dừng sớm nếu belief chỉ chứa goal
        if len(current_belief) == 1 and current_belief[0] == goal:
            #print(current_belief)
            return path

        current_key = tuple(sorted(current_belief))
        if current_key in visited:
            continue
        visited.add(current_key)

        # Nếu đã chắc chắn 1 state và là goal
        # if any(state == goal for state in current_belief):
        #     return path

        for action in ['U', 'D', 'L', 'R']:
            next_states = []
            seen = set()
            for state in current_belief:
                new_state = move_blank(state, action)
                if new_state and new_state not in seen:
                    seen.add(new_state)
                    next_states.append(new_state)

            if not next_states:
                continue

            # Mô phỏng quan sát mới sau action
            new_observation = observe_fn(next_states, step + 1)
            filtered = filter_belief_with_observation(next_states, new_observation)
            if not filtered:
                continue

            g = cost + 1
            h = heuristic(filtered, goal)
            heapq.heappush(heap, (g + h, g, filtered, path + [action]))

        step += 1
        if step > max_steps:
            return ["Đạt giới hạn bước, không tìm thấy lời giải!"]
        #print(current_belief)
    return ["Không tìm thấy lời giải!"]

class PartialObs(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.goal = ((1,2,3),(4,5,6),(7,8,0))
        #self.timer = QTimer()
        self.solution = []
        self.current_step = 0
        # Gán chức năng cho các nút
        self.belief = []
        
        self.current_belief = []

        self.ui.solveButton.clicked.connect(self.solve_puzzle)
        self.ui.resetButton.clicked.connect(self.handle_reset)
        self.ui.exitButton.clicked.connect(self.close)

    def next_step(self):
        if self.current_step >= len(self.solution):
            self.timer.stop()
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            QMessageBox.information(self, "Thành công", f"Thời gian thực hiện: {self.elapsed_time}s")
            return

        action = self.solution[self.current_step]
        next_belief = []
        seen = set()
        for state in self.current_belief:          
            new_state = move_blank(state, action)
            if new_state and new_state not in seen:
                seen.add(new_state)
                next_belief.append(new_state)
                #print(new_state)

        if next_belief:
            self.current_belief = next_belief
            self.update_belief_display(next_belief)

        self.current_step += 1

    def get_observation_from_input(self):
        observation = {}
        for i in range(3):
            for j in range(3):
                label = getattr(self.ui, f"label_{i}_{j}")
                text = label.text()
                if text != "?":
                    if text == "":
                        observation[(i, j)] = 0
                    else:
                        observation[(i, j)] = int(text)
        return observation
    
    def update_belief_display(self, belief):
        grid = belief[0]
        for i in range(3):
            for j in range(3):
                value = grid[i][j]
                label = getattr(self.ui, f"label_{i}_{j}")
                if value == 0:
                    label.setText("")
                else:
                    label.setText(str(value))

    def solve_puzzle(self):
        initial_observation = self.get_observation_from_input()
        self.initial_observation = initial_observation

        path = solve_partial_observation_8puzzle(initial_observation, self.goal)

        if isinstance(path, list) and isinstance(path[0], str):
            self.ui.listWidget.addItem(" -> ".join(path))
            self.solution = path
            print(path)
            if self.solution:
                self.timer = QTimer()
                self.timer.timeout.connect(self.next_step)
                self.current_step = 0
                self.current_belief = generate_initial_belief(initial_observation)
                self.timer.start(300)  # 800ms mỗi bước
                self.start_time = time.time()
        else:
            self.ui.listWidget.addItem("Không tìm thấy lời giải!")
    
    def handle_reset(self):
        if hasattr(self, 'initial_observation'):
            for i in range(3):
                for j in range(3):
                    label = getattr(self.ui, f"label_{i}_{j}")
                    val = self.initial_observation.get((i, j), '?')
                    if val == 0:
                        label.setText("")
                    else:
                        label.setText(str(val))
        else:
            # nếu không có observation thì reset về dấu hỏi
            for i in range(3):
                for j in range(3):
                    label = getattr(self.ui, f"label_{i}_{j}")
                    label.setText("?")

        self.timer.stop()
        self.solution = []
        self.current_step = 0
        self.ui.listWidget.clear()
        self.current_belief = []
#Ví dụ goal
# goal = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

# # Observation ban đầu: biết vài ô
# init_obs = {
#     (0, 0): 1,
#     (0, 1): 2,
#     (0, 2): 8,
#     (1, 1): 5,
#     (2, 2): 0,
#     (2, 1): 3
# }

# # # Hàm mô phỏng quan sát sau mỗi bước
def observe_fn(belief, step):
    state = belief[0]
    observation = {}
    for i in range(3):
        for j in range(3):
            observation[(i, j)] = state[i][j]
    return observation

# # # Giải
# path = solve_partial_observation_8puzzle(init_obs, goal)
# print("Solution path:", path)