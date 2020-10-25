# -*- coding: utf-8 -*-
"""
Checking graph probabilities
"""
from demonstrations_to_graph_v2 import split_task_plan, construct_task_plans, construct_transition_with_probabilities
from restructure_graph import bfs_search, reach_terminate_node, least_common_successor, find_choices, group_choices, return_choices 
import networkx as nx

if __name__=="__main__":
#    path1 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a3', 's3', 'terminate_action']
#    path2 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a3', 's3', 'terminate_action']
#    path3 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a3', 's3', 'terminate_action']
#    path4 = ['', 'a0', 's4', 'a4', 's5', 'a5', 's6', 'a6', 's3', 'terminate_action']
    
    path1 = ['', 'a0', 'sA', 'a1', 'sB', 'a2', 'sC', 'a3', 'sD', 'a4', 'sE', 'a5', 'sF', 'terminate_action']
    path2 = ['', 'a0', 'sA', 'a6', 'sD', 'a4', 'sE', 'a7', 'sB', 'a2', 'sC', 'a8', 'sF', 'terminate_action']
    
    task_plans = [path1, path2]
    task_plans_collection = construct_task_plans(task_plans)
    transitions = construct_transition_with_probabilities(task_plans_collection)
    print(transitions)
    
    
#    G = {'a0':['a1', 'a6'],
#         'a1':['a2'], 'a6':['a4'],
#         'a2':['a3', 'a8'], 'a4':['a7', 'a5'],
#         'a3':['a4'], 'a7':['a2'], 'a5':['terminate_action'], 'a8':['terminate_action']}
    
    G = nx.DiGraph()
    G.add_nodes_from(['a0','a1','a2','a3','a4','a5','a6','a7','a8','terminate_acion'])
    G.add_edges_from([('a0', 'a1'), ('a0', 'a6'), ('a1','a2'), ('a6','a4'), ('a2','a3'), ('a2','a8'), ('a4','a7'),
                      ('a4','a5'), ('a3','a4'), ('a7','a2'), ('a5','terminate_action'), ('a8','terminate_action')])
    
    level, parent = bfs_search(G, 'a0')
    
    print("level:",level)
    
