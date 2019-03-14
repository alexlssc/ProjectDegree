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

    def get_maxSpeedOnLane(self):
        return traci.lane.getMaxSpeed(self.id)

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
                    self.currentOpenSpace.append(OpenSpace(distanceBeforeCar, middlePositionDistanceBeforeCar, "start-" + self.id, id))
                    self.currentOpenSpace.append(OpenSpace(distanceAfterCar, middlePositionDistanceAfterCar, id, "end-" + self.id))
                elif len(self.vehiclePosition) == 2: # Two cars on the lane
                    if count == 0: # First car on the lane / Closest to start
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position))
                        distance = position - lengthVehicle
                        middlePosition = distance / 2
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, "start-" + self.id, id))

                    else: # Last car on the lane / Closest to end
                            # if self.id == "gneE0_0":
                            #     print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                            distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                            middlePosition = (position - lengthVehicle) - (distance / 2)
                            self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))
                            secondDistance = math.sqrt((self.laneLength - position) ** 2)
                            secondMiddlePosition = self.laneLength - (secondDistance / 2)
                            self.currentOpenSpace.append(OpenSpace(secondDistance, secondMiddlePosition, id, "end-" + self.id))

                else: # More than two cars on the lane
                    if count == 0: # First car on the lane / Closest to start
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position))
                        distance = position - lengthVehicle
                        middlePosition = distance / 2
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, "start-" + self.id, id))
                    elif count == len(self.vehiclePosition) - 1: # Last car on the lane / Closest to end
                        # if self.id == "gneE0_0":
                        #     print("ID: " + id + " / P: " + str(position) + " / END: " + str(self.laneLength))
                        distance = math.sqrt(((position - lengthVehicle) - previousPosition) ** 2)
                        middlePosition = (position - lengthVehicle) - (distance / 2)
                        self.currentOpenSpace.append(OpenSpace(distance, middlePosition, previousId, id))
                        secondDistance = math.sqrt((self.laneLength - position) ** 2)
                        secondMiddlePosition = self.laneLength - (secondDistance / 2)
                        self.currentOpenSpace.append(OpenSpace(secondDistance, secondMiddlePosition, id, "end-" + self.id))
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

    def updatePreparingSpace(self):
        for currentSpace in self.currentOpenSpace:
            for preparedSpace in self.gettingReadySpace:
                if currentSpace == preparedSpace:
                    preparedSpace.updateValues(currentSpace)

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
            if space.get_backCar()[0] is not 's': # backCar needs to be a vehicle
                try:
                    traci.vehicle.setSpeed(space.get_backCar(), -1) # Give speed's control back to sumo
                    traci.vehicle.setColor(space.get_backCar(), (255,255,0)) # Set color back to yellow
                except Exception as e:
                    print(str(e))
            if space.get_frontCar()[0] is not 'e': # frontCar needs to be a vehicle
                try:
                    traci.vehicle.setSpeed(space.get_frontCar(), -1) # Give speed's control back to sumo
                    traci.vehicle.setColor(space.get_frontCar(), (255,255,0)) # Set color back to yellow
                except Exception as e:
                    print(str(e))
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
                if backCar[0] is not 's' and frontCar[0] is not 'e': # both front and back are vehicle
                    # get both speed
                    try:
                        frontCarSpeed = traci.vehicle.getSpeed(str(frontCar))
                    except Exception as e:
                        print(str(e) + " / preparingSpace")
                        self.gettingReadySpace.remove(space)
                        return

                    try:
                        backCarSpeed = traci.vehicle.getSpeed(str(backCar))
                    except Exception as e:
                        print(str(e) + " / preparingSpace")
                        self.gettingReadySpace.remove(space)
                        return
                    # average it to get the target locked speed
                    lockSpeed = (backCarSpeed + frontCarSpeed) / 2
                    # get speed difference between front and back car
                    totalDiffFromCommonSpeed = abs(lockSpeed - backCarSpeed) + abs(lockSpeed - frontCarSpeed)
                else:
                    if backCar[0] is 's':
                        frontCarSpeed = round(traci.vehicle.getSpeed(str(frontCar)))
                    if frontCar[0] is 'e':
                        backCarSpeed = round(traci.vehicle.getSpeed(str(backCar)))
                    totalDiffFromCommonSpeed = 0
                # print("Space distance: " + str(space.get_length()) + " / BCS: " + str(backCarSpeed) + " / FCS: " + str(frontCarSpeed) + " / CS: " + str(lockSpeed) + " / TDS: " + str(totalDiffFromCommonSpeed))
                if totalDiffFromCommonSpeed < 0.01: # difference between both speeds is acceptable
                    # print("Equality reached")

                    # workout the new safety distance between vehicles
                    if backCar[0] is not 's' and frontCar[0] is not 'e':
                        space.set_safeDistance(lockSpeed, lockSpeed)
                    else:
                        if backCar[0] is 's':
                            space.set_safeDistance(0, frontCarSpeed)
                        if frontCar[0] is 'e':
                            space.set_safeDistance(backCarSpeed, 0)
                    # update the landing length
                    space.update_landingLength()
                    #print("Growing: " + str(space.get_growing()) + " / Length: " + str(space.get_length()) + " / SD: " + str(space.get_safeDistance()) + " / LL: " + str(space.get_landingLength()))
                    if space.get_landingLength() >= 7: # decide if space can welcome car after speed locked
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
                if backCar[0] is not 's':
                    try:
                        backCarSpeed = traci.vehicle.getSpeed(str(backCar))
                    except Exception as e:
                        print(str(e) + " / preparingSpace")
                        self.gettingReadySpace.remove(space)
                        return
                    traci.vehicle.setSpeed(str(backCar), backCarSpeed - 0.3)
                if frontCar[0] is not 'e':
                    try:
                        frontCarSpeed = traci.vehicle.getSpeed(str(frontCar))
                    except Exception as e:
                        print(str(e) + " / preparingSpace")
                        self.gettingReadySpace.remove(space)
                        return
                    traci.vehicle.setSpeed(str(frontCar), frontCarSpeed + 0.3)
                if backCar[0] is not 's' and frontCar[0] is not 'e':
                    space.set_safeDistance(backCarSpeed, frontCarSpeed)
                else:
                    if backCar[0] is 's':
                        space.set_safeDistance(0,frontCarSpeed)
                    if frontCar[0] is 'e':
                        space.set_safeDistance(backCarSpeed, 0)
                # get the new landing length value
                space.update_landingLength()
                #print("Growing: " + str(space.get_growing()) + " / Length: " + str(space.get_length()) + " / SD: " + str(space.get_safeDistance()) + " / LL: " + str(space.get_landingLength()))
                if space.get_landingLength() >= 7: # Decide if car can welcome the car
                    self.lockedSpace.append(space) # lock the space
                    self.gettingReadySpace.remove(space) # remove from preparing list
                    if space.get_backCar()[0] is not 's':
                        traci.vehicle.setColor(space.get_backCar(), (255, 255,0))
                    if space.get_frontCar()[0] is not 'e':
                        traci.vehicle.setColor(space.get_frontCar(), (255,255,0))

    # Assure that locked space stays intact
    def assureLockedSpace(self):
        for space in self.lockedSpace:
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            #commonSpeed = (traci.vehicle.getSpeed(str(backCar)) + traci.vehicle.getSpeed(str(frontCar))) / 2
            #print("Space distance: " + str(space.get_length()) + " / BCS: " + str(traci.vehicle.getSpeed(str(backCar))) + "/ FCS: " + str(traci.vehicle.getSpeed(str(frontCar))) )
            if backCar[0] is not 's':
                try:
                    traci.vehicle.setSpeed(str(backCar), traci.vehicle.getSpeed(backCar))
                except Exception as e:
                    print(str(e))
                    return
            if frontCar[0] is not 'e':
                try:
                    traci.vehicle.setSpeed(str(frontCar), traci.vehicle.getSpeed(frontCar))
                except Exception as e:
                    print(str(e))
                    return
            if backCar[0] is not 's' and frontCar[0] is not 'e': # space between two vehicles
                # back car adapts its speed to front car
                # allows space to keep same length even though there is a slow down ahead
                try:
                    traci.vehicle.setSpeed(str(backCar), traci.vehicle.getSpeed(frontCar))
                except Exception as e:
                    print(str(e))
                    return
                try:
                    traci.vehicle.setSpeed(str(frontCar), traci.vehicle.getSpeed(frontCar))
                except Exception as e:
                    print(str(e))
                    return
            try:
                traci.vehicle.setColor(str(backCar), (255,0,0)) # change color to red
            except:
                print("Can't draw")
            try:
                traci.vehicle.setColor(str(frontCar), (255,0,0)) # change color to red
            except:
                print("Can't draw")
