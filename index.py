import curses
from curses import wrapper
from time import sleep
from game import *
import os

charts = []
screen = None
killswitch = True
menu = 0
selected_option = 0
max_option = 0
y = 0
x = 0

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
                killswitch = False
                curses.curs_set(1)
                curses.nocbreak()
                screen.keypad(False)
                curses.echo()
                curses.endwin()
            if e.scan_code == 72:
                #Up
                selected_option -= 1
                if selected_option < 0:
                    selected_option += max_option
            if e.scan_code == 80:
                #Down
                selected_option += 1
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
                        curses.curs_set(1)
                        curses.nocbreak()
                        screen.keypad(False)
                        curses.echo()
                        curses.endwin()
                elif menu == 1: #Chart select
                    game = Game(screen, exitMap, charts[selected_option])
        if game is not None:
            game.handle_pressed_keys(e)

def exitMap():
    screen.clear()
    global menu
    global game
    global killswitch
    menu = 1
    game.music.stop()
    keyboard.unhook_all()
    keyboard.hook(handle_pressed_keys)
    game = None
  # killswitch = False
  # curses.curs_set(1)
  # curses.nocbreak()
  # screen.keypad(False)
  # curses.echo()
  # curses.endwin()


def update():
    global screen
    global selected_option
    global max_option
    global y, x
    global game
    if game is None:
        if menu == 0:
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
        if menu == 1:
            max_option = len(charts)
            for i in range(y):
                screen.addstr(i, 0, "|                   |")
                if i < max_option:
                    if selected_option == i:
                        screen.addstr(i, 0, "|> " + charts[i], curses.color_pair(7))
                    else:
                        screen.addstr(i, 1, charts[i])
        screen.refresh()



def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0,0,"Booting up shellrhythm...")
    stdscr.refresh()

    global screen
    screen = stdscr

    global charts
    global killswitch
    sleep(1)
    charts = [f.path[len("./charts\\"):len(f.path)] for f in os.scandir("./charts") if f.is_dir()]
    print(charts)
    for i in range(len(charts)):
        stdscr.addstr(1,0,"Loading maps... (" + str(i + 1) + "/" + str(len(charts)) + ")")
        stdscr.refresh()
        sleep(1/30)
    sleep(10/30)
    stdscr.clear()
    global y, x
    y, x = stdscr.getmaxyx()

    f = open("./assets/logo.txt", encoding="utf-8")
    logo = f.read().split("\n")
  # print(logo)
    f.close()
    
    keyboard.hook(handle_pressed_keys)
    bpm = 120
    steps = 4
    startTime = time()
    offset = 0
    # Clear screen
    stdscr.clear()
    curTime = time()
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
        elapsed = time() - curTime
        newTime = time()
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


wrapper(main)