import os
import hydra
from omegaconf import DictConfig
import pandas as pd
import json


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
        return json_data



@hydra.main(version_base=None, config_path="../../config", config_name="config")
def debug(cfg: DictConfig):
    dataset = COCOSearch18(cfg.dataset)
    print(dataset["TP"])


if __name__ == "__main__":
    debug()
