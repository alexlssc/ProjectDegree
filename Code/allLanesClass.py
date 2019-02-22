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
        self.allLockedSpace = []
        self.listOfLockedVehicle = []
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
                    self.listOfVehicle.append(Vehicle(vehicle,256))

    def get_listOfLane(self):
        return self.listOfLane

    def get_openSpaceForSpecificLane(self, laneId):
        return self.listOfLane[laneId].get_currentOpenSpace()

    def get_openSpaceIDForSpecificLane(self, laneId):
        return self.listOfLane[laneId].get_curentOpenSpaceId()

    def get_vehicleOnLaneForSpecificLane(self, laneId):
        return self.listOfLane[laneId].get_vehicleOnLane()

    def get_listOfVehicle(self):
        return self.listOfVehicle

    def updateAllLanes(self):
        listArrived = traci.simulation.getArrivedIDList()
        for lane in self.listOfLane:
            lane.updateOpenSpace(listArrived)
            #lane.reduceLargeOpenSpace()
            lane.updateLockedSpace()
            lane.preparingOpenSpace()
            lane.assureLockedSpace()
            allLockedSpace = []
            allLockedSpace = lane.get_lockedSpace()
            if allLockedSpace:
                for space in allLockedSpace:
                    self.allLockedSpace.append(space)
            lane.draw_OpenSpace()

    def triggerLockedSpace(self, laneId):
        self.listOfLane[laneId].startLockingSpace(4)

    def triggerLeftChangeLane(self):
        listOfVehicleOnLane = self.listOfLane[0].get_vehicleOnLane()
        targetVehicle = listOfVehicleOnLane[3]
        self.listOfLockedVehicle.append(targetVehicle)
        traci.vehicle.setColor(str(targetVehicle), (0,0,255))
        traci.gui.trackVehicle('View #0', targetVehicle)
        nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[1].get_currentOpenSpace())
        self.listOfLane[1].add_preparingLockedSpace(nearestOpenSpace)

    def otherAttemptLeftChangeLane(self, vehID):
        traci.vehicle.setSpeed(vehID, -1)
        nearestOpenSpace = self.findNearestSpace(vehID, self.listOfLane[1].get_currentOpenSpace())
        self.listOfLane[1].add_preparingLockedSpace(nearestOpenSpace)

    def findNearestSpace(self, vehID, ListOpenSpaces):
        vehiclePosition = traci.vehicle.getLanePosition(vehID)
        vehicleLength = traci.vehicle.getLength(vehID)
        shortestDistanceScore = 999999
        closestMiddlePointSpace = None
        adjacentSpace = None
        bestNonAdjacentSpace = None
        bestSpace = None
        for space in ListOpenSpaces:
            spaceMiddlePosition = space.get_middlePosition()
            distance = math.sqrt((vehiclePosition - spaceMiddlePosition) ** 2)
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            if backCar is not "start":
                backCarSpeed = traci.vehicle.getSpeed(space.get_backCar())
            else:
                backCarSpeed = 0
            if frontCar is not "end":
                frontCarSpeed = traci.vehicle.getSpeed(space.get_frontCar())
            else:
                frontCarSpeed = 0
            backCarSafeDistance = (backCarSpeed ** 2) / (2 * 0.7 * 9.8)
            frontCarSafeDistance = (frontCarSpeed ** 2) / (2 * 0.7 * 9.8)
            safeDistance = backCarSafeDistance + frontCarSafeDistance
            if distance < shortestDistanceScore:
                print("ID: " + space.get_id() + " / " + str(distance) + " / " + str(space.get_length() - safeDistance) + " / " + str(spaceMiddlePosition) + " / " + str(space.get_length() / 2) + " / " + str(space.get_growth()))
                if (space.get_length() - safeDistance) >= 5:
                    shortestDistanceScore = distance
                    closestMiddlePointSpace = space
                    bestNonAdjacentSpace = space
                else:
                    if space.get_length() - safeDistance > -30 and space.get_growth() == 1:
                        shortestDistanceScore = distance
                        closestMiddlePointSpace = space
                        bestNonAdjacentSpace = space

        return bestNonAdjacentSpace

    def checkIfVehicleCanChangeLane(self):
        #print("size ALS: " + str(len(self.allLockedSpace)) + " / size LLV: " + str(len(self.listOfLockedVehicle)))
        if self.allLockedSpace and self.listOfLockedVehicle:
            carPosition = traci.vehicle.getLanePosition(self.listOfLockedVehicle[0])
            targetOpenSpace = self.allLockedSpace[0]
            targetOpenSpace.changeColor((255,0,0))
            middlePositionOpenSpace = targetOpenSpace.get_middlePosition()
            distance = abs(carPosition - middlePositionOpenSpace)
            print("carPosition:" + str(carPosition) + " / middlePositionOpenSpace: " + str(middlePositionOpenSpace) + " / D:" + str(distance))
            print("Accepted distance: " + str((targetOpenSpace.get_length() / 2) - (targetOpenSpace.get_safeDistance() / 2)) + " / distance:" + str(distance))
            if (targetOpenSpace.get_length() / 2) - (targetOpenSpace.get_safeDistance() / 2) < 0:
                self.unlockSpace(targetOpenSpace)
                self.otherAttemptLeftChangeLane(self.listOfLockedVehicle[0])
            if distance < (targetOpenSpace.get_length() / 2) - (targetOpenSpace.get_safeDistance() / 2):
                # print("Lane change occured at " + traci.simulation.getCurrentTime() )
                # print("Change Lane done")
                traci.vehicle.changeLaneRelative(self.listOfLockedVehicle[0], 1, 2.0)
                traci.vehicle.setSpeed(self.listOfLockedVehicle[0], -1)
                self.listOfLockedVehicle.remove(self.listOfLockedVehicle[0])
                self.unlockSpace(targetOpenSpace)
            else:
                if (carPosition - middlePositionOpenSpace) > 0:
                    traci.vehicle.setSpeed(self.listOfLockedVehicle[0], traci.vehicle.getSpeed(self.listOfLockedVehicle[0]) - 0.2)
                else:
                    traci.vehicle.setSpeed(self.listOfLockedVehicle[0], traci.vehicle.getSpeed(self.listOfLockedVehicle[0]) + 0.2)
                print(str(traci.vehicle.getSpeed(self.listOfLockedVehicle[0])))

    def unlockSpace(self, space):
        self.allLockedSpace.remove(space)
        for lane in self.listOfLane:
            lane.unlockSpace(space)

    def handlesAllManoeuvres(self):
        self.keepTrackOfNewVehicle()
        self.updateAllLanes()
        self.checkIfVehicleCanChangeLane()
