from helpers import load_data

# hold the number of resources and robots we have
class State:
	def __init__(self):
		geode_bots = 0
		geode_count = 0
		obsidian_bots = 0
		obsidian_count = 0
		clay_bots = 0
		clay_count = 0
		ore_bots = 0
		ore_count = 1
	
if __name__ == "__main__":
	# TODO fixup gross parsing
	data = load_data("day-19-input.txt")
	data = [d[d.index(':') + 2:] for d in data]
	data = [d.replace('Each ', '') for d in data]
	data = [d.split('. ') for d in data]
	# print(data)

	blueprints = {}
	for i, d in enumerate(data):
		d = [t.replace('robot costs ', '') for t in d]
		d = [t.replace('and ', '') for t in d]

		blueprints[i + 1] = {}
		for t in d:
			tokens = t.split(' ')
			if len(tokens) == 3:
				blueprints[i + 1][tokens[0]] = [(tokens[2], tokens[1])]
			else:
				blueprints[i + 1][tokens[0]] = [(tokens[2], tokens[1]), (tokens[4], tokens[3])]

	resources = ['geode', 'obsidian', 'clay', 'ore']
	# print(blueprints)