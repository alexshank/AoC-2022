from helpers import load_data, load_data_grouped

CHAMBER_WIDTH = 7
STARTING_X_COORD = 2	# left wall is between 0 and -1 x index

def compute_rock_location(complex_point, rock_definition):
	result = set()
	for offset in rock_definition:
		result.add(complex_point + offset)
	return result

def print_chamber(rock_pile, falling_rock, y_limit):
	for y in reversed(range(y_limit)):
		print('|', end='')
		for x in range(CHAMBER_WIDTH):
			if complex(x, y) in falling_rock:
				print('@', end='')
			elif complex(x, y) in rock_pile:
				print('#', end='')
			else:
				print('.', end='')
		print('|')
	print('+' + ('-' * CHAMBER_WIDTH) + '+')

def move_rock(rock_locations, movement):
	result = set()
	for location in rock_locations:
		result.add(location + movement)
	return result

# TODO or side of rock!
def rock_hit_wall(rock_locations, rock_pile):
	for location in rock_locations:
		if location.real == -1 or location.real == CHAMBER_WIDTH or location in rock_pile:
			return True
	return False

def rock_has_stopped(rock_locations, rock_pile):
	for location in rock_locations:
		if location.imag == -1 or location in rock_pile:
			return True
	return False

if __name__ == "__main__":
	wind_blows = load_data("day-17-input.txt")[0]	# TODO itertools should have an infinite iterator
	rocks = load_data_grouped("day-17-rock-input.txt")

	# a rock's location is represented by a set of complex coordinates
	# a rock definition is a set of complex coordinates defined from its bottom-left corner
	rock_definitions = []
	for rock in rocks:
		rock.reverse()
		temp_rock_set = set()
		for y, row in enumerate(rock):
			for x, character in enumerate(row):
				if character == '#':
					temp_rock_set.add(complex(x, y))
		rock_definitions.append(temp_rock_set)

	pile_height = -1	# floor is bewteen 0 and -1 y index
	
	rock_pile = set()	# all coordinates with a stopped rock
	falling_rock = set()	# all coordinates of the currently falling rock
	updated_falling_rock = set()	# we move the falling rock, then check if it's in a valid position


	# updated_falling_rock = move_rock(falling_rock, complex(0, -1))
	rock_definition_index = 0
	wind_blow_index = 0
	stopped_rock_count = 0

	y_distance_offset = 0
	Y_DISTANCE_THRESHOLD = 500

	# part 1 (answer: 3127)

	wind_movements = []
	for wind in wind_blows:
		match wind_blows[wind_blow_index]:
			case '<':
				movement = complex(-1, 0)
			case '>':
				movement = complex(1, 0)
		wind_movements.append(movement)

	# 1000000000000
	# 2022 
	while stopped_rock_count < 1_000_000_000_000:

		print(stopped_rock_count)

		starting_position = complex(STARTING_X_COORD, pile_height + 4)
		falling_rock = compute_rock_location(starting_position, rock_definitions[rock_definition_index])
		rock_definition_index += 1
		if rock_definition_index == 5:
			rock_definition_index = 0

		rock_not_stopped = True 
		while rock_not_stopped:

			# blown by wind
			movement = wind_movements[wind_blow_index]
			wind_blow_index += 1
			if wind_blow_index == len(wind_blows):
				wind_blow_index = 0

			# check wall conditions
			updated_falling_rock = move_rock(falling_rock, movement)
			if not rock_hit_wall(updated_falling_rock, rock_pile):
				falling_rock = updated_falling_rock

			# move down 1
			updated_falling_rock = move_rock(falling_rock, complex(0, -1))

			# check stopped condition
			if not rock_has_stopped(updated_falling_rock, rock_pile):
				falling_rock = updated_falling_rock
			else:
				rock_not_stopped = False
				stopped_rock_count += 1
				rock_pile = rock_pile.union(falling_rock)
				pile_height = int(max(rock_pile, key=lambda x: x.imag).imag)
				# falling_rock = set()	# TODO only clearing for printing
			
		if pile_height > 2 * Y_DISTANCE_THRESHOLD:
			# print()
			# print(rock_pile)
			# print('pile height')
			# print(pile_height)
			# print('y distance offset')
			# print(y_distance_offset)
			# print('y offset constant')
			# print(Y_DISTANCE_THRESHOLD)
			y_distance_offset += Y_DISTANCE_THRESHOLD
			pile_height -= Y_DISTANCE_THRESHOLD
			result = set()
			for location in rock_pile:
				if location.imag > Y_DISTANCE_THRESHOLD:
					result.add(complex(location.real, location.imag - Y_DISTANCE_THRESHOLD))
			rock_pile = result
			# print(rock_pile)


	# part 2 (answer: )
	print(y_distance_offset + pile_height + 1)

