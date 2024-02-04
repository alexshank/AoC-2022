from helpers import load_data
from math import ceil
import time

# TODO could make more efficient with an array data structure?
RESOURCE_INDICES = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
RESOURCE_MASKS = {'geode': (1, 0, 0, 0), 'obsidian': (0, 1, 0, 0), 'clay': (0, 0, 1, 0), 'ore': (0, 0, 0, 1)}
TOTAL_TIME = 24

# various caches for memoizing recursive calls
cache = {}	
type_cache = {}	
time_cache = {}	
best_cache = {i: 0 for i in range(25)}

# the triangle numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(25)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, 25)]


# determine the next time that a robot could be built based on current robots and resources
def time_to_build_robot(blueprint, robot_resource_type, time_left, resource_counts, robot_counts):
	# cache recursive results
	cache_key = f"{robot_resource_type}-{time_left}-{resource_counts}-{robot_counts}"
	if cache_key in time_cache:
		return time_cache[cache_key]

	robot_blueprint = blueprint[robot_resource_type]

	# if already have the resources to build robot, return early
	if lessThanOrEqualT(robot_blueprint, resource_counts):
		time_cache[cache_key] = time_left - 1
		return time_left - 1
	
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {i for i in range(4) if robot_blueprint[i] > 0 and robot_blueprint[i] > resource_counts[i]}
	obtainable_resource_types = {i for i in range(4) if robot_counts[i] > 0}
	if not required_resource_types.issubset(obtainable_resource_types):
		time_cache[cache_key] = None
		return None
	
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = subT(robot_blueprint, resource_counts)
	time_deltas = [
		ceil(resource_differences[required_resource] / robot_counts[required_resource])
		for required_resource 
		in required_resource_types
	]

	result = time_left - max(time_deltas)
	time_cache[cache_key] = result
	return result


"""
tuple utility functions
"""
def addT(t1, t2):
	return tuple(x + y for x, y in zip(t1, t2))


def subT(t1, t2):
	return tuple(x - y for x, y in zip(t1, t2))


def scaleT(t1, scalar):
	return tuple(x * scalar for x in t1)


def lessThanOrEqualT(t1, t2):
	return all(x <= y for x, y in zip(t1, t2))


# recursively run simulation and return the maximum number of geodes that could be mined
def get_max_geodes(blueprint, time_left, resource_counts, robot_counts):
	# TODO make key smaller, also maybe include blueprint?
	# cache recursive results
	cache_key = f"{time_left}-{resource_counts}-{robot_counts}"
	if cache_key in cache:
		return cache[cache_key], type_cache[cache_key]

	# base case: we've run out of time, return the geodes collected at this final time step
	if time_left == 1:
		result = robot_counts[0]
		cache[cache_key] = result
		type_result = [f'Minute {TOTAL_TIME - time_left + 1}: time left is 1, returning {result}']
		type_cache[cache_key] = type_result
		return result, type_result

	# compute absolute upper bound of geodes we could get from this current state
	# trim this branch of the search, since it clearly will not beat the current best
	current_geodes = resource_counts[0]
	geode_upper_bound = current_geodes + (time_left * robot_counts[0]) + TRIANGULAR_NUMBERS[time_left - 1]
	if geode_upper_bound < best_cache[time_left]:
		result = 0
		cache[cache_key] = result
		type_result = [f'Minute {TOTAL_TIME - time_left + 1}: dead branch time left {time_left}, returning {result} geodes']
		type_cache[cache_key] = type_result
		return result, type_result

	all_child_geodes = []
	all_child_geodes_type = []
	for robot_resource_type, tuple_mask in RESOURCE_MASKS.items():
		# returns None if not possible to build
		child_time_left = time_to_build_robot(blueprint, robot_resource_type, time_left, resource_counts, robot_counts)

		# if impossible to build the robot type at all or before time's up, continue
		if child_time_left == None or child_time_left < 2: # TODO should be 2?
			continue

		# add resources, new robot isn't available to mine resources until ((next time step) + 1)
		child_resources = scaleT(robot_counts, (time_left - child_time_left) + 1)
		resource_counts = addT(resource_counts, child_resources)
		robot_counts = addT(robot_counts, tuple_mask)

		# remove the resources needed for newly built robot
		resource_counts = subT(resource_counts, blueprint[robot_resource_type])

		# make recursive call
		child_geodes, child_type = get_max_geodes(blueprint, child_time_left - 1, resource_counts, robot_counts)
		all_child_geodes.append(child_geodes)
		temp = [f'Minute {TOTAL_TIME - time_left + 1}: will build {robot_resource_type} robot at {TOTAL_TIME - (child_time_left - 1)}, now have {robot_counts} robots, and {resource_counts} resources, with {current_geodes} geodes, then produce {child_geodes} geodes']
		temp.extend(child_type)
		all_child_geodes_type.append(temp)

		# add back resources needed for newly built robot
		resource_counts = addT(resource_counts, blueprint[robot_resource_type])

		# remove robot that was just built
		robot_counts = subT(robot_counts, tuple_mask)

		# remove resources that were mined this time step
		resource_counts = subT(resource_counts, child_resources)


	# TODO if no options available, should be current geodes + geode_robots * time_left
	if len(all_child_geodes) == 0:
		result = current_geodes + robot_counts[0] * time_left
		cache[cache_key] = result
		result_type = [f'Minute {TOTAL_TIME - time_left + 1}: nothing to build at {TOTAL_TIME - time_left}, returning {result} geodes']
		type_cache[cache_key] = result_type
	else:
		result = max(all_child_geodes)
		cache[cache_key] = result
		result_type_index = max(range(len(all_child_geodes)), key=all_child_geodes.__getitem__)
		result_type = all_child_geodes_type[result_type_index]
		type_cache[cache_key] = result_type

	# update the most geodes we've ever found at this time step
	if result > best_cache[time_left]:
		best_cache[time_left] = result

	return result, result_type

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

			blueprint[robot_type] = [0 for i in range(4)]
			for resource_cost in resource_costs:
				cost, resource_type = resource_cost.split(" ")
				blueprint[robot_type][RESOURCE_INDICES[resource_type]] = int(cost)
			blueprint[robot_type] = tuple(blueprint[robot_type])

		blueprints.append(blueprint)
	return blueprints

	
if __name__ == "__main__":
	lines = load_data("day-19-test-input.txt")
	blueprints = build_blueprint_dictionaries(lines)

	start_time = time.time()
	print(f"Start time: {start_time}")
	print()

	answer_1 = 0
	for i, blueprint in enumerate(blueprints):
		print(f"Blueprint {i + 1} of {len(blueprints)}.")
		cache = {}	
		time_cache = {}	
		best_cache = {i: 0 for i in range(25)}

		resource_counts = (0, 0, 0, 0)
		robot_counts = (0, 0, 0, 1)

		max_geodes, best_path = get_max_geodes(blueprint, TOTAL_TIME, resource_counts, robot_counts)
		print(f"Geodes for blueprint {i + 1}: {max_geodes}")
		print(f"Path:")
		for event in best_path:
			print(event)
		print()

		# TODO this shows we aren't propogating child results up properly in the recursive calls
		# for k, v in best_cache.items():
		# 	print(f"Time left {k}: {v}")

		answer_1 += (i + 1) * max_geodes

		# TODO remove
		break
	
	end_time = time.time()
	print(f"\nEnd time: {end_time}")
	print()

	elapsed_time = end_time - start_time
	print(f"Elapsed time: {elapsed_time} seconds.")
	print()

	print(f"Answer 1: {answer_1}")
	print()


