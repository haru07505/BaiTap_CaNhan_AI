from collections import deque
import heapq, time

goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def matrix_to_tuple(matrix):
    return tuple(tuple(row) for row in matrix)

def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
            
def get_states(state):
    empty_x, empty_y = find_empty(state)
    states = []

    for x, y in moves:
        new_x, new_y = empty_x + x, empty_y + y
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            new_state = [row[:] for row in state]
            new_state[empty_x][empty_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[empty_x][empty_y]
            states.append(new_state)

    return states

def bfs_solve(start_state):
    open = deque([(start_state, [])])
    visited = set()
    visited.add(matrix_to_tuple(start_state))

    while open:
        current_state, path = open.popleft()
        if current_state == goal_state:
            return path
        for state in get_states(current_state):
            state_tuple = matrix_to_tuple(state)
            if state_tuple not in visited:
                visited.add(state_tuple)
                open.append((state, path + [state]))
    return None

def manhattan_distance(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                target_x, target_y = divmod(state[i][j] - 1, 3)
                distance += abs(target_x - i) + abs(target_y - j)
    return distance
def dfs(start_state):
    stack = [(start_state, [], 0)]
    visited = set()

    while stack:
        state, path, depth = stack.pop()
        state_tuple = tuple(map(tuple, state))

        if state == goal_state:
            return path + [state]
        
        if state_tuple in visited or depth > 30:
            continue
        visited.add(state_tuple)
        next_states = get_states(state)
        next_states.sort(key=manhattan_distance, reverse=True)

        for new_state in next_states:
            stack.append((new_state, path + [state], depth+1))
            
    return None, 

def depth_bound_search(state, depth_bound, visited):
    if state == goal_state:
        return [state]
    if depth_bound > 0:
        state_tuple = tuple(map(tuple, state))
        if state_tuple in visited:
            return None
        visited.add(state_tuple)
        next_states = get_states(state)
        next_states.sort(key=manhattan_distance, reverse=True) 
        for new_state in next_states:
            res = depth_bound_search(new_state, depth_bound - 1, visited)
            if res:
                return [state] + res
    return None

def ids(start_state):
    depth = 0
    for depth in range (30):
        visited = set()
        res = depth_bound_search(start_state, depth, visited)
        if res:
            return res
        depth += 1

def ucs(start_state):
    priority_queue = [(0, start_state, [])]
    visited = set()
    
    while priority_queue:
        cost, state, path = heapq.heappop(priority_queue)
        state_tuple = tuple(map(tuple, state))
        
        if state == goal_state:
            return path + [state]
        
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        
        for new_state in get_states(state):
            heapq.heappush(priority_queue, (cost + 1, new_state, path + [state]))
    
    return None
