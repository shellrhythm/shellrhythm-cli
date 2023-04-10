import os
if __name__ == "__main__":
	from termutil import *
	from textbox import textbox_logic
else:
	try:
		from src.termutil import *
		from src.textbox import textbox_logic
	except ImportError:
		from termutil import *
		from textbox import textbox_logic
import re

class FileBrowser:
	curPath = "/"
	turnOff = False
	fileExtFilter = r"(?:.py$)"
	curFilesInFolder = []
	curSubFolders = []
	selectedItem = 0
	selectFolderMode = False
	caption = "TODO: Come up with a better placeholder"
	offset = 0

	newFolderMode = False
	newFolderName = ""
	newFolderCaret = 0

	output = "?"

	def load_folder(self, path):
		if os.path.exists(path):
			self.curFilesInFolder = [file.name for file in os.scandir(path) if file.is_file() and re.search(self.fileExtFilter, file.name)]
			self.curSubFolders = [fold.name for fold in os.scandir(path) if fold.is_dir()]
			self.curSubFolders.sort()
			self.curSubFolders.insert(0, "..")
			self.curPath = os.path.abspath(path)
			self.curFilesInFolder.sort()
		else:
			return FileNotFoundError()

	def draw(self):
		print_at(0,0,str(self.selectedItem))

		print_box(10,3,term.width-20, term.height-6, caption=self.caption)
		print_cropped(11,4,term.width-22,self.curPath,max(len(self.curPath)-(term.width-22), 0), term.normal, False)
		print_at(11,5,"─"*(term.width-22))

		if self.selectFolderMode:
			print_at(11,term.height-2, term.reverse + "[SPACE] Select folder" + term.normal + " " + term.reverse + "[n] New Folder")

		if self.newFolderMode:
			print_at(11,term.height-3, term.reverse + self.newFolderName)
		y = 0
		for i in range(self.offset, len(self.curSubFolders)):
			if y > term.height-11:
				break
			if self.selectedItem == y+self.offset:
				print_at(12,6 + y, term.reverse + "\uea83 " + self.curSubFolders[i] + "/" + term.normal)
			else:
				print_at(12,6 + y, "\uea83 " + self.curSubFolders[i] + "/")
			y+=1
		for i in range(max(self.offset - len(self.curSubFolders), 0), len(self.curFilesInFolder)):
			if y > term.height-11:
				break
			if self.selectedItem == y+self.offset:
				print_at(14,6 + y, term.reverse + self.curFilesInFolder[i] + term.normal)
			else:
				print_at(14,6 + y, self.curFilesInFolder[i])
			y+=1

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/60, esc_delay=0)

		if not self.newFolderMode:
			if val.name == "KEY_UP":
				self.selectedItem -= 1
				self.selectedItem %= len(self.curFilesInFolder) + len(self.curSubFolders)
				if self.selectedItem < self.offset + 1:
					self.offset -= 1
				# print(term.clear)
			if val.name == "KEY_DOWN":
				self.selectedItem += 1
				self.selectedItem %= len(self.curFilesInFolder) + len(self.curSubFolders)

				if self.selectedItem > self.offset + term.height-12:
					self.offset += 1
				# print(term.clear)
			if val == "J":
				self.offset += 1
				# print(term.clear)
			if val == "K":
				self.offset -= 1
				self.offset = max(self.offset, 0)
				# print(term.clear)
			if val == "n":
				self.newFolderMode = True
			if val.name == "KEY_ENTER":
				if self.selectedItem >= len(self.curSubFolders):
					self.output = self.curPath + "/" + self.curFilesInFolder[self.selectedItem - len(self.curSubFolders)]
					self.turnOff = True
					# print(term.clear)
				else:
					self.load_folder(self.curPath + "/" + self.curSubFolders[self.selectedItem])
					# print(term.clear)
					self.selectedItem = 0
					self.offset = 0
					pass
			if val == " ":
				if self.selectFolderMode:
					self.output = self.curPath + "/" + self.curSubFolders[self.selectedItem]
					self.turnOff = True
					# print(term.clear)


			if val.name == "KEY_ESCAPE":
				self.turnOff = True
				# print(term.clear)
		else:
			if val.name == "KEY_ESCAPE":
				self.newFolderMode = False
				# print(term.clear)
			elif val.name == "KEY_ENTER":
				os.mkdir(self.curPath + "/" + self.newFolderName)
				self.load_folder(self.curPath)
				self.selectedItem = 0
				self.offset = 0
				# print(term.clear)
			else:
				self.newFolderName, self.newFolderCaret = textbox_logic(self.newFolderName, self.newFolderCaret, val)


	def loop(self):
		# print(term.clear)
		while not self.turnOff:
			self.draw()
			refresh()
			self.handle_input()

		self.selectFolderMode = False
		return self.output

	def __init__(self) -> None:
		pass

if __name__ == "__main__":
	fileContext = FileBrowser()
	fileContext.load_folder(os.getcwd())
	fileContext.caption = "Hey, this is a test file browser!"

	with term.fullscreen(), term.cbreak(), term.hidden_cursor():
		fileContext.loop()
	print(fileContext.output)