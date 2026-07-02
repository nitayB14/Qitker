import json


class sequenceOperation:
    def __init__(self):
        with open("parser//braid_sequences.json", "r") as f:
            self.sequences= json.load(f)

    
    def getSeq(self, name):
        return self.sequences[name]["sequence"]



    
