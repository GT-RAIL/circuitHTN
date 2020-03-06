import copy
import random
import networkx as nx

class Node:
    def __init__(self, name, prestate, poststate):
        self.children = []
        self.name = name
        self.prestate = prestate
        self.poststate = poststate

    def get_name(self):
        return self.name

    def add_child(self, node):
        return

    def add_children(self, nodes):
        return

    def get_children(self):
        return self.children

    def random_walk(self):
        return
    
    def change_name(self, node_name):
        self.name = node_name

    def __repr__(self):
        return self.prestate + ', ' + self.name

    def __str__(self):
        return self.name

class PrimitiveNode(Node):
    def add_child(self, node):
        print("Primitive nodes cannot have children")

    def add_children(self, node):
        print("Primitive nodes cannot have children")

    def random_walk(self):
        return [self]

    def count_edges(self):
        return 0

    def count_choices(self):
        return 0

    def count_sequences(self):
        return 0

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, PrimitiveNode):
            return self.name == other.name
        return False

class ChoiceNode(Node):
    def __init__(self, name, prestate, poststate):
        super().__init__(name, prestate, poststate)
        self.children_freq = []

    def add_child(self, node):
        self.add_child_with_freq(node, 1.0)

    def add_child_with_freq(self, node, freq):
        self.children.append(node)
        self.children_freq.append(freq)

    def add_children(self, nodes):
        self.add_children_with_freq(nodes, [1.0] * len(nodes))

    def add_children_with_freq(self, nodes, node_frequencies):
        self.children.extend(nodes)
        self.children_freq.extend(node_frequencies)

    def get_children_freq(self):
        return self.children_freq

    def random_walk(self):
        weights = copy.deepcopy(self.children_freq)
        total_weight = 0
        for i in range(len(weights)):
            total_weight += weights[i]
        for i in range(len(weights)):
            weights[i] /= float(total_weight)
        r = random.random()
        n = 0
        choice = len(weights) - 1
        for i in range(len(weights)):
            n += weights[i]
            if n > r:
                choice = i
                break
        return self.children[choice].random_walk()

        # my ubuntu distro only has python 3.5, so I implemented this myself above :(
        # return random.choices(population=self.children, weights=self.children_freq)[0].random_walk()

    def count_edges(self):
        count = len(self.children)
        for child in self.children:
            count += child.count_edges()
        return count

    def count_choices(self):
        count = 1
        for child in self.children:
            count += child.count_choices()
        return count

    def count_sequences(self):
        count = 0
        for child in self.children:
            count += child.count_sequences()
        return count

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self,other):
        if isinstance(other, ChoiceNode):
            return self.name == other.name
        return False
    

class SequentialNode(Node):
    def add_child_to_front(self, node):
        self.children.insert(0, node)

    def add_child(self, node):
        self.children.append(node)

    def add_children(self, nodes):
        self.children.extend(nodes)

    def random_walk(self):
        walk = []
        for child in self.children:
            walk.extend(child.random_walk())
        return walk

    def count_edges(self):
        count = len(self.children)
        for child in self.children:
            count += child.count_edges()
        return count

    def count_choices(self):
        count = 0
        for child in self.children:
            count += child.count_choices()
        return count

    def count_sequences(self):
        count = 1
        for child in self.children:
            count += child.count_sequences()
        return count

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self,other):
        if isinstance(other, SequentialNode):
            return self.name == other.name
        return False


def convertToDiGraph(root_htn_node):
    digraph = nx.DiGraph()
    print(root_htn_node, ' is the root of the tree.')
    return convertToDiGraphHelper(root_htn_node, digraph)

def convertToDiGraphHelper(root_htn_node, digraph):
    digraph.add_node(root_htn_node)
    children = root_htn_node.get_children()
    for i in range(len(children)):
        child = children[i]
        convertToDiGraphHelper(child, digraph)
        if root_htn_node.__class__.__name__ == 'ChoiceNode':
            digraph.add_edge(root_htn_node, child, prob=root_htn_node.get_children_freq()[i])
        else:
            digraph.add_edge(root_htn_node, child)
    return digraph
