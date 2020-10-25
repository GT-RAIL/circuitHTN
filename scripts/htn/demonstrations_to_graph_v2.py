import numpy as np
import copy 
import networkx as nx
import matplotlib.pyplot as plt
from lfd_trace_to_task_graph import *
import collections
import json

def split_task_plan(path):
	return [(path[i], path[i + 1], path[i + 2], path[i+3])
        for i in range(0, len(path) - 3, 2)]

def construct_task_plans(task_plans):
	task_plans_collection = []
	for individual_task_plan in task_plans:
		task_plans_collection.append(copy.deepcopy(split_task_plan(individual_task_plan)))
	return task_plans_collection

def construct_transition_with_probabilities(task_plans_collection):
	# transition_probabilities[action] returns a dict whose keys are transitions in the form of a 3-tuple:
	# (predecessor_state, successor_state, successor_action)
	# transition_probabilities[action][transition] = probability of transition
	transition_probabilities = {}
	for plan in task_plans_collection:
		for action_state_tuple in plan:
			if action_state_tuple[1] not in transition_probabilities:
				transition_probabilities[action_state_tuple[1]] = {}
			transition = (action_state_tuple[0], action_state_tuple[2], action_state_tuple[3])
			if transition in transition_probabilities[action_state_tuple[1]]:
				transition_probabilities[action_state_tuple[1]][transition] += 1
			else:
				transition_probabilities[action_state_tuple[1]][transition] = 1
	for action in transition_probabilities:
		total_freq = 0.0
		for transition in transition_probabilities[action]:
			total_freq += transition_probabilities[action][transition]
		for transition in transition_probabilities[action]:
			transition_probabilities[action][transition] /= total_freq
	# Hacky solution to get a key for the terminating action:
	transition_probabilities[task_plans_collection[0][-1][-1]] = {}
	return transition_probabilities

def all_transitions(transitions):
	for a0 in transitions:
		for(s0, s1, a1) in transitions[a0]:
			yield(s0, a0, s1, a1)


if __name__=="__main__":
	# with open('chair_state_1.json', 'r') as fp:
	# 	chair_state = json.load(fp)

	# with open('chair_action_1.json', 'r') as fq:
	# 	chair_action = json.load(fq)

	# print(chair_state)
	# print(chair_action)

	## linear graph plan
	path1 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a3', 's3', 'terminate_action']

	## single split plan
	# path1 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a3', 's3', 'a5', 's5', 'terminate_action']
	# path2 = ['', 'a0', 's0', 'a1', 's1', 'a4', 's3', 'a5', 's5', 'terminate_action']

	## double split plan
	# path1 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a4', 's5', 'a6', 's6', 'terminate_action']
	# path2 = ['', 'a0', 's0', 'a1', 's1', 'a3', 's2', 'a4', 's5', 'a6', 's6', 'terminate_action']
	# path3 = ['', 'a0', 's0', 'a5', 's5', 'a6', 's6', 'terminate_action']

	## triple split plan
	# path1 = ['', 'a0', 's0', 'a1', 's4', 'a4', 's5', 'terminate_action']
	# path2 = ['', 'a0', 's0', 'a2', 's4', 'a4', 's5', 'terminate_action']
	# path3 = ['', 'a0', 's0', 'a3', 's4', 'a4', 's5','terminate_action']

	## chair plan
	# path1 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's2', 'a3', 's3', 'a4', 's4', 'a5', 's9', 'a6', 's10', 'terminate_action']
	# path2 = ['', 'a0', 's0', 'a3', 's5', 'a4', 's6', 'a1', 's7', 'a2', 's4', 'a5', 's9', 'a6', 's10', 'terminate_action']

	## random complicated plan
	# path1 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's3', 'a3', 's6', 'a4', 's9', 'a5', 's10', 'a6']
	# path2 = ['', 'a0', 's0', 'a1', 's1', 'a2', 's3', 'a4', 's7', 'a3', 's9', 'a5', 's10', 'a6']
	# path3 = ['', 'a0', 's0', 'a2', 's2', 'a3', 's4', 'a4', 's8', 'a1', 's9', 'a5', 's10', 'a6']
	# path4 = ['', 'a0', 's0', 'a2', 's2', 'a4', 's5', 'a3', 's8', 'a1', 's9', 'a5', 's10', 'a6']

	task_plans = []
	task_plans.append(path1)
	# task_plans.append(path2)
	# task_plans.append(path3)
	# task_plans.append(path4)
	task_plans_collection = construct_task_plans(task_plans)
	transitions = construct_transition_with_probabilities(task_plans_collection)
	# print(transitions)

	lfd_trace = {}
	for element in transitions:
		lfd_trace[element] = list(transitions[element])
	#lfd_trace['terminate_action'] = []

	# print(lfd_trace)
	taskGraphBuilder = StateVectorTaskGraphBuilder(lfd_trace)
	graph = taskGraphBuilder.convertLFDTraceToTaskGraph()
	print(graph)
	## Plot the Graph with Edge Attributes
	nx.draw_networkx(graph, with_labels=True)
	plt.show()
	print('compiled graph')
	
	
					
