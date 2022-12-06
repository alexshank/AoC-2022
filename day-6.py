from helpers import load_data


def solve(data, marker_size):
	for i in range(marker_size, len(data) + 1):
		if len(set(data[i-marker_size:i])) == marker_size:
			return i


if __name__ == "__main__":
	data = load_data("day-6-input.txt")[0]
	print(solve(data, 4))
	print(solve(data, 14))

