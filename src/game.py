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
	from src.results import *
	from src.translate import Locale
else:
	from termutil import *
	from conductor import *
	from results import *
	from translate import Locale


CENTER = 0
LEFT = 1
DOWN = 2
UP = 3
RIGHT = 4
DOWN_LEFT = 5
DOWN_RIGHT = 6
UP_LEFT = 7
UP_RIGHT = 8

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

term = Terminal()

colors = [
	term.normal,
	term.red,
	term.orange,
	term.yellow,
	term.green,
	term.cyan,
	term.blue,
	term.purple,
	term.aqua,
	term.magenta,
	term.gray
]

defaultSize = [80, 24]

inputFrequency = 999

keys = [
	"a","z","e","r","t","y","u","i","o","p",
	"q","s","d","f","g","h","j","k","l","m",
	"w","x","c","v","b","n",",",";",":","!"
]

hitWindows = [0.05, 0.1, 0.2, 0.3, 0.4]
judgementNames = [f"{term.purple}MARV", f"{term.aqua}PERF", f"{term.green}EPIC", f"{term.yellow}GOOD", f"{term.orange} EH ", f"{term.red}MISS"]
judgementShort = [f"{term.purple}@", f"{term.aqua}#", f"{term.green}$", f"{term.yellow}*", f"{term.orange};", f"{term.red}/"]
accMultiplier = [1, 0.95, 0.85, 0.75, 0.5, 0]

# You can either use "setSize" or "scale"
# setSize will use a set terminal size as playfield (By default, 80x24)
# while scale will use the current terminal size with a small offset applied.
playfield_mode = "setSize"

maxScore = 1000000

class Game:
	version = 1.2
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
	pauseOption = 0
	resultsScreen = ResultsScreen()
	playername = ""
	lastHit = {}
	options = {}

	#Locale
	loc:Locale = Locale("en")

	#Bypass size
	bypassSize = False

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
	
	def trueCalcPos(self, x, y, mode = ""):
		if mode == "":
			mode = playfield_mode
		calc_pos = []
		topleft = [int((f.width-defaultSize[0]) * 0.5), int((f.height-defaultSize[1]) * 0.5)]
		if mode == "setSize":
			calc_pos = [
				int(x*(defaultSize[0]))+topleft[0],
				int(y*(defaultSize[1]))+topleft[1]]
		else:
			calc_pos = [
				int(x*(f.width-12))+6,
				int(y*(f.height-9))+4]
		return calc_pos

	def resultsFile(self):
		global keys
		self.score = scoreCalc(maxScore, self.judgements, self.accuracy, self.missesCount, self.chart)
		toBeCheckSumd = dict((i,self.chart[i]) for i in self.chart if i != "actualSong")
		output = {
			"accuracy": self.accuracy,
			"score": self.score,
			"judgements": self.judgements,
			"checksum": hashlib.sha256(json.dumps(toBeCheckSumd,skipkeys=True,ensure_ascii=False).encode("utf-8")).hexdigest(),
			"version": self.version,
			"time": time.time(),
			"playername": self.playername,
			"keys": "".join(keys)
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
		remTime = self.localConduc.currentTimeSec - ((note["beatpos"][0] * 4 + note["beatpos"][1]) * (60/self.localConduc.bpm))
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
				self.lastHit = self.judgements[noteNum]
				self.accuracyUpdate()
				self.score = int(scoreCalc(maxScore, self.judgements, self.accuracy, self.missesCount, self.chart))
				calc_pos = self.trueCalcPos(note["screenpos"][0], note["screenpos"][1])
				print_at(calc_pos[0], calc_pos[1], judgementShort[judgement])

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
					self.lastHit = self.judgements[noteNum]
					self.accuracyUpdate()
					calc_pos = self.trueCalcPos(note["screenpos"][0], note["screenpos"][1])
					print_at(calc_pos[0], calc_pos[1], judgementShort[judgement])
					print_at(10, 1, judgementNames[judgement])
					self.missesCount += 1
				return False
		else:
			if remTime >= 0:
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
				self.lastHit = self.judgements[noteNum]
				self.accuracyUpdate()
				self.score = int(scoreCalc(maxScore, self.judgements, self.accuracy, self.missesCount, self.chart))
				calc_pos = self.trueCalcPos(note["screenpos"][0], note["screenpos"][1])
				print_at(calc_pos[0], calc_pos[1], judgementShort[judgement])
				return True

	def getSongEndTime(self):
		out = self.localConduc.getLength()
		for note in self.chart["notes"]:
			if note["type"] == "end":
				atBeat = (note["beatpos"][0] * 4 + note["beatpos"][1])
				out = atBeat * (60/self.localConduc.bpm)
				break

		return out

	def renderText(self, text = "", offset = [0,0], anchor = CENTER, align = ALIGN_LEFT, renderOffset = [0,0]):
		#calculate position
		calculatedPosition = [0,0]

		if anchor == CENTER:
			calculatedPosition[0] = int(defaultSize[0]/2 + offset[0])
			calculatedPosition[1] = int(defaultSize[1]/2 + offset[1])
		elif anchor == LEFT:
			calculatedPosition[0] = int(offset[0])
			calculatedPosition[1] = int(defaultSize[1]/2 + offset[1])
		elif anchor == DOWN:
			calculatedPosition[0] = int(defaultSize[0]/2 + offset[0])
			calculatedPosition[1] = int(defaultSize[1] + offset[1])
		elif anchor == UP:
			calculatedPosition[0] = int(defaultSize[0]/2 + offset[0])
			calculatedPosition[1] = int(offset[1])
		elif anchor == RIGHT:
			calculatedPosition[0] = int(defaultSize[0] + offset[0])
			calculatedPosition[1] = int(defaultSize[1]/2 + offset[1])
		elif anchor == DOWN_LEFT:
			calculatedPosition[0] = int(offset[0])
			calculatedPosition[1] = int(defaultSize[1] + offset[1])
		elif anchor == DOWN_RIGHT:
			calculatedPosition[0] = int(defaultSize[0] + offset[0])
			calculatedPosition[1] = int(defaultSize[1] + offset[1])
		elif anchor == UP_LEFT:
			calculatedPosition[0] = int(offset[0])
			calculatedPosition[1] = int(offset[1])
		elif anchor == UP_RIGHT:
			calculatedPosition[0] = int(defaultSize[0] + offset[0])
			calculatedPosition[1] = int(offset[1])

		#check for aligns
		if align == ALIGN_LEFT:
			pass
		elif align == ALIGN_CENTER:
			calculatedPosition[0] -= int(len(text)*0.5)
		elif align == ALIGN_RIGHT:
			calculatedPosition[0] -= len(text)-1

		#prevent clipping out of the playfield
		renderedText = text

		if calculatedPosition[0] < 0:
			renderedText = text[-calculatedPosition[0]:]
			calculatedPosition[0] = 0
		if calculatedPosition[0] + len(text) > defaultSize[0]:
			renderedText = text[:len(renderedText) - (calculatedPosition[0] + len(renderedText) - defaultSize[0])]
		
		topleft = [int((term.width-defaultSize[0]) * 0.5) + renderOffset[0], int((term.height-defaultSize[1]) * 0.5) + renderOffset[1]]

		if 0 <= calculatedPosition[1] < defaultSize[1]:
			print_at(calculatedPosition[0] + topleft[0], calculatedPosition[1] + topleft[1], renderedText)

		pass

	def renderNote(self, atPos, color, key, approachedBeats, notes = {}, i = -1):
		toPrint = "   \n   \n   \n"
		val = int(approachedBeats*2)
		if val == 8:
			toPrint = f"{term.normal}{color} ═ \n{term.normal}{color}   \n{term.normal}{color}   {term.normal}"
		elif val == 7:
			toPrint = f"{term.normal}{color} ═╗\n{term.normal}{color}   \n{term.normal}{color}   {term.normal}"
		elif val == 6:
			toPrint = f"{term.normal}{color} ═╗\n{term.normal}{color}  ║\n{term.normal}{color}   {term.normal}"
		elif val == 5:
			toPrint = f"{term.normal}{color} ═╗\n{term.normal}{color}  ║\n{term.normal}{color}  ╝{term.normal}"
		elif val == 4:
			toPrint = f"{term.normal}{color} ═╗\n{term.normal}{color}  ║\n{term.normal}{color} ═╝{term.normal}"
		elif val == 3:
			toPrint = f"{term.normal}{color} ═╗\n{term.normal}{color}  ║\n{term.normal}{color}╚═╝{term.normal}"
		elif val == 2:
			toPrint = f"{term.normal}{color} ═╗\n{term.normal}{color}║ ║\n{term.normal}{color}╚═╝{term.normal}"
		elif val == 1:
			toPrint = f"{term.normal}{color}╔═╗\n{term.normal}{color}║ ║\n{term.normal}{color}╚═╝{term.normal}"
		
		print_lines_at(atPos[0]-1, atPos[1]-1, toPrint)
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
		if len(notes) >= len(self.judgements):
			while len(notes) >= len(self.judgements):
				self.judgements.append({})
		for i in range(len(notes)):
			note = notes[len(notes) - (i+1)] #It's inverted so that the ones with the lowest remBeats are rendered on top of the others.
			if note["type"] == "hit_object":
				calc_pos = self.trueCalcPos(note["screenpos"][0], note["screenpos"][1])
				if type(note["color"]) is int:
					color = colors[note["color"]]
				else:
					# Formatting: "RRGGBB"
					colorSplit = color_code_from_hex(note["color"])
					color = term.color_rgb(colorSplit[0], colorSplit[1], colorSplit[2])
				key = keys[note["key"]]
				remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat - (self.localConduc.offset/(60/self.localConduc.bpm))
				remTime = ((note["beatpos"][0] * 4 + note["beatpos"][1]) * (60/self.localConduc.bpm)) - self.localConduc.currentTimeSec
				approachedBeats = (remBeats * self.chart["approachRate"]) + 1
				if approachedBeats > -0.1 and approachedBeats < 4 and note not in self.dontDraw:

					Game.renderNote(self, calc_pos, color, key, approachedBeats, notes, i) # Say it, you didn't expect a call directly to the Game class. Frankly it's the same shit lmao

				if note not in self.dontDraw and ((remTime <= -0.6) or (self.judgements[len(notes) - (i+1)] != {} and -0.2 > remTime > -0.6 )):
					if note not in self.outOfHere:
						self.outOfHere.append(note)
					if self.judgements[len(notes) - (i+1)] == {}:
						self.checkJudgement(note, len(notes) - (i+1), True)
					print_at(calc_pos[0]-1, calc_pos[1]-1, f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1],   f"{color}   ")
					print_at(calc_pos[0]-1, calc_pos[1]+1, f"{color}   ")
					self.dontDraw.append(note)
			if note["type"] == "text":
				renderAt = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat - (self.localConduc.offset/(60/self.localConduc.bpm))
				stopAt = renderAt + note["length"]
				if note not in self.dontDraw:
					if renderAt <= 0:
						if stopAt > 0:
							self.renderText(note["text"], note["offset"], note["anchor"], note["align"])
						else:
							self.renderText(" " * len(note["text"]), note["offset"], note["anchor"], note["align"])
							self.dontDraw.append(note)
					
				
		text_beat = "○ ○ ○ ○"
		text_beat = text_beat[:int(self.localConduc.currentBeat)%4 * 2] + "●" + text_beat[(int(self.localConduc.currentBeat)%4 * 2) + 1:]
		print_at(int(term.width * 0.5)-3, 1, term.normal + text_beat)
		
	def draw(self):
		print_at(0, term.height-2, str(framerate()) + "fps" + term.clear_eol)
		if not self.localConduc.isPaused:
			timerText = str(format_time(int(self.localConduc.currentTimeSec))) + " / " + str(format_time(int(self.endTime)))
			print_at(0,0, f"{term.normal}{term.center(timerText)}")
			print_at(0,0,term.normal + self.chart["metadata"]["artist"] + " - " + self.chart["metadata"]["title"])
			print_at(term.width - (len(str(self.accuracy)) + 2), 0, str(self.accuracy) + "%")
			print_at(term.width - (len(str(self.score)) + 1), 1, str(self.score))

			if self.auto:
				print_at(0,1, f"{term.reverse}[AUTO ENABLED]{term.normal}")

			if self.lastHit != {}:
				print_at(15, 1, judgementNames[self.lastHit["judgement"]] + "   " + term.normal + str(round(self.lastHit["offset"]*1000, 4)) + "ms")
			
			if playfield_mode == "scale":
				print_box(4,2,term.width-7,term.height-4,term.normal,1)
			elif playfield_mode == "setSize":
				topleft = [int((term.width-defaultSize[0]) * 0.5)-1, int((term.height-defaultSize[1]) * 0.5)-1]
				print_box(topleft[0],topleft[1],defaultSize[0]+2,defaultSize[1]+2,term.normal,1)
			
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
			

	def retry(self):
		print(term.clear)
		self.localConduc.stop()
		self.localConduc.song.move2position_seconds(0)
		self.judgements = []
		self.outOfHere = []
		self.dontDraw = []
		self.localConduc.skippedTimeWithPause = 0
		self.localConduc.play()
		self.localConduc.bpm = self.localConduc.previewChart["bpm"]
		self.localConduc.isPaused = False
		# self.localConduc.resume()

	def handle_input(self):
		if not self.localConduc.isPaused:
			val = ''
			val = term.inkey(timeout=1/inputFrequency, esc_delay=0)

			if val.name == "KEY_ESCAPE":
				self.localConduc.pause()

			if self.localConduc.currentTimeSec > self.endTime:
				result = self.resultsFile()
				if not self.auto:
					if not os.path.exists("./scores/"):
						os.mkdir("./scores/")
					if not os.path.exists("./logs/"):
						os.mkdir("./logs/")
					if not os.path.exists("./logs/results.json"):
						f = open("./logs/results.json", "x")
					else:
						f = open("./logs/results.json", "w")
					f.write(json.dumps(result,indent=4))
					f.close()
					f2 = open("./scores/" + self.chart["foldername"].replace("/", "_").replace("\\", "_") + "-" + hashlib.sha256(json.dumps(result).encode("utf-8")).hexdigest(), "x")
					f2.write(json.dumps(result))
					f2.close()
				self.resultsScreen.hitWindows = hitWindows
				self.resultsScreen.resultsData = result
				self.resultsScreen.isEnabled = True
				print(term.clear)
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
			val = term.inkey(timeout=1/inputFrequency, esc_delay=0)
			
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
					self.localConduc.resume()

	def loop(self):
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.deltatime = self.localConduc.update()
				if not self.resultsScreen.isEnabled:
					if not too_small(self.bypassSize):
						self.draw()
					else:
						text = self.loc("screenTooSmall")
						print_at(int((term.width - len(text))*0.5), int(term.height*0.5), term.reverse + text + term.normal)
					refresh()
					self.handle_input()
				else:
					self.resultsScreen.draw()
					refresh()
					self.resultsScreen.handle_input()
					self.turnOff = self.resultsScreen.gameTurnOff
				if self.auto and not self.resultsScreen.auto: #displays the resultsScreen.auto message even if you somehow can disable it
					self.resultsScreen.auto = self.auto
		self.localConduc.stop()
		self.localConduc.song.stop()
		self.turnOff = False
		self.resultsScreen.gameTurnOff = False
		self.resultsScreen.isEnabled = False

				

	def play(self, chart = {}, layout = "qwerty", options = {}):
		self.options = options
		self.resultsScreen.auto = self.auto
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

