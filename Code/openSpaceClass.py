import os
import sys
import hashlib
import asyncio

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

class OpenSpace:
    def __init__(self,length, middlePosition, backCar, frontCar):
        self.length = length
        self.middlePosition = middlePosition
        self.previousMiddlePosition = None
        self.velocity = None
        self.backCar = backCar
        self.frontCar = frontCar
        self.lockedSpace = False
        backCarIDToBytes = bytes(backCar, encoding="utf-8")
        frontCarIDToBytes = bytes(frontCar, encoding="utf-8")
        backCarHash = hashlib.sha256(backCarIDToBytes).hexdigest()
        frontCarHash = hashlib.sha256(frontCarIDToBytes).hexdigest()
        combinedHashToBytes = bytes(backCarHash + frontCarHash, encoding="utf-8")
        self.id = hashlib.sha256(combinedHashToBytes).hexdigest()



    def get_id(self):
        return self.id

    def get_length(self):
        return self.length

    def set_length(self, new_length):
        self.get_length = new_length

    def get_middlePosition(self):
        return self.middlePosition

    def set_middlePosition(self, new_middlePosition):
        self.middlePosition = new_middlePosition

    def get_locked_state(self):
        return self.lockedSpace

    def set_locked_state(self, new_locked_state):
        self.lockedSpace = new_locked_state

    def get_backCar(self):
        return self.backCar

    def set_backCar(self, new_backCar):
        self.backCar = new_backCar

    def get_frontCar(self):
        return self.frontCar

    def set_frontCar(self, new_frontCar):
        self.frontCar = new_frontCar

    def get_velocity(self):
        if self.velocity:
            return self.velocity
        else:
            return "Unknown"

    def update_velocity(self, new_middlePosition):
        self.previousMiddlePosition = self.middlePosition
        self.middlePosition = new_middlePosition
        self.velocity = self.middlePosition - self.previousMiddlePosition # since simulation step is every second
