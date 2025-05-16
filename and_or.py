
goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

moves = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1)
}

def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
            
def and_or_search(start_state, max_depth = 100):
    def explore(state, path, depth, visited):

        if state == goal_state:
            return path + [state]

        if depth >= max_depth:
            return None
        
        state_tuple = tuple(map(tuple, state))
        if state_tuple in visited:
            return None
        visited.add(state_tuple)

        empty_x, empty_y = find_empty(state)
        for move, (x, y) in moves.items():
            new_x, new_y = empty_x + x, empty_y + y
            if 0 <= new_x < 3 and 0 <= new_y < 3:
                new_state = [row[:] for row in state]
                new_state[empty_x][empty_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[empty_x][empty_y]
                result = explore(new_state, path + [state], depth + 1, visited)
                if result is not None:
                    return result
        return None
    visited = set()
    result = explore(start_state, [], 0, visited)
    return result if result else None

if __name__ == "__main__":
    initial_belief = [
        [2, 6, 5],
        [0, 8, 7],
        [4, 3, 1]
    ]

    result = and_or_search(initial_belief)
    if result:
        print("Giải thuật AND-OR tìm thấy giải pháp:")
        for state in result:
            print(state)
    else:
        print("Không tìm thấy giải pháp.")