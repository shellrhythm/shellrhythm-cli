
import json
from src.scenes.base_scene import BaseScene
from src.scene_manager import SceneManager
from src.options import OptionsManager
from src.termutil import print_at, term

class Credits(BaseScene):
    """The class that displays game credits."""
    turnOff = False
    credits_data = []
    creditsPath = "./assets/credits.json"
    selected_item = 0
    state_viewing_profile = False

    async def draw(self):
        max_length = 0

        for option in self.credits_data:
            if len(option["role"]) > max_length:
                max_length = len(option["role"])

        for (i,data_line) in enumerate(self.credits_data):
            if self.selected_item == i:
                print_at(0,(i*2)+3,term.reverse + term.bold + "    " +
                         (" "*(max_length-len(data_line["role"]))) + data_line["role"]
                         + " " + self.reset_color + term.underline + data_line["name"]
                         + self.reset_color
                        )
            else:
                print_at(0,(i*2)+3,term.bold + "    " + (" "*(max_length-len(data_line["role"])))
                         + data_line["role"] + " " + self.reset_color + data_line["name"]
                         + self.reset_color)
        if self.state_viewing_profile:
            for i in range(len(self.credits_data[self.selected_item]["links"])):
                text = self.credits_data[self.selected_item]["links"][i]["label"]
                print_value = term.link(self.credits_data[self.selected_item]["links"][i]["link"],
                                        self.credits_data[self.selected_item]["links"][i]["label"])
                print_at(term.width - (len(text)+1), i+3, print_value)
                if OptionsManager["nerdFont"]:
                    print_at(term.width - (len(text)+3), i+3,
                             self.credits_data[self.selected_item]["links"][i]["icon"])

    def enter_pressed(self):
        if not self.state_viewing_profile:
            self.state_viewing_profile = True

    async def handle_input(self):
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if val.name == "KEY_ESCAPE":
            if not self.state_viewing_profile:
                self.turn_off = True
                SceneManager.change_scene("Titlescreen")
                # print(term.clear)
            else:
                self.state_viewing_profile = False
                # print(term.clear)

        if val.name == "KEY_DOWN":
            self.selected_item += 1
            self.selected_item %= len(self.credits_data)

        if val.name == "KEY_UP":
            self.selected_item -= 1
            self.selected_item %= len(self.credits_data)

        if val.name == "KEY_ENTER":
            self.enter_pressed()

    def __init__(self) -> None:
        file = open(self.creditsPath, encoding="utf8")
        self.credits_data = json.load(file)