from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
from term_image.image import *
import random

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
localeNames = []
selectedLocale = "en"

options = {
    "layout": "qwerty",
    "globalOffset": 0,
    "lang": "en",
    "nerdFont": False,
    "textImages": True,
    "displayName": "Player"
}

bottom_txt = open("./assets/bottom.txt")
bottomTextLines = bottom_txt.readlines()

currentLoadedSong = 0

def format_time(seconds):
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60

	if hour != 0:
		return "%d:%02d:%02d" % (hour, minutes, seconds)
	else:
		return "%d:%02d" % (minutes, seconds)

class Conductor:
	bpm = 120
	offset = 0
	startTime = 0
	currentTimeSec = 0
	prevTimeSec = 0
	currentBeat = 0
	prevBeat = 0
	song = Song("./assets/clap.wav")
	previewChart = {}
	metronome = False
	metroSound = Song("./assets/clap.wav")
	startTimeNoOffset = 0
	isPaused = False
	pauseStartTime = 0
	skippedTimeWithPause = 0

	def loadsong(self, chart = {}):
		self.bpm = chart["bpm"]
		self.offset = chart["offset"]
		self.song = chart["actualSong"]
		self.previewChart = chart

	def onBeat(self):
		if self.metronome:
			self.metroSound.play()

	def debugSound(self):
		print_at(0, term.height-6, f"beat: {self.currentBeat} | time: {self.currentTimeSec} | start time: {self.startTime}")

	def play(self):
		self.startTimeNoOffset = (time.time_ns() / 10**9)
		self.startTime = self.startTimeNoOffset + self.offset
		self.song.play()

	def pause(self):
		self.bpm = 0
		self.isPaused = True
		self.pauseStartTime = (time.time_ns() / 10**9)
		self.song.pause()
	
	def resume(self):
		self.isPaused = False
		self.bpm = self.previewChart["bpm"]
		self.skippedTimeWithPause = (time.time_ns() / 10**9) - self.pauseStartTime
		self.song.move2position_seconds((time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause))
		self.song.resume()

	def update(self):
		if not self.isPaused and self.bpm > 0:
			self.currentTimeSec = (time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause)
			self.deltatime = self.currentTimeSec - self.prevTimeSec
			self.currentBeat = self.currentTimeSec * (self.bpm/60)
			self.prevTimeSec = self.currentTimeSec

			if int(self.currentBeat) > int(self.prevBeat):
				self.onBeat()

			self.prevBeat = self.currentBeat

			return self.deltatime
		else:
			self.skippedTimeWithPause = (time.time_ns() / 10**9) - self.pauseStartTime
			return 1/60

	def stop(self):
		# self.song.pause()
		self.song.stop()

	def getLength(self):
		return self.song._length_seconds
	
	def setOffset(self, newOffset):
		self.offset = newOffset
		self.startTime = self.startTimeNoOffset + self.offset


	def __init__(self) -> None:
		pass

import game

conduc = Conductor()
chartData = []

# ========================= [UTIL FONCTIONS] =========================

#region [Util Functions]
def print_at(x, y, toPrint):
	print(f"{term.move_xy(x=int(x), y=int(y))}" + toPrint)

def debug_val(val):
		if not val:
			print_at(0,term.height-2,term.move_up(1))
		elif val.is_sequence:
			print_at(0,term.height-2,"got sequence: {0}.".format((str(val), val.name, val.code)) + term.clear_eol)
		elif val:
			print_at(0,term.height-2,"got {0}.".format(val.capitalize()) + term.clear_eol)

def print_lines_at(x, y, text, center = False, eol = False):
	lines = text.split("\n")
	for i in range(len(lines)):
		if center:
			print_at(x, y + i, term.center(lines[i]))
		else:
			if eol:
				print_at(x, y + i, lines[i] + term.clear_eol)
			else:
				print_at(x, y + i, lines[i])

def print_image(x,y,imagePath,scale):
	image = from_file(imagePath, width=scale)
	print_lines_at(x, y, str(image))
	
def print_column(x, y, size, char):
	for i in range(size):
		print_at(x, y + i, char)

def print_cropped(x, y, maxsize, text, offset, color, isWrapAround = True):
	if isWrapAround:
		print_at(x, y, color + (text*3)[(offset%len(text))+len(text):maxsize+(offset%len(text))+len(text)] + term.normal)
	else:
		actualText = text[offset%len(text):maxsize+(offset%len(text))]
		print_at(x, y, color + actualText + term.normal + (" "*(maxsize - len(actualText))))
		
def load_options():
	if os.path.exists("./options.json"):
		global options
		global selectedLocale
		f = open("./options.json")
		options_string = f.read()
		options = json.loads(options_string)
		f.close()
		print(options)
		selectedLocale = options["lang"]
	else:
		f = open("./options.json", "x")
		f.write(json.dumps(options, indent=4))
		f.close()

def load_locales():
	global locales
	localeFiles = [f.name.split(".", 1)[0] for f in os.scandir("./lang") if f.is_file()]
	for i in range(len(localeFiles)):
		print(f"Loading locale \"{localeFiles[i]}\"... ({i+1}/{len(localeFiles)})")
		f = open("./lang/" + localeFiles[i] + ".json")
		locales[localeFiles[i]] = json.loads(f.read())
		localeNames.append(localeFiles[i])
		f.close()

def check_chart(chart = {}, folder = ""):
	output = {}
	if "formatVersion" not in chart.keys():
		chart["formatVersion"] = 0

	if "approachRate" not in chart.keys():
		chart["approachRate"] = 1

	if chart["formatVersion"] == 0:
		#Format 0 docs:
		#no foldername
		#no icon, defaults to a TXT 
		#author/charter instead of artist/author
		output = {
			"formatVersion": 0,
			"sound": chart["sound"],
			"foldername": folder,
			"icon": {
				"img": None,
				"txt": "icon.txt"
			},
			"bpm": chart["bpm"],
			"offset": chart["offset"],
			"metadata": {
				"title": chart["metadata"]["title"],
				"artist": chart["metadata"]["author"],
				"author": chart["metadata"]["charter"],
				"description": chart["metadata"]["description"]
			},
			"difficulty": 0,
			"approachRate": 1,
			"notes": chart["notes"]
		}
	else:
		output = chart

	# fixing errors
	if output["sound"] == "" or output["sound"] == None:
		print("[WARN] " + folder + " has no song!")
	
	if output["foldername"] != folder: output["foldername"] = folder

	return output

def load_charts():
	global chartData
	charts = [f.path[len("./charts\\"):len(f.path)] for f in os.scandir("./charts") if f.is_dir()]
	for i in range(len(charts)):
		print(f"Loading chart \"{charts[i]}\"... ({i+1}/{len(charts)})")
		f = open("./charts/" + charts[i] + "/data.json").read()
		jsonThing = json.loads(f)
		jsonThing = check_chart(jsonThing, charts[i])
		jsonThing["actualSong"] = Song("./charts/" + charts[i] + "/" + jsonThing["sound"])
		chartData.append(jsonThing)

	print("All charts loaded successfully!")

#endregion

# ========================= [MENU CLASSES] =========================

# Options menu
class Options:
	turnOff = False
	deltatime = 0
	selectedItem = 0
	maxItem = 4
	menuOptions = [
		{"var": "globalOffset", "type":"intField", "displayName": "Global offset (ms)"},
		{"var": "lang", "type":"enum", "displayName": "Language", "populatedValues": localeNames},
		{"var": "nerdFont", "type":"bool", "displayName": "Enable Nerd Font display"},
		{"var": "textImages", "type":"bool", "displayName": "Use images as thumbnails"}
	]
	enumInteracted = -1
	curEnumValue = -1

	def translate(self):
		for optn in self.menuOptions:
			optn["displayName"] = locales[selectedLocale]["options"][optn["var"]]

	def moveBy(self, x):
		self.selectedItem = (self.selectedItem + x)%self.maxItem
	def interactBool(self, boolOption):
		global options
		options[boolOption["var"]] = not options[boolOption["var"]]
	def interactEnum(self, enum, curChoice):
		'''curChoice is an integer.'''
		global options
		global selectedLocale
		options[enum["var"]] = enum["populatedValues"][curChoice]
		selectedLocale = enum["populatedValues"][curChoice]
		print(term.clear)
		self.translate()

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
			if self.selectedItem == i:
				if int(conduc.currentBeat) % 2 == 1:
					print_at(0,i*2 + 3, term.reverse + f"- {self.menuOptions[i]['displayName']}{' '*(maxLength-titleLen+1)}>" + term.normal)
				else:
					print_at(0,i*2 + 3, term.normal  + f"- {self.menuOptions[i]['displayName']}{' '*(maxLength-titleLen+1)}>" + term.normal)
			else:
				print_at(0,i*2 + 3, term.normal + f" {self.menuOptions[i]['displayName']}{' '*(maxLength-titleLen+1)}  ")
			if leType == "intField":
				print_at(maxLength + 6, i*2+3, str(options[leVar] * 1000))
			if leType == "enum":
				print_at(maxLength + 6, i*2+3, "[" + options[leVar] + "] ⌄")
				print_at(maxLength + 32, 0, str(self.menuOptions[i]["populatedValues"]))
			if leType == "bool":
				if options[leVar] == True:
					print_at(maxLength + 6, i*2+3, "☑")
				else:
					print_at(maxLength + 6, i*2+3, "☐")

	def enterPressed(self):
		selectedOption = self.menuOptions[self.selectedItem]
		if selectedOption["type"] == "bool":
			self.interactBool(selectedOption)
		if selectedOption["type"] == "enum":
			self.enumInteracted = self.selectedItem
			self.curEnumValue = selectedOption["populatedValues"].index(options[selectedOption["var"]])

	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
		"""
		val = ''
		val = term.inkey(timeout=1/60)
		# debug_val(val)

		if self.enumInteracted == -1:
			if val.name == "KEY_DOWN" or val == "j":
				self.moveBy(1)
			if val.name == "KEY_UP" or val == "k":
				self.moveBy(-1)
			if val.name == "KEY_RIGHT" or val == "l" or val.name == "KEY_ENTER":
				self.enterPressed()
			if val.name == "KEY_ESCAPE":
				global menu
				self.saveOptions()
				self.turnOff = True
				loadedMenus["Titlescreen"].turnOff = False
				loadedMenus["Titlescreen"].loop()
				menu = "Titlescreen"
				print(term.clear)
		else:
			if val.name == "KEY_DOWN" or val == "j":
				self.curEnumValue = (self.curEnumValue-1)%len(self.menuOptions[self.enumInteracted]["populatedValues"])
				self.interactEnum(self.menuOptions[self.enumInteracted], self.curEnumValue)
			if val.name == "KEY_UP" or val == "k":
				self.curEnumValue = (self.curEnumValue+1)%len(self.menuOptions[self.enumInteracted]["populatedValues"])
				self.interactEnum(self.menuOptions[self.enumInteracted], self.curEnumValue)
			if val.name == "KEY_ESCAPE":
				self.enumInteracted = -1
				

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = conduc.update()
				self.draw()

				self.handle_input()

	def __init__(self, boot = True):
		"""
		The base function, where everything happens. Call it to start the loop. It's never gonna stop. (unless you can somehow set `turnOff` to false)
		"""
		if boot:
			self.loop()


# Chart selection menu
class ChartSelect:
	turnOff = False
	selectedItem = 0
	chartsize = 0
	selectedTab = 0
	funniSpeen = 0
	
	def draw(self):
		for i in range(len(chartData)):
			if self.selectedTab == 0:
				if i == self.selectedItem:
					text = chartData[i]["metadata"]["artist"] + " - " + chartData[i]["metadata"]["title"] + " // "
					print_cropped(0, i+1, 20, text, int(conduc.currentBeat), term.reverse)
				else:
					text = chartData[i]["metadata"]["artist"] + " - " + chartData[i]["metadata"]["title"]
					print_cropped(0, i+1, 20, text, 0, term.normal, False)
			print_at(20,i,f"{term.normal}")
		print_column(20, 0, term.height - 2, "┃")
		# Actual image display
		if self.selectedItem > len(chartData):
			print_at(25,5, locales[selectedLocale]["chartSelect"]["no_charts"])
		else:
			if chartData[self.selectedItem]["icon"]["img"] != None:
				print_image(23, 1, 
					"./charts/" + chartData[self.selectedItem]["foldername"] + "/" + chartData[self.selectedItem]["icon"]["img"], 
					int(term.width * 0.2)
				)
			else:
				txt = open("./charts/" + chartData[self.selectedItem]["foldername"] + "/" + chartData[self.selectedItem]["icon"]["txt"])
				print_lines_at(23, 1, txt.read())
			print_column(25 + int(term.width * 0.2), 0, 8, "┃")
			#region metadata
			print_at(27 + int(term.width * 0.2), 2, term.blue 
				+ locales[selectedLocale]["chartSelect"]["metadata"]["song"] 
				+ term.normal 
				+ ": " 
				+ chartData[self.selectedItem]["metadata"]["title"]
				+ term.clear_eol
			)
			print_at(27 + int(term.width * 0.2), 3, term.blue 
				+ locales[selectedLocale]["chartSelect"]["metadata"]["artist"] 
				+ term.normal 
				+ ": " 
				+ chartData[self.selectedItem]["metadata"]["artist"]
				+ term.clear_eol
			)
			print_at(27 + int(term.width * 0.2), 5, term.blue 
				+ locales[selectedLocale]["chartSelect"]["metadata"]["author"] 
				+ term.normal 
				+ ": " 
				+ chartData[self.selectedItem]["metadata"]["author"]
				+ term.clear_eol
			)
			print_at(27 + int(term.width * 0.2), 6, term.blue 
				+ locales[selectedLocale]["chartSelect"]["difficulty"] 
				+ term.normal 
				+ ": " 
				+ str(chartData[self.selectedItem]["difficulty"])
				+ term.clear_eol
			)
			#endregion
			print_at(25 + int(term.width * 0.2), 8, "┠" + ("─"*(term.width - (26 + int(term.width * 0.2)))))
			print_at(28 + int(term.width * 0.2), 8, locales[selectedLocale]["chartSelect"]["metadata"]["description"])
			print_column(25 + int(term.width * 0.2), 9, 7, "┃")
			print_lines_at(26 + int(term.width * 0.2), 11, chartData[self.selectedItem]["metadata"]["description"])
		# Controls
		print_at(1,term.height - 2, f"{term.reverse}[ENTER] Play level {term.normal} {term.reverse}[J/↓] Scroll down {term.normal} {term.reverse}[K/↑] Scroll up {term.normal} ")

	def enterPressed(self):
		self.turnOff = True
		conduc.stop()
		loadedGame.play(chartData[self.selectedItem], options["layout"])
		print(term.clear)
		self.turnOff = False
		
	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
		"""
		val = ''
		val = term.inkey(timeout=1/60)
		# debug_val(val)

		if val.name == "KEY_LEFT" or val == "h":
			self.selectedTab = max(self.selectedTab - 1, 0)
		if val.name == "KEY_DOWN" or val == "j":
			if self.selectedTab == 0:
				self.selectedItem = (self.selectedItem + 1)%self.chartsize
				conduc.loadsong(chartData[self.selectedItem])
		if val.name == "KEY_UP" or val == "k":
			if self.selectedTab == 0:
				self.selectedItem = (self.selectedItem - 1)%self.chartsize
		if val.name == "KEY_RIGHT" or val == "l":
			self.selectedTab = min(self.selectedTab + 1, 1)

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
				self.draw()

				self.handle_input()

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
	maxItem = 4

	curBottomText = 0

	def moveBy(self, x):
		self.selectedItem = (self.selectedItem + x)%self.maxItem

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
			print(term.clear)

		if self.selectedItem == 2:
			# Options
			self.turnOff = True
			loadedMenus["Options"].turnOff = False
			loadedMenus["Options"].loop()
			menu = "Options"
			print(term.clear)
		
		if self.selectedItem == 3:
			# Quit
			self.turnOff = True
			# sys.exit(0)
	
	def draw(self):
		text_play = locales[selectedLocale]["titlescreen"]["play"] #python be wack
		text_edit = locales[selectedLocale]["titlescreen"]["edit"] #python be wack
		text_options = locales[selectedLocale]["titlescreen"]["options"] #python be wack
		text_quit = locales[selectedLocale]["titlescreen"]["quit"] #python be wack
		if self.selectedItem == 0:
			if options["nerdFont"]:
				print_at(0, term.height * 0.5 - 3, f"{term.reverse}   {text_play} {term.normal}\ue0b0")
			else:
				print_at(0, term.height * 0.5 - 3, f"{term.reverse}   {text_play} >{term.normal}")
		else:
			print_at(0, term.height * 0.5 - 3, f"  {text_play}   ")

		if self.selectedItem == 1:
			if options["nerdFont"]:
				print_at(0, term.height * 0.5 - 1, f"{term.reverse}   {text_edit} {term.normal}\ue0b0")
			else:
				print_at(0, term.height * 0.5 - 1, f"{term.reverse}   {text_edit} >{term.normal}")
		else:
			print_at(0, term.height * 0.5 - 1, f"  {text_edit}   ")

		if self.selectedItem == 2:
			if options["nerdFont"]:
				print_at(0, term.height * 0.5 + 1, f"{term.reverse}   {text_options} {term.normal}\ue0b0")
			else:
				print_at(0, term.height * 0.5 + 1, f"{term.reverse}   {text_options} >{term.normal}")
		else:
			print_at(0, term.height * 0.5 + 1, f"  {text_options}   ")

		if self.selectedItem == 3:
			if options["nerdFont"]:
				print_at(0, term.height * 0.5 + 3, f"{term.reverse}   {text_quit} {term.normal}\ue0b0")
			else:
				print_at(0, term.height * 0.5 + 3, f"{term.reverse}   {text_quit} >{term.normal}")
		else:
			print_at(0, term.height * 0.5 + 3, f"  {text_quit}   ")

		text_beat = "○ ○ ○ ○"
		text_beat = text_beat[:int(conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(conduc.currentBeat)%4 * 2) + 1:]

		print_at(0, 0, term.center(f"{text_beat}{term.clear_eol}"))
		text_songTitle = chartData[currentLoadedSong]["metadata"]["artist"] + " - " + chartData[currentLoadedSong]["metadata"]["title"] + " // "
		print_cropped(term.width - 31, 0, 30, text_songTitle, int(conduc.currentBeat), term.normal)

		print_at(term.width-(len("© #Guigui, 2022") + 1), term.height-2, "© #Guigui, 2022")

	
	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function.)
		"""
		val = ''
		val = term.inkey(timeout=1/60)
		debug_val(val)

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
		# self.curBottomText = bottomTextLines[0]
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			print_lines_at(0,1,self.logo,True)
			print_at(int((term.width - len(self.curBottomText)) / 2), len(self.logo.splitlines()) + 2, self.curBottomText)
			while not self.turnOff:
				self.deltatime = conduc.update()
				self.draw()

				self.handle_input()

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
	load_charts()
	load_locales()
	load_options()
	print("Everything loaded successfully!\n=====================")
	# print("Testing image rendering...")
	# print("KittyImage: " + str(KittyImage.is_supported()))
	# print("ITerm2Image: " + str(ITerm2Image.is_supported()))
	# time.sleep(.5) # This is here to be able to see these values above. Everything goes so fast lmao
	try:
		songLoaded = random.randint(0, len(chartData)-1)
		if chartData[songLoaded] != None:
			conduc.loadsong(chartData[songLoaded])
		conduc.play()
		menu = "Titlescreen"
		loadedMenus["ChartSelect"] = ChartSelect(False)
		loadedMenus["Titlescreen"] = TitleScreen(False)
		loadedMenus["Options"] = Options(False) # Sixty-sixteen megabytes- by-bytes 

		loadedGame = game.Game()

		loadedMenus["ChartSelect"].selectedItem = songLoaded

		currentLoadedSong = songLoaded

		loadedMenus[menu].loop()
	except KeyboardInterrupt:
		print('Keyboard Interrupt detected!')
	print(term.clear)
	print(f"Thanks for playing my game!")
