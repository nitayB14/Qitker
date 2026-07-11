import json


class sequenceOperation:
    """
    Loads and provides precomputed braid sequences for quantum gates.

    This class acts as a bridge between high-level gate names and the
    low-level Fibonacci anyon braid operations that implement them.

    Instead of recalculating or searching for braid sequences every time
    a gate is used, the sequences are stored once in a JSON file and loaded
    when the object is initialized.

    This improves performance, keeps the compiler deterministic, and makes
    the braid database easy to update without changing the simulator code.
    """

    def __init__(self):
        with open("Qitker//parser//braid_sequences.json", "r") as f:
            self.sequences= json.load(f)

    
    def getSeq(self, name):
        """
        Returns the precomputed braid sequence for a given gate name.

        Parameters:
            name (str): Gate name stored in braid_sequences.json.

        Returns:
            list: Braid sequence that implements the requested gate.
        """
        return self.sequences[name]["sequence"]



    
