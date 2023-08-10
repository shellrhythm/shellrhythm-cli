"""modified from https://github.com/TheNachoBIT/PyFramebuffer"""

import os
import shutil
import time
import collections

class FPS:
    def __init__(self,avarageof=50):
        self.frametimestamps = collections.deque(maxlen=avarageof)
    def __call__(self):
        self.frametimestamps.append(time.time())
        if len(self.frametimestamps) > 1:
            try:
                return len(self.frametimestamps)/(self.frametimestamps[-1]-self.frametimestamps[0])
            except ZeroDivisionError:
                return 0
        else:
            return 0.0

class Framebuffer:
    """aka. the thing that allows me to condense everything into a single print statement
    (also it adds an FPS function so yea :D)"""
    def UpdateRes(self):
        self.width = shutil.get_terminal_size()[0]
        self.height = shutil.get_terminal_size()[1]

        if self.lastWidth != self.width or self.lastHeight != self.height:
            self.Cleanup()
            if os.name == "posix":
                os.system("clear")
            else:
                os.system("cls")

        self.ClearScreen()
        self.lastWidth = self.width
        self.lastHeight = self.height

        self.clock = 0



    def PrintText(self, text):
        self.buffer += text

    def Cleanup(self):
        self.buffer = ""

    def ClearScreen(self):
        self.Cleanup()

    def Draw(self, prefix = ""):
        print(prefix + self.buffer)
        self.UpdateRes()

    def FPS(self):
        if self.FPSAvgCount < 100:
            if self.FPSManager() > self.FPSAvg:
                self.FPSAvg = self.FPSManager()

            self.FPSAvgCount += 1
        else:
            self.FPSAvgCount = 0
            self.FPSAvg = self.FPSManager()

        return int(self.FPSAvg)
    
    def __init__(self):
        self.lastWidth = 0
        self.lastHeight = 0
        self.buffer = ""
        self.FPSManager = FPS()
        self.FPSAvg = 0
        self.FPSAvgCount = 0

        self.UpdateRes()