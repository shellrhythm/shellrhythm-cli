from index import print_at, print_column, print_cropped, print_lines_at, Conductor, load_charts, chartData
from blessed import Terminal

conduc = Conductor()

term = Terminal()
turnOff = False

hitCount = 0
maxHits = 16

hits = []
totalOffset = 0

calibrationMenu = "CalibrationSelect"
# Possible things:
# CalibrationSelect [100%]: Select calibration options
# CalibrationGlobal [100%]: Calibrate your game
# CalibrationSong [0%]: Sync song to beats

calibselec = 0
selecSong = -1

def handle_input():
	val = ''
	val = term.inkey(timeout=1/60)
	if val:
		global totalOffset
		global turnOff
		if calibrationMenu == "CalibrationGlobal":
			global hitCount
			offset = (conduc.currentBeat - int(conduc.currentBeat)) * (60/conduc.bpm)
			print_at(0,14, f"{term.center(str(round(offset, 3)))}")
			hits.append(offset)
			totalOffset += offset
			hitCount += 1
			if hitCount >= maxHits:
				turnOff = True
		if calibrationMenu == "CalibrationSong":
			if val.name == "KEY_ESCAPE":
				turnOff = True
			if val.name == "KEY_LEFT":
				totalOffset -= 0.001
				print_at(0,14, f"{term.center(str(round(totalOffset, 3)))}")
				conduc.setOffset(totalOffset)
			if val.name == "KEY_RIGHT":
				totalOffset -= 0.001
				print_at(0,14, f"{term.center(str(round(totalOffset, 3)))}")
				conduc.setOffset(totalOffset)

		if calibrationMenu == "CalibrationSelect":
			global calibselec
			global selecSong
			if selecSong == -1:
				if val.name == "KEY_DOWN":
						calibselec = (calibselec + 1)%3
				if val.name == "KEY_UP":
						calibselec = (calibselec + 2)%3
				if val.name == "KEY_ENTER":
					if calibselec == 0:
						startCalibGlobal()
					if calibselec == 1:
						selecSong = 0
						print_at(int((term.width)*0.2), int(term.height*0.5)-1,"Select a song:")
						print_at(int((term.width)*0.2), int(term.height*0.5)+1,"> " + str(selecSong) + "  ")
					if calibselec == 2:
						turnOff = True
			else:
				if val.name == "KEY_LEFT":
					selecSong = (selecSong - 1)%len(chartData)
					print_at(int((term.width)*0.2), int(term.height*0.5)+1,"> " + str(selecSong) + "  ")
				if val.name == "KEY_RIGHT":
					selecSong = (selecSong + 1)%len(chartData)
					print_at(int((term.width)*0.2), int(term.height*0.5)+1,"> " + str(selecSong) + "  ")
				if val.name == "KEY_ENTER":
					startCalibSong(chartData[selecSong])


def draw():
	if calibrationMenu == "CalibrationGlobal":
		text_beat = "○ ○ ○ ○"
		text_beat = text_beat[:int(conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(conduc.currentBeat)%4 * 2) + 1:]

		print_at(0,10,f"{term.center('Hit on beat!')}")
		print_at(0,12,f"{term.center(text_beat)}")
	if calibrationMenu == "CalibrationSong":
		text_title = chartData[selecSong]["metadata"]["title"] + " - " + chartData[selecSong]["metadata"]["artist"]
		text_bpm = "BPM: " + str(chartData[selecSong]["bpm"])
		print_at(0,9,f"{term.center(text_title)}")
		print_at(0,10,f"{term.center(text_bpm)}")
		
		text_beat = "○ ○ ○ ○"
		text_beat = text_beat[:int(conduc.currentBeat)%4 * 2] + "●" + text_beat[(int(conduc.currentBeat)%4 * 2) + 1:]
		print_at(0,12,f"{term.center(text_beat)}")
		

	if calibrationMenu == "CalibrationSelect":
		text_first = "Global offset calibration"
		text_second = "Song offset test"
		text_quit = "Quit"
		if calibselec == 0:
			print_at(int((term.width - len(text_first))*0.5)+2, int(term.height*0.5) - 2, term.reverse + "> " + text_first + " <" + term.normal)
		else:
			print_at(int((term.width - len(text_first))*0.5)+2, int(term.height*0.5) - 2, "< " + text_first + " >")

		if calibselec == 1:
			print_at(int((term.width - len(text_second))*0.5)+2, int(term.height*0.5), term.reverse + "> " + text_second + " <" + term.normal)
		else:
			print_at(int((term.width - len(text_second))*0.5)+2, int(term.height*0.5), "< " + text_second + " >")
		
		if calibselec == 2:
			print_at(int((term.width - len(text_quit))*0.5)+2, int(term.height*0.5) + 2, term.reverse + "> " + text_quit + " <" + term.normal)
		else:
			print_at(int((term.width - len(text_quit))*0.5)+2, int(term.height*0.5) + 2, "< " + text_quit + " >")

def startCalibGlobal():
	global calibrationMenu
	calibrationMenu = "CalibrationGlobal"
	print(term.clear)
	conduc.play()

def startCalibSong(chart):
	global calibrationMenu
	calibrationMenu = "CalibrationSong"
	print(term.clear)
	conduc.stop()
	conduc.loadsong(chart)
	conduc.play()
	conduc.metronome = True

def init():
	load_charts()
	conduc.loadsong(chartData[0])
	with term.fullscreen(), term.cbreak(), term.hidden_cursor():
		print(term.clear)
		while not turnOff:
			if calibrationMenu != "CalibrationSelect":
				deltatime = conduc.update()

			draw()
			handle_input()

	if hitCount != 0:
		print(round(totalOffset / hitCount, 3))
		return totalOffset / hitCount

if __name__ == "__main__":
	init()