from helpers import load_data
import copy


# returns list of lists (treat inner lists as stacks with append() and pop())
def parse_stacks_from_picture(picture, stack_count):
	# remove known spaces and brackets, convert 3 consecutive spaces into arbitrary "not present" symbol
	cleaned_lines = []
	space_indices = [3 + 4 * i for i in range(stack_count - 1)]
	for d in picture:
		temp = [x for i, x in enumerate(d) if i not in space_indices]
		temp = ''.join(temp).replace('   ', '-').replace('[', '').replace(']', '')
		cleaned_lines.append(temp)

	# we'll add the crates to the stacks in FILO order
	stacks = [[] for _ in range(stack_count)]
	for cleaned_line in reversed(cleaned_lines):
		for i in range(stack_count):
			if cleaned_line[i] != '-': stacks[i].append(cleaned_line[i])

	return stacks 


# move crates according to new or older functionality
def move_crates(stacks, triples, is_crate_mover_9001 = False):
	for triple in triples:
		temp_list = []
		for _ in range(triple[0]):
			temp_list.append(stacks[triple[1]].pop())
		if is_crate_mover_9001: temp_list.reverse()
		stacks[triple[2]].extend(temp_list)
	return ''.join([stack.pop() for stack in stacks])


if __name__ == "__main__":
	# split input into key parts
	data = load_data("day-5-input.txt")
	picture = data[:8]
	stack_count = int(data[8].replace(' ', '')[-1])
	movements = data[10:]

	# initialize stack data types for the literal crate stacks
	stacks = parse_stacks_from_picture(picture, stack_count)

	# parse list of movements into triples: (count, from_index, to_index)
	triples = []
	for m in movements:
		nums = m.replace('move ', '').replace(' from ', ',').replace(' to ', ',').split(',')
		triples.append([int(nums[0]), int(nums[1]) - 1, int(nums[2]) - 1])

	# part 1
	stacks_copy = copy.deepcopy(stacks)
	print(move_crates(stacks, triples))
	
	# part 2
	print(move_crates(stacks_copy, triples, is_crate_mover_9001 = True))


