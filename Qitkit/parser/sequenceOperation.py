import json


class sequenceOperation:
    def __init__(self):
        with open("parser//braid_sequences.json", "r") as f:
            self.sequences= json.load(f)


    def H_seq(self):
        return self.sequences["H"]["sequence"]
    
    def X_seq(self):
        return self.sequences["X"]["sequence"]

    def Y_seq(self):
        return self.sequences["Y"]["sequence"]

    def Z_seq(self):
        return self.sequences["Z"]["sequence"]

    def S_seq(self):
        return self.sequences["S"]["sequence"]

    def T_seq(self):
        return self.sequences["T"]["sequence"]

    
