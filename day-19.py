from helpers import load_data
from math import ceil
import time

# TODO could make more efficient with an array data structure?
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
TOTAL_TIME = 24

# TODO move cache out of global space
cache = {}	
time_cache = {}	
best_cache = {i: 0 for i in range(25)}

# the triangle numbers for getting geode upper bounds
NATURAL_NUMBERS = [i + 1 for i in range(25)]
TRIANGULAR_NUMBERS = [sum(NATURAL_NUMBERS[:i]) for i in range(1, 25)]

"""
Helper class for custom addition and multiplication operators
"""
class ResourceSet:
	def __init__(self, resource_dictionary={'ore': 0, 'obsidian': 0, 'clay': 0, 'geode': 0}):
		self.ore = resource_dictionary['ore']
		self.obsidian = resource_dictionary['obsidian']
		self.clay = resource_dictionary['clay']
		self.geode = resource_dictionary['geode']
		
		
	def add_to_resource(self, resource, amount):
		if resource == 'ore':
			self.ore += amount
		elif resource == 'obsidian':
			self.obsidian += amount
		elif resource == 'clay':
			self.clay += amount
		elif resource == 'geode':
			self.geode += amount
		else:
			raise ValueError('Invalid resource.')
		

	def get_resource(self, resource):
		if resource == 'ore':
			return self.ore
		elif resource == 'obsidian':
			return self.obsidian
		elif resource == 'clay':
			return self.clay
		elif resource == 'geode':
			return self.geode
		else:
			raise ValueError('Invalid resource.')
		

	def __add__(self, other):
		if isinstance(other, ResourceSet):
			return ResourceSet({
				'ore': self.ore + other.ore,
				'obsidian': self.obsidian + other.obsidian,
				'clay': self.clay + other.clay,
				'geode': self.geode + other.geode,
			})
		else:
			raise ValueError("Unsupported operand type for +")
	

	def __sub__(self, other):
		if isinstance(other, ResourceSet):
			return ResourceSet({
				'ore': self.ore - other.ore,
				'obsidian': self.obsidian - other.obsidian,
				'clay': self.clay - other.clay,
				'geode': self.geode - other.geode,
			})
		else:
			raise ValueError("Unsupported operand type for -")


	def __le__(self, other):
		if isinstance(other, ResourceSet):
			return all([
				self.ore <= other.ore,
				self.obsidian <= other.obsidian,
				self.clay <= other.clay,
				self.geode <= other.geode,
			])
		else:
			raise ValueError("Unsupported operand type for -")
	

	# note: the integer must be on the right side of the * operator here
	def __mul__(self, other):
		if isinstance(other, int):
			return ResourceSet({
				'ore': self.ore * other,
				'obsidian': self.obsidian * other,
				'clay': self.clay * other,
				'geode': self.geode * other,
			})
		else:
			raise ValueError("Unsupported operand type for *")
		
	def __str__(self):
		return f"ore:{self.ore}:obsidian:{self.obsidian}:clay:{self.clay}:geode:{self.geode}"


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
	
	# check if we have existing robots that can eventually mine us the resources for the new robot
	required_resource_types = {resource_type for resource_type in RESOURCE_TYPES if robot_blueprint.get_resource(resource_type) > 0 and robot_blueprint.get_resource(resource_type) > resource_counts.get_resource(resource_type)}
	obtainable_resource_types = {resource_type for resource_type in required_resource_types if robot_counts.get_resource(resource_type) > 0}
	if obtainable_resource_types < required_resource_types:
		time_cache[cache_key] = None
		return None
	
	# compute how many time steps it will take to acquire enough resources to build the new robot
	resource_differences = robot_blueprint - resource_counts
	time_deltas = [
		ceil(resource_differences.get_resource(required_resource) / robot_counts.get_resource(required_resource))
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
		result = robot_counts.get_resource('geode')
		cache[cache_key] = result
		return result

	# TODO where should this check actually occur?
	# compute absolute upper bound of geodes we could get
	current_geodes = robot_counts.get_resource('geode')
	geode_upper_bound = current_geodes + (time_left * robot_counts.get_resource('geode')) + TRIANGULAR_NUMBERS[time_left - 1]
	if geode_upper_bound < best_cache[time_left]:
		result = 0
		cache[cache_key] = result
		return result

	all_child_geodes = []
	for robot_resource_type in RESOURCE_TYPES:
		# returns None if not possible to build
		child_time_left = time_to_build_robot(blueprint, robot_resource_type, time_left, resource_counts, robot_counts)

		# if impossible to build the robot type at all or before time's up, continue
		if child_time_left == None or child_time_left < 1:
			continue

		# TODO may be innefficient to return whole new object in the += call?
		# add resources, new robot isn't available to mine resources until next time step 
		resource_counts += robot_counts * (time_left - child_time_left) 
		robot_counts.add_to_resource(robot_resource_type, 1)

		# remove the resources needed for newly built robot
		resource_counts -= blueprint[robot_resource_type]

		# make recursive call
		child_geodes = get_max_geodes(blueprint, child_time_left, resource_counts, robot_counts)
		all_child_geodes.append(child_geodes)

		# add back resources needed for newly built robot
		resource_counts += blueprint[robot_resource_type]

		# remove robot that was just built
		robot_counts.add_to_resource(robot_resource_type, -1)

		# remove resources that were mined this time step
		resource_counts -= robot_counts * (time_left - child_time_left)
	
	result = current_geodes if len(all_child_geodes) == 0 else current_geodes + max(all_child_geodes)
	cache[cache_key] = result

	# update the most geodes we've ever found at this time step
	if result > best_cache[time_left]:
		print(f"Updating best possible to {result} for {time_left}")
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

			blueprint[robot_type] = ResourceSet()
			for resource_cost in resource_costs:
				cost, resource_type = resource_cost.split(" ")
				blueprint[robot_type].add_to_resource(resource_type, int(cost))

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

		resource_counts = ResourceSet()
		robot_counts = ResourceSet()
		robot_counts.add_to_resource('ore', 1)

		temp = get_max_geodes(blueprint, TOTAL_TIME, resource_counts, robot_counts)
		print(f"Geodes for blueprint {i + 1}: {temp}")

		answer_1 += (i + 1) * temp
	
	end_time = time.time()
	print(f"End time: {end_time}")

	elapsed_time = end_time - start_time
	print(f"Elapsed time: {elapsed_time} seconds.")

	print(f"Answer 1: {answer_1}")
	print()


