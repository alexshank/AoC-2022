from helpers import load_data_grouped
from visualize import pc
import time

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

	# print(current_location)
	# print(limits)
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
		case _:
			raise Exception()

	if board[test_location] == '.':
		return test_location
	elif board[test_location] == '#':
		return current_location
	else:
		print('DANGER')
		return None	

def print_board(x_board, current_location, arrow):
	min_x = int(min(x_board.keys(), key=lambda x: x.real).real)
	max_x = int(max(x_board.keys(), key=lambda x: x.real).real)
	min_y = int(min(x_board.keys(), key=lambda x: x.imag).imag)
	max_y = int(max(x_board.keys(), key=lambda x: x.imag).imag)

	# # view window of y's
	# min_y = max(min_y, int(current_location.imag) - 20)
	# max_y = min(max_y, int(current_location.imag) + 20)


	for y in reversed(range(min_y, max_y + 1)):
		print(f'{(max_y - y + 1):03} {y:03}', end='')
		for x in range(min_x - 1, max_x + 1):
			if complex(x, y) == current_location:
				pc(arrow, 'green', end='')
			elif complex(x, y) in x_board.keys():
				pc(x_board[complex(x, y)], 'red', end='')
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

	# for r in results[:40]:
	# 	print(r)

	y_max = max(board.keys(), key=lambda x: x.imag).imag
	x_min = min({x for x in board.keys() if x.imag == y_max}, key=lambda x: x.real).real
	current_location = complex(x_min, y_max)
	# print(current_location)

	# for round_num in range(10):
	direction_index = -1 # initialize based on known input
	directions = ['R', 'D', 'L', 'U']
	arrows = ['>', 'V', '<', '^']
	display_board = board.copy()
	for instruction in results:
		temp = list(instruction)
		# print(temp)
		direction = temp[0]
		if direction == 'R':
			direction_index += 1
		else:
			direction_index -= 1
		steps = int(''.join(temp[1:]))
		# print(steps)

		for i in range(steps):
			display_board[current_location] = arrows[direction_index % 4]
			new_position = can_move_again(board, directions[direction_index % 4], current_location)
			if new_position == current_location:
				break
			else:
				current_location = new_position

			# print_board(display_board, current_location, arrows[direction_index % 4])
			# time.sleep(0.1)
			# print("\033[J", end="")
			# print()
		

		
	print_board(display_board, current_location, arrows[direction_index % 4])


	# forgot to modulu and debugged for 4 hours :'(
	# TODO should have called direction_index direction_counter
	# part 1 (answer: 165094)
	print()
	print(current_location)
	print('row')
	print(row_count - (current_location.imag))
	print('col')
	print(current_location.real + 1)
	print('direction')
	print(directions[direction_index % 4])
	print(direction_index % 4)
	print(int(1000 * (row_count - (current_location.imag)) + 4 * (current_location.real + 1) + (direction_index % 4)))



	