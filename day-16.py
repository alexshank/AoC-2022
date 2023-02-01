from helpers import load_data

MAX_DISTANCE = 100_000 # at start of dijsktra, everything is very far away
NO_PRIOR = -1			 		 # at start of dijstra, each vertex has no path back to source
STARTING_VALVE = 'AA'  # starting vertex for given problem

# util functions for Dijsktra's algorithm
def closest_unvisted_vertex(distances, visited):
	min_distance = MAX_DISTANCE 
	min_vertex = None	# there could be no reachable, unvisited vertices
	for v in vertex_set:
		if distances[v] < min_distance and visited[v] == False:
			min_distance = distances[v]
			min_vertex = v
	return min_vertex

def get_incident_edges(vertex, edge_set):
	result = []
	for e in edge_set:
		if e[0] == vertex:
			result.append((e[1], e[2]))
		elif e[1] == vertex:
			result.append((e[0], e[2]))
	return result

def build_shortest_path(priors, source_vertex, destination_vertex):
	path = [destination_vertex]
	prior_vertex = priors[destination_vertex]
	while prior_vertex != NO_PRIOR:
		path.append(prior_vertex)
		prior_vertex = priors[prior_vertex]
	path.reverse()

	# return None if there isn't a path from source to destination
	if len(path) < 2 or path[0] != source_vertex:
		return None
	else:
		return path

# compute shortest paths and shortest distances to every vertex in graph
def dijkstra(source, vertex_set, edge_set):
	distances = {vertex: MAX_DISTANCE for vertex in vertex_set}
	distances[source] = 0
	visited = {vertex: False for vertex in vertex_set}
	priors = {vertex: NO_PRIOR for vertex in vertex_set}

	# algorithm must consider all vertices to complete
	for _ in range(len(vertex_set)):
		u = closest_unvisted_vertex(distances, visited)

		# break early if there's no reachable, reachable vertices
		if u == None: break

		visited[u] = True
		for v, edge_weight in get_incident_edges(u, edge_set):
			if (visited[v] == False and distances[v] > distances[u] + edge_weight):
				distances[v] = distances[u] + edge_weight
				priors[v] = u

	return {destination: (build_shortest_path(priors, source, destination), distances[destination]) for destination in vertex_set}


if __name__ == "__main__":
	data = load_data("day-16-test-input.txt")

	valve_flow_rates = {}
	valve_connections = {}
	for d in data:
		valve = d[6:8]
		d = d[23:]
		d = d.replace('valves', 'valve').replace('tunnels', 'tunnel').replace('leads', 'lead')
		first, second = d.split('; tunnel lead to valve ')

		# data structures to hold parsed info
		valve_flow_rates[valve] = int(first)
		valve_connections[valve] = second.split(', ')

	# create vertex and edge sets
	vertex_set = set(valve_flow_rates.keys())
	edge_set = set()
	for source, destination_list in valve_connections.items():
		for destination in destination_list:
			if (source, destination, 1) not in edge_set and (destination, source, 1) not in edge_set:
				edge_set.add((source, destination, 1))

	# print starting shortest paths
	print(dijkstra(STARTING_VALVE, vertex_set, edge_set))
		


