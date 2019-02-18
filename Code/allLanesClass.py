import os
import sys
import hashlib
from vehicleClass import Vehicle
from oneLaneClass import oneLaneObject

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

class AllLanes:

    def __init__(self):
        self.numberOfLane = traci.lane.getIDCount()
        self.listOfVehicle = []
        self.listOfLane = []
        self.listOfYCoordinate = [-14.85, -11.55, -8.25, -4.45, -1.65]
        for i in range(self.numberOfLane):
            laneId = "gneE0_" + str(i)
            self.listOfLane.append(oneLaneObject(laneId, self.listOfYCoordinate[i]))


    def keepTrackOfNewVehicle(self):
        # Keep track of loaded vehicle
        listOfNewVehicleLoaded = traci.simulation.getLoadedIDList()
        if listOfNewVehicleLoaded:
            for vehicle in listOfNewVehicleLoaded:
                if not vehicle in self.listOfVehicle:
                    self.listOfVehicle.append(Vehicle(vehicle,64))

    def get_listOfLane(self):
        return self.listOfLane

    def get_openSpaceForSpecificLane(self, laneId):
        return self.listOfLane[laneId].get_currentOpenSpace()

    def get_openSpaceIDForSpecificLane(self, laneId):
        return self.listOfLane[laneId].get_curentOpenSpaceId()

    def get_vehicleOnLaneForSpecificLane(self, laneId):
        return self.listOfLane[laneId].get_vehicleOnLane()

    def updateAllLanes(self):
        listArrived = traci.simulation.getArrivedIDList()
        for lane in self.listOfLane:
            lane.updateOpenSpace(listArrived)
            lane.draw_OpenSpace()

    def get_listOfVehicle(self):
        return self.listOfVehicle
