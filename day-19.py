from helpers import load_data

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
		return f"ore: {self.ore}\nobsidian: {self.obsidian}\nclay: {self.clay}\ngeode: {self.geode}"


"""
Class to represent the different states of the simulation that need to be considered
"""
class StatePart1:
	def __init__(self, blueprint, time_left, resource_counts, robot_counts):
		self.blueprint = blueprint
		self.time_left = time_left
		self.resource_counts = resource_counts
		self.robot_counts = robot_counts
	
	# TODO shouldn't be mixing up self properties and non-self properties. Make pure function

	# find every way we could spend all the current resources to build robots
	# returns list of dictionaries with number of robots of each resource type that could be built
	# i.e., [{'ore': 4, 'osidian': 0, ... }, {'ore': 3, 'osidian': 0, ... }, ... ]
	def get_robot_count_combinations(self, resource_counts, robot_type_set=[r for r in RESOURCE_TYPES]):

		# TODO fix this jank caching
		set_string = "-".join([t for t in robot_type_set])
		resource_string = "-".join([str(resource_counts.get_resource(k)) for k in RESOURCE_TYPES])
		cache_key = f"{set_string}-{resource_string}"
		if cache_key in cache:
			return cache[cache_key]

		robot_count_combinations = []

		# TODO should not modify this set while iterating over it
		# TODO think I'm copying this set twice
		local_robot_type_set = set([s for s in robot_type_set])
		for robot_type in robot_type_set:
			robot_costs = self.blueprint[robot_type]

			# determine how many robots of the given type we could build
			i = 1
			while True:

				# check if there's enough resources for this number of robots
				can_build = (robot_costs * i) <= resource_counts
				if not can_build:
					break

				# remove necessary resources
				resource_counts -= robot_costs * i
				local_robot_type_set.remove(robot_type)

				# recursive call
				child_robot_count_combinations = self.get_robot_count_combinations(resource_counts, local_robot_type_set)

				# if there are no child robot count combinations, still add the current combination
				if len(child_robot_count_combinations) == 0:
					current_combination = ResourceSet()
					current_combination.add_to_resource(robot_type, i)
					robot_count_combinations.append(current_combination)	

				# every child combination should also have the current robots added to it
				for child_robot_count_combination in child_robot_count_combinations:
					child_robot_count_combination.add_to_resource(robot_type, i)
					robot_count_combinations.append(child_robot_count_combination)

				# add resources back that were used for this case
				resource_counts += robot_costs * i
				local_robot_type_set.add(robot_type)

				# see if one more robot could have been built with current resources
				i += 1

		cache[cache_key] = robot_count_combinations
		return robot_count_combinations
		

	# TODO will need caching like before
	# TODO should just decrement the robot count after the recursive call returns
	def get_child_states(self):
		# base case: we've run out of time
		if self.time_left == 0:
			return []

		child_states = []

		# TODO any new robots that were built
		# robot_count_combinations = self.get_robot_count_combinations(self.resource_counts)
		# print(f"Time: {self.time_left}")
		# print(f"Current resources")
		# print(f"---\n{self.resource_counts}\n---")
		# print(f"Robot combos: {len(robot_count_combinations)}")
		# print(f"Current robots:")
		# print(f"---\n{self.robot_counts}\n---")
		# print()

		robot_count_combinations = []
		for resource_type in RESOURCE_TYPES:
			if self.blueprint[resource_type] <= self.resource_counts:
				new_robot_combination = ResourceSet()
				new_robot_combination.add_to_resource(resource_type, 1)
				robot_count_combinations.append(new_robot_combination)

		# mine all new resources (should mine after considering robots that can be built)
		self.resource_counts += self.robot_counts

		# TODO  innefficient
		for robot_count_combination in robot_count_combinations:

			child_robot_counts = self.robot_counts + robot_count_combination

			# remove the resources needed for this robot count combination
			local_resource_counts = ResourceSet() + self.resource_counts
			for robot_type in RESOURCE_TYPES:
				local_resource_counts -= self.blueprint[robot_type] * robot_count_combination.get_resource(robot_type)

			# create child state for every combination of robots that could be built
			child_state = StatePart1(self.blueprint, self.time_left - 1, local_resource_counts, child_robot_counts)

			child_states.append(child_state)

		# always add child case where we build no robots but advance time
		child_states.append(StatePart1(self.blueprint, self.time_left - 1, self.resource_counts, self.robot_counts))

		# if len(child_states) > 10:
		# 	print(f"Returning {len(child_states)} child states at time {self.time_left}.")
		return child_states
	

	def get_max_geodes(self):
		# print()
		# print(f'-------{self.time_left}---------')
		
		child_states = self.get_child_states()
		current_geodes = self.robot_counts.get_resource('geode')

		if len(child_states) == 0:
			return current_geodes
	
		my_max = current_geodes
		for i, child_state in enumerate(child_states):

			if self.time_left == 21:
				print(f"{i + 1} of {len(child_states)}")
			
			temp = current_geodes + child_state.get_max_geodes()

			if self.time_left == 21:
				print(f"child geodes: {temp}")
				print()

			if temp > my_max:
				my_max = temp

		return my_max
			# return current_geodes + sum([child_state.get_max_geodes() for child_state in child_states])


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

	for blueprint in blueprints:
		resource_counts = ResourceSet()

		robot_counts = ResourceSet()
		robot_counts.add_to_resource('ore', 1)

		state_part_1 = StatePart1(blueprint, TOTAL_TIME, resource_counts, robot_counts)

		print(f"Answer 1: {state_part_1.get_max_geodes()}")
		
		print()

		# TODO remove
		break


