import os
import sys
import hashlib
import math
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
                    # previous changeLane Mode = 64
                    self.listOfVehicle.append(Vehicle(vehicle,0))

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
            lane.preparingOpenSpace()
            lane.assureLockedSpace()
            lane.draw_OpenSpace()

    def triggerLockedSpace(self, laneId):
        self.listOfLane[laneId].startLockingSpace(4)

    def triggerLeftChangeLane(self):
        listOfVehicleOnLane = self.listOfLane[0].get_vehicleOnLane()
        targetVehicle = listOfVehicleOnLane[3]
        traci.vehicle.setColor(str(targetVehicle), (0,0,255))
        nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[1].get_currentOpenSpace())
        self.listOfLane[1].add_preparingLockedSpace(nearestOpenSpace)

    def findNearestSpace(self, vehID, ListOpenSpaces):
        listOfDistance = []
        vehiclePosition = traci.vehicle.getLanePosition(vehID)
        shortestDistanceScore = 999999
        shortestSpace = None
        for space in ListOpenSpaces:
            spaceMiddlePosition = space.get_middlePosition()
            distance = math.sqrt((vehiclePosition - spaceMiddlePosition) ** 2)
            if distance < shortestDistanceScore:
                shortestDistanceScore = distance
                shortestSpace = space
        return shortestSpace

    def get_listOfVehicle(self):
        return self.listOfVehicle