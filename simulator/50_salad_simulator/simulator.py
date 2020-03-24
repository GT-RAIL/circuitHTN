# -*- coding: utf-8 -*-

import pickle
from frozendict import frozendict
from copy import deepcopy
from scipy.spatial import distance

"""
Simulator for Testing HTNs

Cut and mix ingredients
Prepare dressing
Mix dressing

Salad 1:
    
Salad Bowl: Object (Binary List); Mix
Salad Plate
Cutting Board
Dressing Bowl; Mix Dressing Core
Tomato: Cut; Place
Cheese: Cut; Place
Lettuce: Cut; Place
Cucumber: Peel; Cut; Place
Salt: Add
Vinegar: Add
Oil: Add
Pepper: Add

Salad 2:
    
Salad Bowl: Object (Binary List); Mix
Salad Plate
Cutting Board
Dressing Bowl
Tomato: Cut; Place
Cheese: Cut; Place
Cucumber: Peel; Cut; Place
Salt: Add
Vinegar: Add
Oil: Add
Pepper: Add

Actions: Cut, Peel, Place, Mix, Add

Notes: People cut tomatoes in  two halves, they do it cut half 1, place bowl 1, cut half 2, place bowl 2

Look ahead in the dataset to see if "cut" of a particular object is done and then update the "cut" at each step
Look ahead in the dataset to see if the "place" of a particular object is done and then update the "place" state at each step
Look ahead in the dataset to see if the "mix" is done and then update at each step 

Actions: 
cut_tomato_core, place_tomato_into_bowl_core
cut_cheese_core, place_cheese_into_bowl_core
cut_lettuce_core, place_lettuce_into_bowl_core
peel_cucumber_core, cut_cucumber_core, place_cucumber_into_bowl_core
add_pepper_core, add_vinegar_core, add_oil_core, add_salt_core
mix_dressing_core, add_dressing_core
mix_ingredients_core
serve_salad_onto_plate_core

check if add dressing core is there, check if 

Need to have a forced instance of Done so that the graph converges

To Do:
    1. Need to track if the dressing is added directly in salad bowl and mixed or 
       added to a dressing container, mixed and then added to salad bowl or 
       added to dressing container, added to salad bowl and then mixed or
       added to dressing container, mixed and then added to salad plate
    2. Check if the instances is zero and if so then we don't have to track them and initialize them to -1
    3. Update the cutting board at the location of update of objects
    4. Need to track the following:
        i) If dressing container has the dressing and if it's needed 
        ii) if the salad bowl has the the dressing, has the ingredients
        iii) if cutting board has the ingredients
        iv) if the plate, has the dressing, has the ingredients
"""

class SaladWorld(object):
    def __init__(self, tomato_instances, cheese_instances, cucumber_instances, lettuce_instances, mix_instances, dressing_bowl_exist):
        
        self.tomato_flag = 0
        self.cheese_flag = 0
        self.cucumber_flag = 0
        self.lettuce_flag = 0
        
        self.map = {'add_pepper_core':'pepper', 'add_vinegar_core':'vinegar', 'add_oil_core':'oil', 'add_salt_core':'salt'}
        
        if tomato_instances[0] !=0:
            self.tomato_cut_update_step = 1./tomato_instances[0]
        else:
            self.tomato_cut_update_step = 0
            
        if tomato_instances[1] != 0:
            self.tomato_place_update_step = 1./tomato_instances[1]
        else:
            self.tomato_place_update_step = 0
        
        if cheese_instances[0] != 0:
            self.cheese_cut_update_step = 1./cheese_instances[0]
        else:
            self.cheese_cut_update_step = 0
        
        if cheese_instances[1] != 0:
            self.cheese_place_update_step = 1./cheese_instances[1]
        else:
            self.cheese_place_update_step = 0
            
        if cucumber_instances[0] != 0 :
            self.cucumber_cut_update_step = 1./cucumber_instances[0]
        else:
            self.cucumber_cut_update_step = 0
            
        if cucumber_instances[1] != 0:
            self.cucumber_peel_update_step = 1./cucumber_instances[1]
        else:
            self.cucumber_peel_update_step = 0
            
        if cucumber_instances[2] != 0:
            self.cucumber_place_update_step = 1./cucumber_instances[2]
        else:
            self.cucumber_place_update_step = 0
            
        if lettuce_instances[0] != 0:
            self.lettuce_cut_update_step = 1./lettuce_instances[0]
        else:
            self.lettuce_cut_update_step = 0
            
        if lettuce_instances[1] != 0:
            self.lettuce_place_update_step = 1./lettuce_instances[1]
        else:
            self.lettuce_place_update_step = 0

        '''
        if mix_instances[0] != 0:
            self.mix_ingredients_update_step = 1./mix_instances[0]
        else:
            self.mix_ingredients_update_step = 0            
        self.mix_ingredients = 0
        
        if mix_instances[1] != 0:
            self.mix_dressing_update_step = 1./mix_instances[1]
        else:
            self.mix_dressing_update_step = 0
        self.mix_dressing = 0
        '''

        self.tomato_cut = 0
        self.tomato_place = 0
        self.cheese_cut = 0
        self.cheese_place = 0
        self.cucumber_peel = 0
        self.cucumber_cut = 0
        self.cucumber_place = 0
        self.lettuce_cut = 0
        self.lettuce_place = 0
        
        self.salad_bowl = set()
        self.salad_bowl_mixed = set()

        self.salad_plate_flag = 0
        self.salad_plate = set()
        self.salad_plate_mixed = set()

        self.dressing_bowl_exist = dressing_bowl_exist
        self.dressing_bowl = set()
        self.dressing_bowl_mixed = set()
          
    def update_step_world(self, action):
        if action == 'serve_salad_onto_plate_core':
            self.salad_plate_flag = 1
            self.salad_plate = self.salad_plate.union(self.salad_bowl)
            self.salad_bowl.clear()
            self.salad_plate_mixed = self.salad_plate_mixed.union(self.salad_bowl_mixed)
            self.salad_bowl_mixed.clear()
            # self.salad_plate += self.salad_bowl
            # self.salad_bowl = 'empty'
        elif action == 'add_dressing_core':
            if self.salad_plate_flag == 1:
                # self.salad_plate += self.dressing_bowl + ' '
                self.salad_plate = self.salad_plate.union(self.dressing_bowl)
                # self.salad_plate_mixed = self.salad_plate_mixed.union(self.dressing_bowl_mixed)
            else:
                # self.salad_bowl += self.dressing_bowl + ' '
                self.salad_bowl = self.salad_bowl.union(self.dressing_bowl)
                # self.salad_bowl_mixed = self.salad_bowl_mixed.union(self.dressing_bowl_mixed)
            # self.dressing_bowl = 'empty'
            self.dressing_bowl.clear()
            self.dressing_bowl_mixed.clear()
        elif action == 'mix_dressing_core':
            # self.mix_dressing += self.mix_dressing_update_step
            self.dressing_bowl_mixed = self.dressing_bowl_mixed.union(self.dressing_bowl)
        elif action == 'mix_ingredients_core':
            # self.mix_ingredients += self.mix_ingredients_update_step
            self.salad_bowl_mixed = self.salad_bowl_mixed.union(self.salad_bowl)
        elif action.find('add') != -1:
            if self.dressing_bowl_exist == 1:
                # self.dressing_bowl += self.map[action] + ' '
                self.dressing_bowl.add(self.map[action])
                if self.map[action] in self.dressing_bowl_mixed:
                    self.dressing_bowl_mixed.remove(self.map[action])
            else:
                # self.salad_bowl += self.map[action] + ' '
                self.salad_bowl.add(self.map[action])
                if self.map[action] in self.salad_bowl_mixed:
                    self.salad_bowl_mixed.remove(self.map[action])
        elif action.find('tomato') != -1:
            if action.find('cut') != -1:
                self.tomato_cut += self.tomato_cut_update_step
            elif action.find('place') != -1:
                self.tomato_place += self.tomato_place_update_step
                if self.tomato_flag == 0:
                    # self.salad_bowl += 'tomato '
                    self.salad_bowl.add('tomato')
                    self.tomato_flag = 1
                if 'tomato' in self.salad_bowl_mixed:
                    self.salad_bowl_mixed.remove('tomato')
        elif action.find('cucumber') != -1:
            if action.find('cut') != -1:
                self.cucumber_cut += self.cucumber_cut_update_step
            elif action.find('peel') != -1:
                self.cucumber_peel += self.cucumber_peel_update_step
            elif action.find('place') != -1:
                self.cucumber_place += self.cucumber_place_update_step
                if self.cucumber_flag == 0:
                    # self.salad_bowl += 'cucumber '
                    self.salad_bowl.add('cucumber')
                    self.cucumber_flag = 1
                if 'cucumber' in self.salad_bowl_mixed:
                    self.salad_bowl_mixed.remove('cucumber')
        elif action.find('lettuce') != -1:
            if action.find('cut') != -1:
                self.lettuce_cut += self.lettuce_cut_update_step
            elif action.find('place') != -1:
                self.lettuce_place += self.lettuce_place_update_step
                if self.lettuce_flag == 0:
                    # self.salad_bowl += 'lettuce '
                    self.salad_bowl.add('lettuce')
                    self.lettuce_flag = 1
                if 'lettuce' in self.salad_bowl_mixed:
                    self.salad_bowl_mixed.remove('lettuce')
        elif action.find('cheese') != -1:
            if action.find('cut') != -1:
                self.cheese_cut += self.cheese_cut_update_step
            elif action.find('place') != -1:
                self.cheese_place += self.cheese_place_update_step
                if self.cheese_flag == 0:
                    # self.salad_bowl += 'cheese '
                    self.salad_bowl.add('cheese')
                    self.cheese_flag = 1
                if 'cheese' in self.salad_bowl_mixed:
                    self.salad_bowl_mixed.remove('cheese')

        # print(self.return_state)  

    def return_state(self):
        state = frozendict({'tomato_cut:': self.tomato_cut, 'tomato_place': self.tomato_place,
                 'cucumber_cut': self.cucumber_cut, 'cucumber_peel': self.cucumber_peel, 'cucumber_place': self.cucumber_place,
                 'cheese_cut': self.cheese_cut, 'cheese_place': self.cheese_place,
                 'lettuce_cut': self.lettuce_cut, 'lettuce_place': self.lettuce_place,
                 'salad_bowl': frozenset(self.salad_bowl), 'salad_bowl_mixed': frozenset(self.salad_bowl_mixed), 'dressing_bowl': frozenset(self.dressing_bowl), 
                 'dressing_bowl_mixed': frozenset(self.dressing_bowl_mixed), 'salad_plate': frozenset(self.salad_plate), 'salad_plate_mixed': frozenset(self.salad_plate_mixed)})
        return state

def testcase1():
    salad = SaladWorld([2, 2], [1, 1], [0, 0, 0], [1, 1], [0, 1], 0)
    salad.update_step_world('cut_tomato_core')
    print(salad.return_state())

    salad.update_step_world('place_tomato_into_bowl_core')
    print(salad.return_state())

    salad.update_step_world('cut_tomato_core')
    print(salad.return_state())

    salad.update_step_world('place_tomato_into_bowl_core')
    print(salad.return_state())

    salad.update_step_world('cut_cheese_core')
    print(salad.return_state())

    salad.update_step_world('place_cheese_into_bowl_core')
    print(salad.return_state())

    salad.update_step_world('cut_lettuce_core')
    print(salad.return_state())

    salad.update_step_world('place_lettuce_into_bowl_core')
    print(salad.return_state())

    salad.update_step_world('add_salt_core')
    print(salad.return_state())

    salad.update_step_world('add_vinegar_core')
    print(salad.return_state())

    salad.update_step_world('add_oil_core')
    print(salad.return_state())

    salad.update_step_world('add_pepper_core')
    print(salad.return_state())

    salad.update_step_world('mix_dressing_core')
    print(salad.return_state())

def get_actions_from_demo(file):
    file_object = open(file, "r")
    actions = file_object.read().splitlines()
    return actions

def run_actions(actions):
    tomato_instances = [0, 0] # Cut, place
    cheese_instances = [0, 0] # Cut, place
    cucumber_instances = [0, 0, 0] # Peel, cut, place
    lettuce_instances = [0, 0] # Cut, place
    mix_instances = [0, 0] # mix ingredients, mix dressing
    dressing_bowl_exists = 0

    for action in actions:
        if action == "cut_tomato_core":
            tomato_instances[0] += 1
        elif action == "place_tomato_into_bowl_core":
            tomato_instances[1] += 1
        elif action == "cut_cheese_core":
            cheese_instances[0] += 1
        elif action == "place_cheese_into_bowl_core":
            cheese_instances[1] += 1
        elif action == "cut_cucumber_core":
            cucumber_instances[0] += 1
        elif action == "peel_cucumber_core":
            cucumber_instances[1] += 1
        elif action == "place_cucumber_into_bowl_core":
            cucumber_instances[2] += 1
        elif action == "cut_lettuce_core":
            lettuce_instances[0] += 1
        elif action == "place_lettuce_into_bowl_core":
            lettuce_instances[1] += 1
        elif action == "mix_ingredients_core":
            mix_instances[0] += 1
        elif action == "mix_dressing_core":
            mix_instances[1] += 1
        elif action == "add_dressing_core":
            dressing_bowl_exists = 1
    salad_world = SaladWorld(tomato_instances, cheese_instances, cucumber_instances, lettuce_instances, mix_instances, dressing_bowl_exists)
    state_action_pairs = [salad_world.return_state()]
    for i in range(len(actions)):
        salad_world.update_step_world(actions[i])
        state_action_pairs.append(actions[i])
        new_state = deepcopy(salad_world.return_state())
        # print(new_state)
        state_action_pairs.append(deepcopy(new_state))
        if i == len(actions) - 1:
            final_state = deepcopy(new_state)
        # print(new_state)
        # print(state_action_pairs)
    # print(state_action_pairs)
    return state_action_pairs, final_state

def check_salad_validity(final_salad):
    return 'lettuce' in final_salad['salad_plate'] and \
        'tomato' in final_salad['salad_plate'] and \
        'cheese' in final_salad['salad_plate'] and \
        'vinegar' in final_salad['salad_plate'] and \
        'oil' in final_salad['salad_plate'] and \
        'salt' in final_salad['salad_plate'] and \
        'pepper' in final_salad['salad_plate'] and \
        'lettuce' in final_salad['mixed'] and \
        'tomato' in final_salad['mixed'] and \
        'cheese' in final_salad['mixed']

def calculate_results_for_demos(demos):
    final_salads = {'invalid': 0}
    avg_length = 0
    for demo in demos:
        demo_file_name = '50_salad_dataset/ann-ts/activityAnnotationsFilteredOrdered/'
        if demo < 10:
            demo_file_name += '0'
        demo_file_name += str(demo) + '-1-activityAnnotation.txt'

        demo_actions = get_actions_from_demo(demo_file_name)

        state_action_pairs, final_state = run_actions(demo_actions)
        final_salad = frozendict({'salad_plate': final_state['salad_plate'], 'mixed': final_state['salad_plate_mixed'], 'cucumber_peel': final_state['cucumber_peel']})
        if check_salad_validity(final_salad):
            if final_salad in final_salads.keys():
                final_salads[final_salad] += 1
            else:
                final_salads[final_salad] = 1
        else:
            final_salads['invalid'] += 1

        avg_length += len(demo_actions)

    avg_length /= float(len(demos))

    return final_salads, avg_length

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

    final_salads = {'invalid': 0}
    for k in demo_stats.keys():
        final_salads[k] = 0

    avg_length = 0
    for actions in actions_list:
        avg_length += len(actions)
        state_action_pairs, final_state = run_actions(actions)
        final_salad = frozendict({'salad_plate': final_state['salad_plate'], 'mixed': final_state['salad_plate_mixed'], 'cucumber_peel': final_state['cucumber_peel']})
        if check_salad_validity(final_salad):
            if final_salad in final_salads.keys():
                final_salads[final_salad] += 1
            else:
                final_salads[final_salad] = 1
        else:
            final_salads['invalid'] += 1
    avg_length /= float(len(actions_list))

    return final_salads, avg_length

def calculate_all_results(demos, approach):
    final_salads_demo, avg_length_demo = calculate_results_for_demos(demos)
    final_salads, avg_length = calculate_results_for_approach(demos, approach, final_salads_demo)

    for k in final_salads.keys():
        if k not in final_salads_demo.keys():
            final_salads_demo[k] = 0

    demo_dist = []
    approach_dist = []
    demo_count = 0
    approach_count = 0
    for k in final_salads_demo.keys():
        approach_count += final_salads[k]
        demo_count += final_salads_demo[k]
        if k != 'invalid':
            approach_dist.append(final_salads[k])
            demo_dist.append(final_salads_demo[k])
    approach_dist.append(final_salads['invalid'])
    demo_dist.append(final_salads_demo['invalid'])

    for i in range(len(approach_dist)):
        approach_dist[i] /= float(approach_count)

    for i in range(len(demo_dist)):
        demo_dist[i] /= float(demo_count)

    # print()
    # print(demo_dist)
    # print(approach_dist)
    print(approach_dist[len(approach_dist) - 1], distance.jensenshannon(demo_dist, approach_dist), avg_length - avg_length_demo)

if __name__=="__main__":
    # actions = get_actions_from_demo('./50_salad_dataset/ann-ts/activityAnnotationsFilteredOrdered/25-1-activityAnnotation.txt')
    # final_state_action_pair, final_state = run_actions(actions)
    # print(final_state)

    in_file = open('demo_list.pkl', 'rb')
    demo_list = pickle.load(in_file)

    for i in range(0, 99):
        if i in [3, 12, 16, 18, 20, 24, 26, 27, 29, 32, 37, 41, 43, 44, 45, 48, 49, 52, 53, 56, 58, 59, 60, 62, 65, 66, 67, 69, 71, 72, 76, 77, 80, 81, 82, 84, 85, 86, 89, 91, 92, 95, 96, 97, 99]:
            print('reduction failed for demo set:', i)
            continue
        final_salads_demo = calculate_all_results(demo_list[i], 'phtn')

    # with open('check_demonstration.txt', 'w') as filehandle:
    #     for state_action in final_state_action_pair:
    #         print(state_action)
            # filehandle.write('%s\n' % str(state_action))

