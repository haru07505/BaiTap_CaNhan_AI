import random
from collections import defaultdict
from copy import deepcopy

# Các hành động
actions = ['U', 'D', 'L', 'R']
moves = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

#goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
goal_state = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
# Hàm tìm vị trí của ô trống
def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

# Hàm áp dụng hành động vào trạng thái
def apply_action(state, action):
    x, y = find_empty(state)
    dx, dy = moves[action]
    nx, ny = x + dx, y + dy
    if 0 <= nx < 3 and 0 <= ny < 3:
        new_state = [list(row) for row in state]
        new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
        return tuple(tuple(row) for row in new_state)
    return None

# Các tham só Q-learning p
alpha = 0.1       
gamma = 0.9        
epsilon = 0.2      
episodes = 10000   

# Khởi tạo Q-table
Q = defaultdict(lambda: {a: 0.0 for a in actions})

# Hàm chọn hành động theo epsilon-greedy
def choose_action(state):
    if random.random() < epsilon:
        return random.choice(actions)
    else:
        return max(Q[state], key=Q[state].get)

# Hàm huấn luyện Q-learning
def train_q_learning():
    solution_path = []  # Danh sách các trạng thái trong quá trình giải quyết
    for ep in range(episodes):
        state = ((1, 2, 3), (4, 0, 6), (7, 5, 8))  # Trạng thái khởi tạo
        path = [state]  # Bắt đầu từ trạng thái ban đầu
        
        while state != goal_state:
            action = choose_action(state)
            next_state = apply_action(state, action)
            if next_state:
                reward = 100 if next_state == goal_state else -1
                max_q_next = max(Q[next_state].values())
            else:
                reward = -100
                next_state = state
                max_q_next = max(Q[next_state].values())
            
            # Cập nhật Q-value
            Q[state][action] += alpha * (reward + gamma * max_q_next - Q[state][action])
            state = next_state
            path.append(state)
        
        solution_path.append(path)  # Lưu lại chuỗi trạng thái của một episode
    
    return solution_path

# Hàm chơi game với policy đã học
def play():
    state = ((1, 2, 3), (4, 0, 6), (7, 5, 8))
    path = [list(state)]
    steps = 0
    while state != goal_state and steps < 50:
        action = max(Q[state], key=Q[state].get)
        state = apply_action(state, action)
        path.append(state)
        steps += 1
    
    return path

# Huấn luyện Q-learning và lấy giải pháp
solution_path = train_q_learning()


#In giải pháp cuối cùng (trạng thái đi qua của một episode)
if solution_path:
    print("Solution trong lúc huấn luyện:")
    for path in solution_path[0]:  # In trạng thái của một episode đầu tiên
        for row in path:
            print(row)
        print("----")

# Kiểm tra giải pháp đã học
final_path = play()
list_final_path = list(map(list, final_path))

print("Solution cuối cùng::")
for state in list_final_path:    
    print(state)
    print("----")
