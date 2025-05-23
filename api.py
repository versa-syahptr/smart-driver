import requests
import os

URL = "https://sdp-bot-8c27d3846f66.herokuapp.com/"
BOT_URL = "https://t.me/SmartDriverNotifierBot"
ID = None

def get_id() -> str:
    global ID
    if not os.path.exists("id.txt"):
        print("id.txt not found, creating new id")
        r = requests.get(URL + "new")
        with open("id.txt", "w") as f:
            ID = r.text
            f.write(ID)
    elif ID is None:
        with open("id.txt", "r") as f:
            ID = f.read()
    return ID


def get_detail() -> dict:
    print("getting detail for", get_id())
    return requests.get(URL + "get", params={"id": get_id()}).json()

def broadcast(lat: float, lon: float) -> dict:
    try:
        print("broadcasting accident location")
        r = requests.post(URL + "broadcast", 
                         params={"id": get_id()}, 
                         data={"lat": lat, "lon": lon})
        return r.json()
    # retry when error
    except Exception as e:
        print("Error while trying to broadcast", e)
        print("retrying...")
        return broadcast(lat, lon)

