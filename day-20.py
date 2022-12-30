from helpers import load_data


# TODO next potential issue: when we wrap multiple times, we probably need to increment many times


def find_current_index_by_original_index(target_index):
	for k, v in mix_numbers.items():
		if v.original_index == target_index:
			return k	

class MixNumber:
	def __init__(self, original_index, value):
		self.original_index = original_index
		self.value = value

if __name__ == "__main__":
	data = load_data("day-20-test-input.txt")
	data = [int(d) for d in data]

	# key is the current index of the value
	mix_numbers = {i: MixNumber(i, val) for i, val in enumerate(data)}
	mix_len = len(mix_numbers)

	for i in range(mix_len):
		# print(str(i) + ' of ' + str(mix_len))
		# print('--------------')
		# print([v.value for v in mix_numbers.values()])

		start_index = find_current_index_by_original_index(i)
		movement = mix_numbers[start_index].value

		if movement == 0:
			print('no movement')
			continue

		end_index = (start_index + movement) % mix_len

		# TODO problem just has a strange way of moving numbers around???
		if movement > 0 and (end_index == mix_len - 1 or end_index < start_index):
			# wrap_count = abs((start_index + movement) // mix_len)	# TODO confirm this on paper first
			end_index = (end_index + 1) % mix_len
		elif movement < 0 and (end_index == 0 or end_index > start_index):
			# wrap_count = abs((start_index + movement) // mix_len) # TODO confirm this on paper first
			end_index = (end_index - 1) % mix_len

		# print('moving ' + str(mix_numbers[start_index].value) + ' between ' + str(mix_numbers[(end_index) % mix_len].value) + ' and ' + str(mix_numbers[(end_index + 1) % mix_len].value))

		# save what we'll overwrite
		moving_spot = mix_numbers[start_index]

		if start_index > end_index:

			# print('heerree')
			# print(start_index)
			# print(end_index)
			for i in reversed(range(end_index, start_index)):
				# print((i+1, i))
				mix_numbers[i + 1] = mix_numbers[i]
			# print(end_index)
			mix_numbers[end_index] = moving_spot

		elif start_index < end_index:

			for i in range(start_index, end_index):
				mix_numbers[i] = mix_numbers[i + 1]
			mix_numbers[end_index] = moving_spot

		# print([v.value for v in mix_numbers.values()])
		# print()

print('-----------------')
print([v.value for v in mix_numbers.values()])
print('-----------------')
print()


index_of_zero = None 
for k, v in mix_numbers.items():
	if v.value == 0:
		index_of_zero = k
		break
print(index_of_zero)

print('summing')
print(mix_numbers[(index_of_zero + 1_000) % mix_len].value)
print(mix_numbers[(index_of_zero + 2_000) % mix_len].value)
print(mix_numbers[(index_of_zero + 3_000) % mix_len].value)
print('final')
print(sum([mix_numbers[(index_of_zero + 1_000) % mix_len].value, mix_numbers[(index_of_zero + 2_000) % mix_len].value], mix_numbers[(index_of_zero + 3_000) % mix_len].value))

# print([v.value for v in mix_numbers.values()])




	