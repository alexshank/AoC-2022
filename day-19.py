from helpers import load_data
from math import ceil
import time
from functools import lru_cache, reduce
from operator import mul
import multiprocessing


# TODO could make more efficient with an array data structure?
RESOURCE_INDICES = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
RESOURCE_MASKS = {'geode': (1, 0, 0, 0), 'obsidian': (0, 1, 0, 0), 'clay': (0, 0, 1, 0), 'ore': (0, 0, 0, 1)}
START_TIME = 1
# TOTAL_TIME = 24
TOTAL_TIME = 32 # part 2

# tracks most geodes found at each time step
# gets compared to the max number of possible remaining geodes to reduce search space
# if most geodes at time t is already more than theoretical max, skip searching that branch
MOST_GEODES_AT_TIME = {i: 0 for i in range(TOTAL_TIME + 1)}

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
def time_to_build_robot(blueprint_index, robot_resource_type, updated_resource_counts, updated_robot_counts):
	# if already have the resources to build robot, return early
	robot_blueprint = BLUEPRINTS[blueprint_index][robot_resource_type]
	if lessThanOrEqualT(robot_blueprint, updated_resource_counts):
		return 1
	
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {i for i in range(4) if robot_blueprint[i] > 0 and robot_blueprint[i] > updated_resource_counts[i]}
	obtainable_resource_types = {i for i in range(4) if updated_robot_counts[i] > 0}
	if not required_resource_types.issubset(obtainable_resource_types):
		return None
	
	# TODO likely a cleaner, integer way of doing this without ceiling function
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = subT(robot_blueprint, updated_resource_counts)
	time_deltas = [
		ceil(resource_differences[required_resource] / updated_robot_counts[required_resource])
		for required_resource 
		in required_resource_types
	]

	return max(time_deltas) + 1


# recursively run simulation and return the maximum number of geodes that could be mined
# yields max number of geodes you could get by entering this time step with a build_type already chosen
@lru_cache(maxsize=None)
def get_max_geodes(blueprint_index, time, resource_counts, robot_counts, max_robot_counts, max_resource_counts, build_type=None):
	# compute absolute upper bound of geodes we could get from this current state
	# this assumes you could build one new geode robot at every remaining time step
	# trim this branch off the search, if it clearly will not beat the current best
	current_geodes = resource_counts[0]
	geode_upper_bound = current_geodes + ((TOTAL_TIME - time) * robot_counts[0]) + TRIANGULAR_NUMBERS[TOTAL_TIME - time]
	if geode_upper_bound < MOST_GEODES_AT_TIME[blueprint_index][time]:
		# TODO arbitrary value that makes this branch really undesirable
		return -100_000
 
	# start building the relevant robot that was planned for this time step
	# 1. Remove resources to start buiding robot
	# 2. Collect new resources with existing robots
	# 3. Add new robot to team of robots
	if build_type != None:
		updated_resource_counts = subT(resource_counts, BLUEPRINTS[blueprint_index][build_type])
		updated_resource_counts = addT(updated_resource_counts, robot_counts)

		# TODO don't actually have to do clamp math on the geode 10_000 limit
		# TODO likely don't need the +1?
		# TODO cap resources at a max so that we get more cache hits
		# print('dog')
		# print(f"{blueprint_index} {max_robot_counts}")
		temp_max_resource_counts = tuple(i * (TOTAL_TIME - time + 1) for i in max_robot_counts)
		# print(f"{blueprint_index} {temp_max_resource_counts}")
		# print()
		updated_resource_counts = clampT(updated_resource_counts, temp_max_resource_counts)

		updated_robot_counts = addT(robot_counts, RESOURCE_MASKS[build_type])
		updated_robot_counts = clampT(updated_robot_counts, max_robot_counts)
	else:
		updated_resource_counts = addT(resource_counts, robot_counts)

		# TODO don't actually have to do clamp math on the geode 10_000 limit
		# TODO likely don't need the +1?
		# TODO cap resources at a max so that we get more cache hits
		# print('cat')
		# print(f"{blueprint_index} {max_robot_counts}")
		temp_max_resource_counts = tuple(i * (TOTAL_TIME - time + 1) for i in max_robot_counts)
		# print(f"{blueprint_index} {temp_max_resource_counts}")
		# print()
		updated_resource_counts = clampT(updated_resource_counts, temp_max_resource_counts)

		updated_robot_counts = robot_counts
		updated_robot_counts = clampT(robot_counts, max_robot_counts)
	
	# TODO testing that we are getting to the correct states
	if time == 8 and updated_robot_counts[0] == 0 and updated_resource_counts == (0, 0, 1, 3):
	# if time == 13 and updated_robot_counts[0] == 0 and updated_resource_counts == (0, 0, 21, 3):

	# TODO we do reach this state successfully
	# if time == 14 and updated_robot_counts[1] == 1 and updated_resource_counts == (0, 0, 14, 2):

	# TODO we aren't reaching this, it would be a next state where we choose not to build anything
	# if time == 15 and updated_robot_counts[0] == 0 and updated_resource_counts == (0, 1, 21, 4):
	# if time == 25 and updated_robot_counts[0] == 4 and updated_resource_counts == (11, 10, 35, 4):
		print('~~~~~~~' * 10)
		print(f"Matched state at time: {time}")
		print(updated_robot_counts)
		print(updated_resource_counts)
		print('~~~~~~~' * 10)

	# possible robots that could be built and when
	robot_build_times = [
		(
			robot_resource_type,
			time_to_build_robot(blueprint_index, robot_resource_type, updated_resource_counts, updated_robot_counts)
		)
		for robot_resource_type
		in RESOURCE_MASKS.keys()
		if updated_robot_counts[RESOURCE_INDICES[robot_resource_type]] < max_robot_counts[RESOURCE_INDICES[robot_resource_type]]
	]

	all_child_geodes = []
	for robot_resource_type, child_time in robot_build_times:
		# if impossible to build the robot type at all or before time's up, continue
		# if robot built at time 24, it doesn't contribute any mining
		if child_time == None or time + child_time > TOTAL_TIME - 1:
			continue

		# add resources, new robot isn't available to mine resources until ((next time step) + 1)
		newly_mined_resource_counts = scaleT(updated_robot_counts, child_time - 1)
		child_resource_counts = addT(updated_resource_counts, newly_mined_resource_counts)

		# make recursive call
		child_geodes = get_max_geodes(blueprint_index, time + child_time, child_resource_counts, updated_robot_counts, max_robot_counts, max_resource_counts, robot_resource_type)
		all_child_geodes.append(child_geodes)

	# can never build any future robot by just waiting and collecting resources
	if len(all_child_geodes) == 0:
		result = updated_resource_counts[0] + updated_robot_counts[0] * (TOTAL_TIME - time)
	# could build a future robot before time is up
	elif len(all_child_geodes) > 0:

		# TODO START OF TEST ###########################################################################
		# # TODO check case where we just step ahead in time and choose to build nothing
		# # TODO this is blowing up the search space to giant size
		# # TODO NEXT ATTEMPT IS TO BUMP RESOURCES HERE, THEN USE TIME_TO_BUILD_ROBOT again and create more child results

		# # TODO refactor so that we don't just have copy and paste of the below
		# # TODO checking next robot build times if we choose to not build next turn
		# # possible robots that could be built and when
		# second_updated_resource_counts = addT(updated_resource_counts, updated_robot_counts)
		# robot_build_times = [
		# 	(
		# 		robot_resource_type,
		# 		time_to_build_robot(blueprint_index, robot_resource_type, second_updated_resource_counts, updated_robot_counts)
		# 	)
		# 	for robot_resource_type
		# 	in RESOURCE_MASKS.keys()
		# 	if updated_robot_counts[RESOURCE_INDICES[robot_resource_type]] < max_robot_counts[RESOURCE_INDICES[robot_resource_type]]
		# ]

		# # TODO we're appending to an already non-empty list
		# # all_child_geodes = []
		# for robot_resource_type, child_time in robot_build_times:
		# 	# if impossible to build the robot type at all or before time's up, continue
		# 	# if robot built at time 24, it doesn't contribute any mining
		# 	if child_time == None or time + 1 + child_time > TOTAL_TIME - 1:
		# 		continue

		# 	# add resources, new robot isn't available to mine resources until ((next time step) + 1)
		# 	newly_mined_resource_counts = scaleT(updated_robot_counts, child_time - 1)
		# 	child_resource_counts = addT(second_updated_resource_counts, newly_mined_resource_counts)

		# 	# make recursive call
		# 	child_geodes = get_max_geodes(blueprint_index, time + 1 + child_time, child_resource_counts, updated_robot_counts, max_robot_counts, max_resource_counts, robot_resource_type)
		# 	all_child_geodes.append(child_geodes)
		# TODO END OF TEST ###########################################################################

		result = max(all_child_geodes)
	else:
		raise Exception("Uncaught case for result!")

	# update the most geodes we've ever found at this time step
	if result > MOST_GEODES_AT_TIME[blueprint_index][time]:
		MOST_GEODES_AT_TIME[blueprint_index][time] = result

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

			blueprint[robot_type] = [0 for _ in range(4)]
			for resource_cost in resource_costs:
				cost, resource_type = resource_cost.split(" ")
				blueprint[robot_type][RESOURCE_INDICES[resource_type]] = int(cost)
			blueprint[robot_type] = tuple(blueprint[robot_type])

		blueprints.append(blueprint)
	return blueprints


# put blueprints in global namespace so we can cache methods
lines = load_data("day-19-test-input.txt")
BLUEPRINTS = build_blueprint_dictionaries(lines)
# BLUEPRINTS = BLUEPRINTS[:3] # part 2
BLUEPRINTS = [BLUEPRINTS[0]] # TODO testing
MOST_GEODES_AT_TIME = {
	i: {j: 0 for j in range(TOTAL_TIME + 1)}
	for i in range(len(BLUEPRINTS))
}
	

def process_blueprint(i):
	start_time = time.time()
	print(f"Blueprint {i + 1} of {len(BLUEPRINTS)}.")
	
	# TODO need to determine these maximums / sums more accurately
	# find the maximum number of each robot we would ever want
	# if we can only spend X ore per turn, we would never want X + 1 ore robots
	# this is the main thing that reduces our search space
	blueprint = BLUEPRINTS[i]
	max_geode = 10_000
	max_obsidian = max([blueprint[resource_type][1] for resource_type in RESOURCE_TYPES])
	max_clay = max([blueprint[resource_type][2] for resource_type in RESOURCE_TYPES])
	max_ore = max([blueprint[resource_type][3] for resource_type in RESOURCE_TYPES])
	max_robot_counts = (max_geode, max_obsidian, max_clay, max_ore)
	
	# TODO possibly remove, not currently used
	sum_geode = 10_000
	sum_obsidian = sum([blueprint[resource_type][1] for resource_type in RESOURCE_TYPES])
	sum_clay = sum([blueprint[resource_type][2] for resource_type in RESOURCE_TYPES])
	sum_ore = sum([blueprint[resource_type][3] for resource_type in RESOURCE_TYPES])
	max_resource_counts = (sum_geode, sum_obsidian, sum_clay, sum_ore)
	
	# reset resources and robots
	resource_counts = (0, 0, 0, 0)
	robot_counts = (0, 0, 0, 1)

	# get max geodes that the blueprint could produce from simulation start
	max_geodes = get_max_geodes(i, START_TIME, resource_counts, robot_counts, max_robot_counts, max_resource_counts, None)
	# result = (i + 1) * max_geodes # part 1
	result = max_geodes # part 2

	# view cache efficacy (separate processes can't see each others' caches, so no need to clear)
	print(f"Max geodes  cache: {get_max_geodes.cache_info()}") 
	print(f"Robot build cache: {time_to_build_robot.cache_info()}") 

	# measure elapsed time
	end_time = time.time()
	elapsed_time = end_time - start_time
	print(f"Elapsed time for blueprint {i + 1}: {elapsed_time} seconds.")
	print(f"Result for blueprint {i + 1}: {result}")
	print()
	return result


if __name__ == "__main__":
	overall_start_time = time.time()
	print(f"Start time: {overall_start_time}")
	print()

	# determine the number of available cores
	num_cores = multiprocessing.cpu_count()

	# delegate to a pool of workers
	with multiprocessing.Pool(processes=num_cores) as pool:
		results = pool.map(process_blueprint, range(len(BLUEPRINTS)))

	# sum up all the results
	# answer = sum(results)
	answer = reduce(mul, results) # part 2

	# part 1 (answer: 1127)

	# TODO answer 19656 too low for part 2
	# part 2 (answer: TODO)
	print(f"Answer: {answer}")
	print()

	overall_end_time = time.time()
	overall_elapsed_time = overall_end_time - overall_start_time
	print(f"Total elapsed time: {overall_elapsed_time} seconds.")

