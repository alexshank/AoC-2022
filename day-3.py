from helpers import load_data

def priority(character):
	return ord(character) - 38 if character.isupper() else ord(character) - 96

if __name__ == "__main__":
	data = load_data("day-3-input.txt")

	# part 1
	total = 0
	for d in data:
		half = int(len(d) / 2)
		val = set(d[:half]).intersection(set(d[half:])).pop()
		total += priority(val)
	print(total)

	# part 2
	total = 0
	for i in range(0, len(data), 3):
		s1, s2, s3 = data[i:i + 3]
		val = set(s1).intersection(set(s2)).intersection(set(s3)).pop()
		total += priority(val)
	print(total)

