import os
import sys
import hashlib
import math
from vehicleClass import Vehicle
from openSpaceClass import OpenSpace

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

class oneLaneObject:

    def __init__(self,id, YCoordinate):
        self.id = id
        self.currentOpenSpace = []
        self.previousOpenSpace = []
        self.lockedSpace = []
        self.gettingReadySpace = []
        self.vehiclePosition = {}
        self.laneLength = traci.lane.getLength(id)
        self.YCoordinate = YCoordinate


    def get_id(self):
        return self.id

    def set_id(self, new_id):
        self.id = new_id

    def get_vehicleOnLane(self):
        return traci.lane.getLastStepVehicleIDs(self.id)

    def get_previousOpenSpace(self):
        return self.previousOpenSpace

    def get_currentOpenSpace(self):
        return self.currentOpenSpace

    def get_curentOpenSpaceId(self):
        listOfId = []
        for openSpace in self.currentOpenSpace:
            listOfId.append(openSpace.get_id())
        return listOfId

    def get_lockedSpace(self):
        return self.lockedSpace

    def add_lockedSpace(self, spaceIndex):
        self.lockedSpace.append(self.get_currentOpenSpace[spaceIndex])

    def add_preparingLockedSpace(self, space):
        self.gettingReadySpace.append(space)

    def updateOpenSpace(self, listArrived):
        self.previousOpenSpace = self.currentOpenSpace
        self.currentOpenSpace = []
        self.vehiclePosition = {}
        vehicleOnLane = self.get_vehicleOnLane()
        for vehicle in vehicleOnLane:
            if not vehicle in listArrived:
                self.vehiclePosition.update({vehicle : traci.vehicle.getLanePosition(vehicle) + traci.vehicle.getSpeed(vehicle)})
        previousId = None
        previousPosition = None
        count = 0
        if vehicleOnLane:
            for id, position in self.vehiclePosition.items():
                # if self.id == "gneE0_4":
                #     print("ID: " + id + " / P: " + str(traci.vehicle.getPosition(id)))
                lengthVehicle = traci.vehicle.getLength(id)
                if len(self.vehiclePosition) == 1:
                    distanceBeforeCar = position - lengthVehicle
                    distanceAfterCar = self.laneLength - position
                    middlePositionDistanceBeforeCar = distanceBeforeCar / 2
                    middlePositionDistanceAfterCar = self.laneLength - (distanceAfterCar / 2)
                    self.currentOpenSpace.append(OpenSpace(distanceBeforeCar, middlePositionDistanceBeforeCar, "start", id))
                    self.currentOpenSpace.append(OpenSpace(distanceAfterCar, middlePositionDistanceAfterCar, id, "end"))
                elif len(self.vehiclePosition) == 2:
                    if count == 0:
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position))
                        distance = position - lengthVehicle
                        middlePosition = distance / 2
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, "start", id))

                    else:
                            # if self.id == "gneE0_0":
                            #     print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                            distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                            middlePosition = (position - lengthVehicle) - (distance / 2)
                            self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))
                            secondDistance = math.sqrt((self.laneLength - position) ** 2)
                            secondMiddlePosition = self.laneLength - (secondDistance / 2)
                            self.currentOpenSpace.append(OpenSpace(secondDistance, secondMiddlePosition, id, "end"))

                else:
                    if count == 0:
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position))
                        distance = position - lengthVehicle
                        middlePosition = distance / 2
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, "start", id))
                    elif count == len(self.vehiclePosition) - 1:
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                        distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                        middlePosition = (position - lengthVehicle) - (distance / 2)
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))
                        secondDistance = math.sqrt((self.laneLength - position) ** 2)
                        secondMiddlePosition = self.laneLength - (secondDistance / 2)
                        self.currentOpenSpace.append(OpenSpace(secondDistance, secondMiddlePosition, id, "end"))
                    else:
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / PR: " + str(previousPosition) + " / P: " + str(position))
                        distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                        middlePosition = (position - lengthVehicle) - (distance / 2)
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))

                previousId = id
                previousPosition = position
                count += 1

    def reduceLargeOpenSpace(self):
        for currentSpace in self.currentOpenSpace:
            if currentSpace not in self.lockedSpace and currentSpace not in self.gettingReadySpace:
                lengthSpace = currentSpace.get_length()
                print(lengthSpace)
                if lengthSpace > 300:
                    if currentSpace.get_backCar() is not "start":
                        print("ACCEL")
                        traci.vehicle.slowDown(currentSpace.get_backCar(), traci.vehicle.getSpeed(currentSpace.get_backCar()) + 1, 2)

    def updateLockedSpace(self):
        for currentSpace in self.currentOpenSpace:
            for lockedSpace in self.lockedSpace:
                if currentSpace == lockedSpace:
                    lockedSpace.updateValues(currentSpace)

    def draw_OpenSpace(self):
        for oldSpace in self.previousOpenSpace:
            try:
                traci.poi.remove(oldSpace.get_id(), 10)
            except:
                print("Can't remove space")
        for space in self.currentOpenSpace:
            middlePosition = space.get_middlePosition()
            length = space.get_length()
            try:
                traci.poi.add(space.get_id(), middlePosition, self.YCoordinate, (66,244,83), "line", 10)
            except:
                traci.poi.setPosition(space.get_id(), middlePosition, self.YCoordinate)

    def startLockingSpace(self, spaceIndex):
        self.gettingReadySpace.append(self.currentOpenSpace[spaceIndex])

    def unlockSpace(self, space):
        if space in self.lockedSpace:
            if space.get_backCar() is not "start":
                traci.vehicle.setSpeed(space.get_backCar(), -1)
                traci.vehicle.setColor(space.get_backCar(), (255,255,0))
            if space.get_frontCar() is not "end":
                traci.vehicle.setSpeed(space.get_frontCar(), -1)
                traci.vehicle.setColor(space.get_frontCar(), (255,255,0))
            self.lockedSpace.remove(space)

    def preparingOpenSpace(self):
        for space in self.gettingReadySpace:
            # print("First Growing: " + str(space.get_growing()))
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            if space.get_landingLength() < 0:
                space.set_growing(True)
            if not space.get_growing():
                # print("Locking attempt")
                if backCar is not "start" and frontCar is not "end":
                    frontCarSpeed = traci.vehicle.getSpeed(str(frontCar))
                    backCarSpeed = traci.vehicle.getSpeed(str(backCar))
                    lockSpeed = (backCarSpeed + frontCarSpeed) / 2
                    totalDiffFromCommonSpeed = abs(lockSpeed - backCarSpeed) + abs(lockSpeed - frontCarSpeed)
                else:
                    if backCar is "start":
                        frontCarSpeed = round(traci.vehicle.getSpeed(str(frontCar)))
                    if frontCar is "end":
                        backCarSpeed = round(traci.vehicle.getSpeed(str(backCar)))
                    totalDiffFromCommonSpeed = 0
                print("Space distance: " + str(space.get_length()) + " / BCS: " + str(backCarSpeed) + " / FCS: " + str(frontCarSpeed) + " / CS: " + str(lockSpeed) + " / TDS: " + str(totalDiffFromCommonSpeed))
                if totalDiffFromCommonSpeed < 0.01:
                    # print("Equality reached")
                    if backCar is not "start" and frontCar is not "end":
                        space.set_safeDistance(lockSpeed, lockSpeed)
                    else:
                        if backCar is "start":
                            space.set_safeDistance(0, frontCarSpeed)
                        if frontCar is "end":
                            space.set_safeDistance(backCarSpeed, 0)
                    space.update_landingLength()
                    #print("Growing: " + str(space.get_growing()) + " / Length: " + str(space.get_length()) + " / SD: " + str(space.get_safeDistance()) + " / LL: " + str(space.get_landingLength()))
                    if space.get_landingLength() >= 10:
                        self.lockedSpace.append(space)
                        self.gettingReadySpace.remove(space)
                    else:
                        space.set_growing(True)
                else:
                    traci.vehicle.setColor(str(backCar), (255,0,255))
                    traci.vehicle.setColor(str(frontCar), (255,0,255))
                    # traci.vehicle.setAccel(str(backCar), 0.0)
                    # traci.vehicle.setAccel(str(frontCar), 0.0)
                    traci.vehicle.setSpeed(str(backCar), lockSpeed)
                    traci.vehicle.setSpeed(str(frontCar), lockSpeed)
            else: #else of is_growing
                if backCar is not "start":
                    backCarSpeed = traci.vehicle.getSpeed(str(backCar))
                    print("True BS: " + str(backCarSpeed))
                    traci.vehicle.setSpeed(str(backCar), backCarSpeed - 0.3)
                if frontCar is not "end":
                    frontCarSpeed = traci.vehicle.getSpeed(str(frontCar))
                    print("True FS: " + str(frontCarSpeed))
                    traci.vehicle.setSpeed(str(frontCar), frontCarSpeed + 0.3)
                if backCar is not "start" and frontCar is not "end":
                    space.set_safeDistance(backCarSpeed, frontCarSpeed)
                else:
                    if backCar is "start":
                        space.set_safeDistance(0,frontCarSpeed)
                    if frontCar is "end":
                        space.set_safeDistance(backCarSpeed, 0)
                space.update_landingLength()
                #print("Growing: " + str(space.get_growing()) + " / Length: " + str(space.get_length()) + " / SD: " + str(space.get_safeDistance()) + " / LL: " + str(space.get_landingLength()))
                if space.get_landingLength() >= 10:
                    self.lockedSpace.append(space)
                    self.gettingReadySpace.remove(space)


    def assureLockedSpace(self):
        for space in self.lockedSpace:
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            #commonSpeed = (traci.vehicle.getSpeed(str(backCar)) + traci.vehicle.getSpeed(str(frontCar))) / 2
            print("Space distance: " + str(space.get_length()) + " / BCS: " + str(traci.vehicle.getSpeed(str(backCar))) + "/ FCS: " + str(traci.vehicle.getSpeed(str(frontCar))) )
            # traci.vehicle.setAccel(str(backCar), 0.0)
            # traci.vehicle.setAccel(str(frontCar), 0.0)
            if backCar is not "start":
                traci.vehicle.setSpeed(str(backCar), traci.vehicle.getSpeed(backCar))
            if frontCar is not "end":
                traci.vehicle.setSpeed(str(frontCar), traci.vehicle.getSpeed(frontCar))
            if backCar is not "start" and frontCar is not "end":
                traci.vehicle.setSpeed(str(backCar), traci.vehicle.getSpeed(frontCar))
                traci.vehicle.setSpeed(str(frontCar), traci.vehicle.getSpeed(frontCar))
            try:
                traci.vehicle.setColor(str(backCar), (255,0,0))
            except:
                print("Can't draw")
            try:
                traci.vehicle.setColor(str(frontCar), (255,0,0))
            except:
                print("Can't draw")
