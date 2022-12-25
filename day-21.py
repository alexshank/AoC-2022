from helpers import load_data
from sympy import solve, sympify

class TreeNode:
	def __init__(self, label):
		self.label = label 
		self.parent = None
		self.operator = None
		self.value = None
		self.left = None
		self.right = None

def print_tree(root_node, depth):
	print(depth * ' ' + root_node.label + ' ' + str(root_node.value))
	if root_node.left != None and root_node.right != None:
		print_tree(root_node.left, depth + 1)
		print_tree(root_node.right, depth + 1)
	
def contains_node(root_node, label):
	if root_node.label == label:
		return True
	
	if root_node.left != None and root_node.right != None:
		return contains_node(root_node.left, label) or contains_node(root_node.right, label)
	else:
		return False
	
def process_tree(root_node):
	if root_node.value != None:
		return root_node.value
	else:
		left = process_tree(root_node.left)
		right = process_tree(root_node.right)
		match root_node.operator:
			case '+':
				return int(left + right)
			case '-':
				return int(left - right)
			case '*':
				return int(left * right)
			case '/':
				return int(left / right)
	raise Exception('No bueno!')

# print the math expression represented by the tree structure
def build_expression(root_node):
	if root_node.value != None:
		return str(root_node.value)
	else:
		if contains_node(root_node.left, 'humn'):
			return '(' + build_expression(root_node.left) + root_node.operator + str(process_tree(root_node.right)) + ')'
		elif contains_node(root_node.right, 'humn'):
			return '(' + str(process_tree(root_node.left)) + root_node.operator + build_expression(root_node.right) + ')' 
		else:
			return str(process_tree(root_node))

if __name__ == "__main__":
	data = load_data("day-21-input.txt")
	data = [d.split(': ') for d in data]

	# initialize dictionary of tree nodes
	nodes = {d[0]: TreeNode(d[0]) for d in data}

	# connect the tree nodes to form the full tree
	for name, operation in data:
		if len(operation) > 8:
			left, operator, right = operation.split(' ')
			nodes[name].left = nodes[left]
			nodes[name].operator = operator
			nodes[name].right = nodes[right]
		else:
			nodes[name].value = int(operation)
	
	# part 1 (answer: 21208142603224)
	print(process_tree(nodes['root']))

	# part 2 (answer: 3882224466191)
	left_tree = nodes['root'].left
	right_tree = nodes['root'].right
	nodes['humn'].value = 'X'
	if contains_node(left_tree, 'humn'):
		target_value = process_tree(nodes['root'].right)
		tree_expr = build_expression(left_tree)
	else:
		target_value = process_tree(nodes['root'].left)
		tree_expr = build_expression(right_tree)

	# we build an expression like below and solve it with a library
	# Eq((5*(3-(4*X))), 150)
	sympy_eq = sympify("Eq(" + tree_expr + ',' + str(target_value) + ")")
	print(solve(sympy_eq))



