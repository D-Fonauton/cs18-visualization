import os
import hydra
from omegaconf import DictConfig
import pandas as pd
import json
import numpy as np


class Fixation:
    def __init__(self, jsonfile):
        self.jsonfile = jsonfile

    def __getitem__(self, index):
        return self.jsonfile[index]
    
    def __len__(self):
        return len(self.jsonfile)

    def correct_condition(self, condition: str):
        if condition == "TP":
            return 'present'
        elif condition == "TA":
            return 'absent'
        else:
            return condition


    def image_names(self):
        return np.unique([data["name"] for data in self.jsonfile])
    
    def tasks(self):
        return np.unique([data["task"] for data in self.jsonfile])
    
    def tp_image_names(self):
        return np.unique([data["name"] for data in self.jsonfile if data["condition"] == "present"])
    
    def ta_image_names(self):
        return np.unique([data["name"] for data in self.jsonfile if data["condition"] == "absent"])
    
    def fixations(self, trial, subject=None, task_filters=None, mode='default'):
        condition, task, image_name = trial

        condition = self.correct_condition(condition)
        
        if task_filters is not None:
            if task not in task_filters:
                return None
        if subject is None:
            fixations = [data for data in self.jsonfile if data["condition"] == condition and data["task"] == task and data["name"] == image_name]
        else:
            fixations = [data for data in self.jsonfile if data["condition"] == condition and data["task"] == task and data["name"] == image_name and data["subject"] == subject]
        if fixations:
            if mode == 'default':
            # fixations = fixations[0]
                return [np.transpose([fixation["X"], fixation["Y"], fixation["T"]]) for fixation in fixations]
            elif mode == 'all':
                return fixations
        else: 
            return None
    

    def task_images(self, task):
        return np.unique([data["name"] for data in self.jsonfile if data["task"] == task])
    
    def condition_task_images(self, condition, task):
        condition = self.correct_condition(condition)
        return np.unique([data["name"] for data in self.jsonfile if data["task"] == task and data["condition"] == condition])

    def trials(self):
        return np.unique([[data["condition"], data["task"], data["name"]] for data in self.jsonfile], axis=0)
    

    def filters(self, trials, filter_name, filter_criteria):
        if filter_name == "condition":
            col = 0
        elif filter_name == "task":
            col = 1
        elif filter_name == "name":
            col = 2
        else:
            raise NameError(f"No filter named {filter_name}")
        
        return trials[trials[:, col] == filter_criteria]


class COCOSearch18:
    def __init__(self, cfg_dataset) -> None:
        self.dir = cfg_dataset.dir
        self.conditions = cfg_dataset.conditions
        self.categories = cfg_dataset.categories
        
        self.images = self.load_images()
        self.json = self.load_json(cfg_dataset.json)


    def __getitem__(self, index):
        return self.images[index]


    # return the full path of selected image
    def full_path(self, condition, category, image_name):
        return os.path.join(self.dir, condition, category, image_name)


    # load all images in the category folder
    def load_category_images(self, condition, category):
        category_dir = os.path.join(self.dir, condition, category)
        return [os.path.join(category_dir, f) for f in os.listdir(category_dir) if f.endswith('.jpg')]
    

    # load all COCO-Search18 images
    def load_images(self):
        images = dict()
        for condition in self.conditions:
            images[condition] = dict()
            for category in self.categories:
                images[condition][category] = self.load_category_images(condition, category)
        return images


    def load_json(self, json_paths):
        json_data = []
        for json_path in json_paths:
            with open(os.path.join(self.dir, json_path), 'r') as f:
                json_data.extend(json.load(f))
        return Fixation(json_data)


@hydra.main(version_base=None, config_path="../config", config_name="config")
def debug(cfg: DictConfig):
    dataset = COCOSearch18(cfg.dataset)
    j = dataset.json
    print(dataset["TP"])


if __name__ == "__main__":
    debug()
