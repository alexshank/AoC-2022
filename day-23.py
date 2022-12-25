from helpers import load_data
from collections import defaultdict

def can_move(elves, test_square, mask):
	square_1 = mask[0] + test_square
	square_2 = mask[1] + test_square
	square_3 = mask[2] + test_square
	return square_1 not in elves and square_2 not in elves and square_3 not in elves

def print_board(elves):
	min_x = int(min(elves, key=lambda x: x.real).real)
	max_x = int(max(elves, key=lambda x: x.real).real)
	min_y = int(min(elves, key=lambda x: x.imag).imag)
	max_y = int(max(elves, key=lambda x: x.imag).imag)

	for y in reversed(range(min_y, max_y + 1)):
		for x in range(min_x - 1, max_x + 1):
			if complex(x, y) in elves:
				print('#', end='')
			else:
				print('.', end='')
		print()

	area = int((max_y - min_y + 1) * (max_x - min_x + 1))
	print(area - len(elves))

if __name__ == "__main__":
	data = load_data("day-23-input.txt")

	row_count = len(data)
	col_count = len(data[0])
	elves = set()
	for y in range(row_count):
		for x in range(col_count):
			if data[row_count - 1 - y][x] == '#':
				elves.add(complex(x, y))

	north_mask = [-1 + 1j,  0 + 1j,  1 + 1j]
	south_mask = [-1 - 1j,  0 - 1j,  1 - 1j]
	west_mask =  [-1 + 1j, -1 + 0j, -1 - 1j]
	east_mask =  [ 1 + 1j,  1 + 0j,  1 - 1j]
	masks = [north_mask, south_mask, west_mask, east_mask]

	# key is square to move to, value is list of elves wanting to move there
	elf_moves = defaultdict(lambda: [])
	# for round_num in range(10):
	for round_num in range(10_000):

		# for every elf square
		for test_square in elves:

			# TODO clean up. Check every direction
			try_to_move = False
			for i in range(len(masks)):
				if not can_move(elves, test_square, masks[i]):
					try_to_move = True
			
			if try_to_move == False:
				continue

			# for every mask
			for i in range(len(masks)):
				current_mask = masks[(i + round_num) % len(masks)]
				if can_move(elves, test_square, current_mask):
					elf_moves[current_mask[1] + test_square].append(test_square)
					break

		elf_did_move = False
		for destination_square, list_original_squares in elf_moves.items():
			if len(list_original_squares) == 1:
				elf_did_move = True
				elves.remove(list_original_squares[0])
				elves.add(destination_square)
		elf_moves.clear()

		# part 2 (answer: 925)
		if not elf_did_move:
			print('round number:')
			print(round_num + 1)
			break	

	# part 1 (answer: 3871)
	# print_board(elves)



	