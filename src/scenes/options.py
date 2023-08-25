from src.termutil import print_at, print_lines_at, term
from src.scenes.base_scene import BaseScene
from src.layout import LayoutManager
from src.translate import LocaleManager
from src.scene_manager import SceneManager
from src.options import OptionsManager
from src.textbox import textbox_logic

# Options menu
class Options(BaseScene):
    turnOff = False
    deltatime = 0
    selectedItem = 0
    menuOptions = [
        {"var": "globalOffset",		"type":"intField",	"displayName": "Global offset (ms)", "isOffset": True, "snap": 0.001},
        {"var": "songVolume",		"type":"intSlider",	"displayName": "Song volume", "min": 0, "max": 100, "snap": 5, "mult": 100},
        {"var": "hitSoundVolume",	"type":"intSlider",	"displayName": "Hitsound volume", "min": 0, "max": 100, "snap": 5, "mult": 100},
        {"var": "lang",				"type":"enum", 		"displayName": "Language", "populatedValues": LocaleManager.locale_names, "displayedValues": LocaleManager.locale_names},
        {"var": "nerdFont",			"type":"bool", 		"displayName": "Enable Nerd Font display"},
        {"var": "textImages",		"type":"bool", 		"displayName": "Use images as thumbnails"},
        {"var": "shortTimeFormat",	"type":"bool", 		"displayName": "Shorten relative time formatting"},
        {"var": "layout", 			"type":"enum", 		"displayName": "Layout", "populatedValues": LayoutManager.layoutNames},
        {"var": "displayName", 		"type":"strField",	"displayName": "Local username", "default": "Player"},
        {"var": "bypassSize",		"type":"bool",		"displayName": "Bypass minimal terminal size"},
    ]
    enumInteracted = -1
    curEnumValue = -1
    suggestedOffset = 0
    isPickingOffset = False
    goBack = False

    string_interacted = -1
    current_input = ""
    string_cursor = 0

    def populate_enum(self):
        displayed_values = [LocaleManager.locales[loc]("lang") for loc in LocaleManager.locales]
        self.menuOptions[3]["populatedValues"] = LocaleManager.locale_names
        self.menuOptions[3]["displayedValues"] = displayed_values
        self.menuOptions[7]["displayedValues"] = LayoutManager.layoutNames
        self.menuOptions[7]["populatedValues"] = LayoutManager.layoutNames

    def translate(self):
        for optn in self.menuOptions:
            key = f"options.{optn['var']}"
            optn["displayName"] = self.loc(key)

    def moveBy(self, x):
        # print(term.clear)
        self.selectedItem = (self.selectedItem + x)%len(self.menuOptions)

    def volume(self, volType=0, value = 1):
        if volType == 0:
            self.conduc.setVolume(value)
            SceneManager["Game"].conduc.setVolume(value)
        elif volType == 1:
            self.conduc.setMetronomeVolume(value)
            SceneManager["Game"].beat_sound_volume = value
            
    
    # --- INTERACT FUNCTIONS ---
    def interact_bool(self, boolOption):
        OptionsManager.set(boolOption["var"], not OptionsManager[boolOption["var"]])

    def interact_enum(self, enum, curChoice):
        '''curChoice is an integer.'''
        OptionsManager.set(enum["var"], enum["populatedValues"][curChoice])
        if enum["var"] == "lang":
            LocaleManager.change_locale(enum["populatedValues"][curChoice])
            self.loc = LocaleManager.current_locale()
            # print(term.clear)
            self.translate()
    
    def interact_string(self, curChoice):
        self.string_interacted = curChoice
        self.current_input = OptionsManager[self.menuOptions[curChoice]["var"]]


    # --- END INTERACT FUNC ---

    def saveOptions(self):
        OptionsManager.save_to_file()
        
    async def draw(self):
        maxLength = 0

        for option in self.menuOptions:
            if len(option["displayName"]) > maxLength:
                maxLength = len(option["displayName"])

        for (i,optn) in enumerate(self.menuOptions):
            titleLen = len(optn['displayName'])
            leType = optn["type"]
            leVar = optn["var"]
            #DisplayName
            if self.selectedItem == i and not self.isPickingOffset:
                if int(self.conduc.current_beat) % 2 == 1:
                    print_at(0,i*2 + 3, term.reverse + f"- {optn['displayName']}{' '*(maxLength-titleLen+1)}>" + self.reset_color)
                else:
                    print_at(0,i*2 + 3, self.reset_color  + f"- {optn['displayName']}{' '*(maxLength-titleLen+1)}>" + self.reset_color)
            else:
                print_at(0,i*2 + 3, self.reset_color + f" {optn['displayName']}{' '*(maxLength-titleLen+1)}  ")
            if leType == "intField":
                if self.selectedItem == i and optn["isOffset"]:
                    print_at(maxLength + 6, i*2+3, str(OptionsManager[leVar] * 1000) + (" "*int(term.width*0.2)) + self.loc("options.calibrationTip"))
                else:
                    print_at(maxLength + 6, i*2+3, str(OptionsManager[leVar] * 1000))
            if leType == "intSlider":
                print_at(maxLength + 6, i*2+3, f"{str(int(OptionsManager[leVar] * 100))}%")
                print_at(maxLength + 12, i*2+3, f"{'━'*int(max((term.width*0.7) - (maxLength + 16), 20)*OptionsManager[leVar])}⏺")
            if leType == "enum":
                if self.enumInteracted == i:
                    print_at(maxLength + 6, i*2+3, term.reverse + "{ " + \
                             self.menuOptions[i]["displayedValues"][self.menuOptions[i]["populatedValues"].index(OptionsManager[leVar])] + " }" +\
                                self.reset_color + (" "*6) + str(self.menuOptions[i]["displayedValues"]) + term.clear_eol)
                else:
                    if self.selectedItem == i and self.menuOptions[i]["var"] == "layout":
                        print_at(maxLength + 6, i*2+3, "[" + OptionsManager[leVar] + "] ⌄" + (" "*int(term.width*0.2)) + self.loc("options.layoutTip"))
                    elif "displayedValues" in self.menuOptions[i]:
                        print_at(maxLength + 6, i*2+3, "[" + self.menuOptions[i]["displayedValues"][self.menuOptions[i]["populatedValues"].index(OptionsManager[leVar])] + "] ⌄")
                    else:
                        print_at(maxLength + 6, i*2+3, "[" + OptionsManager[leVar] + "] ⌄")
            if leType == "bool":
                if OptionsManager[leVar]:
                    print_at(maxLength + 6, i*2+3, "☑")
                else:
                    print_at(maxLength + 6, i*2+3, "☐")
            if leType == "strField":
                if self.selectedItem == i:
                    if self.string_interacted == i:
                        print_at(maxLength + 6, i*2+3, term.underline + self.current_input + self.reset_color)
                    else:
                        print_at(maxLength + 6, i*2+3, term.reverse + OptionsManager[leVar] + self.reset_color)
                else:
                    print_at(maxLength + 6, i*2+3, self.reset_color + OptionsManager[leVar])

        if self.menuOptions[self.selectedItem]["var"] == "layout":
            text = f"┌───{'┬───'*9}┐\n" + "".join(\
                ["".join([
                    f"│ {key} " for key in LayoutManager[OptionsManager["layout"]]
                ][10*i:10*(i+1)]) + f"│\n├───{'┼───'*9}┤\n" for i in range(2)]\
            ) + "".join([f"│ {key} " for key in LayoutManager[OptionsManager["layout"]]][20:30]) + f"│\n└───{'┴───'*9}┘\n"
            print_lines_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2), term.height-10, text)

        if self.isPickingOffset:
            text_offsetConfirm = f"Do you want to use the new following offset: {int(self.suggestedOffset*(10**3))}ms?"
            print_at(int((term.width - len(text_offsetConfirm)) * 0.5), int(term.height*0.5)-1, text_offsetConfirm)
            print_at(int(term.width * 0.4)-3, int(term.height*0.5)+1, term.reverse+"Yes [Y]"+self.reset_color)
            print_at(int(term.width * 0.6)-3, int(term.height*0.5)+1, term.reverse+"No [N] "+self.reset_color)

    def enterPressed(self):
        self.populate_enum()
        selectedOption = self.menuOptions[self.selectedItem]
        if selectedOption["type"] == "bool":
            self.interact_bool(selectedOption)
        if selectedOption["type"] == "enum":
            if selectedOption["populatedValues"] != []:
                self.enumInteracted = self.selectedItem
                self.curEnumValue = selectedOption["populatedValues"].index(OptionsManager[selectedOption["var"]])
            else:
                self.populate_enum()
        if selectedOption["type"] == "strField":
            self.interact_string(self.selectedItem)
            

    async def handle_input(self):
        """
        This function is called every update cycle to get keyboard input.
        (Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
        """
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if self.string_interacted > -1:
            option_variable = self.menuOptions[self.string_interacted]["var"]
            if val.name == "KEY_ENTER":
                if self.current_input == "":
                    if OptionsManager[option_variable] == "":
                        OptionsManager.set(option_variable, self.menuOptions[self.string_interacted]["default"])
                    self.string_interacted = -1
                else:
                    OptionsManager.set(option_variable, self.current_input)
                    self.string_interacted = -1
                self.current_input = ""
            elif val.name == "KEY_ESCAPE":
                self.string_interacted = -1
                self.current_input = ""
            else:
                self.current_input, self.string_cursor = textbox_logic(self.current_input, self.string_cursor, val)

        elif self.isPickingOffset:
            if val == "y":
                option_variable = self.menuOptions[self.selectedItem]["var"]
                OptionsManager.set(option_variable, round(self.suggestedOffset,3))
                self.isPickingOffset = False
                # print(term.clear)
            if val == "n":
                self.isPickingOffset = False
                self.suggestedOffset = 0
                # print(term.clear)
        else:
            if self.enumInteracted == -1:
                if val.name == "KEY_DOWN" or val == "j":
                    self.moveBy(1)
                if val.name == "KEY_UP" or val == "k":
                    self.moveBy(-1)
                if (val.name == "KEY_RIGHT" and self.menuOptions[self.selectedItem]["type"] not in ["intField", "intSlider"]) or val.name == "KEY_ENTER":
                    self.enterPressed()
                if val.name == "KEY_LEFT" and self.menuOptions[self.selectedItem]["type"] in ["intField", "intSlider"]:
                    option_variable = self.menuOptions[self.selectedItem]["var"]

                    new_value = OptionsManager[option_variable]
                    if "min" in self.menuOptions[self.selectedItem]:
                        new_value *= self.menuOptions[self.selectedItem]["mult"]
                        new_value -= self.menuOptions[self.selectedItem]["snap"]
                        new_value = min(int(new_value*100)/100, self.menuOptions[self.selectedItem]["max"])
                        new_value /= self.menuOptions[self.selectedItem]["mult"]
                        volume_type = 0
                        if option_variable == "hitSoundVolume":
                            volume_type = 1
                        self.volume(volume_type, new_value)
                    else:
                        new_value -= self.menuOptions[self.selectedItem]["snap"]
                    OptionsManager.set(option_variable, new_value)
                if val.name == "KEY_RIGHT" and self.menuOptions[self.selectedItem]["type"] in ["intField", "intSlider"]:
                    option_variable = self.menuOptions[self.selectedItem]["var"]
                    new_value = OptionsManager[option_variable]
                    if "min" in self.menuOptions[self.selectedItem]:
                        new_value *= self.menuOptions[self.selectedItem]["mult"]
                        new_value += self.menuOptions[self.selectedItem]["snap"]
                        new_value = min(int(new_value*100)/100, self.menuOptions[self.selectedItem]["max"])
                        new_value /= self.menuOptions[self.selectedItem]["mult"]
                        volume_type = 0
                        if option_variable == "hitSoundVolume":
                            volume_type = 1
                        self.volume(volume_type, new_value)
                    else:
                        new_value += self.menuOptions[self.selectedItem]["snap"]
                    OptionsManager.set(option_variable, new_value)
                if val.name == "KEY_ESCAPE":
                    self.saveOptions()
                    self.turn_off = True
                    SceneManager.change_scene("Titlescreen")
                    # print(term.clear)
                if val == "c":
                    self.saveOptions()
                    self.turn_off = True
                    self.goBack = True
                    self.selectedItem = 0
                    self.conduc.stop()
                    SceneManager["Calibration"].turn_off = False
                    SceneManager["Calibration"].startCalibGlobal()
                    self.suggestedOffset = SceneManager["Calibration"].init(False)
                    self.isPickingOffset = True
                    SceneManager["Calibration"].conduc.stop()
                    SceneManager["Calibration"].hitCount = 0
                    SceneManager["Calibration"].hits = []
                    SceneManager["Calibration"].totalOffset = 0
                    self.conduc.startAt(0)
                if val == "l":
                    self.saveOptions()
                    self.turn_off = True
                    self.goBack = True
                    self.selectedItem = 4

                    custom_layout = ["╳" for _ in range(30)]
                    if "custom" in LayoutManager.layoutNames:
                        custom_layout = LayoutManager["custom"]
                    SceneManager["LayoutEditor"].turn_off = False
                    SceneManager["LayoutEditor"].layout = custom_layout
                    SceneManager.change_scene("LayoutEditor")


            else:
                if val.name == "KEY_DOWN" or val == "j":
                    self.curEnumValue = (self.curEnumValue-1) % \
                        len(self.menuOptions[self.enumInteracted]["populatedValues"])
                    self.interact_enum(self.menuOptions[self.enumInteracted], self.curEnumValue)
                if val.name == "KEY_UP" or val == "k":
                    self.curEnumValue = (self.curEnumValue+1) % \
                        len(self.menuOptions[self.enumInteracted]["populatedValues"])
                    self.interact_enum(self.menuOptions[self.enumInteracted], self.curEnumValue)
                if val.name in ("KEY_ESCAPE", "KEY_ENTER"):
                    self.enumInteracted = -1


    def loop(self):
        super().loop()

        if self.goBack is True:
            self.goBack = False
            self.turn_off = False
            self.loop()
