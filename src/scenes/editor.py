import json
import copy
import os
from zipfile import ZipFile
from blessed import Terminal
from pybass3 import Song

from src.scenes.game import Game
from src.conductor import Conductor
from src.constants import colors, ALIGN_CENTER, CENTER, Vector2i, Color
from src.termutil import term, print_at, print_box, framerate, log, logging
from src.scenes.base_scene import BaseScene
from src.translate import Locale
from src.textbox import TextEditor
from src.filebrowser import FileBrowser
from src.calibration import Calibration
from src.layout import LayoutManager
from src.scenes.game_objects.note import NoteObject
from src.scenes.game_objects.text import TextObject
from src.scenes.game_objects.bg_color import BackgroundColorObject
from src.scenes.game_objects.end_level import EndLevelObject
from src.scenes.game_objects.base_object import GameplayObject
from src.scenes.game_objects.playfield import Playfield
from src.scenes.editor_tools.color_picker import ColorPicker
from src.scenes.editor_tools.pause_menu import EditorPauseMenu
from src.scenes.editor_tools.command_line import EditorCommandLine
from src.scenes.editor_tools.key_panel import KeyPanel
from src.scenes.editor_tools.metadata import EditorMetadata
from src.scenes.editor_tools.timeline import EditorTimeline

term = Terminal()

# WARNING TO WHOEVER WANTS TO MOD THIS FILE:
# good luck

class Editor(BaseScene):

    #Basics
    chart = {}
    notes:list[GameplayObject] = []
    keys = []
    conduc = Conductor()
    playtest = False
    beatSound = Song("assets/clap.wav")
    dont_draw_list = []
    dontBeat = [] #Notes that have already got their beatsound played
    playfield:Playfield = Playfield()

    #Saving
    needsSaving = False
    file_location = ""

    #Notes selected
    selected_note = 0
    end_note = -1

    #Editor settings
    snap = 4
    selected_snap = 2
    snapPossible = [1, 2, 4, 8, 16, 3, 6, 12]
    layout = []
    layoutname = "qwerty"

    #Timeline
    timeline:EditorTimeline = EditorTimeline()

    #Key panel
    key_panel:KeyPanel = KeyPanel()

    #Command Line
    command_line:EditorCommandLine = EditorCommandLine()

    #Pause Menu
    pause_menu:EditorPauseMenu = EditorPauseMenu()

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
    metadata:EditorMetadata = EditorMetadata()

    #File Browser
    file_browser:FileBrowser = FileBrowser()

    #Calibration
    calib:Calibration = Calibration("CalibrationSong")

    #Playtest
    game:Game = Game()

    options = {
        "nerdFont": True,
        "bypassSize": True,
    }

    palette = [
        term.normal,
        Color("fc220a"),
        Color("fc9b0a"),
        Color("f4fc0a"),
        Color("0efc0a"),
        Color("0afcfc"),
        Color("0a36fc"),
        Color("830afc"),
        Color("0ab7fc"),
        Color("fc0ab3"),
        Color("72737c")
    ]

    #Text edition
    textEdit = TextEditor()
    is_text_editing = False
    textobjectedited = -1

    #Color picker
    color_picker:ColorPicker = ColorPicker()

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
        self.palette[0] = term.normal + background
        self.reset_color = term.normal + background

    def autocomplete(self, command = ""):
        output = []
        if command != "":
            # return list of commands uhhh
            # commandSplit = command.split(" ")
            pass

        #where do i even begin

        return output


    def export(self):
        """Export song folder into a zip file"""
        file_paths = [] #this is where the paths go

        # crawling through directory and subdirectories
        for _, _the_secondth, files in os.walk("./charts/" + self.chart["foldername"]):
            for filename in files:
                #gimme da full path plz :3
                file_paths.append(filename)

        # actual exporting
        with ZipFile("./charts/" + self.chart["foldername"] + '.zip','w') as zip_file:
            # add in the files
            for file in file_paths:
                zip_file.write("./charts/" + self.chart["foldername"] + "/" + file, file)

    @staticmethod
    def export_palette(palette:list[Color]) -> list[str]:
        out = []
        for pal in palette:
            if isinstance(pal, Color):
                out.append(pal.hex_value)
        return out

    def save(self, folder = "", filename = ""):
        """
        Call this when saving! The two arguments are optional and will
        just use self.folder_location as saving location.
        """
        if self.chart["formatVersion"] != 1:
            self.chart["formatVersion"] = 1
        self.chart["notes"] = self.recreate_note_data(self.notes)
        self.chart["palette"] = Editor.export_palette(self.palette)
        if folder != "":
            self.chart["foldername"] = folder
            if not os.path.exists("./charts/"):
                os.mkdir("./charts")
            if not os.path.exists(f"./charts/{folder}"):
                os.mkdir(f"./charts/{folder}")
            if filename == "":
                self.file_location = f"./charts/{folder}/data.json"
            else:
                self.file_location = f"./charts/{folder}/{filename}.json"
        if self.file_location == "" and folder == "":
            self.file_browser.fileExtFilter = "(?:\\/$)"
            self.file_browser.load_folder(os.getcwd())
            self.file_browser.selectFolderMode = True
            self.file_browser.caption = "Select a folder"
            self.file_browser.turnOff = False
            folder_location = self.file_browser.loop()

            if folder_location != "?":
                log(f"Check this out: {folder_location}", logging.INFO)
                self.file_location = folder_location + "/data.json"
                self.chart["foldername"] = folder_location.split("/")[-1]
            # return False, getFolderLocation
            # return False, self.loc("editor.commandResults.common.notEnoughArgs")
        if os.path.exists(self.file_location):
            file_data = open(self.file_location, "w", encoding="utf8")
        else:
            file_data = open(self.file_location, "x", encoding="utf8")
        output = json.dumps(self.chart, indent=4)
        file_data.write(output)
        file_data.close()

    def setup_map(self):
        """Sets up a default map for ease of use."""
        self.chart = {
            "formatVersion": 1,
            "sound": None,
            "foldername": "",
            "icon": {
                "img": "",
                "txt": ""
            },
            "color_palette": [
                "fc220a",
                "fc9b0a",
                "f4fc0a",
                "0efc0a",
                "0afcfc",
                "0a36fc",
                "830afc",
                "0ab7fc",
                "fc0ab3",
                "72737c",
            ],
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
        self.end_note = -1

    def create_note(self, at_pos, key):
        print(term.clear)
        if "notes" in self.chart:
            new_note = {
                "type": "hit_object",
                "beatpos": [
                    int(at_pos//4),
                    round(at_pos%4, 5)
                ],
                "key": key,
                "screenpos": [
                    0.5,
                    0.5
                ],
                "color": 0
            }
            self.chart["notes"].append(new_note)
            self.chart["notes"] = sorted(
                self.chart["notes"],
                key=lambda d: d['beatpos'][0]*4+d['beatpos'][1]
            )
            if "end" in [note["type"] for note in self.chart["notes"]]:
                self.end_note = [note["type"] for note in self.chart["notes"]].index("end")
            note_obj = NoteObject(
                new_note,
                Game.get_bpm_map(self.chart),
                self.keys,
                self.palette
            )
            note_obj.playfield = self.playfield
            self.notes.append(note_obj)
            self.notes = sorted(
                self.notes,
                key=lambda d: d.beat_position
            )
            return self.chart["notes"].index(new_note)

    def create_text(self, at_pos = 0, lasts = 1, text = "", anchor = CENTER, align = ALIGN_CENTER):
        print(term.clear)
        if "notes" in self.chart:
            new_text = {
                "type": "text",
                "beatpos": [
                    int(at_pos//4),
                    round(at_pos%4, 5)
                ],
                "length": lasts,
                "text": text,
                "anchor": anchor,
                "align": align,
                "offset": [0,0],
            }
            self.chart["notes"].append(new_text)
            self.chart["notes"] = sorted(
                self.chart["notes"],
                key=lambda d: d['beatpos'][0]*4+d['beatpos'][1]
            )
            if "end" in [note["type"] for note in self.chart["notes"]]:
                self.end_note = [note["type"] for note in self.chart["notes"]].index("end")
            note_obj = TextObject(new_text, self.conduc.bpmChanges)
            note_obj.playfield = self.playfield
            self.notes.append(note_obj)

    del_confirm_enabled = False
    del_confirm_obj = -1
    async def draw_confirmDeletion(self):
        confirm_text = self.loc("editor.deleteConfirmPrompt")
        confirm_options = "[Y/Return] Yes    [N/Esc] No"
        print_box((term.width - 30)//2, (term.height - 5)//2, 30, 5)
        print_at((term.width - len(confirm_text))//2, (term.height - 5)//2+1, confirm_text)
        print_at((term.width - len(confirm_options))//2, (term.height - 5)//2+3, confirm_options)

    def input_confirmDeletion(self, val):
        if val == "y" or val.name == "KEY_ENTER":
            self.chart["notes"].remove(self.chart["notes"][self.del_confirm_obj])
            self.del_confirm_enabled = False
        elif val == "n" or val.name == "KEY_ESCAPE":
            self.del_confirm_enabled = False


    def set_end_note(self, at_pos):
        if self.end_note == -1:
            if EndLevelObject in [type(note) for note in self.notes]:
                self.end_note = [type(note) for note in self.notes].index(EndLevelObject)
            else:
                new_note_data = {
                    "type": "end",
                    "beatpos": [
                        int(at_pos//4),
                        round(at_pos%4, 5)
                    ]
                }

                new_note = EndLevelObject(new_note_data, Game.get_bpm_map(self.chart))
                self.notes.append(new_note)
                self.end_note = len(self.notes)-1
        else:
            self.chart["notes"][self.end_note]["beatpos"] = [int(at_pos//4), round(at_pos%4, 5)]

    def run_note_settings(self, note, note_id, option):
        if isinstance(note, NoteObject):
            if option == 0:
                self.key_panel.enabled = True
                self.key_panel.selected = note_id
                self.key_panel.key = note.key_index
                return True
            if option == 1:
                self.color_picker.enabled = not self.color_picker.enabled
                return False
            if option == 2:
                self.chart["notes"].remove(note)
                return True
        elif isinstance(note, TextObject):
            if option == 0:
                self.is_text_editing = True
                self.textEdit.textContent = note.text
                self.textobjectedited = note_id
                return True
            if option == 1:
                # note["color"] += 1
                # note["color"] %= len(colors)
                return False
            if option == 2:
                note.anchor += 1
                note.anchor %= 9
            if option == 3:
                self.chart["notes"].remove(note)
                return True

    def load_chart(self, chart_name, file = "data"):
        self.file_location = f"./charts/{chart_name}/{file}.json"
        if os.path.exists(self.file_location):
            print(term.clear)
            file_data = open(f"./charts/{chart_name}/{file}.json", encoding="utf8")
            self.chart = json.load(file_data)
            file_data.close()

            self.conduc.loadsong(self.chart)
            self.on_open()
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
    cheatsheet_enabled = False
    cheatsheet_seen = False
    tab_press_count = 0

    async def draw_cheatsheet(self):
        """Draws the cheatsheet you see when pressing TAB."""
        # normal mode
        sections = []
        if not self.command_line.command_mode:
            sections.append("basic")
            if self.notes:
                sections.append("objects")
                if isinstance(self.notes[self.selected_note], NoteObject):
                    sections.append("note")
                elif isinstance(self.notes[self.selected_note], TextObject):
                    sections.append("text")
        else:
            sections.append("command")
        # ypos = 0
        lines = []

        # check max
        max_key_len = 0
        max_val_len = 0
        for section in sections:
            for k,value in self.cheatsheet[section].items():
                if k.startswith("[line"):
                    lines.append((value,value))
                else:
                    key = self.loc(f"editor.cheatsheet.{k}")
                    val = str(value)
                    if isinstance(value, int):
                        val = self.layout[value].upper()
                    if isinstance(value, list):
                        val = value[0]
                        for arg in value[1:]: #Parse command line arguments
                            # Thank you, random stackoverflow post!
                            # https://stackoverflow.com/questions/21503865/how-to-denote-that-a-command-line-argument-is-optional-when-printing-usage
                            val += " "
                            if arg[0] is True: 			#Required arguments
                                val += "<"
                                if len(arg) > 2: #Prefix
                                    val += arg[2]
                                val += term.italic + arg[1] + self.reset_color + ">"
                            else: 						#Optional arguments
                                val += "["
                                if len(arg) > 2: #Prefix
                                    val += arg[2]
                                val += term.italic + arg[1] + self.reset_color + "]"
                    if len(term.strip_seqs(key)) > max_key_len:
                        max_key_len = len(term.strip_seqs(key))
                    if len(term.strip_seqs(val)) > max_val_len:
                        max_val_len = len(term.strip_seqs(val))

                    lines.append((key, val))

        # lines.insert(0, ("─"*(maxKeyLen+1), "─"*(maxValLen)))
        print_at(0, term.height-(7+min(len(lines)-1, 49)), "─"*(max_key_len+max_val_len+1) + "┐")

        # actual line writing
        for i in range(min(len(lines), 50)):
            print_at(0, term.height-(6+min(len(lines)-1, 49)-i),
        lines[i][0] + " " * (max_key_len-len(term.strip_seqs(lines[i][0]))+1) +
        (" " * (max_val_len-len(term.strip_seqs(lines[i][1]))) + lines[i][1]   ) + "│"
            )
        if self.tab_press_count < 2:
            print_at(0, term.height-(6+min(len(lines)+1,51)),
                     "Tip: The cheatsheet can change depending on the context!"
            )

    async def draw(self):
        # get background color
        self.set_background(self.get_background(self.conduc.current_beat))
        # print_at(0,term.height-5, self.reset_color+"-"*(term.width-1))

        #Timeline
        await self.timeline.draw(self)


        if self.metadata.enabled:
            await self.metadata.draw(self)


        if self.notes and not self.is_text_editing:
            self.selected_note %= len(self.notes)

            #PLAYFIELD
            await self.playfield.draw(self, self.notes)
        else:
            if not self.key_panel.enabled and not self.is_text_editing:
                text_nomaploaded = self.loc("editor.emptyChart")
                print_at(
                    int((term.width - len(text_nomaploaded))*0.5),
                    int(term.height*0.4),
                    self.reset_color+text_nomaploaded
                )

        if "bpmChanges" not in self.chart:
            self.chart["bpmChanges"] = []
        if self.chart["bpmChanges"] != []:
            for i in range(len(self.chart["bpmChanges"])):
                change = self.chart["bpmChanges"][i]
                remaining_beats = (change["atPosition"][0] + change["atPosition"][1]/4)\
                    - self.conduc.current_beat
                if int(remaining_beats*8+(term.width*0.1)) >= 0:
                    print_at(int(remaining_beats*8+(term.width*0.1)), term.height-3,
                             f"{self.reset_color}\U000f07da{self.reset_color}")

        if self.key_panel.enabled:
            if self.key_panel.selected == -1:
                text_key = self.loc("editor.newKey.creating")
            else:
                text_key = self.loc("editor.newKey.editing")
            await self.key_panel.draw(self,text_key,self.key_panel.key)

        self.command_line.draw(self.reset_color)

        if self.cheatsheet_enabled:
            await self.draw_cheatsheet()

        if not self.cheatsheet_seen:
            cheatsheettip = "[TAB] " + self.loc("editor.cheatsheet.cheatsheet")
            print_at(term.width-len(cheatsheettip), term.height-6, cheatsheettip)

        if self.color_picker.enabled:
            await self.color_picker.draw()

        if self.is_text_editing:
            await self.textEdit.draw()

        if self.del_confirm_enabled:
            await self.draw_confirmDeletion()

        if self.pause_menu.enabled:
            await self.pause_menu.draw()

        framerate_display = str(framerate()) + "fps"
        print_at(term.width-10, 0, term.rjust(framerate_display, 10) )

    @staticmethod
    def recreate_note_data(notes):
        """
        generates an array of the note's serialized data, 
        ready to use as a chart file's "notes"
        """
        notes_list:list = []
        for note in notes:
            notes_list.append(note.serialize())
        return notes_list



    async def handle_input(self):
        val = ''
        val = term.inkey(0, esc_delay=0)

        if self.playtest:
            for actual_note in self.notes:
                if isinstance(actual_note, NoteObject):
                    remaining_beats = actual_note.beat_position - self.conduc.current_beat
                    if not actual_note.played_sound and remaining_beats <= 0:
                        actual_note.check_beat_sound_timing(self.conduc.cur_time_sec)
                    if actual_note.played_sound and remaining_beats > 0:
                        actual_note.played_sound = False

        if self.pause_menu.enabled:
            self.pause_menu.input(val, self)
            return

        if self.metadata.enabled:
            self.metadata.handle_input(editor, val)
            return

        if self.is_text_editing:
            if val.name == "KEY_ESCAPE" and not self.textEdit.isSelectingText:
                self.is_text_editing = False
                self.notes[self.textobjectedited].text = self.textEdit.textContent
            else:
                self.textEdit.handle_input(val)
            return

        if self.color_picker.enabled:
            self.color_picker.note_selected = self.notes[self.selected_note]
            self.color_picker.input(val, self.palette)
            return

        if self.del_confirm_enabled:
            self.del_confirm_obj = self.selected_note
            self.input_confirmDeletion(val)
            return

        if self.command_line.command_mode:
            self.command_line.input(self, val)
            return

        # debug_val(val)
        if self.key_panel.enabled:
            self.key_panel.input(self, val)
            return

        if val.name == "KEY_TAB":
            self.cheatsheet_seen = True
            self.cheatsheet_enabled = not self.cheatsheet_enabled
            self.tab_press_count += 1
        if val.name != "KEY_ENTER" and val:
            self.command_line.command_footer_enabled = False
        if val == ":":
            self.command_line.command_mode = True
            self.command_line.command_string = ""
        if val == " ":
            self.background_changes = Game.load_bg_changes(self.chart["notes"])
            if not self.playtest:
                log("Starting on beat:" + str(self.conduc.current_beat), logging.INFO)
                for actual_note in self.notes:
                    remaining_beats = actual_note.beat_position - self.conduc.current_beat
                    if remaining_beats < 0:
                        self.dontBeat.append(actual_note)
                self.conduc.startAt(self.conduc.current_beat)
            else:
                self.conduc.stop()
                log("Ending on beat:" + \
                    str(round(self.conduc.current_beat/(self.snap/4)) * (self.snap/4)),
                    logging.INFO
                )
                self.conduc.current_beat = round(
                    self.conduc.current_beat/(self.snap/4)) * (self.snap/4)
            self.playtest = not self.playtest
        if val.name == "KEY_ESCAPE":
            self.pause_menu.enabled = True
        if val == "z":
            self.key_panel.enabled = True
            self.key_panel.selected = -1
            self.key_panel.key = 0
            print_at(0,int(term.height*0.4), term.clear_eol)
        if val == "Z":
            self.set_end_note(self.conduc.current_beat)
        if val == "t":
            self.conduc.metronome = not self.conduc.metronome
        if val in ["9"]:
            self.selected_snap -= 1
            self.selected_snap %= len(self.snapPossible)
            self.snap = self.snapPossible[self.selected_snap]
        if val in ["0"]:
            self.selected_snap += 1
            self.selected_snap %= len(self.snapPossible)
            self.snap = self.snapPossible[self.selected_snap]
        await self.timeline.input(self, val)

        if len(self.notes) > 0:
            actual_note:GameplayObject = self.notes[self.selected_note]
            # json_note = self.chart["notes"][self.selected_note]

            if val == "u":
                self.conduc.current_beat = max(
                    self.conduc.current_beat - (1/self.snap)*4, 0
                )
                actual_note.beat_position = self.conduc.current_beat
            if val == "i":
                self.conduc.current_beat += (1/self.snap)*4
                actual_note.beat_position = self.conduc.current_beat

            if val == "d" and isinstance(actual_note, NoteObject):
                self.selected_note = self.create_note(
                    actual_note.beat_position,
                    actual_note.key_index
                )
                self.notes[self.selected_note] = copy.deepcopy(actual_note)
            if val == "d" and isinstance(actual_note, TextObject):
                new_note = copy.deepcopy(actual_note)
                self.notes.append(new_note)
                self.notes = sorted(
                    self.notes,
                    key=lambda d: d.beat_position if hasattr(d, "beat_position") else -1.0)
                if len([True for note in self.notes if isinstance(note, EndLevelObject)]) > 0:
                    self.end_note = [
                        note.__class__.__name__ for note in self.notes
                    ].index("EndLevelObject")
                self.selected_note = self.notes.index(new_note)

            if isinstance(actual_note, NoteObject) and val:
                # calculate new x/y position
                direc = val.lower()
                multiplier = (3 if direc in "hl" else 2) if val.isupper() else 1
                if val in "hH":
                    actual_note.position.x = max(round(
                        actual_note.position.x - multiplier/self.playfield.size.x, 4
                    ), 0)
                if val in "jJ":
                    actual_note.position.y = min(round(
                        actual_note.position.y + multiplier/self.playfield.size.y, 4
                    ), 1)
                if val in "kK":
                    actual_note.position.y = max(round(
                        actual_note.position.y - multiplier/self.playfield.size.y, 4
                    ), 0)
                if val in "lL":
                    actual_note.position.x = min(round(
                        actual_note.position.x + multiplier/self.playfield.size.x, 4
                    ), 1)
                if val == "e":
                    self.run_note_settings(actual_note, self.selected_note, 0)
                if val == "E":
                    self.color_picker.enabled = not self.color_picker.enabled
                if val in ("x", "X"):
                    if isinstance(actual_note.color_string, int):
                        actual_note.set_color_from_palette(
                            (actual_note.color_string+{"x":1, "X":-1}[val])\
                                %len(self.palette),
                            self.palette
                        )
                    else:
                        actual_note.set_color_from_palette(
                            {"x":0, "X":len(self.palette)-1}[val], self.palette
                        )
            if isinstance(actual_note, TextObject) and val:
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
                    self.run_note_settings(actual_note, self.selected_note, 0)

                if val == "c":
                    self.run_note_settings(actual_note, self.selected_note, 2)
            if isinstance(actual_note, BackgroundColorObject) and val:
                if val == "e":
                    self.color_picker.enabled = not self.color_picker.enabled


            if val.name in ("KEY_DELETE", "KEY_BACKSPACE"):
                self.del_confirm_enabled = True
                # self.mapToEdit["notes"].remove(note)

    def on_open(self):
        self.keys = LayoutManager.current_layout()
        if not self.chart:
            self.setup_map()
        else:
            if "palette" in self.chart:
                self.palette = Game.setup_palette(self.chart["palette"])
            else:
                self.palette = colors
            Game.setup_notes(self, self.chart["notes"], Vector2i(0,-1))

    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    editor = Editor()
    # loadedMenus["Editor"] = editor
    editor.layoutname = "qwerty"
    editor.layout = Game.setup_keys(None, editor.layoutname)
    editor.loop()
