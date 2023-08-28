#This file is going to get called every time you need to import a chart through a link
#For example, doing 'shellrhythm --import "zip_url.zip"' will import a zip file if it has valid structure

import sys
import os
import requests
import zipfile
import io
import json

if __name__ == "__main__":
    if len(sys.argv) > 1:
        r = requests.get(sys.argv[1], timeout=60000)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        folder = "something"
        jsonData = {}
        for filename in z.namelist():
            if not os.path.isdir(filename):
                # read the file
                # print(filename)
                # with z.open(filename) as f:
                #     for line in f:
                #         print(line)
                if filename.endswith("data.json"):
                    with z.open(filename) as f:
                        # print(json.load(f))
                        jsonData = json.load(f)
                        folder = jsonData["foldername"]
            else:
                pass
                # print("[DIR] " + filename)
        z.extractall("../charts/" + folder)
        print(f"Successfully imported \"{jsonData['metadata']['title']} - {jsonData['metadata']['artist']}\" by {jsonData['metadata']['author']}.")
