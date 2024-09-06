from helpers import load_data

def adjacent_cubes(x, y, z):
	return [(x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)]

def count_touching_edges(set_a, set_b):
	result = 0
	for point_a in set_a:
		for test_point in adjacent_cubes(*point_a):
			if test_point in set_b:
				result += 1
	return result

# bfs "expands" the outside air around the lava blob
def bfs(full_space, lava_drops):
	outside_air = set()
	queue = [(-5, -5, -5)] # space we know is outside of lava
	while len(queue) > 0:
		for point in adjacent_cubes(*queue.pop(0)):
			if point not in full_space:
				continue

			if point not in lava_drops and point not in outside_air:
				outside_air.add(point)
				queue.append(point)
	return outside_air
	
if __name__ == "__main__":
	data = load_data("day-18-input.txt")
	lava_drops = {tuple(map(int, d.split(','))) for d in data}

	# comprehensive set is inefficient, but allows us to ignore edge conditions
	LOWER_LIMIT, UPPER_LIMIT = -10, 30
	full_space = set()
	for x in range(LOWER_LIMIT, UPPER_LIMIT):
		for y in range(LOWER_LIMIT, UPPER_LIMIT):
			for z in range(LOWER_LIMIT, UPPER_LIMIT):
				full_space.add((x, y, z))
	non_lava = full_space - lava_drops

	# part 1 (answer: 4364)
	print(count_touching_edges(lava_drops, non_lava))

	# part 2 (answer: 2508)
	outside_air = bfs(full_space, lava_drops)
	print(count_touching_edges(outside_air, lava_drops))

