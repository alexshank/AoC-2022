from helpers import load_data

MAX_DISTANCE = 100_000      # at start of dijsktra, everything is very far away
NO_PRIOR = -1			    # at start of dijstra, each vertex has no path back to source
TOTAL_TIME = 30             # problem runs for the given number of time steps
STARTING_VERTEX = 'AA'      # problem always starts here, regardless of data
ELEPHANT_TEACHING_TIME = 4  # we need to spend time teaching the elephant before it helps us

# TODO could probably move all the standard algorithms I implementationed for AoC to a helper library

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
    def __init__(self, valve_pressures, all_candidates, location, time_left, opened_valves, action):
        self.valve_pressures = valve_pressures
        self.all_candidates = all_candidates
        self.candidates = {k: v for k, v in all_candidates[time_left][location].items() if k not in opened_valves}
        self.location = location
        self.time_left = time_left
        self.opened_valves = opened_valves
        self.action = action


    def get_child_states(self):
        result = []
        for child_valve, child_path in self.candidates.items():
            child_time_left = self.time_left - (len(child_path) + 1) # add 1 for time to turn valve

            child_opened_valve_set = self.opened_valves.copy()
            child_opened_valve_set.add(child_valve)

            child_action = (child_valve, child_time_left)
            result.append(StatePart1(self.valve_pressures, self.all_candidates, child_valve, child_time_left, child_opened_valve_set, child_action))
        return result


    def get_max_score(self):
        current_score = 0 if self.action == None else self.valve_pressures[self.action[0]] * self.action[1]

        child_states = self.get_child_states()
        if len(child_states) == 0:
            return current_score

        return max([current_score + child_state.get_max_score() for child_state in child_states])


# TODO likely don't need so much state passed around
# TODO something like DFS of the state tree would likely be MUCH faster. tree structure may need to be modified for that, though
class StatePart2:
    def __init__(self, valve_pressures, all_candidates, elephant_location, elephant_available_at, human_location, human_available_at, time_left, opened_valves, action):
        self.all_candidates = all_candidates
        self.elephant_location = elephant_location
        self.elephant_available_at = elephant_available_at
        self.human_location = human_location
        self.human_available_at = human_available_at
        self.time_left = time_left
        self.opened_valves = opened_valves
        self.action = action
        self.valve_pressures = valve_pressures


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
            result.append(StatePart2(self.valve_pressures, self.all_candidates, child_elephant_valve, child_elephant_available_at, self.human_location, self.human_available_at, child_time_left, child_opened_valve_set, elephant_action))

        # child states from the human taking action
        for child_human_valve, child_path in self.get_human_candidates().items():
            child_human_available_at = self.time_left - (len(child_path) + 1)
            child_time_left = max(self.elephant_available_at, child_human_available_at)

            child_opened_valve_set = self.opened_valves.copy()
            child_opened_valve_set.add(child_human_valve)

            human_action = (child_human_valve, child_human_available_at)
            result.append(StatePart2(self.valve_pressures, self.all_candidates, self.elephant_location, self.elephant_available_at, child_human_valve, child_human_available_at, child_time_left, child_opened_valve_set, human_action))

        return result


    # TODO should attempt some caching, this seems to be on the right track. DFS possibly on our tree of states? Actually contract the graph?
    # TODO don't actually store the paths between each node, just the distances?
    def get_max_score(self):

        # TODO this isn't correctly caching
        cache_key = f"{self.elephant_location}-{self.human_location}-{self.time_left}-{self.opened_valves}-{elephant_available_at}-{human_available_at}-{self.action}"
        if cache_key in score_cache:
            return score_cache[cache_key]


        # root node / state is the only one that doesn't contain a valve opening action
        current_score = 0 if self.action == None else self.valve_pressures[self.action[0]] * self.action[1]

        child_states = self.get_child_states()
        if len(child_states) == 0:
            return current_score

        my_max = 0
        for i, child_state in enumerate(child_states):

            if self.action == None:
                print(f"{i + 1} of {len(child_states)}")

            temp = current_score + child_state.get_max_score()
            if temp > my_max:
                my_max = temp

        # result = max([current_score + child_state.get_max_score() for child_state in child_states])
        # score_cache[cache_key] = result
        score_cache[cache_key] = my_max
        # return result
        return my_max


# TODO move this out of global space
score_cache = {}

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
    state_part_1 = StatePart1(valve_flow_rates, all_candidates, STARTING_VERTEX, TOTAL_TIME, set(), None)
    answer_1 = state_part_1.get_max_score()

    # part 1: answer is 1915. no caching necessary
    print(f"Answer 1: {answer_1}")

    # get every possible order we could release the valves in with elephant's help
    time_left = elephant_available_at = human_available_at = TOTAL_TIME - ELEPHANT_TEACHING_TIME
    state_part_2 = StatePart2(valve_flow_rates, all_candidates, STARTING_VERTEX, elephant_available_at, STARTING_VERTEX, human_available_at, time_left, set(), None)
    answer_2 = state_part_2.get_max_score()

    # part 2: answer is 2772. took ~8 minutes to run with caching
    print(f"Answer 2: {answer_2}")

