from helpers import load_data

MAX_DISTANCE = 100_000  # at start of dijsktra, everything is very far away
NO_PRIOR = -1			# at start of dijstra, each vertex has no path back to source
TOTAL_TIME = 30         # problem runs for the given number of time steps
STARTING_VERTEX = 'AA'  # problem always starts here, regardless of data


# find adjacent, unvisted vertices
def closest_unvisted_vertex(distances, visited):
    min_distance = MAX_DISTANCE
    min_vertex = None  # there could be no reachable, unvisited vertices
    for v in vertex_set:
        if distances[v] < min_distance and visited[v] == False:
            min_distance = distances[v]
            min_vertex = v
    return min_vertex


# get all vertices adjacent to given vertex
def get_adjacent_vertices(vertex, edge_set):
    result = []
    for start, end in edge_set:
        if start == vertex:
            result.append(end)
        elif end == vertex:
            result.append(start)
    return result


# returns dict of key: destination, value: path to destination
def build_shortest_path(priors, source_vertex, destination_vertex):
    if source_vertex == destination_vertex:
        return None

    path = [destination_vertex]
    prior_vertex = priors[destination_vertex]
    while prior_vertex != NO_PRIOR:
        path.append(prior_vertex)
        prior_vertex = priors[prior_vertex]
    path.reverse()

    # return None if there isn't a path from source to destination
    if path[0] != source_vertex:
        return None
    else:
        return path[1:]


# compute shortest paths and shortest distances to every vertex in graph
def dijkstra(source, vertex_set, edge_set):
    distances = {vertex: MAX_DISTANCE for vertex in vertex_set}
    distances[source] = 0
    visited = {vertex: False for vertex in vertex_set}
    priors = {vertex: NO_PRIOR for vertex in vertex_set}

    # algorithm must consider all vertices to complete
    for _ in range(len(vertex_set)):
        # break early if there's no reachable, unactivated vertices
        closest = closest_unvisted_vertex(distances, visited)
        if closest == None:
            break

        # visit new vertex, mark it as the prior of its unvisted, adjacent vertices
        visited[closest] = True
        for adjacent in get_adjacent_vertices(closest, edge_set):
            if (visited[adjacent] == False and distances[adjacent] > distances[closest] + 1):
                distances[adjacent] = distances[closest] + 1
                priors[adjacent] = closest

    # note: walrus operator makes this more concise. it's both a statement and an expression
    return {destination: shortest_path for destination in vertex_set if (shortest_path := build_shortest_path(priors, source, destination)) != None}


# get every possible order we could release the valves in, recursively
def get_possible_combinations_1(shortest_paths, current_location, time_left, activated_valve_set):
    # next valves that could be opened before time runs out
    candidates = {
        destination: path
        for destination, path in shortest_paths[current_location].items()
        if valve_flow_rates[destination] != 0 and destination not in activated_valve_set
    }

    # base case: no candidates left
    if len(candidates) == 0:
        return []

    # recursively get all the combinations from the candidate valves
    combinations = []
    for candidate, path in candidates.items():
        child_time_left = time_left - (len(path) + 1) # add 1 for time to turn valve

        # wouldn't have gotten to this valve in time
        if child_time_left < 0:
            continue

        # get combinations for all child valves
        new_activated_valve_set = activated_valve_set.copy()
        new_activated_valve_set.add(candidate)
        child_combinations = get_possible_combinations_1(shortest_paths, candidate, child_time_left, new_activated_valve_set)

        # add this valve to total list of combinations, or this valve and its child combinations
        if len(child_combinations) == 0:
            combinations.append([(candidate, child_time_left)])
        else:
            for child_combination in child_combinations:
                combinations.append([(candidate, child_time_left)] + child_combination)

    return combinations


if __name__ == "__main__":
    data = load_data("day-16-input.txt")

    # parse graph information from input
    valve_flow_rates = {}
    valve_connections = {}
    for line in data:
        valve = line[6:8]
        connections = line[23:]
        connections = connections.replace('valves', 'valve').replace(
            'tunnels', 'tunnel').replace('leads', 'lead')
        flow_rate, valves = connections.split('; tunnel lead to valve ')

        valve_flow_rates[valve] = int(flow_rate)
        valve_connections[valve] = valves.split(', ')

    # create vertex and edge sets
    vertex_set = set(valve_flow_rates.keys())
    edge_set = set()
    for source, destination_list in valve_connections.items():
        for destination in destination_list:
            if (source, destination) not in edge_set and (destination, source) not in edge_set:
                edge_set.add((source, destination))

    # compute shortest path between every possible vertex pair
    shortest_paths = {source_vertex: dijkstra(source_vertex, vertex_set, edge_set) for source_vertex in vertex_set}

    # track every possible ordering of valve openings
    time_left = TOTAL_TIME
    current_location = STARTING_VERTEX
    activated_valve_set = set()

    # get every possible order we could release the valves in
    combinations_1 = get_possible_combinations_1(shortest_paths, current_location, time_left, activated_valve_set)
    pressures_1 = [
        sum([valve_flow_rates[valve] * time_left for valve, time_left in combination])
        for combination in combinations_1
    ]
    answer_1 = max(pressures_1)

    # TODO complete part 2
    answer_2 = None

    print("Answer 1:")
    print(answer_1)
    print()
    print("Answer 2:")
    print(answer_2)
    print()
