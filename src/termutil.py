from blessed import Terminal
import os, sys
import json
from term_image.image import *

term = Terminal()

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
	image = from_file(imagePath, width=scale)
	print_lines_at(x, y, str(image))
	
def print_column(x, y, size, char):
	for i in range(size):
		print_at(x, y + i, char)

def print_cropped(x, y, maxsize, text, offset, color, isWrapAround = True):
	if isWrapAround:
		print_at(x, y, color + (text*3)[(offset%len(text))+len(text):maxsize+(offset%len(text))+len(text)] + term.normal)
	else:
		actualText = text[offset%len(text):maxsize+(offset%len(text))]
		print_at(x, y, color + actualText + term.normal + (" "*(maxsize - len(actualText))))