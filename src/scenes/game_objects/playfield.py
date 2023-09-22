"""I know how this looks, but this isn't an actually usable object.
Although, it is what draws the actual playfield.
Cry about it."""
from src.constants import Vector2, Vector2i, default_size
from src.termutil import print_box, term

class Playfield:
    position:Vector2 = Vector2(0.5, 0.5)
    size:Vector2i = Vector2i(1, 1)
    offset:Vector2i = Vector2i.zero
    dont_draw_list:list = []

    def __init__(self) -> None:
        self.size.x = default_size.x
        self.size.y = default_size.y

    def top_left(self) -> Vector2i:
        out = Vector2i(
            int((term.width-self.size.x) * self.position.x),
            int((term.height-self.size.y) * self.position.y)
        )
        out += self.offset
        return out

    async def draw(self, parent_scene, notes):
        topleft = self.top_left()
        print_box(
            topleft[0]-1,
            topleft[1]-1,
            self.size.x+2,
            self.size.y+2,
            parent_scene.reset_color,1
        )

        for note in reversed(notes):
            # it probably sucks but who cares it works
            if note.__class__.__name__ == "NoteObject": 
                note.palette = parent_scene.palette
            (self.dont_draw_list, _) = note.render(
                parent_scene.conduc.current_beat,
                self.dont_draw_list,
                parent_scene.conduc.cur_time_sec,
                parent_scene.reset_color,
            )
