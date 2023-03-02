import os
import shutil
import time
import collections

class FPS:
    def __init__(self,avarageof=50):
        self.frametimestamps = collections.deque(maxlen=avarageof)
    def __call__(self):
        self.frametimestamps.append(time.time())
        if(len(self.frametimestamps) > 1):
            return len(self.frametimestamps)/(self.frametimestamps[-1]-self.frametimestamps[0])
        else:
            return 0.0

class Framebuffer:
	def InitFB(self):
		self.buffer = [];
		self.FPSManager = FPS()
		self.FPSAvg = 0;
		self.FPSAvgCount = 0;

	def UpdateRes(self):
		self.width = shutil.get_terminal_size()[0];
		self.height = shutil.get_terminal_size()[1];

		if self.lastWidth != self.width or self.lastHeight != self.height:
			self.Cleanup()
			os.system("cls")
			self.Resize()

		self.ClearScreen()
		self.lastWidth = self.width
		self.lastHeight = self.height

		self.clock = 0

	def Resize(self):
		for x in range(self.width * self.height):
			self.buffer.append(' ')

	def __init__(self):
		self.lastWidth = 0
		self.lastHeight = 0

		self.InitFB()
		self.UpdateRes()

	def PrintAt(self, x, y, char):
		# print("Element: {0}, Size: {1}".format(len(self.buffer), x * self.width + y))
		if x < self.width:
			self.buffer[y * self.width + x] = char

	def PrintText(self, x, y, text):
		count = 0
		while count < len(text):
			self.PrintAt(x + count, y, text[count])
			count += 1

	def Cleanup(self):
		self.buffer.clear()

	def ClearScreen(self):
		try:
			for x in range(self.width * self.height):
				self.buffer[x] = ' '
		except:
			pass

	def Draw(self, prefix = ""):
		joined = [''.join(self.buffer[i*self.width:(i+1)*self.width]) for i in range(self.height)]
		frame = ''.join(joined)
		# isLengthWidth = [len(i) for i in joined]
		print(prefix + frame)
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