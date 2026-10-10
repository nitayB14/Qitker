"""Measurement results and execution reports."""


class reporterObject():
	"""
	Store measurement counts and details of a circuit execution.

	Attributes:
		_anyonsNumber (int): Number of anyons in the circuit.
		_structure: fusion-tree structure.
		_anyonMove (str): Formatted physical operation history.
		_totalGates (int): Recorded gates, excluding barriers.
		_totalBraids (int): Number of braids used.
		_shotsNumber (int): Number of measurement shots.
		_outputStateFidelity (str): Fidelity formatted as a percentage.
		_percentage (dict[str, int]): Outcome shot counts, possibly including LEAKAGE.
		_finalStateVector: Physical state vector before measurement filtering.
		_leakageProbability (float): Probability of leakage.
		_executionTime (float): Execution and measurement time in seconds.
		_ownerCircuit: Circuit that produced this report.
	"""

	def __init__(self, structure, anyonMove, totalGates, totalBraids,
			  shotsNumber, outputStateFidelity, percentage, finalStateVector,
			  leakageProbability, executionTime, ownerCircuit,):
		"""Store the measurement results and their execution details."""


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
		"""Return the number of anyons."""
		return self._anyonsNumber

	def getStructure(self):
		"""Return the final fusion-tree structure."""
		return self._structure

	def getAnyonMove(self):
		"""Return the formatted physical operation history."""
		return self._anyonMove

	def getTotalGates(self):
		"""Return the number of recorded gates, excluding barriers."""
		return self._totalGates

	def getFinalStateVector(self):
		"""Return the physical state vector."""
		return self._finalStateVector

	def getTotalBraids(self):
		"""Return the number of braids used."""
		return self._totalBraids

	def getShotsNumber(self):
		"""Return the number of measurement shots."""
		return self._shotsNumber

	def getFidelity(self):
		"""Return the output-state fidelity as a percentage string."""
		return self._outputStateFidelity

	def getPercentageOpbject(self):
		"""Return the outcome-to-shot-count dictionary."""
		return self._percentage

	def getLeakageProbability(self):
		"""Return the probability of leakage."""
		return self._leakageProbability

	def getExecutionTime(self):
		"""Return the execution and measurement time in seconds."""
		return self._executionTime

	def getPercentage(self):
		"""Format shot counts and percentages, with LEAKAGE last."""
		p = ""

		def measurement_sort_key(item):
			"""Sort bitstrings numerically and place LEAKAGE last."""
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
		"""Return the ranked non-leakage bitstring without selecting it.

		Rank 1 is the most frequent outcome; ties use binary order.
		Raises TypeError for a non-integer rank and ValueError for an
		out-of-range rank.
		"""
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
		"""Select a ranked outcome for the circuit and return its bitstring.

		The report must still be the circuit's latest measurement result.
		"""
		outcome = self.getOutcome(rank)

		self._ownerCircuit._selectMeasurementOutcome(
			self,
			outcome,
		)

		return outcome

	def report(self, debug=False):
		"""
		Return a formatted execution and measurement report.

		Args:
			debug (bool): Include the structure, operation history, and state vector.

		Returns:
			str: Formatted report text.
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
		"""Return the standard report; use report(debug=True) for details."""
		return self.report()


