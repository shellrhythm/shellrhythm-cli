from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
from index import *

term = Terminal()

colors = [
	term.normal,
	term.red,
	term.orange,
	term.yellow,
	term.green,
	term.cyan,
	term.blue,
	term.purple
]

defaultSize = [80, 24]

keys = [
	"a","z","e","r","t","y","u","i","o","p",
	"q","s","d","f","g","h","j","k","l","m",
	"w","x","c","v","b","n",",",";",":","!"
]

# You can either use "setSize" or "scale"
# setSize will use a set terminal size as playfield (By default, 80x24)
# while scale will use the current terminal size with a small offset applied.
playfield_mode = "scale"

class Game:
	localConduc = Conductor()
	chart = {}
	turnOff = False
	score = 0
	judgements = {}
	outOfHere = []

	def draw(self):
		if playfield_mode == "scale":
			print_at(5,2,"-"* (term.width - 9))
			print_at(5,term.height - 3,"-"* (term.width - 9))
			print_column(4,3,term.height-6,"|")
			print_column(term.width-4,3,term.height-6, "|")
		elif playfield_mode == "setSize":
			print_at(5,2,"-"* (defaultSize[0]))
			print_at(5,defaultSize[1] + 3,"-"* (defaultSize[0]))
			print_column(4,3,defaultSize[1],"|")
			print_column(defaultSize[0]+5, 3, defaultSize[1], "|")
		for i in range(len(self.chart["notes"])):
			note = self.chart["notes"][len(self.chart["notes"]) - (i+1)] #It's inverted so that the ones with the lowest remBeats are rendered on top of the others.
			if note["type"] == "hit_object":
				# print_at(40, term.height-2, str(note))
				calc_pos = []
				if playfield_mode == "setSize":
					calc_pos = [
						int(note["screenpos"][0]*(defaultSize[0]))+6,
						int(note["screenpos"][1]*(defaultSize[1]))+4]
				else:
					calc_pos = [
						int(note["screenpos"][0]*(term.width-10))+5,
						int(note["screenpos"][1]*(term.height-8))+3]
				color = colors[note["color"]]
				key = keys[note["key"]]
				remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
				# print_at(50, i, str(remBeats))
				approachedBeats = remBeats * self.chart["approachRate"]
				if approachedBeats > -0.1 and approachedBeats < 4:
					if int(approachedBeats) == 3:
						print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color} ═ ")
						print_at(calc_pos[0]-1, calc_pos[1],   f"{color}   ")
						print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color} ═ ")
					elif int(approachedBeats) == 2:
						print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color} ═╗")
						print_at(calc_pos[0]-1, calc_pos[1],   f"{color}   ")
						print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}╚═ ")
					elif int(approachedBeats) == 1:
						print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color} ═╗")
						print_at(calc_pos[0]-1, calc_pos[1],   f"{color}║ ║")
						print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}╚═ ")
					elif int(approachedBeats) == 0:
						print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color}╔═╗")
						print_at(calc_pos[0]-1, calc_pos[1],   f"{color}║ ║")
						print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}╚═╝")
					print_at(calc_pos[0], calc_pos[1], f"{term.normal}{term.bold}{key.upper()}{term.normal}{color}")
					# print_at(calc_pos[0], calc_pos[1]+1, f"{term.normal}{int(remBeats)}{color}")
				if approachedBeats <= -0.1 and note not in self.outOfHere:
					self.outOfHere.append(note)
					print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1],   f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}   ")


		print_at(0,0,term.normal + self.chart["metadata"]["artist"] + " - " + self.chart["metadata"]["title"])
		# self.localConduc.debugSound()

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/60)
		# debug_val(val)

		if val.name == "KEY_ESCAPE":
			sys.exit(0)
		
		if val in keys:
			debug_val(val)

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = self.localConduc.update()
				self.draw()

				self.handle_input()

	def play(self, chart = {}):
		print(chart)
		conduc.song.stop()
		self.chart = chart
		self.localConduc.loadsong(self.chart)
		self.localConduc.play()
		self.localConduc.song.move2position_seconds(0)
		self.loop()

	def __init__(self) -> None:
		print("Wow, look, nothing!")

		pass

