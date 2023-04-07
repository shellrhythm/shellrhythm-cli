from blessed import Terminal
from wcwidth import wcwidth
try:
	from PyFramebuffer import *
except ImportError:
	from src.PyFramebuffer import *
import os, sys
import json
from term_image.image import *
import signal
import platform
import re

def strip_seqs(text):
	ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\([0-?]*[ -/]*[@-~])')
	return ansi_escape.sub('', text)

box_styles = [
	"┌─┐││└─┘", #Base box
	".-.||'-'"  #Minimal box
	#TODO: Add more styles
]

term = Terminal()
f = Framebuffer()


def prng (beat = 0.0, seed = 0): return int(beat * 210413 + 2531041 * (seed+1.3)/3.4) % 2**32 #quick pseudorandomness don't mind me

def colorText(text = "", beat = 0.0):
	#Here, replace something like {cf XXXXXX} with the corresponding terminal color
	#Combinaisons to support: 
	# - cf RRGGBB		Foreground color
	# - cb RRGGBB		Background color
	# - b				Bold text
	# - i				Italic text
	# - u				Underline text
	# - n				Reverts text back to normal state
	# - k				Glitchifies text

	text = text.replace("\{", "￼ø").replace("\}", "ŧ￼").replace("{", "�{").replace("}", "}�") 
	#If you are using � or ￼ genuiunely, what the #### is wrong with you /gen
	data = text.split("�")
	renderedText = ""
	glitchifyNext = False
	for i in data:
		if i.startswith("{") and i.endswith("}"):
			ac = i.strip("{}")
			if ac.startswith("cf"):
				col = color_code_from_hex(ac.replace("cf ", "", 1))
				renderedText += term.color_rgb(col[0], col[1], col[2])
				continue
			if ac.startswith("cb"):
				col = color_code_from_hex(ac.replace("cb ", "", 1))
				renderedText += term.on_color_rgb(col[0], col[1], col[2])
				continue
			if ac == "b":
				renderedText += term.bold
				continue
			if ac == "i":
				renderedText += term.italic
				continue
			if ac == "u":
				renderedText += term.underline
				continue
			if ac == "n":
				renderedText += term.normal
				glitchifyNext = False
				continue
			if ac == "k":
				glitchifyNext = True
				continue
			if glitchifyNext:
				#this big chunk will generate a random string with characters from 0x20 to 0x7e
				renderedText += "".join([chr(int(prng(beat, k))%(0x7e-0x20) + 0x20) for k in range(len(i.replace("￼ø", "{").replace("ŧ￼", "}")))])
			else:
				renderedText += i.replace("￼ø", "{").replace("ŧ￼", "}")
		else:
			if glitchifyNext:
				renderedText += "".join([chr(int(prng(beat, k))%(0x7e-0x20) + 0x20) for k in range(len(i.replace("￼ø", "{").replace("ŧ￼", "}")))])
			else:
				renderedText += i.replace("￼ø", "{").replace("ŧ￼", "}")
	return renderedText

def split_seqs(text):
	#apparently the part that needs to be optimized the *most*
	pattern = term._caps_unnamed_any
	result = []
	matches = list(re.finditer(pattern, text))
	for i in range(len(matches)):
		result += [matches[i].group()]
	return result

def color_code_from_hex(hexcode:str) -> list:
	# hexcode is string built like "RRGGBB"
	output = [0,0,0]
	if len(hexcode) == 6: #No more, no less
		try:
			output = [int(hexcode[i:i+2], 16) for i in range(0, len(hexcode), 2)]
		except ValueError:
			pass
	return output

def hexcode_from_color_code(code:list) -> str:
	output = "000000"
	if len(code) == 3:
		output = hex((code[0] * 256**2) + (code[1] * 256) + code[2]).replace("0x", "")
	if len(output) < 6:
		output = "0"*(6-len(output)) + output
	return output
# toDraw = ""

beforeWidth = 0
beforeHeight = 0
hasBeenResized = False
minWidth = 125
minHeight = 32

def on_resize(sig, action):
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
	x = int(x)
	y = int(y)
	realPrinted = split_seqs(toPrint)
	result = []
	
	count = 0
	actualCount = 0
	while count < len(realPrinted):
		if len(realPrinted[count]) > 1:
			printedChar = realPrinted[count]
			nextOne = count+1

			if realPrinted[count] not in ["\n", "\r"]: #screw line breaks in particular
				if len(realPrinted) > nextOne:
					printedChar += realPrinted[nextOne]
				while len(realPrinted) > nextOne+1 and strip_seqs(realPrinted[nextOne]) != realPrinted[nextOne]:
					nextOne += 1
					printedChar += realPrinted[nextOne]
				try:
					if strip_seqs(printedChar) == "":
						printedChar += f.buffer[(y+1) * f.width + x + actualCount]
					f.PrintAt(x+actualCount, y+1,printedChar)
				except:
					pass
				result.append(printedChar)
			count = nextOne+1
		else:
			if realPrinted[count] not in ["\n", "\r"]: #screw line breaks in particular
				try:
					f.PrintAt(x+actualCount, y+1,realPrinted[count])
				except:
					pass
				result.append(realPrinted[count])
			wclen = wcwidth(realPrinted[count])
			if wclen > 1:
				for i in range(1, wclen):
					f.PrintAt(x+actualCount+i, y+1, "")
				actualCount += wclen-1
			count += 1
		
		if count < len(realPrinted):
			if realPrinted[count-1] not in ["\n", "\r"]: #screw line breaks in particular
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
	f.Draw(term.move_xy(0,0) + term.normal)

def debug_val(val):
		if not val:
			pass
		elif val.is_sequence:
			print_at(0,term.height-2,"got sequence: {0}.".format((str(val), val.name, val.code)))
		elif val:
			print_at(0,term.height-2,f"got {val}.")

def print_lines_at(x:int, y:int, text:str, center = False, color = None):
	if color is None:
		color = term.normal
	lines = text.split("\n")
	for i in range(len(lines)):
		if center:
			print_at(x, y + i, color + term.center(lines[i]) + term.normal)
		else:
			print_at(x, y + i, color + lines[i] + term.normal)

def print_image(x,y,imagePath,scale):
	if os.path.exists(imagePath):
		image = BlockImage.from_file(imagePath, width=scale)
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
		print_at(x,y,color + curBoxStyle[0] + term.reverse + caption + term.normal + color + (curBoxStyle[1]*(width-(2+len(caption)))) + curBoxStyle[2] + term.normal)
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
