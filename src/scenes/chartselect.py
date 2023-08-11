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
    print_lines_at, print_image, term, reset_color, prettydate, \
    color_text, strip_seqs

# Chart selection menu
class ChartSelect(BaseScene):
    turnOff = False
    chartsize = 0
    selectedItem = 0
    selected_tab = 0
    selected_score = 0
    scoreScrolledBy = []
    funniSpeen = 0
    goBack = False
    resultsThing = ResultsScreen()
    loc = LocaleManager.current_locale()

    async def draw(self):
        for (i,val) in enumerate(ChartManager.chart_data):
            if i == self.selectedItem:
                text = val["metadata"]["artist"] + " - " + val["metadata"]["title"] + " // "
                print_cropped(0, i+1, 20, text, int(self.conduc.current_beat), term.reverse)
            else:
                text = val["metadata"]["artist"] + " - " + val["metadata"]["title"]
                print_cropped(0, i+1, 20, text, 0, reset_color, False)
        print_column(20, 0, term.height-2, reset_color+"┃")
        # Actual chart info display
        if len(ChartManager.chart_data) == 0:
            print_at(25,5, self.loc("chartSelect.no_charts"))
        else:
            chart_in_question = ChartManager.chart_data[self.selectedItem]
            img_width = min(34, int(term.width*0.2))
            if chart_in_question["icon"]["img"] is not None:
                file_exists = None
                if chart_in_question["icon"]["img"] != "":
                    file_exists = print_image(23, 1,
                        "./charts/" + chart_in_question["foldername"] + \
                            "/" + chart_in_question["icon"]["img"], 
                        img_width
                    )
                if not file_exists:
                    print_at(23, 1, term.reverse("[NO IMAGE]"))
            else:
                text_file_name = "./charts/" + chart_in_question["foldername"] + \
                    "/" + chart_in_question["icon"]["txt"]
                if os.path.isfile(text_file_name):
                    txt = open(text_file_name, encoding="utf8")
                    icon_text = color_text(txt.read())
                    split_lines = icon_text.split("\n")
                    width = len(strip_seqs(split_lines[0]))
                    height = len(split_lines)
                    print_lines_at(23+((img_width-width)//2), 1+((img_width//2-height)//2), icon_text)
                    txt.close()
                else:
                    print_at(23, 1, term.reverse("[NO ICON]"))
            print_column(25 + img_width, 0, int(img_width/2)+2, "┃")

            #region metadata
            print_at(27 + img_width, 2, term.blue
                + self.loc("chartSelect.metadata.song")
                + reset_color
                + ": "
                + chart_in_question["metadata"]["title"]
            )

            print_at(27 + img_width, 3, term.blue
                + self.loc("chartSelect.metadata.artist")
                + reset_color
                + ": "
                + chart_in_question["metadata"]["artist"]
            )

            print_at(27 + img_width, 5, term.blue
                + self.loc("chartSelect.metadata.author")
                + reset_color
                + ": "
                + chart_in_question["metadata"]["author"]
            )

            print_at(27 + img_width, 6, term.blue
                + self.loc("chartSelect.difficulty")
                + reset_color
                + ": "
                + str(chart_in_question["difficulty"])
            )

            #endregion
            print_at(25 + img_width, 8, "┠" + ("─"*(term.width - (26 + img_width))))
            print_at(28 + img_width, 8, 
                     term.reverse + self.loc("chartSelect.metadata.description") + reset_color
                    )
            print_lines_at(26 + img_width, 9, chart_in_question["metadata"]["description"])
            print_at(25 + img_width, 19, "┸" + ("─"*(term.width - (26 + img_width))))
            print_at(20, 19, "┠" + ("─"*(4+img_width)))
            text_auto = self.loc("chartSelect.auto")
            if SceneManager["Game"].auto:
                print_at(23, 18,
                    term.reverse(term.center(text_auto, img_width))
                )
            else:
                print_at(23, 18, reset_color+(" "*img_width))

            #Scores!
            max_rendered_scores = min(len(ChartManager.scores[chart_in_question["foldername"]]), term.height-23)
            offset = max(0, min(self.selected_score - max_rendered_scores + 1, len(ChartManager.scores[chart_in_question["foldername"]]) - max_rendered_scores))
            for i in range(max_rendered_scores):
                score = ChartManager.scores[chart_in_question["foldername"]][i + offset]
                rank = getRank(score["score"])
                if score["checkPassed"]:
                    text_date_format = prettydate(datetime.datetime.fromtimestamp(score["time"]), not OptionsManager["shortTimeFormat"])
                    if i+offset == self.selected_score:
                        color = term.underline
                        if self.selected_tab == 1:
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
            if len(ChartManager.scores[chart_in_question["foldername"]]) == 0:
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
        if self.selected_tab == 0:
            self.turn_off = True
            self.conduc.stop()
            self.conduc.song.stop()
            SceneManager["Game"].loc = self.loc
            SceneManager["Game"].playername = OptionsManager["displayName"]
            SceneManager["Game"].play(ChartManager.chart_data[self.selectedItem], OptionsManager["layout"])
            SceneManager.change_scene("Game")

            # toBeCheckSumd = dict((i,ChartManager.chart_data[self.selectedItem][i]) \
            #   for i in ChartManager.chart_data[self.selectedItem] if i != "actualSong")
            # checksum = hashlib.sha256(
            #   json.dumps(toBeCheckSumd,skipkeys=True,ensure_ascii=False).encode("utf-8")
            # ).hexdigest()
            # self.conduc.play()
        else:
            # print(term.clear)
            SceneManager["ResultsScreen"].results_data = ChartManager.scores[\
                ChartManager.chart_data[self.selectedItem]["foldername"]]\
                    [self.selected_score]
            SceneManager.change_scene("ResultsScreen")

    def change_chart(self, new_chart_number):
        if self.chartsize == 0:
            return
        self.selectedItem = new_chart_number
        self.conduc.stop()
        self.conduc.song.stop()
        self.conduc.loadsong(ChartManager.chart_data[self.selectedItem])
        if "previewLoop" in ChartManager.chart_data[self.selectedItem]:
            begin_pos = ChartManager.chart_data[self.selectedItem]["previewLoop"]["start"]
            end_pos = ChartManager.chart_data[self.selectedItem]["previewLoop"]["end"]
            self.conduc.loopStart = (begin_pos[0] + begin_pos[1]/4) * (self.conduc.bpm/60)
            self.conduc.loopEnd = (end_pos[0] + end_pos[1]/4) * (self.conduc.bpm/60)
            self.conduc.isLoop = True
            self.conduc.startAt(begin_pos[0]*4 + begin_pos[1])
        else:
            self.conduc.isLoop = False
            self.conduc.play()
        
        img_width = max(0, term.width-23)
        img_height = term.height-1
        clear_img = (" "*img_width + "\n")*img_height
        print_lines_at(23, 1, clear_img)


    async def handle_input(self):
        """
        This function is called every update cycle to get keyboard input.
        (Note: it is called *after* the `draw()` function, and takes the entire frame to run.)
        """
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if val.name == "KEY_DOWN" or val == "j":
            if self.selected_tab == 0:
                # Empty chart list (avoid division by zero)
                if self.chartsize == 0:
                    return
                self.change_chart((self.selectedItem + 1)%self.chartsize)
            else:
                if len(ChartManager.scores[ChartManager.chart_data[self.selectedItem]["foldername"]]) != 0:
                    self.selected_score += 1
                    self.selected_score = min(self.selected_score, len(ChartManager.scores[ChartManager.chart_data[self.selectedItem]["foldername"]])-1)
        if val.name == "KEY_UP" or val == "k":
            if self.selected_tab == 0:
                # Empty chart list (avoid division by zero)
                if self.chartsize == 0:
                    return
                self.change_chart((self.selectedItem - 1)%self.chartsize)
            else:
                if len(ChartManager.scores[ChartManager.chart_data[self.selectedItem]["foldername"]]) != 0:
                    self.selected_score -= 1
                    self.selected_score = max(self.selected_score, 0)
        if val.name == "KEY_LEFT" or val == "h":
            self.selected_tab = max(self.selected_tab - 1, 0)
        if val.name == "KEY_RIGHT" or val == "l":
            if self.chartsize == 0:
                return

            if len(ChartManager.scores[ChartManager.chart_data[self.selectedItem]["foldername"]]) > 0:
                self.selected_tab = min(self.selected_tab + 1, 1)
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
            SceneManager["Editor"].mapToEdit = ChartManager.chart_data[self.selectedItem]
            SceneManager["Editor"].localConduc.loadsong(ChartManager.chart_data[self.selectedItem])
            SceneManager["Editor"].mapToEdit.pop("actualSong", None)
            SceneManager["Editor"].fileLocation = f"./charts/{ChartManager.chart_data[self.selectedItem]['foldername']}/data.json"
            SceneManager.change_scene("Editor")
            self.turn_off = True
            # self.goBack = True
            # conduc.play()

        if val.name == "KEY_ENTER":
            self.enterPressed()

        if val.name == "KEY_ESCAPE":
            SceneManager.change_scene("Titlescreen")
            # print(term.clear)

    def __init__(self):
        """
        The base function, where everything happens. Call it to start the loop. \
        It's never gonna stop. (unless you can somehow set `turn_off` to false)
        """
        self.chartsize = len(ChartManager.chart_data)
