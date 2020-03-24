# -*- coding: utf-8 -*-
"""
file to parse the dataset files and extract the actions in correct order
"""
from os import listdir
from os.path import isfile, join

dataset_output = "./50_salad_dataset/ann-ts/activityAnnotationsFilteredOrdered"

def build_dataset(dataset_folder, outputToFile):
    action_dataset = []
    for f in listdir(dataset_folder):
        filename = join(dataset_folder, f)
        if isfile(filename):
            action_list = {}
            action_timestamps = []
            action = []
            file = open(join(dataset_folder, f),"r")
            for line in file.readlines():
                word_list = line.split()
                if word_list[-1] == 'cut_and_mix_ingredients' or word_list[-1] == 'prepare_dressing':
                    continue
                elif word_list[-1].find('core') !=-1 :
                    action_list[word_list[0]] = word_list[-1]
                    action_timestamps.append(int(word_list[0]))

        #    print(action_list)
            action_timestamps.sort()
            for t in action_timestamps:
                action.append(action_list[str(t)])
        #    print(action)
            action_dataset.append(action)
            file.close()

            if outputToFile:
                output_file = open(join(dataset_output, f), "w+")
                for single_action in action:
                    output_file.write(single_action + "\n")
                output_file.close()

    return action_dataset

if __name__=="__main__":
    dataset_folder = "./50_salad_dataset/ann-ts/activityAnnotations"
    action_dataset = build_dataset(dataset_folder, True)
    # print(action_dataset)
    print(len(action_dataset))

    ## knowing the actions in the dataset
    unique_actions = set()
    for demonstration in action_dataset:
        for action in demonstration:
            unique_actions.add(action)

    print(unique_actions)

