from src.scenes.base_scene import BaseScene
from src.termutil import term
from src.translate import LocaleManager

class SceneManager:
    """Manages the scenes"""
    current_scene = "Titlescreen"
    loadedMenus:dict[str,BaseScene] = {
        "ChartSelect": None,
        "Titlescreen": None,
        "Options": None,
        "Credits": None,
        "Editor": None,
        "Calibration": None,
        "LayoutEditor": None,
        "Results": None,
        "Game": None,
        "Server": None
    }
    turn_off:bool = False

    @staticmethod
    def loop():
        "Starts the scene manager."

        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            # print(term.clear)
            SceneManager.loadedMenus[SceneManager.current_scene].on_open()
            while not SceneManager.loadedMenus[SceneManager.current_scene].turn_off:
                SceneManager.loadedMenus[SceneManager.current_scene].loop()

    @staticmethod
    def change_scene(new_scene:str = "Titlescreen"):
        """Use this when switching between scenes!"""
        if new_scene in SceneManager.loadedMenus:
            SceneManager.loadedMenus[SceneManager.current_scene].on_close()
            SceneManager.loadedMenus[new_scene].turn_off = False
            print(term.clear)
            SceneManager.loadedMenus[new_scene].loc = LocaleManager.current_locale()
            SceneManager.loadedMenus[new_scene].on_open()
            SceneManager.current_scene = new_scene


    @staticmethod
    def __class_getitem__(key) -> BaseScene:
        return SceneManager.loadedMenus[key]
