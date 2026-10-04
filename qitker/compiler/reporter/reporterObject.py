

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

	def __init__(self, structure, anyonMove, totalGates, totalBraids,
			  shotsNumber, outputStateFidelity, percentage, finalStateVector,
			  leakageProbability, executionTime, ownerCircuit,):


		self._anyonsNumber = ownerCircuit.getQubitsNumber() * 4
		self._structure = structure
		self._anyonMove = anyonMove
		self._totalGates = totalGates
		self._totalBraids = totalBraids
		self._shotsNumber = shotsNumber
		self._outputStateFidelity = outputStateFidelity
		self._percentage = percentage
		self._finalStateVector = finalStateVector
		self._leakageProbability = leakageProbability
		self._executionTime = executionTime
		self._ownerCircuit = ownerCircuit

	def getNumberOfAnyons(self):
		return self._anyonsNumber

	def getStructure(self):
		return self._structure

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
		return self._outputStateFidelity

	def getPercentageOpbject(self):
		return self._percentage

	def getLeakageProbability(self):
		return self._leakageProbability

	def getExecutionTime(self):
		return self._executionTime

	def getPercentage(self):
		p = ""

		def measurement_sort_key(item):
			key = item[0]

			if key == "LEAKAGE":
				return (1, 0)

			return (0, int(key, 2))

		for key, value in sorted(self._percentage.items(), key=measurement_sort_key,):
			percentage = (value / self._shotsNumber) * 100
			p = p + (
				f"{key}: {value} shots  ;  {percentage:.2f}%\n"
			)

		return p



	def getOutcome(self, rank=1):
		if isinstance(rank, bool) or not isinstance(rank, int):
			raise TypeError("rank must be an integer.")

		if rank < 1:
			raise ValueError("rank must be at least 1.")

		rankedOutcomes = [
			(outcome, shots)
			for outcome, shots in self._percentage.items()
			if outcome != "LEAKAGE"
		]

		rankedOutcomes.sort(
			key=lambda item: (
				-item[1],
				int(item[0], 2),
			)
		)

		if rank > len(rankedOutcomes):
			raise ValueError(
				"rank is greater than the number of measured outcomes."
			)

		return rankedOutcomes[rank - 1][0]


	def selectResult(self, rank=1):
		outcome = self.getOutcome(rank)

		self._ownerCircuit._selectMeasurementOutcome(
			self,
			outcome,
		)

		return outcome

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
			reportStr += str(f"Structure: {self._structure} \n")
			reportStr += str(self._anyonMove)
			reportStr += str(f"\nFinal state vector: \n{self._finalStateVector}\n")


		reportStr += "\n[Compilation]\n----------------------------------------------\n"
		reportStr += "Number of anyons:                     : " + str(self._anyonsNumber) + '\n'
		reportStr += "Total gates:                          : " + str(self._totalGates) + '\n'
		reportStr += "Total braids:                         : " + str(self._totalBraids) + '\n'
		reportStr += "Shots number:                         : " + str(self._shotsNumber) + '\n'
		reportStr += "Output state fidelity:                : " + str(self._outputStateFidelity) + '\n'
		reportStr += (f"Leakage probability:                  : {self._leakageProbability * 100:.4f}%\n")
		reportStr += f"Execution time:                       : {self._executionTime:.2f} s"
		reportStr += "\n\n[Results]\n----------------------------------------------\n"
		reportStr += str(self.getPercentage()) + '\n'
		
		return reportStr


	#return information on measurments
	def __str__(self, debug=False):
		return self.report()


