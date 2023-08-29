import os
import shutil
import copy
from src.termutil import term, print_at
from src.textbox import textbox_logic
from src.scenes.game import Game

class EditorCommandLine:

    #Command mode
    command_mode = False
    command_string = ""
    command_select_pos = 0
    commandAutoMode = False
    commandAutoPropositions = []
    command_footer_message = ""
    command_footer_enabled = False
    command_history = []
    command_history_cur = 0
    cached_command = ""

    def run_command(self, editor, command = ""):
        cmd_argv = command.split(" ")
        print_at(0,term.height-2, term.clear_eol)
        # :q - Quit
        if cmd_argv[0] == "q!" or (cmd_argv[0] == "q" and not editor.needsSaving):
            editor.turn_off = True
            return True, ""

        elif cmd_argv[0] == "loop" or cmd_argv[0] == "lp":
            if len(cmd_argv) < 2:
                cmd_argv = "1"
            return None, "START_LOOP:"+cmd_argv[1]

        elif cmd_argv[0] == "cl":
            return None, "END_LOOP"

        # :w - Write (Save) | 1 optional argument (where to save it)
        elif cmd_argv[0] == "w":
            folder = cmd_argv[1] if len(cmd_argv) > 1 else ""
            filename = cmd_argv[2] if len(cmd_argv) > 2 else ""
            editor.save(folder, filename)
            return True, editor.loc("editor.commandResults.save")

        # :wq - Save and Quit | 1 optional argument (where to save it)
        elif cmd_argv[0] == "wq!" or (cmd_argv[0] == "wq" and not editor.needsSaving):
            folder = cmd_argv[1] if len(cmd_argv) > 1 else ""
            filename = cmd_argv[2] if len(cmd_argv) > 2 else ""
            editor.save(folder, filename)
            editor.turn_off = True
            return True, editor.loc("editor.commandResults.save")

        # :ar - Approach Rate
        elif cmd_argv[0] == "ar":
            if len(cmd_argv) >= 2:
                if cmd_argv[1].replace(".", "", 1).isdigit():
                    editor.chart["approachRate"] = float(cmd_argv[1])
                    return True, "[ar_set_to]"+cmd_argv[1]
                else:
                    return False, "[ar_not_a_number]"

        # :diff - Difficulty
        elif cmd_argv[0] == "diff":
            if len(cmd_argv) >= 2:
                if cmd_argv[1].isdigit():
                    editor.chart["difficulty"] = int(cmd_argv[1])
                else:
                    editor.chart["difficulty"] = cmd_argv[1]
                return True, "[diff_set_to]"+cmd_argv[1]

        # :o - Open
        elif cmd_argv[0] == "o":
            if len(cmd_argv) == 2:
                file_exists = editor.load_chart(cmd_argv[1])
                if not file_exists:
                    return file_exists, editor.loc("editor.commandResults.open.notFound")
                else:
                    return file_exists, editor.loc("editor.commandResults.open.success")
            elif len(cmd_argv) == 3:
                editor.load_chart(cmd_argv[1], cmd_argv[2])
            else:
                if len(cmd_argv) < 2:
                    return False, editor.loc("editor.commandResults.common.notEnoughArgs")
                else:
                    return False, editor.loc("editor.commandResults.common.tooManyArgs")
        
        # :p - Place
        elif cmd_argv[0] == "p":
            if len(cmd_argv) > 1:
                if cmd_argv[1].isdigit():
                    editor.selectedNote = editor.create_note(editor.conduc.current_beat, int(cmd_argv[1]))
                    return True, editor.loc("editor.commandResults.note.success")
            else:
                editor.keyPanelEnabled = True
                editor.keyPanelSelected = -1
                editor.keyPanelKey = 0
                return True, ""

        # :song - Change song
        elif cmd_argv[0] == "song":
            if editor.file_location == "":
                return False, "You need to save this file first! To do that, type :w <some_chart_name>"
            if len(cmd_argv) > 1:
                if os.path.exists(cmd_argv[1]) and cmd_argv[1].split(".")[-1] in ["ogg", "mp3", "wav"]:
                    soundFileLocation = cmd_argv[1]
                    editor.chart["sound"] = soundFileLocation.split('/')[-1]
                    shutil.copyfile(soundFileLocation, f"./charts/{editor.chart['foldername']}/{soundFileLocation.split('/')[-1]}")
                    editor.conduc.loadsong(editor.chart)
            else:
                editor.file_browser.fileExtFilter = "(?:\\.ogg$)|(?:\\.wav$)|(?:\\.mp3$)"
                editor.file_browser.load_folder(os.getcwd())
                editor.file_browser.caption = "Select a song"
                editor.file_browser.turnOff = False
                soundFileLocation = editor.file_browser.loop()
                if soundFileLocation != "?":
                    editor.chart["sound"] = soundFileLocation.split('/')[-1]
                    try:
                        shutil.copyfile(soundFileLocation, f"./charts/{editor.chart['foldername']}/{soundFileLocation.split('/')[-1]}")
                    except shutil.SameFileError:
                        pass
                    editor.conduc.loadsong(editor.chart)
                else:
                    return False, "File selection aborted."

        # :off - Change song offset
        elif cmd_argv[0] == "off":
            offset = 0
            if len(cmd_argv) > 1:
                offset = float(cmd_argv[1])
            else:
                editor.calib.startCalibSong(editor.chart)
                offset = editor.calib.init(False)
                editor.calib.conduc.stop()
                editor.calib.turnOff = False
            offset = round(offset, 6) # 6 is completely arbitrary, it's mostly to deal with floating point fuckery
            editor.chart["offset"] = offset
            editor.conduc.setOffset(offset)
            return True, f"New offset: {offset}"

        # :s - Snap
        elif cmd_argv[0] == "s":
            if len(cmd_argv) > 1:
                if cmd_argv[1].replace('.', '', 1).isdigit():
                    editor.snap = float(cmd_argv[1])

        # :m - Move cursor
        elif cmd_argv[0] == "m":
            if len(cmd_argv) > 1:
                if cmd_argv[1].startswith("~"):
                    editor.conduc.current_beat += float(cmd_argv[1].replace("~", ""))
                else:
                    editor.conduc.current_beat = float(cmd_argv[1])

        # :mt - Metadata
        elif cmd_argv[0] == "mt":
            if len(cmd_argv) >= 3:
                value_changed = ""
                changed_to = ""
                if cmd_argv[1] in ["title", "t"]:
                    editor.chart["metadata"]["title"] = " ".join(cmd_argv[2:])
                    value_changed = "title"
                    changed_to = editor.chart["metadata"]["title"]
                if cmd_argv[1] in ["artist", "a"]:
                    editor.chart["metadata"]["artist"] = " ".join(cmd_argv[2:])
                    value_changed = "artist"
                    changed_to = editor.chart["metadata"]["artist"]
                if cmd_argv[1] in ["author", "charter", "au", "c"]:
                    editor.chart["metadata"]["author"] = " ".join(cmd_argv[2:])
                    value_changed = "author"
                    changed_to = editor.chart["metadata"]["author"]
                if cmd_argv[1] in ["description", "desc", "d"]:
                    editor.chart["metadata"]["description"] = " ".join(cmd_argv[2:])
                    value_changed = "description"
                    changed_to = editor.chart["metadata"]["description"]
                return True, editor.loc("editor.commandResults.meta.success").format(value_changed, changed_to)
            elif len(cmd_argv) == 2:
                return_message = ""
                if cmd_argv[1] in ["title", "t"]:
                    return_message = editor.chart["metadata"]["title"]
                if cmd_argv[1] in ["artist", "a"]:
                    return_message = editor.chart["metadata"]["artist"]
                if cmd_argv[1] in ["author", "charter", "au", "c"]:
                    return_message = editor.chart["metadata"]["author"]
                if cmd_argv[1] in ["description", "desc", "d"]:
                    return_message = editor.chart["metadata"]["description"]
                return True, return_message

        # :bpm - Change BPM
        elif cmd_argv[0] == "bpm":
            if len(cmd_argv) == 2:
                newbpm = 120
                if cmd_argv[1].find(".") != -1:
                    newbpm = float(cmd_argv[1])
                else:
                    newbpm = int(cmd_argv[1])

                editor.chart["bpm"] = newbpm
                editor.conduc.bpm = newbpm

                return True, ""
            elif len(cmd_argv) > 2:
                return False, editor.loc("editor.commandResults.common.tooManyArgs")
            return False, editor.loc("editor.commandResults.common.notEnoughArgs")

        elif cmd_argv[0] == "bpmc":
            if len(cmd_argv) == 2:
                newbpm = 120
                if cmd_argv[1].find(".") != -1:
                    newbpm = float(cmd_argv[1])
                else:
                    newbpm = int(cmd_argv[1])

                new_bpm_object = {
                    "atPosition": [
                        editor.conduc.current_beat, 
                        (editor.conduc.current_beat%1)*4
                    ],
                    "toBPM": newbpm
                }

                editor.chart["bpmChanges"].append(new_bpm_object)
                editor.conduc.bpmChanges.append(new_bpm_object)

                return True, ""
            elif len(cmd_argv) > 2:
                return False, editor.loc("editor.commandResults.common.tooManyArgs")
            return False, editor.loc("editor.commandResults.common.notEnoughArgs")

        elif cmd_argv[0] == "delbpmc":
            if len(cmd_argv) == 2:
                editor.conduc.bpmChanges.remove(editor.chart["bpmChanges"][int(cmd_argv[1])])
                editor.chart["bpmChanges"].remove(editor.chart["bpmChanges"][int(cmd_argv[1])])

        # :cp - Copy
        elif cmd_argv[0] == "cp":
            if len(cmd_argv) == 3:
                #XX-YY : Range of notes to copy
                range_to_copy = cmd_argv[1].split("-")
                if len(range_to_copy) < 2:
                    return False, editor.loc("editor.commandResults.common.notEnoughArgs")

                notes_to_copy = [copy.deepcopy(editor.chart["notes"][i]) \
                               for i in range(int(range_to_copy[0]), int(range_to_copy[1])+1)]
                #BB : How many beats to offset it by?

                for (_,note) in enumerate(notes_to_copy):
                    note["beatpos"][1] += float(cmd_argv[2])
                    note["beatpos"][0] += note["beatpos"][1]//4
                    note["beatpos"][1] %= 4
                    editor.chart["notes"].append(note)
                editor.chart["notes"] = sorted(
                    editor.chart["notes"],
                    key=lambda d: d['beatpos'][0]*4+d['beatpos'][1]
                )
                if "end" in [note["type"] for note in editor.chart["notes"]]:
                    editor.end_note = [note["type"] for note in editor.chart["notes"]].index("end")
                return True, ""

            elif len(cmd_argv) > 3:
                return False, editor.loc("editor.commandResults.common.tooManyArgs")
            return False, editor.loc("editor.commandResults.common.notEnoughArgs")

        elif cmd_argv[0] == "t":
            if len(cmd_argv) > 1:
                editor.create_text(editor.conduc.current_beat, text=" ".join(cmd_argv[1:]))
                return True, editor.loc("editor.commandResults.note.success")
            return False, "[cannot create empty text]"

        elif cmd_argv[0] == "c":
            note = editor.chart["notes"][editor.selectedNote]
            if cmd_argv[1].startswith("#") and len(cmd_argv[1].replace("#", "", 1)) == 6:
                note["color"] = cmd_argv[1].replace("#", "", 1)
            elif cmd_argv[1].isDigit():
                note["color"] = int(cmd_argv[1])

        elif cmd_argv[0] == "sel":
            if cmd_argv[1].startswith("~"):
                editor.selectedNote += int(cmd_argv[1].replace("~", ""))
            else:
                editor.selectedNote = int(cmd_argv[1])

        elif cmd_argv[0] == "del":
            if len(cmd_argv) < 2:
                editor.notes.remove(editor.notes[editor.selectedNote])
            else:
                editor.notes.remove(editor.notes[int(cmd_argv[1])])

        elif cmd_argv[0] == "bgc":
            if len(cmd_argv) > 1:
                new_note = {
                    "type": "bg_color",
                    "beatpos": [
                        int(editor.conduc.current_beat//4),
                        round(editor.conduc.current_beat%4, 5)
                    ],
                    "color": cmd_argv[1]
                }
                editor.chart["notes"].append(new_note)
                editor.background_changes = Game.load_bg_changes(editor.chart)
                return True, "this is gonna crash the game isn't it"

        elif cmd_argv[0] == "pal":
            if len(cmd_argv) == 2:
                if int(cmd_argv[1]) > 0:
                    editor.color_picker.palette_edit_mode = True
                    editor.color_picker.palette_selected = int(cmd_argv[1])
                    editor.color_picker.enabled = True
                    editor.color_picker.setup_color(editor.palette[int(cmd_argv[1])].hex_value)

        else:
            if len(cmd_argv[0]) > 128:
                return False, editor.loc("editor.commandResults.common.tooLong")
            return False, editor.loc("editor.commandResults.common.notFound")

        return True, ""

    def input(self, editor, val):
        if val.name == "KEY_TAB":
            editor.cheatsheet_enabled = not editor.cheatsheet_enabled
        if val.name == "KEY_UP":
            if self.command_history_cur == 0:
                self.cached_command = self.command_string
            if self.command_history_cur < len(self.command_history):
                self.command_history_cur+=1
                self.command_string = self.command_history[
                    len(self.command_history) - (self.command_history_cur)]
        if val.name == "KEY_DOWN":
            if self.command_history_cur > 0:
                self.command_history_cur-=1
            if self.command_history_cur == 0:
                self.command_string = self.cached_command
            else:
                self.command_string = self.command_history[
                    len(self.command_history) - (self.command_history_cur)]
        if val.name == "KEY_ESCAPE":
            self.command_mode = False
            self.command_string = ""
            self.command_history_cur = 0
            self.cached_command = ""
        elif val.name == "KEY_ENTER":
            self.command_history_cur = 0

            #Add the command string to the front, remove it anywhere else if it already exists
            if self.command_string in self.command_history:
                self.command_history.remove(self.command_string)
            self.command_history.append(self.command_string)
            self.cached_command = ""
            split_commands = self.command_string.split(";;")
            self.command_footer_message = ""
            if len(split_commands) > 1:
                command_results = []
                errors = []
                index = 0
                for comm in split_commands:
                    is_valid, error_string = self.run_command(editor, comm)
                    if is_valid is None: #LOOP CHECK
                        if error_string.split(":")[0] == "START_LOOP":
                            end_loop = index+1
                            for i in split_commands[index+1:]:
                                end_loop += 1
                                if i == "cl": #CLOSE LOOP
                                    # splitCommands = splitCommands[:endLoop]+splitCommands[endLoop+1:] #Remove cl
                                    # endLoop -= 1
                                    break
                            to_loop = split_commands[index+1:end_loop]
                            for _ in range(int(error_string.split(":")[1]) - 1):
                                count = index
                                for loopcomm in to_loop:
                                    if loopcomm != "cl":
                                        split_commands.insert(index+1+count, loopcomm)
                                        count+=1
                    else:
                        command_results.append([is_valid, error_string])
                    index += 1
                for (_,rsult) in enumerate(command_results):
                    col = term.on_green
                    if not rsult[0]:
                        errors.append(rsult[1])
                        col = term.on_red
                    self.command_footer_message += col + "*"
                self.command_footer_message += editor.reset_color + "     "
                if len(errors) != 0:
                    self.command_footer_message += term.on_red+errors[-1]
                self.command_mode = False
                self.command_string = ""

            else:
                is_valid, error_string = self.run_command(editor, self.command_string)
                self.command_mode = False
                self.command_string = ""
                if is_valid is not None:
                    if is_valid:
                        if error_string != "":
                            self.command_footer_message = term.on_green+error_string
                    else:
                        self.command_mode = False
                        self.command_string = ""
                        self.command_footer_message = term.on_red+error_string
            self.command_footer_enabled = True
        else:
            if self.command_string == "" and val.name == "KEY_BACKSPACE":
                self.command_mode = False
                print_at(0,term.height-2, term.clear_eol+editor.reset_color)
            self.command_string, self.command_select_pos = textbox_logic(
                self.command_string,
                self.command_select_pos,
                val, editor.autocomplete
            )

    def draw(self, reset_color):
        if self.command_mode:
            print_at(0,term.height-2, reset_color+":"+self.command_string+term.clear_eol)
            char_at_cursor = ""
            if len(self.command_string) != 0:
                if self.command_select_pos != 0:
                    char_at_cursor = self.command_string[
                        len(self.command_string)-(self.command_select_pos)
                    ]
                else:
                    char_at_cursor = " "
                print_at(
                    len(self.command_string)-self.command_select_pos + 1,
                    term.height-2,
                    term.underline + char_at_cursor + reset_color
                )
        elif self.command_footer_enabled:
            print_at(0,term.height-2, self.command_footer_message + reset_color)
