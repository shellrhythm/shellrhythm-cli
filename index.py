from blessed import Terminal
import os, sys
import json

term = Terminal()
turnOff = False

menu = None
loadedMenus = {
	"Titlescreen": None,
	"ChartSelect": None,
	"Options": None
}
locales = {}
selectedLocale = "en"

chartData = []

def print_at(x, y, toPrint):
	print(f"{term.move_xy(x=int(x), y=int(y))}" + toPrint)

def print_lines_at(x, y, text, center):
	lines = text.split("\n")
	for i in range(len(lines)):
		if center:
			print_at(x, y + i, term.center(lines[i]))
		else:
			print_at(x, y + i, lines[i])

def print_column(x, y, size, char):
	for i in range(size):
		print_at(x, y + i, char)

def load_locales():
	global locales
	localeFiles = [f.name.split(".", 1)[0] for f in os.scandir("./lang") if f.is_file()]
	for i in range(len(localeFiles)):
		print(f"Loading locale \"{localeFiles[i]}\"... ({i+1}/{len(localeFiles)})")
		f = open("./lang/" + localeFiles[i] + ".json")
		locales[localeFiles[i]] = json.loads(f.read())
		f.close()

def load_charts():
	global chartData
	charts = [f.path[len("./charts\\"):len(f.path)] for f in os.scandir("./charts") if f.is_dir()]
	for i in range(len(charts)):
		f = open("./charts/" + charts[i] + "/data.json")
		chartData.append(json.load(f))
		f.close()

# ========================= [MENU CLASSES] =========================

# Chart selection menu
class ChartSelect:
	selectedItem = 0
	
	def draw(self):
		print_column(20, 0, term.height - 2, "|")
		
	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function.)
		"""
		val = ''
		val = term.inkey(timeout=1/60)
		if not val:
			print_at(0,term.height-2,term.move_up(1))
		elif val.is_sequence:
			print_at(0,term.height-2,"got sequence: {0}.".format((str(val), val.name, val.code)) + term.clear_eol)
		elif val:
			print_at(0,term.height-2,"got {0}.".format(val.capitalize()) + term.clear_eol)

		if val.name == "KEY_LEFT" or val == "h":
			self.moveBy(-1, 0)
		if val.name == "KEY_DOWN" or val == "j":
			self.moveBy(0, 1)
		if val.name == "KEY_UP" or val == "k":
			self.moveBy(0, -1)
		if val.name == "KEY_RIGHT" or val == "l":
			self.moveBy(1, 0)

		if val.name == "KEY_ENTER":
			self.enterPressed()

# Title screen
class TitleScreen:
	logo = ""
	turnOff = False

	selectedItem = 0
	maxItem = 4

	def moveBy(self, x):
		self.selectedItem = (self.selectedItem + x)%self.maxItem

	def enterPressed(self):
		if self.selectedItem == 0:
			# Play
			print(term.clear)

		if self.selectedItem == 1:
			# Edit
			print(term.clear)

		if self.selectedItem == 2:
			# Options
			print(term.clear)
		
		if self.selectedItem == 3:
			# Quit
			self.turnOff = True
			sys.exit(0)
	
	def draw(self):
		text_play = locales[selectedLocale]["titlescreen"]["play"] #python be wack
		text_edit = locales[selectedLocale]["titlescreen"]["edit"] #python be wack
		text_options = locales[selectedLocale]["titlescreen"]["options"] #python be wack
		text_quit = locales[selectedLocale]["titlescreen"]["quit"] #python be wack
		if self.selectedItem == 0:
			print_at(0, term.height * 0.5 - 3, f"{term.reverse}   {text_play} {term.normal}\ue0b0")
		else:
			print_at(0, term.height * 0.5 - 3, f"  {text_play}   ")

		if self.selectedItem == 1:
			print_at(0, term.height * 0.5 - 1, f"{term.reverse}   {text_edit} {term.normal}\ue0b0")
		else:
			print_at(0, term.height * 0.5 - 1, f"  {text_edit}   ")

		if self.selectedItem == 2:
			print_at(0, term.height * 0.5 + 1, f"{term.reverse}   {text_options} {term.normal}\ue0b0")
		else:
			print_at(0, term.height * 0.5 + 1, f"  {text_options}   ")

		if self.selectedItem == 3:
			print_at(0, term.height * 0.5 + 3, f"{term.reverse}   {text_quit} {term.normal}\ue0b0")
		else:
			print_at(0, term.height * 0.5 + 3, f"  {text_quit}   ")

	
	def handle_input(self):
		"""
		This function is called every update cycle to get keyboard input.
		(Note: it is called *after* the `draw()` function.)
		"""
		val = ''
		val = term.inkey(timeout=1/60)
		if not val:
			print_at(0,term.height-2,term.move_up(1))
		elif val.is_sequence:
			print_at(0,term.height-2,"got sequence: {0}.".format((str(val), val.name, val.code)) + term.clear_eol)
		elif val:
			print_at(0,term.height-2,"got {0}.".format(val.capitalize()) + term.clear_eol)

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

	def loop(self):
		with term.fullscreen(), term.cbreak():
			print(term.clear)
			print_lines_at(0,1,self.logo,True)
			while not self.turnOff:
				self.draw()

				self.handle_input()

	def __init__(self):
		"""
		The base function, where everything happens. Call it to start the loop. It's never gonna stop. (unless you can somehow set `turnOff` to false)
		"""
		f = open("./assets/logo.txt", encoding="utf-8")
		self.logo = f.read()
		f.close()

		self.loop()

if __name__ == "__main__":
	load_charts()
	load_locales()
	try:
		print("Everything loaded successfully!\n=====================")
		menu = TitleScreen()
	except KeyboardInterrupt:
		print('Keyboard Interrupt')
		sys.exit(0)