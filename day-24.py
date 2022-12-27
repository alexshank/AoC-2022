from helpers import load_data

class State:
	def __init__(self, blizzards, traveler, destination, state_depth):
		self.blizzards = blizzards
		self.traveler = traveler
		# TODO always the same
		self.destination = destination
		self.state_depth = state_depth

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

	# TODO do we need better "not seen" logic?
# def not_already_seen(test_state, seen_states):
# 	for seen_state in seen_states:
# 		if test_state.traveler == seen_states.traveler:
# 			if test_state.blizzards in seen_state.blizzard:
# 	return True

def update_blizzard_locations(squares, board_width, board_height):
	result = {}
	for coord, symbols in squares.items():

		# TODO unsure if needed
		if len(symbols) == 0:
			# TODO it is... with the empty spaces
			# print('Is this happening?')
			# print(coord)
			continue

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

def possible_traveler_squares(updated_squares, traveler, destination, board_width, board_height):
	potential_squares = [traveler, traveler + complex(-1, 0), traveler + complex(1, 0), traveler + complex(0, -1),traveler + complex(0, 1)]

	result = []
	for potential_square in potential_squares:
		# TODO the potential_square == traveler just allows the elf to stay in the start position
		if (potential_square == destination) or (potential_square == traveler) or (potential_square.real >= 0 and potential_square.real < board_width and potential_square.imag >= 0 and potential_square.imag < board_height):
			# TODO I think this check creates extra entries in our map
			if potential_square not in updated_squares.keys():
				result.append(potential_square)
	return result

# TODO how can we distinguish states properly for "seen" flag?
def bfs(blizzards, traveler, destination, board_width, board_height):
	first_state = State(blizzards, traveler, destination, 0)
	queue = [first_state]
	seen_states = set() # TODO not sure this will work correctly

	while len(queue) > 0:
		current_state = queue.pop(0)

		if current_state.state_depth % 10 == 0:
			print(current_state.state_depth)
		
		if current_state.traveler == current_state.destination:
			return current_state.state_depth 

		new_blizzards = update_blizzard_locations(current_state.blizzards, board_width, board_height)

		potential_moves = possible_traveler_squares(new_blizzards, current_state.traveler, current_state.destination, board_width, board_height)
		for potential_move in potential_moves:
			new_state = State(new_blizzards, potential_move, destination, current_state.state_depth + 1)
			if new_state not in seen_states:
				seen_states.add(new_state)
				queue.append(new_state)
			else:
				print('already saw')

if __name__ == "__main__":
	data = load_data("day-24-test-input.txt")
	print()

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




