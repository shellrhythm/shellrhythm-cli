import json
import requests
from websockets.sync.client import connect

class ServerManager:
    server_url = ""
    cdn_url = ""

    @staticmethod
    def send_request(req:dict) -> dict:
        with connect(ServerManager.server_url) as websocket:
            websocket.send(json.dumps(req))
            resp = json.loads(websocket.recv())
            return resp
