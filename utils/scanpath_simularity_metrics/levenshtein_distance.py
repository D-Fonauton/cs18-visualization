from .metrics import Metric
import numpy as np


class Levenshtein_distance(Metric):
    def __init__(self, split, cfg, fixations1=None, fixations2=None):
        super().__init__(split, cfg, fixations1, fixations2)


    # 1. Levenshtein Distance (Edit Distance)
    def similarity(self):
        super().similarity()
        
        seq1 = self.fix2str(self.fixations1)
        seq2 = self.fix2str(self.fixations2)

        len1, len2 = len(seq1), len(seq2)

        max_dp = max(len1, len2)


        dp = np.zeros((len1 + 1, len2 + 1), dtype=int)

        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])


        return (max_dp - dp[len1][len2]) / max_dp
    