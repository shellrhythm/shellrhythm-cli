import os
import json
import time
import hashlib
from src.termutil import term, print_at, framerate,\
    color_code_from_hex, print_box
from src.constants import Vector2i, colors, MAX_SCORE, accMultiplier, JUDGEMENT_NAMES,\
    INPUT_FREQUENCY, hitWindows, Color
from src.conductor import Conductor, format_time
from src.options import OptionsManager
from src.scene_manager import SceneManager
from src.scenes.base_scene import BaseScene
from src.scenes.results import scoreCalc
from src.layout import LayoutManager
from src.translate import Locale
from src.scenes.game_objects.base_object import GameplayObject
from src.scenes.game_objects.note import NoteObject
from src.scenes.game_objects.text import TextObject
from src.scenes.game_objects.bg_color import BackgroundColorObject
from src.scenes.game_objects.end_level import EndLevelObject
from src.scenes.game_objects.playfield import Playfield
# import easing_functions as easings


class Game(BaseScene):
    version = 1.3

    conduc:Conductor = Conductor()
    beat_sound_volume = 1.0
    chart = {}
    deltatime = 0.0
    turnOff = False
    score = 0
    judgements = []
    out_of_here = []
    dont_draw = []
    end_time = 2**32
    accuracy = 100
    auto = False
    misses_count = 0
    pause_option = 0
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
    palette = [
        term.normal,
        Color("fc220a"),
        Color("fc9b0a"),
        Color("f4fc0a"),
        Color("0efc0a"),
        Color("0afcfc"),
        Color("0a36fc"),
        Color("830afc"),
        Color("0ab7fc"),
        Color("fc0ab3"),
        Color("72737c")
    ]
    notes:list[GameplayObject] = []

    #Locale
    loc:Locale = Locale("en")

    #Bypass size
    bypassSize = False

    playfield:Playfield = Playfield()

    def set_background(self, background):
        self.palette[0] = term.normal + background
        self.reset_color = term.normal + background

    def get_background(self, at_beat):
        out = term.normal
        for i in self.background_changes:
            if i[0] < at_beat:
                out = i[1]
            else:
                break
        return out

    def setup_keys(self, layout):
        if self is not None:
            self.keys = LayoutManager[layout]
        return LayoutManager[layout]

    def generate_results_file(self):
        self.accuracy_update()
        self.score = scoreCalc(
            MAX_SCORE,
            self.judgements,
            self.accuracy,
            self.misses_count,
            self.chart
        )
        checksum_checked_data = dict((i,self.chart[i]) for i in self.chart if i != "actualSong")
        output = {
            "accuracy": self.accuracy,
            "score": self.score,
            "judgements": self.judgements,
            "checksum": hashlib.sha256(
                json.dumps(
                    checksum_checked_data,
                    skipkeys=True,
                    ensure_ascii=False
                ).encode("utf-8")
            ).hexdigest(),
            "version": self.version,
            "time": time.time(),
            "playername": self.playername,
            "keys": "".join(self.keys)
        }
        return output

    def accuracy_update(self):
        """Updates self.accuracy and self.misses_count accurately."""
        judges = 1.0
        count = 1
        misses_c = 0
        for i in self.judgements:
            if i != {}:
                judges += accMultiplier[i["judgement"]]
                count += 1
                if i["judgement"] == 5:
                    misses_c += 1
        self.accuracy = round((judges / count) * 100, 2)
        self.misses_count = misses_c

    @staticmethod
    def calculate_position(screen_pos:list, x:int, y:int, width:int, height:int):
        """
        x: (Int) screen x offset
        y: (Int) screen y offset
        width: (Int) screen width
        height: (Int) screen height
        """
        return [int(screen_pos[0]*width)+x, int(screen_pos[1]*height)+y]

    async def actualKeysRendering(self):
        if len(self.notes) >= len(self.judgements):
            while len(self.notes) >= len(self.judgements):
                self.judgements.append({})

        await self.playfield.draw(self, self.notes)

        text_beat = "○ ○ ○ ○"
        text_beat = text_beat[:int(self.conduc.current_beat)%4 * 2] \
            + "●" + text_beat[(int(self.conduc.current_beat)%4 * 2) + 1:]
        print_at(int(term.width * 0.5)-3, 1, self.reset_color + text_beat)

    async def draw(self):
        # get background color
        self.set_background(self.get_background(self.conduc.current_beat))
        print_at(0, term.height-2, str(framerate()) + "fps" )
        if not self.conduc.paused:
            timer_text = str(format_time(int(self.conduc.cur_time_sec))) + " / "\
                + str(format_time(int(self.end_time)))
            print_at(0,0, f"{self.reset_color}{term.center(timer_text)}")
            print_at(0,0,self.reset_color + self.chart["metadata"]["artist"] + " - "\
                     + self.chart["metadata"]["title"])
            print_at(term.width - (len(str(self.accuracy)) + 2), 0, str(self.accuracy) + "%")
            print_at(term.width - (len(str(int(self.score))) + 1), 1, str(int(self.score)))

            if self.auto:
                print_at(0,1, f"{term.reverse}[AUTO ENABLED]{self.reset_color}")

            if self.lastHit:
                print_at(15, 1, JUDGEMENT_NAMES[self.lastHit["judgement"]] + "   " +\
                         self.reset_color + str(round(self.lastHit["offset"]*1000, 4)) + "ms")

            await self.actualKeysRendering()
        else:
            # global locales
            text_paused = "PAUSED"
            text_resume = "Resume"
            text_retry  = "Retry"
            text_quit	= "Quit"
            print_box(
                int((term.width-len(text_paused)) * 0.5) - 4,
                int(term.height*0.5) - 4,
                8+len(text_paused),
                7,
                self.reset_color,
                2,
                text_paused,
                self.reset_color
            )
            if self.pause_option == 0:
                print_at(
                    int((term.width-len(text_resume)) * 0.5) - 1,
                    int(term.height*0.5) - 2,
                    self.reset_color+term.reverse+" "+text_resume+" "+self.reset_color
                )
            else:
                print_at(
                    int((term.width-len(text_resume)) * 0.5) - 1,
                    int(term.height*0.5) - 2,
                    self.reset_color+" "+text_resume+" "+self.reset_color
                )

            if self.pause_option == 1:
                print_at(
                    int((term.width-len(text_retry)) * 0.5) - 1,
                    int(term.height*0.5) - 1,
                    self.reset_color+term.reverse+" "+text_retry+" "+self.reset_color
                )
            else:
                print_at(
                    int((term.width-len(text_retry)) * 0.5) - 1,
                    int(term.height*0.5) - 1,
                    self.reset_color+" "+text_retry+" "+self.reset_color
                )

            if self.pause_option == 2:
                print_at(
                    int((term.width-len(text_quit)) * 0.5) - 1,
                    int(term.height*0.5),
                    self.reset_color+term.reverse+" "+text_quit+" "+self.reset_color
                )
            else:
                print_at(
                    int((term.width-len(text_quit)) * 0.5) - 1,
                    int(term.height*0.5),
                    self.reset_color+" "+text_quit+" "+self.reset_color
                )

    def retry(self):
        """this is what happens when you press retry"""
        self.conduc.stop()
        self.conduc.song.move2position_seconds(0)
        self.judgements = []
        self.out_of_here = []
        self.dont_draw = []
        self.conduc.skipped_time_with_pause = 0
        self.conduc.play()
        self.conduc.bpm = self.conduc.previewChart["bpm"]
        self.conduc.paused = False
        # self.localConduc.resume()

    async def handle_input(self):
        if not self.conduc.paused:
            val = ''
            val = term.inkey(timeout=0, esc_delay=0)

            if val.name == "KEY_ESCAPE":
                self.conduc.pause()

            if self.conduc.cur_time_sec > self.end_time:
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
                    file2 = open("./scores/"
                            + self.chart["foldername"].replace("/", "_").replace("\\", "_")
                            + "-" + hashlib.sha256(json.dumps(result).encode("utf-8")).hexdigest(),
                            "x", encoding="utf8")
                    file2.write(json.dumps(result))
                    file2.close()
                SceneManager["Results"].hit_windows = hitWindows
                SceneManager["Results"].results_data = result
                SceneManager["Results"].isEnabled = True
                print(term.clear)
                SceneManager.change_scene("Results")

            for (note_id, note) in enumerate(self.notes):
                if isinstance(note, NoteObject):
                    hit_detected = None
                    note.check_beat_sound_timing(self.conduc.cur_time_sec)
                    if val in self.keys and not self.auto and not self.conduc.paused:
                        if note not in self.out_of_here:
                            if note.key == val:
                                hit_detected = note.checkJudgement(
                                    self.conduc.cur_time_sec,
                                    wasnt_hit=False,
                                    auto=self.auto
                                )
                    if self.auto and not self.conduc.paused:
                        if note not in self.out_of_here:
                            hit_detected = note.checkJudgement(
                                self.conduc.cur_time_sec,
                                auto=self.auto
                            )
                    if hit_detected is not None:
                        self.accuracy_update()
                        self.score = scoreCalc(
                                MAX_SCORE,
                                self.judgements,
                                self.accuracy,
                                self.misses_count,
                                self.chart
                        )
                        self.judgements[note_id] = note.judgement
                        self.out_of_here.append(note)
                        break
        else:
            val = ''
            val = term.inkey(timeout=1/INPUT_FREQUENCY, esc_delay=0)

            if val.name == "KEY_ESCAPE":
                self.conduc.resume()
            if val.name == "KEY_DOWN" or val == "j":
                self.pause_option = (self.pause_option + 4)%3
            if val.name == "KEY_UP" or val == "k":
                self.pause_option = (self.pause_option + 2)%3

            if val.name == "KEY_ENTER":
                if self.pause_option == 0: #Resume
                    self.conduc.resume()
                if self.pause_option == 1: #Retry
                    self.retry()
                if self.pause_option == 2: #Quit
                    SceneManager.change_scene("ChartSelect")
                    self.conduc.resume()

    def on_close(self):
        self.set_background(term.normal)
        self.conduc.stop()
        self.conduc.song.stop()
        self.turn_off = False
        SceneManager["Results"].gameTurnOff = False
        SceneManager["Results"].isEnabled = False

    @staticmethod
    def load_bg_changes(notes):
        """Returns an array containing background changes in a convenient tuple
        The format of the tuple is (beatpos, color),
        color being a string containing the change cursor color command.
        """
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
        return out

    @staticmethod
    def get_bpm_map(chart):
        """Quick way to get the bpm map of the chart"""
        if "bpmChanges" in chart:
            if len(chart["bpmChanges"]) != 0:
                return chart["bpmChanges"]
        return [chart["bpm"]]

    def setup_notes(self, notes, offset:Vector2i = Vector2i.zero):
        """Sets up notes in the self.notes variable"""
        self.playfield = Playfield()
        self.playfield.offset = offset
        self.notes = []
        self.background_changes = []
        bpm_changes = Game.get_bpm_map(self.chart)
        for note in notes:
            new_note = None
            if note["type"] == "hit_object": # setup note
                new_note = NoteObject(note, bpm_changes, self.keys, self.palette)
                new_note.approach_rate = self.chart["approachRate"]
                SceneManager["Options"].conduc.bass.SetChannelVolume(
                    new_note.hit_sound.handle, OptionsManager["hitSoundVolume"]
                )
            if note["type"] == "text":
                new_note = TextObject(note, bpm_changes)
            elif note["type"] == "bg_color":
                new_note = BackgroundColorObject(note, bpm_changes)
                self.background_changes.append((new_note.beat_position, new_note.new_color))
            elif note["type"] == "end":
                new_note = EndLevelObject(note, bpm_changes)
                self.end_time = new_note.time_position
            new_note.playfield = self.playfield
            self.notes.append(new_note)

    @staticmethod
    def setup_palette(palette:list) -> list:
        """Builds the actually usable palette variable from an array of hexadecimal colors"""
        out = [
            term.normal
        ]
        for col in palette:
            out.append(Color(col))
        return out


    def play(self, chart, options, layout = "qwerty"):
        """Set up the chart in the game player"""
        if "palette" in chart:
            self.palette = Game.setup_palette(chart["palette"])
        else:
            self.palette = colors

        self.chart = chart
        self.conduc.loadsong(self.chart)
        self.setup_notes(chart["notes"])

        self.setup_keys(layout)

        # self.load_bg_changes(chart)
        self.options = options
        self.judgements = []
        self.dont_draw = []
        self.out_of_here = []

        SceneManager["Results"].auto = self.auto
        self.misses_count = 0
        self.score = 0

        self.conduc.song.move2position_seconds(0)
        self.conduc.play()
