if __name__ == "src.results":
	from src.termutil import *
else:
	from termutil import *
import json

inputFrequency = 120

class ResultsScreen:
	resultsData = {}
	ranks = [
		["@", 1000000, term.purple	,term.on_webpurple	],	# @
		["S",  950000, term.aqua	,term.on_cyan4		],	# #
		["A",  825000, term.green	,term.on_darkgreen	],	# $
		["B",  700000, term.yellow	,term.on_yellow4	],	# *
		["C",  600000, term.orange	,term.on_goldenrod4	],	# ;
		["D",  500000, term.red		,term.on_darkred	],	# /
		["F",       0, term.grey						],	# _
	]
	judgementCount = [0,0,0,0,0,0]
	rankIMGFile = []
	rankIMGImages = []
	isEnabled = False
	gameTurnOff = False
	offsets = []
	hitWindows = [0.05, 0.1, 0.2, 0.3, 0.4] #BAD IDEA TO PUT IT HERE, CHANGE IT LATER
	oneRowIsThisMS = 0.05 #so max 18 rows to write everything

	def getRank(self, score):
		for i in range(len(self.ranks)):
			rank = self.ranks[i]
			if score >= rank[1]:
				return [rank[0], i, rank[2]]
		return ["X", -1, term.darkred]

	def setup(self):
		self.judgementCount = [0,0,0,0,0,0]
		for i in range(len(self.resultsData["judgements"])):
			if self.resultsData["judgements"][i] != {}:
				self.judgementCount[self.resultsData["judgements"][i]["judgement"]] += 1
				self.offsets.append(self.resultsData["judgements"][i]["offset"])

	def draw(self):
		if self.resultsData != {}:
			rank = self.getRank(self.resultsData["score"])
			print_lines_at(5,3, self.rankIMGImages[rank[1]], False, False, rank[2])
			print_at(16, 4, f"{rank[2]}SCORE{term.normal}: {int(self.resultsData['score'])}")
			print_at(16, 6, f"{rank[2]}ACCURACY{term.normal}: {int(self.resultsData['accuracy'])}%")
			print_at(31, 4, f"{self.ranks[0][2]}Marvelous: {self.ranks[0][3]}{self.judgementCount[0]}{term.normal}")
			print_at(31, 5, f"{self.ranks[1][2]}Perfect:   {self.ranks[1][3]}{self.judgementCount[1]}{term.normal}")
			print_at(31, 6, f"{self.ranks[2][2]}Epic:      {self.ranks[2][3]}{self.judgementCount[2]}{term.normal}")
			print_at(31, 7, f"{self.ranks[3][2]}Good:      {self.ranks[3][3]}{self.judgementCount[3]}{term.normal}")
			print_at(31, 8, f"{self.ranks[4][2]}Eh:        {self.ranks[4][3]}{self.judgementCount[4]}{term.normal}")
			print_at(31, 9, f"{self.ranks[5][2]}Misses:    {self.ranks[5][3]}{self.judgementCount[5]}{term.normal}")

			print_at(3, 30, f"{self.ranks[0][2]+self.ranks[0][3]}0" + " "*(term.width-10)+ term.normal)
			print_at(3, 20, "+")
			print_at(3, 40, "-")
			for i in range(0, len(self.offsets), 2):
				symbolLookup = [
					["⠀", "⠁", "⠂", "⠄", "⡀"], 
					["⠈", "⠉", "⠊", "⠌", "⡈"],
					["⠐", "⠑", "⠒", "⠔", "⡐"],
					["⠠", "⠡", "⠢", "⠤", "⡠"],
					["⢀", "⢁", "⢂", "⢄", "⣀"]
				]
				var1 = int(self.offsets[i]/self.oneRowIsThisMS) * -1
				var1_rest = ((self.offsets[i]/self.oneRowIsThisMS)%1) * -4
				var1_color = int((var1+1)/2)
				# print_at(5+int(i), 30, str(var1))
				if i+1 < len(self.offsets):
					var2 = int(self.offsets[i+1]/self.oneRowIsThisMS) * -1
					var2_rest = ((self.offsets[i+1]/self.oneRowIsThisMS)%1) * -4
					var2_color = int((var2+1)/2)
					# print_at(5+int(i+1), 30+1, str(var2))
					if var1 == var2:
						print_at(5+int(i/2), 30+var1, self.ranks[var1_color][3]+symbolLookup[int(var2_rest)][int(var1_rest)]+term.normal)
					else:
						print_at(5+int(i/2), 30+var1, self.ranks[var1_color][3]+symbolLookup[0][int(var1_rest)]+term.normal)
						print_at(5+int(i/2), 30+var2, self.ranks[var2_color][3]+symbolLookup[int(var2_rest)][0]+term.normal)
				else:
					print_at(5+int(i/2), 30+var1, self.ranks[var1_color][3]+symbolLookup[0][int(var1_rest)]+term.normal)




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

if __name__ == "__main__":
	results = ResultsScreen()
	f = open("./logs/results.json")
	results.resultsData = json.load(f)
	f.close()

	results.setup()
	print(len(results.offsets))
	with term.fullscreen(), term.cbreak():
		print(term.clear)

		while not results.gameTurnOff:
			results.draw()
			results.handle_input()