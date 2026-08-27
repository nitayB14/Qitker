

class reporterObject():
	"""
    Represents output of measurements and details
    
    Attributes:
        - anyonMove : tuple list
            contain list of how the anyon move 
        - finalMatrix : 
            the final matrix
        - totalGates : 
            how many gates the circuit has
        - totalBraids : 
            how many braids the circuit has 
        - shotsNumber : 
            how many shots we apply 
        - fidelity : 
            how close the brading to the pure gates  
        - percentage : 
            Distribution of results
    """

	def __init__(self, anyonMove, totalGates, totalBraids,
			  shotsNumber, fidelity, percentage, finalStateVector):

		self._anyonMove = anyonMove
		self._totalGates = totalGates
		self._totalBraids = totalBraids
		self._shotsNumber = shotsNumber
		self._fidelity = fidelity
		self._percentage = percentage
		self._finalStateVector = finalStateVector


	def getAnyonMove(self):
		return self._anyonMove

	def getTotalGates(self):
		return self._totalGates

	def getFinalStateVector(self):
		return self._finalStateVector

	def getTotalBraids(self):
		return self._totalBraids

	def getShotsNumber(self):
		return self._shotsNumber

	def getFidelity(self):
		return self._fidelity

	def getPercentageOpbject(self):
		return self._percentage

	def getPercentage(self):
		p = ""
		for key, value in sorted(self._percentage.items(), key=lambda item: int(item[0], 2)):
			percentage = (value / self._shotsNumber) * 100
			p = p + (f"{key}: {value} shots  ;  {percentage:.2f}%\n")

		return p




	def report(self, debug=False):
		"""
        returning string with all the information on the measurments

        Args:
            - debug (bool):
                show extended information

        Returns:
            - (string) information
        """
	
		reportStr = ""

		if debug:
			reportStr += "\n[Debug]\n----------------------------------------------\n"
			reportStr += str(self._anyonMove)
			reportStr += str(f"\nFinal state vector: \n{self._finalStateVector}\n")


		reportStr += "\n[Compilation]\n----------------------------------------------\n"
		reportStr += "Total gates:        : " + str(self._totalGates) + '\n'
		reportStr += "Total braids:       : " + str(self._totalBraids) + '\n'
		reportStr += "Shots number:       : " + str(self._shotsNumber) + '\n'
		reportStr += "Fidelity:           : " + str(self._fidelity) + '\n'
		reportStr += "\n\n[Results]\n----------------------------------------------\n"
		reportStr += str(self.getPercentage()) + '\n'
		
		return reportStr


	#return information on measurments
	def __str__(self, debug=False):
		return self.report()


