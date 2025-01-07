from abc import ABC, abstractmethod
from omegaconf import DictConfig


class Metric(ABC):
    def __init__(self, split, cfg: DictConfig, fixations1=None, fixations2=None):
        assert len(split) == 2
        self.width_split_number, self.height_split_number = split
        image_width = cfg.width_pixel
        image_height = cfg.height_pixel
        
        self.patch_width = image_width / self.width_split_number
        self.patch_height = image_height / self.height_split_number
        self.fixations1 = fixations1
        self.fixations2 = fixations2


    @abstractmethod
    def similarity(self):
        self.data_check()


    def data_check(self):
        if self.fixations1 is None or self.fixations2 is None:
            raise ValueError(f"fixations must be assigned before calculation!")


    def set(self, fixation1, fixation2):
        self.fixations1 = fixation1
        self.fixations2 = fixation2


    def fix2str(self, fixations):
        output_str = ''
        for fixation in fixations:
            x, y, _ = fixation
            row_index = x // self.patch_width
            col_index = y // self.patch_height
            output_str += chr(65 + int(col_index * self.height_split_number + row_index))
        return output_str




