from src.termutil import *

inputFrequency = 120

class ResultsScreen:
	resultsData = {}
	ranks = [
		["@", 1000000, term.purple],	# @
		["S",  950000, term.aqua],		# #
		["A",  825000, term.green],		# $
		["B",  700000, term.yellow],	# *
		["C",  600000, term.orange],	# ;
		["D",  500000, term.red],		# /
		["F",       0, term.grey],		# _
	]
	judgementCount = [0,0,0,0,0,0]
	rankIMGFile = []
	rankIMGImages = []
	isEnabled = False
	gameTurnOff = False

	def getRank(self, score):
		for i in range(len(self.ranks)):
			rank = self.ranks[i]
			if score >= rank[1]:
				return [rank[0], i, rank[2]]
		return ["X", -1, term.darkred]

	def setup(self):
		for i in range(len(self.resultsData["judgements"])):
			if self.resultsData["judgements"][i] != {}:
				self.judgementCount[self.resultsData["judgements"][i]["judgement"]] += 1

	def draw(self):
		if self.resultsData != {}:
			rank = self.getRank(self.resultsData["score"])
			print_lines_at(5,3, self.rankIMGImages[rank[1]], False, False, rank[2])
			print_at(16, 4, f"{rank[2]}SCORE{term.normal}: {int(self.resultsData['score'])}")
			print_at(16, 6, f"{rank[2]}ACCURACY{term.normal}: {int(self.resultsData['accuracy'])}%")
			print_at(31, 4, f"{self.ranks[0][2]}Marvelous: {term.on_webpurple}{	self.judgementCount[0]}{term.normal}")
			print_at(31, 5, f"{self.ranks[1][2]}Perfect:   {term.on_cyan4}{		self.judgementCount[1]}{term.normal}")
			print_at(31, 6, f"{self.ranks[2][2]}Epic:      {term.on_darkgreen}{	self.judgementCount[2]}{term.normal}")
			print_at(31, 7, f"{self.ranks[3][2]}Good:      {term.on_yellow4}{	self.judgementCount[3]}{term.normal}")
			print_at(31, 8, f"{self.ranks[4][2]}Eh:        {term.on_goldenrod4}{self.judgementCount[4]}{term.normal}")
			print_at(31, 9, f"{self.ranks[5][2]}Misses:    {term.on_darkred}{	self.judgementCount[5]}{term.normal}")

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/inputFrequency)
		# debug_val(val)

		if val.name == "KEY_ESCAPE":
			self.gameTurnOff = True
		
	def __init__(self) -> None:
		f = open("./assets/ranks.txt")
		self.rankIMGFile = f.readlines()
		f.close()
		for lineIndex in range(0, len(self.rankIMGFile), 10):
			self.rankIMGImages.append("".join(self.rankIMGFile[lineIndex:lineIndex+10]))
		pass
