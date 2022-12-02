from helpers import load_data

if __name__ == "__main__":
	data = load_data("day-1-input.txt")
	# only work with ints
	data = [int(x) if x != '' else 0 for x in data]
	# find indices with zeros
	list_splits = [0] + [i for i, v in enumerate(data) if v == 0]
	# sum between all zeros
	sums = [sum(data[list_splits[i-1]:list_splits[i]]) for i in range(1, len(list_splits))]
	# print sum of top 3
	sums.sort()
	print(sum(sums[-3:]))
