"""Language-related shenanigans"""
import json
import os
import logging

class Locale:
    name = "N/A" #N/A
    data = {}
    showRawCodes = False

    def __call__(self, key:str) -> str:
        #Let's search for the key!
        travel_path = key.split(".")
        current_dict = self.data
        output = ""
        for subkey in travel_path:
            if subkey in current_dict.keys():
                if isinstance(current_dict[subkey], dict):
                    current_dict = current_dict[subkey]
                else:
                    output = current_dict[subkey]
            else:
                break
        if output != "" and not self.showRawCodes:
            return output
        return key

    def __str__(self) -> str:
        return f"Locale: {self('lang')} ({self.name})"

    def __init__(self, lang:str, silent:bool = True) -> None:
        if not silent:
            logging.info("Loading locale \"%s\"...", lang)
        file = open("./lang/" + lang + ".json", encoding="utf8")
        self.data = json.loads(file.read())
        self.name = lang
        file.close()


class LocaleManager:
    locales = {}
    locale_names = []
    selectedLocale = "en"

    @staticmethod
    def current_locale() -> Locale:
        if LocaleManager.selectedLocale not in LocaleManager.locales:
            load_locales()
        return LocaleManager.locales[LocaleManager.selectedLocale]

    @staticmethod
    def change_locale(new_locale):
        if new_locale in LocaleManager.locale_names:
            LocaleManager.selectedLocale = new_locale

def load_locales():
    LocaleManager.locale_names = [
        f.name.split(".", 1)[0] for f in os.scandir("./lang") if f.is_file()
    ]
    for (_,lang_code) in enumerate(LocaleManager.locale_names):
        new_locale = Locale(lang_code, False)
        LocaleManager.locales[lang_code] = new_locale

if __name__ == "__main__":
    locale = Locale("fr")
    print(locale("chartSelect.backTitle"))
    print(locale)
