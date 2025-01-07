import numpy as np
from tqdm import tqdm
import math

# local
from utils import Metric, Levenshtein_distance, Needleman_Wunsch, Scanmatch, Multimatch, Scores
from src import Fixation

# subject performances across images
def calculate_similarity_subjects(jsonfile: Fixation, split, cfg, metric_name):
    if not issubclass(metric_name, Metric):
        raise ValueError(f"no metrics named: {metric_name}")
    
    subject_number = cfg.subject_number
    matrix = np.zeros((subject_number, subject_number))
    matrix_count = np.zeros((subject_number, subject_number))

    np.fill_diagonal(matrix, 1)
    np.fill_diagonal(matrix_count, 1)

    metric = metric_name(split, cfg)
    trials = jsonfile.trials()
    for trial in tqdm(trials, desc=f"trials {metric_name.__name__}"):
        fixations = [jsonfile.fixations(trial, subject, cfg.specific_categories) for subject in cfg.subjects]
        for index1 in range(subject_number):
            for index2 in range(index1):

                fixations1 = fixations[index1]
                fixations2 = fixations[index2]

                # fixations1 = jsonfile.fixations(trial, subject1)
                # fixations2 = jsonfile.fixations(trial, subject2)

                if fixations1 is None or fixations2 is None:
                    continue

                metric.set(fixations1, fixations2)
                score = metric.similarity()
                matrix[index2][index1] += score
                matrix[index1][index2] += score

                matrix_count[index1][index2] += 1
                matrix_count[index2][index1] += 1


    matrix /= matrix_count                    
                
    return matrix


# image across subjects
def calculate_similarity_images(jsonfile: Fixation, split, cfg, metric_name):
    if not issubclass(metric_name, Metric):
        raise ValueError(f"no metrics named: {metric_name}")
    
    subject_number = cfg.subject_number

    metric = metric_name(split, cfg)
    trials = jsonfile.trials()
    scores = [Scores() for i in range(math.comb(subject_number, 2))]

    for category, index in zip(cfg.categories, tqdm(range(len(cfg.categories)), desc= "overall progress")):
        this_task_trials = jsonfile.filters(trials, "task", category)
        for trial in tqdm(this_task_trials, desc=f"trials of {category}", leave=False):
            fixations = [jsonfile.fixations(trial, subject) for subject in cfg.subjects]
            comb_rank = 0
            for index1 in range(subject_number):
                for index2 in range(index1 + 1,subject_number):
                    fixations1 = fixations[index1]
                    fixations2 = fixations[index2]

                    # fixations1 = jsonfile.fixations(trial, subject1)
                    # fixations2 = jsonfile.fixations(trial, subject2)

                    if fixations1 is None or fixations2 is None:
                        comb_rank += 1
                        continue

                    metric.set(fixations1, fixations2)
                    scores[comb_rank].append(index, metric.similarity())
                    comb_rank += 1
                    
    return scores
