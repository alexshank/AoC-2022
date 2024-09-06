from helpers import load_data
from math import ceil
import time
from functools import lru_cache, reduce
from operator import mul
import multiprocessing
from collections import deque


# constants
RESOURCE_INDICES = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
RESOURCE_MASKS = {'geode': (1, 0, 0, 0), 'obsidian': (0, 1, 0, 0), 'clay': (0, 0, 1, 0), 'ore': (0, 0, 0, 1)}
START_TIME = 1
TOTAL_TIME = 24
# TOTAL_TIME = 32 # part 2


# the triangular numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(TOTAL_TIME + 1)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, TOTAL_TIME + 1)]


"""
tuple utility functions
"""
def addT(t1: tuple, t2: tuple):
	return (t1[0] + t2[0], t1[1] + t2[1], t1[2] + t2[2], t1[3] + t2[3])


def subT(t1: tuple, t2: tuple):
	return (t1[0] - t2[0], t1[1] - t2[1], t1[2] - t2[2], t1[3] - t2[3])


def scaleT(t1: tuple, scalar: int):
	return (t1[0] * scalar, t1[1] * scalar, t1[2] * scalar, t1[3] * scalar)


def lessThanOrEqualT(t1: tuple, t2: tuple):
	return t1[0] <= t2[0] and t1[1] <= t2[1] and t1[2] <= t2[2] and t1[3] <= t2[3]


def clampT(t1: tuple, t2: tuple):
	return (min(t1[0], t2[0]), min(t1[1], t2[1]), min(t1[2], t2[2]), min(t1[3], t2[3]))


# determine the next time that a robot could be built based on current robots and resources
@lru_cache(maxsize=None)
def time_to_build_robot(robot_cost, resource_counts, robot_counts):
	# if already have the resources to build robot, return early
	if lessThanOrEqualT(robot_cost, resource_counts):
		return 0
	
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {i for i in range(4) if robot_cost[i] > 0 and robot_cost[i] > resource_counts[i]}
	obtainable_resource_types = {i for i in range(4) if robot_counts[i] > 0}
	if not required_resource_types.issubset(obtainable_resource_types):
		return None
	
	# TODO likely a cleaner, integer way of doing this without ceiling function
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = subT(robot_cost, resource_counts)
	time_deltas = [
		ceil(resource_differences[required_resource] / robot_counts[required_resource])
		for required_resource 
		in required_resource_types
	]

	return max(time_deltas)


def get_max_robot_counts(blueprint):
	# TODO need to determine these maximums / sums more accurately
	# find the maximum number of each robot we would ever want
	# if we can only spend X ore per turn, we would never want X + 1 ore robots
	# this is the main thing that reduces our search space
	max_geode = 10_000
	max_obsidian = max([blueprint[resource_type][1] for resource_type in RESOURCE_TYPES])
	max_clay = max([blueprint[resource_type][2] for resource_type in RESOURCE_TYPES])
	max_ore = max([blueprint[resource_type][3] for resource_type in RESOURCE_TYPES])
	max_robot_counts = (max_geode, max_obsidian, max_clay, max_ore)
	return max_robot_counts


# runs logic via DFS queue
def breadth_first_search(blueprint):
	# help caching states by limiting max number of robots
	max_robot_counts = get_max_robot_counts(blueprint)

	# TODO should determine these more accurately
	# help caching states by limiting max number of resources
	max_resource_counts = {k: tuple(i * (TOTAL_TIME - k) for i in max_robot_counts) for k in range(0, TOTAL_TIME + 1)}

	# tracks most geodes found at each time step
	# gets compared to the max number of possible remaining geodes to reduce search space
	# if most geodes at time t is already more than theoretical max, skip searching that branch
	most_geodes_at_time = {i: 0 for i in range(TOTAL_TIME + 1)}

	# initialize resources and robots
	resource_counts = (0, 0, 0, 0)
	robot_counts = (0, 0, 0, 1)
	starting_state = (START_TIME, resource_counts, robot_counts)

	# actual BFS queue logic
	best_result = 0
	queue = deque([starting_state])
	seen_states = set()
	while queue:
		# grab next state off queue
		state = queue.popleft()
		time, resource_counts, robot_counts = state

		# exit early if end of simulation
		if time == TOTAL_TIME:
			# save best results up to this point and at this specific time (for caching)
			updated_resource_counts = addT(resource_counts, robot_counts)
			best_result = max(best_result, updated_resource_counts[0])
			most_geodes_at_time[time] = max(most_geodes_at_time[time], updated_resource_counts[0])
			continue

		# continue immediately if we've already seen this state
		if state in seen_states:
			continue
		else:
			seen_states.add(state)

		# compute absolute upper bound of geodes we could get from this current state
		# this assumes you could build one new geode robot at every remaining time step
		# trim this branch off the search, if it clearly will not beat the current best
		current_geodes = resource_counts[0]
		geode_upper_bound = current_geodes + ((TOTAL_TIME - time - 1) * robot_counts[0]) + TRIANGULAR_NUMBERS[TOTAL_TIME - time]
		if geode_upper_bound < most_geodes_at_time[time]:
			continue

		# possible robots that could be built and when
		robot_build_times = [
			(
				robot_resource_type,
				time_to_build_robot(blueprint[robot_resource_type], resource_counts, robot_counts)
			)
			for robot_resource_type
			in RESOURCE_MASKS.keys()
			if robot_counts[RESOURCE_INDICES[robot_resource_type]] < max_robot_counts[RESOURCE_INDICES[robot_resource_type]]
		]

		can_build_something_by_waiting = False
		for robot_resource_type, child_time_offset in robot_build_times:
			# if impossible to build the robot type at all or before time's up, continue
			# if robot built at time 24, it doesn't contribute any mining
			if child_time_offset == None or time + child_time_offset > TOTAL_TIME:
				continue
				
			# we can build something later if we just wait, meaning we should add a new state where we've simply waited this turn
			can_build_something_by_waiting = True

			# if the child offset is 0, build immediately and go to next state
			if child_time_offset == 0:
				child_resource_counts = addT(resource_counts, robot_counts)
				child_resource_counts = subT(child_resource_counts, blueprint[robot_resource_type])
				# TODO is clamp needed?
				child_resource_counts = clampT(child_resource_counts, max_resource_counts[time])

				# add new robot to counts
				child_robot_counts = addT(robot_counts, RESOURCE_MASKS[robot_resource_type])
				# TODO is clamp needed?
				child_robot_counts = clampT(child_robot_counts, max_robot_counts)

				# add new state to BFS queue
				queue.append((time + 1, child_resource_counts, child_robot_counts))

			else:
				# add resources, new robot isn't available to mine resources until end of this step
				newly_mined_resource_counts = scaleT(robot_counts, child_time_offset)
				child_resource_counts = addT(resource_counts, newly_mined_resource_counts)
				# TODO is clamp needed?
				child_resource_counts = clampT(child_resource_counts, max_resource_counts[time])

				# add new state to BFS queue
				queue.append((time + child_time_offset, child_resource_counts, robot_counts))

		updated_resource_counts = addT(resource_counts, robot_counts)

		# queue the state where we build nothing, but only if we can evenutally build SOMETHING by waiting
		if can_build_something_by_waiting:
			queue.append((time + 1, updated_resource_counts, robot_counts))

		# save best results up to this point and at this specific time (for caching)
		best_result = max(best_result, updated_resource_counts[0])
		most_geodes_at_time[time] = max(most_geodes_at_time[time], updated_resource_counts[0])

	return best_result


# returns array of dictionaries like blueprint['ore']['obsidian'] = 5
# i.e., this blueprint specifies that an ore robot needs 5 obsidian
def build_blueprint_dictionaries(lines):
	blueprints = []
	for line in lines:
		robots = line.split(" Each ")[1:]
		robots = [robot.replace(".", "") for robot in robots]
		blueprint = {resource_type: {resource_type: 0 for resource_type in RESOURCE_TYPES} for resource_type in RESOURCE_TYPES}
		for robot in robots:
			robot_type, resource_costs = robot.split(" robot costs ")
			resource_costs = resource_costs.split(' and ')

			blueprint[robot_type] = [0 for _ in range(4)]
			for resource_cost in resource_costs:
				cost, resource_type = resource_cost.split(" ")
				blueprint[robot_type][RESOURCE_INDICES[resource_type]] = int(cost)
			blueprint[robot_type] = tuple(blueprint[robot_type])

		blueprints.append(blueprint)
	return blueprints


def process_blueprint(i, blueprint):
	start_time = time.time()
	print(f"Blueprint {i + 1}:")

	# get max geodes that the blueprint could produce from simulation start
	max_geodes = breadth_first_search(blueprint)

	# compute relevant quality metric
	result = (i + 1) * max_geodes # part 1
	# result = max_geodes # part 2

	# view cache efficacy
	print(f"Robot build cache: {time_to_build_robot.cache_info()}") 

	# measure elapsed time for this blueprint
	end_time = time.time()
	elapsed_time = end_time - start_time
	print(f"Elapsed time: {elapsed_time} seconds.")
	print(f"Result: {result}\n")

	return result


# TODO chance we need to find a way to quickly evaulate if we'll NEVER produce a geode
# TODO somehow find the fastest way we could get to a single geode, maybe?
if __name__ == "__main__":
	overall_start_time = time.time()
	print(f"Start time: {overall_start_time}\n")

	# put blueprints in global namespace so we can cache methods
	lines = load_data("day-19-test-input.txt")
	blueprints = build_blueprint_dictionaries(lines)
	# BLUEPRINTS = BLUEPRINTS[:3] # part 2
	blueprints = [blueprints[0]] # TODO testing
	
	# sum up all the results
	results = [process_blueprint(i, blueprint) for i, blueprint in enumerate(blueprints)]
	answer = sum(results)
	# answer = reduce(mul, results) # part 2

	# part 1 (answer: 1127)
	# TODO answer 19656 too low for part 2
	# part 2 (answer: TODO)
	print(f"Answer: {answer}\n")

	# print overall run time
	overall_end_time = time.time()
	overall_elapsed_time = overall_end_time - overall_start_time
	print(f"Total elapsed time: {overall_elapsed_time} seconds.\n")

