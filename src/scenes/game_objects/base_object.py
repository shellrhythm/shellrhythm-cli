
from ...conductor import Conductor
from .playfield import Playfield

class GameplayObject:
    """Base gameplay object class"""
    playfield:Playfield = None

    animations:list = []


    @staticmethod
    def compute_time_position(beat_position, bpm_table) -> float:
        """Based on the beat position and a bpm table, returns the corresponding time."""
        if len(bpm_table) == 1 and isinstance(bpm_table[0],float):
            return beat_position * (60/bpm_table[0])
        else:
            return Conductor.calculate_time_sec_from_bpm_table(beat_position, bpm_table)

    def display_informations(self, reset_color:str, note_id:int = 0) -> str:
        """This function is called to display informations when\
             selecting this object in the editor."""
        return reset_color+str(note_id)+": This event exists. I think."

    def editor_timeline_icon(self, reset_color:str, selected:bool = False) -> str:
        """Handles rendering the icon in the editor timeline."""
        if selected:
            return reset_color+"!"
        return reset_color+"?"

    def serialize(self) -> dict:
        """Serializes the object back into its json counterpart."""
        return {}

    def render(self, current_beat:float, dont_draw_list:list,
               current_time:float, reset_color:str, dont_check_judgement:list = None) -> tuple:
        """Prints the object at its position"""
        current_beat += 0
        current_time += 0
        reset_color += ""
        return (dont_draw_list, dont_check_judgement)
