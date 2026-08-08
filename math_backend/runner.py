from QuantumMath.constant import math_constant
from QuantumMath.HilbertSpace import HilbertSpace

shots = 1024


def getPercentage(items):
    p = ""

    for key, value in sorted(items.items(), key=lambda item: int(item[0], 2)):
        percentage = (value / shots) * 100
        p += f"{key}: {value} shots | {percentage:.2f}%\n"

    return p



def main():
    matrixH = [ -1, -2, 1, 1, -2, 1, 1, 2, -1, 2, 1, 2, 1, 1, 2, 2, 1, -2, 1, 1, -2, -2, -1, -1, -1, -2, -1, 2, 1, 2, -1, -2, 1, 2, 2, 2, 2, 2, 1, 2, 2, -1, 2, 2, 1, 2, -1, -2, -2, -2, 1, -2, -2, 1, 1, -2, -2, 1, 1, 2, -1, 2, 2, -1, 2 ]

    # (((1,2),(3,4)),((5,6),(7,8)))
    hb = HilbertSpace(2)

    for i in matrixH:
        hb.sigma(0, i)
        hb.sigma(1, i)



    results = getPercentage(hb.run_measurements(shots))
    print(results)



main()

