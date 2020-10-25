import networkx as nx
import htn
from subprocess import check_call
import pydot

choiceid = 0
seqid = 0

def create_init_htn_graph(task_graph):
    htn_graph = nx.DiGraph()
    temp_dict = {}
    for action_node in task_graph.nodes:
        prestate = ""
        for in_edge in task_graph.in_edges(action_node):
            prestate = task_graph.edges[in_edge[0], in_edge[1]]['state']
            break
        poststate = ""
        for out_edge in task_graph.out_edges(action_node):
            poststate = task_graph.edges[out_edge[0], out_edge[1]]['state']
            break
        primitive_node = htn.PrimitiveNode(action_node, prestate, poststate)
        temp_dict[action_node] = primitive_node
        htn_graph.add_node(primitive_node)

    for edge in task_graph.edges:
        htn_graph.add_edge(temp_dict[edge[0]], temp_dict[edge[1]], prob=task_graph.edges[edge]['prob'])

    return htn_graph

def combine_htns_in_parallel(htn_graph, htn1, htn2):
    global choiceid
    htn1_predecessors = list(htn_graph.predecessors(htn1))
    htn1_successors = list(htn_graph.successors(htn1))

    htn1_prob = htn_graph.get_edge_data(htn1_predecessors[0], htn1)['prob']
    htn2_prob = htn_graph.get_edge_data(htn1_predecessors[0], htn2)['prob']

    htn_graph.remove_node(htn1)
    htn_graph.remove_node(htn2)

    if htn1.__class__.__name__ == 'ChoiceNode' and htn2.__class__.__name__ == 'ChoiceNode':
        htn1.add_children_with_freq(htn2.getChildren(), htn2.get_children_freq())
        choice_node = htn1
    elif htn2.__class__.__name__ == 'ChoiceNode':
        htn2.add_child_with_freq(htn1, htn1_prob)
        choice_node = htn2
    elif htn1.__class__.__name__ == 'ChoiceNode':
        htn1.add_child_with_freq(htn2, htn2_prob)
        choice_node = htn1
    else:
        choice_node = htn.ChoiceNode('C' + str(choiceid), htn1.prestate, htn1.poststate)
        choiceid += 1
        choice_node.add_child_with_freq(htn1, htn1_prob)
        choice_node.add_child_with_freq(htn2, htn2_prob)


    htn_graph.add_node(choice_node)
    htn_graph.add_edge(htn1_predecessors[0], choice_node, prob=htn1_prob + htn2_prob)
    htn_graph.add_edge(choice_node, htn1_successors[0], prob=1.0)

def check_and_combine_htns_in_parallel(htn_graph):
    combined_htns_in_parallel = False
    for htn1 in htn_graph.nodes:
        for htn2 in htn_graph.nodes:
            htn1_predecessors = list(htn_graph.predecessors(htn1))
            htn2_predecessors = list(htn_graph.predecessors(htn2))
            htn1_successors = list(htn_graph.successors(htn1))
            htn2_successors = list(htn_graph.successors(htn2))
            if htn1 != htn2 and len(htn1_predecessors) == 1 and len(htn2_predecessors) == 1 \
                    and len(htn1_successors) == 1 and len(htn2_successors) == 1 \
                    and htn1_predecessors[0] == htn2_predecessors[0] \
                    and htn1_successors[0] == htn2_successors[0]:
                # print("Combining ", htn1, " and ", htn2, " in parallel")
                combine_htns_in_parallel(htn_graph, htn1, htn2)
                combined_htns_in_parallel = True
                break
        else:
            continue
        break
    return combined_htns_in_parallel, htn1, htn2


# htn1 connects to htn2
def combine_htns_in_series(htn_graph, htn1, htn2):
    global seqid
    htn1_predecessors_with_prob = []
    for predecessor in htn_graph.predecessors(htn1):
        htn1_pred_prob = htn_graph.get_edge_data(predecessor, htn1)['prob']
        htn1_predecessors_with_prob.append((predecessor, htn1_pred_prob))
    htn2_successors_with_prob = []
    for successor in htn_graph.successors(htn2):
        htn2_succ_prob = htn_graph.get_edge_data(htn2, successor)['prob']
        htn2_successors_with_prob.append((successor, htn2_succ_prob))

    htn_graph.remove_node(htn1)
    htn_graph.remove_node(htn2)

    if htn1.__class__.__name__ == 'SequentialNode' and htn2.__class__.__name__ == 'SequentialNode':
        htn1.add_children(htn2.get_children())
        htn1.poststate = htn2.poststate
        sequence_node = htn1
    elif htn2.__class__.__name__ == 'SequentialNode':
        htn2.add_child_to_front(htn1)
        htn2.prestate = htn1.prestate
        sequence_node = htn2
    elif htn1.__class__.__name__ == 'SequentialNode':
        htn1.add_child(htn2)
        htn1.poststate = htn2.poststate
        sequence_node = htn1
    else:
        sequence_node = htn.SequentialNode('S' + str(seqid), htn1.prestate, htn2.poststate)
        seqid += 1
        sequence_node.add_child(htn1)
        sequence_node.add_child(htn2)

    htn_graph.add_node(sequence_node)
    for htn1_pred, htn1_pred_prob in htn1_predecessors_with_prob:
        htn_graph.add_edge(htn1_pred, sequence_node, prob=htn1_pred_prob)
    for htn2_succ, htn2_succ_prob in htn2_successors_with_prob:
        htn_graph.add_edge(sequence_node, htn2_succ, prob=htn2_succ_prob)

def check_and_combine_htns_in_series(htn_graph):
    combined_htns_in_series = False
    for htn1 in htn_graph.nodes:
        # print(combined_htns_in_series)
        for htn2 in htn_graph.nodes:
            htn1_predecessors = list(htn_graph.predecessors(htn1))
            htn2_predecessors = list(htn_graph.predecessors(htn2))
            htn1_successors = list(htn_graph.successors(htn1))
            htn2_successors = list(htn_graph.successors(htn2))
            if htn1 != htn2:
                if len(htn1_successors) == 1 and len(htn2_predecessors) == 1 and htn1_successors[0] == htn2:
                    # print("Combining ", htn1, " and ", htn2, " in series -- ", htn1, " connects to ", htn2)
                    combine_htns_in_series(htn_graph, htn1, htn2)
                    combined_htns_in_series = True
                    break

                if len(htn2_successors) == 1 and len(htn1_predecessors) == 1 and htn2_successors[0] == htn1:
                    # print("Combining ", htn2, " and ", htn1, " in series -- ", htn2, " connects to ", htn1)
                    combine_htns_in_series(htn_graph, htn2, htn1)
                    combined_htns_in_series = True
                    break
        else:
            continue
        break
    return combined_htns_in_series, htn1, htn2

def visualize_with_graphviz_dot(digraph, file_name):
    nx.drawing.nx_pydot.write_dot(digraph, "./debug_graphs/"+file_name + ".dot")
    check_call(['dot', '-Tpng', "./debug_graphs/"+file_name + '.dot', '-o', "./debug_graphs/"+file_name + '.png'])

def task_graph_to_htn(task_graph):
    htn_graph = create_init_htn_graph(task_graph)
    # print(nx.to_dict_of_lists(htn_graph))

    no = 0
    while len(list(htn_graph.nodes)) > 1:
        combined_htns_in_parallel, htn1, htn2 = check_and_combine_htns_in_parallel(htn_graph)
        combined_htns_in_series, htn3, htn4 = check_and_combine_htns_in_series(htn_graph)
        
        # print("start of iteration")
        # print(htn1)
        # print(htn2)
        # print(htn3)
        # print(htn4)

        ## plot the reduced graph at each iteration to check for bugs
        visualize_with_graphviz_dot(htn_graph, str(no))
        no += 1

        if not (combined_htns_in_series or combined_htns_in_parallel):
            # print("graph:", nx.to_dict_of_lists(htn_graph))
            # print("type of graph:", type(htn_graph))
            # print("Unable to create HTN graph")
            return htn_graph
            break

    # if len(list(htn_graph.nodes)) == 1:
    #     print("Created HTN graph")


    # print(nx.to_dict_of_lists(htn_graph))
    # print(list(htn_graph.nodes)[0])

    return list(htn_graph.nodes)[0]