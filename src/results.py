if __name__ == "src.results":
	from src.termutil import *
else:
	from termutil import *
import json

inputFrequency = 120

ranks = [
	["@", 1000000, term.purple	,term.on_webpurple	],	# @
	["S",  950000, term.aqua	,term.on_cyan4		],	# #
	["A",  825000, term.green	,term.on_darkgreen	],	# $
	["B",  700000, term.yellow	,term.on_yellow4	],	# *
	["C",  600000, term.orange	,term.on_goldenrod4	],	# ;
	["D",  500000, term.red		,term.on_darkred	],	# /
	["F",       0, term.grey	,term.on_black		],	# _
]

def getRank(score):
	for i in range(len(ranks)):
		rank = ranks[i]
		if score >= rank[1]:
			return [rank[0], i, rank[2]]
	return ["X", -1, term.darkred]

class ResultsScreen:
	resultsData = {}
	judgementCount = [0,0,0,0,0,0]
	rankIMGFile = []
	rankIMGImages = []
	isEnabled = False
	gameTurnOff = False
	offsets = []
	hitWindows = [0.05, 0.1, 0.2, 0.3, 0.4] #BAD IDEA TO PUT IT HERE, CHANGE IT LATER
	oneRowIsThisMS = 0.05 #so max 18 rows to write everything
	centerRow = 24

	def setup(self):
		self.judgementCount = [0,0,0,0,0,0]
		self.offsets.clear()
		for i in range(len(self.resultsData["judgements"])):
			if self.resultsData["judgements"][i] != {}:
				self.judgementCount[self.resultsData["judgements"][i]["judgement"]] += 1
				self.offsets.append(self.resultsData["judgements"][i]["offset"])
		self.render_accuracy_view()

	def render_accuracy_view(self, cursorPos = 0):
		for i in range(5):
			print_at(5, self.centerRow+(i*2)+2, ranks[i+1][3]+" "*(term.width-9)+ term.normal)
			print_at(5, self.centerRow+(i*2)+1, ranks[i+1][3]+" "*(term.width-9)+ term.normal)
			print_at(5, self.centerRow-(i*2)-1, ranks[i+1][3]+" "*(term.width-9)+ term.normal)
			print_at(5, self.centerRow-(i*2)-2, ranks[i+1][3]+" "*(term.width-9)+ term.normal)
		if self.resultsData != {}:
			print_at(3, self.centerRow, f"{ranks[0][2]+ranks[0][3]}0" + " "*(term.width-8)+ term.normal)
			print_at(3, self.centerRow-10, "+")
			print_at(3, self.centerRow+10, "-")
			for i in range(cursorPos, min(len(self.offsets), cursorPos*2 + (term.width-9)), 2):
				symbolLookup = [
					["?", "⠁", "⠂", "⠄", "⡀"], 
					["⠈", "⠉", "⠊", "⠌", "⡈"],
					["⠐", "⠑", "⠒", "⠔", "⡐"],
					["⠠", "⠡", "⠢", "⠤", "⡠"],
					["⢀", "⢁", "⢂", "⢄", "⣀"]
				]
				var1 = int(self.offsets[i]/self.oneRowIsThisMS) * -1
				var1_rest = 4 - (((self.offsets[i]/self.oneRowIsThisMS)%1) * 4)
				var1_color = int((var1+1)/2)
				# print_at(5+int(i), self.centerRow+11, str(var1))
				if i+1 < len(self.offsets):
					var2 = int(self.offsets[i+1]/self.oneRowIsThisMS) * -1
					var2_rest = 4 - (((self.offsets[i+1]/self.oneRowIsThisMS)%1) * 4)
					var2_color = int((var2+1)/2)
					# print_at(5+int(i), self.centerRow-11, str(var2))
					if var1 == var2:
						print_at(5+int(i/2), self.centerRow+var1, ranks[var1_color][3]+symbolLookup[int(var2_rest)][int(var1_rest)]+term.normal)
					else:
						print_at(5+int(i/2), self.centerRow+var1, ranks[var1_color][3]+symbolLookup[0][int(var1_rest)]+term.normal)
						print_at(5+int(i/2), self.centerRow+var2, ranks[var2_color][3]+symbolLookup[int(var2_rest)][0]+term.normal)
				else:
					print_at(5+int(i/2), self.centerRow+var1, ranks[var1_color][3]+symbolLookup[0][int(var1_rest)]+term.normal)


	def draw(self):
		if self.resultsData != {}:
			rank = getRank(self.resultsData["score"])
			print_lines_at(5,3, self.rankIMGImages[rank[1]], False, False, rank[2])
			print_at(16, 4, f"{rank[2]}SCORE{term.normal}: {int(self.resultsData['score'])}")
			print_at(16, 6, f"{rank[2]}ACCURACY{term.normal}: {int(self.resultsData['accuracy'])}%")
			print_at(31, 4, f"{ranks[0][2]}Marvelous: {ranks[0][3]}{self.judgementCount[0]}{term.normal}")
			print_at(31, 5, f"{ranks[1][2]}Perfect:   {ranks[1][3]}{self.judgementCount[1]}{term.normal}")
			print_at(31, 6, f"{ranks[2][2]}Epic:      {ranks[2][3]}{self.judgementCount[2]}{term.normal}")
			print_at(31, 7, f"{ranks[3][2]}Good:      {ranks[3][3]}{self.judgementCount[3]}{term.normal}")
			print_at(31, 8, f"{ranks[4][2]}Eh:        {ranks[4][3]}{self.judgementCount[4]}{term.normal}")
			print_at(31, 9, f"{ranks[5][2]}Misses:    {ranks[5][3]}{self.judgementCount[5]}{term.normal}")

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
	import sys
	results = ResultsScreen()
	f = open("./scores/" + sys.argv[1])
	results.resultsData = json.load(f)
	f.close()

	print(len(results.offsets))
	with term.fullscreen(), term.cbreak(), term.hidden_cursor():
		print(term.clear)
		results.setup()

		while not results.gameTurnOff:
			results.draw()
			results.handle_input()