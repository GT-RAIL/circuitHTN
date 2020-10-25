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

class TableWorld:
    def __init__(self):
        self.cube1 = 'tray' # goal state is cup 
        self.cube2 = 'tray' # goal state is tray (same, doesn't move)
        self.tray = 'table1' # goal state is table1 (same, doesn't move)
        
        self.orange = 'table' # goal state is plate
        self.banana = 'table' # goal state is plate
        
        self.spoon = 'holder' # goal state is table2 (table2 is just the location where the user eats)
        self.knife = 'holder' # goal state is table2
        self.plate = 'holder' # goal state is table2
        
        self.cup = 'table1' # goal state is table2 
        self.water = 'bottle' # goal state is cup
        self.bottle = 'table1' # goal state is table1 (same, moves)
        
        self.holder = 'table1' # goal state is table1 (same, doesn't move)
    
    def update_step_world(self, action):
        if action == 'pickup_plate':
            self.plate = 'robot'
        elif action == 'place_plate':
            self.plate = 'table2'
        elif action == 'pickup_banana':
            self.banana = 'robot'
        elif action == 'place_banana':
            self.banana = 'plate'
        elif action == 'pickup_orange':
            self.orange = 'robot'
        elif action == 'place_orange':
            self.orange = 'plate'
        elif action == 'pickup_cup':
            self.cup = 'robot'
        elif action == 'place_cup':
            self.cup = 'table2'
        elif action == 'pickup_cube':
            self.cube1 = 'robot'
        elif action == 'place_cube':
            self.cube1 = 'cup'
        elif action == 'pickup_bottle':
            self.bottle = 'robot'
        elif action == 'pour_water':
            self.water = 'cup'
        elif action == 'place_bottle':
            self.bottle = 'table1'
        elif action == 'pickup_knife':
            self.knife = 'robot'
        elif action == 'place_knife':
            self.knife = 'table2'
        elif action == 'pickup_spoon':
            self.spoon = 'robot'
        elif action == 'place_spoon':
            self.spoon = 'table2'
        
    def return_state(self):
        state = tuple([self.cube1, self.cube2, self.tray, self.orange, self.banana, self.spoon, self.knife, self.plate,
                       self.cup, self.water, self.bottle, self.holder])
        return state

def run_actions_table(actions):
    final_state = None
    table_world = TableWorld()
    state_action_pairs = [table_world.return_state()]
    
    for i in range(len(actions)):
#        print(table_world.return_state())
#        print(actions[i])
        table_world.update_step_world(actions[i])
        state_action_pairs.append(actions[i])
        new_state = deepcopy(table_world.return_state())
        state_action_pairs.append(deepcopy(new_state))
        
        if i == len(actions) - 1:
            final_state = deepcopy(new_state)
    return state_action_pairs, final_state

def check_table_setting_validity(final_state):
    if final_state == ('cup', 'tray', 'table1', 'plate', 'plate', 'table2', 'table2', 'table2', 'table2', 'cup', 'table1', 'table1'):
        return True
    return False

def get_actions_from_demo_table(file):
    file_object = open(file, "r")
    actions = file_object.read().splitlines()
    return actions

def generate_pickle_file(dataset_folder):
    demonstrations = []
    for filename in os.listdir(dataset_folder):
        demonstrations.append(filename) 
    
    samples = [random.sample(list(itertools.combinations(demonstrations, 2)), 20), 
               random.sample(list(itertools.combinations(demonstrations, 4)), 20), 
               random.sample(list(itertools.combinations(demonstrations, 6)), 20), 
               random.sample(list(itertools.combinations(demonstrations, 8)), 20), 
               list(itertools.combinations(demonstrations, 10))] 
    with open('experiment_groups_table_setting.pkl', 'wb') as f:
        pickle.dump(samples, f)

if __name__=="__main__":
    dataset_folder = r"D:\Desktop\research\circuitHTN\simulator\table_setting_dataset"
    generate_pickle_file(dataset_folder)
    
#    with open('experiment_groups.pkl', 'rb') as p:
#        x = pickle.load(p)
#        print(x)
