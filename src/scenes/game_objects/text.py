from src.scenes.game_objects.base_object import GameplayObject
from src.constants import\
    CENTER, LEFT, UP_LEFT, UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT,\
    ALIGN_CENTER, ALIGN_LEFT, ALIGN_RIGHT, Vector2i, default_size
from src.termutil import color_text, print_at, term

class TextObject(GameplayObject):
    beat_position = 0.0
    duration = 0.0
    text = ""
    offset = Vector2i()
    anchor = CENTER
    align = ALIGN_CENTER
    renderOffset = Vector2i()

    def __init__(self, data, bpm_table) -> None:
        super().__init__()
        self.text = data["text"]
        self.anchor = data["anchor"]
        self.align = data["align"]
        self.offset = Vector2i(data["offset"][0], data["offset"][1])
        self.duration = data["length"]
        self.beat_position = data["beatpos"][0] * 4 + data["beatpos"][1]
        self.time_position = GameplayObject.compute_time_position(self.beat_position, bpm_table)

    def renderText(self, beat = 0.0, clear=False):
        #calculate position
        calculatedPosition = [0,0]

        rendered_text = color_text(self.text, beat)

        if self.anchor == CENTER:
            calculatedPosition[0] = int(default_size[0]/2 + self.offset[0])
            calculatedPosition[1] = int(default_size[1]/2 + self.offset[1])
        elif self.anchor == LEFT:
            calculatedPosition[0] = int(self.offset[0])
            calculatedPosition[1] = int(default_size[1]/2 + self.offset[1])
        elif self.anchor == DOWN:
            calculatedPosition[0] = int(default_size[0]/2 + self.offset[0])
            calculatedPosition[1] = int(default_size[1] + self.offset[1])
        elif self.anchor == UP:
            calculatedPosition[0] = int(default_size[0]/2 + self.offset[0])
            calculatedPosition[1] = int(self.offset[1])
        elif self.anchor == RIGHT:
            calculatedPosition[0] = int(default_size[0] + self.offset[0])
            calculatedPosition[1] = int(default_size[1]/2 + self.offset[1])
        elif self.anchor == DOWN_LEFT:
            calculatedPosition[0] = int(self.offset[0])
            calculatedPosition[1] = int(default_size[1] + self.offset[1])
        elif self.anchor == DOWN_RIGHT:
            calculatedPosition[0] = int(default_size[0] + self.offset[0])
            calculatedPosition[1] = int(default_size[1] + self.offset[1])
        elif self.anchor == UP_LEFT:
            calculatedPosition[0] = int(self.offset[0])
            calculatedPosition[1] = int(self.offset[1])
        elif self.anchor == UP_RIGHT:
            calculatedPosition[0] = int(default_size[0] + self.offset[0])
            calculatedPosition[1] = int(self.offset[1])

        #check for aligns
        if self.align == ALIGN_LEFT:
            pass
        elif self.align == ALIGN_CENTER:
            calculatedPosition[0] -= int(len(term.strip_seqs(rendered_text))*0.5)
        elif self.align == ALIGN_RIGHT:
            calculatedPosition[0] -= len(term.strip_seqs(rendered_text))-1

        topleft = [
            int((term.width-default_size[0]) * 0.5),
            int((term.height-default_size[1]) * 0.5)
        ]

        if clear:
            rendered_text = " "*len(term.strip_seqs(rendered_text))
        print_at(calculatedPosition[0] + topleft[0], 
                 calculatedPosition[1] + topleft[1], 
                 rendered_text
                )

    def render(self, current_beat:float, dont_draw_list:list,
               bpm:float=120, dont_check_judgement:list = None) -> tuple:
        render_at = self.beat_position - current_beat
        stop_at = render_at + self.duration
        if self not in dont_draw_list:
            if render_at <= 0:
                if stop_at > 0:
                    self.renderText(current_beat, False)
                else:
                    self.renderText(current_beat, True)
                    dont_draw_list.append(self)
        return (dont_draw_list, dont_check_judgement)
    