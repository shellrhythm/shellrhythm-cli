import json

class Locale:
	name = "N/A" #N/A
	data = {}
	showRawCodes = False

	def __call__(self, key:str) -> str:
		#Let's search for the key!
		pathToTake = key.split(".")
		iAmAtDict = self.data
		returnedValue = ""
		for subkey in pathToTake:
			if subkey in iAmAtDict.keys():
				if type(iAmAtDict[subkey]) is dict:
					iAmAtDict = iAmAtDict[subkey]
				else:
					returnedValue = iAmAtDict[subkey]
			else:
				break
		if returnedValue != "" and self.showRawCodes == False:
			return returnedValue
		else:
			return key

	def __str__(self) -> str:
		return f"Locale: {self('lang')} ({self.name})"

	def __init__(self, lang:str) -> None:
		print(f"Loading locale \"{lang}\"...")
		f = open("./lang/" + lang + ".json")
		self.data = json.loads(f.read())
		self.name = lang
		f.close()

if __name__ == "__main__":
	locale = Locale("fr")
	print(locale("chartSelect.backTitle"))
	print(locale)