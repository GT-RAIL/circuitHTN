"""
functions to simulate the chair construction task
"""
from copy import deepcopy
import pickle
from scipy.spatial import distance
import os
import itertools
import random
import numpy as np

class ChairWorld:
    def __init__(self):
        self.chair_top = 'table'
        self.left_side = 'table'
        self.right_side = 'table'
        self.back_leg = 'table'
        self.front_leg = 'table'
        self.chair_bottom = 'table'
        self.chair_orientation = 'flat'
    
    
    def update_step_world(self, action):
        
        action = action.replace(" ","")
        
        if action == 'place_right_side':
            self.right_side = 'chair'
            
        elif action == 'place_left_side':
            self.left_side = 'chair'
        
        elif action == 'pickup_left_side':
            self.left_side = 'hand'
            
        elif action == 'pickup_right_side':
            self.right_side = 'hand'
        
        elif action == 'pickup_chair_top':
            self.chair_top = 'hand'
            
        elif action == 'attach_chair_top':
            self.chair_top = 'chair'
        
        elif action == 'pickup_back_leg':
            self.back_leg = 'hand'
            
        elif action == 'attach_back_leg':
            self.back_leg = 'chair'
            
        elif action == 'pickup_front_leg':
            self.front_leg = 'hand'
            
        elif action == 'attach_front_leg':
            self.front_leg = 'chair'
            
        elif action == 'lift_chair_structure':
            self.chair_orientation = 'straight'
        
        elif action == 'pickup_chair_bottom':
            self.chair_bottom = 'hand'
            
        elif action == 'place_chair_bottom':
            self.chair_bottom = 'chair'
            
        else:
            return "Nothing"
    
    def return_orientation(self):
        return self.chair_orientation
    
    def return_state(self):
        state = tuple([self.chair_top, self.left_side, self.right_side, self.back_leg, 
                       self.front_leg, self.chair_bottom, self.chair_orientation])
    
        return state

def get_actions_from_demo(file):
    file_object = open(file, "r")
    actions = file_object.read().splitlines()
    return actions

def run_actions(actions):
    final_state = None
    chair_world = ChairWorld()
    state_action_pairs = [chair_world.return_state()]
    
    for i in range(len(actions)):
        print(chair_world.return_state())
        print(actions[i])
        output = chair_world.update_step_world(actions[i])
        print(output)
        if output != "Nothing":
            state_action_pairs.append(actions[i])
            new_state = deepcopy(chair_world.return_state())
            state_action_pairs.append(deepcopy(new_state))
        
        if i == len(actions) - 1:
            final_state = deepcopy(new_state)
    return state_action_pairs, final_state

def check_chair_validity(final_state):
    for state_att in final_state:
        if state_att == 'flat' or state_att == 'straight':
            continue
        
        if state_att != 'chair':
            return False
    
    return True

def generate_pickle_file(dataset_folder):
    demonstrators = list(range(1,16))
    demonstrations = {str(d):[] for d in demonstrators}
    for filename in os.listdir(dataset_folder):
        temp = filename.split('_')
        demonstrations[temp[1]].append(filename)
        
    
    combinations_2 = list(itertools.combinations(demonstrators, 2))
    combinations_4 = list(itertools.combinations(demonstrators, 4))
    combinations_6 = list(itertools.combinations(demonstrators, 6))
    combinations_8 = list(itertools.combinations(demonstrators, 8))
    combinations_10 = list(itertools.combinations(demonstrators, 10))
    
    samples_2 = [[np.random.choice(demonstrations[str(l)])for l in d] 
                 for d in random.sample(combinations_2, 20)]
    samples_4 = [[np.random.choice(demonstrations[str(l)])for l in d] 
                 for d in random.sample(combinations_4, 20)]
    samples_6 = [[np.random.choice(demonstrations[str(l)])for l in d] 
                 for d in random.sample(combinations_6, 20)]
    samples_8 = [[np.random.choice(demonstrations[str(l)])for l in d] 
                 for d in random.sample(combinations_8, 20)]
    samples_10 = [[np.random.choice(demonstrations[str(l)])for l in d] 
                 for d in random.sample(combinations_10, 20)]
    
    samples = [samples_2, samples_4, samples_6, samples_8, samples_10]
    
    with open('experiment_groups', 'wb') as f:
        pickle.dump(samples, f)

def calculate_results_for_demos(demos, dataset_folder):
    final_chair = {'invalid':0}
    avg_length = 0
    for demo in demos: 
        demo_file_name = os.path.join(dataset_folder, demo)
        demo_actions = get_actions_from_demo(demo_file_name)
        state_action_pairs, final_state = run_actions(demo_actions)
        
        if check_chair_validity(final_state):
            if final_state in final_chair.keys():
                final_chair[final_state] += 1
            else:
                final_chair[final_state] = 1
        else:
            final_chair['invalid'] += 1
        
        avg_length += len(demo_actions)
    
    avg_length /= float(len(demos))
    
    return final_chair, avg_length

def calculate_results_for_approach(demos, approach, demo_stats):
    actions_file_name = ''
    for i in range(len(demos)):
        actions_file_name += str(demos[i])
        if i < len(demos) - 1:
            actions_file_name += '-'
        else:
            actions_file_name += '.pkl'

    actions_file = open(approach + '/' + actions_file_name, 'rb')
    actions_list = pickle.load(actions_file)

    final_chair = {'invalid': 0}
    for k in demo_stats.keys():
        final_chair[k] = 0

    avg_length = 0
    for actions in actions_list:
        avg_length += len(actions)
        state_action_pairs, final_state = run_actions(actions)
        if check_chair_validity(final_state):
            if final_state in final_chair.keys():
                final_chair[final_state] += 1
            else:
                final_chair[final_state] = 1
        else:
            final_chair['invalid'] += 1
    avg_length /= float(len(actions_list))

    return final_chair, avg_length

def calculate_all_results(demos, approach):
    final_chairs_demo, avg_length_demo = calculate_results_for_demos(demos)
    final_chairs, avg_length = calculate_results_for_approach(demos, approach, final_chairs_demo)

    for k in final_chairs.keys():
        if k not in final_chairs_demo.keys():
            final_chairs_demo[k] = 0

    demo_dist = []
    approach_dist = []
    demo_count = 0
    approach_count = 0
    for k in final_chairs_demo.keys():
        approach_count += final_chairs[k]
        demo_count += final_chairs_demo[k]
        if k != 'invalid':
            approach_dist.append(final_chairs[k])
            demo_dist.append(final_chairs_demo[k])
    approach_dist.append(final_chairs['invalid'])
    demo_dist.append(final_chairs_demo['invalid'])

    for i in range(len(approach_dist)):
        approach_dist[i] /= float(approach_count)

    for i in range(len(demo_dist)):
        demo_dist[i] /= float(demo_count)

    # print()
    # print(demo_dist)
    # print(approach_dist)
    print(approach_dist[len(approach_dist) - 1], distance.jensenshannon(demo_dist, approach_dist), avg_length - avg_length_demo)


if __name__ == "__main__":
    dataset_folder = r"C:\Users\nithi\Desktop\research\circuitHTN\simulator\chair_assembly_dataset\demo_15_3.txt"
    actions = get_actions_from_demo(dataset_folder)
    s_a, state = run_actions(actions)
    print(state)
#    generate_pickle_file(dataset_folder)
#    chair_world = ChairWorld()
#    
#    actions = ['place_right_side', 'pickup_chair_top', 'attach_chair_top', 'pickup_back_leg',
#               'attach_back_leg', 'pickup_front_leg', 'attach_front_leg', 'pickup_left_side',
#               'place_left_side', 'lift_chair_structure', 'pickup_chair_bottom', 'place_chair_bottom']
#    
#    for a in actions:
#        chair_world.update_step_world(a)
#    
#    print(chair_world.return_state())
        