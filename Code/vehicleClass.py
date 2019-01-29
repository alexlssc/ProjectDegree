import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

class Vehicle:
    def __init__(self,id, changeLaneMode):
        self.id = id
        self.listSpeed = []
        self.startTime = None
        self.endTime = None
        traci.vehicle.setLaneChangeMode(id, changeLaneMode)
        self.currentLaneID = traci.vehicle.getLaneID(id)
        self.numberOfLaneChange = 0

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def add_new_speed(self, new_speed):
        self.listSpeed.append(new_speed)

    def get_average_speed(self):
        return sum(self.listSpeed) / len(self.listSpeed)

    def get_listSpeed(self):
        return self.listSpeed

    def set_startTime(self, startTime):
        self.startTime = startTime

    def set_endTime(self, endTime):
        self.endTime = endTime

    def get_timeTravelled(self):
        return self.endTime - self.startTime

    def get_laneChangeMode(self):
        return traci.vehicle.getLaneChangeMode(self.id)

    def get_carLane(self):
        return traci.vehicle.getLaneID(self.id)

    def keepTrackOfLaneChange(self):
        if self.currentLaneID != traci.vehicle.getLaneID(self.id):    # Detect if new lane different than old one
            self.numberOfLaneChange += 1                              # Add one lane change to count
            self.currentLaneID = traci.vehicle.getLaneID(self.id)     # Change new lane to current lane

    def get_changeLaneCount(self):
        return self.numberOfLaneChange

    def get_positionOnLane(self):
        return traci.vehicle.getLanePosition(self.id)

    def get_lengthVehicle(self):
        return traci.vehicle.getLength(self.id)
