from helpers import load_data
from itertools import permutations as nPermuteK # avoid naming conflicts

MAX_DISTANCE = 100_000      # at start of dijsktra, everything is very far away
NO_PRIOR = -1			    # at start of dijstra, each vertex has no path back to source
TOTAL_TIME = 30             # problem runs for the given number of time steps
STARTING_VERTEX = 'AA'      # problem always starts here, regardless of data
ELEPHANT_TEACHING_TIME = 4  # we need to spend time teaching the elephant before it helps us


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


# get every possible order we could release the valves in, recursively
def get_possible_combinations_2(shortest_paths, elephant_location, elephant_available_at, human_location, human_available_at, time_left, activated_valve_set):
    # determine which actions could be taken
    elephant_available = elephant_available_at >= time_left
    human_available = human_available_at >= time_left

    if elephant_available and human_available:

        # next valves that could be opened by elephant
        elephant_candidates = {
            destination: path
            for destination, path in shortest_paths[elephant_location].items()
            if valve_flow_rates[destination] != 0 and destination not in activated_valve_set
        }

        # next valves that could be opened by elephant
        human_candidates = {
            destination: path
            for destination, path in shortest_paths[human_location].items()
            if valve_flow_rates[destination] != 0 and destination not in activated_valve_set
        }

        # base case: no candidates left for either human or elephant
        if len(elephant_candidates) == 0:
            return []

        unactivated_valves = [valve for valve in elephant_candidates.keys()]

        if len(unactivated_valves) < 2:
            # print()
            if len(list(elephant_candidates.items())[0][1]) < len(list(human_candidates.items())[0][1]):
                # print('elephant closer than human')

                child_elephant_location = list(elephant_candidates.items())[0][0]
                child_elephant_path = list(elephant_candidates.items())[0][1]

                # update time variables
                child_elephant_available_at = time_left - (len(child_elephant_path) + 1)

                # wouldn't have gotten to valve in time
                if child_elephant_available_at < 0:
                    # print('returning empty in elephant closer...')
                    return []
                else:
                    return [[(child_elephant_location, child_elephant_available_at)]]


            else:
                # print('human equal or closer than elephant')

                child_human_location = list(human_candidates.items())[0][0]
                child_human_path = list(human_candidates.items())[0][1]

                # update time variables
                child_human_available_at = time_left - (len(child_human_path) + 1)

                # wouldn't have gotten to valve in time
                if child_human_available_at < 0:
                    # print('returning empty in human closer...')
                    return []
                else:
                    return [[(child_human_location, child_human_available_at)]]


        permutations = list(nPermuteK(unactivated_valves, 2))
        # print(permutations)

        # recursively get all the permutations from the candidate valves
        combinations = []
        count = 0
        for child_elephant_location, child_human_location in permutations:

            # TODO printing progress of real input data
            if len(permutations) == 210:
                count += 1
                print(f"Getting combinations for loop {count} out of 210")

            # update time variables
            child_elephant_available_at = time_left - (len(elephant_candidates[child_elephant_location]) + 1)
            child_human_available_at = time_left - (len(human_candidates[child_human_location]) + 1)
            child_time_left = max(child_elephant_available_at, child_human_available_at)

            # wouldn't have gotten to any valve in time
            if child_time_left < 0:
                # print('continuing...')
                continue

            # get combinations for all child valves
            new_activated_valve_set = activated_valve_set.copy()
            new_activated_valve_set.add(child_elephant_location)
            new_activated_valve_set.add(child_human_location)

            # if len(new_activated_valve_set) == len(shortest_paths.keys()):
            #     combinations.append([(child_elephant_location, child_elephant_available_at)])
            #     combinations.append([(child_human_location, child_human_available_at)])
            #     continue


            child_combinations = get_possible_combinations_2(shortest_paths, child_elephant_location, child_elephant_available_at, child_human_location, child_human_available_at, child_time_left, new_activated_valve_set)

            # add these valves to total list of combinations, or these valve plus their child combinations
            if len(child_combinations) == 0:
                combinations.append([(child_elephant_location, child_elephant_available_at), (child_human_location, child_human_available_at)])
                # combinations.append([])
            else:
                for child_combination in child_combinations:
                    combinations.append([(child_elephant_location, child_elephant_available_at), (child_human_location, child_human_available_at)] + child_combination)

        return combinations

    elif elephant_available:

        # next valves that could be opened by elephant
        elephant_candidates = {
            destination: path
            for destination, path in shortest_paths[elephant_location].items()
            if valve_flow_rates[destination] != 0 and destination not in activated_valve_set
        }

        # base case: no candidates left for either human or elephant
        if len(elephant_candidates) == 0:
            return []

        # recursively get all the permutations from the candidate valves
        combinations = []
        for child_elephant_location, child_path in elephant_candidates.items():

            # update time variables
            child_elephant_available_at = time_left - (len(child_path) + 1)
            child_human_available_at = human_available_at
            child_time_left = max(child_elephant_available_at, child_human_available_at)

            # wouldn't have gotten to any valve in time
            if child_time_left < 0:
                # print('continuing in elephant...')
                continue

            # get combinations for all child valves
            new_activated_valve_set = activated_valve_set.copy()
            new_activated_valve_set.add(child_elephant_location)
            child_combinations = get_possible_combinations_2(shortest_paths, child_elephant_location, child_elephant_available_at, human_location, human_available_at, child_time_left, new_activated_valve_set)

            # add these valves to total list of combinations, or these valve plus their child combinations
            if len(child_combinations) == 0:
                combinations.append([(child_elephant_location, child_elephant_available_at)])
            else:
                for child_combination in child_combinations:
                    combinations.append([(child_elephant_location, child_elephant_available_at)] + child_combination)

        return combinations


    elif human_available:

        # next valves that could be opened by human
        human_candidates = {
            destination: path
            for destination, path in shortest_paths[human_location].items()
            if valve_flow_rates[destination] != 0 and destination not in activated_valve_set
        }

        # base case: no candidates left for either human or elephant
        if len(human_candidates) == 0:
            return []

        # recursively get all the permutations from the candidate valves
        combinations = []
        for child_human_location, child_path in human_candidates.items():
            # update time variables
            child_elephant_available_at = elephant_available_at 
            child_human_available_at = time_left - (len(child_path) + 1)
            child_time_left = max(child_elephant_available_at, child_human_available_at)

            # wouldn't have gotten to any valve in time
            if child_time_left < 0:
                # print('continuing in human...')
                continue

            # get combinations for all child valves
            new_activated_valve_set = activated_valve_set.copy()
            new_activated_valve_set.add(child_human_location)
            child_combinations = get_possible_combinations_2(shortest_paths, elephant_location, elephant_available_at, child_human_location, child_human_available_at, child_time_left, new_activated_valve_set)

            # add these valves to total list of combinations, or these valve plus their child combinations
            if len(child_combinations) == 0:
                combinations.append([(child_human_location, child_human_available_at)])
            else:
                for child_combination in child_combinations:
                    combinations.append([(child_human_location, child_human_available_at)] + child_combination)

        return combinations

    else:
        raise Exception('This case should never happen.')


if __name__ == "__main__":
    data = load_data("day-16-test-input.txt")

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

    # get every possible order we could release the valves in with elephant's help
    time_left = TOTAL_TIME - ELEPHANT_TEACHING_TIME
    elephant_location = current_location
    elephant_available_at = time_left
    human_available_at = time_left
    human_location = current_location

    combinations_2 = get_possible_combinations_2(shortest_paths, elephant_location, elephant_available_at, human_location, human_available_at, time_left, activated_valve_set)

    print(len(combinations_2))

    print()
    for c in combinations_2:
        if ('EE', 15) in c: # and ('CC', 17) in c:
            print(c)
    print()

    pressures_2 = [
        sum([valve_flow_rates[valve] * time_left for valve, time_left in combination])
        for combination in combinations_2
    ]
    answer_2 = max(pressures_2)

    print()
    print('Best found:')
    print(combinations_2[pressures_2.index(max(pressures_2))])

    # test answer should be:
    print()
    print('Answer should be:')
    expected = [('DD', 24), ('JJ', 23), ('BB', 19), ('HH', 19), ('CC', 17), ('EE', 15)]
    print(expected)
    print(sum([valve_flow_rates[valve] * time_left for valve, time_left in expected]))
    print()

    # print results
    print("Answer 1:")
    print(answer_1)
    print()
    print("Answer 2:")
    print(answer_2)
    print()
