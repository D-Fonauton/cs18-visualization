import itertools
import numpy as np


def find_range(durations, frame):
    milestones = np.array(list(itertools.accumulate(durations)))
    milestones -= frame + 1
    return next((i for i, num in enumerate(milestones) if num >= 0), -1)


def reach_milestone(durations, frame):
    milestones = np.array(list(itertools.accumulate(durations)))
    milestones -= frame + 1
    return next((i for i, num in enumerate(milestones) if num == 0), -1)


if __name__ == '__main__':
    print(reach_milestone([122,700,1200,1888],121))