#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
from curses import wrapper
from time import sleep, time_ns
from game import *
import os

charts = []
chartData = []
chartIcons = []
layouts = []
logo = []
screen = None
killswitch = True
menu = 0
selected_option = 0
max_option = 0
y = 0
x = 0

__version__ = "0.1.0"

game = None


def init_color():
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_CYAN)

def handle_pressed_keys(e):
    global killswitch
    global screen
    global selected_option
    global max_option
    global menu
    global game
  # print(e.name)
    if e.event_type == keyboard.KEY_DOWN:
        if game is None:
            if e.scan_code == 1:
                if menu == 0:
                    killswitch = False
                    curses.endwin()
                else:
                    screen.clear()
                    selected_option = menu - 1
                    menu = 0
                    for i in range(len(logo)):
                        screen.addstr(2+i,int(x * 0.5)-int(len(logo[0])/2), logo[i])
            if e.scan_code == 72:
                #Up
                selected_option -= 1
                if menu == 1:
                    screen.clear()
                if selected_option < 0:
                    selected_option += max_option
            if e.scan_code == 80:
                #Down
                selected_option += 1
                if menu == 1:
                    screen.clear()
                if selected_option >= max_option:
                    selected_option -= max_option
            if e.scan_code == 57 or e.scan_code == 28:
                if menu == 0: #Title screen
                    if   selected_option == 0:
                        screen.clear()
                        menu = 1
                    elif selected_option == 1:
                        screen.clear()
                        menu = 2
                        selected_option = 0
                    elif selected_option == 2:
                        killswitch = False
                        curses.endwin()
                elif menu == 1: #Chart select
                    chartData[selected_option]["filename"] = charts[selected_option]
                    game = Game(screen, exitMap, chartData[selected_option])
                elif menu == 2:
                    orig_f = open("options.json", "r")
                    jsonfile = json.load(orig_f)
                    orig_f.close()
                    jsonfile["layout"] = layouts[selected_option]
                    new_f = open("options.json", "w")
                    new_f.write(json.dumps(jsonfile))
                    new_f.close()
                    screen.addstr(0,0, "Saved!")
        if game is not None:
            game.handle_pressed_keys(e)

def exitMap():
    screen.clear()
    global menu
    global game
    global killswitch
    menu = 1
    if game is not None:
        game.music.stop()
    keyboard.unhook_all()
    keyboard.hook(handle_pressed_keys)
    game = None


def update():
    global screen
    global selected_option
    global max_option
    global y, x
    global game
    if game is None:
        if menu == 0: # Title screen
            max_option = 3
            screen.addstr(20, int(x*0.5) - int(len(" > Select Keyboard Layout < ")*0.5), "        Select Charts       ")
            screen.addstr(22, int(x*0.5) - int(len(" > Select Keyboard Layout < ")*0.5), "   Select Keyboard Layout   ")
            screen.addstr(24, int(x*0.5) - int(len(" > Select Keyboard Layout < ")*0.5), "            Quit            ")

            if selected_option == 0:
                screen.addstr(20, int(x*0.5) - int(len(" > Select Keyboard Layout < ")*0.5), " >      Select Charts     < ", curses.color_pair(7))
            if selected_option == 1:
                screen.addstr(22, int(x*0.5) - int(len(" > Select Keyboard Layout < ")*0.5), " > Select Keyboard Layout < ", curses.color_pair(7))
            if selected_option == 2:
                screen.addstr(24, int(x*0.5) - int(len(" > Select Keyboard Layout < ")*0.5), " >          Quit          < ", curses.color_pair(7))

            screen.addstr(y-1, x-len("vX.X.X")-1, "v" + __version__)
        if menu == 1: # Chart picker
            max_option = max(len(charts), 1)
            for i in range(y):
                screen.addstr(i, 0, "|                   |")
                if i < max_option:
                    if selected_option == i:
                        screen.addstr(i, 0, "|> " + charts[i], curses.color_pair(7))
                    else:
                        screen.addstr(i, 1, charts[i])
                

            #metadata display
            metadata = chartData[selected_option]["metadata"]
            for i in range(len(chartIcons[selected_option])):
                if len(chartIcons[selected_option]) > i:
                    screen.addstr(2+i,int((x-22) * 0.5)+22-int(len(chartIcons[selected_option][0])/2), chartIcons[selected_option][i%len(chartIcons[selected_option])])
                    screen.refresh()

            screen.addstr(15,22, (" "* int( (x-22) * 0.5 - len(metadata["title"] + " - " + metadata["author"] ) /2)) + metadata["title"] + " - " + metadata["author"] + (" "* int( (x-22) * 0.5 - len(metadata["title"] + " - " + metadata["author"] ) /2)))
            screen.addstr(16,int((x-22) * 0.5)+22-int(len("Level by " + metadata["charter"])/2), "Level by " + metadata["charter"])
            n = x-22
            desc = [metadata["description"][i:i+n] for i in range(0, len(metadata["description"]), n)]

            screen.addstr(19,22, "-" * (x-22))
            for i in range(len(desc)):
                screen.addstr(20+i,22, desc[i] + (" " * (x - 22 - len(desc[i]))))
            
            if menu == 0:
                screen.clear()
                for i in range(len(logo)):
                    screen.addstr(2+i,int(x * 0.5)-int(len(logo[0])/2), logo[i])


            
            
                

        if menu == 2: # Keyboard Layout Picker
            max_option = max(len(layouts), 1)
            screen.addstr(0,int(x*0.5) - int(len("Keyboard Layout Select") * 0.5), "Keyboard Layout Select")
            
            for i in range(len(layouts)):
                screen.addstr(3+i, 0, "|")
                if selected_option == i:
                    screen.addstr(3+i, 1, "> " + layouts[i].upper() + "  ", curses.color_pair(7))
                else:
                    screen.addstr(3+i, 1, " " + layouts[i].upper() + "   ")

        screen.refresh()



def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0,0,"Booting up shellrhythm...")
    stdscr.refresh()

    global screen
    screen = stdscr

    global charts
    global chartData
    global layouts
    global killswitch
    sleep(1)
    charts = [f.path[len("./charts\\"):len(f.path)] for f in os.scandir("./charts") if f.is_dir()]
    for i in range(len(charts)):
        f = open("./charts/" + charts[i] + "/data.json")
        chartData.append(json.load(f))
        f.close()
        stdscr.addstr(1,0,"Loading maps... (" + str(i + 1) + "/" + str(len(charts)) + ")")
        stdscr.refresh()
        sleep(1/15)

    print(charts)
    layouts = [f.path[len("./layout\\"):len(f.path)] for f in os.scandir("./layout") if f.name != "CUSTOMLAYOUT.md"]
    print(layouts)
    for i in range(len(charts)):
        stdscr.refresh()
        sleep(1/30)
    sleep(0.5)
    stdscr.clear()
    global y, x
    y, x = stdscr.getmaxyx()

    global logo
    f = open("./assets/logo.txt", encoding="utf-8")
    logo = f.read().split("\n")
    f.close()

    global chartIcons
    for i in range(len(charts)):
        if os.path.exists("./charts/" + charts[i] + "/icon.txt"):
            f = open("./charts/" + charts[i] + "/icon.txt", encoding="utf-8")
            chartIcons.append(f.read().split("\n"))
            f.close()
        else:
            chartIcons.append("PLACEHOLDER\nERPLACEHOLD\nLDERPLACEHO\nHOLDERPLACE\nCEHOLDERPLA")
    
    keyboard.hook(handle_pressed_keys)
    bpm = 120
    steps = 4
    startTime = time_ns()
    offset = 0
    # Clear screen
    stdscr.clear()
    curTime = time_ns()
    startTime = curTime
    # Check if screen was re-sized (True or False)
    totalElapsed = 0
    resize = curses.is_term_resized(y, x)

    init_color()
    
    for i in range(len(logo)):
        stdscr.addstr(2+i,int(x * 0.5)-int(len(logo[0])/2), logo[i])
        stdscr.refresh()
        sleep(1/30)

    while killswitch:
        duration_of_step = max(0, (60 / bpm / steps)) #length of 1/4 beat

        #update stuff
        elapsed = time_ns() - curTime
        newTime = time_ns()
        totalElapsed+=elapsed

        # this is where the funny happens
        if math.floor(((newTime-startTime)-offset)/duration_of_step) > math.floor(((curTime-startTime)-offset)/duration_of_step): #OnStepPassed
            ts = math.floor(((newTime-startTime)-offset)/duration_of_step)
            position = (int(ts/(4*steps)), (int(ts/4)%steps + 1))


          # if ts%steps == 0: #OnBeatPassed
          #     stdscr.addstr(0,0, "○○○○")
          #     stdscr.addstr(0,int(ts/4)%steps, "●")
          #     stdscr.addstr(5,0, str(position))


        # calc offset
        curTime = newTime# Action in loop if resize is True:
        if resize is True:
            y, x = stdscr.getmaxyx()
            stdscr.clear()
            curses.resizeterm(y, x)
            stdscr.refresh()

        # update code
        update()

        if game is not None:
            game.loop(stdscr)


        stdscr.refresh()


if __name__ == "__main__":
    wrapper(main)