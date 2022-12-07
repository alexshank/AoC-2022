from helpers import load_data
from tree import TreeNode

# extend generic tree to store files on each node
class DirNode(TreeNode):
	def __init__(self, name, parent):
		super().__init__(name, parent)
		# application specific property
		self.files = {}
	
	# TODO this should be in the base class somehow, using Python's
	# TODO equivalent to generics
	def add_child(self, name):
		if self.has_child_with_name(name):
			return self.get_child_by_name(name)
		else:
			new_node = DirNode(name, self)
			self.children.append(new_node)
		return new_node


	# cannot use generic print because we want an application-specific property
	def print_dir(self, depth = 0):
		print(' ' * depth + '- ' + self.name + ' (dir)')
		for k, v in self.files.items():
			print(' ' * (depth + 1) + '- ' + k + ' (file, size=' + str(v) + ')')
		for child in self.children:
			child.print_dir(depth + 1)

	# example use case of the traversing higher-order function
	# higher-order function <==> function that takes functions as input
	def dir_size(self):
		def sum_files(node):
			return sum([v for v in node.files.values()])
		return self.traverse_accumulate(sum_files)


# [(dir, size), ..., (dir, size)] where size >= threshold
def get_deletion_candidates(node, min_delete_threshold):
	temp_list = []
	size = node.dir_size()
	if size >= min_delete_threshold:
		temp_list.append((node.name, size))
	for child in node.children:
		temp_list.extend(get_deletion_candidates(child, min_delete_threshold))
	return temp_list

if __name__ == "__main__":
	data = load_data("day-7-input.txt")

	previous_node = None
	current_node = DirNode('/', None)
	for line in data[1:]:
		# switch dir command
		if line.startswith('$ cd '):
			previous_node = current_node
			temp = line.replace('$ cd ', '')
			current_node = current_node.parent if temp == '..' else current_node.add_child(temp)
		# dir listed
		elif line.startswith('dir'):
			_, name = line.split(' ')
			current_node.add_child(name)
		# file size listed
		elif line[0].isnumeric():
			size, name = line.split(' ')
			current_node.files[name] = int(size)

	# seek to root node
	root_node = current_node
	while root_node.parent != None:
		root_node = root_node.parent

	# show our nice file structure
	root_node.print_dir()

	# part 1
	def sum_if_100_000(node):
		temp_sum = node.dir_size() 
		return temp_sum if temp_sum <= 100_000 else 0
	print(root_node.traverse_accumulate(sum_if_100_000))

	# part 2
	need_to_free = 30_000_000 - (70_000_000 - root_node.dir_size())
	ans = get_deletion_candidates(root_node, need_to_free)
	ans.sort(key = lambda x: x[1])
	print(ans[0][1])
