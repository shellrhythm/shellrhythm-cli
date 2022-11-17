from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
from index import *

class Game:
	localConduc = Conductor()
	chart = {}
	turnOff = False

	def draw(self):
		for note in self.chart["notes"]:
			if note["type"] == "hit_object":
				print_at(40, term.height-2, str(note))
				calc_pos = [int(note["screenpos"][0]*(term.width-10))+5,int(note["screenpos"][1]*(term.width-6))+3]
				print_at(calc_pos[0]-1, calc_pos[1]-1, "*-*")
				print_at(calc_pos[0]-1, calc_pos[1],   "| |")
				print_at(calc_pos[0]-1, calc_pos[1]+1, "*-*")

		print_at(0,0,self.chart["metadata"]["artist"] + " - " + self.chart["metadata"]["title"])

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/60)
		# debug_val(val)

		if val.name == "KEY_ESCAPE":
			sys.exit(0)

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = conduc.update()
				self.draw()

				self.handle_input()

	def play(self, chart = {}):
		print(chart)
		self.chart = chart
		self.localConduc.loadsong(self.chart)
		self.localConduc.song.play()
		self.loop()

	def __init__(self) -> None:
		print("Wow, look, nothing!")

		pass