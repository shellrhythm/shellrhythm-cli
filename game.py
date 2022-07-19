import curses
import math
from time import time_ns
import sys
import keyboard
import json

from pybass3 import Song
from curses import wrapper

def get_locale():
    f = open("options.json")
    localestuff = json.load(f)
    f2 = open("layout/" + localestuff["layout"])
    rawstring = f2.read()

    f.close()
    f2.close()

    rows = rawstring.split("\n")
    layout = [ [], [], []]
    for i in range(len(rows)):
        layout[i] = [char for char in rows[i]]

    print(layout)
    return layout


possible_key_presses = [ #                                    [AZERTY LAYOUT]           |           [QWERTY LAYOUT]
    [16, 17, 18, 19, 20, 21, 22, 23, 24, 25], #         a  z  e  r  t  y  u  i  o  p    |     q  w  e  r  t  y  u  i  o  p
    [30, 31, 32, 33, 34, 35, 36, 37, 38, 39], #         q  s  d  f  g  h  j  k  l  m    |     a  s  d  f  g  h  j  k  l  ;
    [44, 45, 46, 47, 48, 49, 50, 51, 52, 53]  #         w  x  c  v  b  n  ,  ;  :  !    |     z  x  c  v  b  n  m  ,  .  /
]

judgements = ["MARVELOUS"," PERFECT ", "  GREAT  ", "  GOOD   ", "  OKAY   ", "  MISS   "]

accu_judgements = [100, 95, 50, 25, 0, 0]

frame_window = [30, 50, 80, 100, 120, 160] #in ms

metronome_enabled = False

maxscore = 1000000

auto = False


class Game:
    def playsound(self, sound):
        song = Song(sound)
        song.play()
        print("Playing: ", sound)
        return song

    def get_judgement(self, ms):
        for i in range(len(frame_window)):
            if frame_window[i] < ms:
                i += 1
            else:
                return i

    def input_check(self, obj, key):
        if auto is False:
            print(obj["secondPos"],self.totalElapsed)

            # the thing
            if obj["secondPos"] > (self.totalElapsed - 0.160) and obj["key"] == key and obj["judgement"]["offset"] is None:
                obj["judgement"]["offset"] = round(((self.curTime - self.startTime) - obj["secondPos"]) * 1000, 2)
                obj["judgement"]["rating"] = self.get_judgement(abs(obj["judgement"]["offset"]))

                if obj["judgement"]["rating"] == None:
                    obj["judgement"]["rating"] = 5

                message_after = "[=]"
                if obj["judgement"]["offset"] > 0.05:
                    message_after = "[-]"
                if obj["judgement"]["offset"] < -0.05:
                    message_after = "[+]"

                print(obj["keyname"] + ": " + str(obj["judgement"]) + " " + message_after)
                self.screen.addstr(0, 20, judgements[obj["judgement"]["rating"]])
                self.screen.addstr(1, 20, str(obj["judgement"]["offset"]) + "        ")
                
                self.playsound('assets/clap.wav')

                self.totalHits += 1
                self.totalAccu += accu_judgements[obj["judgement"]["rating"]]
                self.accuracy = self.totalAccu / self.totalHits

                self.score += (maxscore/self.totalObjects)*(accu_judgements[obj["judgement"]["rating"]]/100)
                return True

            # the miss thing
            if obj["secondPos"] < (self.totalElapsed + 0.160) and obj["judgement"]["offset"] is None:
                obj["judgement"]["offset"] = round(((self.curTime - self.startTime) - obj["secondPos"]) * 1000, 2)
                obj["judgement"]["rating"] = 5
                print(obj["keyname"] + ": " + str(obj["judgement"]) + " [MISSED!!!]")
                self.screen.addstr(0, 20, judgements[obj["judgement"]["rating"]])

                self.totalHits += 1
                self.totalAccu += accu_judgements[obj["judgement"]["rating"]]
                self.accuracy = self.totalAccu / self.totalHits

            return False


        else:
            if obj["beatpos"] <= self.float_ts/4 and obj["judgement"]["offset"] is None:
                obj["judgement"]["offset"] = round(((self.curTime - self.startTime) - obj["secondPos"]) * 1000, 2)
                obj["judgement"]["rating"] = -2

                message_after = "[AUTO]"

                print(obj["keyname"] + ": " + str(obj["judgement"]) + " " + message_after)
                self.screen.addstr(0, 20, "AUTO")

                self.playsound('assets/clap.wav')

                self.totalHits += 1
                self.totalAccu += accu_judgements[0]
                self.accuracy = self.totalAccu / self.totalHits

                self.score += maxscore/self.totalObjects*(accu_judgements[0]/100)
                
                return True


    def handle_pressed_keys(self, e):
      # print(e.name)
        if e.event_type == keyboard.KEY_DOWN:
            if e.scan_code != 1:
                if e.scan_code == 4:
                    global metronome_enabled
                    metronome_enabled = not metronome_enabled
                if e.scan_code == 72:
                    self.offset += 0.01
                    self.screen.addstr(1, 7, "New offset :" + str(round(self.offset, 2)))
                if e.scan_code == 80:
                    self.offset -= 0.01
                    self.screen.addstr(1, 7, "New offset :" + str(round(self.offset, 2)))

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

    def setup_hit_objects(self, data):
        self.hit_objects = []
        for i in data['notes']:
            if i['type'] == "hit_object":
                self.totalObjects += 1
                obj = {
                    "beatpos": (int(i["beatpos"][0]) * 4) + (i["beatpos"][1] - 1),
                    "secondPos": ((int(i["beatpos"][0]) * 4) + (i["beatpos"][1] - 1))*max(0, 60 / self.bpm),
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
            if i['type'] == "end":
                self.stopPosition = (int(i["beatpos"][0]) * 4) + (i["beatpos"][1] - 1)
            

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
            
            earliest_point = obj["secondPos"] - 0.700
            latest_point = obj["secondPos"] + 0.160

            if (self.curTime - self.startTime) > earliest_point:
                if (self.curTime - self.startTime) < latest_point and obj["judgement"]["offset"] is None:
                  
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+3,int(obj["screenpos"][0]*(x - 14))+7, "╔═╗", curses.color_pair(obj["color"]))
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+4,int(obj["screenpos"][0]*(x - 14))+7, "║ ║", curses.color_pair(obj["color"]))
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+5,int(obj["screenpos"][0]*(x - 14))+7, "╚ ╝", curses.color_pair(obj["color"]))

                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+4,int(obj["screenpos"][0]*(x - 14))+8, str(obj["keyname"]), curses.color_pair(obj["color"]))
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+5,int(obj["screenpos"][0]*(x - 14))+8, str(math.floor(obj["beatpos"]*2 - self.float_ts/2)))

                else:
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+3,int(obj["screenpos"][0]*(x - 14))+7, "   ")
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+4,int(obj["screenpos"][0]*(x - 14))+7, "   ")
                    self.screen.addstr(int(obj["screenpos"][1]*(y - 7))+5,int(obj["screenpos"][0]*(x - 14))+7, "   ")

        if auto:
            for obj in self.hit_objects:
                self.input_check(obj, 69) 
                #Any key would work in this case, as key is not checked in this context.
                #Also, 69 is the scan code of "Verr Num". the_more_you_know, I guess.


        self.screen.addstr(0, int((x-len(str(round(self.accuracy,2)))-2)/2), str(round(self.accuracy,2)) + "%")
        self.screen.addstr(1, int((x-len(str(int(self.score)))-2)/2),str(int(self.score))+" ")



    def __init__(self, stdscr, onQuit, map = "bpm-offset-test"):
        self.data = {}
        print(type(map))
        if isinstance(map, str):
            print("The map is apparently a string.")
            f = open('charts/' + map + '/data.json')

            self.data = json.load(f)

            f.close()
        elif isinstance(map, dict):
            self.data = map

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
        self.stopPosition = 2**32 #in measures
        self.totalObjects = 0
        self.totalHits = 0
        self.totalAccu = 0
        self.accuracy = 0.0
        self.score = 0

      # print("Keyboard layout: " + str(get_locale()))
        self.curlayout = get_locale()
        
        self.screen = stdscr
        self.killThing = True #If set to false, terminates the program.
        

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

        self.music = self.playsound("charts/" + self.data["filename"] + "/" + self.data['sound'])
        # Clear screen
        stdscr.clear()
        self.curTime = time_ns()/10**9
        self.startTime = self.curTime
        # Check if screen was re-sized (True or False)
        self.resize = curses.is_term_resized(y, x)

        self.onQuit = onQuit

    def loop(self, stdscr):
        if self.killThing:
            if self.totalElapsed < 0.01:
                stdscr.clear()
            duration_of_step = max(0, (60 / self.bpm / self.steps)) #length of 1/4 beat
            #update stuff
            self.elapsed = time_ns()/10**9 - self.curTime
            self.newTime = time_ns()/10**9
            self.totalElapsed+=self.elapsed
            self.float_ts = ((self.newTime-self.startTime)-self.offset)/duration_of_step
          # stdscr.addstr(1,0, str(round(self.float_ts, 2)))
            if self.float_ts > self.stopPosition * 4:
                self.killThing = False
            # this is where the funny happens
            if math.floor(((self.newTime-self.startTime)-self.offset)/duration_of_step) > math.floor(((self.curTime-self.startTime)-self.offset)/duration_of_step): #OnStepPassed
                self.ts = math.floor(((self.newTime-self.startTime)-self.offset)/duration_of_step)
                position = (int(self.ts/(4*self.steps)), (int(self.ts/4)%self.steps + 1))
                if self.ts%self.steps == 0: #OnBeatPassed
                    if metronome_enabled is True:
                        self.playsound('assets/metronome.wav')
                    stdscr.addstr(0,0, "○○○○")
                    stdscr.addstr(0,int(self.ts/4)%self.steps, "●")
                    stdscr.addstr(5,0, str(position))

                
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

if __name__ == "__main__":
    print("------------------------------[OH NO]------------------------------")
    print("Whoops! It looks like you were trying to launch game.py by itself! This is currently not possible.")
    print("Instead, write \"python ./index.py\" to launch the actual game!")

    print("\n- #Guigui")
    print("-------------------------------------------------------------------")