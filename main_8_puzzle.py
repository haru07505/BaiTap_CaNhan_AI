import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox
from PyQt6.QtCore import QTimer
from interface_8_puzzle import Ui_MainWindow
from uninformed_search import bfs_solve, dfs, ids, ucs
from informed_search import greedy_best_first_search, ida_start, a_start
from local_search import shc, steepest_ahc, stochastic_hc, simulated_annealing, beam_search, solution_for_ga
from and_or import and_or_search
from sensorless_problem import SensorlessApp
from partial_obs import PartialObs
from csps import get_solution, min_conflicts
#from q_learning import train_q_learning, play

def manhattan_distance(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                goal_x, goal_y = divmod(state[i][j] - 1, 3)
                distance += abs(goal_x - i) + abs(goal_y - j)
    return distance

class EightPuzzleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 

        self.initial_state = [
            [2, 6, 5],
            [0, 8, 7],
            [4, 3, 1]
        ]    

        self.positions = {} 

        self.sensorless_window = None
        self.partial_obs_window = None

        for i in range(3):
            for j in range(3):
                value = self.initial_state[i][j]
                label_name = f"label_{value}" if value != 0 else "label_empty"
                label = getattr(self.ui, label_name)
                self.positions[value] = label.pos() 

        self.ui.solveButton.clicked.connect(self.solve_puzzle)
        self.ui.resetButton.clicked.connect(self.reset_puzzle)
        self.ui.exitButton.clicked.connect(self.close)
        self.ui.sensorlessButton.clicked.connect(self.open_sensorless_window)
        self.ui.parObButton.clicked.connect(self.open_partob_window)

    def open_partob_window(self):
        if self.partial_obs_window is None:
            self.partial_obs_window = PartialObs()
        self.partial_obs_window.show()

    def open_sensorless_window(self):
        if self.sensorless_window is None:
            self.sensorless_window = SensorlessApp()
        self.sensorless_window.show()
    def update_grid(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                label_name = f"label_{value}" if value != 0 else "label_empty"
                if hasattr(self.ui, label_name):
                    label = getattr(self.ui, label_name)
                    new_x = self.positions[0].x() + j * 135
                    new_y = self.positions[0].y() + i * 125 

                    label.move(new_x, new_y)
    def solve_puzzle(self):
        QMessageBox.information(self, "Chú ý", "Đang tính toán tiến trình giải.")
        self.selected_algorithm = self.ui.algorithmComboBox.currentText()

        if self.selected_algorithm == "UCS":
            solution = ucs(self.initial_state)
        elif self.selected_algorithm == "BFS":
            solution = bfs_solve(self.initial_state)
        elif self.selected_algorithm == "IDS":
            solution = ids(self.initial_state)
        elif self.selected_algorithm == "DFS":
            solution = dfs(self.initial_state)
        elif self.selected_algorithm == "Greedy Search":
            solution = greedy_best_first_search(self.initial_state)
        elif self.selected_algorithm == "A* Search":
            solution = a_start(self.initial_state)
        elif self.selected_algorithm == "IDA* Search":
            solution = ida_start(self.initial_state)
        elif self.selected_algorithm == "Simple HC":
            solution = shc(self.initial_state)
        elif self.selected_algorithm == "Steepest Ascent HC":
            solution = steepest_ahc(self.initial_state)
        elif self.selected_algorithm == "Stochastic HC":
            solution = stochastic_hc(self.initial_state)
        elif self.selected_algorithm == "Simulated Annealing":
            solution = simulated_annealing(self.initial_state)
        elif self.selected_algorithm == "Beam Search":
            solution = beam_search(self.initial_state)
        elif self.selected_algorithm == "Genetic Algorithm":
            solution = solution_for_ga(self.initial_state)
        elif self.selected_algorithm == "AND-OR Graph":
            solution = and_or_search(self.initial_state)
        elif self.selected_algorithm == "Backtracking":
            solution = get_solution(self.initial_state, "Backtracking")
        elif self.selected_algorithm == "Backtracking with forward checking":
            solution = get_solution(self.initial_state, "Backtracking with forward checking")
        elif self.selected_algorithm == "Min-Conflicts":
            solution = min_conflicts(self.initial_state)
        # elif self.selected_algorithm == "Q-Learning":
        #     train = train_q_learning()
        #     path = play()
        #     solution = list(map(list, path))

        self.solution = solution
        if self.solution:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_solution)
            self.solution_index = 0
            self.timer.start(300)
            self.start_time = time.time()
        else:
            QMessageBox.warning(self, "Thất bại", "Không tìm thấy lời giải!")

    def update_solution(self):
        if self.solution_index < len(self.solution):
            self.initial_state = self.solution[self.solution_index]
            self.update_grid(self.initial_state)
            self.ui.listWidget.addItem(str(self.initial_state))
            h_n = manhattan_distance(self.initial_state)
            g_n = self.solution_index
            f_n = h_n + g_n
            if self.selected_algorithm == "Greedy Search":
                self.ui.label_21.setText("h(n) = ")
                self.ui.hnLabel.setText(str(h_n))
            elif self.selected_algorithm == "A* Search":
                self.ui.label_21.setText("f(n) = ")
                self.ui.hnLabel.setText(str(f_n))
            elif self.selected_algorithm == "IDA* Search":
                self.ui.label_21.setText("f(n) = ")
                self.ui.hnLabel.setText(str(f_n))
            self.solution_index += 1
        else:
            self.timer.stop()
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            self.ui.timeLabel.setText(f"{round(self.elapsed_time, 4)}s")
            QMessageBox.information(self, "Thành công", f"Thời gian thực hiện: {self.elapsed_time}s")
    def reset_puzzle(self):  
        self.initial_state = [
            [2, 6, 5],
            [0, 8, 7],
            [4, 3, 1]
        ]  
        self.update_grid(self.initial_state)
        self.ui.listWidget.clear()
        self.ui.timeLabel.clear()
        self.ui.hnLabel.clear()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EightPuzzleApp()
    window.show()
    sys.exit(app.exec())