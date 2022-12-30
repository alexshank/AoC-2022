from helpers import load_data_grouped

def can_move(elves, test_square, mask):
	square_1 = mask[0] + test_square
	square_2 = mask[1] + test_square
	square_3 = mask[2] + test_square
	return square_1 not in elves and square_2 not in elves and square_3 not in elves

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

	up_mask = 0 + 1j
	down_mask = 0 - 1j
	left_mask =  -1 + 0j
	right_mask =  1 + 0j
	masks = [up_mask, down_mask, left_mask, right_mask]

	# # key is square to move to, value is list of elves wanting to move there
	# elf_moves = defaultdict(lambda: [])
	# # for round_num in range(10):
	# for round_num in range(10_000):

	# 	# for every elf square
	# 	for test_square in elves:

	# 		# TODO clean up. Check every direction
	# 		try_to_move = False
	# 		for i in range(len(masks)):
	# 			if not can_move(elves, test_square, masks[i]):
	# 				try_to_move = True
			
	# 		if try_to_move == False:
	# 			continue

	# 		# for every mask
	# 		for i in range(len(masks)):
	# 			current_mask = masks[(i + round_num) % len(masks)]
	# 			if can_move(elves, test_square, current_mask):
	# 				elf_moves[current_mask[1] + test_square].append(test_square)
	# 				break

	# 	elf_did_move = False
	# 	for destination_square, list_original_squares in elf_moves.items():
	# 		if len(list_original_squares) == 1:
	# 			elf_did_move = True
	# 			elves.remove(list_original_squares[0])
	# 			elves.add(destination_square)
	# 	elf_moves.clear()

	# 	# part 2 (answer: 925)
	# 	if not elf_did_move:
	# 		print('round number:')
	# 		print(round_num + 1)
	# 		break	

	results = ['R' + instructions[:2]]
	instructions = instructions[2:]
	previous_index = 0
	for i, v in enumerate(instructions):
		if not v.isdigit():
			results.append(instructions[previous_index:i])
			previous_index = i
	results.append(instructions[previous_index:])

	for r in results:
		print(r)

	print(results[0])




	# # part 1 (answer: )
	# print_board(board)
	# print(instructions)



	