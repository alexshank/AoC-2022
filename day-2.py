from helpers import load_data

if __name__ == "__main__":
	data = load_data("day-2-input.txt")

	# part 1
	total = 0
	for d in data:
		opponent = ord(d[0]) - 65 	# map A, B, C to 0, 1, 2
		me = ord(d[2]) - 88					# map X, Y, Z to 0, 1, 2
		total += me + 1							# points from the chosen rock, paper, or scissors
		match (opponent - me) % 3:
			case 0: total += 3
			case 1: total += 0				# explicit
			case 2: total += 6
	print(total)

	# part 2
	total = 0
	for d in data:
		opponent = ord(d[0]) - 65 	# map A, B, C to 0, 1, 2
		# choose rock, paper, scissors based on if we should lose, tie, or win
		match d[2]:
			case 'X': total += 0 + (opponent - 1) % 3 + 1
			case 'Y': total += 3 + opponent + 1
			case 'Z': total += 6 + (opponent + 1) % 3 + 1
	print(total)
