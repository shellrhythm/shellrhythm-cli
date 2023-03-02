from blessed import Terminal
import os
import copy
import json
from pybass3 import Song
from zipfile import ZipFile
import time
import shutil
# from index import *
if __name__ == "src.editor":
	from src.game import *
	from src.conductor import *
	from src.translate import Locale
	from src.textbox import textbox_logic
	from src.filebrowser import FileBrowser
	from src.calibration import Calibration
else:
	from game import *
	from conductor import *
	from translate import Locale
	from textbox import textbox_logic
	from filebrowser import FileBrowser
	from calibration import Calibration

term = Terminal()

# WARNING TO WHOEVER WANTS TO MOD THIS FILE:
# good luck

class Editor:
	turnOff = False

	#Basics
	mapToEdit = {}
	localConduc = Conductor()
	playtest = False
	beatSound = Song("assets/clap.wav")
	dontDrawList = []
	dontBeat = [] #Notes that have already got their beatsound played
	
	#Saving
	needsSaving = False
	fileLocation = ""

	#Notes selected
	selectedNote = 0
	endNote = -1
	
	#Command mode
	commandMode = False
	commandString = ""
	commandSelectPos = 0
	commandAutoMode = False
	commandAutoPropositions = []
	commandFooterMessage = ""
	commandFooterEnabled = False

	#Editor settings
	snap = 4
	selectedSnap = 2
	snapPossible = [1, 2, 4, 8, 16, 3, 6, 12]
	layout = []

	#Key panel
	keyPanelEnabled = False
	keyPanelKey = -1
	keyPanelSelected = -1 #Note: use -1 when creating a new note
	keyPanelJustDisabled = False

	pauseMenu = [
		"resume",
		"playtest",
		"song",
		"addimage",
		"metadata",
		"save",
		"export",
		"quit",
	]
	pauseMenuEnabled = False
	pauseMenuSelected = 0
	
	#Locale
	loc:Locale = Locale("en")

	#Note settings
	noteMenu = {
		"hit_object":[
			{"name": "key", "keybind": 20},
			{"name": "color", "keybind": 21},
			{"name": "delete", "keybind": 22},
		],
		"text":[
			{"name": "text", "keybind": 20},
			{"name": "color", "keybind": 21},
			{"name": "anchor", "keybind": 22},
			{"name": "delete", "keybind": 23},
		]
	}
	noteMenuEnabled = False
	noteMenuJustDisabled = False
	noteMenuSelected = 0

	#Metadata settings
	metadataParts = ["title", "artist", "author", "description"]
	metadataMenuEnabled = False
	metadataMenuSelection = 0
	metadataTyping = False
	metadataString = ""
	metadataTypingCursor = 0

	#File Browser
	fileBrwsr:FileBrowser = FileBrowser()

	#Calibration
	calib:Calibration = Calibration("CalibrationSong")

	options = {
		"nerdFont": True
	}

	def autocomplete(self, command = ""):
		output = []
		if command == "":
			# return list of commands uhhh
			return output
		
		commandSplit = command.split(" ")


		#TODO where do i even begin

		return output
	
	def export(self):
		file_paths = [] #this is where the paths go
	
		# crawling through directory and subdirectories
		for root, directories, files in os.walk("./charts/" + self.mapToEdit["foldername"]):
			for filename in files:
				#gimme da full path plz :3
				filepath = filename
				file_paths.append(filepath)
		
		# actual exporting
		with ZipFile("./charts/" + self.mapToEdit["foldername"] + '.zip','w') as zip:
			# add in the files
			for file in file_paths:
				zip.write("./charts/" + self.mapToEdit["foldername"] + "/" + file, file)
		pass

	def setupMap(self):
		self.mapToEdit = {
			"formatVersion": 1,
			"sound": None,
			"foldername": "",
			"icon": {
				"img": "",
				"txt": ""
			},
			"bpm": 120,
			"offset": 0,
			"metadata": {
				"title": "",
				"artist": "",
				"author": "",
				"description": ""
			},
			"approachRate": 1,
			"difficulty": 0,
			"notes": []
		}
		self.endNote = -1
	
	def create_note(self, atPos, key):
		print(term.clear)
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
			self.mapToEdit["notes"] = sorted(self.mapToEdit["notes"], key=lambda d: d['beatpos'][0]*4+d['beatpos'][1])
			if "end" in [note["type"] for note in self.mapToEdit["notes"]]:
				self.endNote = [note["type"] for note in self.mapToEdit["notes"]].index("end")
			
	def create_text(self, atPos = 0, lasts = 1, text = "", anchor = CENTER, align = ALIGN_CENTER):
		print(term.clear)
		if "notes" in self.mapToEdit:
			newNote = {
				"type": "text",
				"beatpos": [
					int(atPos//4),
					round(atPos%4, 5)
				],
				"length": lasts,
				"text": text,
				"anchor": anchor,
				"align": align,
				"offset": [0,0]
			}
			self.mapToEdit["notes"].append(newNote)
			self.mapToEdit["notes"] = sorted(self.mapToEdit["notes"], key=lambda d: d['beatpos'][0]*4+d['beatpos'][1])
			if "end" in [note["type"] for note in self.mapToEdit["notes"]]:
				self.endNote = [note["type"] for note in self.mapToEdit["notes"]].index("end")


	def set_end_note(self, atPos):
		if self.endNote == -1:
			if "end" in [note["type"] for note in self.mapToEdit["notes"]]:
				self.endNote = [note["type"] for note in self.mapToEdit["notes"]].index("end")
			else:
				newNote = {
					"type": "end",
					"beatpos": [
						int(atPos//4),
						round(atPos%4, 5)
					]
				}
				self.mapToEdit["notes"].append(newNote)
				self.endNote = len(self.mapToEdit["notes"])-1
		else:
			self.mapToEdit["notes"][self.endNote]["beatpos"] = [int(atPos//4), round(atPos%4, 5)]

	def draw_pauseMenu(self):
		width = max(len(self.loc("editor.pause." + option)) for option in self.pauseMenu)+4
		print_box((term.width-width)//2 - 1, (term.height//2) - len(self.pauseMenu) - 1, width+2, len(self.pauseMenu) * 2 + 1)
		for i in range(len(self.pauseMenu)):
			if i == self.pauseMenuSelected:
				print_at((term.width-width)//2, (term.height//2) - len(self.pauseMenu) + i*2, term.reverse + term.center(self.loc("editor.pause." + self.pauseMenu[i]), width) + term.normal)
			else:
				print_at((term.width-width)//2, (term.height//2) - len(self.pauseMenu) + i*2, term.center(self.loc("editor.pause." + self.pauseMenu[i]), width))
			if i != len(self.pauseMenu)-1:
				print_at((term.width-width)//2, (term.height//2) - len(self.pauseMenu) + i*2 + 1, " "*width)

	def run_pauseMenu(self, option):
		#what made you think this was a good idea
		#- #Guigui, to himself, 16/2/2023 (DD/MM/YYYY the obviously better formatting)
		if option == 0:
			#resume
			self.pauseMenuEnabled = False
			print(term.clear)
		if option == 1:
			#playtest
			pass
			print_at(0,term.height-2, term.on_red+"Too lazy to implement, please try again later."+term.clear_eol+term.normal)
			#TODO uhhhhhh
		if option == 2:
			self.run_command("song") #uh yeah
		if option == 3:
			#change image
			self.fileBrwsr.fileExtFilter = "(?:\.png$)|(?:\.jpeg$)|(?:\.webp$)|(?:\.jpg$)|(?:\.apng$)|(?:\.gif$)"
			self.fileBrwsr.load_folder(os.getcwd())
			self.fileBrwsr.caption = "Select an image"
			self.fileBrwsr.turnOff = False
			imageFileLocation = self.fileBrwsr.loop()
			try:
				shutil.copyfile(imageFileLocation, f"./charts/{self.mapToEdit['foldername']}/{imageFileLocation.split('/')[-1]}")
			except shutil.SameFileError:
				pass
			self.mapToEdit["icon"]["img"] = imageFileLocation.split("/")[-1]
		if option == 4:
			#metadata
			self.metadataMenuEnabled = True
			self.pauseMenuEnabled = False
			print(term.clear)
		if option == 5:
			#save
			self.run_command("w") #huge W
			self.pauseMenuEnabled = False
		if option == 6:
			#export
			self.run_command("w") #huge W
			self.pauseMenuEnabled = False
			self.export()
			print(term.clear)
			print_at(0,term.height-2, term.on_green+f"Exported successfully to ./charts/{self.mapToEdit['foldername']}.zip" +term.clear_eol+term.normal)
			pass
		if option == 7:
			#quit
			self.run_command("q")
			self.pauseMenuEnabled = False


	def draw_noteSettings(self, note, selectedOption):
		if note["type"] == "hit_object":
			screenPos = note["screenpos"]
			calculatedPos = Game.trueCalcPos(None, screenPos[0], screenPos[1], "setSize")
			width = max(len(self.loc("editor.noteSettings.hit_object." + option["name"])) for option in self.noteMenu["hit_object"])+4
			height = len(self.noteMenu["hit_object"])+2
			anchorPoint = [calculatedPos[0]+2, min(calculatedPos[1]-2, term.height-(2+height))]
			if anchorPoint[0] + width >=term.width:
				anchorPoint[0] = calculatedPos[0]-(2+width)
			print_box(anchorPoint[0], anchorPoint[1], width, height)
			for i in range(len(self.noteMenu["hit_object"])):
				text = self.loc("editor.noteSettings.hit_object." + self.noteMenu["hit_object"][i]["name"])
				if i == selectedOption:
					print_at(anchorPoint[0], 	anchorPoint[1]+1+i, ">"+term.reverse	+ text + (" "*(width-(len(text)+3))) + self.layout[self.noteMenu["hit_object"][i]["keybind"]].upper() + term.normal	)
				else:
					print_at(anchorPoint[0]+1, 	anchorPoint[1]+1+i,		term.normal 	+ text + (" "*(width-(len(text)+3))) + self.layout[self.noteMenu["hit_object"][i]["keybind"]].upper() + term.normal	)
		elif note["type"] == "text":
			width = max(len(self.loc("editor.noteSettings.text." + option["name"])) for option in self.noteMenu["text"])+4
			height = len(self.noteMenu["text"])+2
			anchorPoint = [0,0]

			print_box(anchorPoint[0], anchorPoint[1], width, height)
			for i in range(len(self.noteMenu["text"])):
				text = self.loc("editor.noteSettings.text." + self.noteMenu["text"][i]["name"])
				if i == selectedOption:
					print_at(anchorPoint[0], 	anchorPoint[1]+1+i, ">"+term.reverse	+ text + (" "*(width-(len(text)+3))) + self.layout[self.noteMenu["text"][i]["keybind"]].upper() + term.normal	)
				else:
					print_at(anchorPoint[0]+1, 	anchorPoint[1]+1+i,		term.normal 	+ text + (" "*(width-(len(text)+3))) + self.layout[self.noteMenu["text"][i]["keybind"]].upper() + term.normal	)

	def clear_noteSettings(self, note):
		if note["type"] == "hit_object":
			calculatedPos = Game.calculatePosition(note["screenpos"], 5, 3, term.width-10, term.height-11)
			width = max(len(self.loc("editor.keyOptions." + option["name"])) for option in self.noteMenu["hit_object"])+4
			height = len(self.noteMenu["hit_object"])+2
			anchorPoint = [calculatedPos[0]+2, min(calculatedPos[1]-1, term.height-(2+height))]
			print_lines_at(anchorPoint[0], anchorPoint[1], (" "*width+"\n")*height)
		elif note["type"] == "text":
			width = max(len(self.loc("editor.noteSettings.text." + option["name"])) for option in self.noteMenu["text"])+4
			height = len(self.noteMenu["text"])+2
			anchorPoint = [0,0]
			print_lines_at(anchorPoint[0], anchorPoint[1], (" "*width+"\n")*height)


	def run_noteSettings(self, note, noteID, option):
		if note["type"] == "hit_object":
			if option == 0:
				self.keyPanelEnabled = True
				self.keyPanelSelected = noteID
				self.keyPanelKey = note["key"]
				return True
			elif option == 1:
				#TODO better color picker
				note["color"] += 1
				note["color"] %= len(colors)
				return False
			elif option == 2:
				self.mapToEdit["notes"].remove(note)
				return True
		elif note["type"] == "text":
			if option == 0:
				#TODO add the ability to change text
				return True
			elif option == 1:
				#TODO better color picker
				note["color"] += 1
				note["color"] %= len(colors)
				return False
			elif option == 2:
				note["anchor"] += 1
				note["anchor"] %= 9
			elif option == 3:
				self.mapToEdit["notes"].remove(note)
				return True

	def draw_changeKeyPanel(self, toptext = None, curKey = 0):
		width = 40
		height = 7
		if toptext != None:
			print_at(int((term.width-width)*0.5), int((term.height-height)*0.5), "-"*width)
			print_at(int((term.width-width)*0.5), int((term.height+height)*0.5), "-"*width)
			print_column(int((term.width-width)*0.5), int((term.height-height)*0.5)+1, height, "|")
			print_column(int((term.width+width)*0.5), int((term.height-height)*0.5)+1, height, "|")
			print_at(int((term.width-len(toptext))*0.5), int((term.height-height)*0.5)+1, toptext)
			if curKey > 0 and curKey < 30:
				print_at(int(term.width*0.5)-1, int(term.height *0.5), term.reverse + f" {self.layout[curKey]} " + term.normal)
			else:
				print_at(int(term.width*0.5)-1, int(term.height *0.5), term.reverse + f"   " + term.normal)
		else:
			print_lines_at(int((term.width-width)*0.5), int((term.height-height)*0.5), (" "*(width+1)+"\n")*(height+1))

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
		for i in range(-(int(term.width/80)+1),int(term.width/8)-(int(term.width/80))+1):
			char = "'"
			if (4-(i%4))%4 == (int(self.localConduc.currentBeat)%4):
				char = "|"
			slightOffset = int(self.localConduc.currentBeat%1 * 8)
			realDrawAt = int((i*8)+(term.width*0.1)-slightOffset)
			drawAt = max(realDrawAt, 0)
			# maxAfterwards = int(min(7,term.width - (drawAt+1)))
			if i+self.localConduc.currentBeat >= 0 or realDrawAt == drawAt:
				print_at(drawAt, term.height-5, char+("-"*7))
			else:
				print_at(drawAt, term.height-5, "-"*8)
		if self.playtest:
			print_at(0,term.height-4, term.clear_eol)
		print_at(int(term.width*0.1), term.height-4, "@")
		print_at(0,term.height-6, term.normal
		+f"{self.loc('editor.timelineInfos.bpm')}: {self.localConduc.bpm} | "
		+f"{self.loc('editor.timelineInfos.snap')}: 1/{self.snap} | "
		+f"{self.loc('editor.timelineInfos.bar')}: {int(self.localConduc.currentBeat//4)} | "
		+f"{self.loc('editor.timelineInfos.beat')}: {round(self.localConduc.currentBeat%4, 5)} | "
		+term.clear_eol)

		if self.metadataMenuEnabled:
			length = max(len(self.loc('editor.metadata.'+i)) for i in self.metadataParts)
			for i in range(len(self.metadataParts)):
				if i == self.metadataMenuSelection:
					if self.metadataTyping:
						print_at(1,1+i,f"{term.reverse}{self.loc('editor.metadata.'+self.metadataParts[i])}{' '*(length-len(self.loc('editor.metadata.'+self.metadataParts[i]))+1)}: {term.underline}{self.metadataString}{term.normal}")
					else:
						print_at(1,1+i,f"{term.reverse}{self.loc('editor.metadata.'+self.metadataParts[i])}{' '*(length-len(self.loc('editor.metadata.'+self.metadataParts[i]))+1)}: {term.underline}{self.mapToEdit['metadata'][self.metadataParts[i]]}{term.normal}")
				else:
					print_at(1,1+i,f"{self.loc('editor.metadata.'+self.metadataParts[i])}{' '*(length-len(self.loc('editor.metadata.'+self.metadataParts[i]))+1)}: {self.mapToEdit['metadata'][self.metadataParts[i]]}")
			pass
			print_box(0,0,40,len(self.metadataParts) + 2,term.normal,0)
		

		if self.mapToEdit["notes"] != []:
			self.selectedNote %= len(self.mapToEdit["notes"])
			note = self.mapToEdit["notes"][self.selectedNote]
			
			topleft = [int((term.width-defaultSize[0]) * 0.5)-1, int((term.height-defaultSize[1]) * 0.5)-1]
			print_box(topleft[0],topleft[1]-1,defaultSize[0]+2,defaultSize[1]+2,term.normal,1)
			for i in range(len(self.mapToEdit["notes"])):
				j = len(self.mapToEdit["notes"]) - (i+1)
				note = self.mapToEdit["notes"][j]
				if note["type"] == "hit_object":
					screenPos = note["screenpos"]
					characterDisplayed = self.layout[note["key"]]
					calculatedPos = Game.trueCalcPos(None, screenPos[0], screenPos[1], "setSize")
					calculatedPos[1] -= 1
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
							Game.renderNote(None, calculatedPos, colors[note["color"]]+term.reverse, characterDisplayed, remBeats+1)
						else:
							Game.renderNote(None, calculatedPos, colors[note["color"]], characterDisplayed, remBeats+1)
					elif remBeats < -0.1 and note not in self.dontDrawList:
						print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
						print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
						self.dontDrawList.append(note)
				elif note["type"] == "text":
					remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
					stopAt = remBeats + note["length"]
					
					# TEXT - TIMELINE
					if remBeats*8+(term.width*0.1) >= 0:
						if self.options["nerdFont"]:
							char = "\U000f150f"
						else:
							char = "#"
						if self.selectedNote == j:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.reverse}{term.turquoise}{term.bold}{char} {term.normal}")
							print_at(int(stopAt*8+(term.width*0.1)), term.height-4, f"{term.turquoise}|{term.normal}")
						else:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.normal}{term.turquoise}{term.bold}{char}{term.normal}")

					# TEXT - ON SCREEN
					constOffset = [0,-1]

					if note in self.dontDrawList and stopAt > 0 and remBeats <= 0:
						self.dontDrawList.remove(note)
					if note not in self.dontDrawList:
						if remBeats <= 0:
							if stopAt > 0:
								Game.renderText(None, note["text"], note["offset"], note["anchor"], note["align"], constOffset)
							else:
								Game.renderText(None, " " * len(note["text"]), note["offset"], note["anchor"], note["align"], constOffset)
								self.dontDrawList.append(note)
						else:
							Game.renderText(None, " " * len(note["text"]), note["offset"], note["anchor"], note["align"], constOffset)
							self.dontDrawList.append(note)
				else:
					# END - TIMELINE
					remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
					if remBeats*8+(term.width*0.1) >= 0:
						if self.selectedNote == j:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.reverse}{term.bold_grey}▚{term.normal}")
						else:
							print_at(int(remBeats*8+(term.width*0.1)), term.height-4, f"{term.normal}{term.bold_grey}▚{term.normal}")
			#Current note info
			selectedNote = self.mapToEdit['notes'][self.selectedNote]
			if selectedNote["type"] == "hit_object":
				print_at(0, term.height-7, term.normal
				+f"{self.loc('editor.timelineInfos.curNote')}: {self.selectedNote} | "
				+f"{self.loc('editor.timelineInfos.color')}: {colors[selectedNote['color']]}[{selectedNote['color']}]{term.normal} | "
				+f"{self.loc('editor.timelineInfos.screenpos')}: {selectedNote['screenpos']} | "
				+f"{self.loc('editor.timelineInfos.beatpos')}: {selectedNote['beatpos']}"
				+term.clear_eol)
			else:
				print_at(0, term.height-7, term.normal+f"{'editor.timelineInfos.curNote'}: {self.selectedNote} | {self.loc('editor.timelineInfos.endpos')}: {selectedNote['beatpos']}{term.clear_eol}")
			
			if self.noteMenuEnabled:
				self.draw_noteSettings(note, self.noteMenuSelected)
			elif self.noteMenuJustDisabled:
				self.clear_noteSettings(note)
				self.noteMenuJustDisabled = False
		else:
			if not self.keyPanelEnabled:
				text_nomaploaded = self.loc("editor.emptyChart")
				print_at(int((term.width - len(text_nomaploaded))*0.5),int(term.height*0.4), term.normal+text_nomaploaded)

		if self.keyPanelEnabled:
			if self.keyPanelSelected == -1:
				text_key = self.loc("editor.newKey.creating")
			else:
				text_key = self.loc("editor.newKey.editing")
			self.draw_changeKeyPanel(text_key,self.keyPanelKey)
		elif self.keyPanelJustDisabled:
			self.draw_changeKeyPanel()
			self.keyPanelJustDisabled = False

		if self.pauseMenuEnabled:
			self.draw_pauseMenu()

		if self.commandMode:
			print_at(0,term.height-2, term.normal+":"+self.commandString+term.clear_eol)
			chrAtCursor = ""
			if len(self.commandString) != 0:
				if self.commandSelectPos != 0:
					chrAtCursor = self.commandString[len(self.commandString)-(self.commandSelectPos)]
				else:
					chrAtCursor = " "
				print_at(len(self.commandString)-self.commandSelectPos + 1, term.height-2, term.underline + chrAtCursor + term.normal)
		elif self.commandFooterEnabled:
			print_at(0,term.height-2, self.commandFooterMessage + term.normal)


	def run_command(self, command = ""):
		commandSplit = command.split(" ")
		print_at(0,term.height-2, term.clear_eol)
		# :q - Quit
		if commandSplit[0] == "q!" or (commandSplit[0] == "q" and not self.needsSaving):
			self.turnOff = True
			return True, ""

		# :w - Write (Save) | 1 optional argument (where to save it)
		elif commandSplit[0] == "w":
			output = json.dumps(self.mapToEdit)
			if len(commandSplit) > 1:
				self.mapToEdit["foldername"] = commandSplit[1]
			if len(commandSplit) == 2:
				self.fileLocation = f"./charts/{commandSplit[1]}/data.json"
			elif len(commandSplit) == 3:
				self.fileLocation = f"./charts/{commandSplit[1]}/{commandSplit[2]}.json"
			elif self.fileLocation == "" and len(commandSplit) == 1:
				self.fileBrwsr.fileExtFilter = "(?:\/$)"
				self.fileBrwsr.load_folder(os.getcwd())
				self.fileBrwsr.selectFolderMode = True
				self.fileBrwsr.caption = "Select a folder"
				self.fileBrwsr.turnOff = False
				getFolderLocation = self.fileBrwsr.loop()

				if getFolderLocation != "?":
					self.fileLocation = getFolderLocation + "/data.json"
					self.mapToEdit["foldername"] = getFolderLocation.split("/")[-1]
					pass
				# return False, getFolderLocation
				# return False, self.loc("editor.commandResults.common.notEnoughArgs")
			if os.path.exists(self.fileLocation):
				f = open(self.fileLocation, "w")
			else:
				if not os.path.exists("./charts/"):
					os.mkdir("./charts")
				if len(commandSplit) > 1:
					if not os.path.exists(f"./charts/{commandSplit[1]}"):
						os.mkdir(f"./charts/{commandSplit[1]}")
				f = open(self.fileLocation, "x")
			f.write(output)
			f.close()
			return True, self.loc("editor.commandResults.save")
		
		# :wq - Save and Quit | 1 optional argument (where to save it)
		elif commandSplit[0] == "wq!" or (commandSplit[0] == "wq" and not self.needsSaving):
			output = json.dumps(self.mapToEdit)
			if len(commandSplit) == 2:
				self.fileLocation = f"./charts/{commandSplit[1]}/data.json"
			elif len(commandSplit) == 3:
				self.fileLocation = f"./charts/{commandSplit[1]}/{commandSplit[2]}.json"
			if os.path.exists(self.fileLocation):
				f = open(self.fileLocation, "w")
			else:
				f = open(self.fileLocation, "x")
			f.write(output)
			f.close()
			self.turnOff = True
			return True, self.loc("editor.commandResults.save")

		# :o - Open 
		elif commandSplit[0] == "o":
			if len(commandSplit) == 2:
				fileExists = self.load_chart(commandSplit[1])
				if not fileExists:
					return fileExists, self.loc("editor.commandResults.open.notFound")
				else:
					return fileExists, self.loc("editor.commandResults.open.success")
			elif len(commandSplit) == 3:
				self.load_chart(commandSplit[1], commandSplit[2])
			else:
				if len(commandSplit) < 2:
					return False, self.loc("editor.commandResults.common.notEnoughArgs")
				else:
					return False, self.loc("editor.commandResults.common.tooManyArgs")
		
		# :p - Place
		elif commandSplit[0] == "p":
			if len(commandSplit) > 1:
				if commandSplit[1].isdigit():
					self.create_note(self.localConduc.currentBeat, int(commandSplit[1]))
					return True, self.loc("editor.commandResults.note.success")
			else:
				self.keyPanelEnabled = True
				self.keyPanelSelected = -1
				self.keyPanelKey = 0
				return True, ""

		# :song - Change song
		elif commandSplit[0] == "song":
			if self.fileLocation == "":
				return False, "You need to save this file first! To do that, type :w <some_chart_name>"
			if len(commandSplit) > 1:
				if os.path.exists(commandSplit[1]) and commandSplit[1].split(".")[-1] in ["ogg", "mp3", "wav"]:
					soundFileLocation = commandSplit[1]
					self.mapToEdit["sound"] = soundFileLocation.split('/')[-1]
					shutil.copyfile(soundFileLocation, f"./charts/{self.mapToEdit['foldername']}/{soundFileLocation.split('/')[-1]}")
					self.localConduc.loadsong(self.mapToEdit)
			else:
				self.fileBrwsr.fileExtFilter = "(?:\.ogg$)|(?:\.wav$)|(?:\.mp3$)"
				self.fileBrwsr.load_folder(os.getcwd())
				self.fileBrwsr.caption = "Select a song"
				self.fileBrwsr.turnOff = False
				soundFileLocation = self.fileBrwsr.loop()
				if soundFileLocation != "?":
					self.mapToEdit["sound"] = soundFileLocation.split('/')[-1]
					shutil.copyfile(soundFileLocation, f"./charts/{self.mapToEdit['foldername']}/{soundFileLocation.split('/')[-1]}")
					self.localConduc.loadsong(self.mapToEdit)
				else:
					return False, "File selection aborted."

		# :off - Change song offset
		elif commandSplit[0] == "off":
			if len(commandSplit) > 1:
				self.mapToEdit["offset"] = float(commandSplit[1])
			else:
				self.calib.startCalibSong(self.mapToEdit)
				offset = self.calib.init(False)
				self.mapToEdit["offset"] = offset

		# :s - Snap
		elif commandSplit[0] == "s":
			if len(commandSplit) > 1:
				if commandSplit[1].replace('.', '', 1).isdigit():
					self.snap = float(commandSplit[1])

		# :m - Move cursor
		elif commandSplit[0] == "m":
			if len(commandSplit) > 1:
				if commandSplit[1].replace('.', '', 1).isdigit():
					self.localConduc.currentBeat += float(commandSplit[1])
		
		# :mt - Metadata
		elif commandSplit[0] == "mt":
			if len(commandSplit) >= 3:
				valueChanged = ""
				changedTo = ""
				if commandSplit[1] in ["title", "t"]:
					self.mapToEdit["metadata"]["title"] = " ".join(commandSplit[2:])
					valueChanged = "title"
					changedTo = self.mapToEdit["metadata"]["title"]
				if commandSplit[1] in ["artist", "a"]:
					self.mapToEdit["metadata"]["artist"] = " ".join(commandSplit[2:])
					valueChanged = "artist"
					changedTo = self.mapToEdit["metadata"]["artist"]
				if commandSplit[1] in ["author", "charter", "au", "c"]:
					self.mapToEdit["metadata"]["author"] = " ".join(commandSplit[2:])
					valueChanged = "author"
					changedTo = self.mapToEdit["metadata"]["author"]
				if commandSplit[1] in ["description", "desc", "d"]:
					self.mapToEdit["metadata"]["description"] = " ".join(commandSplit[2:])
					valueChanged = "description"
					changedTo = self.mapToEdit["metadata"]["description"]
				return True, self.loc("editor.commandResults.meta.success").format(valueChanged, changedTo)
			elif len(commandSplit) == 2:
				returnMessage = ""
				if commandSplit[1] in ["title", "t"]:
					returnMessage = self.mapToEdit["metadata"]["title"]
				if commandSplit[1] in ["artist", "a"]:
					returnMessage = self.mapToEdit["metadata"]["artist"]
				if commandSplit[1] in ["author", "charter", "au", "c"]:
					returnMessage = self.mapToEdit["metadata"]["author"]
				if commandSplit[1] in ["description", "desc", "d"]:
					returnMessage = self.mapToEdit["metadata"]["description"]
				return True, returnMessage

		# :bpm - Change BPM
		elif commandSplit[0] == "bpm":
			if len(commandSplit) == 2:
				self.mapToEdit["bpm"] = int(commandSplit[1])
				self.localConduc.bpm = int(commandSplit[1])
				return True, ""
			elif len(commandSplit) > 2:
				return False, self.loc("editor.commandResults.common.tooManyArgs")
			return False, self.loc("editor.commandResults.common.notEnoughArgs")

		# :cp - Copy
		elif commandSplit[0] == "cp":
			if len(commandSplit) == 3:
				#XX-YY : Range of notes to copy
				rangeToPick = commandSplit[1].split("-")
				if len(rangeToPick) >= 2:
					pass
				else:
					return False, self.loc("editor.commandResults.common.notEnoughArgs")

				notesToCopy = [copy.deepcopy(self.mapToEdit["notes"][i]) for i in range(int(rangeToPick[0]), int(rangeToPick[1])+1)]
				#BB : How many beats to offset it by?

				for i in range(len(notesToCopy)):
					notesToCopy[i]["beatpos"][1] += float(commandSplit[2])
					notesToCopy[i]["beatpos"][0] += notesToCopy[i]["beatpos"][1]//4
					notesToCopy[i]["beatpos"][1] %= 4
					self.mapToEdit["notes"].append(notesToCopy[i])
				self.mapToEdit["notes"] = sorted(self.mapToEdit["notes"], key=lambda d: d['beatpos'][0]*4+d['beatpos'][1])
				if "end" in [note["type"] for note in self.mapToEdit["notes"]]:
					self.endNote = [note["type"] for note in self.mapToEdit["notes"]].index("end")
				return True, ""
				
			elif len(commandSplit) > 3:
				return False, self.loc("editor.commandResults.common.tooManyArgs")
			return False, self.loc("editor.commandResults.common.notEnoughArgs")

		elif commandSplit[0] == "t":
			if len(commandSplit) > 1:
				self.create_text(atPos=self.localConduc.currentBeat, text=" ".join(commandSplit[1:]))
				return True, self.loc("editor.commandResults.note.success")
			else:
				return False, "[cannot create empty text]"

		else:
			if len(commandSplit[0]) > 128:
				return False, self.loc("editor.commandResults.common.tooLong")
			return False, self.loc("editor.commandResults.common.notFound")

		return True, ""
		

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/120, esc_delay=0)

		if len(self.mapToEdit["notes"]) == 0 and self.noteMenuEnabled:
			self.noteMenuEnabled = False

		if self.playtest:
			for note in self.mapToEdit["notes"]:
				if note["type"] == "hit_object":
					remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
					if note not in self.dontBeat and remBeats <= 0:
						self.beatSound.move2position_seconds(0)
						self.beatSound.play()
						self.dontBeat.append(note)
					if note in self.dontBeat and remBeats > 0:
						self.dontBeat.remove(note)

		if self.noteMenuEnabled:
			if val:
				note = self.mapToEdit["notes"][self.selectedNote]
				goOff = False

				keyBinds = [self.layout[setting["keybind"]] for setting in self.noteMenu[note["type"]]]
				allowedSpKeys = ["KEY_UP", "KEY_DOWN", "KEY_ENTER"]
				if val not in keyBinds and val.name not in allowedSpKeys:
					goOff = True
				else:
					if val.name == "KEY_ENTER":
						goOff = self.run_noteSettings(note, self.selectedNote, self.noteMenuSelected)
					elif val.name == "KEY_UP":
						self.noteMenuSelected -= 1
						self.noteMenuSelected %= len(self.noteMenu[note["type"]])
					elif val.name == "KEY_DOWN":
						self.noteMenuSelected += 1
						self.noteMenuSelected %= len(self.noteMenu[note["type"]])
					if val in keyBinds:
						goOff = self.run_noteSettings(note, self.selectedNote, keyBinds.index(val))
				if goOff == True:
					# self.noteMenuJustDisabled = self.noteMenuEnabled
					self.noteMenuEnabled = not self.noteMenuEnabled
					self.clear_noteSettings(note)

		elif self.metadataMenuEnabled:
			if not self.metadataTyping:
				if val.name == "KEY_ESCAPE":
					print(term.clear)
					self.metadataMenuEnabled = False
				if val.name == "KEY_UP":
					self.metadataMenuSelection -= 1
					self.metadataMenuSelection = max(self.metadataMenuSelection, 0)
				if val.name == "KEY_DOWN":
					self.metadataMenuSelection += 1
					self.metadataMenuSelection = min(self.metadataMenuSelection, len(self.metadataParts) - 1)
				if val.name == "KEY_ENTER":
					self.metadataTyping = True
					self.metadataString = self.mapToEdit["metadata"][self.metadataParts[self.metadataMenuSelection]]
			else:
				if val.name == "KEY_ESCAPE":
					self.metadataTyping = False
					# self.commandString = ""
					print_at(0,term.height-2, term.clear_eol+term.normal)
				elif val.name == "KEY_ENTER":
					self.metadataTyping = False
					self.mapToEdit["metadata"][self.metadataParts[self.metadataMenuSelection]] = self.metadataString
					pass #TODO
				else:
					if self.metadataString == "" and val.name == "KEY_BACKSPACE":
						self.commandMode = False
						# print_at(0,term.height-2, term.clear_eol+term.normal)
					self.metadataString, self.metadataTypingCursor = textbox_logic(self.metadataString, self.metadataTypingCursor, val)
		elif self.pauseMenuEnabled:
			if val.name == "KEY_UP":
				self.pauseMenuSelected -= 1
				self.pauseMenuSelected %= len(self.pauseMenu)
			if val.name == "KEY_DOWN":
				self.pauseMenuSelected += 1
				self.pauseMenuSelected %= len(self.pauseMenu)
			if val.name == "KEY_ENTER":
				self.run_pauseMenu(self.pauseMenuSelected)
				pass

		elif not self.commandMode:
			# debug_val(val)
			if self.keyPanelEnabled:
				if val.name == "KEY_ESCAPE":
					self.keyPanelEnabled = False
					self.keyPanelJustDisabled = True
				elif val.name == "KEY_ENTER":
					if self.keyPanelKey != -1:
						if self.keyPanelSelected == -1:
							self.create_note(self.localConduc.currentBeat, self.keyPanelKey)
						else:
							self.mapToEdit["notes"][self.keyPanelSelected]["key"] = self.keyPanelKey
						self.keyPanelEnabled = False
						self.keyPanelJustDisabled = True
						self.keyPanelSelected = -1
						self.keyPanelKey = -1
				elif val:
					if str(val) in self.layout:
						self.keyPanelKey = self.layout.index(str(val))
			else:
				if val.name != "KEY_ENTER" and val:
					self.commandFooterEnabled = False
				if val == ":":
					self.commandMode = True
					self.commandString = ""
				if val == " ":
					if not self.playtest:
						for note in self.mapToEdit["notes"]:
							remBeats = (note["beatpos"][0] * 4 + note["beatpos"][1]) - self.localConduc.currentBeat
							if remBeats < 0:
								self.dontBeat.append(note)
						self.localConduc.startAt(self.localConduc.currentBeat)
					else:
						self.localConduc.stop()
						self.localConduc.currentBeat = round(self.localConduc.currentBeat/(self.snap/4)) * (self.snap/4)
					self.playtest = not self.playtest
				if val.name == "KEY_ESCAPE":
					self.pauseMenuEnabled = True
				if val.name == "KEY_RIGHT":
					self.localConduc.currentBeat += (1/self.snap)*4
					print_at(0,term.height-4, term.clear_eol)
				if val.name == "KEY_LEFT":
					self.localConduc.currentBeat = max(self.localConduc.currentBeat - (1/self.snap)*4, 0)
					print_at(0,term.height-4, term.clear_eol)
				if val == "z":
					self.keyPanelEnabled = True
					self.keyPanelSelected = -1
					self.keyPanelKey = 0
					print_at(0,int(term.height*0.4), term.clear_eol)
				if val == "Z":
					self.set_end_note(self.localConduc.currentBeat)
				if val == "e":
					#Note settings
					self.noteMenuJustDisabled = self.noteMenuEnabled
					self.noteMenuEnabled = not self.noteMenuEnabled
					pass
				if val == "t":
					self.localConduc.metronome = not self.localConduc.metronome
				if val in ["1", "&"]:
					self.selectedSnap -= 1
					self.selectedSnap %= len(self.snapPossible)
					self.snap = self.snapPossible[self.selectedSnap]
					pass
				if val in ["2", "é"]:
					self.selectedSnap += 1
					self.selectedSnap %= len(self.snapPossible)
					self.snap = self.snapPossible[self.selectedSnap]
					pass

					
				if self.mapToEdit["notes"] != []:
					if val.name == "KEY_DOWN" and not self.noteMenuEnabled:
						print_at(0,term.height-4, term.clear_eol)
						self.selectedNote = min(self.selectedNote + 1, len(self.mapToEdit["notes"])-1)
						self.localConduc.currentBeat = (self.mapToEdit["notes"][self.selectedNote]["beatpos"][0] * 4 + self.mapToEdit["notes"][self.selectedNote]["beatpos"][1])
					if val.name == "KEY_UP" and not self.noteMenuEnabled:
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
						note = self.mapToEdit["notes"][self.selectedNote]
						calculatedPos = Game.calculatePosition(screenPos, 5, 3, term.width-10, term.height-11)
						if val == "h":
							self.clear_noteSettings(note)
							print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
							self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] = max(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] - 0.05, 2), 0)
						if val == "j":
							self.clear_noteSettings(note)
							print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
							self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] = max(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] - 0.05, 2), 0)
						if val == "k":
							self.clear_noteSettings(note)
							print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
							self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] = min(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][1] + 0.05, 2), 1)
						if val == "l":
							self.clear_noteSettings(note)
							print_at(calculatedPos[0]-1, calculatedPos[1]-1, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+0, f"{term.normal}   ")
							print_at(calculatedPos[0]-1, calculatedPos[1]+1, f"{term.normal}   ")
							self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] = min(round(self.mapToEdit["notes"][self.selectedNote]["screenpos"][0] + 0.05, 2), 1)
					if self.mapToEdit["notes"][self.selectedNote]["type"] == "text":
						offset = self.mapToEdit["notes"][self.selectedNote]["offset"]
						if val == "h":
							print(term.clear)
							self.mapToEdit["notes"][self.selectedNote]["offset"][0] -= 1
						if val == "j":
							print(term.clear)
							self.mapToEdit["notes"][self.selectedNote]["offset"][1] += 1
						if val == "k":
							print(term.clear)
							self.mapToEdit["notes"][self.selectedNote]["offset"][1] -= 1
						if val == "l":
							print(term.clear)
							self.mapToEdit["notes"][self.selectedNote]["offset"][0] += 1
						if val == "U":
							print(term.clear)
							self.mapToEdit["notes"][self.selectedNote]["length"] = max(self.mapToEdit["notes"][self.selectedNote]["length"] - (1/self.snap)*4, 0)
						if val == "I":
							print(term.clear)
							self.mapToEdit["notes"][self.selectedNote]["length"] += (1/self.snap)*4

		else:
			if val.name == "KEY_ESCAPE":
				self.commandMode = False
				self.commandString = ""
			elif val.name == "KEY_ENTER":
				splitCommands = self.commandString.split(";;")
				self.commandFooterMessage = ""
				if len(splitCommands) > 1:
					results = []
					errors = []
					for comm in splitCommands:
						isValid, errorStr = self.run_command(comm)
						results.append([isValid, errorStr])
					for i in range(len(results)):
						col = term.on_green
						if results[i][0] == False:
							errors.append(results[i][1])
							col = term.on_red
						self.commandFooterMessage += col + "*"
					self.commandFooterMessage += term.normal + "     "
					if len(errors) != 0:
						self.commandFooterMessage += term.on_red+errors[-1]
					self.commandMode = False
					self.commandString = ""
				
				else:
					isValid, errorStr = self.run_command(self.commandString)
					self.commandMode = False
					self.commandString = ""
					if isValid:
						if errorStr != "":
							self.commandFooterMessage = term.on_green+errorStr
					else:
						self.commandMode = False
						self.commandString = ""
						self.commandFooterMessage = term.on_red+errorStr
				self.commandFooterEnabled = True
			else:
				if self.commandString == "" and val.name == "KEY_BACKSPACE":
					self.commandMode = False
					print_at(0,term.height-2, term.clear_eol+term.normal)
				self.commandString, self.commandSelectPos = textbox_logic(self.commandString, self.commandSelectPos, val, self.autocomplete)


	def loop(self):
		with term.fullscreen(), term.hidden_cursor(), term.raw():
			print(term.clear)
			if self.mapToEdit == {}:
				self.setupMap()
			global screenOffset
			screenOffset = [0, 10]
			while not self.turnOff:
				if self.playtest:
					self.deltatime = self.localConduc.update()
				self.draw()

				refresh()
				
				self.handle_input()

	def __init__(self) -> None:
		pass


if __name__ == "__main__":
	editor = Editor()
	# loadedMenus["Editor"] = editor
	editor.layout = Game.setupKeys(None, "qwerty")
	editor.loop()