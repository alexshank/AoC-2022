from helpers import load_data_grouped

def compute_limits(board, x, y):
	row_keys = {key for key in board.keys() if key.imag == y}
	col_keys = {key for key in board.keys() if key.real == x}

	min_x = int(min(row_keys, key=lambda x: x.real).real)
	max_x = int(max(row_keys, key=lambda x: x.real).real)
	min_y = int(min(col_keys, key=lambda x: x.imag).imag)
	max_y = int(max(col_keys, key=lambda x: x.imag).imag)

	return min_x, max_x, min_y, max_y

def can_move_again(board, direction, current_location):
	
	limits = compute_limits(board, current_location.real, current_location.imag)

	print(current_location)
	print(limits)
	match direction:
		case 'R':
			test_location = current_location + complex(1, 0)
			if test_location.real > limits[1]:
				test_location = complex(limits[0], test_location.imag)
		
		case 'L':
			test_location = current_location + complex(-1, 0)
			if test_location.real < limits[0]:
				test_location = complex(limits[1], test_location.imag)

		case 'U':
			test_location = current_location + complex(0, 1)
			if test_location.imag > limits[3]:
				test_location = complex(test_location.real, limits[2])

		case 'D':
			test_location = current_location + complex(0, -1)
			if test_location.imag < limits[2]:
				test_location = complex(test_location.real, limits[3])

	if board[test_location] == '.':
				return test_location
	elif board[test_location] == '#':
				return current_location

def print_board(board):
	min_x = int(min(board.keys(), key=lambda x: x.real).real)
	max_x = int(max(board.keys(), key=lambda x: x.real).real)
	min_y = int(min(board.keys(), key=lambda x: x.imag).imag)
	max_y = int(max(board.keys(), key=lambda x: x.imag).imag)

	for y in reversed(range(min_y, max_y + 1)):
		for x in range(min_x - 1, max_x + 1):
			if complex(x, y) in board.keys():
				print(board[complex(x, y)], end='')
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

	masks = {
		'U': 0 + 1j,
		'D': 0 - 1j,
		'L': -1 + 0j,
		'R': 1 + 0j
	}

	results = ['R' + instructions[:2]]
	instructions = instructions[2:]
	previous_index = 0
	for i, v in enumerate(instructions[1:]):
		if not v.isdigit():
			results.append(instructions[previous_index:i + 1])
			previous_index = i + 1
	results.append(instructions[previous_index:])
	# print(results)

	y_max = max(board.keys(), key=lambda x: x.imag).imag
	x_min = min({x for x in board.keys() if x.imag == y_max}, key=lambda x: x.real).real
	current_location = complex(x_min, y_max)
	print(current_location)

	# for round_num in range(10):
	for instruction in results:
		temp = list(instruction)
		# print(temp)
		direction = temp[0]
		# print(direction)
		steps = int(''.join(temp[1:]))
		# print(steps)

		for i in range(steps):
			new_position = can_move_again(board, direction, current_location)
			if new_position == current_location:
				break
			else:
				current_location = new_position

	# # part 1 (answer: )
	print(current_location)



	