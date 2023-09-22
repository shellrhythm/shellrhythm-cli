
from ...termutil import print_at, print_box, term
from ...textbox import textbox_logic

class EditorMetadata():
    enabled = False
    selected = 0
    typing = False
    typed_string = ""
    typed_cursor = 0
    sections = ["title", "artist", "author", "description"]

    async def draw(self, editor):
        print_box(0,0,40,len(self.sections) + 2,editor.reset_color,0)
        length = max(len(editor.loc('editor.metadata.'+i)) for i in self.sections)
        for (i,part) in enumerate(self.sections):
            category_name = editor.loc('editor.metadata.'+part)
            category_name += ' '*(length-len(category_name)+1)
            if i == self.selected:
                full_category_name = term.reverse + category_name
                if self.typing:
                    print_at(1,1+i,full_category_name + ": " +\
                        f"{term.underline}{self.typed_string}{editor.reset_color}")
                else:
                    print_at(1,1+i,full_category_name + ": " +\
                        f"{term.underline}{editor.chart['metadata'][part]}{editor.reset_color}")
            else:
                print_at(1,1+i,f"{category_name}: {editor.chart['metadata'][part]}")

    def handle_input(self, editor, val):
        if not self.typing:
            if val.name == "KEY_ESCAPE":
                print(term.clear)
                self.enabled = False
            if val.name == "KEY_UP":
                self.selected -= 1
                self.selected = max(self.selected, 0)
            if val.name == "KEY_DOWN":
                self.selected += 1
                self.selected = min(
                    self.selected, len(self.sections) - 1
                )
            if val.name == "KEY_ENTER":
                self.typing = True
                self.typed_string = self.chart["metadata"][
                    self.sections[self.selected]]
        else:
            if val.name == "KEY_ESCAPE":
                self.typing = False
                # self.commandString = ""
                print_at(0,term.height-2, term.clear_eol+editor.reset_color)
            elif val.name == "KEY_ENTER":
                self.typing = False
                editor.chart["metadata"][
                    self.sections[
                        self.selected
                    ]
                ] = self.typed_string
                #there was a todo here but i forgor what it was for
            else:
                if self.typed_string == "" and val.name == "KEY_BACKSPACE":
                    editor.command_line.command_mode = False
                    # print_at(0,term.height-2, term.clear_eol+self.reset_color)
                self.typed_string, self.typed_cursor = textbox_logic(
                    self.typed_string, self.typed_cursor, val)
