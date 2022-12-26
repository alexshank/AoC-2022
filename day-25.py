from helpers import load_data

def char_to_num(c):
	match c:
		case '-': return -1
		case '=': return -2
		case _: return int(c)

def increment_snafu(old_snafu):
	match old_snafu[-1]:
		case '2':
			if len(old_snafu) == 1:
				return "1="
			else:
				return increment_snafu(old_snafu[:-1]) + "="
		case '=':
			return old_snafu[:-1] + "-"
		case '-':
			return old_snafu[:-1] + "0"
		case '0':
			return old_snafu[:-1] + "1"
		case '1':
			return old_snafu[:-1] + "2"

if __name__ == "__main__":
	data = load_data("day-25-input.txt")

	total = 0
	for d in data:
		sub_sum = 0
		for i, c in enumerate(reversed(d)):
			val = char_to_num(c)
			sub_sum += val * (5 ** i)
		total += sub_sum
	print(total)

	# temp = "0"
	# for i in range(total):
	# 	temp = increment_snafu(temp)
	# 	if i % 10_000 == 0:
	# 		print(temp)
	# print(temp)




