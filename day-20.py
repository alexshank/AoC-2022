from helpers import load_data

# Note: I still do not intuitively understand "moving the number forward/backward."
# The solution below is based on a Reddit Advent of Code solution I read,
# but I would not consider this behavior what the problem describes.
#
# Accepting defeat on this one since I can't get any further explanation of the prompt.
# I feel good about the coding concepts this was driving at though.
#
# P.S. See git history for many confused attempts!

if __name__ == "__main__":
	data = load_data("day-20-input.txt")
	numbers = [int(d) for d in data]	# The original list, we will NOT augment it.
	indices = list(range(len(data)))	# consider a single element: item[i] = v
																		# i = the new index of a number after being mixed
																		# v = the original index of the number

	for i in range(len(numbers)):
		element_magnitude = numbers[i]
		element_current_mix_index = indices.index(i)

		# This is the very unintuitive behavior imo:
		# (1) We wrap the list while the element is removed?
		# (2) Moving an element to position zero sends it to the back?
		element_mix = indices.pop(element_current_mix_index)
		# Note: len(indices) is len(numbers) - 1 during this call
		element_next_mix_index = (element_current_mix_index + element_magnitude) % len(indices)
		if element_next_mix_index == 0:
			indices.append(element_mix)
		else:
			indices.insert(element_next_mix_index, element_mix)

	# part 1 (answer: 14526)
	mixed_zero_index = indices.index(numbers.index(0))
	result = 0
	for i in [1_000, 2_000, 3_000]:
		original_index = indices[(mixed_zero_index + i) % len(indices)]
		result += numbers[original_index]
	print(f'Part 1: {result}')

	# part 2 (answer: )
	numbers = [number * 811589153 for number in numbers]
	indices = list(range(len(data))) # reset
	for i in indices * 10:
		element_magnitude = numbers[i]
		element_current_mix_index = indices.index(i)
		element_mix = indices.pop(element_current_mix_index)
		element_next_mix_index = (element_current_mix_index + element_magnitude) % len(indices)
		if element_next_mix_index == 0:
			indices.append(element_mix)
		else:
			indices.insert(element_next_mix_index, element_mix)

	mixed_zero_index = indices.index(numbers.index(0))
	result = 0
	for i in [1_000, 2_000, 3_000]:
		original_index = indices[(mixed_zero_index + i) % len(indices)]
		result += numbers[original_index]
	print(f'Part 2: {result}')



