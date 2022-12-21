from helpers import load_data

if __name__ == "__main__":
	# parse data
	data = load_data("day-18-input.txt")
	lava_drops = set()
	for d in data:
		x, y, z = d.split(',')
		lava_drops.add((int(x), int(y), int(z)))

	# part 1 (answer: 4364)
	untouched_sides = 0
	for x, y, z in lava_drops:
		if (x + 1, y, z) not in lava_drops:
			untouched_sides += 1
		if (x - 1, y, z) not in lava_drops:
			untouched_sides += 1
		if (x, y + 1, z) not in lava_drops:
			untouched_sides += 1
		if (x, y - 1, z) not in lava_drops:
			untouched_sides += 1
		if (x, y, z + 1) not in lava_drops:
			untouched_sides += 1
		if (x, y, z - 1) not in lava_drops:
			untouched_sides += 1
	print(untouched_sides)

	# part 2 (answer: )
	x_y_coverage = {}

	for x in range(22):
		for y in range(22):
			x_y_coverage[(x, y)] = min


	y_z_coverage = set()
	x_z_coverage = set()
	for z in range(22):
		x_y_coverage.add((x, y))
		y_z_coverage.add((y, z))
		x_z_coverage.add((x, z))
	print(2 * len(x_y_coverage) + 2 * len(y_z_coverage) + 2 * len(x_z_coverage))








