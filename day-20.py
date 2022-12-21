from helpers import load_data

class MixNumber:
  def __init__(self, start_position, value):
    self.order = start_position
    self.current_index = start_position
    self.value = value
	
if __name__ == "__main__":
	data = load_data("day-20-input.txt")
	data = [int(d) for d in data]
	mix_numbers = [MixNumber(i, val) for i, val in enumerate(data)]

	print(mix_numbers)

	# for i in range(len(mix_numbers)):

	