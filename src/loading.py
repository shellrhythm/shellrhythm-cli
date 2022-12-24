import os, json
from pybass3 import Song

def load_options(options = {}):
	if os.path.exists("./options.json"):
		f = open("./options.json")
		options_string = f.read()
		options = json.loads(options_string)
		f.close()
		print(options)
	else:
		f = open("./options.json", "x")
		f.write(json.dumps(options, indent=4))
		f.close()
	return options, options["lang"]

def load_locales():
	locales = {}
	localeNames = []
	localeFiles = [f.name.split(".", 1)[0] for f in os.scandir("./lang") if f.is_file()]
	for i in range(len(localeFiles)):
		print(f"Loading locale \"{localeFiles[i]}\"... ({i+1}/{len(localeFiles)})")
		f = open("./lang/" + localeFiles[i] + ".json")
		locales[localeFiles[i]] = json.loads(f.read())
		localeNames.append(localeFiles[i])
		f.close()
	return locales, localeNames

def check_chart(chart = {}, folder = ""):
	output = {}
	if "formatVersion" not in chart.keys():
		chart["formatVersion"] = 0

	if "approachRate" not in chart.keys():
		chart["approachRate"] = 1

	if chart["formatVersion"] == 0:
		#Format 0 docs:
		#no foldername
		#no icon, defaults to a TXT 
		#author/charter instead of artist/author
		output = {
			"formatVersion": 0,
			"sound": chart["sound"],
			"foldername": folder,
			"icon": {
				"img": None,
				"txt": "icon.txt"
			},
			"bpm": chart["bpm"],
			"offset": chart["offset"],
			"metadata": {
				"title": chart["metadata"]["title"],
				"artist": chart["metadata"]["author"],
				"author": chart["metadata"]["charter"],
				"description": chart["metadata"]["description"]
			},
			"difficulty": 0,
			"approachRate": 1,
			"notes": chart["notes"]
		}
	else:
		output = chart

	# fixing errors
	if output["sound"] == "" or output["sound"] == None:
		print("[WARN] " + folder + " has no song!")
	
	if output["foldername"] != folder: output["foldername"] = folder

	return output

def load_charts():
	chartData = []
	charts = [f.path[len("./charts\\"):len(f.path)] for f in os.scandir("./charts") if f.is_dir()]
	for i in range(len(charts)):
		print(f"Loading chart \"{charts[i]}\"... ({i+1}/{len(charts)})")
		f = open("./charts/" + charts[i] + "/data.json").read()
		jsonThing = json.loads(f)
		jsonThing = check_chart(jsonThing, charts[i])
		jsonThing["actualSong"] = Song("./charts/" + charts[i] + "/" + jsonThing["sound"])
		chartData.append(jsonThing)

	print("All charts loaded successfully!")
	return chartData