from blessed import Terminal
try:
	from PyFramebuffer import *
except ImportError:
	from src.PyFramebuffer import *
import os, sys
import json
from term_image.image import *
import signal
import platform

box_styles = [
	"┌─┐││└─┘", #Base box
	".-.||'-'"  #Minimal box
	#TODO: Add more styles
]

term = Terminal()
f = Framebuffer()

screenOffset = [0, 0]

# toDraw = ""

beforeWidth = 0
beforeHeight = 0
hasBeenResized = False
minWidth = 125
minHeight = 32

def on_resize(sig, action):
	# print(term.clear)
	# sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=max(term.height,minHeight), cols=max(term.width, minWidth)))
	f.UpdateRes()
	global beforeWidth, beforeHeight, hasBeenResized
	beforeWidth = f.width
	beforeHeight = f.height
	hasBeenResized = True

if platform.system() != "Windows":
	signal.signal(signal.SIGWINCH, on_resize)

def framerate():
	return f.FPS()

def check_term_size():
	if beforeWidth != f.width or beforeHeight != f.height:
		on_resize(None, None)

def print_at(x, y, toPrint):
	global screenOffset
	realPrinted = term.split_seqs(toPrint)
	result = []
	
	count = 0
	actualCount = 0
	while count < len(realPrinted):
		if len(realPrinted[count]) > 1:
			printedChar = realPrinted[count]
			nextOne = count+1
			# lmao = term.strip_seqs(realPrinted[nextOne])
			# notlmao = lmao != realPrinted[nextOne]
			if len(realPrinted) > nextOne:
				printedChar += realPrinted[nextOne]
			while len(realPrinted) > nextOne+1 and term.strip_seqs(realPrinted[nextOne]) != realPrinted[nextOne]:
				nextOne += 1
				printedChar += realPrinted[nextOne]
			if realPrinted[count] not in ["\n", "\r", "\r\n"]: #screw line breaks in particular
				try:
					if term.strip_seqs(printedChar) == "":
						printedChar += term.strip_seqs(f.buffer[int(y+1+screenOffset[1]) * f.width + int(x+screenOffset[0]) + actualCount])
					f.PrintAt(int(x+screenOffset[0]) + actualCount, int(y+1+screenOffset[1]),printedChar)
				except:
					pass
				result.append(printedChar)
			count = nextOne+1
		else:
			if realPrinted[count] not in ["\n", "\r", "\r\n"]: #screw line breaks in particular
				try:
					f.PrintAt(int(x+screenOffset[0]) + actualCount, int(y+1+screenOffset[1]),realPrinted[count])
				except:
					pass
				result.append(realPrinted[count])
			count += 1
		
		if count < len(realPrinted):
			if realPrinted[count-1] not in ["\n", "\r", "\r\n"]: #screw line breaks in particular
				actualCount += 1
	pass
	# f.PrintText(int(x), int(y), toPrint)
	# global toDraw
	# if not "toDraw" in globals():
	# 	toDraw = ""
	# toDraw += f"{term.move_xy(x=int(x), y=int(y))}" + toPrint

def refresh():
	"""
Pro tip: only call this at the end of a frame! Or else, this will reduce the framerate greatly!
	"""
	# global toDraw
	# print(toDraw)
	# toDraw = ""
	f.Draw(term.move_xy(0,0))

def debug_val(val):
		if not val:
			pass
		elif val.is_sequence:
			print_at(0,term.height-2,"got sequence: {0}.".format((str(val), val.name, val.code)))
		elif val:
			print_at(0,term.height-2,f"got {val}.")

def print_lines_at(x, y, text, center = False, eol = False, color = None):
	if color is None:
		color = term.normal
	lines = text.split("\n")
	for i in range(len(lines)):
		if center:
			print_at(x, y + i, color + term.center(lines[i]) + term.normal)
		else:
			if eol:
				print_at(x, y + i, color + lines[i] + term.normal + term.clear_eol)
			else:
				print_at(x, y + i, color + lines[i] + term.normal)

def print_image(x,y,imagePath,scale):
	if os.path.exists(imagePath):
		image = from_file(imagePath, width=scale)
		stringifiedImage = str(image)
		print_lines_at(x, y, stringifiedImage)
		return True
	else:
		return False
	
def print_column(x, y, size, char):
	for i in range(size):
		print_at(x, y + i, char)

def print_cropped(x, y, maxsize, text, offset, color, isWrapAround = True):
	if isWrapAround:
		print_at(x, y, color + (text*(3+int(maxsize/len(text))))[(offset%len(text))+len(text):maxsize+(offset%len(text))+len(text)] + term.normal)
	else:
		actualText = text[offset%len(text):maxsize+(offset%len(text))]
		print_at(x, y, color + actualText + term.normal + (" "*(maxsize - len(actualText))))

def print_box(x,y,width, height, color = term.normal, style = 0, caption = ""):
	curBoxStyle = "????????"
	if type(style) is int:
		curBoxStyle = box_styles[style]
	elif type(style) is str:
		curBoxStyle = box_styles
	if caption != "":
		print_at(x,y,color + curBoxStyle[0] + term.reverse + caption + term.normal + (curBoxStyle[1]*(width-(2+len(caption)))) + curBoxStyle[2] + term.normal)
	else:
		print_at(x,y,color + curBoxStyle[0] + (curBoxStyle[1]*(width-2)) + curBoxStyle[2] + term.normal)
	print_at(x,y+height-1,color + curBoxStyle[5] + (curBoxStyle[6]*(width-2)) + curBoxStyle[7] + term.normal)
	print_column(x,y+1,height-2,color + curBoxStyle[3])
	print_column(x+width-1,y+1,height-2,color + curBoxStyle[4])

def too_small(bypass = False):
	"""Checks if the screen size is smaller than what the game requires.
	Side note: having the bypass variable set to True will completely bypass this check"""
	return (f.width < minWidth or f.height < minHeight) and not bypass


class Grid:
	x = 0
	y = 0
	width = 0
	height = 0
	pointsToPlot = []
	colors = []
	symbolLookup = [
		[" ", "⠁", "⠂", "⠄", "⡀"], 
		["⠈", "⠉", "⠊", "⠌", "⡈"],
		["⠐", "⠑", "⠒", "⠔", "⡐"],
		["⠠", "⠡", "⠢", "⠤", "⡠"],
		["⢀", "⢁", "⢂", "⢄", "⣀"]
	]
	gridrange = [-0.4,0.4]
	offset = 2
	def processPoints(self, point1, point2):
		if point1//4 == point2//4:
			return [self.symbolLookup[int(point1)%4+1][int(point2)%4+1]]
		else:
			return [self.symbolLookup[int(point1)%4+1][0], self.symbolLookup[0][int(point1)%4+1]]

	def draw(self, cursorPos = 0):
		for i in range(max(0, (cursorPos*2)-len(self.pointsToPlot)), min(len(self.pointsToPlot), (cursorPos + self.width)*2), 2):
			point1 = min(max(self.pointsToPlot[i],   self.gridrange[0]), self.gridrange[1])
			point2 = min(max(self.pointsToPlot[i+1], self.gridrange[0]), self.gridrange[1])
			firstpos = ((point1 / (self.gridrange[1] - self.gridrange[0])) - self.gridrange[0]) * self.height*4 + self.offset
			secpos   = ((point2 / (self.gridrange[1] - self.gridrange[0])) - self.gridrange[0]) * self.height*4 + self.offset
			points = self.processPoints(firstpos, secpos)
			for j in range(len(points)):
				atpos = ((self.pointsToPlot[i+j] / (self.gridrange[1] - self.gridrange[0])) - self.gridrange[0]) * self.height + (self.offset/4)
				print_at(self.x + (i//2), self.y + int(atpos), self.colors[i+j] + points[j])

	def __init__(self, x, y, width, height) -> None:
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		pass