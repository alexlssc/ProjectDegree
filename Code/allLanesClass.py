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
        self.listOfYCoordinate = [-14.85, -11.55, -8.25, -4.45, -1.65] # YCoordinate of simulation to draw space's middle position
        self.allLockedSpace = []
        self.listOfLockedVehicle = []
        for i in range(self.numberOfLane):
            laneId = "gneE0_" + str(i)
            self.listOfLane.append(oneLaneObject(laneId, self.listOfYCoordinate[i]))

    # Detect new vehicle loaded and create a Vehicle object with them
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

    # Runs all functions that handle open space
    def updateAllLanes(self):
        listArrived = traci.simulation.getArrivedIDList()
        for lane in self.listOfLane:
            lane.updateOpenSpace(listArrived) # Keep track of all open space
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

    # Lock target space
    def triggerLockedSpace(self, laneId):
        self.listOfLane[laneId].startLockingSpace(4)

    # Trigger random left change
    def triggerLeftChangeLane(self):
        listOfVehicleOnLane = self.listOfLane[0].get_vehicleOnLane()
        targetVehicle = listOfVehicleOnLane[3] # Get a vehicle on lane 0
        self.listOfLockedVehicle.append(targetVehicle) # Keep track of the vehicle
        traci.vehicle.setColor(str(targetVehicle), (0,0,255)) #Set its color for GUI
        traci.gui.trackVehicle('View #0', targetVehicle) # Center camera on it
        nearestOpenSpace = self.findNearestSpace(targetVehicle, self.listOfLane[1].get_currentOpenSpace()) # Find its best nearest open space
        self.listOfLane[1].add_preparingLockedSpace(nearestOpenSpace) # Prepare that open Space

    # find best nearest open space and return it
    def findNearestSpace(self, vehID, ListOpenSpaces):
        # Get vehicle properties
        vehiclePosition = traci.vehicle.getLanePosition(vehID)
        vehicleLength = traci.vehicle.getLength(vehID)
        # Initialise fitness score and fitness value
        shortestDistanceScore = 999999
        closestMiddlePointSpace = None
        bestNonAdjacentSpace = None
        for space in ListOpenSpaces:
            spaceMiddlePosition = space.get_middlePosition()
            distance = math.sqrt((vehiclePosition - spaceMiddlePosition) ** 2) # Get the distance between car and middle point
            backCar = space.get_backCar()
            frontCar = space.get_frontCar()
            # get vehicle speed
            if backCar is not "start":
                backCarSpeed = traci.vehicle.getSpeed(space.get_backCar())
            else:
                backCarSpeed = 0
            if frontCar is not "end":
                frontCarSpeed = traci.vehicle.getSpeed(space.get_frontCar())
            else:
                frontCarSpeed = 0
            # Use vehicle speed to detect safe distance between cars
            # In this case, safe distance = braking distance
            backCarSafeDistance = (backCarSpeed ** 2) / (254 * 0.7 )
            frontCarSafeDistance = (frontCarSpeed ** 2) / (254 * 0.7)
            safeDistance = backCarSafeDistance + frontCarSafeDistance
            if distance < shortestDistanceScore: # If new distance shorter than currentBest
                print("ID: " + space.get_id() + " / " + str(distance) + " / " + str(space.get_length() - safeDistance) + " / " + str(spaceMiddlePosition) + " / " + str(space.get_length() / 2) + " / " + str(space.get_growth()))
                if (space.get_length() - safeDistance) >= 5: # check if car has enough room to fit in open space
                    # Yes, this space become currentBest
                    shortestDistanceScore = distance
                    closestMiddlePointSpace = space
                    bestNonAdjacentSpace = space
                else:
                    # Check if space could still be considered even though not enough room for car
                    # Check if the space growth needed to welcome car is not bigger than 30 and if the space is currently growing
                    # get_growth() is the difference between the speed of the backCar and the frontCar
                    # if backCarSpeed > frontCarSpeed than space is shrinking otherwise it is growing
                    if space.get_length() - safeDistance > -30 and space.get_growth() == 1:
                        # yes, space can be considered and become currentBest
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
            distance = abs(carPosition - middlePositionOpenSpace) # get the distance between car and space's middle position
            # print("carPosition:" + str(carPosition) + " / middlePositionOpenSpace: " + str(middlePositionOpenSpace) + " / D:" + str(distance))
            print("Accepted distance: " + str(targetOpenSpace.get_landingLength()) + " / distance:" + str(distance))

            # Verify that cars is close enough to the space's middlePosition to insert into itself into space
            if distance < targetOpenSpace.get_landingLength():
                # print("Lane change occured at " + traci.simulation.getCurrentTime() )
                # print("Change Lane done")
                traci.vehicle.changeLaneRelative(self.listOfLockedVehicle[0], 1, 2.0) # Start manoeuvre to change lane
                traci.vehicle.setSpeed(self.listOfLockedVehicle[0], -1) # give back to sumo the control of car's speed
                self.listOfLockedVehicle.remove(self.listOfLockedVehicle[0]) # remove vehicle from locked vehicle
                self.unlockSpace(targetOpenSpace) # remove open space from list of locked space
            else: # Car is too far from middle point to insert
                if (carPosition - middlePositionOpenSpace) > 0: # Car is ahead of space's middle position
                    # Reduce car speed to meet space's middle position
                    traci.vehicle.setSpeed(self.listOfLockedVehicle[0], traci.vehicle.getSpeed(self.listOfLockedVehicle[0]) - 0.2)
                else: # Car is behind space's middle position
                    # Increase speed to meet space's middle position
                    traci.vehicle.setSpeed(self.listOfLockedVehicle[0], traci.vehicle.getSpeed(self.listOfLockedVehicle[0]) + 0.2)

    # Remove space from locked space's list
    def unlockSpace(self, space):
        self.allLockedSpace.remove(space)
        for lane in self.listOfLane:
            lane.unlockSpace(space)

    # main function that handles everything in this class
    def handlesAllManoeuvres(self):
        self.keepTrackOfNewVehicle()
        self.updateAllLanes()
        self.checkIfVehicleCanChangeLane()
