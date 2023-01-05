from helpers import load_data


# TODO need to create a larger example case with zero in it and numbers that are > 3 * len of list
# TODO next potential issue: when we wrap multiple times, we probably need to increment many times??

def find_current_index_by_original_index(target_index):
	for k, v in mix_numbers.items():
		if v.original_index == target_index:
			return k	

class MixNumber:
	def __init__(self, original_index, value):
		self.original_index = original_index
		self.value = value

def swap(mix_numbers, left_index, right_index):
		temp = mix_numbers[left_index]
		mix_numbers[left_index] = mix_numbers[right_index]
		mix_numbers[right_index] = temp

if __name__ == "__main__":
	data = load_data("day-20-input.txt")
	data = [int(d) for d in data]

	# key is the current index of the value
	mix_numbers = {i: MixNumber(i, val) for i, val in enumerate(data)}
	mix_len = len(mix_numbers)

	# print([v.value for v in mix_numbers.values()])
	# print()

	for i in range(mix_len):
		# print(str(i) + ' of ' + str(mix_len))
		# print('--------------')
		# print([v.value for v in mix_numbers.values()])

		start_index = find_current_index_by_original_index(i)
		movement = mix_numbers[start_index].value

		print(f'Starting at: {start_index}')
		print(f'Moving: {movement}')

		# moving left
		if movement < 0:
			left = abs(movement) % mix_len
			if left == 0:
				print('skipping left')
				print()
				continue
			elif start_index - left <= 0: # TODO should this be zero inclusive? really?
				right = mix_len - 1 - left
				print(f'Right: {right}')
				for i in range(right):
					swap(mix_numbers, start_index + i, start_index + 1 + i)
			else:
				print(f'Left: {left}')
				for i in range(left):
					swap(mix_numbers, start_index - 1 - i, start_index - i)
		# moving right
		else:
			right = movement % mix_len
			if right == 0:
				print('skipping right')
				print()
				continue
			elif start_index + right >= mix_len:
				left = mix_len - 1 - right
				print(f'Left: {left}')
				for i in range(left):
					swap(mix_numbers, start_index - 1 - i, start_index - i)
			else:
				print(f'Right: {right}')
				for i in range(right):
					swap(mix_numbers, start_index + i, start_index + 1 + i)
		print()

		# print([v.value for v in mix_numbers.values()])
		print()

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

# TODO guessed 2487, was too low
print('summing')
print(mix_numbers[(index_of_zero + 1_000) % mix_len].value)
print(mix_numbers[(index_of_zero + 2_000) % mix_len].value)
print(mix_numbers[(index_of_zero + 3_000) % mix_len].value)
print('final')
print(sum([mix_numbers[(index_of_zero + 1_000) % mix_len].value, mix_numbers[(index_of_zero + 2_000) % mix_len].value], mix_numbers[(index_of_zero + 3_000) % mix_len].value))

# print([v.value for v in mix_numbers.values()])




	