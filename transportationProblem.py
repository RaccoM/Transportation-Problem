import csv
import numpy as np

# Function to read CSV file and extract supply, demand, and costs
def read_csv_data(file_name):
    with open(file_name, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        data = list(reader)

    data = np.array(data, dtype=float)
    
    # Extracting the costs matrix (all but the last row and column)
    cost_matrix = data[:-1, :-1]
    
    # Extracting the supply values (last column, excluding the last row)
    supply = data[:-1, -1]
    
    # Extracting the demand values (last row, excluding the last column)
    demand = data[-1, :-1]
    
    return supply, demand, cost_matrix

# Function to verify if supply equals demand
def check_balance(supply, demand):
    total_supply = sum(supply)
    total_demand = sum(demand)
    
    if total_supply != total_demand:
        raise Exception(f"Total supply ({total_supply}) and total demand ({total_demand}) are not equal.")
    
    return supply, demand

# Function to print the data: supply, demand, and cost matrix
def print_data(supply, demand, cost_matrix):
    print("Supply:", supply)
    print("Demand:", demand)
    print("Costs:")
    for row in cost_matrix:
        print(row)
    print()

# North-West Corner Method to initialize the BFS
def north_west_corner(supply, demand):
    supply_copy = supply.copy()
    demand_copy = demand.copy()
    i, j = 0, 0
    bfs = []
    
    while len(bfs) < len(supply) + len(demand) - 1:
        s = supply_copy[i]
        d = demand_copy[j]
        min_value = min(s, d)
        supply_copy[i] = supply_copy[i] - min_value
        demand_copy[j] = demand_copy[j] - min_value
        bfs.append(((i, j), min_value))
        
        if supply_copy[i] == 0 and i < len(supply) - 1:
            i = i + 1
        elif demand_copy[j] == 0 and j < len(demand) - 1:
            j = j + 1
            
    return bfs

# Function to calculate u and v values from BFS
def calculate_u_v(bfs, cost_matrix):
    u_values = [None] * len(cost_matrix)
    v_values = [None] * len(cost_matrix[0])
    u_values[0] = 0
    bfs_copy = bfs.copy()
    
    while len(bfs_copy) > 0:
        for index, bv in enumerate(bfs_copy):
            i, j = bv[0]
            if u_values[i] is None and v_values[j] is None: continue
                
            cost = cost_matrix[i][j]
            if u_values[i] is None:
                u_values[i] = cost - v_values[j]
            else:
                v_values[j] = cost - u_values[i]
            bfs_copy.pop(index)
            break
            
    return u_values, v_values

# Calculate the reduced costs for non-basic variables
def calculate_reduced_costs(bfs, cost_matrix, u_values, v_values):
    reduced_costs = []
    for i, row in enumerate(cost_matrix):
        for j, cost in enumerate(row):
            is_non_basic = all([p[0] != i or p[1] != j for p, v in bfs])
            if is_non_basic:
                reduced_costs.append(((i, j), u_values[i] + v_values[j] - cost))
    
    return reduced_costs

# Check if any non-basic variable can improve the solution
def check_improvement(reduced_costs):
    for p, cost in reduced_costs:
        if cost > 0: 
            return True
    return False

# Find the position of the entering variable
def find_entering_variable_position(reduced_costs):
    reduced_costs_copy = reduced_costs.copy()
    reduced_costs_copy.sort(key=lambda x: x[1])
    return reduced_costs_copy[-1][0]

# Get the possible next nodes to form a loop
def find_possible_next_nodes(loop, not_visited):
    last_node = loop[-1]
    row_nodes = [n for n in not_visited if n[0] == last_node[0]]
    column_nodes = [n for n in not_visited if n[1] == last_node[1]]
    
    if len(loop) < 2:
        return row_nodes + column_nodes
    else:
        prev_node = loop[-2]
        is_row_move = prev_node[0] == last_node[0]
        if is_row_move:
            return column_nodes
        return row_nodes

# Find the loop in the cycle
def find_loop(bfs_positions, entering_position):
    def search_loop(loop):
        if len(loop) > 3:
            can_be_closed = len(find_possible_next_nodes(loop, [entering_position])) == 1
            if can_be_closed: return loop
        
        not_visited = list(set(bfs_positions) - set(loop))
        next_nodes = find_possible_next_nodes(loop, not_visited)
        
        for next_node in next_nodes:
            new_loop = search_loop(loop + [next_node])
            if new_loop: return new_loop
    
    return search_loop([entering_position])

# Pivot the loop in the BFS to get the new solution
def pivot_loop(bfs, loop):
    even_cells = loop[0::2]
    odd_cells = loop[1::2]
    get_bv_value = lambda pos: next(v for p, v in bfs if p == pos)
    leaving_position = sorted(odd_cells, key=get_bv_value)[0]
    leaving_value = get_bv_value(leaving_position)
    
    new_bfs = []
    for pos, value in [bv for bv in bfs if bv[0] != leaving_position] + [(loop[0], 0)]:
        if pos in even_cells:
            value = value + leaving_value
        elif pos in odd_cells:
            value = value - leaving_value
        new_bfs.append((pos, value))
        
    return new_bfs

# Main transportation simplex method
def transportation_simplex(supply, demand, cost_matrix):
    # Check if supply equals demand before proceeding
    supply, demand = check_balance(supply, demand) 
    
    print_data(supply, demand, cost_matrix)
    
    bfs = north_west_corner(supply, demand)  # Initialize BFS using North-West Corner Method
    
    # Iterative process to improve the solution
    while True:
        u_values, v_values = calculate_u_v(bfs, cost_matrix)
        reduced_costs = calculate_reduced_costs(bfs, cost_matrix, u_values, v_values)
        
        if not check_improvement(reduced_costs):
            break
        
        entering_position = find_entering_variable_position(reduced_costs)
        loop = find_loop([p for p, v in bfs], entering_position)
        bfs = pivot_loop(bfs, loop)
    
    # Generate final solution matrix
    solution_matrix = np.zeros((len(cost_matrix), len(cost_matrix[0])))
    for (i, j), value in bfs:
        solution_matrix[i][j] = value

    return solution_matrix

# Function to calculate the total cost of the transportation plan
def calculate_total_cost(cost_matrix, solution_matrix):
    total_cost = 0
    for i, row in enumerate(cost_matrix):
        for j, cost in enumerate(row):
            total_cost = total_cost + cost * solution_matrix[i][j]
    return total_cost

# Example usage
file_name = 'matrix.csv'  # Replace with your file path
supply, demand, cost_matrix = read_csv_data(file_name)  # Read data from CSV file

# Solve the transportation problem using simplex method
solution = transportation_simplex(supply, demand, cost_matrix)

# Print the result and total cost
print("Solution:")
print(solution)
print('Total cost:', calculate_total_cost(cost_matrix, solution))
