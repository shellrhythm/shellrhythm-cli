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

hitWindows = [0.05, 0.1, 0.2, 0.35, 0.6]
judgementNames = ["MARV", "PERF", "EPIC", "GOOD", " EH ", "MISS"]
judgementShort = [f"{term.purple}@", f"{term.aqua}#", f"{term.springgreen}$", f"{term.green}*", f"{term.orange};", f"{term.red}/"]
accMultiplier = [1, 0.95, 0.75, 0.50, 0.25, 0]

# You can either use "setSize" or "scale"
# setSize will use a set terminal size as playfield (By default, 80x24)
# while scale will use the current terminal size with a small offset applied.
playfield_mode = "scale"

maxScore = 1000000

class Game:
	localConduc = Conductor()
	beatSound = Song("assets/clap.wav")
	chart = {}
	turnOff = False
	score = 0
	judgements = []
	outOfHere = []
	dontDraw = []
	endTime = 2**32
	accuracy = 100
	auto = False
	missesCount = 0

	def scoreCalc(self):
		filteredJudgementCount = 0
		for i in self.judgements:
			if i != {}:
				filteredJudgementCount += 1
		totalNotes = 0
		for i in self.chart["notes"]:
			if i["type"] == "hit_object":
				totalNotes += 1
		return ((self.accuracy/100) * (maxScore*0.8) + ((1/(self.missesCount+1)) * (maxScore*0.2))) * (filteredJudgementCount/totalNotes)

	def resultsFile(self):
		self.score = self.scoreCalc()
		output = {
			"accuracy": self.accuracy,
			"score": self.score,
			"judgements": self.judgements,
		}
		return output

	def accuracyUpdate(self):
		judges = 1.0
		count = 1
		for i in self.judgements:
			if i != {}:
				judges += accMultiplier[i["judgement"]]
				count += 1
		self.accuracy = round((judges / count) * 100, 2)

	def checkJudgement(self, note, noteNum, notHit = False):
		# print_at(10, 2, "idk man figure it out yourself")
		remTime = ((note["beatpos"][0] * 4 + note["beatpos"][1]) * (60/self.localConduc.bpm)) - self.localConduc.currentTimeSec
		if not self.auto:
			if -0.6 < remTime < 0.6:
				self.beatSound.move2position_seconds(0)
				self.beatSound.play()
				judgement = 5
				for i in range(len(hitWindows)):
					if abs(remTime) <= hitWindows[i]:
						judgement = i
						break
				if noteNum >= len(self.judgements):
					while noteNum >= len(self.judgements):
						self.judgements.append({})
				self.judgements[noteNum] = {
					"offset": remTime,
					"judgement": judgement
				}
				self.accuracyUpdate()
				calc_pos = []
				if playfield_mode == "setSize":
					calc_pos = [
						int(note["screenpos"][0]*(defaultSize[0]))+6,
						int(note["screenpos"][1]*(defaultSize[1]))+4]
				else:
					calc_pos = [
						int(note["screenpos"][0]*(term.width-12))+6,
						int(note["screenpos"][1]*(term.height-9))+4]
				print_at(calc_pos[0], calc_pos[1], judgementShort[judgement])
				print_at(10, 1, judgementNames[judgement])

				if judgement == 5:
					missesCount += 1
				return True
			else:
				if remTime <= -0.6 and notHit:
					judgement = 5
					self.judgements[noteNum] = {
						"offset": remTime,
						"judgement": judgement
					}
					self.accuracyUpdate()
					calc_pos = []
					if playfield_mode == "setSize":
						calc_pos = [
							int(note["screenpos"][0]*(defaultSize[0]))+6,
							int(note["screenpos"][1]*(defaultSize[1]))+4]
					else:
						calc_pos = [
							int(note["screenpos"][0]*(term.width-12))+6,
							int(note["screenpos"][1]*(term.height-9))+4]
					print_at(calc_pos[0], calc_pos[1], judgementShort[judgement])
					print_at(10, 1, judgementNames[judgement])
					missesCount += 1
				return False
		else:
			if remTime <= 0:
				self.beatSound.move2position_seconds(0)
				self.beatSound.play()
				judgement = 0
				for i in range(len(hitWindows)):
					if abs(remTime) <= hitWindows[i]:
						judgement = i
						break
				self.judgements[noteNum] = {
					"offset": remTime,
					"judgement": judgement
				}
				self.accuracyUpdate()
				calc_pos = []
				if playfield_mode == "setSize":
					calc_pos = [
						int(note["screenpos"][0]*(defaultSize[0]))+6,
						int(note["screenpos"][1]*(defaultSize[1]))+4]
				else:
					calc_pos = [
						int(note["screenpos"][0]*(term.width-12))+6,
						int(note["screenpos"][1]*(term.height-9))+4]
				print_at(calc_pos[0], calc_pos[1], judgementShort[judgement])
				print_at(10, 1, judgementNames[judgement])
				return True


	def getSongEndTime(self):
		out = self.localConduc.getLength()
		for note in self.chart["notes"]:
			if note["type"] == "end":
				atBeat = (note["beatpos"][0] * 4 + note["beatpos"][1])
				out = atBeat * (60/self.localConduc.bpm)
				break

		return out

	def draw(self):
		timerText = str(format_time(int(self.localConduc.currentTimeSec))) + " / " + str(format_time(int(self.endTime)))
		print_at(0,0, f"{term.normal}{term.center(timerText)}")
		print_at(0,0,term.normal + self.chart["metadata"]["artist"] + " - " + self.chart["metadata"]["title"])
		print_at(term.width - (len(str(self.accuracy)) + 2), 0, str(self.accuracy) + "%")
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

		
		if len(self.chart["notes"]) >= len(self.judgements):
			while len(self.chart["notes"]) >= len(self.judgements):
				self.judgements.append({})
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
						int(note["screenpos"][0]*(term.width-12))+6,
						int(note["screenpos"][1]*(term.height-9))+4]
				color = colors[note["color"]]
				key = keys[note["key"]]
				remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
				remTime = ((note["beatpos"][0] * 4 + note["beatpos"][1]) * (60/self.localConduc.bpm)) - self.localConduc.currentTimeSec
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
					if len(self.judgements) > len(self.chart["notes"]) - (i+1):
						if self.judgements[len(self.chart["notes"]) - (i+1)] != {}:
							print_at(calc_pos[0], calc_pos[1], f"{term.bold}{judgementShort[self.judgements[len(self.chart['notes']) - (i+1)]['judgement']]}{term.normal}{color}")
						else:
							print_at(calc_pos[0], calc_pos[1], f"{term.normal}{term.bold}{key.upper()}{term.normal}{color}")
					else:
						print_at(calc_pos[0], calc_pos[1], f"{term.normal}{term.bold}{key.upper()}{term.normal}{color}")
					# print_at(calc_pos[0], calc_pos[1]+1, f"{term.normal}{int(remBeats)}{color}")
				if note not in self.dontDraw and ((remTime <= -0.6) or (self.judgements[len(self.chart["notes"]) - (i+1)] != {} and -0.2 > remTime > -0.6 )):
					if note not in self.outOfHere:
						self.outOfHere.append(note)
					if self.judgements[len(self.chart["notes"]) - (i+1)] == {}:
						self.checkJudgement(note, len(self.chart["notes"]) - (i+1), True)
					print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1],   f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}   ")
					self.dontDraw.append(note)


		# self.localConduc.debugSound()

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/60)
		# debug_val(val)

		if val.name == "KEY_ESCAPE":
			raise NotImplementedError("Pause menu missing!")

		if self.localConduc.currentTimeSec > self.endTime:
			f = open("./logs/results.json", "w")
			f.write(json.dumps(self.resultsFile(),indent=4))
			f.close()
			raise NotImplementedError("Results screen missing!")
		
		if val in keys and not self.auto:
			pos = [-1, -1]
			for y in range(len(keys)):
				for x in range(len(keys[y])):
					if keys[y][x] == val:
						pos = [x, y]
			for i in range(len(self.chart["notes"])):
				note = self.chart["notes"][i]
				if note["type"] == "hit_object":
					if note["key"] == pos[0] * 10 + pos[1] and note not in self.outOfHere:
						isHit = self.checkJudgement(note, i)
						if isHit:
							self.outOfHere.append(note)
							break;

		if self.auto:
			for i in range(len(self.chart["notes"])):
				note = self.chart["notes"][i]
				if note["type"] == "hit_object":
					if note not in self.outOfHere:
						isHit = self.checkJudgement(note, i)
						if isHit:
							self.outOfHere.append(note)
							break;

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = self.localConduc.update()
				self.draw()

				self.handle_input()

	def play(self, chart = {}):
		# print(chart)
		conduc.song.stop()
		self.chart = chart
		self.localConduc.loadsong(self.chart)
		self.localConduc.play()
		self.localConduc.song.move2position_seconds(0)
		self.endTime = self.getSongEndTime()
		self.loop()


	def __init__(self) -> None:
		print("Wow, look, nothing!")

		pass

