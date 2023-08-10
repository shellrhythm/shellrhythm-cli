import os
import datetime
from src.scenes.base_scene import BaseScene
from src.scenes.results import ResultsScreen, getRank
from src.charts_manager import ChartManager
from src.scene_manager import SceneManager
from src.translate import LocaleManager
from src.options import OptionsManager
from src.scenes.game import Game
from src.termutil import print_cropped, print_column, print_at, \
    print_lines_at, print_image, term, reset_color, prettydate

# Chart selection menu
class ChartSelect(BaseScene):
    turnOff = False
    chartsize = 0
    selectedItem = 0
    selectedTab = 0
    selected_score = 0
    scoreScrolledBy = []
    funniSpeen = 0
    goBack = False
    resultsThing = ResultsScreen()
    loc = LocaleManager.current_locale()

    chartData = []
    scores = []

    async def draw(self):
        for (i,val) in enumerate(self.chartData):
            if i == self.selectedItem:
                text = val["metadata"]["artist"] + " - " + val["metadata"]["title"] + " // "
                print_cropped(0, i+1, 20, text, int(self.conduc.currentBeat), term.reverse)
            else:
                text = val["metadata"]["artist"] + " - " + val["metadata"]["title"]
                print_cropped(0, i+1, 20, text, 0, reset_color, False)
        print_column(20, 0, term.height-2, reset_color+"┃")
        # Actual chart info display
        if len(self.chartData) == 0:
            print_at(25,5, self.loc("chartSelect.no_charts"))
        else:
            img_width = min(34, int(term.width*0.2))
            if self.chartData[self.selectedItem]["icon"]["img"] is None:
                file_exists = None
                if self.chartData[self.selectedItem]["icon"]["img"] != "":
                    file_exists = print_image(23, 1,
                        "./charts/" + self.chartData[self.selectedItem]["foldername"] + \
                            "/" + self.chartData[self.selectedItem]["icon"]["img"], 
                        img_width
                    )
                if not file_exists:
                    print_at(23, 1, "[NO IMAGE]")
            else:
                text_file_name = "./charts/" + self.chartData[self.selectedItem]["foldername"] + \
                    "/" + self.chartData[self.selectedItem]["icon"]["txt"]
                if os.path.exists(text_file_name):
                    txt = open(text_file_name, encoding="utf8")
                    print_lines_at(23, 1, txt.read())
                    txt.close()
                else:
                    print_at(23, 1, "[NO ICON]")
            print_column(25 + img_width, 0, int(img_width/2)+2, "┃")

            #region metadata
            print_at(27 + img_width, 2, term.blue
                + self.loc("chartSelect.metadata.song")
                + reset_color
                + ": "
                + self.chartData[self.selectedItem]["metadata"]["title"]
            )

            print_at(27 + img_width, 3, term.blue
                + self.loc("chartSelect.metadata.artist")
                + reset_color
                + ": "
                + self.chartData[self.selectedItem]["metadata"]["artist"]
            )

            print_at(27 + img_width, 5, term.blue
                + self.loc("chartSelect.metadata.author")
                + reset_color
                + ": "
                + self.chartData[self.selectedItem]["metadata"]["author"]
            )

            print_at(27 + img_width, 6, term.blue
                + self.loc("chartSelect.difficulty")
                + reset_color
                + ": "
                + str(self.chartData[self.selectedItem]["difficulty"])
            )

            #endregion
            print_at(25 + img_width, 8, "┠" + ("─"*(term.width - (26 + img_width))))
            print_at(28 + img_width, 8, term.reverse + self.loc("chartSelect.metadata.description") + reset_color)
            print_lines_at(26 + img_width, 9, self.chartData[self.selectedItem]["metadata"]["description"])
            print_at(25 + img_width, 19, "┸" + ("─"*(term.width - (26 + img_width))))
            print_at(20, 19, "┠" + ("─"*(4+img_width)))
            text_auto = self.loc("chartSelect.auto")
            if SceneManager["Game"].auto:
                print_at(23, 18, 
                    term.reverse + (" "*int((round(term.width*0.2)-len(text_auto))/2)) 
                    + text_auto + (" "*int((int(term.width*0.2)-len(text_auto))/2)) 
                    + reset_color
                )
            else:
                print_at(23, 18, reset_color+(" "*int(term.width*0.2)))

            #Scores!
            max_rendered_scores = min(len(self.scores[self.chartData[self.selectedItem]["foldername"]]), term.height-23)
            offset = max(0, min(self.selected_score - max_rendered_scores + 1, len(self.scores[self.chartData[self.selectedItem]["foldername"]]) - max_rendered_scores))
            for i in range(max_rendered_scores):
                score = self.scores[self.chartData[self.selectedItem]["foldername"]][i + offset]
                rank = getRank(score["score"])
                if score["checkPassed"]:
                    text_date_format = prettydate(datetime.datetime.fromtimestamp(score["time"]), not OptionsManager["shortTimeFormat"])
                    if i+offset == self.selected_score:
                        color = term.underline
                        if self.selectedTab == 1:
                            color = term.reverse

                        playername = score['playername'] if 'playername' in score else 'Unknown'
                        if score["isOutdated"]:
                            print_at(23, 20+i, f"{term.grey}{color}{rank[0]} {playername} - {int(score['score'])} ({score['accuracy']}%)     [OUTDATED]" + reset_color)
                        else:
                            print_at(23, 20+i, f"{color}{rank[2]}{rank[0]} {playername} - {int(score['score'])} ({score['accuracy']}%)" + reset_color)
                        print_at(term.width - (len(text_date_format)+1), 20+i, term.reverse + text_date_format + reset_color)
                    else:
                        if score["isOutdated"]:
                            print_at(23, 20+i, f"{term.grey}{rank[0]} {playername} - {int(score['score'])} ({score['accuracy']}%)     [OUTDATED]" )
                        else:
                            print_at(23, 20+i, f"{rank[2]}{rank[0]}{reset_color} {playername} - {int(score['score'])} ({score['accuracy']}%)" )
                        print_at(term.width - (len(text_date_format)+1), 20+i, text_date_format)
                else:
                    print_at(25, 20+i, "[INVALID SCORE]")
            if len(self.scores[self.chartData[self.selectedItem]["foldername"]]) == 0:
                print_at(35, int((term.height-18)/2)+17, "No scores yet!")
        # Controls
        print_at(1,term.height - 2,
        f"{term.reverse}[ENTER] {self.loc('chartSelect.controls.play')} {reset_color} "+
        f"{term.reverse}[j/↓] {self.loc('chartSelect.controls.down')} {reset_color} "+
        f"{term.reverse}[k/↑] {self.loc('chartSelect.controls.up')} {reset_color} "+
        f"{term.reverse}[a] {self.loc('chartSelect.controls.auto')} {reset_color} "+
        f"{term.reverse}[e] {self.loc('chartSelect.controls.editor')} {reset_color} "
        )

    def enterPressed(self):
        if self.selectedTab == 0:
            self.turn_off = True
            self.conduc.stop()
            self.conduc.song.stop()
            SceneManager["Game"].loc = self.loc
            SceneManager["Game"].playername = OptionsManager["displayName"]
            SceneManager["Game"].play(self.chartData[self.selectedItem], OptionsManager["layout"])

            # toBeCheckSumd = dict((i,self.chartData[self.selectedItem][i]) \
            #   for i in self.chartData[self.selectedItem] if i != "actualSong")
            # checksum = hashlib.sha256(
            #   json.dumps(toBeCheckSumd,skipkeys=True,ensure_ascii=False).encode("utf-8")
            # ).hexdigest()
            self.scores[self.chartData[self.selectedItem]["foldername"]] = \
                ChartManager.scores[self.chartData[self.selectedItem]["foldername"]]
            self.goBack = True
            self.conduc.play()
        else:
            # print(term.clear)
            self.resultsThing.resultsData = self.scores[self.chartData[\
                self.selectedItem]["foldername"]][self.selected_score]
            self.resultsThing.setup()
            self.resultsThing.isEnabled = True

    async def handle_input(self):
        """
        This function is called every update cycle to get keyboard input.
        (Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
        """
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if val.name == "KEY_DOWN" or val == "j":
            if self.selectedTab == 0:
                # Empty chart list (avoid division by zero)
                if self.chartsize == 0:
                    return
                self.selectedItem = (self.selectedItem + 1)%self.chartsize
                self.conduc.stop()
                self.conduc.song.stop()
                self.conduc.loadsong(self.chartData[self.selectedItem])
                if "previewLoop" in self.chartData[self.selectedItem]:
                    begin_pos = self.chartData[self.selectedItem]["previewLoop"]["start"]
                    end_pos = self.chartData[self.selectedItem]["previewLoop"]["end"]
                    self.conduc.loopStart = (begin_pos[0] + begin_pos[1]/4) * (self.conduc.bpm/60)
                    self.conduc.loopEnd = (end_pos[0] + end_pos[1]/4) * (self.conduc.bpm/60)
                    self.conduc.isLoop = True
                    self.conduc.startAt(begin_pos[0]*4 + begin_pos[1])
                else:
                    self.conduc.isLoop = False
                    self.conduc.play()
                # print(term.clear)
            else:
                if len(self.scores[self.chartData[self.selectedItem]["foldername"]]) != 0:
                    self.selected_score += 1
                    self.selected_score = min(self.selected_score, len(self.scores[self.chartData[self.selectedItem]["foldername"]])-1)
        if val.name == "KEY_UP" or val == "k":
            if self.selectedTab == 0:
                # Empty chart list (avoid division by zero)
                if self.chartsize == 0:
                    return

                self.selectedItem = (self.selectedItem - 1)%self.chartsize
                self.conduc.stop()
                self.conduc.song.stop()
                self.conduc.loadsong(self.chartData[self.selectedItem])
                if "previewLoop" in self.chartData[self.selectedItem]:
                    begin_pos = self.chartData[self.selectedItem]["previewLoop"]["start"]
                    end_pos = self.chartData[self.selectedItem]["previewLoop"]["end"]
                    self.conduc.loopStart = (begin_pos[0] + begin_pos[1]/4) * (self.conduc.bpm/60)
                    self.conduc.loopEnd = (end_pos[0] + end_pos[1]/4) * (self.conduc.bpm/60)
                    self.conduc.isLoop = True
                    self.conduc.startAt(begin_pos[0]*4 + begin_pos[1])
                else:
                    self.conduc.isLoop = False
                    self.conduc.play()
                # print(term.clear)
            else:
                if len(self.scores[self.chartData[self.selectedItem]["foldername"]]) != 0:
                    self.selected_score -= 1
                    self.selected_score = max(self.selected_score, 0)
        if val.name == "KEY_LEFT" or val == "h":
            self.selectedTab = max(self.selectedTab - 1, 0)
        if val.name == "KEY_RIGHT" or val == "l":
            if self.chartsize == 0:
                return

            if len(self.scores[self.chartData[self.selectedItem]["foldername"]]) > 0:
                self.selectedTab = min(self.selectedTab + 1, 1)
        if val == "a":
            SceneManager["Game"].auto = not SceneManager["Game"].auto
        if val == "e":
            #load editor
            self.conduc.stop()
            self.conduc.song.stop()
            SceneManager["Editor"].turnOff = False
            SceneManager["Editor"].layoutname = OptionsManager["layout"]
            SceneManager["Editor"].layout = Game.setupKeys(None, OptionsManager["layout"])
            SceneManager["Editor"].loc = self.loc
            SceneManager["Editor"].mapToEdit = self.chartData[self.selectedItem]
            SceneManager["Editor"].localConduc.loadsong(self.chartData[self.selectedItem])
            SceneManager["Editor"].mapToEdit.pop("actualSong", None)
            SceneManager["Editor"].fileLocation = f"./charts/{self.chartData[self.selectedItem]['foldername']}/data.json"
            SceneManager.change_scene("Editor")
            self.turn_off = True
            # self.goBack = True
            # conduc.play()

        if val.name == "KEY_ENTER":
            self.enterPressed()

        if val.name == "KEY_ESCAPE":
            SceneManager.change_scene("Titlescreen")
            # print(term.clear)

    async def handle_screen_too_small(self) -> None:
        text = self.loc("screenTooSmall")
        print_at(int((term.width - len(text))*0.5), 
                 int(term.height*0.5), term.reverse + text + reset_color)

    def __init__(self):
        """
        The base function, where everything happens. Call it to start the loop. \
        It's never gonna stop. (unless you can somehow set `turn_off` to false)
        """
        self.chartsize = len(self.chartData)
