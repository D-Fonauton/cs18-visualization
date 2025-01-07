import numpy as np

class Scores:
    def __init__(self):
        self.category_index = []
        self.similarity_score = []
        
    def append(self, index, score):
        self.category_index.append(index)
        self.similarity_score.append(score)
        
    def concatenate(self, index, score):
        for i in range(len(index)):
            self.category_index.append(index[i])
            self.similarity_score.append(score[i])

    def get_all(self):
        return self.category_index, self.similarity_score

    def get_all_score(self):
        return np.array(self.similarity_score)
    
    def get_category_score(self, index):
        category_index = np.array(self.category_index)
        similarity_score = np.array(self.similarity_score)
        if not index in category_index:
            return []
        else:
            return similarity_score[np.where(category_index == index)[0]]
