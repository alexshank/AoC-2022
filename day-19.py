from helpers import load_data
from math import ceil
import time
from functools import lru_cache


# constants
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
START_TIME = 1
TOTAL_TIME = 24


class ResourceCount:
	def __init__(self, geode: int, obsidian: int, clay: int, ore: int):
		self.resources = {
			'geode': geode,
			'obsidian': obsidian,
			'clay': clay,
			'ore': ore
		}
	

	def add(self, resource_count) -> None:
		for resource_type in RESOURCE_TYPES:
			self.resources[resource_type] = self.resources[resource_type] + resource_count.resources[resource_type] 


	def sub(self, resource_count) -> None:
		for resource_type in RESOURCE_TYPES:
			self.resources[resource_type] = self.resources[resource_type] - resource_count.resources[resource_type] 

	def mul(self, scalar: int) -> None:
		for resource_type in RESOURCE_TYPES:
			self.resources[resource_type] = self.resources[resource_type] * scalar
	
	def increment_resource(self, resource_type: str) -> None:
		self.resources[resource_type] = self.resources[resource_type] + 1


	def get_resource(self, resource_type: str) -> int:
		return self.resources[resource_type]


	def lessThanOrEqual(self, resource_count) -> bool:
		return self.resources['geode'] <= resource_count.resources['geode'] and self.resources['obsidian'] <= resource_count.resources['obsidian'] and self.resources['clay'] <= resource_count.resources['clay'] and self.resources['ore'] <= resource_count.resources['ore']

	
	def copy(self):
		return ResourceCount(*[self.resources[resource_type] for resource_type in RESOURCE_TYPES])


	def __eq__(self, resource_count):
		return self.__hash__() == resource_count.__hash__()


	def __hash__(self):
		return hash((self.resources['geode'], self.resources['obsidian'], self.resources['clay'], self.resources['ore']))


# tracks maximum geodes found at each time step
# gets compared to the max number of possible remaining geodes to reduce search space
# if most geodes at time t is already more than theoretical max, skip searching that branch
most_geodes_at_time = {i: 0 for i in range(TOTAL_TIME + 1)}

# the triangular numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(25)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, 25)]


# determine the next time that a robot could be built based on current robots and resources
@lru_cache(maxsize=None)
def time_to_build_robot(blueprint_index, robot_resource_type, previous_time, updated_resource_counts, updated_robot_counts):
	# if already have the resources to build robot, return early
	robot_blueprint = BLUEPRINTS[blueprint_index][robot_resource_type]
	if robot_blueprint.lessThanOrEqual(updated_resource_counts):
		return previous_time + 1
	
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {
		resource_type
		for resource_type
		in RESOURCE_TYPES
		if robot_blueprint.get_resource(resource_type) > 0 and robot_blueprint.get_resource(resource_type) > updated_resource_counts.get_resource(resource_type)
	}
	obtainable_resource_types = {
		resource_type
		for resource_type
		in RESOURCE_TYPES
		if updated_robot_counts.get_resource(resource_type) > 0
	}
	if not required_resource_types.issubset(obtainable_resource_types):
		return None
	
	# TODO likely a cleaner, integer way of doing this without ceiling function
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = robot_blueprint.copy()
	resource_differences.sub(updated_resource_counts)
	time_deltas = [
		ceil(resource_differences.get_resource(required_resource) / updated_robot_counts.get_resource(required_resource))
		for required_resource 
		in required_resource_types
	]

	return previous_time + max(time_deltas) + 1


# recursively run simulation and return the maximum number of geodes that could be mined
# yields max number of geodes you could get by entering this time step with a build_type already chosen
@lru_cache(maxsize=None, typed=False)
def get_max_geodes(blueprint_index: int, time: int, resource_counts: ResourceCount, robot_counts: ResourceCount, build_type: str=None) -> int:
	# compute absolute upper bound of geodes we could get from this current state
	# this assumes you could build one new geode robot at every remaining time step
	# trim this branch off the search, if it clearly will not beat the current best
	current_geodes = resource_counts.get_resource('geode')
	geode_upper_bound = current_geodes + ((TOTAL_TIME - time) * robot_counts.get_resource('geode')) + TRIANGULAR_NUMBERS[TOTAL_TIME - time]
	if geode_upper_bound <= most_geodes_at_time[time]:
		return 0

	# start building the relevant robot that was planned for this time step
	# 1. Remove resources to start buiding robot
	# 2. Collect new resources with existing robots
	# 3. Add new robot to team of robots
	if build_type != None:
		# TODO these should be in place rather than copying new objects
		updated_resource_counts = resource_counts.copy()
		updated_resource_counts.sub(BLUEPRINTS[blueprint_index][build_type])
		updated_resource_counts.add(robot_counts)

		updated_robot_counts = robot_counts.copy()
		updated_robot_counts.increment_resource(build_type)
	else:
		# TODO these should be in place rather than copying new objects
		updated_resource_counts = resource_counts.copy()
		updated_resource_counts.add(robot_counts)

		updated_robot_counts = robot_counts.copy()

	# possible robots that could be built and when
	robot_build_times = [
		(
			robot_resource_type,
			time_to_build_robot(blueprint_index, robot_resource_type, time, updated_resource_counts, updated_robot_counts)
		)
		for robot_resource_type
		in RESOURCE_TYPES
	]

	all_child_geodes = []
	for robot_resource_type, child_time in robot_build_times:
		# if impossible to build the robot type at all or before time's up, continue
		# if robot built at time 24, it doesn't contribute any mining
		if child_time == None or child_time > TOTAL_TIME - 1:
			continue

		# add resources, new robot isn't available to mine resources until ((next time step) + 1)
		# TODO these should be in place rather than copying new objects
		newly_mined_resource_counts = updated_robot_counts.copy()
		newly_mined_resource_counts.mul(child_time - time - 1)
		child_resource_counts = updated_resource_counts.copy()
		child_resource_counts.add(newly_mined_resource_counts)

		# make recursive call
		child_geodes = get_max_geodes(blueprint_index, child_time, child_resource_counts, updated_robot_counts, robot_resource_type)
		all_child_geodes.append(child_geodes)

	# get best robot choice and resulting geodes
	if len(all_child_geodes) == 0:
		result = updated_resource_counts.get_resource('geode') + updated_robot_counts.get_resource('geode') * (TOTAL_TIME - time)
	else:
		result = max(all_child_geodes)

	# update the most geodes we've ever found at this time step
	if result > most_geodes_at_time[time]:
		most_geodes_at_time[time] = result

	return result


# returns array of dictionaries like blueprint['ore']['obsidian'] = 5
# i.e., this blueprint specifies that an ore robot needs 5 obsidian
def build_blueprint_dictionaries(lines):
	blueprints = []
	resource_indices = {'geode': 0, 'obsidian': 1, 'clay': 2, 'ore': 3}
	resource_types = ['geode', 'obsidian', 'clay', 'ore']
	for line in lines:
		robots = line.split(" Each ")[1:]
		robots = [robot.replace(".", "") for robot in robots]
		blueprint = {resource_type: {resource_type: 0 for resource_type in resource_types} for resource_type in resource_types}
		for robot in robots:
			robot_type, resource_costs = robot.split(" robot costs ")
			resource_costs = resource_costs.split(' and ')

			blueprint[robot_type] = [0 for _ in range(4)]
			for resource_cost in resource_costs:
				cost, resource_type = resource_cost.split(" ")
				blueprint[robot_type][resource_indices[resource_type]] = int(cost)
			blueprint[robot_type] = ResourceCount(*tuple(blueprint[robot_type]))

		blueprints.append(blueprint)
	return blueprints


# put blueprints in global namespace so we can cache methods
lines = load_data("day-19-test-input.txt")
BLUEPRINTS = build_blueprint_dictionaries(lines)
	

if __name__ == "__main__":
	start_time = time.time()
	print(f"Start time: {start_time}")
	print()

	answer_1 = 0
	for i in range(len(BLUEPRINTS)):
		print(f"Blueprint {i + 1} of {len(BLUEPRINTS)}.")

		most_geodes_at_time = {i: 0 for i in range(25)}

		# reset resources and robots
		resource_counts = ResourceCount(0, 0, 0, 0)
		robot_counts = ResourceCount(0, 0, 0, 1)

		# TODO Not likely, but is it possible that we could build a robot on the very first time step? (i.e., are given enough resources to start)
		# get max geodes that the blueprint could produce from simulation start
		max_geodes = get_max_geodes(i, START_TIME, resource_counts, robot_counts, None)
		answer_1 += (i + 1) * max_geodes

		# reset caches
		print(f"Max geodes  cache: {get_max_geodes.cache_info()}") 
		print(f"Robot build cache: {time_to_build_robot.cache_info()}") 
		get_max_geodes.cache_clear() 
		time_to_build_robot.cache_clear() 

		# make sure each blueprint isn't taking a ridiculous amount of time
		end_time = time.time()
		elapsed_time = end_time - start_time
		start_time = end_time
		print(f"Elapsed time for blueprint {i + 1}: {elapsed_time} seconds.")
		print()

	print(f"Answer 1: {answer_1}")
	print()


