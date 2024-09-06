from helpers import load_data

if __name__ == "__main__":
	data = load_data("day-14-input.txt")
	data = [d.split(' -> ') for d in data]

	rock_map = {}
	x_min, x_max = 1000, 0
	y_min, y_max = 1000, 0
	for move_list in data:

		for i in range(1, len(move_list)):
			start_x, start_y = [int(x) for x in move_list[i - 1].split(',')]
			stop_x, stop_y = [int(y) for y in move_list[i].split(',')]

			x_min = min(x_min, start_x, stop_x)
			x_max = max(x_max, start_x, stop_x)
			y_min = min(y_min, start_y, stop_y)
			y_max = max(y_max, start_y, stop_y)

			x_diff = stop_x - start_x
			y_diff = stop_y - start_y
			x_mult = 1 if stop_x > start_x else -1
			y_mult = 1 if stop_y > start_y else -1

			if x_diff != 0:
				for n in range(abs(x_diff) + 1):
					rock_map[complex(start_x + x_mult * n, start_y)] = '#'
			elif y_diff != 0:
				for n in range(abs(y_diff) + 1):
					rock_map[complex(start_x, start_y + y_mult * n)] = '#'
	
	rock_map[complex(500,0)] = '+'

	def print_rock_map():
		print()
		for i in range(0, y_max + 1 + 3):
			print(str(i) + ' ', end='')
			for j in range(x_min - 100, x_max + 1 + 100):
				if complex(j, i) in rock_map.keys():
					print(rock_map[complex(j, i)], end='')
				else:
					print('.', end='')
			print()
		print()


	def get_next_location():
		location = complex(500, 0)
		while True:


			# should never hit in part 2
			# if location.imag > y_max:
			# 	return None

			# elif
			if location + 0 + 1j not in rock_map.keys():
				location += 0 + 1j
			# TODO don't think we need edge conditions
			# elif location.real - 1 >= x_min and location - 1 + 1j not in rock_map.keys():
			elif location - 1 + 1j not in rock_map.keys():
				location += -1 + 1j
			# elif location.real + 1 <= x_max and location + 1 + 1j not in rock_map.keys():
			elif location + 1 + 1j not in rock_map.keys():
				location += 1 + 1j
			else:
				# part 2 edge case, we can't move at all from start location
				if location == complex(500, 0):
					return None

				break

		return location	


	# part 1 (answer: 901)
	# count = 0
	# while (location := get_next_location()) != None:
	# 	rock_map[location] = 'O'
	# 	count += 1
	# print_rock_map()
	# print(count)


	# part 2 (answer: 24589)
	for k in range(x_min - 200, x_max + 200):
		rock_map[complex(k, y_max + 2)] = '#'

	count = 0
	while (location := get_next_location()) != None:
		rock_map[location] = 'O'
		count += 1
	print_rock_map()
	print(count + 1)







