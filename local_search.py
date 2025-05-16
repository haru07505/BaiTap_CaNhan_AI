import heapq
import math
import random

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

def shc(start_state):
    current_state = start_state
    path = [current_state]

    while True:
        current_score = manhattan_distance(current_state)
        next_states = get_states(current_state)
        best_state = None
        for state in next_states:
            if manhattan_distance(state) < current_score:  
                current_state = state
                path.append(current_state)
                break
        if best_state is None:
            break

        if current_state == goal_state:
            return path
    return None

def steepest_ahc(start_state):
    current_state = start_state
    path = [current_state]

    while True:
        current_score = manhattan_distance(start_state)
        next_states = get_states(current_state)
        best_state = None
        best_score = current_score
        for state in next_states:
            score = manhattan_distance(state)
            if score < best_score:
                best_score = score
                best_state = state
        if best_state is None:
            break
        path.append(best_state)
        current_state = best_state
        if current_state == goal_state:
            return path
    return None

def stochastic_hc(start_state):
    current_state = start_state
    path = [current_state]

    while True:
        current_score = manhattan_distance(current_state)
        next_states = get_states(current_state)
        better = [state for state in next_states if manhattan_distance(state) < current_score]
        if not better:
            break
        current_state = random.choice(better)
        path.append(current_state)
        if current_state == goal_state:
            return path
    return None

def simulated_annealing(start_state, max_steps=10000, initial_temp=10000.0, rate=0.999999):
    current_state = start_state
    path = [current_state]
    T = initial_temp

    for step in range(max_steps):
        current_score = manhattan_distance(current_state)
        if current_state == goal_state:
            return path

        next_states = get_states(current_state)
        if not next_states:
            break

        # Chọn ngẫu nhiên một state từ next_states
        next_state = random.choice(next_states)
        next_score = manhattan_distance(next_state)
        delta_e = next_score - current_score

        # Nếu tốt hơn thì nhận, nếu không thì chấp nhận với xác suất
        if delta_e < 0 or random.uniform(0, 1) < math.exp(-delta_e / T):
            current_state = next_state
            path.append(current_state)

        # Giảm nhiệt độ
        T *= rate
        if T < 1e-3:
            break

    return None

def beam_search(start_state, beam_width=5):
    beam = [(manhattan_distance(start_state), start_state, [start_state])]
    visited = set()

    for step in range(1000):
        new_beam = []
        for _, state, path in beam:
            if tuple(map(tuple, state)) in visited:
                continue
            visited.add(tuple(map(tuple, state)))

            if state == goal_state:
                return path

            for next_state in get_states(state):
                heapq.heappush(new_beam, (manhattan_distance(next_state), next_state, path + [next_state]))
        if not new_beam:
            break   
        beam = heapq.nsmallest(beam_width, new_beam)
    
    return None

def solution_for_ga(start_state):
    def create_population(size):
        population = []
        for _ in range(size):
            individual = [random.randint(0, 3) for _ in range(30)]
            population.append(individual)
        return population

    def fitness(individual):
        state = [row[:] for row in start_state]
        for move in individual:
            empty_x, empty_y = find_empty(state)
            new_x, new_y = empty_x + moves[move][0], empty_y + moves[move][1]
            if 0 <= new_x < 3 and 0 <= new_y < 3:
                state[empty_x][empty_y], state[new_x][new_y] = state[new_x][new_y], state[empty_x][empty_y]
        return manhattan_distance(state), state

    def crossover(p1, p2):
        cut = random.randint(0, len(p1) - 1)
        return p1[:cut] + p2[cut:]

    def mutate(individual, mutation_rate=0.05):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = random.randint(0, 3)
        return individual

    def genetic_algorithm(population_size=100, generations=1000):
        population = create_population(population_size)
        best_fitness = float('inf')
        best_path = [start_state]

        for gen in range(generations):
            evaluated = []
            for individual in population:
                score, state = fitness(individual)
                evaluated.append((score, individual, state))

            evaluated.sort(key=lambda x: x[0])
            best_fitness, best_individual, best_state = evaluated[0]
    
            if best_fitness == 0:
                state = [row[:] for row in start_state]
                for move in best_individual:
                    empty_x, empty_y = find_empty(state)
                    new_x, new_y = empty_x + moves[move][0], empty_y + moves[move][1]
                    if 0 <= new_x < 3 and 0 <= new_y < 3:
                        state[empty_x][empty_y], state[new_x][new_y] = state[new_x][new_y], state[empty_x][empty_y]
                        best_path.append([row[:] for row in state])
                    if state == goal_state:
                        break
                return best_path

            new_population = []
            while len(new_population) < population_size:
                p1 = random.choice(evaluated[:population_size // 2])[1]
                p2 = random.choice(evaluated[:population_size // 2])[1]
                child = crossover(p1, p2)
                child = mutate(child)
                new_population.append(child)

            population = new_population

        return None

    sol = genetic_algorithm()
    if sol:
        return sol
    else:
        return None
    
# start = [
#     [1, 2, 3],
#     [4, 0, 6],
#     [7, 5, 8]
# ]

# start = [[4,1,3],
#          [7,2,5],
#          [0,8,6]]

# start = [[1, 6, 5],
#          [0, 8, 7],
#          [4, 3, 1]
# ]

# result = solution_for_ga(start)

# if result:
#     print("Solution:", result)
# else:
#     print("No solution found.")