from helpers import load_data

def char_to_num(c):
	match c:
		case '-': return -1
		case '=': return -2
		case _: return int(c)

def decrement_char(old_char):
	match old_char:
		case '2': return '1'
		case '1': return '0'
		case '0': return '-'
		case '-': return '='
		case _: raise Exception('Cannot decrement')

def decrement_at_index(str_number, index):
	old_char = str_number[index]
	new_char = decrement_char(old_char)
	result = str_number[:index] + new_char + str_number[index + 1:]
	return result

def weird_num_to_decimal(str_num):
	result = 0
	for i, c in enumerate(reversed(str_num)):
		val = char_to_num(c)
		result += val * (5 ** i)
	return result
	

if __name__ == "__main__":
	data = load_data("day-25-input.txt")

	total = sum([weird_num_to_decimal(d) for d in data])
	# total = 36067808580527
	print(total)

	powers_2 =[2 * 5 ** i for i in range(30)] 
	for i in range(len(powers_2)):
		if total < sum(powers_2[:i]):
			num_digits = i
			print(f'{num_digits} digits')
			break

	# part 1 (answer: 2-212-2---=00-1--102)
	answer = '2' * num_digits
	found = False
	for i in range(num_digits):
		# at most 2 -> =, or 4 decrements
		candidate = answer
		for _ in range(4):
			candidate = decrement_at_index(candidate, i)
			test_val = weird_num_to_decimal(candidate)
			if test_val == total:
				found = True
				answer = candidate
				break
			elif test_val > total:
				answer = candidate
			else:
				break
		
		if found == True:
			break

	print(answer)
	




