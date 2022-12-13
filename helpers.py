# every problem will require us to read a text file line by line
def load_data(path):
	with open('./inputs/' + path, "r") as input_file:
		data = input_file.read().split('\n')
	return data

# some problems will have groups of lines separated by a blank line
def load_data_grouped(path):
	with open('./inputs/' + path, "r") as input_file:
		data = [x.split('\n') for x in input_file.read().split('\n\n')]
	return data


