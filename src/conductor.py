from pybass3 import *
from time import time_ns
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
    start_time = 0
    cur_time_sec = 0
    prev_time_sec = 0
    current_beat = 0
    prevBeat = 0
    song = Song("./assets/clap.wav")
    previewChart = {}
    metronome = False
    metroSound = Song("./assets/metronome.wav")
    start_time_no_offset = 0
    paused = False
    pause_start_time = 0
    skipped_time_with_pause = 0
    volume = 1
    metronomeVolume = 1
    bpmChanges = [
        # {
        # 	"atPosition": [16,0],
        # 	"toBPM": 150
        # }
    ]
    loopStart = -1
    loopEnd = -1
    isLoop = False
    bass = Bass()
    deltatime = 0.0

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

    def loadsong(self, chart:dict = None):
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

    def debugSound(self):
        print_at(0, term.height-6, f"beat: {self.current_beat} | "+\
                f"time: {self.cur_time_sec} | "+\
                f"start time: {self.start_time}")

    def play(self):
        self.skipped_time_with_pause = 0
        self.start_time_no_offset = time_ns() / 10**9
        self.start_time = self.start_time_no_offset + self.offset
        self.setVolume(self.volume)
        self.song.play()

    def pause(self):
        self.bpm = 0
        self.paused = True
        self.pause_start_time = time_ns() / 10**9
        if self.song.is_playing:
            self.song.pause()

    def resume(self):
        if self.paused:
            self.paused = False
            self.bpm = self.previewChart["bpm"]
            self.skipped_time_with_pause = (time_ns() / 10**9) - self.pause_start_time
            # self.song.move2position_seconds(max((time.time_ns() / 10**9) - (self.startTime + self.skippedTimeWithPause), 0))
            self.song.resume()

    def update(self):
        if not self.paused and self.bpm > 0 and self.song.is_playing:
            assert self.start_time != 0
            self.cur_time_sec = (time_ns() / 10**9) - (self.start_time + self.skipped_time_with_pause)
            self.deltatime = self.cur_time_sec - self.prev_time_sec
            self.current_beat = self.getBeatPos(self.cur_time_sec)
            self.prev_time_sec = self.cur_time_sec

            if self.current_beat < 0 and self.cur_time_sec + self.offset < 0:
                self.song.move2position_seconds(0)
                self.current_beat = 0
                self.skipped_time_with_pause = 0
                self.start_time_no_offset = (time_ns() / 10**9)
                self.start_time = self.start_time_no_offset + self.offset

            if int(self.current_beat) > int(self.prevBeat):
                self.onBeat()

            self.prevBeat = self.current_beat

            if self.isLoop:
                if self.cur_time_sec > self.loopEnd:
                    difference = self.loopEnd - self.loopStart
                    self.cur_time_sec = self.cur_time_sec - difference
                    self.prev_time_sec = self.prev_time_sec - difference
                    self.start_time = self.start_time + difference
                    self.current_beat = self.getBeatPos(self.cur_time_sec)
                    self.song.move2position_seconds(self.cur_time_sec)
            return self.deltatime
        if self.song.is_playing:
            self.song.pause()
        self.skipped_time_with_pause = (time_ns() / 10**9) - self.pause_start_time
        return 1/60

    def stop(self):
        # self.song.pause()
        self.song.stop()

    def getLength(self):
        return self.song.duration

    def setOffset(self, newOffset):
        self.offset = newOffset
        self.start_time = self.start_time_no_offset + self.offset

    def startAt(self, beatpos):
        secPos = beatpos*(60/self.bpm)
        self.start_time_no_offset = (time_ns() / 10**9) - secPos
        self.start_time = self.start_time_no_offset + self.offset
        self.cur_time_sec = secPos
        self.prev_time_sec = 0
        self.current_beat = beatpos
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
