# def checkIfCarFinished():
#     finishedVehicle = traci.simulation.getArrivedIDList()
#     if finishedVehicle:
#         for vehicle in finishedVehicle:
#             listOfVehicle[int(vehicle)].set_endTime(traci.simulation.getTime())

# def keepTrackOfNewVehicle():
#
#     # Keep track of loaded vehicle
#     listOfNewVehicleLoaded = traci.simulation.getLoadedIDList()
#     if listOfNewVehicleLoaded:
#         for vehicle in listOfNewVehicleLoaded:
#             listOfVehicle.append(Vehicle(vehicle,64))
#
#     # Keep track of all departing vehicle
#     listOfNewVehicleDeparted = traci.simulation.getDepartedIDList()
#     for vehicle in listOfNewVehicleDeparted:
#         listOfVehicle[int(vehicle)].set_startTime(traci.simulation.getTime())

# def displayResultsTimeTravelled(idx):
#     listOfTime = []
#     for vehicle in listOfVehicle:
#         listOfTime.append(vehicle.get_timeTravelled())
#     ws.write(idx, 0, np.median(listOfTime))
#     fit = stats.norm.pdf(sorted(listOfTime), np.mean(listOfTime), np.std(listOfTime))  #this is a fitting indeed
#     timeTravelledPlot = plt.figure(1)
#     plt.plot(sorted(listOfTime),fit,'-o')
#     plt.hist(sorted(listOfTime), density=True)
#     plt.ylabel('Percentage of cars')
#     plt.xlabel('Time travelled in second')
#     plt.title('Time travelled per vehicle in second')
#
# def displayAverageSpeedPerCar(idx):
#     listOfSpeedAverage = []
#     for vehicle in listOfVehicle:
#         listOfSpeedAverage.append(vehicle.get_average_speed())
#     ws.write(idx, 1, np.median(listOfSpeedAverage))
#     fit = stats.norm.pdf(sorted(listOfSpeedAverage), np.mean(listOfSpeedAverage), np.std(listOfSpeedAverage))  #this is a fitting indeed
#     averageSpeedPlot = plt.figure(2)
#     plt.plot(sorted(listOfSpeedAverage),fit,'-o')
#     plt.hist(sorted(listOfSpeedAverage), density=True)
#     plt.ylabel('Percentage of cars')
#     plt.xlabel('Average speed in m/s')
#     plt.title('Average speed per vehicle in m/s')
#
# def displayChangeLaneCount(idx):
#     listOfChangeLaneCount = []
#     for vehicle in listOfVehicle:
#         listOfChangeLaneCount.append(vehicle.get_changeLaneCount())
#     ws.write(idx, 2, np.median(listOfChangeLaneCount))
#     changeLaneCountPlot = plt.figure(3)
#     plt.hist(sorted(listOfChangeLaneCount), density=True)
#     plt.ylabel('Percentage of cars')
#     plt.xlabel('Amount of lane change')
#     plt.title('Amount of lane change per vehicle')
#
# def displayResults(idx):
#     displayResultsTimeTravelled(idx)
#     displayAverageSpeedPerCar(idx)
#     displayChangeLaneCount(idx)
#     if showGraph:
#         plt.show()

# def updateVehicleData():
#     listOfVehicleOnNetwork = traci.vehicle.getIDList()
#     for vehicle in listOfVehicleOnNetwork:
#         listOfVehicle[int(vehicle)].keepTrackOfLaneChange()
#         listOfVehicle[int(vehicle)].add_new_speed(traci.vehicle.getSpeed(vehicle))

# def keepTrackOfOpenSpace(numberOfLane):
#     ListOfLanes = []
#     for i in range(numberOfLane - 1):
#         listOfPosition = {}
#         listOfOpenSpace = {}
#         laneToCheck = "gneE0_" + str(i)
#         lengthLane = traci.lane.getLength(laneToCheck)
#         vehicleOnLane = traci.lane.getLastStepVehicleIDs(laneToCheck)
#         for vehicle in vehicleOnLane:
#             listOfPosition.update({vehicle : listOfVehicle[int(vehicle)].get_positionOnLane()})
#
#         previousId = None
#         previousPosition = None
#         count = 0
#         for id, position in listOfPosition.items():
#             lengthVehicle = listOfVehicle[int(id)].get_lengthVehicle()
#             if len(listOfPosition) == 1:
#                 distanceBeforeCar = position - (lengthVehicle / 2)
#                 distanceAfterCar = lengthLane - (position + ( lengthVehicle / 2 ))
#                 middlePositionDistanceBeforeCar = distanceBeforeCar / 2
#                 middlePositionDistanceAfterCar = lengthLane - (distanceAfterCar / 2)
#                 listOfOpenSpace.update({middlePositionDistanceBeforeCar : distanceBeforeCar})
#                 listOfOpenSpace.update({middlePositionDistanceAfterCar : distanceAfterCar})
#             else:
#                 if count == 0:
#                     distance = position - (lengthVehicle / 2)
#                     middlePosition = distance / 2
#                 elif count == len(listOfPosition) - 1:
#                     distance = lengthLane - (position + ( lengthVehicle / 2 ) )
#                     middlePosition = lengthLane - (distance / 2)
#                 else:
#                     distance = (position - (lengthVehicle / 2)) - (previousPosition + (listOfVehicle[int(previousId)].get_lengthVehicle() / 2))
#                     middlePosition = position - ((distance / 2) + (lengthVehicle / 2))
#                 listOfOpenSpace.update({middlePosition : distance})
#
#             previousId = id
#             previousPosition = position
#             count += 1
#         ListOfLanes.append(listOfOpenSpace)
