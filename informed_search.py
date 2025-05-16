import heapq

goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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

def manhattan_distance(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                target_x, target_y = divmod(state[i][j] - 1, 3)
                distance += abs(target_x - i) + abs(target_y - j)
    return distance

def greedy_best_first_search(start_state):
    priority_queue = [(manhattan_distance(start_state), start_state, [])]
    visited = set()

    while priority_queue:
        _, state, path = heapq.heappop(priority_queue)
        state_tuple = tuple(map(tuple, state))

        if state == goal_state:
            return path + [state]

        if state_tuple in visited:
            continue
        visited.add(state_tuple)

        for new_state in get_states(state):
            heapq.heappush(priority_queue, (manhattan_distance(new_state), new_state, path + [state]))

    return None

def ida_start(start_state):
    thershold = manhattan_distance(start_state)
    while True:
        stack = [(start_state, 0, [])]
        min_thereshold = float('inf')
        while stack:
            state, cost, path = stack.pop()
            f = cost + manhattan_distance(state)
            if f > thershold:
                min_thereshold = min(min_thereshold, f)
                continue

            if state == goal_state:
                return path + [state]

            for new_state in get_states(state):
                if new_state not in path:
                    stack.append((new_state, cost+1, path + [state]))

        if min_thereshold == float('inf'):
            return None
        thershold = min_thereshold

def a_start(start_state):
    priority_queue = [(manhattan_distance(start_state), 0, start_state, [])]
    visited = set()

    while priority_queue:
        _, cost, state, path = heapq.heappop(priority_queue)
        state_tuple = tuple(map(tuple, state))

        if state == goal_state:
            return path + [state]

        if state_tuple in visited:
            continue
        visited.add(state_tuple)

        for new_state in get_states(state):
            new_cost = cost + 1
            heapq.heappush(priority_queue, (new_cost + manhattan_distance(new_state), new_cost, new_state, path + [state]))

    return None