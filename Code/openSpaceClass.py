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
        if backCar is not "start":
            self.backCarSpeed = traci.vehicle.getSpeed(backCar)
        else:
            self.backCarSpeed = 0
        if frontCar is not "end":
            self.frontCarSpeed = traci.vehicle.getSpeed(frontCar)
        else:
            self.frontCarSpeed = 0
        if self.backCarSpeed < self.frontCarSpeed:
            self.growth = 1
        elif self.backCarSpeed > self.frontCarSpeed:
            self.growth = -1
        else:
            self.growth = 0
        self.lockedSpace = False
        backCarIDToBytes = bytes(backCar, encoding="utf-8")
        frontCarIDToBytes = bytes(frontCar, encoding="utf-8")
        backCarHash = hashlib.sha256(backCarIDToBytes).hexdigest()
        frontCarHash = hashlib.sha256(frontCarIDToBytes).hexdigest()
        combinedHashToBytes = bytes(backCarHash + frontCarHash, encoding="utf-8")
        self.id = hashlib.sha256(combinedHashToBytes).hexdigest()
        self.safeDistance = None
        self.landingLength = None
        self.growing = False

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

    def get_safeDistance(self):
        if self.safeDistance is not None:
            return self.safeDistance
        else:
            return -1

    # workout safe distance between vehicle for space
    def set_safeDistance(self, backVehicleOneSecSpeed, frontVehicleOneSecSpeed):
        # using braking distance formula to calculate safe distance
        backCarSafeDistance = (backVehicleOneSecSpeed ** 2) / (2 * 0.7 * 9.8)
        frontCarSafeDistance = (backVehicleOneSecSpeed ** 2) / (2 * 0.7 * 9.8)
        self.safeDistance = backCarSafeDistance + frontCarSafeDistance

    def get_landingLength(self):
        self.updateSpeedVehicles() # update front and back car speed
        self.set_safeDistance(self.backCarSpeed, self.frontCarSpeed) # set new safe distance
        return self.length - self.get_safeDistance() # return landing length

    def updateSpeedVehicles(self):
        if self.backCar is not "start":
            self.backCarSpeed = traci.vehicle.getSpeed(self.backCar)
        if self.frontCar is not "end":
            self.frontCarSpeed = traci.vehicle.getSpeed(self.frontCar)

    def update_landingLength(self):
        self.landingLength = self.length - self.safeDistance

    def get_growing(self):
        return self.growing

    def set_growing(self, new_value):
        self.growing = new_value

    def get_growth(self):
        return self.growth

    def changeColor(self, color):
        try:
            traci.poi.setColor(self.id, color)
        except:
            print("Can't draw")

    def update_velocity(self, new_middlePosition):
        self.previousMiddlePosition = self.middlePosition
        self.middlePosition = new_middlePosition
        self.velocity = self.middlePosition - self.previousMiddlePosition # since simulation step is every second

    def updateValues(self, other):
        self.middlePosition = other.middlePosition
        self.length = other.length

    def __eq__(self, other):
        return self.id == other.id
