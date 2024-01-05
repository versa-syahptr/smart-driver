import time
from typing import Dict
from flask import Flask, request, abort, jsonify
# mongo
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from dataclasses import dataclass, field
import os
import telebot
import threading
import configparser
import logging
# import certifi

import dotenv
dotenv.load_dotenv()

app = Flask(__name__)
# mongo
uri = os.environ.get('MONGO_URI', "")
# Create a new client and connect to the server
# ca = certifi.where()
client = MongoClient(uri, serverSelectionTimeoutMS=10000)
db = client.sdp

BOT_TOKEN = os.environ.get('BOT_TOKEN', "")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
telebot.logger.setLevel(logging.DEBUG)

conf_parser = configparser.ConfigParser()
conf_parser.read("config.ini", encoding="utf-8")
templates = conf_parser["messages"]

PRODUCTION_ENV = os.environ.get("PRODUCTION", "0") == "1"


@dataclass
class Device:
    obj_id: str = ""
    details: str = ""
    plate_number: str = ""
    chat_ids: list = field(default_factory=list)

    def empty(self):
        return self.details == "" and self.plate_number == "" and len(self.chat_ids) == 0
    
    @classmethod
    def from_db(cls, db_obj):
        return cls(obj_id=str(db_obj["_id"]),
                   details=db_obj["details"], 
                   plate_number=db_obj["plate_number"], 
                   chat_ids=db_obj["chat_ids"])
    
    def to_dict(self):
        return {"details": self.details, 
                "plate_number": self.plate_number, 
                "chat_ids": self.chat_ids}


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'

@app.route('/ping', methods=['GET', 'HEAD'])
def ping():
    try:
        client.admin.command('ping')
        return 'ok'
    except Exception as e:
        raise
        # return str(e), 500

@app.route('/new', methods=['GET'])
def new_device():
    docu = db.devices.insert_one(Device().to_dict())
    return str(docu.inserted_id)

@app.route('/get', methods=['GET'])
def get_device():
    obj_id = request.args.get('id')
    docu = db.devices.find_one({"_id": ObjectId(obj_id)})
    return jsonify(str(docu))

@app.route('/broadcast', methods=['POST'])
def broadcast():
    device_id = request.args.get('id')
    device = db.devices.find_one({"_id": ObjectId(device_id)})
    if device is None:
        return "Device not found.", 404
    lat = request.form.get('lat') or 0
    lon = request.form.get('lon') or 0
    device = Device.from_db(device)
    message = templates["broadcast"].format(name=device.details, 
                                           plate=device.plate_number,
                                           location=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}")
    for chat_id in device.chat_ids:
        bot.send_message(chat_id, message, parse_mode="Markdown")
        bot.send_location(chat_id, float(lat), float(lon))
    return {"status": "ok", "message": message}


# BOT HANDLER
device_dict : Dict[str, Device]= {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    cmd = message.text.split()
    if len(cmd) < 2:
        bot.reply_to(message, templates["err_invalid_link"])
        return
    device_id = cmd[1]
    try:
        device = db.devices.find_one({"_id": ObjectId(device_id)})
    except Exception:
        bot.reply_to(message, "something went wrong. Please try again.")
        return
    if device is None:
        bot.reply_to(message, "something went wrong. Please try again.")
        return
    device = Device.from_db(device)
    device_dict[message.chat.id] = device
    bot.send_message(message.chat.id, templates["welcome"])
    if device.details == "":
        bot.send_message(message.chat.id, templates["car_details"])
        bot.register_next_step_handler(message, handle_device_details)
    else:
        db_update(message)


def handle_device_details(message):
    device = device_dict[message.chat.id]
    device.details = message.text
    bot.reply_to(message, templates["car_plate"])
    bot.register_next_step_handler(message, handle_device_plate_number)


def handle_device_plate_number(message):
    device = device_dict[message.chat.id]
    device.plate_number = message.text
    # bot.reply_to(message, "Thank you for your information.")
    db_update(message)


def db_update(message):
    device = device_dict[message.chat.id]
    db.devices.update_one({"_id": ObjectId(device.obj_id)}, {"$set": device.to_dict()})
    if message.chat.id not in device.chat_ids:
        db.devices.update_one({"_id": ObjectId(device.obj_id)}, {"$push": {"chat_ids": message.chat.id}})
    bot.send_message(message.chat.id, 
                     templates["user_registered"]
                     .format(name=device.details, plate=device.plate_number))
    bot.send_message(message.chat.id, "You will receive notification if your device detected an accident.")
    device_dict.pop(message.chat.id)


# bot webhook
@app.route('/bot', methods=['POST'])
def bot_handler():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update]) # type: ignore
        return ''
    abort(403)



# set webhook
bot.remove_webhook()
if PRODUCTION_ENV:
    print("set webhook")
    time.sleep(0.1)
    bot.set_webhook(url="https://versa.my.id/sdp/bot")


if __name__ == '__main__':
    # stop_event = threading.Event()
    # threading.Thread(target=bot_polling, args=(stop_event,)).start()
    # app.run(host="0.0.0.0", port=5000, debug=True)
    threading.Thread(target=app.run, args=("localhost", 5000), daemon=True).start()
    print("ok")
    bot.infinity_polling()
    
    