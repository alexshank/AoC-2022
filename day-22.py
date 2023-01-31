from helpers import load_data_grouped
from visualize import pc

# TODO not used
MOVEMENT_MASKS = {
	'U': 0 + 1j,
	'D': 0 - 1j,
	'L': -1 + 0j,
	'R': 1 + 0j
}


SIDES = {
	0: (50, 99, 150, 199),
	1: (100, 149, 150, 199),
	2: (50, 99, 100, 149),
	3: (50, 99, 50, 99),
	4: (0, 49, 50, 99),
	5: (0, 49, 0, 49)
}

SIDE_LENGTH = 50

def orient_right(relative_coord, x_coord):
	return complex(x_coord, SIDE_LENGTH - relative_coord.real - 1)

def orient_left(relative_coord, y_coord):
	return complex(SIDE_LENGTH - relative_coord.imag - 1, y_coord)

def orient_flip(relative_coord, x_coord):
	return complex(x_coord, SIDE_LENGTH - relative_coord.imag - 1)

# if we go from side k to side j, find out what transition we need to make
transition_matrix = {
	# TODO could use partial function application here :)
	(0, 4): (orient_flip, 2, SIDES[4][0]), # flip orientation, increment direction index twice, use side 4 x_min
	(0, 5): (orient_right, 1, SIDES[5][0]),

	(1, 2): (orient_right, 1, SIDES[2][1]),
	(1, 3): (orient_flip, 2, SIDES[3][1]),

	(2, 1): (orient_left, -1, SIDES[1][2]),
	(2, 4): (orient_left, -1, SIDES[4][3]),

	(3, 1): (orient_flip, 2, SIDES[1][1]),
	(3, 5): (orient_right, 1, SIDES[5][1]),

	(4, 0): (orient_flip, 2, SIDES[0][0]),
	(4, 2): (orient_right, 1, SIDES[2][0]),

	(5, 0): (orient_left, -1, SIDES[0][3]),
	(5, 3): (orient_left, -1, SIDES[3][2])
}

# keep track of sides you transition to going out of current square left, up, right, or down
SIDE_TO_SIDE = {
	0: [4, 5, 1, 2],
	1: [0, 5, 3, 2],
	2: [4, 0, 1, 3],
	3: [4, 2, 1, 5],
	4: [0, 2, 3, 5],
	5: [0, 4, 3, 1],
}

def compute_destination_side(candidate_relative_coord, current_side):
	print(f'candidate rel: {candidate_relative_coord} : {current_side}')
	if candidate_relative_coord.real < 0:
		return SIDE_TO_SIDE[current_side][0]
	elif candidate_relative_coord.real == SIDE_LENGTH:
		return SIDE_TO_SIDE[current_side][2]
	elif candidate_relative_coord.imag < 0:
		return SIDE_TO_SIDE[current_side][3]
	elif candidate_relative_coord.imag == SIDE_LENGTH:
		return SIDE_TO_SIDE[current_side][1]
	else:
		return current_side

# TODO could cache this computation
def compute_limits(board, x, y):
	row_keys = {key for key in board.keys() if key.imag == y}
	col_keys = {key for key in board.keys() if key.real == x}

	min_x = int(min(row_keys, key=lambda x: x.real).real)
	max_x = int(max(row_keys, key=lambda x: x.real).real)
	min_y = int(min(col_keys, key=lambda x: x.imag).imag)
	max_y = int(max(col_keys, key=lambda x: x.imag).imag)

	return min_x, max_x, min_y, max_y

def get_new_rel_location(abs_coord, side):
	return complex(abs_coord.real - SIDES[side][0], abs_coord.imag - SIDES[side][2],)

def can_move_again(board, direction, current_abs_location, current_side, relative_location, direction_index):
	
	print(f'current abs: {current_abs_location}')
	print(f'direction: {direction}')
	print(f'current side: {current_side}')
	print(f'relative loc: {relative_location}')
	print(f'direction index: {direction_index}')

	test_relative_location = relative_location + MOVEMENT_MASKS[direction]

	test_destination_side = compute_destination_side(test_relative_location, current_side)
	print(f'test destination side: {test_destination_side}')

	print(f'tuple: {(current_side, test_destination_side)}')

	if (current_side, test_destination_side) not in transition_matrix:
		# no transformation needed
		direction_increment = 0
		test_transformed_relative_location = get_new_rel_location(current_abs_location + MOVEMENT_MASKS[direction], test_destination_side)

		# TODO still need to update relative coords here!!!

		print(f'Going from/to {(current_side, test_destination_side)} without transformation')
	else:
		print(f'Going from/to {(current_side, test_destination_side)}')
		orient_func, direction_increment, orient_arg_1 = transition_matrix[(current_side, test_destination_side)]
		print(f'orient func: {orient_func}')
		print(f'direction_increment: {direction_increment}')
		print(f'orient arg 1: {orient_arg_1}')
		test_transformed_relative_location = orient_func(test_relative_location, orient_arg_1)

	test_abs_location = complex(SIDES[test_destination_side][0], SIDES[test_destination_side][2])
	test_abs_location = test_abs_location + test_transformed_relative_location

	print(test_abs_location)
	print('-----')

	if board[test_abs_location] == '.':
		return test_abs_location, test_transformed_relative_location, direction_index + direction_increment, test_destination_side
	elif board[test_abs_location] == '#':
		return current_abs_location, relative_location, direction_index, current_side
	else:
		raise Exception('no bueno')

def in_range(complex_point, limits):
	result = True
	result = result and complex_point.real >= limits[0]
	result = result and complex_point.real <= limits[1]
	result = result and complex_point.imag >= limits[2]
	result = result and complex_point.imag <= limits[3]
	return result

def print_board(x_board, current_location, arrow, side_number):
	min_x = int(min(x_board.keys(), key=lambda x: x.real).real)
	max_x = int(max(x_board.keys(), key=lambda x: x.real).real)
	min_y = int(min(x_board.keys(), key=lambda x: x.imag).imag)
	max_y = int(max(x_board.keys(), key=lambda x: x.imag).imag)

	# # view window of y's
	# min_y = max(min_y, int(current_location.imag) - 20)
	# max_y = min(max_y, int(current_location.imag) + 20)

	print(f'current location while printing board: {current_location}')
	for y in reversed(range(min_y, max_y + 1)):
		print(f'{(max_y - y + 1):03} {y:03}', end='')
		for x in range(min_x - 1, max_x + 1):
			if complex(x, y) == current_location:
				pc(arrow, 'green', end='')
			elif in_range(complex(x, y), SIDES[side_number]):
				pc(x_board[complex(x, y)], 'blue', end='')
			elif complex(x, y) in x_board.keys():
				pc(x_board[complex(x, y)], 'yellow', end='')
			else:
				print(' ', end='')
		print()


if __name__ == "__main__":
	data, instructions = load_data_grouped("day-22-input.txt")
	instructions = instructions[0]

	# TODO can we re-use common "board looking input" logic?
	row_count = len(data)
	col_count = len(data[0])
	board = {}
	for y in range(row_count):
		data_y_index = row_count - 1 - y
		for x in range(len(data[data_y_index])):
			if data[data_y_index][x] != ' ':
				board[complex(x, y)] = data[data_y_index][x]

	# parse instructions in to ['R42', 'L43', ...]
	results = ['R' + instructions[:2]]
	instructions = instructions[2:]
	previous_index = 0
	for i, v in enumerate(instructions[1:]):
		if not v.isdigit():
			results.append(instructions[previous_index:i + 1])
			previous_index = i + 1
	results.append(instructions[previous_index:])

	# TODO move into function (used in compute... function above)
	y_max = max(board.keys(), key=lambda x: x.imag).imag
	x_min = min({x for x in board.keys() if x.imag == y_max}, key=lambda x: x.real).real
	current_abs_location = complex(x_min, y_max)
	print(current_abs_location)

	# TODO also maintain relative position
	current_side = 0
	relative_location = complex(0, SIDE_LENGTH - 1)

	display_board = board.copy()


	direction_index = -1 # initialize to U since first instruction is to turn to R
	directions = ['R', 'D', 'L', 'U']
	arrows = ['>', 'V', '<', '^']
	for counter, instruction in enumerate(results):

		temp = list(instruction)
		direction = temp[0]
		if direction == 'R':
			direction_index += 1
		else:
			direction_index -= 1
		steps = int(''.join(temp[1:]))

		for i in range(steps):
			display_board[current_abs_location] = arrows[direction_index % 4]

			# TODO may need to get back the new direction index and current side
			new_abs_position, new_rel_position, new_direction_index, new_side = can_move_again(board, directions[direction_index % 4], current_abs_location, current_side, relative_location, direction_index)
			if new_abs_position == current_abs_location:
				break
			else:
				current_abs_location = new_abs_position
				relative_location = new_rel_position
				direction_index = new_direction_index
				current_side = new_side
			
		print_board(display_board, current_abs_location, arrows[direction_index % 4], current_side)

		if counter == 600:
			break


	
	# part 1 (answer: 165094)
	print(int(1000 * (row_count - (current_abs_location.imag)) + 4 * (current_abs_location.real + 1) + (direction_index % 4)))



	