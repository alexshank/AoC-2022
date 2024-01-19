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


class StatePart1:
    def __init__(self, all_candidates, location, time_left, opened_valves):
        self.all_candidates = all_candidates
        self.candidates = {k: v for k, v in all_candidates[time_left][location].items() if k not in opened_valves}
        self.location = location
        self.time_left = time_left
        self.opened_valves = opened_valves


    def get_child_states(self):
        result = []
        for child_valve, child_path in self.candidates.items():
            child_time_left = self.time_left - (len(child_path) + 1) # add 1 for time to turn valve

            child_opened_valve_set = self.opened_valves.copy()
            child_opened_valve_set.add(child_valve)

            result.append(StatePart1(self.all_candidates, child_valve, child_time_left, child_opened_valve_set))
        return result


    def get_combinations(self):
        start = [(self.location, self.time_left)] if self.location != 'AA' else []
        child_states = self.get_child_states()

        if len(child_states) == 0:
            return [start]

        result = []
        for child_state in child_states:
            child_state_combinations = child_state.get_combinations()
            
            for child_state_combination in child_state_combinations:
                result.append(start + child_state_combination)
        return result


class StatePart2:
    def __init__(self, all_candidates, elephant_location, elephant_available_at, human_location, human_available_at, time_left, opened_valves, action):
        self.all_candidates = all_candidates
        self.elephant_location = elephant_location
        self.elephant_available_at = elephant_available_at
        self.human_location = human_location
        self.human_available_at = human_available_at
        self.time_left = time_left
        self.opened_valves = opened_valves
        self.action = action


    def get_elephant_candidates(self):
        if self.elephant_available_at < self.time_left:
            return {}

        return {k: v for k, v in all_candidates[self.time_left][self.elephant_location].items() if k not in self.opened_valves}


    def get_human_candidates(self):
        if self.human_available_at < self.time_left:
            return {}

        return {k: v for k, v in all_candidates[self.time_left][self.human_location].items() if k not in self.opened_valves}


    def get_child_states(self):
        result = []

        # child states from the elephant taking action
        for child_elephant_valve, child_path in self.get_elephant_candidates().items():
            child_elephant_available_at = self.time_left - (len(child_path) + 1)
            child_time_left = max(child_elephant_available_at, self.human_available_at)

            child_opened_valve_set = self.opened_valves.copy()
            child_opened_valve_set.add(child_elephant_valve)

            elephant_action = (child_elephant_valve, child_elephant_available_at)
            result.append(StatePart2(self.all_candidates, child_elephant_valve, child_elephant_available_at, self.human_location, self.human_available_at, child_time_left, child_opened_valve_set, elephant_action))

        # child states from the human taking action
        for child_human_valve, child_path in self.get_human_candidates().items():
            child_human_available_at = self.time_left - (len(child_path) + 1)
            child_time_left = max(self.elephant_available_at, child_human_available_at)

            child_opened_valve_set = self.opened_valves.copy()
            child_opened_valve_set.add(child_human_valve)

            human_action = (child_human_valve, child_human_available_at)
            result.append(StatePart2(self.all_candidates, self.elephant_location, self.elephant_available_at, child_human_valve, child_human_available_at, child_time_left, child_opened_valve_set, human_action))

        return result


    # TODO shouldn't find the actual highest combination, just find the highest score
    def get_combinations(self):
        # root node / state is the only one that doesn't contain a valve opening action
        start = [] if self.action == None else [self.action]
        child_states = self.get_child_states()

        if len(child_states) == 0:
            return [start]

        result = []
        for child_state in child_states:
            child_state_combinations = child_state.get_combinations()
            
            for child_state_combination in child_state_combinations:
                result.append(start + child_state_combination)

        return result


# get every possible order we could release the valves in, recursively
def get_possible_combinations_2(all_candidates, shortest_paths, elephant_location, elephant_available_at, human_location, human_available_at, time_left, activated_valve_set):
    # determine which actions could be taken
    elephant_available = elephant_available_at >= time_left
    human_available = human_available_at >= time_left

    if len(activated_valve_set) == len(shortest_paths.keys()):
        raise Exception('All valves already opened')

    if elephant_available and human_available:

        elephant_candidates = {k: v for k, v in all_candidates[time_left][elephant_location].items() if k not in activated_valve_set}
        human_candidates = {k: v for k, v in all_candidates[time_left][human_location].items() if k not in activated_valve_set}

        # TODO elephant and human could have different number of candidates now
        # TODO just build all the recursive calls here, then handle the list joining below
        if len(elephant_candidates) > 0 and len(human_candidates) > 0:
            pass
        elif len(elephant_candidates) > 0:
            pass
        elif len(human_candidates) > 0:
            pass
        # TODO put back
        # else:
        #     raise Exception('This should not have been possible.')


        # base case: no candidates left for either human or elephant
        if len(elephant_candidates) == 0:
            return []
        elif len(elephant_candidates) == 1:

            # TODO just try both, even if one is obviously further away

            if len(list(elephant_candidates.items())[0][1]) < len(list(human_candidates.items())[0][1]):
                # print('elephant closer than human')

                child_elephant_location = list(elephant_candidates.items())[0][0]
                child_elephant_path = list(elephant_candidates.items())[0][1]

                # update time variables
                child_elephant_available_at = time_left - (len(child_elephant_path) + 1)
                return [[(child_elephant_location, child_elephant_available_at)]]


            else:
                # print('human equal or closer than elephant')

                child_human_location = list(human_candidates.items())[0][0]
                child_human_path = list(human_candidates.items())[0][1]

                # update time variables
                child_human_available_at = time_left - (len(child_human_path) + 1)
                return [[(child_human_location, child_human_available_at)]]


        # TODO shouldn't convert to a list, just use the iterator properly
        # TODO this should now become a product of the two candidate lists
        unactivated_valves = [valve for valve in elephant_candidates.keys()]
        permutations = list(nPermuteK(unactivated_valves, 2))
        # print(permutations)

        # recursively get all the permutations from the candidate valves
        combinations = []
        count = 0
        for child_elephant_location, child_human_location in permutations:

            # TODO printing progress of real input data
            if len(permutations) == 210:
                count += 1
                print(f"Getting combinations for root permuation {count} out of 210")

            # update time variables
            child_elephant_available_at = time_left - (len(elephant_candidates[child_elephant_location]) + 1)
            child_human_available_at = time_left - (len(human_candidates[child_human_location]) + 1)
            child_time_left = max(child_elephant_available_at, child_human_available_at)

            # get combinations for all child valves
            new_activated_valve_set = activated_valve_set.copy()
            new_activated_valve_set.add(child_elephant_location)
            new_activated_valve_set.add(child_human_location)

            child_combinations = get_possible_combinations_2(all_candidates, shortest_paths, child_elephant_location, child_elephant_available_at, child_human_location, child_human_available_at, child_time_left, new_activated_valve_set)

            # add these valves to total list of combinations, or these valve plus their child combinations
            start = [(child_elephant_location, child_elephant_available_at), (child_human_location, child_human_available_at)]
            if len(child_combinations) == 0:
                combinations.append(start)
            else:
                for child_combination in child_combinations:
                    combinations.append(start + child_combination)

        return combinations

    elif elephant_available:

        # next valves that could be opened by elephant
        elephant_candidates = {k: v for k, v in all_candidates[time_left][elephant_location].items() if k not in activated_valve_set}

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

            # get combinations for all child valves
            new_activated_valve_set = activated_valve_set.copy()
            new_activated_valve_set.add(child_elephant_location)
            child_combinations = get_possible_combinations_2(all_candidates, shortest_paths, child_elephant_location, child_elephant_available_at, human_location, human_available_at, child_time_left, new_activated_valve_set)

            # add these valves to total list of combinations, or these valve plus their child combinations
            start = [(child_elephant_location, child_elephant_available_at)]
            if len(child_combinations) == 0:
                combinations.append(start)
            else:
                for child_combination in child_combinations:
                    combinations.append(start + child_combination)

        return combinations


    elif human_available:

        # next valves that could be opened by human
        human_candidates = {k: v for k, v in all_candidates[time_left][human_location].items() if k not in activated_valve_set}

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
                continue

            # get combinations for all child valves
            new_activated_valve_set = activated_valve_set.copy()
            new_activated_valve_set.add(child_human_location)
            child_combinations = get_possible_combinations_2(all_candidates, shortest_paths, elephant_location, elephant_available_at, child_human_location, child_human_available_at, child_time_left, new_activated_valve_set)

            # add these valves to total list of combinations, or these valve plus their child combinations
            start = [(child_human_location, child_human_available_at)]
            if len(child_combinations) == 0:
                combinations.append(start)
            else:
                for child_combination in child_combinations:
                    combinations.append(start + child_combination)

        return combinations

    else:
        # TODO remove case after testing
        raise Exception('Elephant or human should always be available.')


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

    # compute all the possible movements between nonzero pressure valves at all timesteps
    # this lookup object saves many, many recursive list creations
    all_candidates = {}
    for i in range(30, 0, -1):
        all_candidates[i] = {}
        for location in shortest_paths.keys():
            all_candidates[i][location] = {
                destination: path
                for destination, path in shortest_paths[location].items()
                if valve_flow_rates[destination] != 0 and i - (len(path) + 1) > 0
            }

    # get every possible order we could release the valves in by ourselves
    state_part_1 = StatePart1(all_candidates, STARTING_VERTEX, TOTAL_TIME, set())
    combinations_1 = state_part_1.get_combinations()
    pressures_1 = [
        sum([valve_flow_rates[valve] * time_left for valve, time_left in combination])
        for combination in combinations_1
    ]
    answer_1 = max(pressures_1)

    # print result
    print(f"Answer 1: {answer_1}")

    # get every possible order we could release the valves in with elephant's help
    time_left = elephant_available_at = human_available_at = TOTAL_TIME - ELEPHANT_TEACHING_TIME
    state_part_2 = StatePart2(all_candidates, STARTING_VERTEX, elephant_available_at, STARTING_VERTEX, human_available_at, time_left, set(), None)
    combinations_2 = state_part_2.get_combinations()
    pressures_2 = [
        sum([valve_flow_rates[valve] * time_left for valve, time_left in combination])
        for combination in combinations_2
    ]
    answer_2 = max(pressures_2)

    # time_left = TOTAL_TIME - ELEPHANT_TEACHING_TIME
    # elephant_location = 'AA'
    # elephant_available_at = time_left
    # human_available_at = time_left
    # human_location = 'AA' 
    # combinations_2_old = get_possible_combinations_2(all_candidates, shortest_paths, elephant_location, elephant_available_at, human_location, human_available_at, time_left, set())
    # pressures_2_old = [
    #     sum([valve_flow_rates[valve] * time_left for valve, time_left in combination])
    #     for combination in combinations_2_old
    # ]
    # answer_2_old = max(pressures_2_old)

    # print result
    print(f"Answer 2: {answer_2}")
    # print(f"Answer 2 (old): {answer_2_old}")

    # combinations_2 = sorted(combinations_2, key=lambda x: ''.join(t[0] for t in x))
    # combinations_2_old = sorted(combinations_2_old, key=lambda x: ''.join(t[0] for t in x))


    # print(len(combinations_2)) 
    # print(len(combinations_2_old))

    # for i in range(len(combinations_2)):
    #     print(combinations_2[i])
    #     # print(combinations_2_old[i])
    #     # print()
