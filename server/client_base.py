import socket

class ServerFeaturesClientSide:
    sock = None
    server_address = ()
    token = ""

    def connect(_, ip):
        _.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _.server_address = (ip, 10000)
        print(f'connecting to {_.server_address[0]} port {_.server_address[1]}')
        _.sock.connect(_.server_address)
        if _.token == "":
            _.sock.send(b"token")
            print("Waiting for token...")
            _.token = _.sock.recv(4096).decode("UTF-8")
            print(f"Got token! It's {_.token[:5]}-")

    def submitScore(self, results, mapID):
        self.sock.send(bytes(str(mapID) + ":" + str(results), "UTF-8"))

    def updateOnline(self, gameState):
        # "So, what should gameState be?"
        # a miserable little pile of secrets

        #Jokes aside, it'll look something like this:
        if gameState == None:
            gameState = {
                "timeposition": 0, #In seconds!
                "currentCombo": -1,
                "score": -1,
                "accuracy": -1,
            }

    def __init__(self) -> None:
        pass
