import curses
import vlc
import math
from time import time
import sys
import keyboard
import json

from curses import wrapper

import os
if os.name == 'posix':    
    from subprocess import check_output
elif os.name == 'nt':
    import win32api, win32con, win32process
    from ctypes import windll
    user32 = windll.user32

def get_locale():
    if os.name == 'nt':
        w = user32.GetForegroundWindow() 
        tid = user32.GetWindowThreadProcessId(w, 0) 
        return hex(user32.GetKeyboardLayout(tid) & (2**16 - 1))
    elif os.name == 'posix':
        return check_output(["xkblayout-state", "print", "%s"])

possible_key_presses = [ #                                    [AZERTY LAYOUT]           |           [QWERTY LAYOUT]
    [16, 17, 18, 19, 20, 21, 22, 23, 24, 25], #         a  z  e  r  t  y  u  i  o  p    |     q  w  e  r  t  y  u  i  o  p
    [30, 31, 32, 33, 34, 35, 36, 37, 38, 39], #         q  s  d  f  g  h  j  k  l  m    |     a  s  d  f  g  h  j  k  l  ;
    [44, 45, 46, 47, 48, 49, 50, 51, 52, 53]  #         w  x  c  v  b  n  ,  ;  :  !    |     z  x  c  v  b  n  m  ,  .  /
]

layouts = {
    "us": [
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
    ],
    "0x40c": [
        ["a", "z", "e", "r", "t", "y", "u", "i", "o", "p"],
        ["q", "s", "d", "f", "g", "h", "j", "k", "l", "m"],
        ["w", "x", "c", "v", "b", "n", ",", ";", ":", "!"]
    ]
}

judgements = ["MARVELOUS"," PERFECT ", "  GREAT  ", "  GOOD   ", "  OKAY   ", "  MISS   "]

frame_window = 2 #in beats, until i find out how to change it

metronome_enabled = False

auto = False


class Game:
    def input_check(self, obj, key):
        if auto is False:
            if obj["beatpos"]*4 < self.float_ts+frame_window and obj["key"] == key and obj["judgement"]["offset"] is None:
                obj["judgement"]["offset"] = self.curTime - self.startTime
                obj["judgement"]["rating"] = int(abs(obj["beatpos"]*4 - self.float_ts))

                message_after = "[=]"
                if obj["beatpos"]*4 - self.float_ts > 1:
                    message_after = "[-]"
                if obj["beatpos"]*4 - self.float_ts < -1:
                    message_after = "[+]"

                print(obj["keyname"] + ": " + str(obj["judgement"]) + " " + message_after)
                self.screen.addstr(0, 20, judgements[obj["judgement"]["rating"]])

                self.hitsound.stop()
                self.hitsound.play()
                return True
            if obj["beatpos"]*4 < self.float_ts-frame_window and obj["judgement"]["offset"] is None:
                obj["judgement"]["offset"] = self.curTime - self.startTime
                obj["judgement"]["rating"] = 5
                print(obj["keyname"] + ": " + str(obj["judgement"]) + " [MISSED!!!]")
                self.screen.addstr(0, 20, judgements[obj["judgement"]["rating"]])

            return False
        else:
            if obj["beatpos"]*4 <= self.float_ts and obj["judgement"]["offset"] is None:
                obj["judgement"]["offset"] = self.ts/4 - obj["beatpos"]
                obj["judgement"]["rating"] = -2

                message_after = "[AUTO]"

                print(obj["keyname"] + ": " + str(obj["judgement"]) + " " + message_after)
                self.screen.addstr(0, 20, "AUTO")

                self.hitsound.stop()
                self.hitsound.play()
                return True



    def handle_pressed_keys(self, e):
      # print(e.name)
        if e.event_type == keyboard.KEY_DOWN:
            if e.scan_code != 1:
                processedKey = False
                for obj in self.hit_objects:
                    if processedKey is False:
                        processedKey = self.input_check(obj, e.scan_code)
            else:
                self.killThing = False
                self.music.stop()
                self.onQuit()
                self = None
              # curses.curs_set(1)
              # curses.nocbreak()
              # self.screen.keypad(False)
              # curses.echo()
              # curses.endwin()
        if self is not None:
            self.keys = [keyboard._pressed_events[name].scan_code for name in keyboard._pressed_events]
            if self.screen is not None:
                global offset
                global totalElapsed
                self.screen.addstr(0,7, str(self.keys) + "        ")
      #   # if 72 in keys:
      #   #     if 42 in keys:
      #   #         offset += 0.01
      #   #     else:
      #   #         offset += 0.1
      #   #     screen.addstr(1, 7, "New offset :" + str(offset))
      #   # if 80 in keys:
      #   #     offset -= 0.1
      #   #     screen.addstr(1, 7, "New offset :" + str(offset))

    def setup_hit_objects(self, data):
        self.hit_objects = []
        for i in data['notes']:
            if i['type'] != "hit_object":
                pass
            obj = {
                "beatpos": (int(i["beatpos"][0]) * 4) + (i["beatpos"][1] - 1),
                "key": possible_key_presses[int(i["key"]/10)][i["key"]%10],
                "keyname": self.curlayout[int(i["key"]/10)][i["key"]%10].upper(),
                "screenpos": [i["screenpos"][0],i["screenpos"][1]],
                "judgement": {
                    "offset": None,
                    "rating": -1
                },
                "color": i["color"]
            }
            self.hit_objects.append(obj)
            if i["beatpos"][1] != int(i["beatpos"][1]):
                print(obj["beatpos"])

    def update(self):
        y, x = self.screen.getmaxyx()

        self.screen.addstr( 2,  6,  "┌")
        self.screen.addstr(y-1, 6,  "└")
        self.screen.addstr( 2, x-4, "┐")
        self.screen.addstr(y-1,x-4, "┘")

        self.screen.addstr( 2,  7,  "─" * (x - 11))
        self.screen.addstr(y-1, 7,  "─" * (x - 11))

        for i in range(y - 4):
            self.screen.addstr(3+i, 6,  "│")
            self.screen.addstr(3+i, x-4,  "│")
        for obj in self.hit_objects:
            if obj["beatpos"]*4 > self.float_ts-frame_window and obj["judgement"]["offset"] is None:

                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+3,int(obj["screenpos"][0]*(x - 14))+7, "╔═╗", curses.color_pair(obj["color"]))
                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+4,int(obj["screenpos"][0]*(x - 14))+7, "║ ║", curses.color_pair(obj["color"]))
                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+5,int(obj["screenpos"][0]*(x - 14))+7, "╚ ╝", curses.color_pair(obj["color"]))

                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+4,int(obj["screenpos"][0]*(x - 14))+8, str(obj["keyname"]), curses.color_pair(obj["color"]))
                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+5,int(obj["screenpos"][0]*(x - 14))+8, str(math.floor(obj["beatpos"]*2 - self.float_ts/2) + 1))

            else:
                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+3,int(obj["screenpos"][0]*(x - 14))+7, "   ")
                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+4,int(obj["screenpos"][0]*(x - 14))+7, "   ")
                self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+5,int(obj["screenpos"][0]*(x - 14))+7, "   ")

        if auto:
            for obj in self.hit_objects:
                self.input_check(obj, 69) 
                #Any key would work in this case, as key is not checked in this context.
                #Also, 69 is the scan code of "Verr Num". the_more_you_know, I guess.



    def __init__(self, stdscr, onQuit, map = "bpm-offset-test"):
        f = open('charts/' + map + '/data.json')

        self.data = json.load(f)

        f.close()

        #Important variables
        self.bpm = self.data['bpm']
        self.offset = self.data['offset']
        self.steps = 4
        self.ts = 0
        self.float_ts = 0.0
        self.startTime = 0
        self.curTime = 0
        self.newTime = 0
        self.totalElapsed = 0
        self.position = (0,0)
        self.hit_objects = []
        self.keys = []

        print("Keyboard layout: " + str(get_locale()))
        self.curlayout = layouts[get_locale()]
        
        self.screen = stdscr
        self.killThing = True #If set to false, terminates the program.
        
        #Sound loading stuff
        self.vlc_instance = vlc.Instance()
        self.music_file = self.vlc_instance.media_new("charts/" + map + "/" + self.data['sound'])
        self.music = self.vlc_instance.media_player_new()
        self.music.set_media(self.music_file)
        self.metronome_file = self.vlc_instance.media_new('assets/metronome.wav')
        self.metronome = self.vlc_instance.media_player_new()
        self.metronome.set_media(self.metronome_file)
        self.hitsound_file = self.vlc_instance.media_new('assets/clap.wav')
        self.hitsound = self.vlc_instance.media_player_new()
        self.hitsound.set_media(self.hitsound_file)

        self.setup_hit_objects(self.data)
        #keyboard.hook(self.handle_pressed_keys)
        curses.curs_set(0)
        y = 0
        x = 0

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

        self.music.play()
        # Clear screen
        stdscr.clear()
        self.curTime = time()
        self.startTime = self.curTime
        # Check if screen was re-sized (True or False)
        self.resize = curses.is_term_resized(y, x)

        self.onQuit = onQuit

    def loop(self, stdscr):
        if self.killThing:
            duration_of_step = max(0, (60 / self.bpm / self.steps)) #length of 1/4 beat
            #update stuff
            self.elapsed = time() - self.curTime
            self.newTime = time()
            self.totalElapsed+=self.elapsed
            self.float_ts = ((self.newTime-self.startTime)-self.offset)/duration_of_step
            stdscr.addstr(1,0, str(self.float_ts))
            # this is where the funny happens
            if math.floor(((self.newTime-self.startTime)-self.offset)/duration_of_step) > math.floor(((self.curTime-self.startTime)-self.offset)/duration_of_step): #OnStepPassed
                self.ts = math.floor(((self.newTime-self.startTime)-self.offset)/duration_of_step)
                position = (int(self.ts/(4*self.steps)), (int(self.ts/4)%self.steps + 1))
                if self.ts%self.steps == 0: #OnBeatPassed
                    if metronome_enabled is True:
                        self.metronome.stop()
                        self.metronome.play()
                    stdscr.addstr(0,0, "○○○○")
                    stdscr.addstr(0,int(self.ts/4)%self.steps, "●")
                    stdscr.addstr(5,0, str(position))

                  # if self.ts > 32:
                  #    self.killThing = False
            # calc offset
            self.curTime = self.newTime# Action in loop if resize is True:
            if self.resize is True:
                y, x = stdscr.getmaxyx()
                stdscr.clear()
                curses.resizeterm(y, x)
                stdscr.refresh()
            # update code
            self.update()
            stdscr.refresh()
        else:
            self.onQuit()

# game = Game()

# wrapper(game.main)

# curses.curs_set(1)
# curses.nocbreak()
# self.screen.keypad(False)
# curses.echo()
# curses.endwin()