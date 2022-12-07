class TreeNode:
  def __init__(self, name, parent):
		# minimum data structure properties
    self.name = name
    self.parent = parent
    self.children = []
	
  def get_child_by_name(self, name):
    return [x for x in self.children if x.name == name][0]
	
  def has_child_with_name(self, name):
    return len([x for x in self.children if x.name == name]) > 0

	# traverse the tree, sum an operation performed on all nodes
  def traverse_accumulate(self, fn):
    total = fn(self)
    for child in self.children:
      total += child.traverse_accumulate(fn)
    return total
