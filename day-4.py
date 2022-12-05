from helpers import load_data

if __name__ == "__main__":
	# take each line "19-24,45-67" -> [19, 24, 45, 67]
	data = load_data("day-4-input.txt")
	data = [x.replace(',', '-').split('-') for x in data]
	data = [list(map(lambda s: int(s), x)) for x in data]

	# part 1 (fully overlapped ranges)
	total = 0
	for x1, x2, y1, y2 in data:
		if (x1 <= y1 and x2 >= y2) or (x1 >= y1 and x2 <= y2):
			total += 1
	print(total)

	# part 2 (partially overlapped ranges)
	total = 0
	for x1, x2, y1, y2 in data:
		if (x1 < y1 and x2 < y1) or (x1 > y2 and x2 > y2):
			total += 1
	print(len(data) - total)


