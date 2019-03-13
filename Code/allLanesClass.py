import os
import sys
import hashlib
import math
from random import randint
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
        self.listOfYCoordinate = [-14.85, -11.55, -8.25, -4.45, -1.65] # YCoordinate of simulation to draw space's middle position
        self.allLockedSpace = []
        self.allLockedSpaces = {}
        self.listOfLockedVehicle = []
        self.waitingList = []
        for i in range(self.numberOfLane):
            laneId = "gneE0_" + str(i)
            self.listOfLane.append(oneLaneObject(laneId, self.listOfYCoordinate[i]))

    # Detect new vehicle loaded and create a Vehicle object with them
    def keepTrackOfNewVehicle(self):
        # Keep track of loaded vehicle
        listOfNewVehicleLoaded = traci.simulation.getDepartedIDList()
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

    # Runs all functions that handle open space
    def updateAllLanes(self):
        listArrived = traci.simulation.getArrivedIDList()
        for lane in self.listOfLane:
            lane.updateOpenSpace(listArrived) # Keep track of all open space
            lane.updatePreparingSpace() # Update values of locked spaces
            lane.updateLockedSpace() # Update values of locked spaces
            lane.preparingOpenSpace() # Prepare future locked spaces
            lane.assureLockedSpace() # Assure that locked spaces stays lockde
            allLockedSpace = []
            allLockedSpace = lane.get_lockedSpace()
            # Keep track of every locked space on the road
            if allLockedSpace:
                for space in allLockedSpace:
                    self.allLockedSpace.append(space)
            # Draw middle point of every open space
            lane.draw_OpenSpace()

    # Trigger random left change
    def triggerLeftChangeLane(self, vehID = -1):
        if vehID is -1:
            targetVehicle = self.listOfVehicle[randint(0, len(self.listOfVehicle))].get_id() # Get a vehicle on lane 0
        else:
            targetVehicle = vehID
        if targetVehicle not in self.listOfLockedVehicle:
            if targetVehicle in self.waitingList:
                self.waitingList.remove(targetVehicle)
            targetVehicleCurrentLane = traci.vehicle.getLaneID(str(targetVehicle))
            targetVehicleLaneIndex = int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])
            # listOfVehicleOnLane = self.listOfLane[int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])].get_vehicleOnLane()
            traci.vehicle.setSpeed(targetVehicle, traci.vehicle.getSpeed(targetVehicle))
            self.listOfLockedVehicle.append((targetVehicle, "left")) # Keep track of the vehicle
            traci.vehicle.setColor(str(targetVehicle), (0,0,255)) #Set its color for GUI
            nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[targetVehicleLaneIndex + 1].get_currentOpenSpace(), "left") # Find its best nearest open space
            self.listOfLockedVehicle.append(nearestOpenSpace.get_backCar())
            self.listOfLockedVehicle.append(nearestOpenSpace.get_frontCar())
            self.allLockedSpaces.update({nearestOpenSpace.get_id() : (targetVehicle, "left")})
            self.listOfLane[targetVehicleLaneIndex + 1].add_preparingLockedSpace(nearestOpenSpace) # Prepare that open Space
        else:
            self.waitingList.append((targetVehicle, "left"))

    # Trigger random left change
    def triggerRightChangeLane(self, vehID = -1):
        if vehID is -1:
            targetVehicle = self.listOfVehicle[randint(0, len(self.listOfVehicle))].get_id() # Get a vehicle on lane 0
        else:
            targetVehicle = vehID
        if targetVehicle not in self.listOfLockedVehicle:
            if targetVehicle in self.waitingList:
                self.waitingList.remove(targetVehicle)
            targetVehicleCurrentLane = traci.vehicle.getLaneID(targetVehicle)
            targetVehicleLaneIndex = int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])
            traci.vehicle.setSpeed(targetVehicle, traci.vehicle.getSpeed(targetVehicle))
            self.listOfLockedVehicle.append((targetVehicle, "right")) # Keep track of the vehicle
            traci.vehicle.setColor(str(targetVehicle), (0,0,255)) #Set its color for GUI
            nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[targetVehicleLaneIndex - 1].get_currentOpenSpace(), "right") # Find its best nearest open space
            self.listOfLockedVehicle.append(nearestOpenSpace.get_backCar())
            self.listOfLockedVehicle.append(nearestOpenSpace.get_frontCar())
            self.allLockedSpaces.update({nearestOpenSpace.get_id() : (targetVehicle, "right")})
            self.listOfLane[targetVehicleLaneIndex - 1].add_preparingLockedSpace(nearestOpenSpace) # Prepare that open Space
        else:
            if targetVehicle not in self.waitingList:
                self.waitingList.append((targetVehicle, "right"))

    # find best nearest open space and return it
    def findNearestSpace(self, vehID, ListOpenSpaces, direction):
        # Get vehicle properties
        vehiclePosition = traci.vehicle.getLanePosition(vehID) + traci.vehicle.getSpeed(vehID)
        vehicleLength = traci.vehicle.getLength(vehID)
        if traci.vehicle.getLeader(vehID, 0) is not None:
            leadingCarSpeed = traci.vehicle.getSpeed(traci.vehicle.getLeader(vehID,0)[0])
        else:
            leadingCarSpeed = 0
        # Initialise fitness score and fitness value
        shortestDistanceScore = 999999
        closestMiddlePointSpace = None
        bestNonAdjacentSpace = None
        for space in ListOpenSpaces:
            spaceMiddlePosition = space.get_middlePosition()
            distance = math.sqrt((vehiclePosition - spaceMiddlePosition) ** 2) # Get the distance between car and middle point
            relativeDistance = spaceMiddlePosition - vehiclePosition
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            #print("ID: " + space.get_id() + " / " + str(relativeDistance) + " / " + str(space.get_landingLength()) + " / " + str(spaceMiddlePosition) + " / " + str(space.get_length() / 2) + " / " + str(space.get_growth()) + " / " + str(space.get_velocity()))
            if frontCar not in self.listOfLockedVehicle and backCar not in self.listOfLockedVehicle:
                if relativeDistance > 0:
                    if space.get_velocity() < traci.lane.getMaxSpeed(traci.vehicle.getLaneID(vehID)):
                        if distance < shortestDistanceScore: # If new distance shorter than currentBest
                            if space.get_landingLength() >= 5: # check if car has enough room to fit in open space
                                # Yes, this space become currentBest
                                shortestDistanceScore = distance
                                closestMiddlePointSpace = space
                                bestNonAdjacentSpace = space
                            else:
                                # Check if space could still be considered even though not enough room for car
                                # Check if the space growth needed to welcome car is not bigger than 30 and if the space is currently growing
                                # get_growth() is the difference between the speed of the backCar and the frontCar
                                # if backCarSpeed > frontCarSpeed than space is shrinking otherwise it is growing
                                if space.get_landingLength() > -30 and space.get_growth() == 1:
                                    # yes, space can be considered and become currentBest
                                    shortestDistanceScore = distance
                                    closestMiddlePointSpace = space
                                    bestNonAdjacentSpace = space
                else:
                    if space.get_velocity() > traci.vehicle.getSpeed(vehID) :
                        if distance < shortestDistanceScore: # If new distance shorter than currentBest
                            if space.get_landingLength() >= 5: # check if car has enough room to fit in open space
                                # Yes, this space become currentBest
                                shortestDistanceScore = distance
                                closestMiddlePointSpace = space
                                bestNonAdjacentSpace = space
                            else:
                                # Check if space could still be considered even though not enough room for car
                                # Check if the space growth needed to welcome car is not bigger than 30 and if the space is currently growing
                                # get_growth() is the difference between the speed of the backCar and the frontCar
                                # if backCarSpeed > frontCarSpeed than space is shrinking otherwise it is growing
                                if space.get_landingLength() > -30 and space.get_growth() == 1:
                                    # yes, space can be considered and become currentBest
                                    shortestDistanceScore = distance
                                    closestMiddlePointSpace = space
                                    bestNonAdjacentSpace = space
        return bestNonAdjacentSpace

    def checkIfVehicleCanChangeLane(self):
        #print("size ALS: " + str(len(self.allLockedSpace)) + " / size LLV: " + str(len(self.listOfLockedVehicle)))
        deleteList = []
        if self.allLockedSpaces and self.allLockedSpace:
            for targetOpenSpace, targetCar in self.allLockedSpaces.items():
                carPosition = traci.vehicle.getLanePosition(targetCar[0]) + traci.vehicle.getSpeed(targetCar[0])
                #print("Max Speed: " + str(traci.lane.getMaxSpeed('gneE0_0')) + " / CurrentSpeed: " + str(traci.vehicle.getSpeed(self.listOfLockedVehicle[0])))
                targetOpenSpace = self.returnCorrectOSObject(targetOpenSpace)
                targetOpenSpace.changeColor((255,0,0))
                middlePositionOpenSpace = targetOpenSpace.get_middlePosition()
                #distance = abs((carPosition - traci.vehicle.getLength(targetCar[0]) - middlePositionOpenSpace) # get the distance between car and space's middle position
                # print("carPosition:" + str(carPosition) + " / middlePositionOpenSpace: " + str(middlePositionOpenSpace) + " / D:" + str(distance))
                #print(str(carPosition) + " / " + str(middlePositionOpenSpace) + " / " + str(middlePositionOpenSpace - (targetOpenSpace.get_landingLength() / 2)) + " / " + str(middlePositionOpenSpace + (targetOpenSpace.get_landingLength() / 2)) + " / " + str(targetOpenSpace.get_length()) + " / " + str(targetOpenSpace.get_safeDistance()))
                # Verify that cars is close enough to the space's middlePosition to insert into itself into space
                if carPosition > middlePositionOpenSpace - (targetOpenSpace.get_landingLength() / 2) and carPosition < middlePositionOpenSpace + (targetOpenSpace.get_landingLength() / 2):
                    if targetCar[1] is "left":
                        traci.vehicle.changeLaneRelative(self.listOfLockedVehicle[0][0], 1, 2.0) # Start manoeuvre to change lane
                    elif targetCar[1] is "right":
                        traci.vehicle.changeLaneRelative(targetCar[0], 0, 2.0) # Start manoeuvre to change lane
                    traci.vehicle.setSpeed(targetCar[0], -1) # give back to sumo the control of car's speed
                    #self.listOfLockedVehicle.remove(self.listOfLockedVehicle[0]) # remove vehicle from locked vehicle
                    deleteList.append(targetOpenSpace.get_id())
                    self.unlockVehicle(targetCar[0])
                    self.unlockSpace(targetOpenSpace) # remove open space from list of locked space
                else: # Car is too far from middle point to insert
                    if (carPosition - middlePositionOpenSpace) > 0: # Car is ahead of space's middle position
                        # Reduce car speed to meet space's middle position
                        traci.vehicle.setSpeed(self.listOfLockedVehicle[0][0], traci.vehicle.getSpeed(self.listOfLockedVehicle[0][0]) - 0.2)
                    else: # Car is behind space's middle position
                        # Increase speed to meet space's middle position
                        traci.vehicle.setSpeed(self.listOfLockedVehicle[0][0], traci.vehicle.getSpeed(self.listOfLockedVehicle[0][0]) + 0.2)
            for k in deleteList: del self.allLockedSpaces[k]

    # Remove space from locked space's list
    def unlockSpace(self, space):
        self.allLockedSpace.remove(space)
        self.listOfLockedVehicle.remove(space.get_backCar())
        self.listOfLockedVehicle.remove(space.get_frontCar())
        for lane in self.listOfLane:
            lane.unlockSpace(space)

    def returnCorrectOSObject(self, OSId):
        for openSpace in self.allLockedSpace:
            if openSpace.get_id() is OSId:
                return openSpace
                break

    def unlockVehicle(self, vehID):
        for vehicle in self.listOfLockedVehicle:
            if vehID is vehicle[0]:
               self.listOfLockedVehicle.remove(vehicle)

    def newAttemptToLaneChangeWaitingCars(self):
        for car in self.waitingList:
            if car[1] is "left":
                self.triggerLeftChangeLane(car[0])
            elif car[1] is "right":
                self.triggerRightChangeLane(car[0])

    # main function that handles everything in this class
    def handlesAllManoeuvres(self):
        self.keepTrackOfNewVehicle()
        self.updateAllLanes()
        self.checkIfVehicleCanChangeLane()
