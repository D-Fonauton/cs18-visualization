import math
import numpy as np
from scipy.spatial.distance import euclidean

# local
from .metrics import Metric


class Multimatch(Metric):
    def __init__(self, split, cfg, fixations1=None, fixations2=None):
         super().__init__(split, cfg, fixations1, fixations2)

    
    # 4. MultiMatch (Simplified Example)
    def similarity(self):
        super().similarity()
        seq1 = self.fixations1
        seq2 = self.fixations2

        scanpath1 = [[f[0], f[1]] for f in self.fixations1]
        duration1 = [f[2] for f in self.fixations1]

        scanpath2 = [[f[0], f[1]] for f in self.fixations2]
        duration1 = [f[2] for f in self.fixations2]


        if len(seq1) != len(seq2):
            return "MultiMatch requires equal-length sequences (simplified version)"

        shape_similarity = sum(euclidean(seq1[i], seq2[i]) for i in range(len(seq1)))
        direction_similarity = sum(1 for i in range(len(seq1) - 1) if seq1[i + 1] == seq2[i + 1])

        return {
            "Shape Similarity": shape_similarity,
            "Direction Similarity": direction_similarity / (len(seq1) - 1)
        }
    

    def cal_shape(self, scanpath1, scanpath2):
        norm1 = np.linalg.norm(scanpath1, axis=1)
        norm2 = np.linalg.norm(scanpath2, axis=1)
        shape_similarity = 1 - np.mean(np.abs(norm1 - norm2) / (norm1 + norm2 + 1e-6))
        return shape_similarity


    def cal_length(self, scanpath1, scanpath2):
        length1 = sum(euclidean(scanpath1[i], scanpath1[i + 1]) for i in range(len(scanpath1) - 1))
        length2 = sum(euclidean(scanpath2[i], scanpath2[i + 1]) for i in range(len(scanpath2) - 1))
        length_similarity = 1 - abs(length1 - length2) / (length1 + length2 + 1e-6)
        return length_similarity


    def cal_direction(self, scanpath1, scanpath2):
        def calculate_angles(scanpath):
            return [np.arctan2(scanpath[i + 1][1] - scanpath[i][1], scanpath[i + 1][0] - scanpath[i][0]) for i in range(len(scanpath) - 1)]

        angles1 = calculate_angles(scanpath1)
        angles2 = calculate_angles(scanpath2)
        direction_similarity = 1 - np.mean(np.abs(np.array(angles1) - np.array(angles2)) / np.pi)
        return direction_similarity
    

    def cal_position(self, scanpath1, scanpath2):
        centroid1 = np.mean(scanpath1, axis=0)
        centroid2 = np.mean(scanpath2, axis=0)
        max_distance = np.max([np.linalg.norm(p) for p in scanpath1 + scanpath2])
        position_similarity = 1 - euclidean(centroid1, centroid2) / (max_distance + 1e-6)
        return position_similarity


    def cal_duration(self, duration1, duration2):
        return 1 - np.mean(np.abs(duration1 - duration2) / (duration1 + duration2 + 1e-6))

