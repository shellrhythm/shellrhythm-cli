import json
import copy
import os
import shutil
from zipfile import ZipFile
from blessed import Terminal
from pybass3 import Song

from src.scenes.game import Game
from src.conductor import Conductor
from src.options import OptionsManager
from src.constants import colors, ALIGN_CENTER, CENTER, default_size
from src.termutil import term, reset_color, print_at, print_lines_at, print_box, print_column,\
    hexcode_from_color_code, color_code_from_hex, set_reset_color, framerate
from src.scenes.base_scene import BaseScene
from src.translate import Locale
from src.textbox import textbox_logic, TextEditor
from src.filebrowser import FileBrowser
from src.calibration import Calibration
from src.layout import LayoutManager
from src.scenes.game_objects.note import NoteObject
from src.scenes.game_objects.text import TextObject
from src.scenes.game_objects.base_object import GameplayObject

term = Terminal()

blockStates = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

# WARNING TO WHOEVER WANTS TO MOD THIS FILE:
# good luck

class Editor(BaseScene):

    #Basics
    chart = {}
    notes:list[GameplayObject] = []
    keys = []
    localConduc = Conductor()
    playtest = False
    beatSound = Song("assets/clap.wav")
    dont_draw_list = []
    dontBeat = [] #Notes that have already got their beatsound played

    #Saving
    needsSaving = False
    fileLocation = ""

    #Notes selected
    selectedNote = 0
    endNote = -1

    #Command mode
    commandMode = False
    commandString = ""
    commandSelectPos = 0
    commandAutoMode = False
    commandAutoPropositions = []
    commandFooterMessage = ""
    commandFooterEnabled = False
    commandHistory = []
    commandHistoryCursor = 0
    cachedCommand = ""

    #Editor settings
    snap = 4
    selectedSnap = 2
    snapPossible = [1, 2, 4, 8, 16, 3, 6, 12]
    layout = []
    layoutname = "qwerty"

    #Key panel
    keyPanelEnabled = False
    keyPanelKey = -1
    keyPanelSelected = -1 #Note: use -1 when creating a new note
    keyPanelJustDisabled = False

    pauseMenu = [
        "resume",
        "playtest",
        "song",
        "addimage",
        "metadata",
        "save",
        "export",
        "quit",
    ]
    pauseMenuEnabled = False
    pauseMenuSelected = 0

    #Locale
    loc:Locale = Locale("en")

    #Note settings
    noteMenu = {
        "hit_object":[
            {"name": "key", "keybind": 20},
            {"name": "color", "keybind": 21},
            {"name": "delete", "keybind": 22},
        ],
        "text":[
            {"name": "text", "keybind": 20},
            {"name": "color", "keybind": 21},
            {"name": "anchor", "keybind": 22},
            {"name": "delete", "keybind": 23},
        ]
    }

    #Metadata settings
    metadataParts = ["title", "artist", "author", "description"]
    metadataMenuEnabled = False
    metadataMenuSelection = 0
    metadataTyping = False
    metadataString = ""
    metadataTypingCursor = 0

    #File Browser
    fileBrwsr:FileBrowser = FileBrowser()

    #Calibration
    calib:Calibration = Calibration("CalibrationSong")

    #Playtest
    game:Game = Game()

    options = {
        "nerdFont": True,
        "bypassSize": True,
    }

    #Text edition
    textEdit = TextEditor()
    isTextEditing = False
    textobjectedited = -1

    background_changes = []
    def get_background(self, at_beat):
        out = term.normal
        for i in self.background_changes:
            if i[0] <= at_beat:
                out = i[1]
            else:
                break
        return out

    def set_background(self, background):
        colors[0] = background
        set_reset_color(background)

    def autocomplete(self, command = ""):
        output = []
        if command != "":
            # return list of commands uhhh
            # commandSplit = command.split(" ")
            pass

        #where do i even begin

        return output

    
    def export(self):
        file_paths = [] #this is where the paths go
    
        # crawling through directory and subdirectories
        for _, _the_secondth, files in os.walk("./charts/" + self.chart["foldername"]):
            for filename in files:
                #gimme da full path plz :3
                filepath = filename
                file_paths.append(filepath)
        
        # actual exporting
        with ZipFile("./charts/" + self.chart["foldername"] + '.zip','w') as zip_file:
            # add in the files
            for file in file_paths:
                zip_file.write("./charts/" + self.chart["foldername"] + "/" + file, file)

    def setupMap(self):
        self.chart = {
            "formatVersion": 1,
            "sound": None,
            "foldername": "",
            "icon": {
                "img": "",
                "txt": ""
            },
            "bpm": 120,
            "bpmChanges": [],
            "offset": 0,
            "metadata": {
                "title": "",
                "artist": "",
                "author": "",
                "description": ""
            },
            "approachRate": 1,
            "difficulty": 0,
            "notes": []
        }
        self.notes = []
        self.endNote = -1
    
    def create_note(self, atPos, key):
        print(term.clear)
        if "notes" in self.chart:
            newNote = {
                "type": "hit_object",
                "beatpos": [
                    int(atPos//4),
                    round(atPos%4, 5)
                ],
                "key": key,
                "screenpos": [
                    0.5,
                    0.5
                ],
                "color": 0
            }
            self.chart["notes"].append(newNote)
            self.chart["notes"] = sorted(self.chart["notes"], key=lambda d: d['beatpos'][0]*4+d['beatpos'][1])
            if "end" in [note["type"] for note in self.chart["notes"]]:
                self.endNote = [note["type"] for note in self.chart["notes"]].index("end")
            note_obj = NoteObject(newNote, self.conduc.bpmChanges, LayoutManager.layouts[LayoutManager.layoutNames[0]])
            self.notes.append(note_obj)
            return self.chart["notes"].index(newNote)
            
    def create_text(self, atPos = 0, lasts = 1, text = "", anchor = CENTER, align = ALIGN_CENTER):
        print(term.clear)
        if "notes" in self.chart:
            newNote = {
                "type": "text",
                "beatpos": [
                    int(atPos//4),
                    round(atPos%4, 5)
                ],
                "length": lasts,
                "text": text,
                "anchor": anchor,
                "align": align,
                "offset": [0,0],
            }
            self.chart["notes"].append(newNote)
            self.chart["notes"] = sorted(self.chart["notes"], key=lambda d: d['beatpos'][0]*4+d['beatpos'][1])
            if "end" in [note["type"] for note in self.chart["notes"]]:
                self.endNote = [note["type"] for note in self.chart["notes"]].index("end")
            note_obj = TextObject(newNote, self.conduc.bpmChanges)
            self.notes.append(note_obj)

    colorPickerEnabled = False
    colorPickerColor = [0,0,0]
    colorPickerFieldSelected = False
    colorPickerFieldContent = "000000"
    colorPickerFieldCursor = 0
    colorPickerSelectedCol = 0
    colorPickerNoteSelected = -1
    def draw_colorPicker(self):
        print_box((term.width - 40)//2, (term.height-9)//2, 40, 9, color=term.color_rgb(self.colorPickerColor[0], self.colorPickerColor[1], self.colorPickerColor[2]), caption="Select color")
        
        for (i,col) in enumerate(self.colorPickerColor):
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
            if i == self.colorPickerSelectedCol:
                real_to_print += reset_color+"<"
            else:
                real_to_print += reset_color+" "
            print_at((term.width - 40)//2 + 1, (term.height-9)//2 + (i*2+1), real_to_print+reset_color + "  " + term.reverse + str(col) + " "*(3-len(str(col))) + reset_color)

        if self.colorPickerSelectedCol == 3:
            print_at((term.width + 8)//2, (term.height-9)//2 + 7, "<")
        print_at((term.width - 8)//2-1, (term.height-9)//2 + 7, reset_color + "#" + term.reverse + f" {self.colorPickerFieldContent} "+reset_color)

    def input_colorPicker(self, val):
        if self.colorPickerFieldSelected:
            if val.isdigit() or val.lower() in ["a", "b", "c", "d", "e", "f"] or val.name is not None:
                self.colorPickerFieldContent, self.colorPickerFieldCursor = textbox_logic(self.colorPickerFieldContent, self.colorPickerFieldCursor, val)
                if len(self.colorPickerFieldContent) == 6:
                    self.colorPickerColor = color_code_from_hex(self.colorPickerFieldContent)
            if val.name == "KEY_ESCAPE" or val.name == "KEY_ENTER":
                self.colorPickerFieldSelected = False
        else:
            if val.name in ("KEY_RIGHT", "KEY_SRIGHT") and self.colorPickerSelectedCol < 3:
                self.colorPickerColor[self.colorPickerSelectedCol] += {'KEY_RIGHT': 1, 'KEY_SRIGHT': 10}[val.name]
                self.colorPickerColor[self.colorPickerSelectedCol] = min(self.colorPickerColor[self.colorPickerSelectedCol], 255)
                self.colorPickerFieldContent = hexcode_from_color_code(self.colorPickerColor)
            if val.name in ("KEY_LEFT", "KEY_SLEFT") and self.colorPickerSelectedCol < 3:
                self.colorPickerColor[self.colorPickerSelectedCol] -= {'KEY_LEFT': 1, 'KEY_SLEFT': 10}[val.name]
                self.colorPickerColor[self.colorPickerSelectedCol] = max(self.colorPickerColor[self.colorPickerSelectedCol], 0)
                self.colorPickerFieldContent = hexcode_from_color_code(self.colorPickerColor)
            if val.name == "KEY_DOWN":
                self.colorPickerSelectedCol += 1
                self.colorPickerSelectedCol %= 4
            if val.name == "KEY_UP":
                self.colorPickerSelectedCol -= 1
                self.colorPickerSelectedCol %= 4
            if val.name == "KEY_ESCAPE" or val == "E":
                self.colorPickerEnabled = False
            if val.name == "KEY_ENTER" and self.colorPickerSelectedCol == 3:
                self.colorPickerFieldSelected = True
        if self.colorPickerNoteSelected > -1:
            if self.chart["notes"][self.colorPickerNoteSelected]["type"] == "hit_object":
                self.chart["notes"][self.colorPickerNoteSelected]["color"] = self.colorPickerFieldContent
            if self.chart["notes"][self.colorPickerNoteSelected]["type"] == "bg_color":
                self.chart["notes"][self.colorPickerNoteSelected]["color"] = "#" + self.colorPickerFieldContent

    delConfirmEnabled = False
    delConfirmObj = -1
    def draw_confirmDeletion(self):
        confirm_text = self.loc("editor.deleteConfirmPrompt")
        confirm_options = "[Y/Return] Yes    [N/Esc] No"
        print_box((term.width - 30)//2, (term.height - 5)//2, 30, 5)
        print_at((term.width - len(confirm_text))//2, (term.height - 5)//2+1, confirm_text)
        print_at((term.width - len(confirm_options))//2, (term.height - 5)//2+3, confirm_options)

    def input_confirmDeletion(self, val):
        if val == "y" or val.name == "KEY_ENTER":
            self.chart["notes"].remove(self.chart["notes"][self.delConfirmObj])
            self.delConfirmEnabled = False
        elif val == "n" or val.name == "KEY_ESCAPE":
            self.delConfirmEnabled = False
        

    def set_end_note(self, atPos):
        if self.endNote == -1:
            if "end" in [note["type"] for note in self.chart["notes"]]:
                self.endNote = [note["type"] for note in self.chart["notes"]].index("end")
            else:
                newNote = {
                    "type": "end",
                    "beatpos": [
                        int(atPos//4),
                        round(atPos%4, 5)
                    ]
                }
                self.chart["notes"].append(newNote)
                self.endNote = len(self.chart["notes"])-1
        else:
            self.chart["notes"][self.endNote]["beatpos"] = [int(atPos//4), round(atPos%4, 5)]

    def draw_pauseMenu(self):
        width = max(len(self.loc("editor.pause." + option)) for option in self.pauseMenu)+4
        print_box((term.width-width)//2 - 1, (term.height//2) - len(self.pauseMenu) - 1, width+2, len(self.pauseMenu) * 2 + 1)
        for (i,optn) in enumerate(self.pauseMenu):
            if i == self.pauseMenuSelected:
                print_at(
                    (term.width-width)//2,
                    (term.height//2) - len(self.pauseMenu) + i*2,
                    term.reverse + term.center(self.loc("editor.pause." + optn), width)\
                        + reset_color
                )
            else:
                print_at(
                    (term.width-width)//2,
                    (term.height//2) - len(self.pauseMenu) + i*2,
                    term.center(self.loc("editor.pause." + optn), width)
                )
            if i != len(self.pauseMenu)-1:
                print_at(
                    (term.width-width)//2,
                    (term.height//2) - len(self.pauseMenu) + i*2 + 1,
                    " "*width
                )

    def run_pauseMenu(self, option):
        #what made you think this was a good idea
        #- #Guigui, to himself, 16/2/2023 (DD/MM/YYYY the obviously better formatting)
        if option == 0:
            #resume
            self.pauseMenuEnabled = False
            print(term.clear)
        if option == 1:
            #playtest
            self.game.play(self.chart, self.layoutname, self.options)
            self.pauseMenuEnabled = False
        if option == 2:
            self.run_command("song") #uh yeah
        if option == 3:
            #change image
            self.fileBrwsr.fileExtFilter = "(?:\\.png$)|(?:\\.jpeg$)|(?:\\.webp$)|(?:\\.jpg$)|(?:\\.apng$)|(?:\\.gif$)"
            self.fileBrwsr.load_folder(os.getcwd())
            self.fileBrwsr.caption = "Select an image"
            self.fileBrwsr.turnOff = False
            imageFileLocation = self.fileBrwsr.loop()
            try:
                shutil.copyfile(imageFileLocation, f"./charts/{self.chart['foldername']}/{imageFileLocation.split('/')[-1]}")
            except shutil.SameFileError:
                pass
            self.chart["icon"]["img"] = imageFileLocation.split("/")[-1]
        if option == 4:
            #metadata
            self.metadataMenuEnabled = True
            self.pauseMenuEnabled = False
            print(term.clear)
        if option == 5:
            #save
            self.run_command("w") #huge W
            self.pauseMenuEnabled = False
        if option == 6:
            #export
            self.run_command("w") #huge W
            self.pauseMenuEnabled = False
            self.export()
            print(term.clear)
            print_at(0,term.height-2, term.on_green+f"Exported successfully to ./charts/{self.chart['foldername']}.zip" +term.clear_eol+reset_color)
        if option == 7:
            #quit
            self.run_command("q")
            self.pauseMenuEnabled = False

    def run_noteSettings(self, note, noteID, option):
        if note["type"] == "hit_object":
            if option == 0:
                self.keyPanelEnabled = True
                self.keyPanelSelected = noteID
                self.keyPanelKey = note["key"]
                return True
            elif option == 1:
                #TODO better color picker
                note["color"] += 1
                note["color"] %= len(colors)
                return False
            elif option == 2:
                self.chart["notes"].remove(note)
                return True
        elif note["type"] == "text":
            if option == 0:
                self.isTextEditing = True
                self.textEdit.textContent = note["text"]
                self.textobjectedited = noteID
                return True
            elif option == 1:
                #TODO better color picker
                note["color"] += 1
                note["color"] %= len(colors)
                return False
            elif option == 2:
                note["anchor"] += 1
                note["anchor"] %= 9
            elif option == 3:
                self.chart["notes"].remove(note)
                return True

    def draw_changeKeyPanel(self, toptext = None, curKey = 0):
        width = 40
        height = 7
        if toptext != None:
            print_at(int((term.width-width)*0.5), int((term.height-height)*0.5), "-"*width)
            print_at(int((term.width-width)*0.5), int((term.height+height)*0.5), "-"*width)
            print_column(int((term.width-width)*0.5), int((term.height-height)*0.5)+1, height, "|")
            print_column(int((term.width+width)*0.5), int((term.height-height)*0.5)+1, height, "|")
            print_at(int((term.width-len(toptext))*0.5), int((term.height-height)*0.5)+1, toptext)
            if curKey > 0 and curKey < 30:
                print_at(int(term.width*0.5)-1, int(term.height *0.5),
                         term.reverse + f" {self.layout[curKey]} " + reset_color)
            else:
                print_at(int(term.width*0.5)-1, int(term.height *0.5),
                         term.reverse + "   " + reset_color)
        else:
            print_lines_at(int((term.width-width)*0.5), int((term.height-height)*0.5), (" "*(width+1)+"\n")*(height+1))

    def load_chart(self, chart_name, file = "data"):
        self.fileLocation = f"./charts/{chart_name}/{file}.json"
        if os.path.exists(self.fileLocation):
            print(term.clear)
            file_data = open(f"./charts/{chart_name}/{file}.json", encoding="utf8")
            self.chart = json.load(file_data)
            file_data.close()

            self.localConduc.loadsong(self.chart)
            return True
        else:
            return False

    cheatsheet = {
        "basic": {
            "playtest": "Space",
            "cheatsheet": "Tab",
            "pauseMenu": "Escape",
            "goToBeginning": "Home",
            "moveCursor": "←/→",
            "placeNote": "Z",
            "setEndPoint": "Shift+Z",
            "metronome": "T",
            "changeSnap": "1/2",
            "commandMode": ":",
        },
        "objects": {
            "selectNextObject": "↓/↑",
            "moveObjectOnTimeline": "U/I",
            "moveObjectOnScreen": "H/J/K/L",
            "duplicateObject": "d"
        },
        "note": {
            "changeKey": "E",
            "changeColor": "X / Shift+X",
            "changeCustomColor": "Shift+E",
            "delete": "Delete"
        },
        "text": {
            "changeText": "E",
            "changeTextColor": "X",
            "changeTextAnchor": "C",
            "delete": "Delete"
        },
        "command": {
            "cheatsheet": "Tab",
            "leaveCommand": "Escape",
            "runCommand": "Enter",

            # "commandfunction": ["command", [Argument1Needed, "ArgumentName", "Prefix"]]
            "[line_0]": " ",
            "save": [":w", [False, "FilePath"]],
            "quit": [":q"],
            "saveAndQuit": [":wq", [False, "FilePath"]],
            "openExistingChart": [":o", [True, "ChartID"]],
            "setSong": [":song", [False, "SongLocation"]],
            "setBPM": [":bpm", [True, "NewBPM"]],
            "setOffset": [":off", [False, "NewOffset"]],
            "setApproachRate": [":ar", [True, "NewAR"]],
            "setDiff": [":diff", [True, "NewDiff"]],
            "setMetadata": [":mt", [True, "MetadataField"], [True, "Value"]],

            "[line_1]": " ",
            "placeNote": [":p", [False, "NoteID"]],
            "createText": [":t", [True, "TextContent"]],
            "changeSnap": [":s", [True, "Snap"]],
            "moveToPos": [":m", [True, "Position"]],
            "moveBy": [":m", [True, "ByAmount", "~"]],
            "copyNotes": [":cp", [True, "XX-YY Range"], [True, "ByNBeats"]],
            "changeNoteColor": [":c", [True, "NewColor"]],

            "[line_2]": " ",
            "selectNote": [":sel", [True, "SelectNote"]],
            "deleteNote": [":del", [False, "NoteToDelete"]],

        }
    }
    cheatsheetEnabled = False
    hasCheatsheetBeenSeen = False
    howManyTimesHasTabBeenPressed = 0
    
    def draw_cheatsheet(self):
        # normal mode
        sections = []
        if not self.commandMode:
            sections.append("basic")
            if self.notes != []:
                sections.append("objects")
                if isinstance(self.notes[self.selectedNote], NoteObject):
                    sections.append("note")
                elif isinstance(self.notes[self.selectedNote], TextObject):
                    sections.append("text")
        else:
            sections.append("command")
        # ypos = 0
        lines = []

        # check max
        maxKeyLen = 0
        maxValLen = 0
        for section in sections:
            for k,v in self.cheatsheet[section].items():
                if k.startswith("[line"): 
                    lines.append((v,v))
                else:
                    key = self.loc(f"editor.cheatsheet.{k}")
                    val = str(v)
                    if isinstance(v, int):
                        val = self.layout[v].upper()
                    if isinstance(v, list):
                        val = v[0]
                        for arg in v[1:]: #Parse command line arguments
                            # Thank you, random stackoverflow post!
                            # https://stackoverflow.com/questions/21503865/how-to-denote-that-a-command-line-argument-is-optional-when-printing-usage
                            val += " "
                            if arg[0] == True: 			#Required arguments
                                val += "<"
                                if len(arg) > 2: #Prefix
                                    val += arg[2]
                                val += term.italic + arg[1] + reset_color + ">"
                            else: 						#Optional arguments
                                val += "["
                                if len(arg) > 2: #Prefix
                                    val += arg[2]
                                val += term.italic + arg[1] + reset_color + "]"
                    if len(term.strip_seqs(key)) > maxKeyLen: maxKeyLen = len(term.strip_seqs(key))
                    if len(term.strip_seqs(val)) > maxValLen: maxValLen = len(term.strip_seqs(val))

                    lines.append((key, val)) #probably the only use of tuples in the entire code?

        # lines.insert(0, ("─"*(maxKeyLen+1), "─"*(maxValLen)))
        print_at(0, term.height-(7+min(len(lines)-1, 49)), "─"*(maxKeyLen+maxValLen+1) + "┐")

        # actual line writing
        for i in range(min(len(lines), 50)):
            print_at(0, term.height-(6+min(len(lines)-1, 49)-i), 
        lines[i][0] + " " * (maxKeyLen-len(term.strip_seqs(lines[i][0]))+1) + 
        (" " * (maxValLen-len(term.strip_seqs(lines[i][1]))) + lines[i][1]   ) + "│"
            )
        if self.howManyTimesHasTabBeenPressed < 2:
            print_at(0, term.height-(6+min(len(lines)+1,51)), "Tip: The cheatsheet can change depending on the context!")

    async def draw(self):
        # get background color
        self.set_background(self.get_background(self.localConduc.current_beat))
        # print_at(0,term.height-5, reset_color+"-"*(term.width-1))
        print_at(0,term.height-3, reset_color+"-"*(term.width))

        #Timeline
        for i in range(-(int(term.width/80)+1),int(term.width/8)-(int(term.width/80))+1):
            char = "'"
            if (4-(i%4))%4 == (int(self.localConduc.current_beat)%4):
                char = "|"
            slight_offset = int(self.localConduc.current_beat%1 * 8)
            real_draw_at = int((i*8)+(term.width*0.1)-slight_offset)
            draw_at = max(real_draw_at, 0)
            # maxAfterwards = int(min(7,term.width - (drawAt+1)))
            if i+self.localConduc.current_beat >= 0 or real_draw_at == draw_at:
                print_at(draw_at, term.height-5, char+("-"*7))
            else:
                print_at(draw_at, term.height-5, "-"*8)
        print_at(0,term.height-4, " "*(term.width-1))
        print_at(int(term.width*0.1), term.height-4, "@")
        print_at(0,term.height-6, reset_color
        +f"{self.loc('editor.timelineInfos.bpm')}: {self.localConduc.bpm} | "
        +f"{self.loc('editor.timelineInfos.snap')}: 1/{self.snap} | "
        +f"{self.loc('editor.timelineInfos.bar')}: {int(self.localConduc.current_beat//4)} | "
        +f"{self.loc('editor.timelineInfos.beat')}: {round(self.localConduc.current_beat%4, 5)} | "
        +term.clear_eol)


        if self.metadataMenuEnabled:
            length = max(len(self.loc('editor.metadata.'+i)) for i in self.metadataParts)
            for (i,part) in enumerate(self.metadataParts):
                category_name = self.loc('editor.metadata.'+part)
                category_name += ' '*(length-len(category_name)+1)
                if i == self.metadataMenuSelection:
                    full_category_name = term.reverse + category_name
                    if self.metadataTyping:
                        print_at(1,1+i,f"{full_category_name}: {term.underline}{self.metadataString}{reset_color}")
                    else:
                        print_at(1,1+i,f"{full_category_name}: {term.underline}{self.chart['metadata'][part]}{reset_color}")
                else:
                    print_at(1,1+i,f"{category_name}: {self.chart['metadata'][part]}")
            print_box(0,0,40,len(self.metadataParts) + 2,reset_color,0)


        if self.notes and not self.isTextEditing:
            self.selectedNote %= len(self.notes)
            note = self.notes[self.selectedNote]

            topleft = [
                int((term.width-default_size.x) * 0.5)-1,
                int((term.height-default_size.y) * 0.5)-1
            ]
            print_box(topleft[0],topleft[1]-1,default_size.x+2,default_size.y+2,reset_color,1)
            for i in range(len(self.notes)):
                j = len(self.notes) - (i+1)
                note = self.notes[j]
                remaining_beats = note.beat_position - self.localConduc.current_beat

                #TIMELINE
                if remaining_beats*8+(term.width*0.1) >= 0:
                    rendered_string = note.editor_timeline_icon(self.selectedNote == j)
                    print_at(
                        int(remaining_beats*8+(term.width*0.1)),
                        term.height-4,
                        rendered_string
                    )

                #PLAYFIELD
                (self.dont_draw_list, _) = note.render(
                    self.localConduc.current_beat,
                    self.dont_draw_list,
                    self.localConduc.cur_time_sec)

                # if note["type"] == "hit_object": # HIT OBJECT STUFF
                #     pass
                    # screenPos = note["screenpos"]
                    # characterDisplayed = self.layout[note["key"]]
                    # calculatedPos = Game.trueCalcPos(None, screenPos[0], screenPos[1], "setSize")
                    # calculatedPos[1] -= 1
                    # remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
                    # if type(note["color"]) is int:
                    #     color = colors[note["color"]]
                    # else:
                    #     # Formatting: "RRGGBB"
                    #     colorSplit = color_code_from_hex(note["color"])
                    #     color = term.color_rgb(colorSplit[0], colorSplit[1], colorSplit[2])



                    # if note in self.dontDrawList and remBeats > -0.1:
                    #     self.dontDrawList.remove(note)
                    # if not "approachRate" in self.mapToEdit:
                    #     self.mapToEdit["approachRate"] = 1
                    # appeoachedBeats = (remBeats * self.mapToEdit["approachRate"])
                    # if appeoachedBeats > -0.1 and appeoachedBeats < 4:
                    #     if self.selectedNote == j:
                    #         Game.renderNote(None, calculatedPos, color+term.reverse, characterDisplayed, appeoachedBeats+1, resetcol=reset_color)
                    #     else:
                    #         Game.renderNote(None, calculatedPos, color, characterDisplayed, appeoachedBeats+1, resetcol=reset_color)
                    # elif appeoachedBeats < -0.1 and note not in self.dontDrawList:
                    #     print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{reset_color}   ")
                    #     print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{reset_color}   ")
                    #     print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{reset_color}   ")
                    #     self.dontDrawList.append(note)
                # elif note["type"] == "text": # TEXT STUFF
                #     pass
                    # remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
                    # stopAt = remBeats + note["length"]
                    
                    # # TEXT - TIMELINE
                    # if remBeats*8+(term.width*0.1) >= 0:
                    #     if self.options["nerdFont"]:
                    #         char = "\U000f150f"
                    #     else:
                    #         char = "§"
                    #     if self.selectedNote == j:
                    #         print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.reverse}{term.turquoise}{term.bold}{char} {reset_color}")
                    #         print_at(int(stopAt*8+(term.width*0.1)), term.height-4, f"{term.turquoise}|{reset_color}")
                    #     else:
                    #         print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{reset_color}{term.turquoise}{term.bold}{char}{reset_color}")

                    # # TEXT - ON SCREEN
                    # constOffset = [0,-1]

                    # if note in self.dontDrawList and stopAt > 0 and remBeats <= 0:
                    #     self.dontDrawList.remove(note)
                    # if note not in self.dontDrawList:
                    #     if remBeats <= 0:
                    #         if stopAt > 0:
                    #             Game.renderText(None, note["text"], note["offset"], note["anchor"], note["align"], constOffset, self.localConduc.currentBeat)
                    #         else:
                    #             Game.renderText(None, " " * len(note["text"]), note["offset"], note["anchor"], note["align"], constOffset, self.localConduc.currentBeat)
                    #             self.dontDrawList.append(note)
                    #     else:
                    #         Game.renderText(None, " " * len(note["text"]), note["offset"], note["anchor"], note["align"], constOffset, self.localConduc.currentBeat)
                    #         self.dontDrawList.append(note)
                # elif note["type"] == "bg_color":
                #     remaining_beats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.current_beat
                #     # BACKGROUND_COLOR - TIMELINE
                #     if remaining_beats*8+(term.width*0.1) >= 0:
                #         if self.options["nerdFont"]:
                #             char = "\ue22b"
                #         else:
                #             char = "¶"
                #         symbol_color = self.get_background(note['beatpos'][0]*4 + note['beatpos'][1])
                #         if self.selectedNote == j:
                #             print_at(int(remaining_beats*8+(term.width*0.1)), term.height-3, f"{term.reverse}{symbol_color}{term.bold}{char} {reset_color}")
                #         else:
                #             print_at(int(remaining_beats*8+(term.width*0.1)), term.height-3, f"{reset_color}{symbol_color}{term.bold}{char}{reset_color}")

                # else:
                #     # END - TIMELINE
                #     remaining_beats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.current_beat
                #     if remaining_beats*8+(term.width*0.1) >= 0:
                #         if self.selectedNote == j:
                #             print_at(int(remaining_beats*8+(term.width*0.1)), term.height-4, f"{term.reverse}{term.bold_grey}▚{reset_color}")
                #         else:
                #             print_at(int(remaining_beats*8+(term.width*0.1)), term.height-4, f"{reset_color}{term.bold_grey}▚{reset_color}")
            #Current note info
            selected_note = self.notes[self.selectedNote]
            print_at(0, term.height-7, selected_note.display_informations(self.selectedNote))

            #Render selected note on top in the timeline
            if remaining_beats*8+(term.width*0.1) >= 0:
                rendered_string = note.editor_timeline_icon(self.selectedNote == j)
                print_at(
                    int(remaining_beats*8+(term.width*0.1)),
                    term.height-4,
                    rendered_string
                )
            # elif selectedNote["type"] == "end":
            #     print_at(0, term.height-7, reset_color+f"{self.loc('editor.timelineInfos.curNote')}: {self.selectedNote} | {self.loc('editor.timelineInfos.endpos')}: {selectedNote['beatpos']}")
        else:
            if not self.keyPanelEnabled and not self.isTextEditing:
                text_nomaploaded = self.loc("editor.emptyChart")
                print_at(int((term.width - len(text_nomaploaded))*0.5),int(term.height*0.4), reset_color+text_nomaploaded)

        if "bpmChanges" not in self.chart:
            self.chart["bpmChanges"] = []
        if self.chart["bpmChanges"] != []:
            for i in range(len(self.chart["bpmChanges"])):
                change = self.chart["bpmChanges"][i]
                remaining_beats = (change["atPosition"][0] + change["atPosition"][1]/4) - self.localConduc.current_beat
                if int(remaining_beats*8+(term.width*0.1)) >= 0:
                    print_at(int(remaining_beats*8+(term.width*0.1)), term.height-3, f"{reset_color}\U000f07da{reset_color}")

        if self.keyPanelEnabled:
            if self.keyPanelSelected == -1:
                text_key = self.loc("editor.newKey.creating")
            else:
                text_key = self.loc("editor.newKey.editing")
            self.draw_changeKeyPanel(text_key,self.keyPanelKey)
        elif self.keyPanelJustDisabled:
            self.draw_changeKeyPanel()
            self.keyPanelJustDisabled = False

        if self.commandMode:
            print_at(0,term.height-2, reset_color+":"+self.commandString+term.clear_eol)
            chrAtCursor = ""
            if len(self.commandString) != 0:
                if self.commandSelectPos != 0:
                    chrAtCursor = self.commandString[len(self.commandString)-(self.commandSelectPos)]
                else:
                    chrAtCursor = " "
                print_at(len(self.commandString)-self.commandSelectPos + 1, term.height-2, term.underline + chrAtCursor + reset_color)
        elif self.commandFooterEnabled:
            print_at(0,term.height-2, self.commandFooterMessage + reset_color)

        if self.cheatsheetEnabled:
            self.draw_cheatsheet()

        if not self.hasCheatsheetBeenSeen:
            cheatsheettip = "[TAB] " + self.loc("editor.cheatsheet.cheatsheet")
            print_at(term.width-len(cheatsheettip), term.height-6, cheatsheettip)

        if self.colorPickerEnabled:
            self.draw_colorPicker()

        if self.isTextEditing:
            self.textEdit.draw()

        if self.delConfirmEnabled:
            self.draw_confirmDeletion()

        if self.pauseMenuEnabled:
            self.draw_pauseMenu()

        framerate_display = str(framerate()) + "fps"
        print_at(term.width-10, 0, term.rjust(framerate_display, 10) )

    @staticmethod
    def recreate_note_data(notes):
        notes_list:list = []
        for note in notes:
            notes_list.append(note.serialize())
        return notes_list

    def run_command(self, command = ""):
        cmd_argv = command.split(" ")
        print_at(0,term.height-2, term.clear_eol)
        # :q - Quit
        if cmd_argv[0] == "q!" or (cmd_argv[0] == "q" and not self.needsSaving):
            self.turn_off = True
            return True, ""

        elif cmd_argv[0] == "loop" or cmd_argv[0] == "lp":
            if len(cmd_argv) < 2:
                cmd_argv = "1"
            return None, "START_LOOP:"+cmd_argv[1]

        elif cmd_argv[0] == "cl":
            return None, "END_LOOP"

        # :w - Write (Save) | 1 optional argument (where to save it)
        elif cmd_argv[0] == "w":
            if self.chart["formatVersion"] != 1:
                self.chart["formatVersion"] = 1
            self.chart["notes"] = self.recreate_note_data(self.notes)
            output = json.dumps(self.chart, indent=4)
            if len(cmd_argv) > 1:
                self.chart["foldername"] = cmd_argv[1]
            if len(cmd_argv) == 2:
                self.fileLocation = f"./charts/{cmd_argv[1]}/data.json"
            elif len(cmd_argv) == 3:
                self.fileLocation = f"./charts/{cmd_argv[1]}/{cmd_argv[2]}.json"
            elif self.fileLocation == "" and len(cmd_argv) == 1:
                self.fileBrwsr.fileExtFilter = "(?:\\/$)"
                self.fileBrwsr.load_folder(os.getcwd())
                self.fileBrwsr.selectFolderMode = True
                self.fileBrwsr.caption = "Select a folder"
                self.fileBrwsr.turnOff = False
                folder_location = self.fileBrwsr.loop()

                if folder_location != "?":
                    self.fileLocation = folder_location + "/data.json"
                    self.chart["foldername"] = folder_location.split("/")[-1]
                # return False, getFolderLocation
                # return False, self.loc("editor.commandResults.common.notEnoughArgs")
            if os.path.exists(self.fileLocation):
                file_data = open(self.fileLocation, "w", encoding="utf8")
            else:
                if not os.path.exists("./charts/"):
                    os.mkdir("./charts")
                if len(cmd_argv) > 1:
                    if not os.path.exists(f"./charts/{cmd_argv[1]}"):
                        os.mkdir(f"./charts/{cmd_argv[1]}")
                file_data = open(self.fileLocation, "x", encoding="utf8")
            file_data.write(output)
            file_data.close()
            return True, self.loc("editor.commandResults.save")

        # :wq - Save and Quit | 1 optional argument (where to save it)
        elif cmd_argv[0] == "wq!" or (cmd_argv[0] == "wq" and not self.needsSaving):
            output = json.dumps(self.chart, indent=4)
            if len(cmd_argv) == 2:
                self.fileLocation = f"./charts/{cmd_argv[1]}/data.json"
            elif len(cmd_argv) == 3:
                self.fileLocation = f"./charts/{cmd_argv[1]}/{cmd_argv[2]}.json"
            if os.path.exists(self.fileLocation):
                file_data = open(self.fileLocation, "w", encoding="utf8")
            else:
                file_data = open(self.fileLocation, "x", encoding="utf8")
            file_data.write(output)
            file_data.close()
            self.turn_off = True
            return True, self.loc("editor.commandResults.save")

        # :ar - Approach Rate
        elif cmd_argv[0] == "ar":
            if len(cmd_argv) >= 2:
                if cmd_argv[1].replace(".", "", 1).isdigit():
                    self.chart["approachRate"] = float(cmd_argv[1])
                    return True, "[ar_set_to]"+cmd_argv[1]
                else:
                    return False, "[ar_not_a_number]"

        # :diff - Difficulty
        elif cmd_argv[0] == "diff":
            if len(cmd_argv) >= 2:
                if cmd_argv[1].isdigit():
                    self.chart["difficulty"] = int(cmd_argv[1])
                else:
                    self.chart["difficulty"] = cmd_argv[1]
                return True, "[diff_set_to]"+cmd_argv[1]

        # :o - Open
        elif cmd_argv[0] == "o":
            if len(cmd_argv) == 2:
                file_exists = self.load_chart(cmd_argv[1])
                if not file_exists:
                    return file_exists, self.loc("editor.commandResults.open.notFound")
                else:
                    return file_exists, self.loc("editor.commandResults.open.success")
            elif len(cmd_argv) == 3:
                self.load_chart(cmd_argv[1], cmd_argv[2])
            else:
                if len(cmd_argv) < 2:
                    return False, self.loc("editor.commandResults.common.notEnoughArgs")
                else:
                    return False, self.loc("editor.commandResults.common.tooManyArgs")
        
        # :p - Place
        elif cmd_argv[0] == "p":
            if len(cmd_argv) > 1:
                if cmd_argv[1].isdigit():
                    self.selectedNote = self.create_note(self.localConduc.current_beat, int(cmd_argv[1]))
                    return True, self.loc("editor.commandResults.note.success")
            else:
                self.keyPanelEnabled = True
                self.keyPanelSelected = -1
                self.keyPanelKey = 0
                return True, ""

        # :song - Change song
        elif cmd_argv[0] == "song":
            if self.fileLocation == "":
                return False, "You need to save this file first! To do that, type :w <some_chart_name>"
            if len(cmd_argv) > 1:
                if os.path.exists(cmd_argv[1]) and cmd_argv[1].split(".")[-1] in ["ogg", "mp3", "wav"]:
                    soundFileLocation = cmd_argv[1]
                    self.chart["sound"] = soundFileLocation.split('/')[-1]
                    shutil.copyfile(soundFileLocation, f"./charts/{self.chart['foldername']}/{soundFileLocation.split('/')[-1]}")
                    self.localConduc.loadsong(self.chart)
            else:
                self.fileBrwsr.fileExtFilter = "(?:\\.ogg$)|(?:\\.wav$)|(?:\\.mp3$)"
                self.fileBrwsr.load_folder(os.getcwd())
                self.fileBrwsr.caption = "Select a song"
                self.fileBrwsr.turnOff = False
                soundFileLocation = self.fileBrwsr.loop()
                if soundFileLocation != "?":
                    self.chart["sound"] = soundFileLocation.split('/')[-1]
                    try:
                        shutil.copyfile(soundFileLocation, f"./charts/{self.chart['foldername']}/{soundFileLocation.split('/')[-1]}")
                    except shutil.SameFileError:
                        pass
                    self.localConduc.loadsong(self.chart)
                else:
                    return False, "File selection aborted."

        # :off - Change song offset
        elif cmd_argv[0] == "off":
            offset = 0
            if len(cmd_argv) > 1:
                offset = float(cmd_argv[1])
            else:
                self.calib.startCalibSong(self.chart)
                offset = self.calib.init(False)
                self.calib.conduc.stop()
                self.calib.turnOff = False
            offset = round(offset, 6) # 6 is completely arbitrary, it's mostly to deal with floating point fuckery
            self.chart["offset"] = offset
            self.localConduc.setOffset(offset)
            return True, f"New offset: {offset}"

        # :s - Snap
        elif cmd_argv[0] == "s":
            if len(cmd_argv) > 1:
                if cmd_argv[1].replace('.', '', 1).isdigit():
                    self.snap = float(cmd_argv[1])

        # :m - Move cursor
        elif cmd_argv[0] == "m":
            if len(cmd_argv) > 1:
                if cmd_argv[1].startswith("~"):
                    self.localConduc.current_beat += float(cmd_argv[1].replace("~", ""))
                else:
                    self.localConduc.current_beat = float(cmd_argv[1])
        
        # :mt - Metadata
        elif cmd_argv[0] == "mt":
            if len(cmd_argv) >= 3:
                value_changed = ""
                changed_to = ""
                if cmd_argv[1] in ["title", "t"]:
                    self.chart["metadata"]["title"] = " ".join(cmd_argv[2:])
                    value_changed = "title"
                    changed_to = self.chart["metadata"]["title"]
                if cmd_argv[1] in ["artist", "a"]:
                    self.chart["metadata"]["artist"] = " ".join(cmd_argv[2:])
                    value_changed = "artist"
                    changed_to = self.chart["metadata"]["artist"]
                if cmd_argv[1] in ["author", "charter", "au", "c"]:
                    self.chart["metadata"]["author"] = " ".join(cmd_argv[2:])
                    value_changed = "author"
                    changed_to = self.chart["metadata"]["author"]
                if cmd_argv[1] in ["description", "desc", "d"]:
                    self.chart["metadata"]["description"] = " ".join(cmd_argv[2:])
                    value_changed = "description"
                    changed_to = self.chart["metadata"]["description"]
                return True, self.loc("editor.commandResults.meta.success").format(value_changed, changed_to)
            elif len(cmd_argv) == 2:
                return_message = ""
                if cmd_argv[1] in ["title", "t"]:
                    return_message = self.chart["metadata"]["title"]
                if cmd_argv[1] in ["artist", "a"]:
                    return_message = self.chart["metadata"]["artist"]
                if cmd_argv[1] in ["author", "charter", "au", "c"]:
                    return_message = self.chart["metadata"]["author"]
                if cmd_argv[1] in ["description", "desc", "d"]:
                    return_message = self.chart["metadata"]["description"]
                return True, return_message

        # :bpm - Change BPM
        elif cmd_argv[0] == "bpm":
            if len(cmd_argv) == 2:
                newbpm = 120
                if cmd_argv[1].find(".") != -1:
                    newbpm = float(cmd_argv[1])
                else:
                    newbpm = int(cmd_argv[1])
                
                self.chart["bpm"] = newbpm
                self.localConduc.bpm = newbpm

                return True, ""
            elif len(cmd_argv) > 2:
                return False, self.loc("editor.commandResults.common.tooManyArgs")
            return False, self.loc("editor.commandResults.common.notEnoughArgs")
        
        elif cmd_argv[0] == "bpmc":
            if len(cmd_argv) == 2:
                newbpm = 120
                if cmd_argv[1].find(".") != -1:
                    newbpm = float(cmd_argv[1])
                else:
                    newbpm = int(cmd_argv[1])
                
                new_bpm_object = {
                    "atPosition": [
                        self.localConduc.current_beat, 
                        (self.localConduc.current_beat%1)*4
                    ],
                    "toBPM": newbpm
                }

                self.chart["bpmChanges"].append(new_bpm_object)
                self.localConduc.bpmChanges.append(new_bpm_object)

                return True, ""
            elif len(cmd_argv) > 2:
                return False, self.loc("editor.commandResults.common.tooManyArgs")
            return False, self.loc("editor.commandResults.common.notEnoughArgs")

        elif cmd_argv[0] == "delbpmc":
            if len(cmd_argv) == 2:
                self.localConduc.bpmChanges.remove(self.chart["bpmChanges"][int(cmd_argv[1])])
                self.chart["bpmChanges"].remove(self.chart["bpmChanges"][int(cmd_argv[1])])

        # :cp - Copy
        elif cmd_argv[0] == "cp":
            if len(cmd_argv) == 3:
                #XX-YY : Range of notes to copy
                rangeToPick = cmd_argv[1].split("-")
                if len(rangeToPick) >= 2:
                    pass
                else:
                    return False, self.loc("editor.commandResults.common.notEnoughArgs")

                notes_to_copy = [copy.deepcopy(self.chart["notes"][i]) \
                               for i in range(int(rangeToPick[0]), int(rangeToPick[1])+1)]
                #BB : How many beats to offset it by?

                for (_,note) in enumerate(notes_to_copy):
                    note["beatpos"][1] += float(cmd_argv[2])
                    note["beatpos"][0] += note["beatpos"][1]//4
                    note["beatpos"][1] %= 4
                    self.chart["notes"].append(note)
                self.chart["notes"] = sorted(
                    self.chart["notes"], 
                    key=lambda d: d['beatpos'][0]*4+d['beatpos'][1]
                )
                if "end" in [note["type"] for note in self.chart["notes"]]:
                    self.endNote = [note["type"] for note in self.chart["notes"]].index("end")
                return True, ""

            elif len(cmd_argv) > 3:
                return False, self.loc("editor.commandResults.common.tooManyArgs")
            return False, self.loc("editor.commandResults.common.notEnoughArgs")

        elif cmd_argv[0] == "t":
            if len(cmd_argv) > 1:
                self.create_text(atPos=self.localConduc.current_beat, text=" ".join(cmd_argv[1:]))
                return True, self.loc("editor.commandResults.note.success")
            else:
                return False, "[cannot create empty text]"

        elif cmd_argv[0] == "c":
            note = self.chart["notes"][self.selectedNote]
            if cmd_argv[1].startswith("#") and len(cmd_argv[1].replace("#", "", 1)) == 6:
                note["color"] = cmd_argv[1].replace("#", "", 1)
            elif cmd_argv[1].isDigit():
                note["color"] = int(cmd_argv[1])

        elif cmd_argv[0] == "sel":
            if cmd_argv[1].startswith("~"):
                self.selectedNote += int(cmd_argv[1].replace("~", ""))
            else:
                self.selectedNote = int(cmd_argv[1])

        elif cmd_argv[0] == "del":
            if len(cmd_argv) < 2:
                self.notes.remove(self.notes[self.selectedNote])
            else:
                self.notes.remove(self.notes[int(cmd_argv[1])])

        elif cmd_argv[0] == "bgc":
            if len(cmd_argv) > 1:
                newNote = {
                    "type": "bg_color",
                    "beatpos": [
                        int(self.localConduc.current_beat//4),
                        round(self.localConduc.current_beat%4, 5)
                    ],
                    "color": cmd_argv[1]
                }
                self.chart["notes"].append(newNote)
                self.background_changes = Game.load_bg_changes(self.chart)
                return True, "this is gonna crash the game isn't it"

        else:
            if len(cmd_argv[0]) > 128:
                return False, self.loc("editor.commandResults.common.tooLong")
            return False, self.loc("editor.commandResults.common.notFound")

        return True, ""

    async def handle_input(self):
        val = ''
        val = term.inkey(timeout=1/120, esc_delay=0)

        if self.playtest:
            for actual_note in self.notes:
                if isinstance(actual_note, NoteObject):
                    remaining_beats = actual_note.beat_position - self.localConduc.current_beat
                    if actual_note not in self.dontBeat and remaining_beats <= 0:
                        self.beatSound.move2position_seconds(0)
                        self.beatSound.play()
                        self.dontBeat.append(actual_note)
                    if actual_note in self.dontBeat and remaining_beats > 0:
                        self.dontBeat.remove(actual_note)

        if self.metadataMenuEnabled:
            if not self.metadataTyping:
                if val.name == "KEY_ESCAPE":
                    print(term.clear)
                    self.metadataMenuEnabled = False
                if val.name == "KEY_UP":
                    self.metadataMenuSelection -= 1
                    self.metadataMenuSelection = max(self.metadataMenuSelection, 0)
                if val.name == "KEY_DOWN":
                    self.metadataMenuSelection += 1
                    self.metadataMenuSelection = min(self.metadataMenuSelection, len(self.metadataParts) - 1)
                if val.name == "KEY_ENTER":
                    self.metadataTyping = True
                    self.metadataString = self.chart["metadata"][self.metadataParts[self.metadataMenuSelection]]
            else:
                if val.name == "KEY_ESCAPE":
                    self.metadataTyping = False
                    # self.commandString = ""
                    print_at(0,term.height-2, term.clear_eol+reset_color)
                elif val.name == "KEY_ENTER":
                    self.metadataTyping = False
                    self.chart["metadata"][self.metadataParts[self.metadataMenuSelection]] = self.metadataString
                    #there was a todo here but i forgor what it was for
                else:
                    if self.metadataString == "" and val.name == "KEY_BACKSPACE":
                        self.commandMode = False
                        # print_at(0,term.height-2, term.clear_eol+reset_color)
                    self.metadataString, self.metadataTypingCursor = textbox_logic(self.metadataString, self.metadataTypingCursor, val)
        elif self.pauseMenuEnabled:
            if val.name == "KEY_UP":
                self.pauseMenuSelected -= 1
                self.pauseMenuSelected %= len(self.pauseMenu)
            if val.name == "KEY_DOWN":
                self.pauseMenuSelected += 1
                self.pauseMenuSelected %= len(self.pauseMenu)
            if val.name == "KEY_ENTER":
                self.run_pauseMenu(self.pauseMenuSelected)

        elif self.isTextEditing:
            if val.name == "KEY_ESCAPE" and self.textEdit.isSelectingText == False:
                self.isTextEditing = False
                self.notes[self.textobjectedited].text = self.textEdit.textContent
            else:
                self.textEdit.handle_input(val)

        elif self.colorPickerEnabled:
            self.colorPickerNoteSelected = self.selectedNote
            self.input_colorPicker(val)

        elif self.delConfirmEnabled:
            self.delConfirmObj = self.selectedNote
            self.input_confirmDeletion(val)

        elif not self.commandMode:
            if val.name == "KEY_TAB":
                self.hasCheatsheetBeenSeen = True
                self.cheatsheetEnabled = not self.cheatsheetEnabled
                self.howManyTimesHasTabBeenPressed += 1
            # debug_val(val)
            if self.keyPanelEnabled:
                if val.name == "KEY_ESCAPE":
                    self.keyPanelEnabled = False
                    self.keyPanelJustDisabled = True
                elif val.name == "KEY_ENTER":
                    if self.keyPanelKey != -1:
                        if self.keyPanelSelected == -1:
                            self.selectedNote = self.create_note(self.localConduc.current_beat, self.keyPanelKey)
                        else:
                            self.notes[self.keyPanelSelected]._key_index = self.keyPanelKey
                        self.keyPanelEnabled = False
                        self.keyPanelJustDisabled = True
                        self.keyPanelSelected = -1
                        self.keyPanelKey = -1
                elif val:
                    if str(val) in self.layout:
                        self.keyPanelKey = self.layout.index(str(val))
            else:
                if val.name != "KEY_ENTER" and val:
                    self.commandFooterEnabled = False
                if val == ":":
                    self.commandMode = True
                    self.commandString = ""
                if val == " ":
                    self.background_changes = Game.load_bg_changes(self.chart["notes"])
                    if not self.playtest:
                        for actual_note in self.notes:
                            remaining_beats = actual_note.beat_position - self.localConduc.current_beat
                            if remaining_beats < 0:
                                self.dontBeat.append(actual_note)
                        self.localConduc.startAt(self.localConduc.current_beat)
                    else:
                        self.localConduc.stop()
                        self.localConduc.current_beat = round(self.localConduc.current_beat/(self.snap/4)) * (self.snap/4)
                    self.playtest = not self.playtest
                if val.name == "KEY_HOME":
                    self.localConduc.current_beat = 0
                if val.name == "KEY_ESCAPE":
                    self.pauseMenuEnabled = True
                if val.name in ("KEY_RIGHT", "KEY_SRIGHT"):
                    multiplier = {"KEY_RIGHT": 1, "KEY_SRIGHT": 4}[val.name]
                    self.localConduc.current_beat += (1/self.snap)*4*multiplier
                if val.name in ("KEY_LEFT", "KEY_SLEFT"):
                    multiplier = {"KEY_LEFT": 1, "KEY_SLEFT": 4}[val.name]
                    self.localConduc.current_beat = max(self.localConduc.current_beat - (1/self.snap)*4*multiplier, 0)
                if val == "z":
                    self.keyPanelEnabled = True
                    self.keyPanelSelected = -1
                    self.keyPanelKey = 0
                    print_at(0,int(term.height*0.4), term.clear_eol)
                if val == "Z":
                    self.set_end_note(self.localConduc.current_beat)
                if val == "t":
                    self.localConduc.metronome = not self.localConduc.metronome
                if val in ["1", "&"]:
                    self.selectedSnap -= 1
                    self.selectedSnap %= len(self.snapPossible)
                    self.snap = self.snapPossible[self.selectedSnap]
                if val in ["2", "é"]:
                    self.selectedSnap += 1
                    self.selectedSnap %= len(self.snapPossible)
                    self.snap = self.snapPossible[self.selectedSnap]

                    
                if self.chart["notes"] != []:
                    actual_note:NoteObject|TextObject = self.notes[self.selectedNote]
                    json_note = self.chart["notes"][self.selectedNote]
                    if val.name in ("KEY_DOWN", "KEY_SDOWN"):
                        multiplier = {"KEY_DOWN": 1, "KEY_SDOWN": 4}[val.name]
                        self.selectedNote = min(self.selectedNote + (1*multiplier), len(self.chart["notes"])-1)
                        actual_note = self.notes[self.selectedNote]
                        self.localConduc.current_beat = actual_note.beat_position
                    if val.name in ("KEY_UP", "KEY_SUP"):
                        multiplier = {"KEY_UP": 1, "KEY_SUP": 4}[val.name]
                        self.selectedNote = max(self.selectedNote - (1*multiplier), 0)
                        actual_note = self.notes[self.selectedNote]
                        self.localConduc.current_beat = actual_note.beat_position

                    if val == "u":
                        self.localConduc.current_beat = max(self.localConduc.current_beat - (1/self.snap)*4, 0)
                        actual_note.beat_position = self.localConduc.current_beat
                    if val == "i":
                        self.localConduc.current_beat += (1/self.snap)*4
                        actual_note.beat_position = self.localConduc.current_beat

                    if val == "d" and json_note["type"] == "hit_object":
                        self.selectedNote = self.create_note(
                            actual_note.beat_position,
                            actual_note.key_index
                        )
                        self.chart["notes"][self.selectedNote] = copy.deepcopy(json_note)
                    if val == "d" and json_note["type"] == "text":
                        newNote = copy.deepcopy(json_note)
                        self.chart["notes"].append(newNote)
                        self.chart["notes"] = sorted(self.chart["notes"], key=lambda d: d['beatpos'][0]*4+d['beatpos'][1])
                        if "end" in [note["type"] for note in self.chart["notes"]]:
                            self.endNote = [note["type"] for note in self.chart["notes"]].index("end")
                        self.selectedNote = self.chart["notes"].index(newNote)

                    if json_note["type"] == "hit_object" and val:
                        screen_position = actual_note.position
                        calculated_pos = Game.calculate_position(
                            screen_position,
                            5, 3,
                            term.width-10, term.height-11
                        )
                        # erase hitbox
                        if val in "hjklHJKL":
                            print_at(calculated_pos[0]-1, calculated_pos[1]-1, f"{reset_color}   ")
                            print_at(calculated_pos[0]-1, calculated_pos[1]+0, f"{reset_color}   ")
                            print_at(calculated_pos[0]-1, calculated_pos[1]+1, f"{reset_color}   ")
                        # calculate new x/y position
                        direc = val.lower()
                        multiplier = (3 if direc in "hl" else 2) if val.isupper() else 1
                        if val in "hH":
                            actual_note.position.x = max(round(
                                actual_note.position.x - multiplier/default_size[0], 4
                            ), 0)
                        if val in "jJ":
                            actual_note.position.y = min(round(
                                actual_note.position.y + multiplier/default_size[1], 4
                            ), 1)
                        if val in "kK":
                            actual_note.position.y = max(round(
                                actual_note.position.y - multiplier/default_size[1], 4
                            ), 0)
                        if val in "lL":
                            actual_note.position.x = min(round(
                                actual_note.position.x + multiplier/default_size[0], 4
                            ), 1)
                        if val == "e":
                            self.run_noteSettings(actual_note, self.selectedNote, 0)
                        if val == "E":
                            self.colorPickerEnabled = not self.colorPickerEnabled
                        # if val == "x":
                        #     json_note["color"] += 1
                        #     json_note["color"] %= len(colors)
                        # if val == "X":
                        #     json_note["color"] -= 1
                        #     json_note["color"] %= len(colors)
                    if actual_note["type"] == "text" and val:
                        direc = val.lower()
                        multiplier = (3 if direc in "hl" else 2) if val.isupper() else 1
                        if val in "hH":
                            actual_note.offset.x -= multiplier
                        if val in "jJ":
                            actual_note.offset.y += multiplier
                        if val in "kK":
                            actual_note.offset.y -= multiplier
                        if val in "lL":
                            actual_note.offset.x += multiplier
                        if val == "U":
                            actual_note.duration = max(actual_note.duration - (1/self.snap)*4, 0)
                        if val == "I":
                            actual_note.duration += (1/self.snap)*4
                        if val == "e":
                            self.run_noteSettings(actual_note, self.selectedNote, 0)

                        if val == "x":
                            actual_note["color"] = actual_note.get('color', -1) + 1
                            actual_note["color"] %= len(colors)
                        if val == "X":
                            actual_note["color"] = actual_note.get('color', len(colors)) - 1
                            actual_note["color"] %= len(colors)
                        if val == "c":
                            self.run_noteSettings(actual_note, self.selectedNote, 2)
                    if actual_note["type"] == "bg_color" and val:
                        if val == "e":
                            self.colorPickerEnabled = not self.colorPickerEnabled


                    if val.name == "KEY_DELETE" or val.name == "KEY_BACKSPACE":
                        self.delConfirmEnabled = True
                        # self.mapToEdit["notes"].remove(note)

        else:
            if val.name == "KEY_TAB":
                self.cheatsheetEnabled = not self.cheatsheetEnabled
            if val.name == "KEY_UP":
                if self.commandHistoryCursor == 0:
                    self.cachedCommand = self.commandString
                if self.commandHistoryCursor < len(self.commandHistory):
                    self.commandHistoryCursor+=1
                    self.commandString = self.commandHistory[len(self.commandHistory) - (self.commandHistoryCursor)]
            if val.name == "KEY_DOWN":
                if self.commandHistoryCursor > 0:
                    self.commandHistoryCursor-=1
                if self.commandHistoryCursor == 0:
                    self.commandString = self.cachedCommand
                else:
                    self.commandString = self.commandHistory[len(self.commandHistory) - (self.commandHistoryCursor)]
            if val.name == "KEY_ESCAPE":
                self.commandMode = False
                self.commandString = ""
                self.commandHistoryCursor = 0
                self.cachedCommand = ""
            elif val.name == "KEY_ENTER":
                self.commandHistoryCursor = 0

                #Add the command string to the front, remove it anywhere else if it already exists
                if self.commandString in self.commandHistory:
                    self.commandHistory.remove(self.commandString)
                self.commandHistory.append(self.commandString)
                self.cachedCommand = ""
                splitCommands = self.commandString.split(";;")
                self.commandFooterMessage = ""
                if len(splitCommands) > 1:
                    command_results = []
                    errors = []
                    index = 0
                    for comm in splitCommands:
                        is_valid, error_string = self.run_command(comm)
                        if is_valid is None: #LOOP CHECK
                            if error_string.split(":")[0] == "START_LOOP":
                                endLoop = index+1
                                for i in splitCommands[index+1:]:
                                    endLoop += 1
                                    if i == "cl": #CLOSE LOOP
                                        # splitCommands = splitCommands[:endLoop]+splitCommands[endLoop+1:] #Remove cl
                                        # endLoop -= 1
                                        break
                                toLoop = splitCommands[index+1:endLoop]
                                for _ in range(int(error_string.split(":")[1]) - 1):
                                    count = index
                                    for loopcomm in toLoop:
                                        if loopcomm != "cl":
                                            splitCommands.insert(index+1+count, loopcomm)
                                            count+=1
                        else:
                            command_results.append([is_valid, error_string])
                        index += 1
                    for (_,rsult) in enumerate(command_results):
                        col = term.on_green
                        if not rsult[0]:
                            errors.append(rsult[1])
                            col = term.on_red
                        self.commandFooterMessage += col + "*"
                    self.commandFooterMessage += reset_color + "     "
                    if len(errors) != 0:
                        self.commandFooterMessage += term.on_red+errors[-1]
                    self.commandMode = False
                    self.commandString = ""

                else:
                    is_valid, error_string = self.run_command(self.commandString)
                    self.commandMode = False
                    self.commandString = ""
                    if is_valid is not None:
                        if is_valid:
                            if error_string != "":
                                self.commandFooterMessage = term.on_green+error_string
                        else:
                            self.commandMode = False
                            self.commandString = ""
                            self.commandFooterMessage = term.on_red+error_string
                self.commandFooterEnabled = True
            else:
                if self.commandString == "" and val.name == "KEY_BACKSPACE":
                    self.commandMode = False
                    print_at(0,term.height-2, term.clear_eol+reset_color)
                self.commandString, self.commandSelectPos = textbox_logic(
                    self.commandString, 
                    self.commandSelectPos, 
                    val, self.autocomplete
                )

    def on_open(self):
        if not self.chart:
            self.setupMap()
        else:
            self.keys = LayoutManager[OptionsManager["layout"]]
            Game.setup_notes(self, self.chart["notes"])

    def loop(self):
        super().loop()
        self.set_background(term.normal)

    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    editor = Editor()
    # loadedMenus["Editor"] = editor
    editor.layoutname = "qwerty"
    editor.layout = Game.setupKeys(None, editor.layoutname)
    editor.loop()
