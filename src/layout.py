from blessed import Terminal
import json, os
# print(__name__)
if __name__ != "src.layout":
	from termutil import print_at, print_lines_at
	from translate import Locale
else:
	from src.termutil import print_at, print_lines_at
	from src.translate import Locale

term = Terminal()

class LayoutCreator:
	turnOff = False
	selectedKey = 0
	changingKey = False
	layoutName = "custom"
	layout = ["╳" for _ in range(30)]

	#Locale
	loc:Locale = Locale("en")

	def save(self):
		if "╳" in self.layout:
			return False, "Empty keys!"
		if len(list(set(self.layout))) != len(self.layout):
			return False, "Duplicate keys!"
		if not os.path.exists("./layout/" + self.layoutName):
			f = open("./layout/" + self.layoutName, "x")
		else:
			f = open("./layout/" + self.layoutName, "w")
		text = "\n".join(["".join(self.layout[i*10:(i+1)*10]) for i in range(3)])
		f.write(text)
		f.close()
		return True, ""

	def draw(self):
		# this mess is to generate a grid
		text = f"┌───{'┬───'*9}┐\n" + "".join(
			["".join([f"│ {key} " for key in self.layout][10*i:10*(i+1)]) + f"│\n├───{'┼───'*9}┤\n" for i in range(2)]
		) + "".join(
			[f"│ {key} " for key in self.layout][20:30]
		) + f"│\n└───{'┴───'*9}┘\n"
		print_lines_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2), int((term.height-len(text.split("\n")))*0.5), text)
		print_at(int(term.width*0.5 - len(f"┌───{'┬───'*9}┐")/2) + 1 + (self.selectedKey%10)*4, int((term.height-len(text.split("\n")))*0.5) + 1 + (self.selectedKey//10)*2, term.reverse + f" {self.layout[self.selectedKey]} " + term.normal)
		if self.changingKey:
			text_changeKey = self.loc("")
			print_at(int((term.width-len(text_changeKey))*0.5), int(term.height*0.5) + 6, text_changeKey)
		else:
			print_at(0, int(term.height*0.5) + 6, term.clear_eol)

	def handle_input(self):
		val = ''
		val = term.inkey(timeout=1/120, esc_delay=0)

		if val:
			if val.name == "KEY_ESCAPE":
				if not self.changingKey:
					self.turnOff = True
				else:
					self.changingKey = False
			if val.name == "KEY_LEFT":
				self.selectedKey -= 1
			if val.name == "KEY_RIGHT":
				self.selectedKey += 1
			if val.name == "KEY_UP":
				self.selectedKey -= 10
			if val.name == "KEY_DOWN":
				self.selectedKey += 10
			self.selectedKey %= 30
			if val.name == "KEY_ENTER":
				self.changingKey = True
			if val.name == None and self.changingKey:
				if str(val) in self.layout:
					self.layout[self.layout.index(str(val))] = "╳"
				self.layout[self.selectedKey] = str(val)
				self.selectedKey += 1
				if self.selectedKey >= 30:
					self.changingKey = False
				self.selectedKey %= 30
					
	def loop(self, layout = None):
		if layout is not None:
			self.layout = layout
		with term.fullscreen(), term.cbreak(), term.hidden_cursor():
			print(term.clear)
			while not self.turnOff:
				self.draw()

				self.handle_input()
	
		result, code = self.save()
		if __name__ == "__main__":
			if not result:
				print(term.on_yellow + "Could not save: " + code + term.normal)
		else:
			return result, code

	def __init__(self):
		pass
if __name__ == "__main__":
	layout = LayoutCreator()
	layout.loop()