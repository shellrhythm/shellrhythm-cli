from pybass3 import *
import time
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
	metroSound = Song("./assets/metronome.wav")
	startTimeNoOffset = 0
	isPaused = False
	pauseStartTime = 0
	skippedTimeWithPause = 0
	volume = 1
	metronomeVolume = 1
	bpmChanges = [
		# {
		# 	"atPosition": [16,0],
		# 	"toBPM": 150
		# }
	]
	bass = Bass()

	def setMetronomeVolume(self, volume):
		self.metronomeVolume = volume
		self.bass.SetChannelVolume(self.metroSound.handle, volume)

	def setVolume(self, volume):
		self.volume = volume
		self.bass.SetChannelVolume(self.song.handle, volume)

	def getBeatPos(self, position:float) -> float:
		if self.bpmChanges == []:
			return position * (self.bpm/60)
		else:
			lastBPMChange = [0, 0, self.bpm] #Beat to change at, corresponding second, bpm to go to
			for change in self.bpmChanges:
				nextBeat = change["atPosition"][0] + (change["atPosition"][1]/4)
				bpm = change["toBPM"]
				sec = (nextBeat - lastBPMChange[0])/(lastBPMChange[2]/60) + lastBPMChange[1]
				if sec > position:
					timeSinceLastChange = position - lastBPMChange[1]
					self.bpm = lastBPMChange[2]
					return (timeSinceLastChange*(lastBPMChange[2]/60) + (lastBPMChange[0]))
				lastBPMChange = [nextBeat, sec, bpm]
			timeSinceLastChange = position - lastBPMChange[1]
			self.bpm = lastBPMChange[2]
			return (timeSinceLastChange*(bpm/60) + (lastBPMChange[0]))

	def loadsong(self, chart = {}):
		self.bpm = chart["bpm"]
		self.offset = chart["offset"]
		if "bpmChanges" in chart:
			self.bpmChanges = chart["bpmChanges"]
		if "actualSong" in chart:
			self.song = chart["actualSong"]
		else:
			if chart["sound"] != "" and chart["sound"] is not None:
				self.song = Song("./charts/" + chart["foldername"] + "/" + chart["sound"])
		self.previewChart = chart

	def onBeat(self):
		if self.metronome:
			self.metroSound.play()

	def debugSound(self, term):
		print_at(0, term.height-6, f"beat: {self.currentBeat} | time: {self.currentTimeSec} | start time: {self.startTime}")

	def play(self):
		self.skippedTimeWithPause = 0
		self.startTimeNoOffset = (time.time_ns() / 10**9)
		self.startTime = self.startTimeNoOffset + self.offset
		self.setVolume(self.volume)
		self.song.play()

	def pause(self):
		self.bpm = 0
		self.isPaused = True
		self.pauseStartTime = (time.time_ns() / 10**9)
		if self.song.is_playing:
			self.song.pause()
	
	def resume(self):
		if self.isPaused:
			self.isPaused = False
			self.bpm = self.previewChart["bpm"]
			self.skippedTimeWithPause = (time.time_ns() / 10**9) - self.pauseStartTime
			# self.song.move2position_seconds(max((time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause), 0))
			self.song.resume()

	def update(self):
		if not self.isPaused and self.bpm > 0:
			self.currentTimeSec = (time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause)
			self.deltatime = self.currentTimeSec - self.prevTimeSec
			self.currentBeat = self.getBeatPos(self.currentTimeSec)
			self.prevTimeSec = self.currentTimeSec

			if self.currentBeat < 0:
				self.song.move2position_seconds(0)
				self.currentBeat = 0
				self.skippedTimeWithPause = 0
				self.startTimeNoOffset = (time.time_ns() / 10**9)
				self.startTime = self.startTimeNoOffset + self.offset

			if int(self.currentBeat) > int(self.prevBeat):
				self.onBeat()

			self.prevBeat = self.currentBeat

			return self.deltatime
		else:
			if self.song.is_playing:
				self.song.pause()
			self.skippedTimeWithPause = (time.time_ns() / 10**9) - self.pauseStartTime
			return 1/60

	def stop(self):
		# self.song.pause()
		self.song.stop()

	def getLength(self):
		return self.song.duration
	
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
		if self.song.duration is not None:
			if self.song.duration >= secPos:
				self.song.stop()
				self.song.play()
				self.song.move2position_seconds(secPos)
				return True
		else:
			self.song.play()
		return False


	def __init__(self) -> None:
		pass
