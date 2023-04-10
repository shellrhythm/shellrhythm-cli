if __name__ == "src.results":
	from src.termutil import *
else:
	from termutil import *
import json
import datetime

inputFrequency = 120

ranks = [
	["@", 1000000, term.purple	,term.on_webpurple,		term.on_color_rgb(148, 29, 96)	],	# @
	["S",  950000, term.aqua	,term.on_cyan4,			term.on_color_rgb(29, 106, 148)	],	# #
	["A",  825000, term.green	,term.on_darkgreen,		term.on_color_rgb(36, 85, 36)	],	# $
	["B",  700000, term.yellow	,term.on_yellow4,		term.on_color_rgb(112, 110, 22)	],	# *
	["C",  600000, term.orange	,term.on_goldenrod4,	term.on_color_rgb(148, 77, 29)	],	# ;
	["D",  500000, term.red		,term.on_darkred,		term.on_color_rgb(83, 14, 14)	],	# /
	["F",       0, term.grey	,term.on_black,		],	# _
]

def getRank(score):
	for i in range(len(ranks)):
		rank = ranks[i]
		if score >= rank[1]:
			return [rank[0], i, rank[2]]
	return ["X", -1, term.darkred]


def scoreCalc(maxScore, judgements, accuracy, missesCount, chart):
	filteredJudgementCount = 0
	totalNotes = 0
	for i in judgements:
		if i != {}:
			filteredJudgementCount += 1
	for i in chart["notes"]:
		if i["type"] == "hit_object":
			totalNotes += 1
	
	#TO ANYONE CHECKING THIS OUT: Here are the following ways score is calculated

	#Current score version: 1.1

	#1: Acc/100 * 80% of max score + 1/(misses+1) * 20% of max score
	#1.1: Acc/100 * 80% of max score + notes hit / (notes hit + misses) * 20% of max score

	if filteredJudgementCount != 0:
		theAccuracyPart = (accuracy/100) * (maxScore*0.8)
		theFractionForThePointTwo = (filteredJudgementCount/(filteredJudgementCount+missesCount))
		theMissDependent = theFractionForThePointTwo * (maxScore*0.2)
		theJudgementPercent = (filteredJudgementCount/totalNotes)

		calculatedResult = (theAccuracyPart + theMissDependent) * theJudgementPercent
		return calculatedResult
	else:
		return -1

class ResultsScreen:
	resultsData = {}
	judgementCount = [0,0,0,0,0,0]
	rankIMGFile = []
	rankIMGImages = []
	isEnabled = False
	gameTurnOff = False
	offsets = []
	hitWindows = [None] #I did in fact change it later
	oneRowIsThisMS = 0.05 #so max 18 rows to write everything
	centerRow = 24
	debug = False
	grid = Grid(0,0,10,10)
	auto = False

	def setup(self):
		self.judgementCount = [0,0,0,0,0,0]
		self.grid.x = 5
		self.grid.y = self.centerRow - 8
		self.grid.height = 20
		self.offsets.clear()
		for i in range(len(self.resultsData["judgements"])):
			if self.resultsData["judgements"][i] != {}:
				self.judgementCount[self.resultsData["judgements"][i]["judgement"]] += 1
				self.offsets.append(self.resultsData["judgements"][i]["offset"])
				self.grid.pointsToPlot.append(-self.resultsData["judgements"][i]["offset"])
				self.grid.colors.append(ranks[self.resultsData["judgements"][i]["judgement"]][3])
		self.render_accuracy_view()

	def draw_debug_info(self):
		print_at(60, 4, "Scored at date: " + datetime.datetime.fromtimestamp(self.resultsData["time"]).strftime('%d %b %y, %H:%M:%S'))
		print_at(60, 5, "Chart SHA256: " + term.underline + self.resultsData["checksum"][:6] + term.normal + self.resultsData["checksum"][6:])

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
			self.grid.draw(cursorPos)


	def draw(self):
		if self.resultsData != {}:
			print_box(4, 2, term.width-7, term.height-4, term.normal, 0)
			rank = getRank(self.resultsData["score"])
			print_lines_at(5,3, self.rankIMGImages[rank[1]], False, rank[2])
			print_at(16, 4, f"{rank[2]}SCORE{term.normal}: {int(self.resultsData['score'])}")
			print_at(16, 6, f"{rank[2]}ACCURACY{term.normal}: {int(self.resultsData['accuracy'])}%")
			print_at(31, 4, f"{ranks[0][2]}Marvelous: {ranks[0][4]}{self.judgementCount[0]}{term.normal}")
			print_at(31, 5, f"{ranks[1][2]}Perfect:   {ranks[1][4]}{self.judgementCount[1]}{term.normal}")
			print_at(31, 6, f"{ranks[2][2]}Epic:      {ranks[2][4]}{self.judgementCount[2]}{term.normal}")
			print_at(31, 7, f"{ranks[3][2]}Good:      {ranks[3][4]}{self.judgementCount[3]}{term.normal}")
			print_at(31, 8, f"{ranks[4][2]}Eh:        {ranks[4][4]}{self.judgementCount[4]}{term.normal}")
			print_at(31, 9, f"{ranks[5][2]}Misses:    {ranks[5][4]}{self.judgementCount[5]}{term.normal}")
			if self.auto:
				print_at(16, 8, f"{term.reverse}[AUTO ENABLED]{term.normal}")
			if self.debug:
				self.draw_debug_info()
			self.render_accuracy_view()

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/inputFrequency, esc_delay=0)

		if val.name == "KEY_ESCAPE":
			print(term.clear)
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