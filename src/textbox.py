def textbox_logic(curText, cursorPos, val, autocomplete = None):
	if val.name == "KEY_BACKSPACE":
		if curText != "":
			curText = curText[:len(curText)-(cursorPos+1)] + curText[len(curText)-cursorPos:]
		# else:
		# 	self.commandMode = False
		# 	print_at(0,term.height-2, term.clear_eol+term.normal)
	elif val.name == "KEY_LEFT":
		cursorPos += 1
		if cursorPos > len(curText):
			cursorPos = len(curText)
	elif val.name == "KEY_RIGHT":
		cursorPos -= 1
		if cursorPos < 0:
			cursorPos = 0
	elif val.name == "KEY_TAB" and autocomplete is not None:
		commandAutoPropositions = autocomplete(curText)
		# if commandAutoPropositions != []:
		# 	commandAutoMode = True

	else:
		if val.name == None:
			if cursorPos == 0:
				curText += str(val)
			else:
				curText = curText[:len(curText)-cursorPos] + str(val) + curText[len(curText)-cursorPos:]
	
	return curText, cursorPos
	