from collections import defaultdict

def load_data():
	with open("day-1-input.txt", "r") as input_file:
		data = input_file.read().split('\n')
	return data

if __name__ == "__main__":
	data = load_data()
	# only work with ints
	data = [int(x) if x != '' else 0 for x in data]
	# find indices with zeros
	list_splits = [0] + [i for i, v in enumerate(data) if v == 0]
	# sum between all zeros
	sums = [sum(data[list_splits[i-1]:list_splits[i]]) for i in range(1, len(list_splits))]
	# print sum of top 3
	sums.sort()
	print(sum(sums[-3:]))

	d = defaultdict(lambda: 0)
	d['cat'] += 5
	print(d['cat'])
