from helpers import load_data


class TreeNode:
  def __init__(self, name, parent):
		# minimum data structure properties
    self.name = name
    self.parent = parent
    self.children = []
		# application specific properties
    self.files = {}
	
  def get_child_by_name(self, name):
    return [x for x in self.children if x.name == name][0]
	
  def has_child_with_name(self, name):
    return len([x for x in self.children if x.name == name]) > 0

  def add_child(self, name):
    if self.has_child_with_name(name):
      return current_node.get_child_by_name(name)
    else:
      new_node = TreeNode(name, self)
      self.children.append(new_node)
      return new_node

  def print_tree(self, depth = 0):
    print(' ' * depth + '- ' + self.name + ' (dir)')
    for k, v in self.files.items():
      print(' ' * (depth + 1) + '- ' + k + ' (file, size=' + str(v) + ')')
    for child in self.children:
      child.print_tree(depth + 1)

	# traverse the tree, sum an operation performed on all nodes
  def traverse_accumulate(self, fn):
    total = fn(self)
    for child in self.children:
      total += child.traverse_accumulate(fn)
    return total

	# example use case of the traversing higher-order function
	# higher-order function <--> function that takes functions as input
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
	current_node = TreeNode('/', None)
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
	root_node.print_tree()

	# part 1
	def sum_if_100_000(node):
		temp_sum = node.dir_size() 
		return temp_sum if temp_sum <= 100_000 else 0
	print(root_node.traverse_accumulate(sum_if_100_000))

	# part 2
	total_used = root_node.dir_size()
	total_free = 70_000_000 - total_used
	need_to_free = 30_000_000 - total_free
	ans = get_deletion_candidates(root_node, need_to_free)
	ans.sort(key = lambda x: x[1])
	print(ans[0][1])
