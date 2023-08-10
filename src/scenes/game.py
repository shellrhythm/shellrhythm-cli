from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
# from index import *
import hashlib
from src.termutil import term, print_at, set_reset_color
from src.conductor import *
from src.scenes.results import *
from src.scenes.base_scene import BaseScene
from src.translate import Locale
from src.scenes.game_objects.note import NoteObject

from src.constants import *




class Game(BaseScene):
    version = 1.2
    localConduc = Conductor()
    beatSound = Song("assets/clap.wav")
    chart = {}
    deltatime = 0.0
    turnOff = False
    score = 0
    judgements = []
    outOfHere = []
    dontDraw = []
    end_time = 2**32
    accuracy = 100
    auto = False
    misses_count = 0
    pause_option = 0
    results_screen = ResultsScreen()
    playername = ""
    lastHit = {}
    options = {}
    background_changes = [
        [0, term.normal]
    ]
    keys = [
        "a","z","e","r","t","y","u","i","o","p",
        "q","s","d","f","g","h","j","k","l","m",
        "w","x","c","v","b","n",",",";",":","!"
    ]
    notes = []

    #Locale
    loc:Locale = Locale("en")

    #Bypass size
    bypassSize = False

    def set_background(self, background):
        colors[0] = background
        set_reset_color(background)

    def get_background(self, at_beat):
        out = term.normal
        for i in self.background_changes:
            if i[0] < at_beat:
                out = i[1]
            else:
                break
        return out

    def setupKeys(self, layout):
        if os.path.exists("./layout/" + layout):
            output = []
            file = open("./layout/" + layout, encoding="utf8")
            rows = file.readlines()

            for row in range(len(rows)):
                for char in range(10):
                    output.append(rows[row][char])

            if self is not None:
                self.keys = output
            else:
                return output
    

    def generate_results_file(self):
        self.score = scoreCalc(MAX_SCORE, self.judgements, self.accuracy, self.misses_count, self.chart)
        checksum_checked_data = dict((i,self.chart[i]) for i in self.chart if i != "actualSong")
        output = {
            "accuracy": self.accuracy,
            "score": self.score,
            "judgements": self.judgements,
            "checksum": hashlib.sha256(json.dumps(checksum_checked_data,skipkeys=True,ensure_ascii=False).encode("utf-8")).hexdigest(),
            "version": self.version,
            "time": time.time(),
            "playername": self.playername,
            "keys": "".join(self.keys)
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

    # def getSongEndTime(self):
    #     out = self.localConduc.getLength()
    #     for note in self.chart["notes"]:
    #         if note["type"] == "end":
    #             ends_at_beat = note["beatpos"][0] * 4 + note["beatpos"][1]
    #             out = ends_at_beat * (60/self.localConduc.bpm)
    #             break

    #     return out


    @staticmethod
    def calculate_position(screen_pos:list, x:int, y:int, width:int, height:int):
        """
        x: (Int) screen x offset
        y: (Int) screen y offset
        width: (Int) screen width
        height: (Int) screen height
        """
        return [int(screen_pos[0]*width)+x, int(screen_pos[1]*height)+y]

    def actualKeysRendering(self):
        if len(self.notes) >= len(self.judgements):
            while len(self.notes) >= len(self.judgements):
                self.judgements.append({})
        for i in range(len(self.notes)):
            note = self.notes[len(self.notes) - (i+1)] #It's inverted so that the ones with the lowest remaining_beats are rendered on top of the others.
            offseted_beat = self.localConduc.currentBeat - (self.localConduc.offset/(60/self.localConduc.bpm))
            note.render(offseted_beat,self.dontDraw)
                    
                
        text_beat = "○ ○ ○ ○"
        text_beat = text_beat[:int(self.localConduc.currentBeat)%4 * 2] + "●" + text_beat[(int(self.localConduc.currentBeat)%4 * 2) + 1:]
        print_at(int(term.width * 0.5)-3, 1, reset_color + text_beat)
        
    def draw(self):
        # get background color
        self.set_background(self.get_background(self.localConduc.currentBeat))
        print_at(0, term.height-2, str(framerate()) + "fps" )
        if not self.localConduc.isPaused:
            timerText = str(format_time(int(self.localConduc.currentTimeSec))) + " / " + str(format_time(int(self.end_time)))
            print_at(0,0, f"{reset_color}{term.center(timerText)}")
            print_at(0,0,reset_color + self.chart["metadata"]["artist"] + " - " + self.chart["metadata"]["title"])
            print_at(term.width - (len(str(self.accuracy)) + 2), 0, str(self.accuracy) + "%")
            print_at(term.width - (len(str(self.score)) + 1), 1, str(self.score))

            if self.auto:
                print_at(0,1, f"{term.reverse}[AUTO ENABLED]{reset_color}")

            if self.lastHit != {}:
                print_at(15, 1, JUDGEMENT_NAMES[self.lastHit["judgement"]] + "   " + reset_color + str(round(self.lastHit["offset"]*1000, 4)) + "ms")
            
            # if PLAYFIELD_MODE == "scale":
            #     print_box(4,2,term.width-7,term.height-4,reset_color,1)
            # elif PLAYFIELD_MODE == "setSize":
            topleft = [int((term.width-default_size[0]) * 0.5)-1, int((term.height-default_size[1]) * 0.5)-1]
            print_box(topleft[0],topleft[1],default_size[0]+2,default_size[1]+2,reset_color,1)
            
            self.actualKeysRendering()
        else:
            # global locales
            text_paused = "PAUSED"
            text_resume = "Resume"
            text_retry  = "Retry"
            text_quit	= "Quit"
            print_at(int((term.width-len(text_paused)) * 0.5) - 4, int(term.height*0.5) - 4, "*---" + text_paused + "---*")
            print_at(int((term.width-len(text_paused)) * 0.5) - 4, int(term.height*0.5) + 2, "*---" + ("-"*len(text_paused)) + "---*")
            print_column(int((term.width-len(text_paused)) * 0.5) - 4, int(term.height*0.5) - 3, 5, '|')
            print_column(int((term.width+len(text_paused)) * 0.5) + 3, int(term.height*0.5) - 3, 5, '|')
            if self.pause_option == 0:
                print_at(int((term.width-len(text_resume)) * 0.5) - 1, int(term.height*0.5) - 2, reset_color+term.reverse+" "+text_resume+" "+reset_color)
            else:
                print_at(int((term.width-len(text_resume)) * 0.5) - 1, int(term.height*0.5) - 2, reset_color+" "+text_resume+" "+reset_color)

            if self.pause_option == 1:
                print_at(int((term.width-len(text_retry)) * 0.5) - 1, int(term.height*0.5) - 1, reset_color+term.reverse+" "+text_retry+" "+reset_color)
            else:
                print_at(int((term.width-len(text_retry)) * 0.5) - 1, int(term.height*0.5) - 1, reset_color+" "+text_retry+" "+reset_color)

            if self.pause_option == 2:
                print_at(int((term.width-len(text_quit)) * 0.5) - 1, int(term.height*0.5), reset_color+term.reverse+" "+text_quit+" "+reset_color)
            else:
                print_at(int((term.width-len(text_quit)) * 0.5) - 1, int(term.height*0.5), reset_color+" "+text_quit+" "+reset_color)
            

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
            val = term.inkey(timeout=1/INPUT_FREQUENCY, esc_delay=0)

            if val.name == "KEY_ESCAPE":
                self.localConduc.pause()

            if self.localConduc.currentTimeSec > self.end_time:
                result = self.generate_results_file()
                if not self.auto:
                    if not os.path.exists("./scores/"):
                        os.mkdir("./scores/")
                    if not os.path.exists("./logs/"):
                        os.mkdir("./logs/")
                    file = None
                    if not os.path.exists("./logs/results.json"):
                        file = open("./logs/results.json", "x", encoding="utf8")
                    else:
                        file = open("./logs/results.json", "w", encoding="utf8")
                    file.write(json.dumps(result,indent=4))
                    file.close()
                    f2 = open("./scores/"
                            + self.chart["foldername"].replace("/", "_").replace("\\", "_")
                            + "-" + hashlib.sha256(json.dumps(result).encode("utf-8")).hexdigest(),
                            "x", encoding="utf8")
                    f2.write(json.dumps(result))
                    f2.close()
                self.results_screen.hitWindows = hitWindows
                self.results_screen.resultsData = result
                self.results_screen.isEnabled = True
                print(term.clear)
                self.results_screen.setup()

            if val in self.keys and not self.auto and not self.localConduc.isPaused:
                pos = [-1, -1]
                for y in range(len(self.keys)):
                    for x in range(len(self.keys[y])):
                        if self.keys[y][x] == val:
                            pos = [x, y]
                for i in range(len(self.chart["notes"])):
                    note = self.chart["notes"][i]
                    if note["type"] == "hit_object":
                        if note["key"] == pos[0] * 10 + pos[1] and note not in self.outOfHere:
                            hit_detected = self.checkJudgement(note, i)
                            if hit_detected:
                                self.outOfHere.append(note)
                                break

            if self.auto and not self.localConduc.isPaused:
                for i in range(len(self.chart["notes"])):
                    note = self.chart["notes"][i]
                    if note["type"] == "hit_object":
                        if note not in self.outOfHere:
                            hit_detected = self.checkJudgement(note, i)
                            if hit_detected:
                                self.outOfHere.append(note)
                                break
        else:
            val = ''
            val = term.inkey(timeout=1/INPUT_FREQUENCY, esc_delay=0)

            if val.name == "KEY_ESCAPE":
                self.localConduc.resume()
            if val.name == "KEY_DOWN" or val == "j":
                self.pause_option = (self.pause_option + 4)%3
            if val.name == "KEY_UP" or val == "k":
                self.pause_option = (self.pause_option + 2)%3

            if val.name == "KEY_ENTER":
                if self.pause_option == 0:
                    self.localConduc.resume()
                if self.pause_option == 1:
                    self.retry()
                if self.pause_option == 2:
                    self.turn_off = True
                    self.localConduc.resume()

    def handle_screen_too_small(self):
        text = self.loc("screenTooSmall")
        print_at(
            int((term.width - len(text))*0.5),
            int(term.height*0.5),
            term.reverse + text + reset_color
        )

    def loop(self):
        super().loop()
        self.set_background(term.normal)
        self.localConduc.stop()
        self.localConduc.song.stop()
        self.turn_off = False
        self.results_screen.gameTurnOff = False
        self.results_screen.isEnabled = False

    def load_bg_changes(self, notes):
        """TODO: REWRITE THIS"""
        out = []
        for note in notes:
            if note["type"] == "bg_color":
                color = term.normal
                for col in note["color"].split("/"):
                    if col.startswith("#"): # background color
                        parsed_color = color_code_from_hex(note["color"][1:])
                        color += term.on_color_rgb(
                            parsed_color[0],
                            parsed_color[1],
                            parsed_color[2]
                        )
                    elif col.startswith("%"): # foreground color
                        parsed_color = color_code_from_hex(note["color"][1:])
                        color += term.color_rgb(
                            parsed_color[0],
                            parsed_color[1],
                            parsed_color[2]
                        )
                    else: # reset
                        color = term.normal
                out.append([(note["beatpos"][0] * 4 + note["beatpos"][1]), color])
        if self is not None:
            self.background_changes = out
        else:
            return out

    def setup_notes(self, notes):
        """Sets up notes in the self.notes variable"""
        self.background_changes = []
        for note in notes:
            if note["type"] == "hit_object": # setup note
                new_note = NoteObject(note, self.keys)
                new_note.approach_rate = self.chart["approachRate"]
                self.notes.append(new_note)
            elif note["type"] == "bg_color":
                color = term.normal
                for col in note["color"].split("/"):
                    if col.startswith("#"): # background color
                        parsed_color = color_code_from_hex(note["color"][1:])
                        color += term.on_color_rgb(
                            parsed_color[0],
                            parsed_color[1],
                            parsed_color[2]
                        )
                    elif col.startswith("%"): # foreground color
                        parsed_color = color_code_from_hex(note["color"][1:])
                        color += term.color_rgb(
                            parsed_color[0],
                            parsed_color[1],
                            parsed_color[2]
                        )
                    else: # reset
                        color = term.normal
            elif note["type"] == "end":
                ends_at_beat = note["beatpos"][0] * 4 + note["beatpos"][1]
                self.end_time = ends_at_beat * (60/self.localConduc.bpm)


    def play(self, chart, options, layout = "qwerty"):
        self.chart = chart
        self.setupKeys(layout)

        self.setup_notes(chart["notes"])
        # self.load_bg_changes(chart)
        self.options = options
        self.judgements = []
        self.dontDraw = []
        self.outOfHere = []

        self.results_screen = ResultsScreen()
        self.results_screen.auto = self.auto
        self.misses_count = 0
        self.score = 0

        self.localConduc.loadsong(self.chart)
        self.localConduc.play()
        self.localConduc.song.move2position_seconds(0)

        self.loop()


    def __init__(self) -> None:
        print("Wow, look, nothing!")

