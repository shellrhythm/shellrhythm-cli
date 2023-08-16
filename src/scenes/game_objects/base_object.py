
from ...conductor import Conductor

class GameplayObject:
    """Base gameplay object class"""
    @staticmethod
    def compute_time_position(beat_position, bpm_table) -> float:
        """Based on the beat position and a bpm table, returns the corresponding time."""
        if len(bpm_table) == 1 and isinstance(bpm_table[0],float):
            return beat_position * (60/bpm_table[0])
        else:
            return Conductor.calculate_time_sec_from_bpm_table(beat_position, bpm_table)

    def render(self, current_beat:float, dont_draw_list:list,
               bpm:float=120, dont_check_judgement:list = None) -> tuple:
        """Prints the object at its position"""
        current_beat += 0
        bpm += 0
        return (dont_draw_list, dont_check_judgement)
