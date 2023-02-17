#!/usr/bin/env python3

from blessed import Terminal
import json
from term_image.image import *
import random
import webbrowser

from src.conductor import *
from src.calibration import *
from src.loading import *
from src.editor import *
from src.layout import *
from src.results import *

import sys
import platform

__version__ = "1.0.0"

term = Terminal()
turnOff = False

menu = None
loadedMenus = {
	"Titlescreen": None,
	"ChartSelect": None,
	"Options": None
}
loadedGame = None
locales = {}
localeNames = [
	"en",
	"fr",
	"da"
]
selectedLocale = "en"

layouts = {}
layoutNames = []

options = {
	"layout": "qwerty",
	"globalOffset": 0,
	"lang": "en",
	"nerdFont": False,
	"textImages": True,
	"shortTimeFormat": False,
	"displayName": "Unknown",
	"bypassSize": False
}

bottom_txt = open("./assets/bottom.txt")
bottomTextLines = bottom_txt.readlines()

currentLoadedSong = 0

import src.game as game

conduc = Conductor()
chartData = []
scores = {}

# ========================= [UTIL FUNCTIONS] =========================

# adapted from https://stackoverflow.com/questions/410221/natural-relative-days-in-python#5164027
import datetime
def prettydate(d, longFormat = False):
	diff = datetime.datetime.fromtimestamp(time.time()) - d
	output = d.strftime('%d %b %y, %H:%M:%S')
	if longFormat:
		if diff.days < 1:
			if diff.seconds <= 1:
				output = locales[selectedLocale](f"datetime.long.now")
			elif diff.seconds < 60:
				output = locales[selectedLocale](f"datetime.long.secs").format(int(diff.seconds))
			elif diff.seconds < 120:
				output = locales[selectedLocale](f"datetime.long.min1")
			elif diff.seconds < 3600:
				output = locales[selectedLocale](f"datetime.long.min").format(int(diff.seconds/60))
			elif diff.seconds < 7200:
				output = locales[selectedLocale](f"datetime.long.hour1")
			else:
				output = locales[selectedLocale](f"datetime.long.hour").format(int(diff.seconds/3600))
		elif diff.days < 2:
			output = locales[selectedLocale](f"datetime.long.ystd")
		elif diff.days < 30:
			output = locales[selectedLocale](f"datetime.long.day").format(int(diff.days))
	else:
		if diff.days < 1:
			if diff.seconds <= 10:
				output = locales[selectedLocale](f"datetime.short.now")
			elif diff.seconds < 60:
				output = locales[selectedLocale](f"datetime.short.secs").format(int(diff.seconds))
			elif diff.seconds < 3600:
				output = locales[selectedLocale](f"datetime.short.mins").format(int(diff.seconds/60))
			else:
				output = locales[selectedLocale](f"datetime.short.hours").format(int(diff.seconds/3600))
		elif diff.days < 30:
			output = locales[selectedLocale](f"datetime.short.days").format(int(diff.days))
	return output

# =========================  [MENU CLASSES]  =========================

class Credits:
	turnOff = False
	creditsOrSomething = []
	creditsPath = "./assets/credits.json"
	selectedItem = 0
	isViewingProfile = False

	def draw(self):
		maxLength = 0

		for option in self.creditsOrSomething:
			if len(option["role"]) > maxLength:
				maxLength = len(option["role"])
				
		for i in range(len(self.creditsOrSomething)):
			if self.selectedItem == i:
				print_at(0,(i*2)+3,term.reverse + term.bold + "    " + (" "*(maxLength-len(self.creditsOrSomething[i]["role"]))) + self.creditsOrSomething[i]["role"] + " " + term.normal + term.underline + self.creditsOrSomething[i]["name"] + term.normal)
			else:
				print_at(0,(i*2)+3,term.bold + "    " + (" "*(maxLength-len(self.creditsOrSomething[i]["role"]))) + self.creditsOrSomething[i]["role"] + " " + term.normal + self.creditsOrSomething[i]["name"] + term.normal)
		if self.isViewingProfile:
			for i in range(len(self.creditsOrSomething[self.selectedItem]["links"])):
				text = self.creditsOrSomething[self.selectedItem]["links"][i]["label"]
				toPrint = term.link(self.creditsOrSomething[self.selectedItem]["links"][i]["link"], self.creditsOrSomething[self.selectedItem]["links"][i]["label"])
				print_at(term.width - (len(text)+1), i+3, toPrint)
				if options["nerdFont"]:
					print_at(term.width - (len(text)+3), i+3, self.creditsOrSomething[self.selectedItem]["links"][i]["icon"])

	def enter_pressed(self):
		if not self.isViewingProfile:
			self.isViewingProfile = True

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/60, esc_delay=0)

		if val.name == "KEY_ESCAPE":
			if not self.isViewingProfile:
				global menu
				self.turnOff = True
				loadedMenus["Titlescreen"].turnOff = False
				loadedMenus["Titlescreen"].loop()
				menu = "Titlescreen"
				print(term.clear)
			else:
				self.isViewingProfile = False
				print(term.clear)
		
		if val.name == "KEY_DOWN":
			self.selectedItem += 1
			self.selectedItem %= len(self.creditsOrSomething)
		
		if val.name == "KEY_UP":
			self.selectedItem -= 1
			self.selectedItem %= len(self.creditsOrSomething)
		
		if val.name == "KEY_ENTER":
			self.enter_pressed()

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			f = open(self.creditsPath)
			self.creditsOrSomething = json.loads(f.read())
			f.close()
			while not self.turnOff:
				self.deltatime = conduc.update()
				if not too_small(options["bypassSize"]):
					self.draw()
				else:
					text = locales[selectedLocale]("screenTooSmall")
					print_at(int((term.width - len(text))*0.5), int(term.height*0.5), term.reverse + text + term.normal)

				self.handle_input()

				if platform.system() == "Windows":
					check_term_size()

	def __init__(self) -> None:
		pass

# Options menu
class Options:
	turnOff = False
	deltatime = 0
	selectedItem = 0
	menuOptions = [
		{"var": "globalOffset",		"type":"intField",	"displayName": "Global offset (ms)", "isOffset": True, "snap": 0.001},
		{"var": "lang",				"type":"enum", 		"displayName": "Language", "populatedValues": localeNames},
		{"var": "nerdFont",			"type":"bool", 		"displayName": "Enable Nerd Font display"},
		{"var": "textImages",		"type":"bool", 		"displayName": "Use images as thumbnails"},
		{"var": "shortTimeFormat",	"type":"bool", 		"displayName": "Shorten relative time formatting"},
		{"var": "layout", 			"type":"enum", 		"displayName": "Layout", "populatedValues": layoutNames},
		{"var": "displayName", 		"type":"strField",	"displayName": "Local username", "default": "Player"},
		{"var": "bypassSize",		"type":"bool",		"displayName": "Bypass minimal terminal size"},
	]
	enumInteracted = -1
	curEnumValue = -1
	suggestedOffset = 0
	isPickingOffset = False
	goBack = False

	strInteracted = -1
	curInput = ""
	strCursor = 0

	def populate_enum(self):
		self.menuOptions[1]["populatedValues"] = localeNames
		self.menuOptions[5]["populatedValues"] = layoutNames

	def translate(self):
		for optn in self.menuOptions:
			optn["displayName"] = locales[selectedLocale](f"options.{optn['var']}")

	def moveBy(self, x):
		print(term.clear)
		self.selectedItem = (self.selectedItem + x)%len(self.menuOptions)
	
	# --- INTERACT FUNCTIONS ---
	def interactBool(self, boolOption):
		global options
		options[boolOption["var"]] = not options[boolOption["var"]]

	def interactEnum(self, enum, curChoice):
		'''curChoice is an integer.'''
		global options
		global selectedLocale
		options[enum["var"]] = enum["populatedValues"][curChoice]
		if enum["var"] == "lang":
			selectedLocale = enum["populatedValues"][curChoice]
			print(term.clear)
			self.translate()
	
	def interactStr(self, curChoice):
		global options
		global selectedLocale
		self.strInteracted = curChoice
		self.curInput = options[self.menuOptions[curChoice]["var"]]


	# --- END INTERACT FUNC ---

	def saveOptions(self):
		f = open("./options.json", "w")
		f.write(json.dumps(options, indent=4))
		
	def draw(self):
		maxLength = 0

		for option in self.menuOptions:
			if len(option["displayName"]) > maxLength:
				maxLength = len(option["displayName"])

		for i in range(len(self.menuOptions)):
			titleLen = len(self.menuOptions[i]['displayName'])
			leType = self.menuOptions[i]["type"]
			leVar = self.menuOptions[i]["var"]
			#DisplayName
			if self.selectedItem == i and not self.isPickingOffset:
				if int(conduc.currentBeat) % 2 == 1:
					print_at(0,i*2 + 3, term.reverse + f"- {self.menuOptions[i]['displayName']}{' '*(maxLength-titleLen+1)}>" + term.normal)
				else:
					print_at(0,i*2 + 3, term.normal  + f"- {self.menuOptions[i]['displayName']}{' '*(maxLength-titleLen+1)}>" + term.normal)
			else:
				print_at(0,i*2 + 3, term.normal + f" {self.menuOptions[i]['displayName']}{' '*(maxLength-titleLen+1)}  ")
			if leType == "intField":
				if self.selectedItem == i and self.menuOptions[i]["isOffset"]:
					print_at(maxLength + 6, i*2+3, str(options[leVar] * 1000) + (" "*int(term.width*0.2)) + locales[selectedLocale]("options.calibrationTip") + term.clear_eol)
				else:
					print_at(maxLength + 6, i*2+3, str(options[leVar] * 1000) + term.clear_eol)
			if leType == "enum":
				if self.enumInteracted == i:
					print_at(maxLength + 6, i*2+3, term.reverse + "{ " + options[leVar] + " }" +term.normal + (" "*6) + str(self.menuOptions[i]["populatedValues"]) + term.clear_eol)
				else:
					if self.selectedItem == i and self.menuOptions[i]["var"] == "layout":
						print_at(maxLength + 6, i*2+3, "[" + options[leVar] + "] ⌄" + (" "*int(term.width*0.2)) + locales[selectedLocale]("options.layoutTip") + term.clear_eol)
					else:
						print_at(maxLength + 6, i*2+3, "[" + options[leVar] + "] ⌄" + term.clear_eol)
			if leType == "bool":
				if options[leVar] == True:
					print_at(maxLength + 6, i*2+3, "☑")
				else:
					print_at(maxLength + 6, i*2+3, "☐")
			if leType == "strField":
				if self.selectedItem == i:
					if self.strInteracted == i:
						print_at(maxLength + 6, i*2+3, term.underline + self.curInput + term.clear_eol + term.normal)
					else:
						print_at(maxLength + 6, i*2+3, term.reverse + options[leVar] + term.clear_eol + term.normal)
				else:
					print_at(maxLength + 6, i*2+3, term.normal + options[leVar])

		if self.menuOptions[self.selectedItem]["var"] == "layout":
			text = f"┌───{'┬───'*9}┐\n" + "".join(["".join([f"│ {key} " for key in layouts[options["layout"]]][10*i:10*(i+1)]) + f"│\n├───{'┼───'*9}┤\n" for i in range(2)]) + "".join([f"│ {key} " for key in layouts[options["layout"]]][20:30]) + f"│\n└───{'┴───'*9}┘\n"
			print_lines_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2), term.height-10, text)

		if self.isPickingOffset:
			text_offsetConfirm = f"Do you want to use the new following offset: {int(self.suggestedOffset*(10**3))}ms?"
			print_at(int((term.width - len(text_offsetConfirm)) * 0.5), int(term.height*0.5)-1, text_offsetConfirm)
			print_at(int(term.width * 0.4)-3, int(term.height*0.5)+1, term.reverse+"Yes [Y]"+term.normal)
			print_at(int(term.width * 0.6)-3, int(term.height*0.5)+1, term.reverse+"No [N] "+term.normal)

	def enterPressed(self):
		self.populate_enum()
		selectedOption = self.menuOptions[self.selectedItem]
		if selectedOption["type"] == "bool":
			self.interactBool(selectedOption)
		if selectedOption["type"] == "enum":
			self.enumInteracted = self.selectedItem
			self.curEnumValue = selectedOption["populatedValues"].index(options[selectedOption["var"]])
		if selectedOption["type"] == "strField":
			self.interactStr(self.selectedItem)
			

	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
		"""
		val = ''
		val = term.inkey(timeout=1/60, esc_delay=0)
		global options

		if self.strInteracted > -1:
			leVar = self.menuOptions[self.strInteracted]["var"]
			if val.name == "KEY_ENTER":
				if self.curInput == "":
					if options[leVar] == "":
						options[leVar] = self.menuOptions[self.strInteracted]["default"]
					self.strInteracted = -1
				else:
					options[leVar] = self.curInput
					self.strInteracted = -1
				self.curInput = ""
			elif val.name == "KEY_ESCAPE":
				self.strInteracted = -1
				self.curInput = ""
			else:
				self.curInput, self.strCursor = textbox_logic(self.curInput, self.strCursor, val)

		elif self.isPickingOffset:
			if val == "y":
				leVar = self.menuOptions[self.selectedItem]["var"]
				options[leVar] = round(self.suggestedOffset,3)
				self.isPickingOffset = False
				print(term.clear)
			if val == "n":
				self.isPickingOffset = False
				self.suggestedOffset = 0
				print(term.clear)
		else:
			if self.enumInteracted == -1:
				if val.name == "KEY_DOWN" or val == "j":
					self.moveBy(1)
				if val.name == "KEY_UP" or val == "k":
					self.moveBy(-1)
				if (val.name == "KEY_RIGHT" and self.menuOptions[self.selectedItem]["type"] != "intField") or val.name == "KEY_ENTER":
					self.enterPressed()
				if val.name == "KEY_LEFT" and self.menuOptions[self.selectedItem]["type"] == "intField":
					leVar = self.menuOptions[self.selectedItem]["var"]
					options[leVar] -= self.menuOptions[self.selectedItem]["snap"]
				if val.name == "KEY_RIGHT" and self.menuOptions[self.selectedItem]["type"] == "intField":
					leVar = self.menuOptions[self.selectedItem]["var"]
					options[leVar] += self.menuOptions[self.selectedItem]["snap"]
				if val.name == "KEY_ESCAPE":
					global menu
					self.saveOptions()
					self.turnOff = True
					loadedMenus["Titlescreen"].turnOff = False
					loadedMenus["Titlescreen"].loop()
					menu = "Titlescreen"
					print(term.clear)
				if val == "c":
					self.saveOptions()
					self.turnOff = True
					self.goBack = True
					self.selectedItem = 0
					conduc.stop()
					loadedMenus["Calibration"].loc = locales[selectedLocale]
					loadedMenus["Calibration"].turnOff = False
					loadedMenus["Calibration"].startCalibGlobal()
					self.suggestedOffset = loadedMenus["Calibration"].init()
					self.isPickingOffset = True
					loadedMenus["Calibration"].conduc.stop()
					loadedMenus["Calibration"].hitCount = 0
					loadedMenus["Calibration"].hits = []
					loadedMenus["Calibration"].totalOffset = 0
					conduc.startAt(0)
				if val == "l":
					self.saveOptions()
					self.turnOff = True
					self.goBack = True
					self.selectedItem = 4

					loadedMenus["LayoutEditor"].loc = locales[selectedLocale]
					result = False
					error = ""
					customLayout = ["╳" for _ in range(30)]
					if "custom" in layouts:
						customLayout = layouts["custom"]
					while not result:
						loadedMenus["LayoutEditor"].turnOff = False
						result, error = loadedMenus["LayoutEditor"].loop(customLayout)

					

			else:
				if val.name == "KEY_DOWN" or val == "j":
					self.curEnumValue = (self.curEnumValue-1)%len(self.menuOptions[self.enumInteracted]["populatedValues"])
					self.interactEnum(self.menuOptions[self.enumInteracted], self.curEnumValue)
				if val.name == "KEY_UP" or val == "k":
					self.curEnumValue = (self.curEnumValue+1)%len(self.menuOptions[self.enumInteracted]["populatedValues"])
					self.interactEnum(self.menuOptions[self.enumInteracted], self.curEnumValue)
				if val.name == "KEY_ESCAPE" or val.name == "KEY_ENTER":
					self.enumInteracted = -1


	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			self.translate()
			while not self.turnOff:
				self.deltatime = conduc.update()
				if not too_small(options["bypassSize"]):
					self.draw()
				else:
					text = locales[selectedLocale]("screenTooSmall")
					print_at(int((term.width - len(text))*0.5), int(term.height*0.5), term.reverse + text + term.normal)

				self.handle_input()

				if platform.system() == "Windows":
					check_term_size()

		if self.goBack == True:
			self.goBack = False
			self.turnOff = False
			self.loop()

	def __init__(self, boot = True):
		"""
		The base function, where everything happens. Call it to start the loop. It's never gonna stop. (unless you can somehow set `turnOff` to false)
		"""
		if boot:
			self.loop()

# Chart selection menu
class ChartSelect:
	turnOff = False
	chartsize = 0
	selectedItem = 0
	selectedTab = 0
	selectedScore = 0
	scoreScrolledBy = []
	funniSpeen = 0
	goBack = False
	resultsThing = ResultsScreen()

	def draw(self):
		for i in range(len(chartData)):
			if i == self.selectedItem:
				text = chartData[i]["metadata"]["artist"] + " - " + chartData[i]["metadata"]["title"] + " // "
				print_cropped(0, i+1, 20, text, int(conduc.currentBeat), term.reverse)
			else:
				text = chartData[i]["metadata"]["artist"] + " - " + chartData[i]["metadata"]["title"]
				print_cropped(0, i+1, 20, text, 0, term.normal, False)
			print_at(20,i,f"{term.normal}")
		print_column(20, 0, 19, "┃")
		print_column(20, 20, term.height - 22, "┃")
		# Actual chart info display
		if len(chartData) == 0:
			print_at(25,5, locales[selectedLocale]("chartSelect.no_charts"))
		else:
			if chartData[self.selectedItem]["icon"]["img"] != None:
				fileExists = None
				if chartData[self.selectedItem]["icon"]["img"] != "":
					fileExists = print_image(23, 1, 
						"./charts/" + chartData[self.selectedItem]["foldername"] + "/" + chartData[self.selectedItem]["icon"]["img"], 
						int(term.width * 0.2)
					)
				if not fileExists:
					print_at(23, 1, "[NO IMAGE]")
			else:
				if os.path.exists("./charts/" + chartData[self.selectedItem]["foldername"] + "/" + chartData[self.selectedItem]["icon"]["txt"]):
					txt = open("./charts/" + chartData[self.selectedItem]["foldername"] + "/" + chartData[self.selectedItem]["icon"]["txt"])
					print_lines_at(23, 1, txt.read())
				else:
					print_at(23, 1, "[NO ICON]")
			print_column(25 + int(term.width * 0.2), 0, 8, "┃")
			#region metadata
			print_at(27 + int(term.width * 0.2), 2, term.blue 
				+ locales[selectedLocale]("chartSelect.metadata.song") 
				+ term.normal 
				+ ": " 
				+ chartData[self.selectedItem]["metadata"]["title"]
				+ term.clear_eol
			)
			print_at(27 + int(term.width * 0.2), 3, term.blue 
				+ locales[selectedLocale]("chartSelect.metadata.artist") 
				+ term.normal 
				+ ": " 
				+ chartData[self.selectedItem]["metadata"]["artist"]
				+ term.clear_eol
			)
			print_at(27 + int(term.width * 0.2), 5, term.blue 
				+ locales[selectedLocale]("chartSelect.metadata.author") 
				+ term.normal 
				+ ": " 
				+ chartData[self.selectedItem]["metadata"]["author"]
				+ term.clear_eol
			)
			print_at(27 + int(term.width * 0.2), 6, term.blue 
				+ locales[selectedLocale]("chartSelect.difficulty") 
				+ term.normal 
				+ ": " 
				+ str(chartData[self.selectedItem]["difficulty"])
				+ term.clear_eol
			)
			#endregion
			print_at(25 + int(term.width * 0.2), 8, "┠" + ("─"*(term.width - (26 + int(term.width * 0.2)))))
			print_at(28 + int(term.width * 0.2), 8, term.reverse + locales[selectedLocale]("chartSelect.metadata.description") + term.normal)
			print_column(25 + int(term.width * 0.2), 9, 10, "┃")
			print_lines_at(26 + int(term.width * 0.2), 9, chartData[self.selectedItem]["metadata"]["description"])
			print_at(25 + int(term.width * 0.2), 19, "┸" + ("─"*(term.width - (26 + int(term.width * 0.2)))))
			print_at(20, 19, "┠" + ("─"*(4+int(term.width * 0.2))))
			text_auto = locales[selectedLocale]("chartSelect.auto")
			if loadedGame.auto:
				print_at(23, 18, 
					term.reverse + (" "*int((round(term.width*0.2)-len(text_auto))/2)) 
					+ text_auto + (" "*int((int(term.width*0.2)-len(text_auto))/2)) 
					+ term.normal
				)
			else:
				print_at(23, 18, term.normal+(" "*int(term.width*0.2)))

			#Scores!
			maxRenderedScores = min(len(scores[chartData[self.selectedItem]["foldername"]]), term.height-23) 
			offset = max(0, min(self.selectedScore - maxRenderedScores + 1, len(scores[chartData[self.selectedItem]["foldername"]]) - maxRenderedScores))
			for i in range(maxRenderedScores):
				score = scores[chartData[self.selectedItem]["foldername"]][i + offset]
				rank = getRank(score["score"])
				if score["checkPassed"]:
					text_date_format = prettydate(datetime.datetime.fromtimestamp(score["time"]), not options["shortTimeFormat"])
					if i+offset == self.selectedScore:
						color = term.underline
						if self.selectedTab == 1: color = term.reverse

						if score["isOutdated"]:
							print_at(23, 20+i, f"{term.grey}{color}{rank[0]} {score['playername'] if 'playername' in score else 'Unknown'} - {int(score['score'])} ({score['accuracy']}%)     [OUTDATED]" + term.clear_eol + term.normal)
						else:
							print_at(23, 20+i, f"{color}{rank[2]}{rank[0]} {score['playername'] if 'playername' in score else 'Unknown'} - {int(score['score'])} ({score['accuracy']}%)" + term.clear_eol + term.normal)
						print_at(term.width - (len(text_date_format)+1), 20+i, term.reverse + text_date_format + term.normal)
					else:
						if score["isOutdated"]:
							print_at(23, 20+i, f"{term.grey}{rank[0]} {score['playername'] if 'playername' in score else 'Unknown'} - {int(score['score'])} ({score['accuracy']}%)     [OUTDATED]" + term.clear_eol)
						else: 
							print_at(23, 20+i, f"{rank[2]}{rank[0]}{term.normal} {score['playername'] if 'playername' in score else 'Unknown'} - {int(score['score'])} ({score['accuracy']}%)" + term.clear_eol)
						print_at(term.width - (len(text_date_format)+1), 20+i, text_date_format)
				else:
					print_at(25, 20+i, "[INVALID SCORE]")
			if len(scores[chartData[self.selectedItem]["foldername"]]) == 0:
				print_at(35, int((term.height-18)/2)+17, "No scores yet!")
		# Controls
		print_at(1,term.height - 2, 
		f"{term.reverse}[ENTER] {locales[selectedLocale]('chartSelect.controls.play')} {term.normal} "+
		f"{term.reverse}[j/↓] {locales[selectedLocale]('chartSelect.controls.down')} {term.normal} "+
		f"{term.reverse}[k/↑] {locales[selectedLocale]('chartSelect.controls.up')} {term.normal} "+
		f"{term.reverse}[a] {locales[selectedLocale]('chartSelect.controls.auto')} {term.normal} "+
		f"{term.reverse}[e] {locales[selectedLocale]('chartSelect.controls.editor')} {term.normal} "
		)

	def enterPressed(self):
		if self.selectedTab == 0:
			self.turnOff = True
			conduc.stop()
			conduc.song.stop()
			loadedGame.loc = locales[selectedLocale]
			loadedGame.playername = options["displayName"]
			loadedGame.play(chartData[self.selectedItem], options["layout"])
			
			toBeCheckSumd = dict((i,chartData[self.selectedItem][i]) for i in chartData[self.selectedItem] if i != "actualSong")
			checksum = hashlib.sha256(json.dumps(toBeCheckSumd,skipkeys=True,ensure_ascii=False).encode("utf-8")).hexdigest()
			global scores
			scores[chartData[self.selectedItem]["foldername"]] = load_scores(chartData[self.selectedItem]["foldername"], checksum, chartData[self.selectedItem])
			self.goBack = True
			conduc.play()
		else:
			print(term.clear)
			self.resultsThing.resultsData = scores[chartData[self.selectedItem]["foldername"]][self.selectedScore]
			self.resultsThing.setup()
			self.resultsThing.isEnabled = True
		
	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
		"""
		val = ''
		val = term.inkey(timeout=1/60, esc_delay=0)

		if val.name == "KEY_DOWN" or val == "j":
			if self.selectedTab == 0:
				self.selectedItem = (self.selectedItem + 1)%self.chartsize
				conduc.stop()
				conduc.song.stop()
				conduc.loadsong(chartData[self.selectedItem])
				conduc.play()
				print(term.clear)
			else:
				if len(scores[chartData[self.selectedItem]["foldername"]]) != 0:
					self.selectedScore += 1
					self.selectedScore = min(self.selectedScore, len(scores[chartData[self.selectedItem]["foldername"]])-1)
		if val.name == "KEY_UP" or val == "k":
			if self.selectedTab == 0:
				self.selectedItem = (self.selectedItem - 1)%self.chartsize
				conduc.stop()
				conduc.song.stop()
				conduc.loadsong(chartData[self.selectedItem])
				conduc.play()
				print(term.clear)
			else:
				if len(scores[chartData[self.selectedItem]["foldername"]]) != 0:
					self.selectedScore -= 1
					self.selectedScore = max(self.selectedScore, 0)
		if val.name == "KEY_LEFT" or val == "h":
			self.selectedTab = max(self.selectedTab - 1, 0)
		if val.name == "KEY_RIGHT" or val == "l":
			if len(scores[chartData[self.selectedItem]["foldername"]]) > 0:
				self.selectedTab = min(self.selectedTab + 1, 1)
		if val == "a":
			loadedGame.auto = not loadedGame.auto
		if val == "e":
			#load editor
			conduc.stop()
			conduc.song.stop()
			loadedMenus["Editor"].turnOff = False
			loadedMenus["Editor"].options = options
			loadedMenus["Editor"].layout = Game.setupKeys(None, "qwerty")
			loadedMenus["Editor"].loc = locales[selectedLocale]
			loadedMenus["Editor"].mapToEdit = chartData[self.selectedItem]
			loadedMenus["Editor"].localConduc.loadsong(chartData[self.selectedItem])
			loadedMenus["Editor"].mapToEdit.pop("actualSong", None)
			loadedMenus["Editor"].fileLocation = f"./charts/{chartData[self.selectedItem]['foldername']}/data.json"
			loadedMenus["Editor"].loop()
			print(term.clear)
			self.turnOff = True
			self.goBack = True
			conduc.play()

		if val.name == "KEY_ENTER":
			self.enterPressed()

		if val.name == "KEY_ESCAPE":
			self.turnOff = True
			loadedMenus["Titlescreen"].turnOff = False
			loadedMenus["Titlescreen"].loop()
			menu = "Titlescreen"
			print(term.clear)

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = conduc.update()
				if self.resultsThing.isEnabled:
					if not too_small(options["bypassSize"]):
						self.resultsThing.draw()
					else:
						text = locales[selectedLocale]("screenTooSmall")
						print_at(int((term.width - len(text))*0.5), int(term.height*0.5), term.reverse + text + term.normal)
					self.resultsThing.handle_input()

					if self.resultsThing.gameTurnOff:
						self.resultsThing.gameTurnOff = False
						self.resultsThing.isEnabled = False
				else:
					if not too_small(options["bypassSize"]):
						self.draw()
					else:
						text = locales[selectedLocale]("screenTooSmall")
						print_at(int((term.width - len(text))*0.5), int(term.height*0.5), term.reverse + text + term.normal)
					self.handle_input()

				if platform.system() == "Windows":
					check_term_size()
		if self.goBack == True:
			self.goBack = False
			self.turnOff = False
			self.loop()

	def __init__(self, boot = True):
		"""
		The base function, where everything happens. Call it to start the loop. It's never gonna stop. (unless you can somehow set `turnOff` to false)
		"""
		self.chartsize = len(chartData)
		if boot:
			self.loop()

# Title screen
class TitleScreen:
	logo = ""
	turnOff = False
	selectedItem = 0
	menuOptions = [
		"titlescreen.play",
		"titlescreen.edit",
		"titlescreen.options",
		"titlescreen.credits",
		"titlescreen.discord",
		"titlescreen.github",
		"titlescreen.quit",
	]
	curBottomText = 0
	goBack = False
	discordLink = "https://discord.gg/artQgD3Y8V"
	githubLink = "https://github.com/HastagGuigui/shellrhythm"

	def moveBy(self, x):
		self.selectedItem = (self.selectedItem + x)%len(self.menuOptions)

	def enterPressed(self):
		global loadedMenus
		global menu
		if self.selectedItem == 0:
			# Play
			self.turnOff = True
			loadedMenus["ChartSelect"].turnOff = False
			loadedMenus["ChartSelect"].loop()
			menu = "ChartSelect"
			print(term.clear)

		if self.selectedItem == 1:
			# Edit
			conduc.stop()
			conduc.song.stop()
			loadedMenus["Editor"].options = options
			loadedMenus["Editor"].turnOff = False
			loadedMenus["Editor"].layout = Game.setupKeys(None, "qwerty")
			loadedMenus["Editor"].loc = locales[selectedLocale]
			loadedMenus["Editor"].loop()
			print(term.clear)
			print_lines_at(0,1,self.logo,True)
			print_at(int((term.width - len(self.curBottomText)) / 2), len(self.logo.splitlines()) + 2, self.curBottomText)
			global chartData, scores
			chartData, scores = load_charts()
			self.turnOff = True
			self.goBack = True
			conduc.play()

		if self.selectedItem == 2:
			# Options
			self.turnOff = True
			loadedMenus["Options"].turnOff = False
			loadedMenus["Options"].loop()
			menu = "Options"
			print(term.clear)

		if self.selectedItem == 3:
			self.turnOff = True
			loadedMenus["Credits"].turnOff = False
			loadedMenus["Credits"].loop()
			menu = "Credits"
			print(term.clear)
		
		if self.selectedItem == 4:
			webbrowser.open(self.discordLink)
		if self.selectedItem == 5:
			webbrowser.open(self.githubLink)
		
		if self.selectedItem == 6:
			# Quit
			self.turnOff = True
	
	def draw(self):
		print_lines_at(0,1,self.logo,True)
		print_at(int((term.width - len(self.curBottomText)) / 2), len(self.logo.splitlines()) + 2, self.curBottomText)

		for i in range(len(self.menuOptions)):
			text = locales[selectedLocale](self.menuOptions[i])
			if self.selectedItem == i:
				if options["nerdFont"]:
					print_at(0, term.height * 0.5 - len(self.menuOptions) + i*2, f"{term.reverse}   {text} {term.normal}\ue0b0")
				else:
					print_at(0, term.height * 0.5 - len(self.menuOptions) + i*2, f"{term.reverse}   {text} >{term.normal}")
			else:
				print_at(0, term.height * 0.5 - len(self.menuOptions) + i*2, f"  {text}   ")

		text_beat = "○ ○ ○ ○"
		text_beat = text_beat[:int(conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(conduc.currentBeat)%4 * 2) + 1:]

		print_at(0, 0, term.center(f"{text_beat}{term.clear_eol}"))
		if len(chartData) != 0:
			text_songTitle = chartData[currentLoadedSong]["metadata"]["artist"] + " - " + chartData[currentLoadedSong]["metadata"]["title"] + " // "
		else:
			text_songTitle = "[NO SONG PLAYING] // "
		print_cropped(term.width - 31, 0, 30, text_songTitle, int(conduc.currentBeat), term.normal)

		text_copyright = "© #Guigui, 2022-2023"
		text_version = "v"+__version__
		print_at(term.width-(len(text_version) + 1), term.height-3, text_version)
		print_at(term.width-(len(text_copyright) + 1), term.height-2, text_copyright)

	
	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function.)
		"""
		val = ''
		val = term.inkey(timeout=1/60, esc_delay=0)

		if val.name == "KEY_LEFT" or val == "h":
			self.moveBy(0)
		if val.name == "KEY_DOWN" or val == "j":
			self.moveBy(1)
		if val.name == "KEY_UP" or val == "k":
			self.moveBy(-1)
		if val.name == "KEY_RIGHT" or val == "l":
			self.moveBy(0)

		if val.name == "KEY_ENTER":
			self.enterPressed()

		if val == "t":
			conduc.metronome = not conduc.metronome

	def loop(self):
		self.curBottomText = bottomTextLines[random.randint(0, len(bottomTextLines)-1)]
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = conduc.update()
				if not too_small(options["bypassSize"]):
					self.draw()
				else:
					text = locales[selectedLocale]("screenTooSmall")
					print_at(int((term.width - len(text))*0.5), int(term.height*0.5), term.reverse + text + term.normal)

				self.handle_input()

				if platform.system() == "Windows":
					check_term_size()
		if self.goBack == True:
			self.goBack = False
			self.turnOff = False
			self.loop()
		# print(term.clear)

	def __init__(self, boot = True):
		"""
		The base function, where everything happens. Call it to start the loop. It's never gonna stop. (unless you can somehow set `turnOff` to false)
		"""
		f = open("./assets/logo.txt", encoding="utf-8")
		self.logo = f.read()
		f.close()

		if boot:
			self.loop()

if __name__ == "__main__":
	chartData, scores = load_charts()
	locales, localeNames = load_locales()
	options, selectedLocale = load_options(options)
	layouts, layoutNames = load_layouts()
	print("Everything loaded successfully!\n-----------------------------------------")
	try:
		if len(chartData) != 0:
			songLoaded = random.randint(0, len(chartData)-1)
			if chartData[songLoaded] != None:
				conduc.loadsong(chartData[songLoaded])
			conduc.play()
		else:
			songLoaded = 0
		menu = "Titlescreen"
		loadedMenus["ChartSelect"] = ChartSelect(False)
		loadedMenus["Titlescreen"] = TitleScreen(False)
		loadedMenus["Options"] = Options(False) # Sixty-sixteen megabytes- by-bytes 
		loadedMenus["Credits"] = Credits() # Funding for this program was made possible by-by-by-by-by-
		loadedMenus["Editor"] = Editor()
		loadedMenus["Calibration"] = Calibration("CalibrationGlobal")
		loadedMenus["LayoutEditor"] = LayoutCreator()

		loadedGame = game.Game()

		loadedMenus["ChartSelect"].selectedItem = songLoaded
		loadedMenus["Options"].populate_enum()

		currentLoadedSong = songLoaded

		loadedMenus[menu].loop()
	except KeyboardInterrupt:
		print('Keyboard Interrupt detected!')
	print(term.move_xy(0,0))
