from blessed import Terminal
import json
from term_image.image import *
import random
from src.conductor import *
from src.loading import *

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

import src.game as game

conduc = Conductor()
chartData = []

# ========================= [UTIL FONCTIONS] =========================

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
		conduc.song.stop()
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
	
	chartData = load_charts()
	locales, localeNames = load_locales()
	options, selectedLocale = load_options(options)
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
