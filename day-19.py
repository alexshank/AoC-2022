from helpers import load_data
from math import ceil
import time
from functools import lru_cache
import multiprocessing


# TODO could make more efficient with an array data structure?
RESOURCE_INDICES = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
RESOURCE_MASKS = {'geode': (1, 0, 0, 0), 'obsidian': (0, 1, 0, 0), 'clay': (0, 0, 1, 0), 'ore': (0, 0, 0, 1)}
START_TIME = 1
TOTAL_TIME = 24

# tracks most geodes found at each time step
# gets compared to the max number of possible remaining geodes to reduce search space
# if most geodes at time t is already more than theoretical max, skip searching that branch
MOST_GEODES_AT_TIME = {i: 0 for i in range(TOTAL_TIME + 1)}

# the triangular numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(25)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, 25)]


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


# determine the next time that a robot could be built based on current robots and resources
@lru_cache(maxsize=None)
def time_to_build_robot(blueprint_index, robot_resource_type, previous_time, updated_resource_counts, updated_robot_counts):
	# if already have the resources to build robot, return early
	robot_blueprint = BLUEPRINTS[blueprint_index][robot_resource_type]
	if lessThanOrEqualT(robot_blueprint, updated_resource_counts):
		return previous_time + 1
	
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

	return previous_time + max(time_deltas) + 1


# recursively run simulation and return the maximum number of geodes that could be mined
# yields max number of geodes you could get by entering this time step with a build_type already chosen
@lru_cache(maxsize=None)
def get_max_geodes(blueprint_index, time, resource_counts, robot_counts, build_type=None):
	# compute absolute upper bound of geodes we could get from this current state
	# this assumes you could build one new geode robot at every remaining time step
	# trim this branch off the search, if it clearly will not beat the current best
	current_geodes = resource_counts[0]
	geode_upper_bound = current_geodes + ((TOTAL_TIME - time) * robot_counts[0]) + TRIANGULAR_NUMBERS[TOTAL_TIME - time]
	if geode_upper_bound <= MOST_GEODES_AT_TIME[blueprint_index][time]:
		return 0

	# start building the relevant robot that was planned for this time step
	# 1. Remove resources to start buiding robot
	# 2. Collect new resources with existing robots
	# 3. Add new robot to team of robots
	if build_type != None:
		updated_resource_counts = subT(resource_counts, BLUEPRINTS[blueprint_index][build_type])
		updated_resource_counts = addT(updated_resource_counts, robot_counts)
		updated_robot_counts = addT(robot_counts, RESOURCE_MASKS[build_type])
	else:
		updated_resource_counts = addT(resource_counts, robot_counts)
		updated_robot_counts = robot_counts

	# possible robots that could be built and when
	robot_build_times = [
		(
			robot_resource_type,
			time_to_build_robot(blueprint_index, robot_resource_type, time, updated_resource_counts, updated_robot_counts)
		)
		for robot_resource_type
		in RESOURCE_MASKS.keys()
	]

	all_child_geodes = []
	for robot_resource_type, child_time in robot_build_times:
		# if impossible to build the robot type at all or before time's up, continue
		# if robot built at time 24, it doesn't contribute any mining
		if child_time == None or child_time > TOTAL_TIME - 1:
			continue

		# add resources, new robot isn't available to mine resources until ((next time step) + 1)
		newly_mined_resource_counts = scaleT(updated_robot_counts, child_time - time - 1)
		child_resource_counts = addT(updated_resource_counts, newly_mined_resource_counts)

		# make recursive call
		child_geodes = get_max_geodes(blueprint_index, child_time, child_resource_counts, updated_robot_counts, robot_resource_type)
		all_child_geodes.append(child_geodes)

	# get best robot choice and resulting geodes
	if len(all_child_geodes) == 0:
		result = updated_resource_counts[0] + updated_robot_counts[0] * (TOTAL_TIME - time)
	else:
		result = max(all_child_geodes)

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
lines = load_data("day-19-input.txt")
BLUEPRINTS = build_blueprint_dictionaries(lines)
MOST_GEODES_AT_TIME = {
	i: {j: 0 for j in range(TOTAL_TIME + 1)}
	for i in range(len(BLUEPRINTS))
}
	

def process_blueprint(i):
    start_time = time.time()
    print(f"Blueprint {i + 1} of {len(BLUEPRINTS)}.")

    # reset resources and robots
    resource_counts = (0, 0, 0, 0)
    robot_counts = (0, 0, 0, 1)

    # get max geodes that the blueprint could produce from simulation start
    max_geodes = get_max_geodes(i, START_TIME, resource_counts, robot_counts, None)
    result = (i + 1) * max_geodes

    # view cache efficacy (separate processes can't see each others' caches, so no need to clear)
    print(f"Max geodes  cache: {get_max_geodes.cache_info()}") 
    print(f"Robot build cache: {time_to_build_robot.cache_info()}") 

    # measure elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time for blueprint {i + 1}: {elapsed_time} seconds.")
    print()

    return result


if __name__ == "__main__":
    overall_start_time = time.time()
    print(f"Start time: {overall_start_time}")
    print()

    # determine the number of available cores
    num_cores = multiprocessing.cpu_count()

    # create a pool of workers
    with multiprocessing.Pool(processes=num_cores) as pool:
        # Map the process_blueprint function to each blueprint index
        results = pool.map(process_blueprint, range(len(BLUEPRINTS)))

    # sum up all the results
    answer_1 = sum(results)

	# part 1 (answer: 1127)
    print(f"Answer 1: {answer_1}")
    print()

    overall_end_time = time.time()
    overall_elapsed_time = overall_end_time - overall_start_time
    print(f"Total elapsed time: {overall_elapsed_time} seconds.")

