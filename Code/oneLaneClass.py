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
            # shape = "line"
            # position = [
            #     (middlePosition - (length / 2), self.YCoordinate - 0.5),
            #     (middlePosition - (length / 2), self.YCoordinate + 0.5),
            #     (middlePosition + (length / 2), self.YCoordinate - 0.5),
            #     (middlePosition + (length / 2), self.YCoordinate + 0.5)
            # ]
            # traci.polygon.add(space.get_id(), position, (66,244,83), True)

    def moveSpaceToLockedList(self, spaceIndex):
        self.lockedSpace.append(self.currentOpenSpace[spaceIndex])

    def assureLockedSpace(self):
        for space in self.lockedSpace:
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            print(space.get_length())
            traci.vehicle.setAccel(str(backCar), 0.0)
            traci.vehicle.setAccel(str(frontCar), 0.0)
            traci.vehicle.setColor(str(backCar), (255,0,0))
            traci.vehicle.setColor(str(frontCar), (255,0,0))
