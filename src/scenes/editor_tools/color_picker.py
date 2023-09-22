
from src.termutil import term, print_box, print_at, color_code_from_hex,\
    hexcode_from_color_code
from src.textbox import textbox_logic
from src.constants import blockStates, Color
from src.scenes.game_objects.note import NoteObject
from src.scenes.game_objects.bg_color import BackgroundColorObject

class ColorPicker():
    enabled = False
    col = [0,0,0]
    field_selected = False
    field_content = "000000"
    field_cursor = 0
    selected_col = 0
    note_selected:NoteObject|BackgroundColorObject = None
    palette_selected:int = -1
    palette_edit_mode:bool = False
    reset_color = term.normal

    async def draw(self):
        col = term.color_rgb(
            self.col[0],
            self.col[1],
            self.col[2]
        )
        print_box(
            (term.width - 40)//2, (term.height-9)//2,
            40, 9,
            color=col,
            caption="Select color"
        )

        for (i,col) in enumerate(self.col):
            text_to_print = blockStates[8]*int(col/8) + blockStates[col%8]
            text_to_print += " "*(31-int(col/8))
            real_to_print = term.underline
            for (j,char) in enumerate(text_to_print):
                if i == 0:
                    char = term.color_rgb(j*8,0,0) + char
                if i == 1:
                    char = term.color_rgb(0,j*8,0) + char
                if i == 2:
                    char = term.color_rgb(0,0,j*8) + char
                real_to_print += char
            if i == self.selected_col:
                real_to_print += self.reset_color+"<"
            else:
                real_to_print += self.reset_color+" "
            print_at(
                (term.width - 40)//2 + 1,
                (term.height-9)//2 + (i*2+1),
                real_to_print+self.reset_color +\
                    "  " + term.reverse + str(col) +\
                    " "*(3-len(str(col))) + self.reset_color
                )

        if self.selected_col == 3:
            print_at((term.width + 8)//2, (term.height-9)//2 + 7, "<")
        print_at(
            (term.width - 8)//2-1,
            (term.height-9)//2 + 7,
            self.reset_color + "#" + term.reverse +\
                f" {self.field_content} "+self.reset_color
        )

    def setup_color(self, hexcode:str):
        self.field_content = hexcode
        self.col = color_code_from_hex(hexcode)

    def input(self, val, palette:list[Color] = None):
        if self.field_selected:
            if val.isdigit() \
            or val.lower() in ["a", "b", "c", "d", "e", "f"] \
            or val.name is not None:
                self.field_content, self.field_cursor = textbox_logic(
                    self.field_content, self.field_cursor, val)
                if len(self.field_content) == 6:
                    self.col = color_code_from_hex(self.field_content)
            if val.name == "KEY_ESCAPE" or val.name == "KEY_ENTER":
                self.field_selected = False
        else:
            if val.name in ("KEY_RIGHT", "KEY_SRIGHT") and self.selected_col < 3:
                self.col[self.selected_col] += {'KEY_RIGHT': 1, 'KEY_SRIGHT': 10}[val.name]
                self.col[self.selected_col] = min(self.col[self.selected_col], 255)
                self.field_content = hexcode_from_color_code(self.col)
            if val.name in ("KEY_LEFT", "KEY_SLEFT") and self.selected_col < 3:
                self.col[self.selected_col] -= {'KEY_LEFT': 1, 'KEY_SLEFT': 10}[val.name]
                self.col[self.selected_col] = max(self.col[self.selected_col], 0)
                self.field_content = hexcode_from_color_code(self.col)
            if val.name == "KEY_DOWN":
                self.selected_col += 1
                self.selected_col %= 4
            if val.name == "KEY_UP":
                self.selected_col -= 1
                self.selected_col %= 4
            if val.name == "KEY_ESCAPE" or val == "E":
                self.enabled = False
            if val.name == "KEY_ENTER" and self.selected_col == 3:
                self.field_selected = True
        if self.palette_edit_mode and palette is not None and self.palette_selected >= 0:
            if len(palette) > self.palette_selected:
                palette[self.palette_selected].hex_value = self.field_content
        elif self.note_selected:
            # if self.chart["notes"][self.note_selected]["type"] == "hit_object":
            #     self.chart["notes"][self.note_selected]["color"] = self.field_content
            # if self.chart["notes"][self.note_selected]["type"] == "bg_color":
            #     self.chart["notes"][self.note_selected]["color"] = "#" + self.field_content
            if isinstance(self.note_selected, NoteObject):
                self.note_selected.set_color_hex(self.field_content)
            if isinstance(self.note_selected, BackgroundColorObject):
                self.note_selected.background_col = self.field_content
        # return self.field_content
