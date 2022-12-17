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

	def draw(self):
		print_at(0,term.height-4, "-"*(term.width-1))
		print_at(0,term.height-2, "-"*(term.width-1))
		Game.renderNote(None, [10,10], term.cyan, "j", 2, None, 0, print_at)

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/120)

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
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