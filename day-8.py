from helpers import load_data
from functools import reduce
from operator import mul

# return trees to the left, right, above, below
def get_views(data, h, w):
	row, col = data[h], [row[w] for row in data]
	return reversed(row[:w]), row[w+1:], reversed(col[:h]), col[h+1:]

# how many trees you see before your view is blocked
def tree_count(tree_height_diffs):
	count = 0
	for height_diff in tree_height_diffs:
		count += 1
		if height_diff <= 0: break
	return count

# part 1 - check if tree is visible from any direction (or, tree can see out of forest)
def is_visible(data, h, w):
	all_pos = lambda xs: all([x > 0 for x in xs])
	height_diff = lambda xs: [data[h][w] - x for x in xs]
	return any(map(all_pos, map(height_diff, get_views(data, h, w))))

# part 2 - score based on how many other trees are in a tree's view
def scenic_score(data, h, w):
	height_diff = lambda xs: [data[h][w] - x for x in xs]
	return reduce(mul, map(tree_count, map(height_diff, get_views(data, h, w))))

if __name__ == "__main__":
	data = load_data("day-8-input.txt")
	data = [[int(x) for x in line] for line in data]
	
	total = 0
	max_scenic_score = 0
	for h in range(len(data)):
		for w in range(len(data[0])):
			if is_visible(data, h, w): total += 1
			max_scenic_score = max(max_scenic_score, scenic_score(data, h, w))
			
	print(total) 						# part 1
	print(max_scenic_score) # part 2


