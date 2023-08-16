from pybass3 import Song, Bass
from time import time_ns
from src.termutil import print_at, term

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
    previous_beat = 0
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

    @staticmethod
    def get_bpm_at_time_from_bpm_table(time_pos:float, bpm_table:list) -> float:
        result:float = 100.0
        for change in bpm_table[1:]:
            next_beat = change["atPosition"][0] + (change["atPosition"][1]/4)
            bpm = change["toBPM"]
            sec = (next_beat - last_bpm_change[0])/(last_bpm_change[2]/60) + last_bpm_change[1]
            if sec > time_pos:
                result = last_bpm_change[2]
                return result
            last_bpm_change = [next_beat, sec, bpm]
        result = last_bpm_change[2]
        return result

    @staticmethod
    def calculate_time_sec_from_bpm_table(beat_pos:float, bpm_table:list) -> float:
        """bruh i most likely have to redo this from scratch i can't do it in reverse :("""
        last_bpm_change = [0, 0, bpm_table[0]] #Beat to change at, corresponding time, bpm to go to
        #Note: this assumes that the first bpm event is set at beat 0.0. If it isn't, you're weird.
        bpm = bpm_table[0]
        for change in bpm_table[1:]:
            next_beat = change["atPosition"][0] + (change["atPosition"][1]/4)
            bpm = change["toBPM"]
            sec = (next_beat - last_bpm_change[0])/(last_bpm_change[2]/60) + last_bpm_change[1]
            if next_beat > beat_pos:
                break
            last_bpm_change = [next_beat, sec, bpm]
        beats_since_last_change = beat_pos - last_bpm_change[1]
        return (beats_since_last_change/(bpm/60) + (last_bpm_change[0]))

    @staticmethod
    def calculate_beat_from_bpm_table(time_pos:float, bpm_table:list) -> float:
        last_bpm_change = [0, 0, bpm_table[0]] #Beat to change at, corresponding time, bpm to go to
        #Note: this assumes that the first bpm event is set at beat 0.0. If it isn't, you're weird.
        for change in bpm_table[1:]:
            next_beat = change["atPosition"][0] + (change["atPosition"][1]/4)
            bpm = change["toBPM"]
            sec = (next_beat - last_bpm_change[0])/(last_bpm_change[2]/60) + last_bpm_change[1]
            if sec > time_pos:
                break
            last_bpm_change = [next_beat, sec, bpm]
        time_since_last_change = time_pos - last_bpm_change[1]
        return (time_since_last_change*(bpm/60) + (last_bpm_change[0]))

    def getBeatPos(self, position:float) -> float:
        if self.bpmChanges == []:
            return position * (self.bpm/60)
        else:
            self.bpm = Conductor.get_bpm_at_time_from_bpm_table(position, self.bpmChanges)
            return Conductor.calculate_beat_from_bpm_table(position, self.bpmChanges)

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
            self.song.resume()

    def update(self):
        if not self.paused and self.bpm > 0 and self.song.is_playing:
            assert self.start_time != 0
            self.cur_time_sec = (time_ns() / 10**9) - \
                (self.start_time + self.skipped_time_with_pause)
            self.deltatime = self.cur_time_sec - self.prev_time_sec
            self.current_beat = self.getBeatPos(self.cur_time_sec)
            self.prev_time_sec = self.cur_time_sec

            if self.current_beat < 0 and self.cur_time_sec + self.offset < 0:
                self.song.move2position_seconds(0)
                self.current_beat = 0
                self.skipped_time_with_pause = 0
                self.start_time_no_offset = time_ns() / 10**9
                self.start_time = self.start_time_no_offset + self.offset

            if int(self.current_beat) > int(self.previous_beat):
                self.onBeat()

            self.previous_beat = self.current_beat

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

    def setOffset(self, new_offset):
        self.offset = new_offset
        self.start_time = self.start_time_no_offset + self.offset

    def startAt(self, beatpos):
        seconds_pos = beatpos*(60/self.bpm)
        self.start_time_no_offset = (time_ns() / 10**9) - seconds_pos
        self.start_time = self.start_time_no_offset + self.offset
        self.cur_time_sec = seconds_pos
        self.prev_time_sec = 0
        self.current_beat = beatpos
        if self.song.duration is not None:
            if self.song.duration >= seconds_pos:
                self.song.stop()
                self.song.play()
                self.song.move2position_seconds(seconds_pos)
                return True
        else:
            self.song.play()
        return False


    def __init__(self) -> None:
        pass
