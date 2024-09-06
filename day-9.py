from helpers import load_data

if __name__ == "__main__":
	data = load_data("day-9-input.txt")

	head = (0,0)
	tail = (0,0)
	tail_positions = set()

	for datum in data:
		direction, count = datum[0], int(datum[2:])
		for i in range(count):
			match direction:
				case 'U': head = (head[0], head[1] + 1)
				case 'D': head = (head[0], head[1] - 1)
				case 'L': head = (head[0] - 1, head[1])
				case 'R': head = (head[0] + 1, head[1])
			
			# always put the tail on the same col or row as head if it moves (handles diagonals)
			x_diff = head[0] - tail[0]
			y_diff = head[1] - tail[1]
			match x_diff, y_diff:
				case 2, _: tail = (tail[0] + 1, head[1])
				case -2, _: tail = (tail[0] - 1, head[1])
				case _, 2: tail = (head[0], tail[1] + 1)
				case _, -2: tail = (head[0], tail[1] - 1)
			
			tail_positions.add(tail)

	# part 1
	print(len(tail_positions))


	# part 2
	rope = [(0,0) for _ in range(10)] # head is index 9
	tail_positions = set() # tail is index 0

	for datum in data:
		direction, count = datum[0], int(datum[2:])
		for i in range(count):
			match direction:
				case 'U': rope[9] = (rope[9][0], rope[9][1] + 1)
				case 'D': rope[9] = (rope[9][0], rope[9][1] - 1)
				case 'L': rope[9] = (rope[9][0] - 1, rope[9][1])
				case 'R': rope[9] = (rope[9][0] + 1, rope[9][1])
				
			for j in reversed(range(1, len(rope))):
				# always put the tail on the same col or row as head if it moves (handles diagonals)
				x_diff = rope[j][0] - rope[j - 1][0]
				y_diff = rope[j][1] - rope[j - 1][1]
				match x_diff, y_diff:
					# can now have diagonals
					case 2, 2: rope[j - 1] = (rope[j - 1][0] + 1, rope[j - 1][1] + 1)
					case -2, 2: rope[j - 1] = (rope[j - 1][0] - 1, rope[j - 1][1] + 1)
					case -2, -2: rope[j - 1] = (rope[j - 1][0] - 1, rope[j - 1][1] - 1)
					case 2, -2: rope[j - 1] = (rope[j - 1][0] + 1, rope[j - 1][1] - 1)

					case 2, _: rope[j - 1] = (rope[j - 1][0] + 1, rope[j][1])
					case -2, _: rope[j - 1] = (rope[j - 1][0] - 1, rope[j][1])
					case _, 2: rope[j - 1] = (rope[j][0], rope[j - 1][1] + 1)
					case _, -2: rope[j - 1] = (rope[j][0], rope[j - 1][1] - 1)
				
			tail_positions.add(rope[0])
			
			# print board
			# x_min = min([x[0] for x in rope])
			# x_max = max([x[0] for x in rope])
			# y_min = min([x[1] for x in rope])
			# y_max = max([x[1] for x in rope])
			# print('------')
			# print('After ' + direction + ' - ' + str(i + 1))
			# print('------')
			# for y in reversed(range(y_min, y_max + 1)):
			# 	for x in range(x_min, x_max+1):
			# # for y in reversed(range(-5, 20)):
			# # 	for x in range(-20, 20):
			# 		if (x,y) in rope:
			# 			# print('X', end='')
			# 			# print highest index in position
			# 			for m in reversed(range(len(rope))):
			# 				if rope[m] == (x,y):
			# 					if m == 9:
			# 						print('H', end='')
			# 					elif m == 0:
			# 						print('T', end='')
			# 					else:
			# 						print(str(len(rope) - 1 - m), end='')
			# 					break
			# 		else:
			# 			print('.', end='')
			# 	print()

	# part 2
	print(len(tail_positions))