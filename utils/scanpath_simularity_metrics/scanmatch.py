from difflib import SequenceMatcher

# local
from .metrics import Metric


class Scanmatch(Metric):
    def __init__(self, split, cfg, fixations1=None, fixations2=None):
        super().__init__(split, cfg, fixations1, fixations2)

    
    def similarity(self):
        super().similarity()
        
        seq1 = self.fix2str(self.fixations1)
        seq2 = self.fix2str(self.fixations2)

        matcher = SequenceMatcher(None, seq1, seq2)
        return matcher.ratio()