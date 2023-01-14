from blessed import Terminal
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

beforeWidth = 0
beforeHeight = 0
hasBeenResized = False
minWidth = 125
minHeight = 32

def on_resize(sig, action):
	print(term.clear)
	sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=max(term.height,minHeight), cols=max(term.width, minWidth)))
	global beforeWidth, beforeHeight, hasBeenResized
	beforeWidth = term.width
	beforeHeight = term.height
	hasBeenResized = True

if platform.system() != "Windows":
	signal.signal(signal.SIGWINCH, on_resize)

def check_term_size():
	if beforeWidth != term.width or beforeHeight != term.height:
		on_resize(None, None)

def print_at(x, y, toPrint):
	print(f"{term.move_xy(x=int(x), y=int(y))}" + toPrint)

def debug_val(val):
		if not val:
			print_at(0,term.height-2,term.move_up(1))
		elif val.is_sequence:
			print_at(0,term.height-2,"got sequence: {0}.".format((str(val), val.name, val.code)) + term.clear_eol)
		elif val:
			print_at(0,term.height-2,f"got {val}." + term.clear_eol)

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
		print_lines_at(x, y, str(image))
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

def print_box(x,y,width, height, color, style):
	curBoxStyle = "????????"
	if type(style) is int:
		curBoxStyle = box_styles[style]
	elif type(style) is str:
		curBoxStyle = box_styles
	print_at(x,y,color + curBoxStyle[0] + (curBoxStyle[1]*(width-2)) + curBoxStyle[2] + term.normal)
	print_at(x,y+height-1,color + curBoxStyle[5] + (curBoxStyle[6]*(width-2)) + curBoxStyle[7] + term.normal)
	print_column(x,y+1,height-2,color + curBoxStyle[3])
	print_column(x+width-1,y+1,height-2,color + curBoxStyle[4])