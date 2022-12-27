from helpers import load_data
from collections import defaultdict

# TODO General idea: Create a graph where each node is an entire state of the problem.
# This would mean each node keeps a record of:
# - the current minute in the simulation
#	- where every blizzard is currently located
# - where the traveler is currently located
# At every minute, we'll compute the next states/spaces we could move to
# Each potential state is added to the graph by a directed edge coming from the current node
# Finally, we run BFS on the graph, with the terminating condition being the traveler
# reaching the end coordinate
# Ideally this is fast enough for the given input size
# An important point: We don't have to create the graph and then traverse it. We can
# just create the new nodes as we are running BFS. This limits the runtime to 
# that of BFS (which is O(V+E)).

def print_board(squares, row_count, col_count):
	for y in reversed(range(row_count - 2)):
		for x in range(col_count - 2):
			# TODO hanlde overlaps
			if len(squares[complex(x, y)]) == 1:
				print(squares[complex(x, y)][0], end='')
			else:
				print(len(squares[complex(x, y)]), end='')
		print()

def update_blizzard_location(squares, blizzard_coordinate):
	board_width = 6
	board_height = 4
	# TODO could have multiple blizzards at each square
	# TODO need to handle not processing blizzards more than once 
	symbol = squares[blizzard_coordinate]
	match symbol:
		case '<':
			# TODO modulo compute x coordinate
			pass
		case '>':
			pass
		case 'v':
			pass
		case '^':
			pass
		case _: raise Exception('No bueno')

if __name__ == "__main__":
	data = load_data("day-24-test-input.txt")
	print()

	# load data into a data structure
	row_count = len(data)
	col_count = len(data[0])
	traveler = None
	destination = None
	squares = defaultdict(lambda: [])
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
					else:
						squares[complex(x - 1, y - 1)].append(symbol)
				case _:
						# should be the >, <, v, and ^ cases
						squares[complex(x - 1, y - 1)].append(symbol)
	print_board(squares, row_count, col_count)
	print(traveler)
	print(destination)

	# now move all blizzards one unit and check what traveler's options




