# -*- coding: utf-8 -*-
"""
Intelligent circuitHTN
"""
import time
import pickle
import networkx as nx
import numpy as np
from task_graph_to_htn import *
from lfd_trace_to_task_graph import *
from htn import *
from demonstrations_to_graph_v2 import *
from subprocess import check_call
import pydot
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator.simulator import *
from os import listdir
from os.path import isfile, join
from graphviz import *
from copy import deepcopy
from restructure_graph import *

SALAD_DEMONSTRATION_DIR = "../simulator/50_salad_dataset/ann-ts/activityAnnotationsFilteredOrdered/"

def generate_action_graphs_from_demonstrations(paths):
    task_plans_collection = construct_task_plans(paths)
    lfd_trace = construct_transition_with_probabilities(task_plans_collection)
    root_state = paths[0][0]
    root_action = paths[0][1]
    actionGraphBuilder = StateVectorTaskGraphBuilder()
    action_graph = actionGraphBuilder.convertLFDTraceToTaskGraph(lfd_trace, root_state, root_action)
    return action_graph

def salad_demonstrations_to_htn(demos):
    paths = []
    for demo in demos:
        demo_file_name = '../simulator/50_salad_dataset/ann-ts/activityAnnotationsFilteredOrdered/'
        if demo < 10:
            demo_file_name += '0'
        demo_file_name += str(demo) + '-1-activityAnnotation.txt'

        demo_actions = get_actions_from_demo(demo_file_name)

        state_action_pair, final_state = run_actions(demo_actions)

        # state_action_pair = get_state_action_pair_from_demonstration_file(filename)
        state_action_pair.insert(0, "init_action")
        state_action_pair.insert(0, "init_state")
        state_action_pair.pop()
        state_action_pair.append("term_state")
        state_action_pair.append("term_action")
        paths.append(state_action_pair)
    return generate_action_graphs_from_demonstrations(paths)

def action_graph_to_htn(action_graph):
    htn_graph = create_init_htn_graph(action_graph)
    for action in htn_graph.nodes:
        action_name = action.get_name()
        if action_name.find('init_action') != -1:
            node_start = action
        elif action.name.find('term_action') != -1:
            node_terminate = action

    start_time = time.time()
    while len(list(htn_graph.nodes)) > 1:
        prev_node_count = len(list(htn_graph.nodes))
        combined_htns_in_parallel, htn1, htn2 = check_and_combine_htns_in_parallel(htn_graph)
        combined_htns_in_series, htn3, htn4 = check_and_combine_htns_in_series(htn_graph)
        
        if not(combined_htns_in_series or combined_htns_in_parallel):
            restructure_htn_graph(htn_graph, node_start, node_terminate)

        if time.time() - start_time > 30:
            return -1, False

    # if len(list(htn_graph.nodes)) == 1:
        # print("HTN Created")

    return list(htn_graph.nodes)[0], True

def action_graph_to_htn_naive(action_graph):
    htn_graph = create_init_htn_graph(action_graph)
    for action in htn_graph.nodes:
        action_name = action.get_name()
        if action_name.find('init_action') != -1:
            node_start = action
        elif action.name.find('term_action') != -1:
            node_terminate = action

    while len(list(htn_graph.nodes)) > 1:
        combined_htns_in_parallel, htn1, htn2 = check_and_combine_htns_in_parallel(htn_graph)
        combined_htns_in_series, htn3, htn4 = check_and_combine_htns_in_series(htn_graph)

        if not(combined_htns_in_series or combined_htns_in_parallel):
            return -1, False

    # if len(list(htn_graph.nodes)) == 1:
        # print("HTN Created")

    return list(htn_graph.nodes)[0], True
    
def visualize_with_graphviz_dot(digraph, file_name):
    nx.drawing.nx_pydot.write_dot(digraph, file_name + ".dot")
    check_call(['dot', '-Tpng', file_name + '.dot', '-o', file_name + '.png'])
    
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int)
    args = parser.parse_args()

    in_file = open('demo_list.pkl', 'rb')
    demo_list = pickle.load(in_file)

    demos = demo_list[args.n]
    action_graph = salad_demonstrations_to_htn(demos)
    # visualize_with_graphviz_dot(action_graph, 'action_graph')
    built_htn, result = action_graph_to_htn_naive(action_graph)

    if result == False:
        print('reduction failed for demo set:', args.n)
    else:
        action_lists = []
        for i in range(100):
            random_walk = built_htn.random_walk()
            actions = []
            for element in random_walk:
                action = element.get_name()
                if 'init_action' in action or 'term_action' in action:
                    continue
                action = action.split(' ')[-1]
                action = action.split('-')[0]
                actions.append(action)
            action_lists.append(actions)

        file_name = ''
        for i in range(len(demos)):
            file_name += str(demos[i])
            if i < len(demos) - 1:
                file_name += '-'
        out_file = open(file_name + '.pkl', 'wb')
        pickle.dump(action_lists, out_file)

        print(built_htn.count_choices(), built_htn.count_sequences(), built_htn.count_edges())

        # htn_digraph = convertToDiGraph(built_htn)
        # visualize_with_graphviz_dot(htn_digraph, 'htn')
    
    
    
