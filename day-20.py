from helpers import load_data

def find_current_index_by_original_index(target_index):
	for k, v in mix_numbers.items():
		if v.original_index == target_index:
			return k	

class MixNumber:
	def __init__(self, original_index, value):
		self.original_index = original_index
		self.value = value

if __name__ == "__main__":
	data = load_data("day-20-input.txt")
	data = [int(d) for d in data]

	# key is the current index of the value
	mix_numbers = {i: MixNumber(i, val) for i, val in enumerate(data)}
	mix_len = len(mix_numbers)

	for i in range(mix_len):
		# print(str(i) + ' of ' + str(mix_len))
		print('--------------')
		print([v.value for v in mix_numbers.values()])

		start_index = find_current_index_by_original_index(i)
		movement = mix_numbers[start_index].value
		end_index = (start_index + movement) % mix_len

		# print('start ' + str(start_index))
		# print('end   ' + str(end_index))
		print('moving ' + str(mix_numbers[start_index].value) + ' between ' + str(mix_numbers[(end_index) % mix_len].value) + ' and ' + str(mix_numbers[(end_index + 1) % mix_len].value))

		# save what we'll overwrite
		moving_spot = mix_numbers[start_index]

		if movement > 0:
			for n in range(start_index, end_index):
				mix_numbers[n % mix_len] = mix_numbers[(n + 1) % mix_len]
			mix_numbers[end_index] = moving_spot

		elif end_index < start_index:
			for n in range(start_index, end_index, -1):
				mix_numbers[n % mix_len] = mix_numbers[(n - 1) % mix_len]
			mix_numbers[end_index] = moving_spot

		print([v.value for v in mix_numbers.values()])

index_of_zero = None 
for k, v in mix_numbers.items():
	if v.value == 0:
		index_of_zero = k
		break
print(index_of_zero)

# print([v.value for v in mix_numbers.values()])




	