import numpy as np

from .metrics import Metric



class Needleman_Wunsch(Metric):
    def __init__(self, split, cfg, fixations1=None, fixations2=None):
        super().__init__(split, cfg, fixations1, fixations2)


    # 2. String Matching (Needleman-Wunsch Algorithm)
    def similarity(self, match_score=1, gap_cost=-1, mismatch_cost=-1):
        super().similarity()

        seq1 = self.fix2str(self.fixations1)
        seq2 = self.fix2str(self.fixations2)

        len1, len2 = len(seq1), len(seq2)

        max_dp = max(len1, len2)
        min_dp = -max_dp

        dp = np.zeros((len1 + 1, len2 + 1))

        for i in range(len1 + 1):
            dp[i][0] = i * gap_cost
        for j in range(len2 + 1):
            dp[0][j] = j * gap_cost

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                match = dp[i - 1][j - 1] + (match_score if seq1[i - 1] == seq2[j - 1] else mismatch_cost)
                delete = dp[i - 1][j] + gap_cost
                insert = dp[i][j - 1] + gap_cost
                dp[i][j] = max(match, delete, insert)

        return (dp[len1][len2] - min_dp) / (max_dp - min_dp)