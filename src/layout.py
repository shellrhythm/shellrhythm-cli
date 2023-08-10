import os
from src.termutil import print_at, print_lines_at, term, reset_color
from src.translate import LocaleManager
from src.scenes import BaseScene

class LayoutManager:
    layouts:dict = {}
    layoutNames:list = []

    @staticmethod
    def setup():
        layout_files = [f.name for f in os.scandir("./layout") if f.is_file()]
        for (i, file_name) in enumerate(layout_files):
            print(f"Loading layout \"{file_name}\"... ({i+1}/{len(layout_files)})")
            file = open("./layout/" + file_name, encoding="utf8")
            LayoutManager.layouts[file_name] = list(file.read().replace('\n', ''))
            LayoutManager.layoutNames.append(file_name)
            file.close()

    @staticmethod
    def __class_getitem__(key):
        return LayoutManager.layouts[key]

class LayoutCreator(BaseScene):
    turnOff = False
    selectedKey = 0
    changingKey = False
    layoutName = "custom"
    layout = ["╳" for _ in range(30)]

    loc = LocaleManager.current_locale

    def save(self):
        if "╳" in self.layout:
            return False, "Empty keys!"
        if len(list(set(self.layout))) != len(self.layout):
            return False, "Duplicate keys!"
        if not os.path.exists("./layout/" + self.layoutName):
            f = open("./layout/" + self.layoutName, "x", encoding="utf8")
        else:
            f = open("./layout/" + self.layoutName, "w", encoding="utf8")
        text = "\n".join(["".join(self.layout[i*10:(i+1)*10]) for i in range(3)])
        f.write(text)
        f.close()
        return True, ""

    def draw(self):
        # this mess is to generate a grid
        text = f"┌───{'┬───'*9}┐\n" + "".join(
            ["".join([f"│ {key} " for key in self.layout][10*i:10*(i+1)]) + f"│\n├───{'┼───'*9}┤\n" for i in range(2)]
        ) + "".join(
            [f"│ {key} " for key in self.layout][20:30]
        ) + f"│\n└───{'┴───'*9}┘\n"
        print_lines_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2), int((term.height-len(text.split("\n")))*0.5), text)
        print_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2) + 1 + (self.selectedKey%10)*4, int((term.height-len(text.split("\n")))*0.5) + 1 + (self.selectedKey//10)*2, term.reverse + f" {self.layout[self.selectedKey]} " + reset_color)
        if self.changingKey:
            text_change_key = self.loc("")
            print_at(int((term.width-len(text_change_key))*0.5), int(term.height*0.5) + 6, text_change_key)
        else:
            print_at(0, int(term.height*0.5) + 6, term.clear_eol)

    def handle_input(self):
        val = ''
        val = term.inkey(timeout=1/120, esc_delay=0)

        if val:
            if val.name == "KEY_ESCAPE":
                if not self.changingKey:
                    self.turn_off = True
                else:
                    self.changingKey = False
            if val.name == "KEY_LEFT":
                self.selectedKey -= 1
            if val.name == "KEY_RIGHT":
                self.selectedKey += 1
            if val.name == "KEY_UP":
                self.selectedKey -= 10
            if val.name == "KEY_DOWN":
                self.selectedKey += 10
            self.selectedKey %= 30
            if val.name == "KEY_ENTER":
                self.changingKey = True
            if val.name is None and self.changingKey:
                if str(val) in self.layout:
                    self.layout[self.layout.index(str(val))] = "╳"
                self.layout[self.selectedKey] = str(val)
                self.selectedKey += 1
                if self.selectedKey >= 30:
                    self.changingKey = False
                self.selectedKey %= 30
                    
    def loop(self, layout = None):
        if layout is not None:
            self.layout = layout
        super().loop()
    
        result, code = self.save()
        if __name__ == "__main__":
            if not result:
                print(term.on_yellow + "Could not save: " + code + reset_color)
        else:
            return result, code

    def __init__(self):
        pass
if __name__ == "__main__":
    print("Nope, sorry...")
    # layout = LayoutCreator()
    # layout.loop()