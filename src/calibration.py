# from index import print_at, print_column, print_cropped, print_lines_at, Conductor, load_charts, chartData
from blessed import Terminal
import json, os
print(__name__)
if __name__ != "src.calibration":
	from loading import check_chart, load_charts
	from termutil import print_at
	from conductor import Conductor
	from translate import Locale
else:
	from src.loading import check_chart, load_charts
	from src.termutil import print_at
	from src.conductor import Conductor
	from src.translate import Locale

from pybass3 import Song

term = Terminal()

class Calibration:
	conduc = Conductor()
	turnOff = False
	hitCount = 0
	maxHits = 16

	hits = []
	totalOffset = 0

	calibrationMenu = "CalibrationSelect"
	# Possible things:
	# CalibrationSelect : Select calibration options
	# CalibrationGlobal : Calibrate your game
	# CalibrationSong   : Sync song to beats

	calibselec = 0
	selecSong = -1

	chartData = []

	#Locale
	loc:Locale = Locale("en")

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/120, esc_delay=0)
		if val:
			if self.calibrationMenu == "CalibrationGlobal":
				offset = (self.conduc.currentBeat - int(self.conduc.currentBeat)) * (60/self.conduc.bpm)
				print_at(0,14, f"{term.center(str(round(offset, 3)))}")
				self.hits.append(offset)
				self.totalOffset += offset
				self.hitCount += 1
				if self.hitCount >= self.maxHits:
					self.turnOff = True
			if self.calibrationMenu == "CalibrationSong":
				if val.name == "KEY_ESCAPE":
					self.turnOff = True
				if val.name == "KEY_LEFT":
					self.totalOffset -= 0.001
					print_at(0,14, f"{term.center(str(round(self.totalOffset, 3)))}")
					self.conduc.setOffset(self.totalOffset)
				if val.name == "KEY_RIGHT":
					self.totalOffset += 0.001
					print_at(0,14, f"{term.center(str(round(self.totalOffset, 3)))}")
					self.conduc.setOffset(self.totalOffset)

			if self.calibrationMenu == "CalibrationSelect":
				if self.selecSong == -1:
					if val.name == "KEY_DOWN":
							self.calibselec = (self.calibselec + 1)%3
					if val.name == "KEY_UP":
							self.calibselec = (self.calibselec + 2)%3
					if val.name == "KEY_ENTER":
						if self.calibselec == 0:
							self.startCalibGlobal()
						if self.calibselec == 1:
							self.selecSong = 0
							print_at(int((term.width)*0.2), int(term.height*0.5)-1,self.loc("calibration.selectSong"))
							print_at(int((term.width)*0.2), int(term.height*0.5)+1,"> " + str(self.selecSong) + "  ")
						if self.calibselec == 2:
							self.turnOff = True
				else:
					if val.name == "KEY_LEFT":
						self.selecSong = (self.selecSong - 1)%len(self.chartData)
						print_at(int((term.width)*0.2), int(term.height*0.5)+1,"> " + str(self.selecSong) + "  ")
					if val.name == "KEY_RIGHT":
						self.selecSong = (self.selecSong + 1)%len(self.chartData)
						print_at(int((term.width)*0.2), int(term.height*0.5)+1,"> " + str(self.selecSong) + "  ")
					if val.name == "KEY_ENTER":
						self.startCalibSong(self.chartData[self.selecSong])


	def draw(self):
		if self.calibrationMenu == "CalibrationGlobal":
			text_beat = "○ ○ ○ ○"
			text_beat = text_beat[:int(self.conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(self.conduc.currentBeat)%4 * 2) + 1:]

			print_at(0,10,f"{term.center(self.loc('calibration.hit'))}")
			print_at(0,12,f"{term.center(text_beat)}")
		if self.calibrationMenu == "CalibrationSong":
			text_title = self.chartData[self.selecSong]["metadata"]["title"] + " - " + self.chartData[self.selecSong]["metadata"]["artist"]
			text_bpm = "BPM: " + str(self.chartData[self.selecSong]["bpm"])
			print_at(0,9,f"{term.center(text_title)}")
			print_at(0,10,f"{term.center(text_bpm)}")

			text_beat = "○ ○ ○ ○"
			text_beat = text_beat[:int(self.conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(self.conduc.currentBeat)%4 * 2) + 1:]
			print_at(0,12,f"{term.center(text_beat)}")


		if self.calibrationMenu == "CalibrationSelect":
			text_first = self.loc('calibration.global')
			text_second = self.loc('calibration.perSong')
			text_quit = self.loc('calibration.quit')
			if self.calibselec == 0:
				print_at(int((term.width - len(text_first))*0.5)+2, int(term.height*0.5) - 2, term.reverse + "> " + text_first + " <" + term.normal)
			else:
				print_at(int((term.width - len(text_first))*0.5)+2, int(term.height*0.5) - 2, "< " + text_first + " >")

			if self.calibselec == 1:
				print_at(int((term.width - len(text_second))*0.5)+2, int(term.height*0.5), term.reverse + "> " + text_second + " <" + term.normal)
			else:
				print_at(int((term.width - len(text_second))*0.5)+2, int(term.height*0.5), "< " + text_second + " >")

			if self.calibselec == 2:
				print_at(int((term.width - len(text_quit))*0.5)+2, int(term.height*0.5) + 2, term.reverse + "> " + text_quit + " <" + term.normal)
			else:
				print_at(int((term.width - len(text_quit))*0.5)+2, int(term.height*0.5) + 2, "< " + text_quit + " >")

	def startCalibGlobal(self):
		self.calibrationMenu = "CalibrationGlobal"
		print(term.clear)
		self.conduc.play()

	def startCalibSong(self, chart):
		self.calibrationMenu = "CalibrationSong"
		print(term.clear)
		self.conduc.stop()
		self.conduc.loadsong(chart)
		self.conduc.play()
		self.conduc.metronome = True

	def init(self):
		self.chartData = load_charts()
		self.conduc.loadsong(self.chartData[0])
		if self.calibrationMenu == "CalibrationGlobal":
			self.startCalibGlobal()
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				if self.calibrationMenu != "CalibrationSelect":
					deltatime = self.conduc.update()

				self.draw()
				self.handle_input()

		if self.hitCount != 0:
			print(round(self.totalOffset / self.hitCount, 3))
			return self.totalOffset / self.hitCount
	
	def __init__(self, calibrationMenu) -> None:
		self.calibrationMenu = calibrationMenu

if __name__ == "__main__":
	calib = Calibration("CalibrationSelect")
	calib.init()