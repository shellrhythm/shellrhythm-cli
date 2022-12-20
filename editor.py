from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
from index import *
from game import *
import hashlib

term = Terminal()

class Editor:
	turnOff = False
	mapToEdit = {}
	localConduc = Conductor()
	playtest = True
	commandMode = False
	commandString = ""
	needsSaving = False
	fileLocation = ""

	def load_chart(self, chart_name, file = "data"):
		self.fileLocation = f"./charts/{chart_name}/{file}.json"
		f = open(f"./charts/{chart_name}/{file}.json")
		self.mapToEdit = json.load(f) # TODO: And what happens if the file doesn't exist?
		f.close()

	def draw(self):
		print_at(0,term.height-5, "-"*(term.width-1))
		print_at(0,term.height-3, "-"*(term.width-1))
		if self.mapToEdit != {}:
			for i in range(len(self.mapToEdit["notes"])):
				Game.renderNote(None, [Game.calculatePosition(),10], term.cyan, "j", 2, None, 0, print_at)
		else:
			text_nomaploaded = "Wow, such empty."
			print_at(int((term.width - len(text_nomaploaded))*0.5),int(term.height*0.4), text_nomaploaded)
		if self.commandMode:
			print_at(0,term.height-2, ":"+self.commandString+term.clear_eol)

	def run_command(self, command = ""):
		commandSplit = command.split(" ")
		print_at(0,term.height-2, term.clear_eol)
		if commandSplit[0] == "q!" or (commandSplit[0] == "q" and not self.needsSaving):
			sys.exit(0)
		if commandSplit[0] == "w":
			pass
			#save
		if commandSplit[0] == "o":
			if len(commandSplit) == 2:
				self.load_chart(commandSplit[1])
			elif len(commandSplit) == 3:
				self.load_chart(commandSplit[1], commandSplit[2])
			else:
				if len(commandSplit) < 2:
					return False, "Too few arguments."
				else:
					return False, "Too many arguments."
		

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/120)
		if not self.commandMode:
			debug_val(val)
			if val == ":":
				self.commandMode = True
				self.commandString = ""
		else:
			if val.name == "KEY_ESCAPE":
				self.commandMode = False
				self.commandString = ""
			elif val.name == "KEY_ENTER":
				isValid, errorStr = self.run_command(self.commandString)
				if isValid:
					self.commandMode = False
					self.commandString = ""
				else:
					self.commandMode = False
					self.commandString = ""
					print_at(0,term.height-2, term.on_red+errorStr+term.clear_eol+term.normal)

			else:
				if val.name == None:
					self.commandString += str(val)
			

	def loop(self):
		with term.fullscreen(), term.hidden_cursor(), term.raw():
			print(term.clear)
			while not self.turnOff:
				if self.playtest:
					self.deltatime = self.localConduc.update()
				self.draw()
				
				self.handle_input()

	def __init__(self) -> None:
		pass


if __name__ == "__main__":
	editor = Editor()
	loadedMenus["Editor"] = editor
	editor.loop()