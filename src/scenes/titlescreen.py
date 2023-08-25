"""Title screen"""
import random
import webbrowser
from src.constants import __version__
from src.scene_manager import SceneManager
from src.scenes.game import Game
from src.termutil import print_at, print_lines_at, print_cropped, term, color_text
from src.conductor import Conductor
from src.charts_manager import ChartManager
from src.scenes.base_scene import BaseScene
from src.options import OptionsManager

class TitleScreen(BaseScene):
    logo = ""
    turn_off = False
    selectedItem = 0
    menuOptions = [
        "titlescreen.play",
        "titlescreen.edit",
        "titlescreen.options",
        "titlescreen.credits",
        "titlescreen.discord",
        "titlescreen.github",
        "titlescreen.quit",
    ]
    bottom_text = ""
    discordLink = "https://discord.gg/artQgD3Y8V"
    githubLink = "https://github.com/HastagGuigui/shellrhythm"
    conduc:Conductor = Conductor()
    options:dict = {}
    bottom_text_lines:list = []
    playing_num:int = 0

    def moveBy(self, x):
        self.selectedItem = (self.selectedItem + x)%len(self.menuOptions)

    def enterPressed(self):
        if self.selectedItem == 0:
            # Play
            self.turn_off = True
            SceneManager.change_scene("ChartSelect")
            # print(term.clear)

        if self.selectedItem == 1:
            # Edit
            self.conduc.stop()
            self.conduc.song.stop()
            # SceneManager["Editor"].options = self.options
            SceneManager["Editor"].layoutname = OptionsManager["layout"]
            SceneManager["Editor"].layout = Game.setupKeys(None, OptionsManager["layout"])
            SceneManager.change_scene("Editor")

        if self.selectedItem == 2:
            SceneManager.change_scene("Options")

        if self.selectedItem == 3:
            SceneManager.change_scene("Credits")

        if self.selectedItem == 4:
            webbrowser.open(self.discordLink)

        if self.selectedItem == 5:
            webbrowser.open(self.githubLink)

        if self.selectedItem == 6:
            # Quit
            self.turn_off = True

    async def draw(self):
        print_lines_at(0,1,color_text(self.logo,self.conduc.current_beat),True)
        print_at(int((term.width - len(self.bottom_text)) / 2), len(self.logo.splitlines()) + 2, self.bottom_text)

        for (i,optn) in enumerate(self.menuOptions):
            text = self.loc(optn)
            if self.selectedItem == i:
                if OptionsManager["nerdFont"]:
                    print_at(
                        0,
                        term.height * 0.5 - len(self.menuOptions) + i*2,
                        f"{term.reverse}   {text} {self.reset_color}\ue0b0"
                    )
                else:
                    print_at(
                        0,
                        term.height * 0.5 - len(self.menuOptions) + i*2,
                        f"{term.reverse}   {text} >{self.reset_color}"
                    )
            else:
                print_at(0, term.height * 0.5 - len(self.menuOptions) + i*2, f"  {text}   ")

        text_beat = "○ ○ ○ ○"
        text_beat = text_beat[:int(self.conduc.current_beat)%4 * 2] + "●"\
            + text_beat[(int(self.conduc.current_beat)%4 * 2) + 1:]

        print_at(0, 0, term.center(f"{text_beat}"))
        text_song_title = "[NO SONG PLAYING] // "
        if len(ChartManager.chart_data) != 0:
            text_song_title = ChartManager.chart_data[self.playing_num]["metadata"]["artist"] +\
                " - " + ChartManager.chart_data[self.playing_num]["metadata"]["title"] + " // "
        print_cropped(
            term.width - 31, 0,
            30,
            text_song_title,
            int(self.conduc.current_beat),
            self.reset_color
        )

        text_copyright = "© #Guigui, 2022-2023"
        text_version = "v"+__version__
        print_at(term.width-(len(text_version) + 1), term.height-3, text_version)
        print_at(term.width-(len(text_copyright) + 1), term.height-2, text_copyright)

    async def handle_input(self):
        """
        This function is called every update cycle to get keyboard input.
        (Note: it is called *after* the `draw()` function.)
        """
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if val.name == "KEY_LEFT" or val == "h":
            self.moveBy(0)
        if val.name == "KEY_DOWN" or val == "j":
            self.moveBy(1)
        if val.name == "KEY_UP" or val == "k":
            self.moveBy(-1)
        if val.name == "KEY_RIGHT" or val == "l":
            self.moveBy(0)

        if val.name == "KEY_ENTER":
            self.enterPressed()

        if val == "t":
            self.conduc.metronome = not self.conduc.metronome

    def on_open(self):
        self.bottom_text = self.bottom_text_lines[random.randint(0, len(self.bottom_text_lines)-1)]
        print_lines_at(0,1,self.logo,True)
        print_at(int((term.width - len(self.bottom_text)) / 2),
                 len(self.logo.splitlines()) + 2, self.bottom_text)
        self.conduc.play()

    def on_close(self):
        pass

    def __init__(self):
        """
        The base function, where everything happens. Call it to start the loop. It's never gonna stop. (unless you can somehow set `turnOff` to false)
        """

        bottom_txt = open("./assets/bottom.txt", encoding="utf8")
        self.bottom_text_lines = bottom_txt.read().split("\n")
        bottom_txt.close()

        logo_file = open("./assets/logo.txt", encoding="utf-8")
        self.logo = logo_file.read()
        logo_file.close()
