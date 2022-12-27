from helpers import load_data

def print_board(squares, x_count, y_count, traveler):
	for y in reversed(range(y_count)):
		for x in range(x_count):

			if complex(x, y) == traveler:
				print('T', end='')
			else:
				# TODO hanlde overlaps
				if len(squares[complex(x, y)]) == 1:
					print(squares[complex(x, y)][0], end='')
				elif len(squares[complex(x, y)]) == 0:
					print('.', end='')
				else:
					print(len(squares[complex(x, y)]), end='')
		print()

# TODO could speed up by updating blizzards in place?
def update_blizzard_locations(squares, board_width, board_height):
	result = {}
	for coord, symbols in squares.items():
		for symbol in symbols:
			match symbol:
				case '<':
					new_coord = complex((coord.real - 1) % board_width, coord.imag)
				case '>':
					new_coord = complex((coord.real + 1) % board_width, coord.imag)
				case 'v':
					new_coord = complex(coord.real, (coord.imag - 1) % board_height)
				case '^':
					new_coord = complex(coord.real, (coord.imag + 1) % board_height)
				case _: raise Exception(symbol)

			if new_coord not in result.keys():
				result[new_coord] = [symbol]
			else:
				result[new_coord].append(symbol)

	return result

# TODO this is likely slow
def possible_traveler_squares(updated_squares, traveler, destination, board_width, board_height):
	result = []
	potential_squares = [traveler, traveler + complex(-1, 0), traveler + complex(1, 0), traveler + complex(0, -1),traveler + complex(0, 1)]
	for potential_square in potential_squares:
		# TODO the potential_square == traveler just allows the elf to stay in the start position
		if (potential_square == destination) or (potential_square == traveler) or (potential_square.real >= 0 and potential_square.real < board_width and potential_square.imag >= 0 and potential_square.imag < board_height):
			if potential_square not in updated_squares.keys():
				result.append(potential_square)
	return result

def bfs(blizzards, traveler, destination, board_width, board_height):

	blizzard_cache = {0: blizzards}

	# our nodes / states are a given position at a given time
	queue = [(traveler, 0)]
	seen_states = set()
	
	while len(queue) > 0:

		position, time = queue.pop(0)

		if position == destination:
			return time

		if time + 1 not in blizzard_cache.keys():
			blizzard_cache[time + 1] = update_blizzard_locations(blizzard_cache[time], board_width, board_height)
		new_blizzards = blizzard_cache[time + 1]

		potential_moves = possible_traveler_squares(new_blizzards, position, destination, board_width, board_height)
		for potential_move in potential_moves:
			new_state = (potential_move, time + 1)
			if new_state not in seen_states:
				seen_states.add(new_state)
				queue.append(new_state)

if __name__ == "__main__":
	data = load_data("day-24-input.txt")

	# load data into a data structure
	row_count = len(data)
	col_count = len(data[0])
	traveler = None
	destination = None
	squares = {}
	for y in range(row_count):
		for x in range(col_count):
			symbol = data[row_count - 1 - y][x]
			match symbol:
				case '#':
					pass
				case '.':
					if y == 0:
						destination = complex(x - 1, y - 1)
					elif y == row_count - 1:
						traveler = complex(x - 1, y - 1)
				# should be the >, <, v, and ^ cases
				case _:
					squares[complex(x - 1, y - 1)] = [symbol]

	# the width and height of the board without walls
	x_count = col_count - 2
	y_count = row_count - 2

	print(bfs(squares, traveler, destination, x_count, y_count))


