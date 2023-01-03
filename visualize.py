import time

COLORS = {
	'red_': '\033[41m',
	'green_': '\033[42m',
	'yellow_': '\033[43m',
	'blue_': '\033[44m',
	'purple_': '\033[45m',
	'cyan_': '\033[46m',
	'red': '\033[91m',
	'green': '\033[92m',
	'yellow': '\033[93m',
	'blue': '\033[94m',
}

# print color with ANSI terminal emulator codes
def pc(text, color, end='\n'):
	print(COLORS[color], end='')
	print(text, end='')
	print('\033[0m', end='')
	print(end, end='')

if __name__ == "__main__":
	# demo
	for t in range(100):
		for i in range(10):
			for j in range(15):
				if i * 15 + j == t:
					pc('O', 'yellow_', end='')
				else:
					pc('X', 'green_', end='')
			print()
		time.sleep(0.1)
		print("\033[J", end="")
		print()
		