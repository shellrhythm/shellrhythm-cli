from pybass3 import Song
import time
print(__name__)
if __name__ != "src.conductor":
	from termutil import *
else:
	from src.termutil import *

def format_time(seconds):
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60

	if hour != 0:
		return "%d:%02d:%02d" % (hour, minutes, seconds)
	else:
		return "%d:%02d" % (minutes, seconds)


class Conductor:
	bpm = 120
	offset = 0
	startTime = 0
	currentTimeSec = 0
	prevTimeSec = 0
	currentBeat = 0
	prevBeat = 0
	song = Song("./assets/clap.wav")
	previewChart = {}
	metronome = False
	metroSound = Song("./assets/clap.wav")
	startTimeNoOffset = 0
	isPaused = False
	pauseStartTime = 0
	skippedTimeWithPause = 0

	def loadsong(self, chart = {}):
		self.bpm = chart["bpm"]
		self.offset = chart["offset"]
		if "actualSong" in chart:
			self.song = chart["actualSong"]
		else:
			self.song = Song("./charts/" + chart["foldername"] + "/" + chart["sound"])
		self.previewChart = chart

	def onBeat(self):
		if self.metronome:
			self.metroSound.play()

	def debugSound(self, term):
		print_at(0, term.height-6, f"beat: {self.currentBeat} | time: {self.currentTimeSec} | start time: {self.startTime}")

	def play(self):
		self.startTimeNoOffset = (time.time_ns() / 10**9)
		self.startTime = self.startTimeNoOffset + self.offset
		self.song.play()

	def pause(self):
		self.bpm = 0
		self.isPaused = True
		self.pauseStartTime = (time.time_ns() / 10**9)
		self.song.pause()
	
	def resume(self):
		self.isPaused = False
		self.bpm = self.previewChart["bpm"]
		self.skippedTimeWithPause = (time.time_ns() / 10**9) - self.pauseStartTime
		self.song.move2position_seconds(max((time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause), 0))
		self.song.resume()

	def update(self):
		if not self.isPaused and self.bpm > 0:
			self.currentTimeSec = (time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause)
			self.deltatime = self.currentTimeSec - self.prevTimeSec
			self.currentBeat = self.currentTimeSec * (self.bpm/60)
			self.prevTimeSec = self.currentTimeSec

			if int(self.currentBeat) > int(self.prevBeat):
				self.onBeat()

			self.prevBeat = self.currentBeat

			return self.deltatime
		else:
			self.skippedTimeWithPause = (time.time_ns() / 10**9) - self.pauseStartTime
			return 1/60

	def stop(self):
		# self.song.pause()
		self.song.stop()

	def getLength(self):
		return self.song._length_seconds
	
	def setOffset(self, newOffset):
		self.offset = newOffset
		self.startTime = self.startTimeNoOffset + self.offset
	
	def startAt(self, beatpos):
		secPos = beatpos*(60/self.bpm)
		self.startTimeNoOffset = (time.time_ns() / 10**9) - secPos
		self.startTime = self.startTimeNoOffset + self.offset
		self.currentTimeSec = secPos
		self.prevTimeSec = 0
		self.currentBeat = beatpos
		if self.song._length_seconds is not None:
			if self.song._length_seconds >= secPos:
				self.song.stop()
				self.song.play()
				self.song.move2position_seconds(secPos)
				return True
		return False


	def __init__(self) -> None:
		pass
