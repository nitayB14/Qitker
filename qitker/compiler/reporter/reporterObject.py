

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

	def __init__(self, anyonMove, finalMatrix, totalGates, totalBraids,
			  shotsNumber, fidelity, percentage):

		self.anyonMove = anyonMove
		self.finalMatrix = finalMatrix
		self.totalGates = totalGates
		self.totalBraids = totalBraids
		self.shotsNumber = shotsNumber
		self.fidelity = fidelity
		self.percentage = percentage


	def getAnyonMove(self):
		return self.anyonMove

	def getFinalMatrix(self):
		return self.finalMatrix

	def getTotalGates(self):
		return self.totalGates

	def getTotalBraids(self):
		return self.totalBraids

	def getShotsNumber(self):
		return self.shotsNumber

	def getFidelity(self):
		return self.fidelity

	def getPercentage(self):
		return self.percentage





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
			reportStr += "[Debug]\n----------------------------------------------\n\n"
			reportStr += str(self.anyonMove)
			reportStr += f"\nFinal matrix:\n{self.finalMatrix}\n"

		reportStr += "\n[Compilation]\n----------------------------------------------\n"
		reportStr += "Total gates:        : " + str(self.totalGates) + '\n'
		reportStr += "Total braids:       : " + str(self.totalBraids) + '\n'
		reportStr += "Shots number:       : " + str(self.shotsNumber) + '\n'
		reportStr += "Fidelity:           : " + str(self.fidelity) + '\n'
		reportStr += "\n[Results]\n----------------------------------------------\n"
		reportStr += str(self.percentage) + '\n'
		
		return reportStr


	#return information on measurments
	def __str__(self, debug=False):
		return self.report()


