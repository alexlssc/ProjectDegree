import os
import sys
import hashlib
from vehicleClass import Vehicle

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

class oneLaneObject:

    def __init__(self,id):
        self.id = id
        self.currentOpenSpace = {}
        self.previousOpenSpace = {}
        self.vehiclePosition = {}
        self.laneLength = traci.lane.getLength(id)

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

    def updateOpenSpace(self, listArrived):
        self.currentOpenSpace = {}
        self.vehiclePosition = {}
        vehicleOnLane = self.get_vehicleOnLane()
        for vehicle in vehicleOnLane:
            if not vehicle in listArrived:
                self.vehiclePosition.update({vehicle : traci.vehicle.getLanePosition(vehicle)})
        previousId = None
        previousPosition = None
        count = 0
        if self.id == "gneE0_0":
            print(len(self.vehiclePosition))
        for id, position in self.vehiclePosition.items():
            lengthVehicle = traci.vehicle.getLength(id)
            if self.id == "gneE0_0":
                print("Car length: " + str(lengthVehicle))
            if len(self.vehiclePosition) == 1:
                distanceBeforeCar = position - lengthVehicle
                distanceAfterCar = self.laneLength - position
                middlePositionDistanceBeforeCar = distanceBeforeCar / 2
                middlePositionDistanceAfterCar = self.laneLength - (distanceAfterCar / 2)
                self.currentOpenSpace.update({middlePositionDistanceBeforeCar : distanceBeforeCar})
                self.currentOpenSpace.update({middlePositionDistanceAfterCar : distanceAfterCar})
            elif len(self.vehiclePosition) == 2:
                if count == 0:
                    if self.id == "gneE0_0":
                        print("ID: " + id + " / P: " + str(position))
                    distance = position - lengthVehicle
                    middlePosition = distance / 2
                    self.currentOpenSpace.update({middlePosition : distance})

                else:
                        if self.id == "gneE0_0":
                            print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                        distance = (position - lengthVehicle) - previousPosition
                        middlePosition = (position - lengthVehicle) - (distance / 2)
                        self.currentOpenSpace.update({middlePosition : distance})
                        secondDistance = self.laneLength - position
                        secondMiddlePosition = self.laneLength - (secondDistance / 2)
                        self.currentOpenSpace.update({secondMiddlePosition : secondDistance})

            else:
                if count == 0:
                    if self.id == "gneE0_0":
                        print("ID: " + id + " / P: " + str(position))
                    distance = position - (lengthVehicle / 2)
                    middlePosition = distance / 2
                    self.currentOpenSpace.update({middlePosition : distance})
                elif count == len(self.vehiclePosition) - 1:
                    if self.id == "gneE0_0":
                        print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                    distance = (position - lengthVehicle) - previousPosition
                    middlePosition = (position - lengthVehicle) - (distance / 2)
                    self.currentOpenSpace.update({middlePosition : distance})
                    secondDistance = self.laneLength - position
                    secondMiddlePosition = self.laneLength - (secondDistance / 2)
                    self.currentOpenSpace.update({secondMiddlePosition : secondDistance})
                else:
                    if self.id == "gneE0_0":
                        print("ID: " + id + " / PR: " + str(previousPosition) + " / P: " + str(position))
                    distance = (position - lengthVehicle) - previousPosition
                    middlePosition = (position - lengthVehicle) - (distance / 2)
                    self.currentOpenSpace.update({middlePosition : distance})

            previousId = id
            previousPosition = position
            count += 1
