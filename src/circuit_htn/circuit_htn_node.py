from __future__ import division
import pickle

class CircuitHTNNode(object):
    CHOICE = 0
    SEQUENCE = 1
    PRIMITIVE = 2

    def __init__(self, name='', node_type=PRIMITIVE, parent=None, action=None, probabilities=[]):
        self.name = name  # name of the node
        self.node_type = node_type  # how execution of children is ordered
        self.action = action  # primitive action to execute (for primitives)

        self.parent = parent  # parent of the HTN node, if any; used for traversing up network
        self.children = []  # list of child HTN nodes, if any; used for traversing down to reach primitive actions

        self.probabilities = probabilities  # probabilities for executing each child node (for decisions)

    def set_children(self, nodes):
        self.children = nodes

    def add_child(self, node):
        self.children.append(node)

    def add_children(self, node_list):
        self.children.extend(node_list)

    def remove_child(self, node):
        if self.node_type == CircuitHTNNode.CHOICE:
            self.probabilities.pop(self.children.index(node))
        self.children.remove(node)

    def replace_child(self, old_child, new_child):
        i = self.children.index(old_child)
        self.remove_child(old_child)
        self.children.insert(i, new_child)

    def normalize_probabilities(self):
        total = sum(self.probabilities)
        for i in range(len(self.probabilities)):
            self.probabilities[i] /= total

    def text_output(self, level=0, parent_type=None):
        htn_str = ''
        for i in range(level):
            htn_str += '  '
        if parent_type is not None:
            if parent_type == CircuitHTNNode.SEQUENCE:
                htn_str += '=> '
            elif parent_type == CircuitHTNNode.CHOICE:
                htn_str += '<: '
        htn_str += str(self)

        for c in self.children:
            htn_str += '\n' + c.text_output(level + 1, self.node_type)
        return htn_str

    @staticmethod
    def type_to_string(node_type):
        if node_type == CircuitHTNNode.PRIMITIVE:
            return 'primitive'
        elif node_type == CircuitHTNNode.SEQUENCE:
            return 'sequence'
        elif node_type == CircuitHTNNode.CHOICE:
            return 'choice'

    def __str__(self):
        if self.node_type == CircuitHTNNode.PRIMITIVE:
            return self.name + ' [' + self.action + ']'
        else:
            return self.name + ' (' + CircuitHTNNode.type_to_string(self.node_type) + ')'

    def __repr__(self):
        return str(self)