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
        self.listOpenSpaces = []
        # (spaceID, vehID, direction, state)
        self.LaneChangeData = []
        self.commonOneLaneObject = oneLaneObject(-1, -1)

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

    def removeFinishedVehicle(self):
        finishedVehicles = traci.simulation.getArrivedIDList()
        for finishedCar in finishedVehicles:
            for onLaneCar in self.listOfVehicle:
                if finishedCar is onLaneCar.get_id():
                    self.listOfVehicle.remove(onLaneCar)
            for idx,laneChangeData in enumerate(self.LaneChangeData):
                if laneChangeData[0].get_backCar() == finishedCar or laneChangeData[0].get_frontCar() == finishedCar:
                    self.unlockVehicle(laneChangeData)
                    try:
                        del self.LaneChangeData[idx]
                    except:
                        print(self.allLockedSpaces)
                        print(space.get_id())


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
        self.listOpenSpaces = []
        currentPreparingList = []
        currentLockedList = []
        listReadyToBeLocked = []
        self.spacesToRemove = []
        for lane in self.listOfLane:
            this_lane_openSpace = lane.updateOpenSpace(listArrived) # Keep track of all open space
            lane.set_currentOpenSpace(this_lane_openSpace)
            lane.draw_OpenSpace(this_lane_openSpace)
            for new_space in this_lane_openSpace:
                self.listOpenSpaces.append(new_space)

        # Update all spaces
        if self.LaneChangeData:
            for space in self.listOpenSpaces:
                for idx,laneChangeData in enumerate(self.LaneChangeData):
                    if space.get_id() == laneChangeData[0].get_id():
                        self.LaneChangeData[idx] = (space, laneChangeData[1], laneChangeData[2], laneChangeData[3])

        # Keep track of lock and preparing space
        if self.LaneChangeData:
            for laneChangeData in self.LaneChangeData:
                if laneChangeData[3] is "preparing":
                    currentPreparingList.append(laneChangeData[0])
                if laneChangeData[3] is "locking":
                    currentLockedList.append(laneChangeData[0])
        if currentPreparingList:
            listReadyToBeLocked = self.commonOneLaneObject.preparingOpenSpace(currentPreparingList) # Prepare future locked spaces

        if listReadyToBeLocked:
            for space in listReadyToBeLocked:
                for idx,laneChangeData in enumerate(self.LaneChangeData):
                    if laneChangeData[0] is space:
                        self.LaneChangeData[idx] = (laneChangeData[0], laneChangeData[1], laneChangeData[2], "locked")
                        currentLockedList.append(laneChangeData[0])
        if currentLockedList:
            self.spacesToRemove = self.commonOneLaneObject.assureLockedSpace(currentLockedList) # Assure that locked spaces stays lockde

        # Remove gone space
        if self.spacesToRemove:
            if self.LaneChangeData:
                print(str(spacesToRemove))
                for removeSpace in spacesToRemove:
                    for index, laneChangeData in enumerate(self.LaneChangeData):
                        if laneChangeData[0] is removeSpace:
                            del self.LaneChangeData[index]

    def triggerLaneChange(self, vehID = -1):
        carAccepted = False
        count = 0
        if vehID is -1:
            while carAccepted is False and count < 20:
                try:
                    targetVehicle = self.listOfVehicle[randint(0, len(self.listOfVehicle) - 1)].get_id() # Get a vehicle on lane 0
                    targetVehiclePosition = traci.vehicle.getLanePosition(targetVehicle)
                    if targetVehiclePosition > 150 and targetVehiclePosition < 1500:
                        carAccepted = True
                        break
                    else:
                        count += 1
                except Exception as e:
                    print(str(e))
                    count += 1
        else:
            try:
                targetVehicle = vehID
                targetVehiclePosition = traci.vehicle.getLanePosition(targetVehicle)
                if targetVehiclePosition > 150 or targetVehiclePosition < 1500:
                    carAccepted =  True
                else:
                    self.waitingList.remove(targetVehicle)
            except Exception as e:
                print(str(e))
                self.waitingList.remove(targetVehicle)
        if carAccepted:
            if targetVehicle not in self.listOfLockedVehicle:
                if targetVehicle in self.waitingList:
                    self.waitingList.remove(targetVehicle)
                targetVehicleCurrentLane = traci.vehicle.getLaneID(str(targetVehicle))
                targetVehicleLaneIndex = int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])
                if targetVehicleLaneIndex is 0:
                    self.triggerLeftChangeLane(targetVehicle)
                elif targetVehicleLaneIndex is 4:
                    self.triggerRightChangeLane(targetVehicle)
                else:
                    randomTrigger = randint(0,100)
                    if randomTrigger < 50:
                        self.triggerLeftChangeLane(targetVehicle)
                    else:
                        self.triggerRightChangeLane(targetVehicle)


    # Trigger random left change
    def triggerLeftChangeLane(self, targetVehicle):
        targetVehicleCurrentLane = traci.vehicle.getLaneID(str(targetVehicle))
        targetVehicleLaneIndex = int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])
        # listOfVehicleOnLane = self.listOfLane[int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])].get_vehicleOnLane()
        traci.vehicle.setSpeed(targetVehicle, traci.vehicle.getSpeed(targetVehicle))
        #traci.vehicle.setColor(str(targetVehicle), (0,0,255)) #Set its color for GUI
        nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[targetVehicleLaneIndex + 1].get_currentOpenSpace()) # Find its best nearest open space
        if nearestOpenSpace is not None:
            self.listOfLockedVehicle.append(targetVehicle) # Keep track of the vehicle
            self.listOfLockedVehicle.append(nearestOpenSpace.get_backCar())
            self.listOfLockedVehicle.append(nearestOpenSpace.get_frontCar())
            self.LaneChangeData.append((nearestOpenSpace, targetVehicle, "left", "preparing"))
        else:
            self.waitingList.append(targetVehicle)

    # Trigger random left change
    def triggerRightChangeLane(self, targetVehicle):
        targetVehicleCurrentLane = traci.vehicle.getLaneID(targetVehicle)
        targetVehicleLaneIndex = int(targetVehicleCurrentLane[len(targetVehicleCurrentLane) - 1])
        traci.vehicle.setSpeed(targetVehicle, traci.vehicle.getSpeed(targetVehicle))
        nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[targetVehicleLaneIndex - 1].get_currentOpenSpace()) # Find its best nearest open space
        if nearestOpenSpace is not None:
            self.listOfLockedVehicle.append(targetVehicle) # Keep track of the vehicle
            self.listOfLockedVehicle.append(nearestOpenSpace.get_backCar())
            self.listOfLockedVehicle.append(nearestOpenSpace.get_frontCar())
            self.LaneChangeData.append((nearestOpenSpace, targetVehicle, "right", "preparing"))
        else:
            self.waitingList.append(targetVehicle)

    # find best nearest open space and return it
    def findNearestSpace(self, vehID, ListOpenSpaces):
        # Get vehicle properties
        vehiclePosition = traci.vehicle.getLanePosition(vehID) + traci.vehicle.getSpeed(vehID)
        vehicleLength = traci.vehicle.getLength(vehID)
        # if traci.vehicle.getLeader(vehID, 0) is not None:
        #     leadingCarSpeed = traci.vehicle.getSpeed(traci.vehicle.getLeader(vehID,0)[0])
        # else:
        #     leadingCarSpeed = 0
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
            if frontCar not in self.listOfLockedVehicle and backCar not in self.listOfLockedVehicle:
                if relativeDistance > 0: # Open space ahead of lane changing car
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
                else: # Open space behind lane changing car
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
        if self.LaneChangeData:
            for idx,laneChangeData in enumerate(self.LaneChangeData):
                if laneChangeData[3] is "locked":
                    try:
                        carPosition = traci.vehicle.getLanePosition(laneChangeData[1]) + traci.vehicle.getSpeed(laneChangeData[1])
                    except Exception as e:
                        self.unlockVehicle(laneChangeData)
                        del self.LaneChangeData[idx]
                        return
                    #targetOpenSpace.changeColor((255,0,0))
                    middlePositionOpenSpace = laneChangeData[0].get_middlePosition()
                    # Verify that cars is close enough to the space's middlePosition to insert into itself into space
                    if carPosition > middlePositionOpenSpace - (laneChangeData[0].get_landingLength() / 2) and carPosition < middlePositionOpenSpace + (laneChangeData[0].get_landingLength() / 2):
                        if laneChangeData[2] is "left":
                            traci.vehicle.changeLaneRelative(laneChangeData[1], 1, 2.0) # Start manoeuvre to change lane
                        elif laneChangeData[2] is "right":
                            traci.vehicle.changeLaneRelative(laneChangeData[1], 0, 2.0) # Start manoeuvre to change lane
                        traci.vehicle.setSpeed(laneChangeData[1], -1) # give back to sumo the control of car's speed
                        self.unlockVehicle(laneChangeData)
                        del self.LaneChangeData[idx]
                    else: # Car is too far from middle point to insert
                        if (carPosition - middlePositionOpenSpace) > 0: # Car is ahead of space's middle position
                            # Reduce car speed to meet space's middle position
                            traci.vehicle.setSpeed(laneChangeData[1], traci.vehicle.getSpeed(laneChangeData[1]) - 0.2)
                        else: # Car is behind space's middle position
                            # Increase speed to meet space's middle position
                            traci.vehicle.setSpeed(laneChangeData[1], traci.vehicle.getSpeed(laneChangeData[1]) + 0.2)

    # Remove space from locked space's list
    def unlockSpace(self, space):
        self.allLockedSpace.remove(space)
        try:
            self.listOfLockedVehicle.remove(space.get_backCar())
        except Exception as e:
            print(str(e) + " / Unlock Space AllLanes / " + space.get_id())
        try:
            self.listOfLockedVehicle.remove(space.get_frontCar())
        except Exception as e:
            print(str(e) + " / Unlock Space AllLanes / " + space.get_id())
        if space.get_backCar()[0] is not 's':
            try:
                traci.vehicle.setColor(space.get_backCar(), (255,255,0))
            except Exception as e:
                print(str(e) + " / Unlock Space AllLanes / " + space.get_id())
        if space.get_frontCar()[0] is not 'e':
            try:
                traci.vehicle.setColor(space.get_frontCar(), (255,255,0))
            except Exception as e:
                print(str(e) + " / Unlock Space AllLanes / " + space.get_id())
        for lane in self.listOfLane:
            lane.unlockSpace(space)

    def returnCorrectOSObject(self, OSId):
        for openSpace in self.allLockedSpace:
            if openSpace.get_id() is OSId:
                return openSpace
                break

    def unlockVehicle(self, laneChangeData):
        try:
            backCar = laneChangeData[0].get_backCar()
        except:
            print("ERROR UNLOCK: " + str(laneChangeData[0]))
        frontCar = laneChangeData[0].get_frontCar()
        vehID = laneChangeData[1]

        if backCar in self.listOfLockedVehicle:
            self.listOfLockedVehicle.remove(backCar)
        if frontCar in self.listOfLockedVehicle:
            self.listOfLockedVehicle.remove(frontCar)
        if vehID in self.listOfLockedVehicle:
            self.listOfLockedVehicle.remove(vehID)


    def newAttemptToLaneChangeWaitingCars(self):
        print(str(self.waitingList))
        for car in self.waitingList:
            self.triggerLaneChange(car)

    # main function that handles everything in this class
    def handlesAllManoeuvres(self):
        self.keepTrackOfNewVehicle()
        self.removeFinishedVehicle()
        self.updateAllLanes()
        if self.waitingList:
            self.newAttemptToLaneChangeWaitingCars()
        self.checkIfVehicleCanChangeLane()
