
from ...termutil import print_at, print_box, term

class KeyPanel():
    enabled = False
    key = -1
    selected = -1 #Note: use -1 when creating a new note
    catch = False

    async def draw(self, editor, toptext = None, current_key = 0):
        width = max(len(toptext) + 2, 40)
        height = 7
        print_box(
            int((term.width-width)*0.5),
            int((term.height-height)*0.5),
            width,
            height,
            style=1
        )
        print_at(int((term.width-len(toptext))*0.5), int((term.height-height)*0.5)+1, toptext)
        if current_key > 0 and current_key < 30:
            print_at(int(term.width*0.5)-1, int(term.height *0.5),
                     term.reverse + f" {editor.layout[current_key]} " + editor.reset_color)
        else:
            print_at(int(term.width*0.5)-1, int(term.height *0.5),
                     term.reverse + "   " + editor.reset_color)

    def input(self, editor, val):
        if val.name == "KEY_ESCAPE":
            self.enabled = False
        elif val.name == "KEY_ENTER":
            if self.key != -1:
                if self.selected == -1:
                    if self.catch:
                        editor.selected_note = editor.create_catch(
                            editor.conduc.current_beat, self.key)
                    else:
                        editor.selected_note = editor.create_note(
                            editor.conduc.current_beat, self.key)
                else:
                    editor.notes[self.selected].key_index = self.key
                self.enabled = False
                self.selected = -1
                self.key = -1
        elif val:
            if str(val) in editor.layout:
                self.key = editor.layout.index(str(val))
