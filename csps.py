from copy import copy, deepcopy
import random
goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]
moves = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def get_states(state):
    empty_x, empty_y = find_empty(state)
    states = []

    for x, y in MOVES:
        new_x, new_y = empty_x + x, empty_y + y
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            new_state = [row[:] for row in state]
            new_state[empty_x][empty_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[empty_x][empty_y]
            states.append(new_state)

    return states

def apply_action(state, action):
    x, y = find_empty(state)
    dx, dy = moves[action]
    nx, ny = x + dx, y + dy
    if 0 <= nx < 3 and 0 <= ny < 3:
        new_state = deepcopy(state)
        new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
        return new_state
    return None  

def backtrack_csp(state, path, visited, depth, max_depth):
    if state == goal_state:
        return path

    if depth >= max_depth:
        return None

    for action in moves:
        new_state = apply_action(state, action)
        if new_state is None:
            continue
        state_tuple = tuple(tuple(row) for row in new_state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        result = backtrack_csp(new_state, path + [new_state], visited, depth+1, max_depth)
        if result:
            return result
        visited.remove(state_tuple)  # CSP-style backtrack

    return None

def manhattan(state, goal):
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value == 0:
                continue
            for x in range(3):
                for y in range(3):
                    if goal[x][y] == value:
                        distance += abs(i - x) + abs(j - y)
                        break
    return distance

def backtrack_csp_fc(state, path, visited, depth, max_depth):
    if state == goal_state:
        return path

    # Forward checking (prune if no hope)
    if depth + manhattan(state, goal_state) > max_depth:
        return None

    for action in moves:
        new_state = apply_action(state, action)
        if new_state is None:
            continue
        state_tuple = tuple(tuple(row) for row in new_state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        result = backtrack_csp_fc(new_state, path + [new_state], visited, depth+1, max_depth)
        if result:
            return result
        visited.remove(state_tuple)  # CSP-style backtrack

    return None


def min_conflicts(start_state, max_steps=20000):
    current_state = deepcopy(start_state)
    path = [start_state]
    stuck_counter = 0
    max_stuck_steps = 10000

    for i in range(max_steps):
        if current_state == goal_state:
            return path
        next_states = get_states(current_state)
        min_conflicts = float('inf')
        best_states = []
        for state in next_states:
            conf = manhattan(state, goal_state)
            if conf < min_conflicts:
                min_conflicts = conf
                best_states = [state]
            elif conf == min_conflicts:
                best_states.append(state)
        if not next_states:
            continue

        chosen_state = random.choice(best_states)
        #current_state = chosen_state
        path.append(chosen_state)
        if manhattan(chosen_state, goal_state) >= manhattan(current_state, goal_state):
            stuck_counter += 1
        else:
            stuck_counter = 0

        current_state = chosen_state

        if stuck_counter >= max_stuck_steps:
            current_state = generate_random_state()
            path = []
            stuck_counter = 0
    
    return None

def generate_random_state():
    flat = list(range(9))
    while True:
        random.shuffle(flat)
        state = tuple(tuple(flat[i*3:(i+1)*3]) for i in range(3))
        if is_solvable(state):
            return state
        
def is_solvable(state):
    arr = [num for row in state for num in row if num != 0]  # Flatten trừ ô trống
    inversions = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inversions += 1
    return inversions % 2 == 0

def get_solution(start_state, algo):

    visited = set()
    visited.add(tuple(tuple(row) for row in start_state))
    if algo == "Backtracking":
        path  = backtrack_csp(start_state, [], visited, 0, 50)
    elif algo == "Backtracking with forward checking":
        path  = backtrack_csp_fc(start_state, [], visited, 0, 30)
    
    if path:
        return path
    

# start = [[4,1,3],
#          [7,2,5],
#          [0,8,6]]

# visited = set()
# visited.add(tuple(tuple(row) for row in start))

# result = min_conflicts(start)

# if result:
#     print("Solution:", result)
# else:
#     print("No solution found.")