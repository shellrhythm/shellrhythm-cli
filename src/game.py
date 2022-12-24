from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
# from index import *
import hashlib
if __name__ == "src.game":
	from src.termutil import *
	from src.conductor import *
	from src.results import ResultsScreen
else:
	from termutil import *
	from conductor import *
	from results import ResultsScreen

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

inputFrequency = 200

keys = [
	"a","z","e","r","t","y","u","i","o","p",
	"q","s","d","f","g","h","j","k","l","m",
	"w","x","c","v","b","n",",",";",":","!"
]

hitWindows = [0.05, 0.075, 0.1, 0.15, 0.2]
judgementNames = ["MARV", "PERF", "EPIC", "GOOD", " EH ", "MISS"]
judgementShort = [f"{term.purple}@", f"{term.aqua}#", f"{term.green}$", f"{term.yellow}*", f"{term.orange};", f"{term.red}/"]
accMultiplier = [1, 1, 0.85, 0.75, 0.5, 0]

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
	auto = True
	missesCount = 0
	pauseOption = 0
	resultsScreen = ResultsScreen()

	def setupKeys(self, layout):
		if os.path.exists("./layout/" + layout):
			output = []
			f = open("./layout/" + layout)
			rows = f.readlines()

			for row in range(len(rows)):
				for char in range(10):
					output.append(rows[row][char])

			if self != None:
				global keys
				keys = output
			else:
				return output

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
		global keys
		self.score = self.scoreCalc()
		output = {
			"accuracy": self.accuracy,
			"score": self.score,
			"judgements": self.judgements,
			"checksum": hashlib.sha256(json.dumps(f"{self.chart['notes']}",skipkeys=True,ensure_ascii=False).encode("utf-8")).hexdigest()
			# "keys": keys
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
				self.score = int(self.scoreCalc())
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
					self.missesCount += 1
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
					self.missesCount += 1
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
				self.score = int(self.scoreCalc())
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

	def renderNote(self, atPos, color, key, approachedBeats, notes = {}, i = -1):
		if int(approachedBeats*2) == 7:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═ {term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}   {term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}   {term.normal}")
		elif int(approachedBeats*2) == 6:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}   {term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}   {term.normal}")
		elif int(approachedBeats*2) == 5:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}  ║{term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}   {term.normal}")
		elif int(approachedBeats*2) == 4:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}  ║{term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}  ╝{term.normal}")
		elif int(approachedBeats*2) == 3:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}  ║{term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color} ═╝{term.normal}")
		elif int(approachedBeats*2) == 2:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}  ║{term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}╚═╝{term.normal}")
		elif int(approachedBeats*2) == 1:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color} ═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}║ ║{term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}╚═╝{term.normal}")
		elif int(approachedBeats*2) == 0:
			print_at(atPos[0]-1, atPos[1]-1, f"{term.normal}{color}╔═╗{term.normal}")
			print_at(atPos[0]-1, atPos[1],   f"{term.normal}{color}║ ║{term.normal}")
			print_at(atPos[0]-1, atPos[1]+1, f"{term.normal}{color}╚═╝{term.normal}")
		
		if self is not None:
			if len(self.judgements) > len(notes) - (i+1):
				if self.judgements[len(notes) - (i+1)] != {}:
					print_at(atPos[0], atPos[1], f"{term.bold}{judgementShort[self.judgements[len(self.chart['notes']) - (i+1)]['judgement']]}{term.normal}{color}")
				else:
					print_at(atPos[0], atPos[1], f"{term.normal}{term.bold}{key.upper()}{term.normal}{color}")
			else:
				print_at(atPos[0], atPos[1], f"{term.normal}{term.bold}{key.upper()}{term.normal}{color}")
		else:
			print_at(atPos[0], atPos[1], f"{term.normal}{term.bold}{key.upper()}{term.normal}{color}")

	def calculatePosition(screenPos, x, y, width, height):
		"""
		x: (Int) screen x offset
		y: (Int) screen y offset
		width: (Int) screen width
		height: (Int) screen height
		"""
		return [int(screenPos[0]*width)+x, int(screenPos[1]*height)+y]

	def actualKeysRendering(self, notes):
		# if playfield_mode == "scale":
		# 	print_at(5,2,"-"* (term.width - 9))
		# 	print_at(5,term.height - 3,"-"* (term.width - 9))
		# 	print_column(4,3,term.height-6,"|")
		# 	print_column(term.width-4,3,term.height-6, "|")
		# elif playfield_mode == "setSize":
		# 	print_at(5,2,"-"* (defaultSize[0]))
		# 	print_at(5,defaultSize[1] + 3,"-"* (defaultSize[0]))
		# 	print_column(4,3,defaultSize[1],"|")
		# 	print_column(defaultSize[0]+5, 3, defaultSize[1], "|")
		if len(notes) >= len(self.judgements):
			while len(notes) >= len(self.judgements):
				self.judgements.append({})
		for i in range(len(notes)):
			note = notes[len(notes) - (i+1)] #It's inverted so that the ones with the lowest remBeats are rendered on top of the others.
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
				approachedBeats = (remBeats * self.chart["approachRate"]) + 1
				if approachedBeats > -0.1 and approachedBeats < 4 and note not in self.dontDraw:

					Game.renderNote(self, calc_pos, color, key, approachedBeats, notes, i) # Say it, you didn't expect a call directly to the Game class. Frankly it's the same shit lmao

					# print_at(calc_pos[0], calc_pos[1]+1, f"{term.normal}{int(remBeats)}{color}")
				if note not in self.dontDraw and ((remTime <= -0.6) or (self.judgements[len(notes) - (i+1)] != {} and -0.2 > remTime > -0.6 )):
					if note not in self.outOfHere:
						self.outOfHere.append(note)
					if self.judgements[len(notes) - (i+1)] == {}:
						self.checkJudgement(note, len(notes) - (i+1), True)
					print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1],   f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}   ")
					self.dontDraw.append(note)
		text_beat = "○ ○ ○ ○"
		text_beat = text_beat[:int(self.localConduc.currentBeat)%4 * 2] + "●" + text_beat[(int(self.localConduc.currentBeat)%4 * 2) + 1:]
		print_at(int(term.width * 0.5)-3, 1, term.normal + text_beat)
		
	def draw(self):
		if not self.localConduc.isPaused:
			timerText = str(format_time(int(self.localConduc.currentTimeSec))) + " / " + str(format_time(int(self.endTime)))
			print_at(0,0, f"{term.normal}{term.center(timerText)}")
			print_at(0,0,term.normal + self.chart["metadata"]["artist"] + " - " + self.chart["metadata"]["title"])
			print_at(term.width - (len(str(self.accuracy)) + 2), 0, str(self.accuracy) + "%")
			print_at(term.width - (len(str(self.score)) + 1), 1, str(self.score))
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

			self.actualKeysRendering(self.chart["notes"])
		else:
			global locales
			text_paused = "PAUSED"
			text_resume = "Resume"
			text_retry  = "Retry"
			text_quit	= "Quit"
			print_at(int((term.width-len(text_paused)) * 0.5) - 4, int(term.height*0.5) - 4, "*---" + text_paused + "---*")
			print_at(int((term.width-len(text_paused)) * 0.5) - 4, int(term.height*0.5) + 2, "*---" + ("-"*len(text_paused)) + "---*")
			print_column(int((term.width-len(text_paused)) * 0.5) - 4, int(term.height*0.5) - 3, 5, '|')
			print_column(int((term.width+len(text_paused)) * 0.5) + 3, int(term.height*0.5) - 3, 5, '|')
			if self.pauseOption == 0:
				print_at(int((term.width-len(text_resume)) * 0.5) - 1, int(term.height*0.5) - 2, term.normal+term.reverse+" "+text_resume+" "+term.normal)
			else:
				print_at(int((term.width-len(text_resume)) * 0.5) - 1, int(term.height*0.5) - 2, term.normal+" "+text_resume+" "+term.normal)

			if self.pauseOption == 1:
				print_at(int((term.width-len(text_retry)) * 0.5) - 1, int(term.height*0.5) - 1, term.normal+term.reverse+" "+text_retry+" "+term.normal)
			else:
				print_at(int((term.width-len(text_retry)) * 0.5) - 1, int(term.height*0.5) - 1, term.normal+" "+text_retry+" "+term.normal)

			if self.pauseOption == 2:
				print_at(int((term.width-len(text_quit)) * 0.5) - 1, int(term.height*0.5), term.normal+term.reverse+" "+text_quit+" "+term.normal)
			else:
				print_at(int((term.width-len(text_quit)) * 0.5) - 1, int(term.height*0.5), term.normal+" "+text_quit+" "+term.normal)
			

		# self.localConduc.debugSound()

	def retry(self):
		print(term.clear)
		self.localConduc.stop()
		self.localConduc.song.move2position_seconds(0)
		self.localConduc.play()

	def handle_input(self):
		if not self.localConduc.isPaused:
			val = ''
			val = term.inkey(timeout=1/inputFrequency)
			# debug_val(val)

			if val.name == "KEY_ESCAPE":
				self.localConduc.pause()

			if self.localConduc.currentTimeSec > self.endTime:
				if not os.path.exists("./logs/results.json"):
					f = open("./logs/results.json", "x")
				else:
					f = open("./logs/results.json", "w")
				f.write(json.dumps(self.resultsFile(),indent=4))
				f.close()
				# raise NotImplementedError("Results screen missing!")
				self.resultsScreen.resultsData = self.resultsFile()
				self.resultsScreen.isEnabled = True
				self.resultsScreen.setup()

			if val in keys and not self.auto and not self.localConduc.isPaused:
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

			if self.auto and not self.localConduc.isPaused:
				for i in range(len(self.chart["notes"])):
					note = self.chart["notes"][i]
					if note["type"] == "hit_object":
						if note not in self.outOfHere:
							isHit = self.checkJudgement(note, i)
							if isHit:
								self.outOfHere.append(note)
								break;
		else:
			val = ''
			val = term.inkey(timeout=1/60)
			
			if val.name == "KEY_ESCAPE":
				self.localConduc.resume()
			if val.name == "KEY_DOWN" or val == "j":
				self.pauseOption = (self.pauseOption + 4)%3
			if val.name == "KEY_UP" or val == "k":
				self.pauseOption = (self.pauseOption + 2)%3

			if val.name == "KEY_ENTER":
				if self.pauseOption == 0:
					self.localConduc.resume()
				if self.pauseOption == 1:
					self.retry()
				if self.pauseOption == 2:
					self.turnOff = True

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = self.localConduc.update()
				if not self.resultsScreen.isEnabled:
					self.draw()
					self.handle_input()
				else:
					self.resultsScreen.draw()
					self.resultsScreen.handle_input()
					self.turnOff = self.resultsScreen.gameTurnOff
		# print("On god? Just like that?")
		self.localConduc.stop()
		self.localConduc.song.stop()
		self.turnOff = False
		self.resultsScreen.gameTurnOff = False
		self.resultsScreen.isEnabled = False

				

	def play(self, chart = {}, layout = "qwerty"):
		# print(chart)
		self.setupKeys(layout)
		self.judgements = []
		self.dontDraw = []
		self.outOfHere = []
		self.resultsScreen = ResultsScreen()
		self.missesCount = 0
		self.score = 0
		self.chart = chart
		self.localConduc.loadsong(self.chart)
		self.localConduc.play()
		self.localConduc.song.move2position_seconds(0)
		self.endTime = self.getSongEndTime()
		self.loop()


	def __init__(self) -> None:
		print("Wow, look, nothing!")

		pass

