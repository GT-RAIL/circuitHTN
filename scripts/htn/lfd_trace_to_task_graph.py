import networkx as nx
import collections

####Legacy Code#####

counter = 0
# a0 = 'idle_action'
# a6 = 'terminate_action'
def getLFDTrace():
    dict = {}
    dict['a0'] = [(('s0',), 'a1'), (('s0',), 'a2')]
    dict['a1'] = [(('s0', 's1'), 'a2'), (('s0', 's1', 's2', 's3', 's4'), 'a5')]
    dict['a2'] = [(('s0', 's1', 's2'), 'a3'), (('s0', 's1', 's2'), 'a4'), (('s0', 's2'), 'a3'), (('s0', 's2'), 'a4')]
    dict['a3'] = [(('s0', 's1', 's2', 's3'), 'a4'), (('s0', 's2', 's3'), 'a4'), (('s0', 's2', 's3', 's4'), 'a1'), (('s0', 's1', 's2', 's3', 's4'), 'a5')]
    dict['a4'] = [(('s0', 's1', 's2', 's4'), 'a3'), (('s0', 's2', 's4'), 'a3'), (('s0', 's2', 's3', 's4'), 'a1'), (('s0', 's1', 's2', 's3', 's4'), 'a5')]
    dict['a5'] = [(('s0', 's1', 's2', 's3', 's4', 's5'), 'a6')]
    dict['a6'] = []

    # dict = {}
    # dict['a0'] = [(('s0',), 'a1'), (('s0',), 'a2')]
    # dict['a1'] = [(('s0', 's1'), 'a2'), (('s0', 's1', 's2'), 'a3')]
    # dict['a2'] = [(('s0', 's1', 's2'), 'a3'), (('s0', 's2'), 'a1')]
    # dict['a3'] = []
    return dict

def convertLFDTraceToTaskGraph(lfd_trace):
    graph = nx.DiGraph()
    current_node = ((), 'a0')
    visitedSet = {}
    convertLFDTraceToTaskGraphHelper(lfd_trace, graph, current_node, visitedSet)
    return graph

def convertLFDTraceToTaskGraphHelper(lfd_trace, graph, current_node, visitedSet):
    global counter
    # TODO: Use matplotlib to plot node and edge attributes. Once this occurs, replace below line with:
    # node_id = str(self.counter)
    node_id = str(counter) + ": " + current_node[1]
    counter += 1
    visitedSet[current_node] = node_id
    graph.add_node(node_id, action=current_node[1])
    for neighbor in lfd_trace[current_node[1]]:
        current_node_state_comp = list(current_node[0])
        current_node_state_comp.append('s' + current_node[1][len(current_node) - 1])
        next_node_state_comp = tuple(current_node_state_comp)
        if collections.Counter(next_node_state_comp) == collections.Counter(neighbor[0]):
            if neighbor not in visitedSet:
                convertLFDTraceToTaskGraphHelper(lfd_trace, graph, neighbor, visitedSet)
            graph.add_edge(node_id, visitedSet[neighbor], state_composition=neighbor[0])


####End of Legacy Code#####

# Each state with id (e.g. 's6') represents a unique state vector.
class StateVectorTaskGraphBuilder:
    def __init__(self):
        self.counter = 0

    # a0 = 'idle_action'
    # a6 = 'terminate_action'
    def getLFDTrace(self):
        # Nodes are in the format of:
        # adjList[action] = ('state before action', 'state after action', 'successor action node')
        adjList = {}
        adjList['a0'] = [('', 's0', 'a1'), ('', 's0', 'a2')]
        adjList['a1'] = [('s0', 's1', 'a2'), ('s8', 's9', 'a5')]
        adjList['a2'] = [('s1', 's3', 'a3'), ('s1', 's3', 'a4'), ('s0', 's2', 'a3'), ('s0', 's2', 'a4')]
        adjList['a3'] = [('s3', 's6', 'a4'), ('s7', 's9', 'a5'), ('s2', 's4', 'a4'), ('s5', 's8', 'a1')]
        adjList['a4'] = [('s6', 's9', 'a5'), ('s3', 's7', 'a3'), ('s4', 's8', 'a1'), ('s2', 's5', 'a3')]
        adjList['a5'] = [('s9', 's10', 'a6')]
        adjList['a6'] = []
        return adjList

    def getLFDTrace2(self):
        adjList = {}
        adjList['a0'] = [('', 's0', 'a1'), ('', 's0', 'a2'), ('', 's0', 'a3')]
        adjList['a1'] = [('s0', 's1', 'a4')]
        adjList['a2'] = [('s0', 's1', 'a4')]
        adjList['a3'] = [('s0', 's2', 'a5')]
        adjList['a4'] = [('s1', 's2', 'a5')]
        adjList['a5'] = []
        return adjList

    def convertLFDTraceToTaskGraph(self, lfd_trace, root_state, root_action):
        graph = nx.DiGraph()
        current_node = (root_state, root_action)
        visitedSet = {}
        self.convertLFDTraceToTaskGraphHelper(lfd_trace, graph, current_node, visitedSet)
        return graph

    # Current_node is a tuple containing previous state (edge) and current action (node)
    def convertLFDTraceToTaskGraphHelper(self, lfd_trace, graph, current_node, visitedSet):
        #TODO: Use matplotlib to plot node and edge attributes. Once this occurs, replace below line with:
        #node_id = str(self.counter)
        node_id = str(self.counter) + " - " + current_node[1]
        self.counter += 1
        visitedSet[current_node] = node_id
        graph.add_node(node_id, action=current_node[1])
        for neighbor in lfd_trace[current_node[1]]:
            if current_node[0] == neighbor[0]:
                neighbor_node = (neighbor[1], neighbor[2])
                if neighbor_node not in visitedSet:
                    self.convertLFDTraceToTaskGraphHelper(lfd_trace, graph, neighbor_node, visitedSet)
                graph.add_edge(node_id, visitedSet[neighbor_node], state=neighbor[1], prob=lfd_trace[current_node[1]][neighbor])


class StateCompositionTaskGraphBuilder:

    def __init__(self):
        self.counter = 0

    # a0 = 'idle_action'
    # a6 = 'terminate_action'
    def getLFDTrace(self):
        adjList = {}
        adjList['a0'] = [(('s0',), 'a1'), (('s0',), 'a2')]
        adjList['a1'] = [(('s0', 's1'), 'a2'), (('s0', 's1', 's2', 's3', 's4'), 'a5')]
        adjList['a2'] = [(('s0', 's1', 's2'), 'a3'), (('s0', 's1', 's2'), 'a4'), (('s0', 's2'), 'a3'),
                      (('s0', 's2'), 'a4')]
        adjList['a3'] = [(('s0', 's1', 's2', 's3'), 'a4'), (('s0', 's2', 's3'), 'a4'), (('s0', 's2', 's3', 's4'), 'a1'),
                      (('s0', 's1', 's2', 's3', 's4'), 'a5')]
        adjList['a4'] = [(('s0', 's1', 's2', 's4'), 'a3'), (('s0', 's2', 's4'), 'a3'), (('s0', 's2', 's3', 's4'), 'a1'),
                      (('s0', 's1', 's2', 's3', 's4'), 'a5')]
        adjList['a5'] = [(('s0', 's1', 's2', 's3', 's4', 's5'), 'a6')]
        adjList['a6'] = []
        return adjList


    def convertLFDTraceToTaskGraph(self, lfd_trace):
        graph = nx.DiGraph()
        current_node = ((), 'a0')
        visitedSet = {}
        self.convertLFDTraceToTaskGraphHelper(lfd_trace, graph, current_node, visitedSet)
        return graph


    def convertLFDTraceToTaskGraphHelper(self, lfd_trace, graph, current_node, visitedSet):
        # TODO: Use matplotlib to plot node and edge attributes. Once this occurs, replace below line with:
        # node_id = str(self.counter)
        node_id = str(self.counter) + ": " + current_node[1]
        self.counter += 1
        visitedSet[current_node] = node_id
        graph.add_node(node_id, action=current_node[1])
        for neighbor in lfd_trace[current_node[1]]:
            current_node_state_comp = list(current_node[0])
            current_node_state_comp.append('s' + current_node[1][len(current_node) - 1])
            next_node_state_comp = tuple(current_node_state_comp)
            if collections.Counter(next_node_state_comp) == collections.Counter(neighbor[0]):
                if neighbor not in visitedSet:
                    self.convertLFDTraceToTaskGraphHelper(lfd_trace, graph, neighbor, visitedSet)
                graph.add_edge(node_id, visitedSet[neighbor], state_composition=neighbor[0])


def main():
    taskGraphBuilder = StateVectorTaskGraphBuilder()
    lfdTrace = taskGraphBuilder.getLFDTrace()
    graph = taskGraphBuilder.convertLFDTraceToTaskGraph(lfdTrace)
    # TODO: Use matplotlib to draw the graph.
    print('compiled graph')


if __name__ == '__main__':
    main()
