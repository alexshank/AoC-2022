from helpers import load_data

# TODO could make more efficient with an array data structure?
RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
TOTAL_TIME = 24

# TODO move cache out of global space
cache = {}	

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


# recursively run simulation and return the maximum number of geodes that could be mined
def get_max_geodes(blueprint, time_left, resource_counts, robot_counts):
	# cache recursive results
	cache_key = f"{time_left}-{resource_counts}-{robot_counts}"
	if cache_key in cache:
		return cache[cache_key]

	# base case: we've run out of time
	if time_left == 1:
		return robot_counts.get_resource('geode')

	# TODO alternative, possibly smaller, problem space would be: "which type of robot do we want to make next?"
	# TODO we would then jump ahead X states until we could build the desired robot (and probably avoid a lot of recursion cases)

	all_child_geodes = []
	for robot_resource_type in RESOURCE_TYPES:
		# check if you can build a robot BEFORE mining this time step's resources
		if not blueprint[robot_resource_type] <= resource_counts:
			continue

		# TODO may be innefficient to return whole new object in the += call?
		# add resources, new robot isn't available to mine resources until next time step 
		resource_counts += robot_counts
		robot_counts.add_to_resource(robot_resource_type, 1)

		# remove the resources needed for newly built robot
		resource_counts -= blueprint[robot_resource_type]

		# make recursive call
		child_geodes = get_max_geodes(blueprint, time_left - 1, resource_counts, robot_counts)
		all_child_geodes.append(child_geodes)

		# add back resources needed for newly built robot
		resource_counts += blueprint[robot_resource_type]

		# remove robot that was just built
		robot_counts.add_to_resource(robot_resource_type, -1)

		# remove resources that were mined this time step
		resource_counts -= robot_counts

	# always add child case where we build no robots but advance time
	resource_counts += robot_counts
	child_geodes = get_max_geodes(blueprint, time_left - 1, resource_counts, robot_counts)
	resource_counts -= robot_counts

	current_geodes = robot_counts.get_resource('geode')
	all_child_geodes.append(child_geodes)

	result = current_geodes + max(all_child_geodes)
	cache[cache_key] = result
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

	answer_1 = 0
	for i, blueprint in enumerate(blueprints):
		print(f"Blueprint {i + 1} of {len(blueprints)}.")
		cache = {}	

		resource_counts = ResourceSet()
		robot_counts = ResourceSet()
		robot_counts.add_to_resource('ore', 1)
		answer_1 += (i + 1) * get_max_geodes(blueprint, TOTAL_TIME, resource_counts, robot_counts)
	
	print(f"Answer 1: {answer_1}")
	print()


