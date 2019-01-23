import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from vehicleClass import Vehicle

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "/Users/alexandrelissac/Documents/SUMO/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "/Users/alexandrelissac/Desktop/Project/Simulation/Resources/FiveLanes/100v.sumocfg"]

import traci
import traci.constants as tc

def checkIfCarFinished():
    finishedVehicle = traci.simulation.getArrivedIDList()
    if finishedVehicle:
        for vehicle in finishedVehicle:
            listOfVehicle[int(vehicle)].set_endTime(traci.simulation.getTime())

def keepTrackOfNewVehicle():

    # Keep track of loaded vehicle
    listOfNewVehicleLoaded = traci.simulation.getLoadedIDList()
    if listOfNewVehicleLoaded:
        for vehicle in listOfNewVehicleLoaded:
            listOfVehicle.append(Vehicle(vehicle))

    # Keep track of all departed vehicle
    listOfNewVehicleDeparted = traci.simulation.getDepartedIDList()
    for vehicle in listOfNewVehicleDeparted:
        listOfVehicle[int(vehicle)].set_startTime(traci.simulation.getTime())

def displayResultsTimeTravelled():
    listOfTime = []
    for vehicle in listOfVehicle:
        listOfTime.append(vehicle.get_timeTravelled())
    fit = stats.norm.pdf(sorted(listOfTime), np.mean(listOfTime), np.std(listOfTime))  #this is a fitting indeed
    timeTravelledPlot = plt.figure(1)
    plt.plot(sorted(listOfTime),fit,'-o')
    plt.hist(sorted(listOfTime), density=True)
    plt.ylabel('Probability')
    plt.xlabel('Time travelled in tic')
    plt.title('Time travelled per vehicle in tic')

def displayAverageSpeedPerCar():
    listOfSpeedAverage = []
    for vehicle in listOfVehicle:
        listOfSpeedAverage.append(vehicle.get_average_speed())
    fit = stats.norm.pdf(sorted(listOfSpeedAverage), np.mean(listOfSpeedAverage), np.std(listOfSpeedAverage))  #this is a fitting indeed
    averageSpeedPlot = plt.figure(2)
    plt.plot(sorted(listOfSpeedAverage),fit,'-o')
    plt.hist(sorted(listOfSpeedAverage), density=True)
    plt.ylabel('Probability')
    plt.xlabel('Average speed in m/s')
    plt.title('Average speed per vehicle in m/s')

def displayResults():
    displayResultsTimeTravelled()
    displayAverageSpeedPerCar()
    plt.show()

def keepTrackOfSpeed():
    listOfVehicleOnNetwork = traci.vehicle.getIDList()
    for vehicle in listOfVehicleOnNetwork:
        listOfVehicle[int(vehicle)].add_new_speed(traci.vehicle.getSpeed(vehicle))

traci.start(sumoCmd)
vehID = '0'
# traci.vehicle.setColor(vehID, (255, 0, 0))
# traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_LANE_ID))
listOfVehicle = []
print(traci.simulation.getTime())
while traci.simulation.getMinExpectedNumber() > 0:
    keepTrackOfNewVehicle()
    traci.simulationStep()
    keepTrackOfSpeed()
    checkIfCarFinished()

displayResults()
# for vehicle in listOfVehicle:
#     print(vehicle.get_id())
#     print(vehicle.get_listSpeed())
traci.close(False)
