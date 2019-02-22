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

    # Detect all the open spaces of the lane
    def updateOpenSpace(self, listArrived):
        self.previousOpenSpace = self.currentOpenSpace
        self.currentOpenSpace = []
        self.vehiclePosition = {}
        vehicleOnLane = self.get_vehicleOnLane() # Get all the cars' id on this lane
        # Get all cars' position on this lane
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
                lengthVehicle = traci.vehicle.getLength(id) # Get length of vehicle analysed
                if len(self.vehiclePosition) == 1: # Only one car on the lane
                    distanceBeforeCar = position - lengthVehicle
                    distanceAfterCar = self.laneLength - position
                    middlePositionDistanceBeforeCar = distanceBeforeCar / 2
                    middlePositionDistanceAfterCar = self.laneLength - (distanceAfterCar / 2)
                    self.currentOpenSpace.append(OpenSpace(distanceBeforeCar, middlePositionDistanceBeforeCar, "start", id))
                    self.currentOpenSpace.append(OpenSpace(distanceAfterCar, middlePositionDistanceAfterCar, id, "end"))
                elif len(self.vehiclePosition) == 2: # Two cars on the lane
                    if count == 0: # First car on the lane / Closest to start
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position))
                        distance = position - lengthVehicle
                        middlePosition = distance / 2
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, "start", id))

                    else: # Last car on the lane / Closest to end
                            # if self.id == "gneE0_0":
                            #     print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                            distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                            middlePosition = (position - lengthVehicle) - (distance / 2)
                            self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))
                            secondDistance = math.sqrt((self.laneLength - position) ** 2)
                            secondMiddlePosition = self.laneLength - (secondDistance / 2)
                            self.currentOpenSpace.append(OpenSpace(secondDistance, secondMiddlePosition, id, "end"))

                else: # More than two cars on the lane
                    if count == 0: # First car on the lane / Closest to start
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position))
                        distance = position - lengthVehicle
                        middlePosition = distance / 2
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, "start", id))
                    elif count == len(self.vehiclePosition) - 1: # Last car on the lane / Closest to end
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                        distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                        middlePosition = (position - lengthVehicle) - (distance / 2)
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))
                        secondDistance = math.sqrt((self.laneLength - position) ** 2)
                        secondMiddlePosition = self.laneLength - (secondDistance / 2)
                        self.currentOpenSpace.append(OpenSpace(secondDistance, secondMiddlePosition, id, "end"))
                    else: # Any middle car on the lane
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / PR: " + str(previousPosition) + " / P: " + str(position))
                        distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                        middlePosition = (position - lengthVehicle) - (distance / 2)
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))

                previousId = id
                previousPosition = position
                count += 1

    # Update values of all locked space
    def updateLockedSpace(self):
        for currentSpace in self.currentOpenSpace:
            for lockedSpace in self.lockedSpace:
                if currentSpace == lockedSpace: #currentSpace is lockedSpace
                    lockedSpace.updateValues(currentSpace)

    # Draw all open spaces' middle position
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

    # Send current space to preparation to be locked
    def startLockingSpace(self, spaceIndex):
        self.gettingReadySpace.append(self.currentOpenSpace[spaceIndex])

    # Unlock expired locked spaces
    def unlockSpace(self, space):
        if space in self.lockedSpace:
            if space.get_backCar() is not "start": # backCar needs to be a vehicle
                traci.vehicle.setSpeed(space.get_backCar(), -1) # Give speed's control back to sumo
                traci.vehicle.setColor(space.get_backCar(), (255,255,0)) # Set color back to yellow
            if space.get_frontCar() is not "end": # frontCar needs to be a vehicle
                traci.vehicle.setSpeed(space.get_frontCar(), -1) # Give speed's control back to sumo
                traci.vehicle.setColor(space.get_frontCar(), (255,255,0)) # Set color back to yellow
            self.lockedSpace.remove(space) # remove locked space from list

    # Prepare future locked space
    def preparingOpenSpace(self):
        for space in self.gettingReadySpace:
            # print("First Growing: " + str(space.get_growing()))
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            if space.get_landingLength() < 0: # currently the space can not welcome vehicle
                space.set_growing(True) # declare space is growing
            if not space.get_growing(): # if space is not growing / can welcome car straight away
                # print("Locking attempt")
                if backCar is not "start" and frontCar is not "end": # both front and back are vehicle
                    # get both speed
                    frontCarSpeed = traci.vehicle.getSpeed(str(frontCar))
                    backCarSpeed = traci.vehicle.getSpeed(str(backCar))
                    # average it to get the target locked speed
                    lockSpeed = (backCarSpeed + frontCarSpeed) / 2
                    # get speed difference between front and back car
                    totalDiffFromCommonSpeed = abs(lockSpeed - backCarSpeed) + abs(lockSpeed - frontCarSpeed)
                else:
                    if backCar is "start":
                        frontCarSpeed = round(traci.vehicle.getSpeed(str(frontCar)))
                    if frontCar is "end":
                        backCarSpeed = round(traci.vehicle.getSpeed(str(backCar)))
                    totalDiffFromCommonSpeed = 0
                # print("Space distance: " + str(space.get_length()) + " / BCS: " + str(backCarSpeed) + " / FCS: " + str(frontCarSpeed) + " / CS: " + str(lockSpeed) + " / TDS: " + str(totalDiffFromCommonSpeed))
                if totalDiffFromCommonSpeed < 0.01: # difference between both speeds is acceptable
                    # print("Equality reached")

                    # workout the new safety distance between vehicles
                    if backCar is not "start" and frontCar is not "end":
                        space.set_safeDistance(lockSpeed, lockSpeed)
                    else:
                        if backCar is "start":
                            space.set_safeDistance(0, frontCarSpeed)
                        if frontCar is "end":
                            space.set_safeDistance(backCarSpeed, 0)
                    # update the landing length
                    space.update_landingLength()
                    #print("Growing: " + str(space.get_growing()) + " / Length: " + str(space.get_length()) + " / SD: " + str(space.get_safeDistance()) + " / LL: " + str(space.get_landingLength()))
                    if space.get_landingLength() >= 5: # decide if space can welcome car after speed locked
                        self.lockedSpace.append(space) # lock the space
                        self.gettingReadySpace.remove(space) # remove from preparing list
                    else: # space can not welcome the car anymore
                        space.set_growing(True) # start growing the space
                else: # if both speeds aren't synchronised yet
                    # change both car's colours to purple
                    traci.vehicle.setColor(str(backCar), (255,0,255))
                    traci.vehicle.setColor(str(frontCar), (255,0,255))
                    # change their speed
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
                # get the new landing length value
                space.update_landingLength()
                #print("Growing: " + str(space.get_growing()) + " / Length: " + str(space.get_length()) + " / SD: " + str(space.get_safeDistance()) + " / LL: " + str(space.get_landingLength()))
                if space.get_landingLength() >= 5: # Decide if car can welcome the car
                    self.lockedSpace.append(space) # lock the space
                    self.gettingReadySpace.remove(space) # remove from preparing list

    # Assure that locked space stays intact
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
            if backCar is not "start" and frontCar is not "end": # space between two vehicles
                # back car adapts its speed to front car
                # allows space to keep same length even though there is a slow down ahead
                traci.vehicle.setSpeed(str(backCar), traci.vehicle.getSpeed(frontCar))
                traci.vehicle.setSpeed(str(frontCar), traci.vehicle.getSpeed(frontCar))
            try:
                traci.vehicle.setColor(str(backCar), (255,0,0)) # change color to red
            except:
                print("Can't draw")
            try:
                traci.vehicle.setColor(str(frontCar), (255,0,0)) # change color to red
            except:
                print("Can't draw")
