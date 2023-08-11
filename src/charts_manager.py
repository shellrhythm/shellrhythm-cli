import os, json
from pybass3 import Song
import hashlib
from src.termutil import term
from src.constants import MAX_SCORE
from src.scenes.results import scoreCalc
from src.scenes.game import Game


class ChartManager:
    chart_data = []
    chart_packs = [
        # {
        #     "name": "Official Songs",
        #     "charter": "#Guigui",
        #     "folder": "@official",
        #     "charts": {
        #         "tutorial": ["tutorial"],
        #         "on_hold": ["on_hold"],
        #     }
        # }
    ]
    scores = {}

    @staticmethod
    def load_scores(chart_name:str, chart_checksum:str, chart:dict) -> list:
        """Returns all scores of a given chart."""
        if not os.path.exists("./scores/"):
            os.mkdir("./scores/")
        score_files = [f.name for f in os.scandir("./scores/") if f.is_file() and f.name.startswith(chart_name.replace("/", "_").replace("\\", "_")+"-")]
        output = []
        for (i,file_name) in enumerate(score_files):
            print(f"Loading scores for map {chart_name}: ({i+1}/{len(score_files)})")
            file = open("./scores/" + file_name, encoding="utf8")
            content = file.read()
            file.close()
            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            file_json = json.loads(content)
            if file_hash != file_name[len(chart_name)+1:]:
                print(term.yellow+"[WARNING] SHA256 check failed for score " + file_hash + term.normal)
                file_json["checkPassed"] = False
            else:
                file_json["checkPassed"] = True
            if isinstance(file_json["version"], str):
                print(term.yellow+f"[WARNING] Score {file_hash} was made on an outdated version! (on game.py pre-version 1)" + term.normal)
                file_json["toRecalculate"] = True
            elif file_json["version"] < Game.version:
                print(term.yellow+f"[WARNING] Score {file_hash} was made on an outdated version! (on game.py version {file_json['version']})" + term.normal)
                file_json["toRecalculate"] = True
            else:
                file_json["toRecalculate"] = False

            if file_json["toRecalculate"]:
                # miss count
                miss_count = 0
                for i in range(len(file_json["judgements"])):
                    if file_json["judgements"][i] != {}:
                        if file_json["judgements"][i]["judgement"] > 4:
                            miss_count += 1
                file_json["score"] = scoreCalc(MAX_SCORE, file_json["judgements"], file_json["accuracy"], 0, chart)

            if file_json["checksum"] != chart_checksum:
                print(term.yellow+"[WARNING] Score " + file_hash + " wasn't made on the current version of this chart!" + term.normal)
                file_json["isOutdated"] = True
            else:
                file_json["isOutdated"] = False
            output.append(file_json)

        output.sort(key=lambda score:-score["score"] + (10**8 if score["isOutdated"] or not score["checkPassed"] else 0))

        return output

    @staticmethod
    def check_chart(chart:dict = None, folder:str = ""):
        """Verifies if the chart is not corrupted, or if it's on an older version, updates it."""
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
        if output["sound"] == "" or output["sound"] is None:
            print(f"{term.yellow}[WARN] {folder} has no song!{term.normal}")

        if output["foldername"] != folder: 
            output["foldername"] = folder

        return output

    @staticmethod
    def load_charts():
        """Populates the variables in ChartManager. Run this to reload the list."""
        ChartManager.chart_data = []
        ChartManager.chart_packs = []
        ChartManager.scores = {}
        if os.path.exists("./charts"):
            charts = [f.path[len("./charts\\"):len(f.path)] \
                    for f in os.scandir("./charts") if f.is_dir()]
            i = 0
            while i < len(charts):
                subfolder = [f.path[len("./charts\\"):len(f.path)] \
                            for f in os.scandir("./charts/" + charts[i]) if f.is_dir()]
                if len(subfolder) > 0:
                    packname = charts[i]
                    packjson = {
                        "name": "TODO",
                        "folder": packname,
                        "charts": []
                    }
                    charts.remove(charts[i])
                    i-=1
                    for sub in subfolder:
                        charts.append(sub)
                        packjson["charts"].append(sub)
                    ChartManager.chart_packs.append(packjson)
                else:
                    print(f"Loading chart \"{charts[i]}\"... ({i+1}/{len(charts)})")
                    chart_file_data = open("./charts/" + charts[i] + "/data.json", encoding="utf8")
                    data = chart_file_data.read()
                    chart_file_data.close()
                    json_content = json.loads(data)
                    check_la_sum = hashlib.sha256(json.dumps(json_content).encode("utf-8")).hexdigest()
                    updated_json_thing = ChartManager.check_chart(json_content, charts[i])
                    if updated_json_thing["sound"] is not None:
                        updated_json_thing["actualSong"] = \
                            Song("./charts/" + charts[i] + "/" + updated_json_thing["sound"])
                    else:
                        updated_json_thing["actualSong"] = Song("./assets/metronome.wav")
                    ChartManager.chart_data.append(updated_json_thing)
                    ChartManager.scores[charts[i]] = ChartManager.load_scores(charts[i],
                        check_la_sum,
                        json_content
                    )
                i+=1
            print("All charts loaded successfully!")
        else:
            print(f"{term.yellow}[WARN] Chart folder inexistant!{term.normal}")
