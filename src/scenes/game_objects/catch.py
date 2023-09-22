"""Catch note gameplay object, a note where you can simply hold down the key in advance"""

from pybass3 import Song
from .base_object import GameplayObject
from ...translate import LocaleManager
from ...termutil import print_at, print_lines_at, term, color_code_from_hex
from ...constants import JUDGEMENT_NAMES, JUDGEMENT_NAMES_SHORT,\
    Vector2, Vector2i, hitWindows

class CatchObject(GameplayObject):
    """Catch object."""
    key:str = "?"
    position:Vector2 = Vector2() #0-1 on every axis
    color:str = term.normal
    color_string:str|int = "NOTHING"
    beat_position:float = 0.0
    time_position:float = 0.0
    approach_rate:float = 1.0
    judgement:dict = {}
    hit_sound:Song = Song("assets/clap.wav")
    played_sound:bool = False
    palette:list = None
    _key_index:int = -1
    _keys:list = []
    _color:int|str = ""
    _using_palette:bool = False
    _palette_id:int = -1
    _palette_color = None

    def __init__(self, data:dict, bpm_table:list, keys:list, palette:list) -> None:
        self.beat_position = data["beatpos"][0] * 4 + data["beatpos"][1]
        self.time_position = GameplayObject.compute_time_position(self.beat_position, bpm_table)
        self._keys = keys
        self._key_index = data["key"]
        self._color = data["color"]
        self.key = keys[data["key"]]

        if isinstance(data["color"], int):
            self.set_color_from_palette(data["color"], palette)
        else:
            color_split = color_code_from_hex(data["color"])
            self.color = term.color_rgb(color_split[0], color_split[1], color_split[2])
            self.color_string = str(data["color"])
        self.position = Vector2i(data["screenpos"][0], data["screenpos"][1])

    def set_color_from_palette(self, palette_id:int, palette:list):
        self._using_palette = True
        self._color = palette_id
        if palette_id != 0:
            self._palette_id = palette_id
            self._palette_color = palette[palette_id]
            self.color = self._palette_color.col
        else:
            self.color = palette[palette_id]
        self.color_string = palette_id

    def set_color_hex(self, new_color:str):
        self._using_palette = False
        self._color = new_color
        self.color_string = new_color
        color_split = color_code_from_hex(new_color)
        self.color = term.color_rgb(color_split[0], color_split[1], color_split[2])

    @property
    def key_index(self) -> int:
        return self._key_index

    @key_index.setter
    def key_index(self, new_key:int):
        self._key_index = new_key
        self.key = self._keys[new_key]

    def serialize(self):
        return {
            "type":     "hit_object",
            "key":      self._key_index,
            "color":    self._color,
            "beatpos":  [self.beat_position//4, self.beat_position%4],
            "screenpos":[self.position.x, self.position.y]
        }

    def calculate_position(self) -> Vector2i:
        """Converts position (normalized) into an actual onscreen position \
        based on the playfield size."""
        calc_pos = []
        topleft = self.playfield.top_left()
        calc_pos = Vector2i(
               int(self.position.x*(self.playfield.size.x))+topleft.x,
               int(self.position.y*(self.playfield.size.y))+topleft.y)
        # calc_pos = [
        #     int(x*(f.width-12))+6,
        #     int(y*(f.height-9))+4]
        return calc_pos

    def check_beat_sound_timing(self, current_time:float):
        remaining_time = self.time_position - current_time
        if remaining_time <= 0.0 and not self.played_sound:
            self.played_sound = True
            self.hit_sound.move2position_seconds(0)
            self.hit_sound.play()


    def checkJudgement(self, current_time:float, wasnt_hit:bool = False, \
                       auto:bool = False) -> bool | None:
        remaining_time = self.time_position - current_time
        if not auto:
            if -0.6 < remaining_time < hitWindows[0]:
                # if noteNum >= len(self.judgements):
                #     while noteNum >= len(self.judgements):
                #         self.judgements.append({})
                self.judgement = {
                    "offset": remaining_time,
                    "judgement": 0
                }
                # self.lastHit = self.judgements[noteNum]
                # self.accuracyUpdate()
                # self.score = int(scoreCalc(MAX_SCORE, self.judgements, \
                #                  self.accuracy, self.missesCount, self.chart))
                calc_pos = self.calculate_position()
                print_at(calc_pos[0], calc_pos[1], JUDGEMENT_NAMES_SHORT[0])

                # if judgement == 5:
                #     self.missesCount += 1
                return True
            else:
                if remaining_time <= -0.6 and wasnt_hit:
                    self.judgement = {
                        "offset": remaining_time,
                        "judgement": 5
                    }
                    calc_pos = self.calculate_position()
                    print_at(calc_pos[0], calc_pos[1], JUDGEMENT_NAMES_SHORT[5])
                    print_at(10, 1, JUDGEMENT_NAMES[5])
                    # self.missesCount += 1
                return False
        else:
            if remaining_time <= 0:
                self.judgement = {
                    "offset": remaining_time,
                    "judgement": 0
                }
                calc_pos = self.calculate_position()
                print_at(calc_pos[0], calc_pos[1], JUDGEMENT_NAMES_SHORT[0])
                return True
        return None

    def editor_timeline_icon(self, reset_color:str, selected:bool = False):
        output = self.key.upper() + reset_color
        if selected:
            output = term.reverse + output
        output = self.color + output
        return output

    def display_informations(self, reset_color:str, note_id:int = 0) -> str:
        loc = LocaleManager.current_locale()
        return reset_color\
                +f"{loc('editor.timelineInfos.curNote')}: {note_id} | "\
                +f"{loc('editor.timelineInfos.color')}: " \
                    +f"{self.color}[{self.color_string}]{reset_color} | "\
                +f"{loc('editor.timelineInfos.screenpos')}: {self.position} | "\
                +f"{loc('editor.timelineInfos.beatpos')}: {self.beat_position}"

    def onscreen_print(self, reset_color:str, current_beat:float = 0.0) -> None:
        onscreen_position = self.calculate_position()
        to_print = "   \n   \n   \n"
        approached_beats = ((self.beat_position - current_beat) * self.approach_rate) + 1
        val = int(approached_beats*2)
        if val == 8:
            to_print = f"{reset_color}{self.color} - \n" \
                     + f"{reset_color}{self.color}   \n" \
                     + f"{reset_color}{self.color}   {reset_color}"
        elif val == 7:
            to_print = f"{reset_color}{self.color} -,\n" \
                     + f"{reset_color}{self.color}   \n" \
                     + f"{reset_color}{self.color}   {reset_color}"
        elif val == 6:
            to_print = f"{reset_color}{self.color} -,\n" \
                     + f"{reset_color}{self.color}  |\n" \
                     + f"{reset_color}{self.color}   {reset_color}"
        elif val == 5:
            to_print = f"{reset_color}{self.color} -,\n" \
                     + f"{reset_color}{self.color}  |\n" \
                     + f"{reset_color}{self.color}  '{reset_color}"
        elif val == 4:
            to_print = f"{reset_color}{self.color} -,\n" \
                     + f"{reset_color}{self.color}  |\n" \
                     + f"{reset_color}{self.color} -'{reset_color}"
        elif val == 3:
            to_print = f"{reset_color}{self.color} -,\n" \
                     + f"{reset_color}{self.color}  |\n" \
                     + f"{reset_color}{self.color}'-'{reset_color}"
        elif val == 2:
            to_print = f"{reset_color}{self.color} -,\n" \
                     + f"{reset_color}{self.color}| |\n" \
                     + f"{reset_color}{self.color}'-'{reset_color}"
        elif val == 1:
            to_print = f"{reset_color}{self.color},-,\n" \
                     + f"{reset_color}{self.color}| |\n" \
                     + f"{reset_color}{self.color}'-'{reset_color}"

        print_lines_at(onscreen_position.x-1, onscreen_position.y-1, to_print)
        if self.judgement:
            print_at(onscreen_position.x,
                     onscreen_position.y,
                     f"{term.bold}{JUDGEMENT_NAMES_SHORT[self.judgement['judgement']]}" +\
                     f"{reset_color}{self.color}")
        else:
            print_at(onscreen_position.x,
                     onscreen_position.y,
                     f"{reset_color}{term.bold}{self.key.upper()}{reset_color}{self.color}")

    def render(self, current_beat:float, dont_draw_list:list,
               current_time:float, reset_color:str, dont_check_judgement:list = None) -> tuple:
        calc_pos = self.calculate_position()

        if self.palette is not None:
            self.set_color_from_palette(self._palette_id, self.palette)

        remaining_beats = self.beat_position - current_beat
        remaining_time = self.time_position - current_time
        approached_beats = (remaining_beats * self.approach_rate) + 1
        if 4 > approached_beats > -0.1 and self not in dont_draw_list:
            self.onscreen_print(reset_color, current_beat)
        # print_at(calc_pos[0], calc_pos[1]+1, str(int(remaining_time)))

        if self not in dont_draw_list and (
            (remaining_time <= -0.6) or (self.judgement and remaining_time < -0.2)
        ):
            if dont_check_judgement is not None:
                if self not in dont_check_judgement:
                    dont_check_judgement.append(self)
                if not self.judgement:
                    self.checkJudgement(current_beat, True)
            print_at(calc_pos[0]-1, calc_pos[1]-1, f"{self.color}   ")
            print_at(calc_pos[0]-1, calc_pos[1],   f"{self.color}   ")
            print_at(calc_pos[0]-1, calc_pos[1]+1, f"{self.color}   ")
            dont_draw_list.append(self)

        if self in dont_draw_list and remaining_time > 0.0:
            dont_draw_list.remove(self)
        return (dont_draw_list, dont_check_judgement)
