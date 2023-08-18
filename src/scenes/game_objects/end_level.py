from .base_object import GameplayObject
from ...termutil import term, reset_color
from ...translate import LocaleManager

class EndLevelObject(GameplayObject):

    beat_position:float = 0.0
    time_position:float = 0.0

    def display_informations(self, note_id:int = 0) -> str:
        loc = LocaleManager.current_locale()
        return reset_color\
                +f"{loc('editor.timelineInfos.curNote')}: {note_id} | "\
                +f"{loc('editor.timelineInfos.beatpos')}: {self.beat_position}"

    def editor_timeline_icon(self, selected:bool = False):
        char = "🮕"
        output = term.grey + char + reset_color
        if selected:
            output = term.reverse + output
        return output

    def serialize(self) -> dict:
        return {
            "type": "end",
            "beatpos": [self.beat_position//4, self.beat_position%4]
        }

    def __init__(self, data, bpm_table) -> None:
        self.beat_position = data["beatpos"][0] * 4 + data["beatpos"][1]
        self.time_position = GameplayObject.compute_time_position(self.beat_position, bpm_table)
