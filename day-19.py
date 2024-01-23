from helpers import load_data
from math import ceil
import time

# TODO could make more efficient with an array data structure?
RESOURCE_INDICES = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
RESOURCE_MASKS = {'geode': (1, 0, 0, 0), 'obsidian': (0, 1, 0, 0), 'clay': (0, 0, 1, 0), 'ore': (0, 0, 0, 1)}
TOTAL_TIME = 24

# TODO move cache out of global space
cache = {}	
time_cache = {}	
best_cache = {i: 0 for i in range(25)}

# the triangle numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(25)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, 25)]


# TODO may benefit from caching as well
def time_to_build_robot(blueprint, robot_resource_type, time_left, resource_counts, robot_counts):
	# cache recursive results
	cache_key = f"{robot_resource_type}-{time_left}-{resource_counts}-{robot_counts}"
	if cache_key in time_cache:
		return time_cache[cache_key]

	robot_blueprint = blueprint[robot_resource_type]

	# if already have the resources to build robot, return early
	if robot_blueprint <= resource_counts:
		time_cache[cache_key] = time_left - 1
		return time_left - 1
	
	# TODO should use indices instead of word keys
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {i for i in range(4) if robot_blueprint[i] > 0 and robot_blueprint[i] > resource_counts[i]}
	obtainable_resource_types = {i for i in range(4) if robot_counts[i] > 0}
	if obtainable_resource_types < required_resource_types:
		time_cache[cache_key] = None
		return None
	
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = tuple([x - y for x, y in zip(robot_blueprint, resource_counts)])
	time_deltas = [
		ceil(resource_differences[required_resource] / robot_counts[required_resource])
		for required_resource 
		in required_resource_types
	]
	result = time_left - max(time_deltas)
	time_cache[cache_key] = result
	return result


# recursively run simulation and return the maximum number of geodes that could be mined
def get_max_geodes(blueprint, time_left, resource_counts, robot_counts):
	# TODO make key smaller, also maybe include blueprint?
	# cache recursive results
	cache_key = f"{time_left}-{resource_counts}-{robot_counts}"
	if cache_key in cache:
		return cache[cache_key]

	# base case: we've run out of time, return the geodes collected at this final time step
	if time_left == 1:
		result = robot_counts[0]
		cache[cache_key] = result
		return result

	# TODO where should this check actually occur?
	# compute absolute upper bound of geodes we could get
	current_geodes = resource_counts[0]
	geode_upper_bound = current_geodes + (time_left * robot_counts[0]) + TRIANGULAR_NUMBERS[time_left - 1]
	if geode_upper_bound < best_cache[time_left]:
		result = 0 # TODO just say we got zero geodes from this state. better way to handle?
		cache[cache_key] = result
		return result

	all_child_geodes = []
	for robot_resource_type, tuple_mask in RESOURCE_MASKS.items():
		# returns None if not possible to build
		child_time_left = time_to_build_robot(blueprint, robot_resource_type, time_left, resource_counts, robot_counts)

		# if impossible to build the robot type at all or before time's up, continue
		if child_time_left == None or child_time_left < 1:
			continue

		# TODO may be innefficient to return whole new object in the += call?
		# add resources, new robot isn't available to mine resources until next time step 
		resource_counts += robot_counts * (time_left - child_time_left) 
		robot_counts += tuple_mask

		# remove the resources needed for newly built robot
		resource_counts = tuple([x - y for x, y in zip(resource_counts, blueprint[robot_resource_type])])

		# make recursive call
		child_geodes = get_max_geodes(blueprint, child_time_left, resource_counts, robot_counts)
		all_child_geodes.append(child_geodes)

		# add back resources needed for newly built robot
		resource_counts += blueprint[robot_resource_type]

		# remove robot that was just built
		robot_counts = tuple([x - y for x, y in zip(robot_counts, tuple_mask)])

		# remove resources that were mined this time step
		resource_counts = tuple([x - y for x, y in zip(resource_counts, robot_counts * (time_left - child_time_left))])


	result = current_geodes if len(all_child_geodes) == 0 else current_geodes + max(all_child_geodes)
	cache[cache_key] = result

	# update the most geodes we've ever found at this time step
	if result > best_cache[time_left]:
		best_cache[time_left] = result

	return result

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

	answer_1 = 0
	for i, blueprint in enumerate(blueprints):
		print(f"Blueprint {i + 1} of {len(blueprints)}.")
		cache = {}	
		time_cache = {}	
		best_cache = {i: 0 for i in range(25)}

		resource_counts = (0, 0, 0, 0)
		robot_counts = (0, 0, 0, 1)

		max_geodes = get_max_geodes(blueprint, TOTAL_TIME, resource_counts, robot_counts)
		print(f"Geodes for blueprint {i + 1}: {max_geodes}")

		answer_1 += (i + 1) * max_geodes
	
	end_time = time.time()
	print(f"End time: {end_time}")

	elapsed_time = end_time - start_time
	print(f"Elapsed time: {elapsed_time} seconds.")

	print(f"Answer 1: {answer_1}")
	print()


