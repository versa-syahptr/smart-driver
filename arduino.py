import serial
import json
import api
from typing import Dict
import time

class AccidentDetector:
    def __init__(self, port) -> None:
        self.ser = serial.Serial(port, 9600)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.last_update_time: float = 0

    def get_update(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').rstrip()
            print("raw:", line)
            location: Dict[str, float] = json.loads(line)
            print(location)
            if time.time() - self.last_update_time > 5*60:
                print("Broadcasting accident location")
                api.broadcast(location["latitude"], location["longitude"])
                self.last_update_time = time.time()
            else:
                print("Not broadcasting accident location")


if __name__ == "__main__":
    ad = AccidentDetector("COM4")
    while True:
        ad.get_update()
        time.sleep(1)