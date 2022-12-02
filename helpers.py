# every problem will require us to read a text file line by line
def load_data(path):
	with open(path, "r") as input_file:
		data = input_file.read().split('\n')
	return data

