from helpers import load_data_grouped
from math import prod

class Monkey:
	def __init__(self, lines):
		lines = [line.strip() for line in lines]

		self.item_worries = [int(x) for x in lines[1].replace('Starting items: ', '').split(', ')]
		self.operation = lines[2].replace('Operation: new = old ', '')
		self.test = int(lines[3].replace('Test: divisible by ', ''))
		self.true = int(lines[4].replace('If true: throw to monkey ', ''))
		self.false = int(lines[5].replace('If false: throw to monkey ', ''))
		self.business = 0
	
	def process(self, monkey_list):

		# TODO could move so it isn't computed a ton
		lcm = prod([m.test for m in monkey_list])

		while len(self.item_worries) > 0:
			worry = self.item_worries.pop(0)
			self.business += 1

			operation_value = None
			match self.operation[2:]:
				case 'old': operation_value = worry
				case _: operation_value = int(self.operation[2:])

			match self.operation[0]:
				case '*':
					worry = worry * operation_value
				case '+':
					worry = worry + operation_value

			# worry = worry // 3

			if worry % self.test == 0:
				worry = worry % lcm
				monkey_list[self.true].item_worries.append(worry)
			else:
				monkey_list[self.false].item_worries.append(worry)



if __name__ == "__main__":
	# get groups of lines between blank lines
	data = load_data_grouped("day-11-input.txt")
	# TODO I've broken this now

	monkeys = [Monkey(d) for d in data]

	for r in range(10_000):
		for monkey in monkeys:
			monkey.process(monkeys)
	
	businesses = [m.business for m in monkeys]
	businesses.sort()
	print(businesses[6] * businesses[7])

	# part 2 (hint from Reddit: (a mod kn) mod n = a mod n for any positive integer k)
	# store a mod kn instead of a
	# so keep taking modulo of result after each divisor check
	# least common multiple (LCM) of prime numbers (like we have) is just their product!
	# k above is the lcm, or product of all the possible divisors

	# part 1 solution: 110220
	# part 2 solution: 19457438264



