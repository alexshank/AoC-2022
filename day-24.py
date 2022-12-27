from helpers import load_data

class State:
	def __init__(self, blizzards, traveler, state_depth):
		self.blizzards = blizzards
		self.traveler = traveler
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

# TODO how can we distinguish states properly for "seen" flag?
def bfs(blizzards, traveler, destination, board_width, board_height):
	first_state = State(blizzards, traveler, 0)
	queue = [first_state]
	seen_states = set() # TODO not sure this will work correctly
	
	# TODO remove
	traveler_set = set()
	previous_size = 0
	while len(queue) > 0:
		current_state = queue.pop(0)

		# TODO we're considering way too many paths. unique traveler locations are increasing, but slowly
		traveler_set.add(current_state.traveler)
		if len(traveler_set) > previous_size:
			previous_size = len(traveler_set)
			print('Unique traveler locations seen: ' + str(len(traveler_set)))
		# print(str(len(seen_states)))

		# TODO not even getting to depth 20 :O	
		if current_state.traveler == destination:
			return current_state.state_depth 

		new_blizzards = update_blizzard_locations(current_state.blizzards, board_width, board_height)

		potential_moves = possible_traveler_squares(new_blizzards, current_state.traveler, destination, board_width, board_height)
		for potential_move in potential_moves:
			new_state = State(new_blizzards, potential_move, current_state.state_depth + 1)

			# TODO this has to be crazy slow
			already_seen = False
			for state in seen_states:
				if are_states_equal(new_state, state):
					# print('already saw')
					already_seen == True
					break

			if not already_seen:
				seen_states.add(new_state)
				queue.append(new_state)

def are_states_equal(state_1, state_2):
	return state_1.traveler == state_2.traveler and state_1.blizzards == state_2.blizzards

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

	# test_dict_1 = {1: '1', 2: '2'}
	# test_dict_2 = {2: '2', 1: '1'}
	# traveler_1 = complex(2,2)
	# traveler_2 = complex(2,2)
	# destination_1 = complex(3,3)
	# destination_2 = complex(3,3)

	# test_state_1 = State(test_dict_1, traveler_1, destination_1, 5)
	# test_state_2 = State(test_dict_2, traveler_2, destination_2, 5)
	# print(test_state_1 == test_state_2)
	# print(are_states_equal(test_state_1, test_state_2))




