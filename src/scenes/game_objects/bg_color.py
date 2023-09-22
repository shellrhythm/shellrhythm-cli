from .base_object import GameplayObject
from ...termutil import term, color_code_from_hex
from ...translate import LocaleManager
from ...options import OptionsManager

class BackgroundColorObject(GameplayObject):
    new_color:str = ""
    background_col:str = "n"
    foreground_col:str = "n"

    beat_position:float = 0.0
    time_position:float = 0.0

    editor_tab = 1

    def display_informations(self, reset_color:str, note_id:int = 0) -> str:
        loc = LocaleManager.current_locale()
        return reset_color\
                +f"{loc('editor.timelineInfos.curNote')}: {note_id} | "\
                +f"{loc('editor.timelineInfos.beatpos')}: {self.beat_position}"\
                +f"{loc('editor.timelineInfos.bgColor')}: {self.background_col} | "\
                +f"{loc('editor.timelineInfos.fgColor')}: {self.foreground_col} | "

    def editor_timeline_icon(self, reset_color:str, selected:bool = False):
        char = "\ue22b" if OptionsManager["nerdFont"] else "¶"
        output = self.new_color + char + reset_color
        if selected:
            output = term.underline + output
        return output

    def serialize(self) -> dict:
        back_col = "#"+self.background_col if self.background_col != "n" else ""
        fore_col = "%"+self.foreground_col if self.foreground_col != "n" else ""
        col = back_col + "/" + fore_col
        if back_col == "":
            col = fore_col
        if fore_col == "":
            col = back_col
        if col == "":
            col = "n"
        return {
            "type": "bg_color",
            "beatpos": [self.beat_position//4, self.beat_position%4],
            "color": col
        }

    def __init__(self, data, bpm_table) -> None:
        self.beat_position = data["beatpos"][0] * 4 + data["beatpos"][1]
        self.time_position = GameplayObject.compute_time_position(self.beat_position, bpm_table)
        self.new_color = ""
        for col in data["color"].split("/")[:2]:
            if col.startswith("#"): # background color
                self.background_col = col[1:]
                parsed_color = color_code_from_hex(col[1:])
                self.new_color += term.on_color_rgb(
                    parsed_color[0],
                    parsed_color[1],
                    parsed_color[2]
                )
            elif col.startswith("%"): # foreground color
                self.foreground_col = col[1:]
                parsed_color = color_code_from_hex(col[1:])
                self.new_color += term.color_rgb(
                    parsed_color[0],
                    parsed_color[1],
                    parsed_color[2]
                )
            else: # reset
                if data["color"].split("/") == 1:
                    self.new_color = term.normal
                    self.background_col = "n"
                    self.foreground_col = "n"
