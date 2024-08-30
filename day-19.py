from helpers import load_data
from math import ceil
import time

# TODO could make more efficient with an array data structure?
RESOURCE_INDICES = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
RESOURCE_MASKS = {'geode': (1, 0, 0, 0), 'obsidian': (0, 1, 0, 0), 'clay': (0, 0, 1, 0), 'ore': (0, 0, 0, 1)}
TOTAL_TIME = 24

# various caches for memoizing recursive calls
max_geode_cache = {}	
log_cache = {}	
time_to_build_robot_cache = {}	
best_cache = {i: 0 for i in range(25)}

# the triangle numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(25)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, 25)]

# helper functions for printing nicely
STR_TIME = lambda time: str(time).rjust(2)
STR_BUILD_TYPE = lambda build_type: build_type + ' ' * (len('obsidian') - len(build_type)) if build_type is not None else ' ' * len('obsidian')
STR_COUNT_DICT = lambda count_tuple: f"({STR_TIME(count_tuple[0])}, {STR_TIME(count_tuple[1])}, {STR_TIME(count_tuple[2])}, {STR_TIME(count_tuple[3])})"

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


def anyLessThanT(t1, t2):
	return any(x < y for x, y in zip(t1, t2))


def nonzeroT(t1):
	return tuple(x if x > 0 else 0 for x in t1)


# determine the next time that a robot could be built based on current robots and resources
def time_to_build_robot(robot_blueprint, previous_time, updated_resource_counts, updated_robot_counts):
	# cache recursive results
	cache_key = f"{robot_blueprint}-{previous_time}-{updated_resource_counts}-{updated_robot_counts}"
	if cache_key in time_to_build_robot_cache:
		return time_to_build_robot_cache[cache_key]

	# if already have the resources to build robot, return early
	if lessThanOrEqualT(robot_blueprint, updated_resource_counts):
		time_to_build_robot_cache[cache_key] = previous_time + 1
		return previous_time + 1
	
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {i for i in range(4) if robot_blueprint[i] > 0 and robot_blueprint[i] > updated_resource_counts[i]}
	obtainable_resource_types = {i for i in range(4) if updated_robot_counts[i] > 0}
	if not required_resource_types.issubset(obtainable_resource_types):
		time_to_build_robot_cache[cache_key] = None
		return None
	
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = subT(robot_blueprint, updated_resource_counts)
	time_deltas = [
		ceil(resource_differences[required_resource] / updated_robot_counts[required_resource])
		for required_resource 
		in required_resource_types
	]

	# TODO remove
	if previous_time < 4:
		print(f"\t{robot_blueprint}")
		print(f"\t{updated_resource_counts}")
		print(f"\t{resource_differences}")
		print(f"\t{time_deltas}")

	# needed_time = 0
	# temp_resources = (0, 0, 0, 0)
	# while anyLessThanT(temp_resources, resource_differences):
	# 	temp_resources = addT(temp_resources, robot_counts)
	# 	needed_time += 1

	# result = time + needed_time
	result = previous_time + max(time_deltas) + 1
	time_to_build_robot_cache[cache_key] = result
	return result


# recursively run simulation and return the maximum number of geodes that could be mined
# yields max number of geodes you could get by entering this time step with a build_type already chosen
def get_max_geodes(blueprint, time, resource_counts, robot_counts, build_type=None):
	# cache recursive results
	cache_key = f"{time}-{resource_counts}-{robot_counts}-{build_type}"
	if cache_key in max_geode_cache:
		return max_geode_cache[cache_key], log_cache[cache_key]

	# base case: we've run out of time, return the geodes collected at this final time step
	if time == 24:

		# TODO we should never hit this, because robot would be built in final step and never mine anything
		raise Exception("Should not reach. We should calculate the geodes we'd have by end time without simulating actual end time.")

		result = robot_counts[0] + resource_counts[0]
		max_geode_cache[cache_key] = result
		type_result = [f'Minute {time}: time is 24, returning current geodes + geode robot count: {result}']
		log_cache[cache_key] = type_result
		return result, type_result

	# compute absolute upper bound of geodes we could get from this current state
	# this assumes you could build one new geode robot at every remaining time step
	# trim this branch off the search, if it clearly will not beat the current best
	current_geodes = resource_counts[0]
	geode_upper_bound = current_geodes + ((TOTAL_TIME - time) * robot_counts[0]) + TRIANGULAR_NUMBERS[TOTAL_TIME - time]
	if geode_upper_bound <= best_cache[time]:
		result = 0
		max_geode_cache[cache_key] = result
		type_result = [f'Minute {STR_TIME(time)}: useless branch at time {STR_TIME(time)}, returning arbitrary {STR_TIME(result)} geodes']
		log_cache[cache_key] = type_result
		return result, type_result

	# start building the relevant robot that was planned for this time step
	# 1. Remove resources to start buiding robot
	# 2. Collect new resources with existing robots
	# 3. Add new robot to team of robots
	if build_type != None:
		updated_resource_counts = subT(resource_counts, blueprint[build_type])
		updated_resource_counts = addT(updated_resource_counts, robot_counts)
		updated_robot_counts = addT(robot_counts, RESOURCE_MASKS[build_type])
	else:
		updated_resource_counts = addT(resource_counts, robot_counts)
		updated_robot_counts = robot_counts

	# possible robots that could be built and when
	if time < 4:

		print(f"DEBUG: Time {time}")
		print(f"DEBUG: Starting robots {STR_COUNT_DICT(robot_counts)}")
		print(f"DEBUG: Starting resources {STR_COUNT_DICT(resource_counts)}")

		print(f"At the end of time {time}...")
		print(f"We have {STR_COUNT_DICT(updated_robot_counts)} robots")
		print(f"We have {STR_COUNT_DICT(updated_resource_counts)} resources")

	robot_build_times = []
	for robot_resource_type in RESOURCE_MASKS.keys():
		robot_blueprint = blueprint[robot_resource_type]
		child_time = time_to_build_robot(robot_blueprint, time, updated_resource_counts, updated_robot_counts)
		robot_build_times.append((robot_resource_type, child_time))

		if time < 4:
			print(f"Can build {STR_BUILD_TYPE(robot_resource_type)} robot at time {STR_TIME(child_time)}")

	if time < 4:
		print()
	
	all_child_geodes = []
	all_child_geodes_type = []
	for robot_resource_type, child_time in robot_build_times:
		# if impossible to build the robot type at all or before time's up, continue
		# if robot built at time 24, it doesn't contribute any mining
		if child_time == None or child_time > TOTAL_TIME - 1:
			continue

		# add resources, new robot isn't available to mine resources until ((next time step) + 1)
		newly_mined_resource_counts = scaleT(updated_robot_counts, child_time - time - 1)
		child_resource_counts = addT(updated_resource_counts, newly_mined_resource_counts)

		# make recursive call
		child_geodes, child_type = get_max_geodes(blueprint, child_time, child_resource_counts, updated_robot_counts, robot_resource_type)

		all_child_geodes.append(child_geodes)
		temp = [f"Minute {STR_TIME(time)}: Built {STR_BUILD_TYPE(build_type)} robot at {STR_TIME(time)}, now have {STR_COUNT_DICT(updated_robot_counts)} robots, and {STR_COUNT_DICT(updated_resource_counts)} resources, with {STR_TIME(updated_resource_counts[0])} geodes"]
		temp.extend(child_type)
		all_child_geodes_type.append(temp)

	# get best robot choice and resulting geodes
	if len(all_child_geodes) == 0:
		result = updated_resource_counts[0] + updated_robot_counts[0] * (TOTAL_TIME - time)
		result_type = [f'Minute {time}: No future robots to build past {time}, returning {result} geodes']
	else:
		result = max(all_child_geodes)
		result_type_index = max(range(len(all_child_geodes)), key=all_child_geodes.__getitem__)
		result_type = all_child_geodes_type[result_type_index]

	# update cached results
	max_geode_cache[cache_key] = result
	log_cache[cache_key] = result_type

	# update the most geodes we've ever found at this time step
	if result > best_cache[time]:
		best_cache[time] = result

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

			blueprint[robot_type] = [0 for _ in range(4)]
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
		max_geode_cache = {}	
		time_to_build_robot_cache = {}	
		best_cache = {i: 0 for i in range(25)}

		resource_counts = (0, 0, 0, 0)
		robot_counts = (0, 0, 0, 1)

		# TODO is it possible that we could build a robot on the very first time step? (i.e., are given enough resources to start)
		max_geodes, best_path = get_max_geodes(blueprint, 1, resource_counts, robot_counts, None)
		print(f"Geodes for blueprint {i + 1}: {max_geodes}")
		print(f"Path:")
		for event in best_path:
			print(event)
		print()

		# TODO this shows we aren't propogating child results up properly in the recursive calls
		# for k, v in best_cache.items():
		# 	print(f"Time left {k}: {v}")

		answer_1 += (i + 1) * max_geodes

		# make sure each blueprint isn't taking a ridiculous amount of time
		end_time = time.time()
		elapsed_time = end_time - start_time
		start_time = end_time
		print(f"Elapsed time for blueprint {i + 1}: {elapsed_time} seconds.")
		print()

		# TODO remove and run on all provided blueprints
		# break

	print(f"Answer 1: {answer_1}")
	print()


