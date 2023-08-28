import os
import logging
from src.options import OptionsManager


class LayoutManager:
    layouts:dict = {}
    layoutNames:list = []

    @staticmethod
    def current_layout():
        """Returns currently active layout based on OptionsManager.layout"""
        return LayoutManager.layouts[OptionsManager.layout]

    @staticmethod
    def setup():
        LayoutManager.layouts = {}
        LayoutManager.layoutNames = []
        layout_files = [f.name for f in os.scandir("./layout") if f.is_file()]
        for (i, file_name) in enumerate(layout_files):
            logging.info("Loading layout \"%s\"... (%d/%d)", file_name, i+1, len(layout_files))
            file = open("./layout/" + file_name, encoding="utf8")
            LayoutManager.layouts[file_name] = list(file.read().replace('\n', ''))
            LayoutManager.layoutNames.append(file_name)
            file.close()

    @staticmethod
    def __class_getitem__(key):
        return LayoutManager.layouts[key]

if __name__ == "__main__":
    print("Nope, sorry...")
    # layout = LayoutCreator()
    # layout.loop()
