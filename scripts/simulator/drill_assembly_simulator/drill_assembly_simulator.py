# -*- coding: utf-8 -*-
"""
Functions to simulate table setting task
"""
from copy import deepcopy
import pickle
from scipy.spatial import distance
import os
import itertools
import random
import numpy as np

class DrillWorld:
    def __init__(self):
        self.parts1_gathered = False
        self.shell1_attached = False
        self.screws1_attached = False
        self.battery1_attached = False
        self.drill1_finished = False
        self.parts2_gathered = False
        self.shell2_attached = False
        self.screws2_attached = False
        self.battery2_attached = False
        self.drill2_finished = False
    
    def update_step_world(self, action):
        if action == 'grab_tools':
            if not self.parts1_gathered:
                self.parts1_gathered = True
            else:
                self.parts2_gathered = True
        elif action == 'attach_shell':
            if not self.shell1_attached:
                self.shell1_attached = True
            else:
                self.shell2_attached = True
        elif action == 'screw':
            if not self.screws1_attached:
                self.screws1_attached = True
            else:
                self.screws2_attached = True
        elif action == 'hold_for_robot':
            if not self.battery1_attached:
                self.battery1_attached = True
                self.drill1_finished = True
            else:
                self.battery2_attached = True
                self.drill2_finished = True
        elif action == 'grab_tools1':
            self.parts1_gathered = True
        elif action == 'attach_shell1':
            self.shell1_attached = True
        elif action == 'screw1':
            self.screws1_attached = True
        elif action == 'hold_for_robot1':
            self.battery1_attached = True
            self.drill1_finished = True
        elif action == 'grab_tools2':
            self.parts2_gathered = True
        elif action == 'attach_shell2':
            self.shell2_attached = True
        elif action == 'screw2':
            self.screws2_attached = True
        elif action == 'hold_for_robot2':
            self.battery2_attached = True
            self.drill2_finished = True

        
    def return_state(self):
        state = tuple([self.parts1_gathered, self.parts2_gathered, self.shell1_attached, self.shell2_attached,
                       self.screws1_attached, self.screws2_attached, self.battery1_attached, self.battery2_attached,
                       self.drill1_finished, self.drill2_finished])
        return state

def run_actions_drill(actions):
    final_state = None
    drill_world = DrillWorld()
    state_action_pairs = [drill_world.return_state()]
    
    for i in range(len(actions)):
#        print(table_world.return_state())
#        print(actions[i])
        drill_world.update_step_world(actions[i])
        state_action_pairs.append(actions[i])
        new_state = deepcopy(drill_world.return_state())
        state_action_pairs.append(deepcopy(new_state))
        
        if i == len(actions) - 1:
            final_state = deepcopy(new_state)
    return state_action_pairs, final_state

def check_drill_assembly_validity(final_state):
    return final_state[8] and final_state[9]

def get_actions_from_demo_drill(file):
    file_object = open(file, "r")
    frames = file_object.read().splitlines()
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

# def generate_pickle_file(dataset_folder):
#     demonstrations = []
#     for filename in os.listdir(dataset_folder):
#         demonstrations.append(filename)
#
#     samples = [random.sample(list(itertools.combinations(demonstrations, 2)), 20),
#                random.sample(list(itertools.combinations(demonstrations, 4)), 20),
#                random.sample(list(itertools.combinations(demonstrations, 6)), 20),
#                random.sample(list(itertools.combinations(demonstrations, 8)), 20),
#                list(itertools.combinations(demonstrations, 10))]
#     with open('experiment_groups_table_setting.pkl', 'wb') as f:
#         pickle.dump(samples, f)
#
# if __name__=="__main__":
#     dataset_folder = r"D:\Desktop\research\circuitHTN\simulator\table_setting_dataset"
#     generate_pickle_file(dataset_folder)
    
#    with open('experiment_groups.pkl', 'rb') as p:
#        x = pickle.load(p)
#        print(x)
