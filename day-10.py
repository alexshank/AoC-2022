from helpers import load_data

if __name__ == "__main__":
	data = load_data("day-10-input.txt")

	cycle_counter = 0
	x_register = 1
	cycle_dict = {0: ('na', 1)}	# cycle number: (instruction, value AFTER cycle)
	for datum in data:
		if datum.startswith('noop'):
			cycle_dict[(cycle_counter := cycle_counter + 1)] = ('noop', x_register)
		else:
			add_value = int(datum.split(' ')[1])
			cycle_dict[(cycle_counter := cycle_counter + 1)] = ('addx', x_register)
			cycle_dict[(cycle_counter := cycle_counter + 1)] = ('addx', x_register := x_register + add_value)
	
	# part 1
	result = 0
	for i in [20, 60, 100, 140, 180, 220]:
		result += i * cycle_dict[i - 1][1]
	print(result)

	# part 2
	for current_pixel in range(len(cycle_dict) - 1): # we added an initial state
		current_cycle = current_pixel + 1
		current_center_x_position = cycle_dict[current_pixel][1]
		current_sprite_positions = [current_center_x_position - 1, current_center_x_position, current_center_x_position + 1]

		if current_pixel % 40 in current_sprite_positions:
			print('#', end='')
		else:
			print('.', end='')

		if current_cycle % 40 == 0:
			print()


