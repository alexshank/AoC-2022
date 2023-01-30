from helpers import load_data, load_data_grouped

CHAMBER_WIDTH = 7
STARTING_X_COORD = 2	# left wall is between -1 and 0 x indices
LEFT = complex(-1, 0)
RIGHT = complex(1, 0)
DOWN = complex(0, -1)

# part 1: 2022 
# part 2: 1_000_000_000_000
ROCK_COUNT = 1_000_000_000_000


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


def rock_hit_wall_or_side_of_other_rock(rock_locations, rock_pile):
	for location in rock_locations:
		if location.real == -1 or location.real == CHAMBER_WIDTH or location in rock_pile:
			return True
	return False


def rock_has_stopped(rock_locations, rock_pile):
	for location in rock_locations:
		if location.imag == -1 or location in rock_pile:
			return True
	return False


def normalize_set(rock_pile, starting_position):
	result = set()
	min_y = 1_000_000_000_000 # arbitrary large number
	for coord in rock_pile:
		if coord.imag >= starting_position.imag - 300:
			result.add(coord)
			min_y = min(min_y, coord.imag)
	
	final = set()
	for r in result:
		final.add(complex(r.real, r.imag - min_y))
	
	# frozenset is an immutable built-in, meaning it can be hashed and added to a set
	return frozenset(final)
	


if __name__ == "__main__":
	wind_chars = load_data("day-17-input.txt")[0]	# TODO itertools should have an infinite iterator
	rocks = load_data_grouped("day-17-rock-input.txt")

	# parse rock definitions
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

	# parse cycular wind movements
	wind_movements = [LEFT if c == '<' else RIGHT for c in wind_chars]

	rock_pile = set()								# all coordinates containing a stopped rock
	pile_max_y = -1									# track the highest y coordinate in the pile set
	falling_rock = set()						# all coordinates containing the currently falling rock
	candidate_falling_rock = set()	# we move the falling rock, then check if new set is in a valid position
	rock_definition_index = 0				# rotate through rock definitions
	wind_movement_index = 0					# rotate through wind movements
	stopped_rock_count = 0					# track how many rocks we've dropped into the pile

	cached_sets = dict()						# we need to notice when the cycular pattern starts (keys are frozensets)
	start_of_cycle = None						# we are indexing by the "stopped rock count"
	first_repeated_placement = None # we are indexing by the "stopped rock count"
	last_pile_max_y = -1						# keep this to compute the change in pile height from last cycle element back to first

	while stopped_rock_count < ROCK_COUNT:
		starting_position = complex(STARTING_X_COORD, pile_max_y + 4)
		falling_rock = compute_rock_location(starting_position, rock_definitions[rock_definition_index])
		normalized_set = normalize_set(rock_pile, starting_position)

		if normalized_set in cached_sets:
			start_of_cycle = cached_sets[normalized_set][0]
			first_repeated_placement = stopped_rock_count
			break
		else:
			cached_sets[normalized_set] = (stopped_rock_count, pile_max_y + 1)

		rock_definition_index = (rock_definition_index + 1) % len(rock_definitions)

		rock_is_stopped = False
		while not rock_is_stopped:
			# blown by wind
			movement = wind_movements[wind_movement_index]
			wind_movement_index = (wind_movement_index + 1) % len(wind_movements)

			# check wall conditions
			candidate_falling_rock = move_rock(falling_rock, movement)
			if not rock_hit_wall_or_side_of_other_rock(candidate_falling_rock, rock_pile):
				falling_rock = candidate_falling_rock

			# move down 1
			candidate_falling_rock = move_rock(falling_rock, DOWN)

			# check stopping conditions
			if not rock_has_stopped(candidate_falling_rock, rock_pile):
				falling_rock = candidate_falling_rock
			else:
				rock_is_stopped = True
				stopped_rock_count += 1
				# TODO could probably get last diff in a cleaner/faster way
				last_pile_max_y = int(max(rock_pile, key=lambda x: x.imag, default=complex(0j)).imag)
				rock_pile = rock_pile.union(falling_rock)
				pile_max_y = int(max(rock_pile, key=lambda x: x.imag).imag)
	

	cycle_elements = [s for s in cached_sets.values() if s[0] >= start_of_cycle]
	cycle_length = len(cycle_elements)

	cycle_diffs = [cycle_elements[i+1][1] - cycle_elements[i][1] for i in range(cycle_length - 1)]
	cycle_diffs.append(pile_max_y - last_pile_max_y) # TODO could get this last diff in a cleaner way?
	cycle_pile_height = sum(cycle_diffs)

	rocks_to_go = ROCK_COUNT - first_repeated_placement
	cycles_needed = rocks_to_go // cycle_length
	remainder = rocks_to_go % cycle_length

	# part 1 (answer: 3127)
	# part 2 (answer: 1542941176480)
	answer = (pile_max_y + 1) + cycles_needed * cycle_pile_height + sum(cycle_diffs[:remainder])
	print(f'answer: {answer}')