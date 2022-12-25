from blessed import Terminal
import os, sys
import json
from pybass3 import Song
import time
# from index import *
if __name__ == "src.editor":
	from src.game import *
	from src.conductor import *
else:
	from game import *
	from conductor import *

term = Terminal()

class Editor:
	turnOff = False
	mapToEdit = {}
	localConduc = Conductor()
	playtest = False
	commandMode = False
	commandString = ""
	commandSelectPos = 0
	commandAutoMode = False
	commandAutoPropositions = []
	needsSaving = False
	fileLocation = ""
	snap = 4
	selectedNote = 0
	layout = []
	dontDrawList = []
	keyPanelEnabled = False
	keyPanelKey = ""
	keyPanelSelected = -1 #Note: use -1 when creating a new note

	def autocomplete(self, command):
		output = []

		#TODO where do i even begin

		return output
	
	def create_note(self, atPos, key):
		if "notes" in self.mapToEdit:
			newNote = {
				"type": "hit_object",
				"beatpos": [
					int(atPos//4),
					round(atPos%4, 5)
				],
				"key": key,
				"screenpos": [
					0.5,
					0.5
				],
				"color": 0
			}
			self.mapToEdit["notes"].append(newNote)

	def draw_changeKeyPanel(self, toptext, curKey):
		print_at(int((term.width-10)*0.5), int((term.height-7)*0.5), "-"*10)
		print_at(int((term.width-10)*0.5), int((term.height+7)*0.5), "-"*10)
		print_column(int((term.width-10)*0.5), int((term.height-6)*0.5), 13, "|")
		print_column(int((term.width+10)*0.5), int((term.height-6)*0.5), 13, "|")
		print_at(int((term.width-len(toptext))*0.5), int((term.height-6)*0.5), toptext)

	def load_chart(self, chart_name, file = "data"):
		self.fileLocation = f"./charts/{chart_name}/{file}.json"
		if os.path.exists(self.fileLocation):
			print(term.clear)
			f = open(f"./charts/{chart_name}/{file}.json")
			self.mapToEdit = json.load(f)
			f.close()

			self.localConduc.loadsong(self.mapToEdit)
			return True
		else:
			return False

	def draw(self):
		# print_at(0,term.height-5, term.normal+"-"*(term.width-1))
		print_at(0,term.height-3, term.normal+"-"*(term.width))

		#Timeline
		for i in range(-(int(term.width/80)+1),int(term.width/8)-(int(term.width/80))):
			char = "'"
			if (4-(i%4))%4 == (int(self.localConduc.currentBeat)%4):
				char = "|"
			slightOffset = int(self.localConduc.currentBeat%1 * 8)
			realDrawAt = int((i*8)+(term.width*0.1)-slightOffset)
			drawAt = max(realDrawAt, 0)
			maxAfterwards = int(min(7,term.width - (drawAt+1)))
			if i+self.localConduc.currentBeat >= 0 or realDrawAt == drawAt:
				print_at(drawAt, term.height-5, char+("-"*maxAfterwards))
			else:
				print_at(drawAt, term.height-5, "-"*(maxAfterwards+1))
		print_at(int(term.width*0.1), term.height-4, "@")
		print_at(0,term.height-6, term.normal+f"BPM: {self.localConduc.bpm} | Snap: 1/{self.snap} | Bar: {int(self.localConduc.currentBeat//4)} | Beat: {round(self.localConduc.currentBeat%4, 5)} |{term.clear_eol}")

		if self.mapToEdit != {}:
			for i in range(len(self.mapToEdit["notes"])):
				j = len(self.mapToEdit["notes"]) - (i+1)
				note = self.mapToEdit["notes"][j]
				if self.mapToEdit["notes"][j]["type"] == "hit_object":
					screenPos = note["screenpos"]
					characterDisplayed = self.layout[note["key"]]
					calculatedPos = Game.calculatePosition(screenPos, 5, 3, term.width-10, term.height-7)
					remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat

					#TIMELINE
					if remBeats*8+(term.width*0.1) >= 0:
						if self.selectedNote == j:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.reverse}{colors[note['color']]}{term.bold}{characterDisplayed.upper()}{term.normal}")
						else:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.normal}{colors[note['color']]}{term.bold}{characterDisplayed.upper()}{term.normal}")


					if note in self.dontDrawList and remBeats > -0.1:
						self.dontDrawList.remove(note)
					if remBeats > -0.1 and remBeats < 4:
						if self.selectedNote == j:
							Game.renderNote(None, calculatedPos, colors[note["color"]]+term.reverse, characterDisplayed, remBeats)
						else:
							Game.renderNote(None, calculatedPos, colors[note["color"]], characterDisplayed, remBeats)
					elif remBeats < -0.1 and note not in self.dontDrawList:
						print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
						self.dontDrawList.append(note)
				else:
					remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
					if remBeats*8+(term.width*0.1) >= 0:
						if self.selectedNote == j:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.reverse}{term.bold_grey}▚{term.normal}")
						else:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.normal}{term.bold_grey}▚{term.normal}")
			#Current note info
			selectedNote = self.mapToEdit['notes'][self.selectedNote]
			if selectedNote["type"] == "hit_object":
				print_at(0, term.height-7, term.normal+f"Currently selected note: {self.selectedNote} | Color: {colors[selectedNote['color']]}[{selectedNote['color']}]{term.normal} | Screenpos: {selectedNote['screenpos']} | Beatpos: {selectedNote['beatpos']}{term.clear_eol}")
			else:
				print_at(0, term.height-7, f"{term.normal}Currently selected note: {self.selectedNote} | End position: {selectedNote['beatpos']}{term.clear_eol}")
		else:
			text_nomaploaded = "Wow, such empty."
			print_at(int((term.width - len(text_nomaploaded))*0.5),int(term.height*0.4), term.normal+text_nomaploaded)
			
		if self.commandMode:
			print_at(0,term.height-2, term.normal+":"+self.commandString+term.clear_eol)
			chrAtCursor = ""
			if len(self.commandString) != 0:
				chrAtCursor = self.commandString[len(self.commandString)-(self.commandSelectPos+1)]
				print_at(len(self.commandString)-self.commandSelectPos, term.height-2, term.underline + chrAtCursor + term.normal)

	def run_command(self, command = ""):
		commandSplit = command.split(" ")
		print_at(0,term.height-2, term.clear_eol)
		if commandSplit[0] == "q!" or (commandSplit[0] == "q" and not self.needsSaving):
			self.turnOff = True
			return True, ""
		elif commandSplit[0] == "w":
			output = json.dumps(self.mapToEdit)
			f = open(self.fileLocation, "w")
			f.write(output)
			f.close()
			return True, "Saved successfully!"
			#save
		elif commandSplit[0] == "o":
			if len(commandSplit) == 2:
				fileExists = self.load_chart(commandSplit[1])
				if not fileExists:
					return fileExists, "This chart doesn't exist."
				else:
					return fileExists, "Chart loaded successfully."
			elif len(commandSplit) == 3:
				self.load_chart(commandSplit[1], commandSplit[2])
			else:
				if len(commandSplit) < 2:
					return False, "Too few arguments."
				else:
					return False, "Too many arguments."
		elif commandSplit[0] == "p":
			if len(commandSplit) > 1:
				if commandSplit[1].isdigit():
					self.create_note(self.localConduc.currentBeat, int(commandSplit[1]))
					return True, "Successfully created a new note."
			return False, "Whoops, looks like you're in unimplemented territory!"

		else:
			if len(commandSplit[0]) > 128:
				return False, "...what?"
			return False, "Command not found."

		return True, ""
		

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/120)
		if not self.commandMode:
			# debug_val(val)
			if val.name != "KEY_ENTER" and val:
				print_at(0,term.height-2, term.clear_eol)
			if val == ":":
				self.commandMode = True
				self.commandString = ""
			if val.name == "KEY_RIGHT":
				self.localConduc.currentBeat += (1/self.snap)*4
				print_at(0,term.height-4, term.clear_eol)
			if val.name == "KEY_LEFT":
				self.localConduc.currentBeat = max(self.localConduc.currentBeat - (1/self.snap)*4, 0)
				print_at(0,term.height-4, term.clear_eol)
			if self.mapToEdit != {}:
				if val.name == "KEY_DOWN":
					print_at(0,term.height-4, term.clear_eol)
					self.selectedNote = min(self.selectedNote + 1, len(self.mapToEdit["notes"])-1)
					self.localConduc.currentBeat = (self.mapToEdit["notes"][self.selectedNote]["beatpos"][0] * 4 + self.mapToEdit["notes"][self.selectedNote]["beatpos"][1])
				if val.name == "KEY_UP":
					print_at(0,term.height-4, term.clear_eol)
					self.selectedNote = max(self.selectedNote - 1, 0)
					self.localConduc.currentBeat = (self.mapToEdit["notes"][self.selectedNote]["beatpos"][0] * 4 + self.mapToEdit["notes"][self.selectedNote]["beatpos"][1])

				if val == "u":
					self.localConduc.currentBeat = max(self.localConduc.currentBeat - (1/self.snap)*4, 0)
					print_at(0,term.height-4, term.clear_eol)
					self.mapToEdit["notes"][self.selectedNote]["beatpos"] = [self.localConduc.currentBeat//4, self.localConduc.currentBeat%4]
				if val == "i":
					self.localConduc.currentBeat += (1/self.snap)*4
					print_at(0,term.height-4, term.clear_eol)
					self.mapToEdit["notes"][self.selectedNote]["beatpos"] = [self.localConduc.currentBeat//4, self.localConduc.currentBeat%4]
				
				if self.mapToEdit["notes"][self.selectedNote]["type"] == "hit_object":
					screenPos = self.mapToEdit["notes"][self.selectedNote]["screenpos"]
					calculatedPos = Game.calculatePosition(screenPos, 5, 3, term.width-10, term.height-7)
					if val == "h":
						print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
						self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] = max(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] - 0.05, 2), 0)
					if val == "j":
						print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
						self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] = max(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] - 0.05, 2), 0)
					if val == "k":
						print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
						self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] = min(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] + 0.05, 2), 1)
					if val == "l":
						print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
						self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] = min(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] + 0.05, 2), 1)

		else:
			if val.name == "KEY_ESCAPE":
				self.commandMode = False
				self.commandString = ""
				print_at(0,term.height-2, term.clear_eol+term.normal)
			elif val.name == "KEY_ENTER":
				isValid, errorStr = self.run_command(self.commandString)
				if isValid:
					self.commandMode = False
					self.commandString = ""
					if errorStr != "":
						print_at(0,term.height-2, term.on_green+errorStr+term.clear_eol+term.normal)
				else:
					self.commandMode = False
					self.commandString = ""
					print_at(0,term.height-2, term.on_red+errorStr+term.clear_eol+term.normal)
			elif val.name == "KEY_BACKSPACE":
				if self.commandString != "":
					self.commandString = self.commandString[:len(self.commandString)-(self.commandSelectPos+1)] + self.commandString[len(self.commandString)-self.commandSelectPos:]
				else:
					self.commandMode = False
					print_at(0,term.height-2, term.clear_eol+term.normal)
			elif val.name == "KEY_LEFT":
				self.commandSelectPos += 1
				if self.commandSelectPos > len(self.commandString):
					self.commandSelectPos = len(self.commandString)
			elif val.name == "KEY_RIGHT":
				self.commandSelectPos -= 1
				if self.commandSelectPos < 0:
					self.commandSelectPos = 0
			elif val.name == "KEY_TAB":
				self.commandAutoPropositions = self.autocomplete(self.commandString)
				if self.commandAutoPropositions != []:
					self.commandAutoMode = True

			else:
				if val.name == None:
					self.commandString += str(val)
			

	def loop(self):
		with term.fullscreen(), term.hidden_cursor(), term.raw():
			print(term.clear)
			while not self.turnOff:
				if self.playtest:
					self.deltatime = self.localConduc.update()
				self.draw()
				
				self.handle_input()

	def __init__(self) -> None:
		pass


if __name__ == "__main__":
	editor = Editor()
	# loadedMenus["Editor"] = editor
	editor.layout = Game.setupKeys(None, "qwerty")
	editor.loop()