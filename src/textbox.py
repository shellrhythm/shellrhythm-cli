import colorsys
from src.termutil import term, print_at, print_box, print_lines_at, refresh, color_text, hexcode_from_color_code

def textbox_logic(curText, cursorPos, val, autocomplete = None):
    if val.name == "KEY_BACKSPACE":
        if curText != "":
            curText = curText[:len(curText)-(cursorPos+1)] + curText[len(curText)-cursorPos:]
    elif val.name == "KEY_LEFT":
        cursorPos += 1
        if cursorPos > len(curText):
            cursorPos = len(curText)
    elif val.name == "KEY_RIGHT":
        cursorPos -= 1
        if cursorPos < 0:
            cursorPos = 0
    elif val.name == "KEY_TAB" and autocomplete is not None:
        pass
        # commandAutoPropositions = autocomplete(curText)
        # if commandAutoPropositions != []:
        # 	commandAutoMode = True

    else:
        if val.name is None:
            if cursorPos == 0:
                curText += str(val)
            else:
                curText = curText[:len(curText)-cursorPos] + str(val) + curText[len(curText)-cursorPos:]
    
    return curText, cursorPos
    
class TextEditor:
    textContent = "it's funny"
    textCursor = 0
    isSelectingText = True
    selectedColorSection = 0
    pickTheColor = [0, 0, 1]
    reset_color = term.normal
    
    async def draw(self):
        print_box(5,2, term.width-10, term.height-4)
        renText = self.textContent
        renText += " "
        renText = renText[:len(renText)-(self.textCursor+1)] + term.underline(renText[len(renText)-(self.textCursor+1)]) + renText[len(renText)-(self.textCursor):]
        if self.isSelectingText:
            print_lines_at(6,3,renText)
        else:
            colText = color_text(self.textContent)
            print_lines_at(6,3,colText)
        print_at(6,{True:term.height-12, False:8}[self.isSelectingText],"-"*(term.width-12))
        
        # THE COLOR PICKER
        normalizedcolor = colorsys.hsv_to_rgb(self.pickTheColor[0], self.pickTheColor[1], self.pickTheColor[2])
        color = [int(i*255) for i in normalizedcolor]
        for i in range(term.width - 12):
            colorH = colorsys.hsv_to_rgb(i/(term.width-12), self.pickTheColor[1], self.pickTheColor[2])
            colorS = colorsys.hsv_to_rgb(self.pickTheColor[0], i/(term.width-12), self.pickTheColor[2])
            colorV = colorsys.hsv_to_rgb(self.pickTheColor[0], self.pickTheColor[1], i/(term.width-12))
            print_at(6+i,{True:term.height-11, False:9}[self.isSelectingText], term.on_color_rgb(
                int(colorH[0]*255), 
                int(colorH[1]*255), 
                int(colorH[2]*255)) + " ")
            print_at(6+i,{True:term.height-9, False:11}[self.isSelectingText], term.on_color_rgb(
                int(colorS[0]*255), 
                int(colorS[1]*255), 
                int(colorS[2]*255)) + " ")
            print_at(6+i,{True:term.height-7, False:13}[self.isSelectingText], term.on_color_rgb(
                int(colorV[0]*255), 
                int(colorV[1]*255), 
                int(colorV[2]*255)) + " ")
        print_at(int(self.pickTheColor[0]*(term.width-13)) + 6, {True:term.height-10, False:10}[self.isSelectingText], term.color_rgb(int(color[0]), int(color[1]), int(color[2])) + "^")
        print_at(int(self.pickTheColor[1]*(term.width-13)) + 6, {True:term.height-8, False:12}[self.isSelectingText], term.color_rgb(int(color[0]), int(color[1]), int(color[2])) + "^")
        print_at(int(self.pickTheColor[2]*(term.width-13)) + 6, {True:term.height-6, False:14}[self.isSelectingText], term.color_rgb(int(color[0]), int(color[1]), int(color[2])) + "^")
        print_at(
            6,
            {True:term.height-4, False:16}[self.isSelectingText],
            term.color_rgb(color[0], color[1], color[2]) + term.bold + term.reverse + \
                term.center("#" + hexcode_from_color_code(color), term.width - 12) + self.reset_color
        )

    def handle_input(self, val):
        if val.name == "KEY_TAB":
            self.isSelectingText = not self.isSelectingText
        
        if self.isSelectingText:
            if val.name == None and val:
                self.textContent = self.textContent[:len(self.textContent)-(self.textCursor)] + val + self.textContent[len(self.textContent)-(self.textCursor):]
            if val.name == "KEY_BACKSPACE":
                self.textContent = self.textContent[:len(self.textContent)-(self.textCursor+1)] + self.textContent[len(self.textContent)-(self.textCursor):]
            if val.name == "KEY_DELETE":
                self.textContent = self.textContent[:len(self.textContent)-(self.textCursor)] + self.textContent[len(self.textContent)-(self.textCursor-1):]
                self.textCursor -= 1
                self.textCursor = max(self.textCursor, 0)
            if val.name == "KEY_ENTER":
                self.textContent = self.textContent[:len(self.textContent)-(self.textCursor)] + "\n" + self.textContent[len(self.textContent)-(self.textCursor):]
            if val.name == "KEY_LEFT":
                self.textCursor += 1
                self.textCursor = min(self.textCursor, len(self.textContent))
            if val.name == "KEY_RIGHT":
                self.textCursor -= 1
                self.textCursor = max(self.textCursor, 0)
        else:
            multiplier = {0:360, 1:100, 2:100}[self.selectedColorSection]
            if val.name in ("KEY_RIGHT", "KEY_SRIGHT"):
                self.pickTheColor[self.selectedColorSection] += {"KEY_RIGHT": 1/multiplier, "KEY_SRIGHT": 10/multiplier}[val.name]
                self.pickTheColor[self.selectedColorSection] = min(self.pickTheColor[self.selectedColorSection], 1.0)
                    
            if val.name in ("KEY_LEFT", "KEY_SLEFT"):
                self.pickTheColor[self.selectedColorSection] -= {"KEY_LEFT": 1/multiplier, "KEY_SLEFT": 10/multiplier}[val.name]
                self.pickTheColor[self.selectedColorSection] = max(self.pickTheColor[self.selectedColorSection], 0.0)

            if val.name == "KEY_UP":
                self.selectedColorSection -= 1
                self.selectedColorSection %= 3
            if val.name == "KEY_DOWN":
                self.selectedColorSection += 1
                self.selectedColorSection %= 3

            if val.name == "KEY_ENTER":
                normalizedcolor = colorsys.hsv_to_rgb(self.pickTheColor[0], self.pickTheColor[1], self.pickTheColor[2])
                color = [int(i*255) for i in normalizedcolor]
                colStr = "{cf " + hexcode_from_color_code(color) + "}"
                self.textContent = self.textContent[:len(self.textContent)-(self.textCursor)] + colStr + self.textContent[len(self.textContent)-(self.textCursor):]
            if val.name == "KEY_SENTER":
                normalizedcolor = colorsys.hsv_to_rgb(self.pickTheColor[0], self.pickTheColor[1], self.pickTheColor[2])
                color = [int(i*255) for i in normalizedcolor]
                colStr = "{cb " + hexcode_from_color_code(color) + "}"
                self.textContent = self.textContent[:len(self.textContent)-(self.textCursor)] + colStr + self.textContent[len(self.textContent)-(self.textCursor):]


    def __init__(self) -> None:
        pass

if __name__ == "__main__":
    edit = TextEditor()
    with term.fullscreen(), term.hidden_cursor(), term.raw():
        while 1:
            edit.draw()
            refresh()

            the_val = ''
            the_val = term.inkey(timeout=1/120, esc_delay=0)
            edit.handle_input(the_val)