import os
from src.termutil import print_at, print_lines_at, term
from src.scenes.base_scene import BaseScene
from src.scene_manager import SceneManager
from src.layout import LayoutManager

class LayoutCreator(BaseScene):
    turnOff = False
    selected_key = 0
    changing_key = False
    current_error = ""
    layoutName = "custom"
    layout = ["╳" for _ in range(30)]

    def save(self):
        """Checks if layout can be saved, then saves it.
        Returns two values: a boolean representing whether the save was successful,
        and a string representing the error message (empty if no error)"""
        if "╳" in self.layout:
            return False, "Empty keys!"
        if len(list(set(self.layout))) != len(self.layout):
            return False, "Duplicate keys!"
        if not os.path.exists("./layout/" + self.layoutName):
            file = open("./layout/" + self.layoutName, "x", encoding="utf8")
        else:
            file = open("./layout/" + self.layoutName, "w", encoding="utf8")
        text = "\n".join(["".join(self.layout[i*10:(i+1)*10]) for i in range(3)])
        file.write(text)
        file.close()
        return True, ""

    async def draw(self):
        # this mess is to generate a grid
        text = f"┌───{'┬───'*9}┐\n" + "".join(
            ["".join([f"│ {key} " for key in self.layout][10*i:10*(i+1)]) + \
             f"│\n├───{'┼───'*9}┤\n" for i in range(2)]
        ) + "".join(
            [f"│ {key} " for key in self.layout][20:30]
        ) + f"│\n└───{'┴───'*9}┘\n"
        print_lines_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2),
                       int((term.height-len(text.split("\n")))*0.5), text
                    )
        print_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2) + 1 + (self.selected_key%10)*4,
                 int((term.height-len(text.split("\n")))*0.5) + 1 + (self.selected_key//10)*2,
                 term.reverse + f" {self.layout[self.selected_key]} " + self.reset_color
                )
        if self.changing_key:
            text_change_key = self.loc("layout.newKey")
            print_at(
                0,
                int(term.height*0.5) + 6,
                term.center(text_change_key)
            )
        print_at(0, int(term.height*0.5) - 8, term.center(self.current_error))

    async def handle_input(self):
        val = ''
        val = term.inkey(timeout=1/120, esc_delay=0)

        if val:
            if val.name == "KEY_ESCAPE":
                if not self.changing_key:
                    result, code = self.save()
                    if result:
                        LayoutManager.setup()
                        SceneManager.change_scene("Options")
                    else:
                        self.current_error = code
                else:
                    self.changing_key = False
            else:
                self.current_error = ""


            if val.name == "KEY_LEFT":
                self.selected_key -= 1
            if val.name == "KEY_RIGHT":
                self.selected_key += 1
            if val.name == "KEY_UP":
                self.selected_key -= 10
            if val.name == "KEY_DOWN":
                self.selected_key += 10
            self.selected_key %= 30
            if val.name == "KEY_ENTER":
                self.changing_key = True
            if val.name is None and self.changing_key:
                if str(val) in self.layout:
                    self.layout[self.layout.index(str(val))] = "╳"
                self.layout[self.selected_key] = str(val)
                self.selected_key += 1
                if self.selected_key >= 30:
                    self.changing_key = False
                self.selected_key %= 30
