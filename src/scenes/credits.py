
from src.scenes.base_scene import BaseScene
from src.scene_manager import SceneManager
from src.termutil import print_at, term, reset_color

class Credits(BaseScene):
    """The class that displays game credits."""
    turnOff = False
    credits_data = []
    creditsPath = "./assets/credits.json"
    selectedItem = 0
    isViewingProfile = False
    options = {}

    def draw(self):
        max_length = 0

        for option in self.credits_data:
            if len(option["role"]) > max_length:
                max_length = len(option["role"])

        for (i,data_line) in enumerate(self.credits_data):
            if self.selectedItem == i:
                print_at(0,(i*2)+3,term.reverse + term.bold + "    " +
                         (" "*(max_length-len(data_line["role"]))) + data_line["role"]
                         + " " + reset_color + term.underline + data_line["name"] + reset_color
                        )
            else:
                print_at(0,(i*2)+3,term.bold + "    " + (" "*(max_length-len(data_line["role"])))
                         + data_line["role"] + " " + reset_color + data_line["name"] + reset_color)
        if self.isViewingProfile:
            for i in range(len(self.credits_data[self.selectedItem]["links"])):
                text = self.credits_data[self.selectedItem]["links"][i]["label"]
                print_value = term.link(self.credits_data[self.selectedItem]["links"][i]["link"],
                                        self.credits_data[self.selectedItem]["links"][i]["label"])
                print_at(term.width - (len(text)+1), i+3, print_value)
                if self.options["nerdFont"]:
                    print_at(term.width - (len(text)+3), i+3,
                             self.credits_data[self.selectedItem]["links"][i]["icon"])

    def enter_pressed(self):
        if not self.isViewingProfile:
            self.isViewingProfile = True

    def handle_input(self):
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if val.name == "KEY_ESCAPE":
            if not self.isViewingProfile:
                self.turn_off = True
                SceneManager.change_scene("Titlescreen")
                # print(term.clear)
            else:
                self.isViewingProfile = False
                # print(term.clear)

        if val.name == "KEY_DOWN":
            self.selectedItem += 1
            self.selectedItem %= len(self.credits_data)

        if val.name == "KEY_UP":
            self.selectedItem -= 1
            self.selectedItem %= len(self.credits_data)

        if val.name == "KEY_ENTER":
            self.enter_pressed()

    def __init__(self) -> None:
        pass