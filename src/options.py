import json, os
from typing import Any

class OptionsManager:
    """If you need to check options, use this!"""

    #key-value:
    # key: the name of the option in the options file
    # value: the name of the option in OptionsManager
    OPTIONS_NAME:dict = {
        "layout": "layout",
        "globalOffset": "global_offset",
        "lang": "language",
        "nerdFont": "use_nerd_font",
        "textImages": "display_images",
        "displayName": "ingame_name",
        "shortTimeFormat": "shorten_time_format",
        "bypassSize": "bypass_minimum_size",
        "songVolume": "song_volume",
        "hitSoundVolume": "hit_sound_volume"
    }

    layout:str = ""
    global_offset:float = 0.0
    language:str = "en"
    use_nerd_font:bool = False
    display_images:bool = True
    ingame_name:str = "Player"
    shorten_time_format:bool = False
    bypass_minimum_size:bool = False
    song_volume:float = 1
    hit_sound_volume:float = 1
    #server_adress = "" #Not yet!

    @staticmethod
    def load_from_file():
        if os.path.exists("./options.json"):
            file = open("./options.json", encoding="utf8")
            options_string = file.read()
            maybe_options = json.loads(options_string)
            file.close()
            file2 = open("./example_options.json", encoding="utf8")
            default_options_string = file2.read()
            default_options = json.loads(default_options_string)
            file2.close()
            print(maybe_options)
            for k,val in default_options.items():
                maybe_options.setdefault(k, val)
            OptionsManager.layout               = maybe_options["layout"]
            OptionsManager.global_offset        = maybe_options["globalOffset"]
            OptionsManager.language             = maybe_options["lang"]
            OptionsManager.use_nerd_font        = maybe_options["nerdFont"]
            OptionsManager.display_images       = maybe_options["textImages"]
            OptionsManager.ingame_name          = maybe_options["displayName"]
            OptionsManager.shorten_time_format  = maybe_options["shortTimeFormat"]
            OptionsManager.bypass_minimum_size  = maybe_options["bypassSize"]
            OptionsManager.song_volume          = maybe_options["songVolume"]
            OptionsManager.hit_sound_volume     = maybe_options["hitSoundVolume"]

            options = maybe_options

        else:
            file = open("./options.json", "x", encoding="utf8")
            file.write(json.dumps(options, indent=4))
            file.close()

    @staticmethod
    def save_to_file(options_file:str="./options.json"):
        json_dict = {
            "layout":           OptionsManager.layout,
            "globalOffset":     OptionsManager.global_offset,
            "lang":             OptionsManager.language,
            "nerdFont":         OptionsManager.use_nerd_font,
            "textImages":       OptionsManager.display_images,
            "displayName":      OptionsManager.ingame_name,
            "shortTimeFormat":  OptionsManager.shorten_time_format,
            "bypassSize":       OptionsManager.bypass_minimum_size,
            "songVolume":       OptionsManager.song_volume,
            "hitSoundVolume":   OptionsManager.hit_sound_volume,
        }
        file = open(options_file, "w", encoding="utf8")
        file.write(json.dumps(json_dict, indent=4))
        file.close()

    @staticmethod
    def __class_getitem__(key):
        return getattr(OptionsManager, OptionsManager.OPTIONS_NAME[key])
    
    @staticmethod
    def set(key, newvalue):
        setattr(OptionsManager, OptionsManager.OPTIONS_NAME[key], newvalue)
    
    @staticmethod
    def __setitem__(key, newvalue):
        setattr(OptionsManager, OptionsManager.OPTIONS_NAME[key], newvalue)

    @staticmethod
    def __init__():
        OptionsManager.load_from_file()
        pass

if __name__ == "__main__":
    OptionsManager.load_from_file()
