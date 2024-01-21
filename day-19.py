from helpers import load_data

RESOURCE_TYPES = ['geode', 'obsidian', 'clay', 'ore']
TOTAL_TIME = 24

# TODO move cache out of global space
cache = {}	

"""
Helper class for custom addition and multiplication operators
"""
class ResourceSet:
	def __init__(self):
		self.ore = 0
		self.obsidian = 0
		self.clay = 0
		self.geode = 0
		

	def __init__(self, resource_dictionary):
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
		

	def get_resource(self, resource, amount):
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
	
	def __mul__(self, scalar):
		if isinstance(scalar, int):
			return ResourceSet({
				'ore': self.ore * scalar,
				'obsidian': self.obsidian * scalar,
				'clay': self.clay * scalar,
				'geode': self.geode * scalar,
			})
		else:
			raise ValueError("Unsupported operand type for *")
		
	def __str__(self):
		return "Not Implemented."


"""
Class to represent the different states of the simulation that need to be considered
"""
class StatePart1:
	def __init__(self, blueprint, time_left, resource_counts, robot_counts, robot_type_set):
		self.blueprint = blueprint
		self.time_left = time_left
		self.resource_counts = resource_counts
		self.robot_counts = robot_counts
		# TODO don't think this needs to be a property
		self.robot_type_set = robot_type_set
	

	# TODO shouldn't be mixing up self properties and non-self properties. Make pure function

	# find every way we could spend all the current resources to build robots
	# returns list of dictionaries with number of robots of each resource type that could be built
	# i.e., [{'ore': 4, 'osidian': 0, ... }, {'ore': 3, 'osidian': 0, ... }, ... ]
	def get_robot_combinations(self, resource_counts, robot_type_set):

		set_string = "-".join([t for t in robot_type_set])
		resource_string = "-".join([str(k) for k in resource_counts.values()])
		cache_key = f"{set_string}-{resource_string}"
		if cache_key in cache:
			return cache[cache_key]

		robot_combinations = []

		# TODO should not modify this set while iterating over it
		local_robot_type_set = set([s for s in robot_type_set])
		for robot_type in robot_type_set:
			robot_costs = self.blueprint[robot_type]

			# determine how many robots of the given type we could build
			i = 1
			while True:

				can_build = all([(robot_costs[resource_type] * i) <= resource_counts[resource_type] for resource_type in RESOURCE_TYPES])	
				if not can_build:
					break

				# TODO could move above loop?
				for resource_type in RESOURCE_TYPES:
					resource_counts[resource_type] -= robot_costs[resource_type] * i
				local_robot_type_set.remove(robot_type)

				child_robot_combinations = self.get_robot_combinations(resource_counts, local_robot_type_set)

				# TODO if there's no children... still add
				if len(child_robot_combinations) == 0:
					current_combination = {resource_type: 0 for resource_type in RESOURCE_TYPES}
					current_combination[robot_type] += i # TODO think this can just be equals, not add
					robot_combinations.append(current_combination)	

				for child_robot_combination in child_robot_combinations:
					for resource_type in RESOURCE_TYPES:
						child_robot_combination[robot_type] += i # TODO think this can just be equals, not add
					robot_combinations.append(child_robot_combination)

				for resource_type in RESOURCE_TYPES:
					resource_counts[resource_type] += robot_costs[resource_type] * i
				local_robot_type_set.add(robot_type)

				i += 1

		cache[cache_key] = robot_combinations
		return robot_combinations
		

	# TODO will need caching like before
	# TODO should just decrement the robot count after the recursive call returns
	def get_child_states(self):
		# base case: we've run out of time
		if self.time_left == 0:
			return []

		child_states = []

		# mine all new resources
		for robot_type, robot_count in self.robot_counts.items():

			# TODO blueprints should be a dictionary of nested ResourceSet
			robot_blueprint = self.blueprint[robot_type]


			for resource_type in RESOURCE_TYPES:
				self.resource_counts[resource_type] += self.blueprint[robot_type][resource_type] * robot_count


		# TODO any new robots that were built
		robot_combinations = self.get_robot_combinations(self.resource_counts, self.robot_type_set)
		print(self.time_left)
		print(self.resource_counts)
		print(len(robot_combinations))
		print()


		# TODO  innefficient
		robot_type_set = set([resource_type for resource_type in RESOURCE_TYPES])
		for robot_count_combination in robot_combinations:


			robot_counts = {resource_type: self.robot_counts[resource_type] + robot_count_combination[resource_type] for resource_type in RESOURCE_TYPES}

			# TODO probably shouldn't be recomputing this
			resource_counts = {resource_type: self.resource_counts[resource_type] for resource_type in RESOURCE_TYPES}
			for robot_type in RESOURCE_TYPES:
				for local_resource_type in RESOURCE_TYPES:
					resource_counts[local_resource_type] -= robot_count_combination[robot_type] * self.blueprint[robot_type][local_resource_type]
			child_state = StatePart1(self.blueprint, self.time_left - 1, resource_counts, robot_counts, robot_type_set)

			child_states.append(child_state)

		# build no robots but advance time
		if len(robot_combinations) == 0:
			child_states.append(StatePart1(self.blueprint, self.time_left - 1, self.resource_counts, self.robot_counts, self.robot_type_set))

		# TODO call combination function
		# TODO there are no children / candidates at all

		if len(child_states) == 0:
			print("returning no child states")

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
			if self.time_left == 24:
				print(f"{i + 1} of {len(child_states)}")
			
			temp = current_geodes + child_state.get_max_geodes()

			if self.time_left == 24:
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
			for resource_cost in resource_costs:
				cost, resource_type = resource_cost.split(" ")
				blueprint[robot_type][resource_type] += int(cost)
		blueprints.append(blueprint)
	return blueprints

	
if __name__ == "__main__":
	lines = load_data("day-19-test-input.txt")
	blueprints = build_blueprint_dictionaries(lines)
	blueprints = [ResourceSet(b) for b in blueprints]

	for blueprint in blueprints:
		resource_counts = ResourceSet()

		robot_counts = ResourceSet()
		robot_counts.add_to_resource('ore', 1)

		robot_type_set = set([resource_type for resource_type in RESOURCE_TYPES])
		state_part_1 = StatePart1(blueprint, TOTAL_TIME, resource_counts, robot_counts, robot_type_set)

		print(state_part_1.get_max_geodes())
		
		print()


