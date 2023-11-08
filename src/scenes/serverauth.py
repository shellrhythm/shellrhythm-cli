import json
import requests
from websockets.sync.client import connect
from src.scenes.base_scene import BaseScene
from src.termutil import term, print_at, log, logging
from src.textbox import Textbox


class ServerAuthentication(BaseScene):
    cdn_host = "http://localhost:6969"
    wss_host = "ws://localhost:8765"
    returned_value = ""
    token = ""
    user_id = -1

    server_box:Textbox = Textbox()
    username_box:Textbox = Textbox()
    password_box:Textbox = Textbox()
    selected = 0

    def on_open(self):
        self.server_box.text = self.wss_host


    def upload_chart(self, chart_zip):
        files = {'upload_file': open(chart_zip,'rb')}
        values = {'TOKEN': self.token}

        r = requests.post(self.cdn_host, files=files, data=values, timeout=1000)
        return json.loads(r.content)

    async def draw(self) -> None:
        self.server_box.x = (term.width - self.username_box.width)//2
        self.username_box.x = (term.width - self.username_box.width)//2
        self.password_box.x = (term.width - self.password_box.width)//2
        self.server_box.y = (term.height - 6)//2
        self.username_box.y = (term.height - 3)//2
        self.password_box.y = (term.height + 3)//2
        print_at(self.server_box.x, self.server_box.y - 1, "Login to Server")
        print_at(self.username_box.x, self.username_box.y - 1, "Username")
        print_at(self.password_box.x, self.password_box.y - 1, "Password")
        print_at(self.password_box.x, (term.height - 3)//2 + 6, term.reverse("Login"))
        print_at((term.width - 44)//2, (term.height - 6)//2 + (self.selected*3),
            ">")
        if self.user_id != -1:
            print_at(0,5, f"Logged in as ID:{self.user_id}")
        await self.username_box.draw()
        await self.password_box.draw()
        await self.server_box.draw()

    async def handle_input(self) -> None:
        val = ''
        val = term.inkey(timeout=1/60, esc_delay=0)

        if self.username_box.focused:
            self.username_box.focused = not await self.username_box.handle_input(val)
        elif self.password_box.focused:
            self.password_box.focused = not await self.password_box.handle_input(val)
        elif self.server_box.focused:
            self.server_box.focused = not await self.server_box.handle_input(val)
        else:
            if val.name == "KEY_ENTER":
                if self.selected == 0:
                    self.server_box.focus()
                if self.selected == 1:
                    self.username_box.focus()
                if self.selected == 2:
                    self.password_box.focus()
                if self.selected == 3:
                    self.login()
            if val.name == "KEY_DOWN":
                self.selected += 1
                self.selected %= 4
            if val.name == "KEY_UP":
                self.selected -= 1
                self.selected %= 4
            # if val == "j":
            #     self.hello()
            if val == "k":
                res = self.upload_chart("charts/@official/tutorial.zip")
                log(res, logging.INFO)

    def login(self):
        self.wss_host = self.server_box.text
        with connect(self.wss_host) as websocket:
            data = {
                "type": "login",
                "username": self.username_box.text,
                "password": self.password_box.text
            }
            websocket.send(json.dumps(data))
            resp = json.loads(websocket.recv())
            # self.returned_value = resp
            if resp["code"] == 200:
                self.token = resp["content"][2]
                self.user_id = resp["content"][1]
                websocket.send(json.dumps({
                    "type": "get_cdn"
                }))
                cdn_resp = json.loads(websocket.recv)
                if cdn_resp["code"]==200:
                    self.cdn_host = "http://" + cdn_resp["content"] #i still have no idea how to https

    def hello(self):
        with connect(self.wss_host) as websocket:
            data = {
                "type": "whats_9_plus_10"
            }
            websocket.send(json.dumps(data))
            self.returned_value = websocket.recv()
