from helpers import load_data

# TODO General idea: Create a graph where each node is an entire state of the problem.
# This would mean each node keeps a record of:
# - the current minute in the simulation
#	- where every blizzard is currently located
# - where the traveler is currently located
# At every minute, we'll compute the next states/spaces we could move to
# Each potential state is added to the graph by a directed edge coming from the current node
# Finally, we run BFS on the graph, with the terminating condition being the traveler
# reaching the end coordinate
# Ideally this is fast enough for the given input size
# An important point: We don't have to create the graph and then traverse it. We can
# just create the new nodes as we are running BFS. This limits the runtime to 
# that of BFS (which is O(V+E)).

if __name__ == "__main__":
	data = load_data("day-24-test-input.txt")
	print(data)


