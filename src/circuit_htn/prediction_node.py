#!/usr/bin/env python

from __future__ import print_function

from circuit_htn.srv import PredictNext, PredictNextResponse
import copy
from difflib import SequenceMatcher
import networkx as nx
import pickle
import rospkg
import rospy
from circuit_htn_node import CircuitHTNNode

class PredictionNode:

    def __init__(self):

        # Instance of RosPack with the default file path
        path = rospkg.RosPack().get_path('circuit_htn')

        # Load the task model
        model_name = rospy.get_param('~model_name', 'htn')
        print('Loading', (model_name + '.pkl...'))
        self.model = pickle.load(open(path + '/models/' + model_name + '.pkl', 'rb'))

        print(self.model.text_output())
        print('Task model loaded.')

        print('Calculating all paths through the model with associated probabilities...')
        self.paths = self.create_paths(self.model)
        self.path_strings = []
        for path in self.paths:
            self.path_strings.append(self.path_to_string(path['path']))
        print('All paths calculated.')
        print(self.path_strings)

        # initialize the service and pass in inputs
        self.service = rospy.Service('predict_next_action', PredictNext, self.predict_next)

    def prediction_test(self):
        '''load a data file to test prediction offline'''
        path = rospkg.RosPack().get_path('circuit_htn')
        frames = []
        with open(path + '/data/parallel.txt') as f:
            frames = f.readlines()
        frames = [x.strip() for x in frames]
        #actions = self.frames_to_action_list(frames)

        for i in range(len(frames)):
            action_preds, probs = self.predict_next_action(frames[0:i+1])
            output = 'next action: '
            for j in range(len(action_preds)):
                output += action_preds[j] + ' (' + str('{0:3.1f}'.format(probs[j]*100) + ')')
                if j+1 < len(action_preds):
                    output += ', '
            print(output)

    def frames_to_action_list(self, frames):
        ''' Filter a list of per-frame classifications to a list of actions (note: filtering behavior is hardcoded
        for the drill assembly task)

        :param frames: per-frame classification (list of strings)
        :return: list of actions
        '''
        actions = []
        prev_action = 'none'
        count = 0
        actions_seen = []
        for s in frames:
            if s == prev_action and count < 300:
                count += 1
                if count == 6 and s != 'none':
                    if s in actions_seen:
                        s += '2'
                    else:
                        actions_seen.append(s)
                        s += '1'
                    actions.append(s)
            else:
                count = 0
                prev_action = s
        return actions

    def path_to_string(self, path):
        ''' Change path (list of actions) to a string representation for string similarity functions
        :param path: a list of actions
        :return: list of actions in string form, where one character represents one action
        '''
        s = ''
        for a in path:
            s += self.action_to_char(a)
        return s

    def action_to_char(self, action):
        if action == 'grab_tools1':
            return 'a'
        elif action == 'attach_shell1':
            return 'b'
        elif action == 'screw1':
            return 'c'
        elif action == 'hold_for_robot1':
            return 'd'
        elif action == 'grab_tools2':
            return 'e'
        elif action == 'attach_shell2':
            return 'f'
        elif action == 'screw2':
            return 'g'
        elif action == 'hold_for_robot2':
            return 'h'

    def predict_next(self, req):
        actions, probs = self.predict_next_action(req.prev_actions)

        print('actions:', actions)
        print('probabilities:', probs)

        return PredictNextResponse([actions], [probs])

    def predict_next_action(self, action_history):
        path = self.frames_to_action_list(action_history)
        if len(path) == 0:
            action_pred = {}
            for i in range(len(self.paths)):
                next_action = self.paths[i]['path'][0]
                prob = self.paths[i]['prob']
                if action_pred.has_key(next_action):
                    action_pred[next_action] += prob
                else:
                    action_pred[next_action] = prob
            actions = sorted(action_pred, key=action_pred.get)
            actions.reverse()
            probs = action_pred.values()
            probs.sort()
            probs.reverse()
            return actions, probs

        # compute (Ratcliff-Obershelp) similarity between query sequence and every path
        path_string = self.path_to_string(path)
        action_pred = {}
        for i in range(len(self.paths)):
            compare_str = self.path_strings[i]
            full_path = self.paths[i]['path']
            if len(compare_str) > len(path_string):
                # compare_str = self.path_strings[i][:min(len(path_string)+1, len(compare_str))]  # buffer of 1 in case there's an incorrect number of actions
                compare_str = self.path_strings[i][:len(path_string)]  # assumes query sequence has correct number of actions

            # get next action in the matched path sequence (the action following the last action in the query path)
            next_i = self.path_strings[i].find(path_string[-1])
            if next_i == -1:
                continue
            next_i += 1
            if next_i >= len(full_path):
                next_action = 'end_task'
            else:
                next_action = full_path[next_i]

            # calculate similarity value [0,1] between paths, multiply by probability of path
            sm = SequenceMatcher(a=path_string, b=compare_str)
            prob = sm.ratio()*self.paths[i]['prob']

            # print('query:', path)
            # print('path:', self.paths[i]['path'])
            # print('similarity:', sm.ratio())

            # update action prediction probabilities
            if action_pred.has_key(next_action):
                action_pred[next_action] += prob
            else:
                action_pred[next_action] = prob

        # get action predictions sorted from highest to lowest probability
        actions = sorted(action_pred, key=action_pred.get)
        actions.reverse()
        probs = action_pred.values()
        probs.sort()
        probs.reverse()

        # normalize probabilities
        sum = 0
        for p in probs:
            sum += p
        for i in range(len(probs)):
            probs[i] /= float(sum)

        return actions, probs

    def find_root(self):
        nodes = list(self.model.nodes())
        n = nodes[0]
        while len(list(self.model.predecessors(n))) > 0:
            n = list(self.model.predecessors(n))[0]
        return n

    def create_paths(self, node, paths=[{'prob':1.0, 'path':[]}]):
        if node.node_type == CircuitHTNNode.PRIMITIVE:
            for p in paths:
                p['path'].append(node.action)
            return paths

        elif node.node_type == CircuitHTNNode.SEQUENCE:
            for child in node.children:
                paths = self.create_paths(child, paths)
            return paths

        elif node.node_type == CircuitHTNNode.CHOICE:
            in_paths = paths
            paths = []
            for i in range(len(node.children)):
                child_paths = copy.deepcopy(in_paths)
                for cp in child_paths:
                    cp['prob'] = cp['prob']*node.probabilities[i]
                child_paths = self.create_paths(node.children[i], child_paths)
                paths.extend(child_paths)
            return paths

        return paths


if __name__ == "__main__":

    rospy.init_node('prediction_node')
    classify = PredictionNode()
    print('Ready for action prediction.')

    # print()
    # print('Action filtering test:')
    # classify.prediction_test()

    rospy.spin()
