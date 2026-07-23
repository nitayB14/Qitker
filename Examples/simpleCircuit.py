import sys
from pathlib import Path

from qiskit import result
sys.path.append(str(Path(__file__).resolve().parent.parent))


from qitker import circuit, qubit




def main():
    flipper = circuit()

    coin = qubit(flipper)

    coin.superPosition()

    flipper.execute()

    results = flipper.measure()
    
    print(results.getPercentage())

main()