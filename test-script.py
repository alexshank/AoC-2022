# basis we're working with
candidates = [1, 5, 25, 125, 625]
# numbers that have any negative symbol (-, =) in them
negatives = [3, 4, 8, 9, 13, 14, 18, 19, 20, 21, 22, 23, 24, 28, 29, 33, 34, 38, 39, 40]

def first_greater_index(src):
	for i, v in enumerate(candidates):
		if v > src:
			return i - 1
	return None

for src in range(2, 40 + 1):
	important_index = first_greater_index(src)
	lower = candidates[important_index]
	upper = candidates[important_index + 1]
	if src in negatives:
		print('*', end='')
	else:
		print(' ', end='')
	print("{:02d}".format(src) + ': (' + "{:02d}".format(lower) + ', ' + "{:02d}".format(upper) + ') (+' + "{:02d}".format(src - lower) + ', -' + "{:02d}".format(upper - src) + ')')