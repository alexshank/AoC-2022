from helpers import load_data_grouped

def parse_list(str_list):
	# remove enclosing []
	str_list = str_list[1:len(str_list) - 1]

	# empty list base case
	if str_list == '':
		return []
	# TODO alex not needed?
	elif str_list == '[]':
		return [[]]

	# just ints base case
	if not '[' in str_list:
		return [int(x) for x in str_list.split(',')]
	
	start_index = 0
	bracket_indices = []
	within_brackets = True if str_list[0] == '[' else False
	bracket_count = 0
	for i, c in enumerate(str_list):
		if c == '[' and not within_brackets:
			bracket_indices.append((start_index, i, 'normal'))
			start_index = i
			within_brackets = True
			bracket_count = 1
		elif c == '[' and within_brackets:
			bracket_count += 1
		elif c == ']':
			bracket_count -= 1
			if bracket_count == 0:
				within_brackets = False
				bracket_indices.append((start_index, i + 1, 'list'))
				start_index = i + 1

	result = []
	
	for s, e, type in bracket_indices:
		if type == 'list':
			result.append(parse_list(str_list[s:e]))
		else:
			for str_integer in str_list[s:e].split(','):
				if len(str_integer) > 0:
					result.append(int(str_integer))

	return result


def is_correct_order(first, second):
	first_is_list = hasattr(first, "__len__")
	second_is_list = hasattr(second, "__len__")

	match first_is_list, second_is_list:
		case True, True:
			for i in range(min(len(first), len(second))):
				temp = is_correct_order(first[i], second[i])
				if temp == None:
					continue
				else:
					return temp

			if len(first) != len(second):
				return len(first) < len(second)
			else:
				return None

		case True, False:
			return is_correct_order(first, [second]) # TODO this might not be valid?
		case False, True:
			return is_correct_order([first], second) # TODO this might not be valid?
		case False, False:
			if first == second:
				return None
			else:
				return first < second

if __name__ == "__main__":
	data = load_data_grouped("day-13-input.txt")

	parsed_data = []
	for group in data:
		temp_list = []
		for line in group:
			temp_list.append(parse_list(line))
		parsed_data.append(temp_list)

	count = 0
	for i, group in enumerate(parsed_data):
		first, second = group
		if is_correct_order(first, second):
			count += i + 1
	
	# part 1 (answer: 5717)
	print(count)

	# part 2 (answer: 25935)
	def is_in_order(test_list):
		for i in range(1, len(test_list)):
			if not is_correct_order(test_list[i - 1], test_list[i]):
				return False
		return True 

	all_lines = [line for group in parsed_data for line in group]
	all_lines.append([[2]])
	all_lines.append([[6]])
	result = [all_lines.pop()]
	while len(all_lines) > 0:
		new_item = all_lines.pop()
		for i in range(len(result) + 1):
			result.insert(i, new_item)
			if is_in_order(result):
				break
			else:
				del result[i]
	
	final = []
	for i, item in enumerate(result):
		if item == [[2]] or item == [[6]]:
			final.append(i + 1)
	
	ans = 1
	for t in final:
		ans *= t
	print(ans)
	


	

