from helpers import load_data

def manhattan_distance(p1, p2):
	return int(abs(p1.real - p2.real) + abs(p1.imag - p2.imag))

def x_pairs_for_row(sensor_dist_dict, row_to_check, with_constraints = False):
	return [ \
		x_pair \
		for sensor, beacon_dist in sensor_dist_dict.items() \
		if (x_pair := compute_x_pair(sensor, row_to_check, beacon_dist, with_constraints)) != None \
	]

# If a row intersects a circle (defined by the sensor and beacon pair),
# then there will be two x coordinates defined by the intersection.
# All x coordinates between these intersections cannot contain beacons
def compute_x_pair(sensor, row_y, closest_beacon_dist, with_constraints = False):
		y_diff = abs(sensor.imag - row_y)

		if y_diff > closest_beacon_dist:
			return None
		else:
			min_x = sensor.real - (closest_beacon_dist - y_diff)
			max_x = sensor.real + (closest_beacon_dist - y_diff)

			if with_constraints:
				min_x = max(min_x, 0)
				max_x = min(max_x, 4_000_000)

			return (int(min_x), int(max_x))

def count_ineligble_squares(reduced_x_pairs):
	return sum([x2 - x1 for x1, x2 in reduced_x_pairs])

# take x pairs (1, 5), (3, 13) --> (1, 13)
def reduce_x_pairs(x_pairs):
		x_pairs.sort(key = lambda x: x[0])
		i = 1
		while i < len(x_pairs):
			x2 = x_pairs[i]
			x1 = x_pairs[i - 1]
			if x2[0] <= x1[1]:
				x_pairs[i] = (min(x1[0], x2[0]), max(x1[1], x2[1]))
				del x_pairs[i - 1]
				i = 1
			else:
				i += 1
		return x_pairs

if __name__ == "__main__":
	data = load_data("day-15-input.txt")
	data = [d.replace('Sensor at x=', '') for d in data]
	data = [d.replace(' y=', '') for d in data]
	data = [d.replace(' closest beacon is at x=', '') for d in data]
	data = [d.split(':') for d in data]

	sensor_dict = {}
	for d in data:
		sensor_x, sensor_y = [int(x) for x in d[0].split(',')]
		beacon_x, beacon_y = [int(x) for x in d[1].split(',')]
		sensor_dict[complex(sensor_x, sensor_y)] = complex(beacon_x, beacon_y)

	sensor_dist_dict = {k: manhattan_distance(k, v) for k, v in sensor_dict.items()}

	# part 1 (answer: 5112034)
	row_to_check = 2_000_000
	reduced_x_pairs = reduce_x_pairs(x_pairs_for_row(sensor_dist_dict, row_to_check))
	print(count_ineligble_squares(reduced_x_pairs))

	# part 2 (answer: 13172087230812)
	coordinate_limit =  4_000_000
	for y in range(coordinate_limit + 1):
		reduced_x_pairs = reduce_x_pairs(x_pairs_for_row(sensor_dist_dict, y, with_constraints = True))

		if count_ineligble_squares(reduced_x_pairs) < coordinate_limit:
			print(reduced_x_pairs)
			print('y: ' + str(y))
			print('x: ' + str(x := reduced_x_pairs[0][1] + 1))
			print(str(x * coordinate_limit + y))
			break
		
		if y % 100_000 == 0:
			print('Currently at: ' + str(y))
