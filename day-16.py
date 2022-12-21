from helpers import load_data

if __name__ == "__main__":
	data = load_data("day-16-input.txt")

	valve_flow_rates = {}
	valve_connections = {}
	for d in data:
		valve = d[6:8]
		d = d[23:]
		d = d.replace('valves', 'valve').replace('tunnels', 'tunnel').replace('leads', 'lead')
		first, second = d.split('; tunnel lead to valve ')

		valve_flow_rates[valve] = int(first)
		valve_connections[valve] = second.split(', ')
	
	print(valve_flow_rates)
	print(valve_connections)
	starting_valve = 'AA'



