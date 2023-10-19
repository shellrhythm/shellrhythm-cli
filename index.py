#!/usr/bin/env python3

import random
import sys
from blessed import Terminal

from src.scenes import ChartSelect, TitleScreen, Options, Credits, \
    Editor, ResultsScreen, LayoutCreator, ServerAuthentication
from src.translate import load_locales, LocaleManager
from src.options import OptionsManager
from src.calibration import Calibration
from src.charts_manager import ChartManager
from src.layout import LayoutManager
from src.constants import __version__
from src.scene_manager import SceneManager
import src.scenes.game as game


term = Terminal()

layouts = {}
layoutNames = []

if __name__ == "__main__":
    load_locales()
    OptionsManager.load_from_file()
    LocaleManager.change_locale(OptionsManager["lang"])
    ChartManager.load_charts()
    LayoutManager.setup()
    print("Everything loaded successfully!\n-----------------------------------------")
    try:
        SceneManager.loadedMenus["ChartSelect"] = ChartSelect()
        SceneManager.loadedMenus["Titlescreen"] = TitleScreen()
        # Sixty-sixteen megabytes- by-bytes
        SceneManager.loadedMenus["Options"] = Options()
        # Funding for this program was made possible by-by-by-by-by-by-
        SceneManager.loadedMenus["Credits"] = Credits()
        SceneManager.loadedMenus["Editor"] = Editor()
        SceneManager.loadedMenus["Calibration"] = Calibration("CalibrationGlobal")
        SceneManager.loadedMenus["LayoutEditor"] = LayoutCreator()
        SceneManager.loadedMenus["Game"] = game.Game()
        SceneManager.loadedMenus["Results"] = ResultsScreen()
        SceneManager.loadedMenus["Server"] = ServerAuthentication()

        if len(ChartManager.chart_data) != 0:
            song_loaded = random.randint(0, len(ChartManager.chart_data)-1)
            SceneManager["Titlescreen"].playing_num = song_loaded
            if ChartManager.chart_data[song_loaded] is not None:
                SceneManager["Titlescreen"].conduc.loadsong(ChartManager.chart_data[song_loaded])
            if "previewLoop" in ChartManager.chart_data[song_loaded]:
                beginPos = ChartManager.chart_data[song_loaded]["previewLoop"]["start"]
                endPos = ChartManager.chart_data[song_loaded]["previewLoop"]["end"]
                SceneManager["Titlescreen"].conduc.loopStart = (beginPos[0] + beginPos[1]/4) *\
                    (SceneManager["Titlescreen"].conduc.bpm/60)
                SceneManager["Titlescreen"].conduc.loopEnd = (endPos[0] + endPos[1]/4) *\
                    (SceneManager["Titlescreen"].conduc.bpm/60)
                SceneManager["Titlescreen"].conduc.isLoop = True
                SceneManager["Titlescreen"].conduc.startAt(beginPos[0]*4 + beginPos[1])
            else:
                SceneManager["Titlescreen"].conduc.isLoop = False
                SceneManager["Titlescreen"].conduc.play()
            SceneManager["ChartSelect"].selected_item = song_loaded

        SceneManager["ChartSelect"].conduc = SceneManager["Titlescreen"].conduc
        SceneManager["Options"].conduc = SceneManager["Titlescreen"].conduc
        SceneManager["Credits"].conduc = SceneManager["Titlescreen"].conduc

        SceneManager["Options"].populate_enum()
        SceneManager["Options"].volume(0, OptionsManager.song_volume)
        SceneManager["Options"].volume(1, OptionsManager.hit_sound_volume)

        if len(sys.argv) > 1:
            if sys.argv[1] == "editor":
                SceneManager.change_scene("Editor")

        SceneManager.loop()
    except KeyboardInterrupt:
        print('Keyboard Interrupt detected!')
    print(term.clear)
