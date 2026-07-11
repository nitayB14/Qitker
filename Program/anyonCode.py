
from qitker import circuit, qubit, export_to



def main():

    party = circuit()
    
    alice = qubit(party, 0)
    alice.superPosition()
    #alice.halfPhase()


    party.execute()
    result = party.measure()



    party.details()
    print(result)



main()
