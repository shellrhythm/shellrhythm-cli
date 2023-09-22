import os
import shutil
from src.termutil import term, print_box, print_at
from src.translate import LocaleManager


class EditorPauseMenu:
    buttons = [
        "resume",
        "playtest",
        "song",
        "addimage",
        "metadata",
        "save",
        "export",
        "quit",
    ]
    enabled = False
    selected = 0
    reset_color = term.normal
    loc = LocaleManager.current_locale()

    async def draw(self):
        width = max(len(self.loc("editor.pause." + option)) for option in self.buttons)+4
        print_box(
            (term.width-width)//2 - 1,
            (term.height//2) - len(self.buttons) - 1,
            width+2,
            len(self.buttons) * 2 + 1
        )
        for (i,optn) in enumerate(self.buttons):
            if i == self.selected:
                print_at(
                    (term.width-width)//2,
                    (term.height//2) - len(self.buttons) + i*2,
                    term.reverse + term.center(self.loc("editor.pause." + optn), width)\
                        + self.reset_color
                )
            else:
                print_at(
                    (term.width-width)//2,
                    (term.height//2) - len(self.buttons) + i*2,
                    term.center(self.loc("editor.pause." + optn), width)
                )
            if i != len(self.buttons)-1:
                print_at(
                    (term.width-width)//2,
                    (term.height//2) - len(self.buttons) + i*2 + 1,
                    " "*width
                )

    def run_option(self, option, editor):
        #what made you think this was a good idea
        #- #Guigui, to himself, 16/2/2023 (DD/MM/YYYY the obviously better formatting)
        if option == 0:
            #resume
            self.enabled = False
            print(term.clear)
        if option == 1:
            #playtest
            editor.game.play(editor.chart, editor.layoutname, editor.options)
            self.enabled = False
        if option == 2:
            editor.command_line.run_command(editor, "song") #uh yeah
        if option == 3:
            #change image
            editor.file_browser.fileExtFilter = \
                "(?:\\.png$)|(?:\\.jpeg$)|(?:\\.webp$)|(?:\\.jpg$)|(?:\\.apng$)|(?:\\.gif$)"
            editor.file_browser.load_folder(os.getcwd())
            editor.file_browser.caption = "Select an image"
            editor.file_browser.turnOff = False
            image_file_location = editor.file_browser.loop()
            try:
                shutil.copyfile(
                    image_file_location,
                    f"./charts/{editor.chart['foldername']}/{image_file_location.split('/')[-1]}"
                )
            except shutil.SameFileError:
                pass
            editor.chart["icon"]["img"] = image_file_location.split("/")[-1]
        if option == 4:
            #metadata
            editor.metadata_menu_enabled = True
            self.enabled = False
            print(term.clear)
        if option == 5:
            #save
            editor.save()
            self.enabled = False
        if option == 6:
            #export
            editor.save()
            self.enabled = False
            editor.export()
            print(term.clear)
            print_at(
                0,
                term.height-2,
                term.on_green+\
                f"Exported successfully to ./charts/{editor.chart['foldername']}.zip"+\
                term.clear_eol+self.reset_color
            )
        if option == 7:
            #quit
            editor.command_line.run_command(editor, "q")
            self.enabled = False

    def input(self, val, editor):
        if val.name == "KEY_UP":
            self.selected -= 1
            self.selected %= len(self.buttons)
        if val.name == "KEY_DOWN":
            self.selected += 1
            self.selected %= len(self.buttons)
        if val.name == "KEY_ENTER":
            self.run_option(self.selected, editor)
