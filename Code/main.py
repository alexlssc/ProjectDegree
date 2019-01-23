import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from random import randint
from vehicleClass import Vehicle

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

listOfSimulation = []

sumoBinary = "/Users/alexandrelissac/Documents/SUMO/bin/sumo-gui"
for i in range(1):
    randomSeed = str(randint(0,900))
    sumoCmd = [sumoBinary, "-c", "/Users/alexandrelissac/Desktop/Project/Simulation/Resources/FiveLanes/500v.sumocfg", "--seed", randomSeed]
    listOfSimulation.append(sumoCmd)

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
            listOfVehicle.append(Vehicle(vehicle,64))

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
    plt.xlabel('Time travelled in second')
    plt.title('Time travelled per vehicle in second')

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

def displayChangeLaneCount():
    listOfChangeLaneCount = []
    for vehicle in listOfVehicle:
        listOfChangeLaneCount.append(vehicle.get_changeLaneCount())
    changeLaneCountPlot = plt.figure(3)
    plt.hist(sorted(listOfChangeLaneCount), density=True)
    plt.ylabel('Probability')
    plt.xlabel('Average amount of lane change')
    plt.title('Average amount of lane change per vehicle')

def displayResults():
    displayResultsTimeTravelled()
    displayAverageSpeedPerCar()
    displayChangeLaneCount()
    plt.show()

def updateVehicleData():
    listOfVehicleOnNetwork = traci.vehicle.getIDList()
    for vehicle in listOfVehicleOnNetwork:
        listOfVehicle[int(vehicle)].keepTrackOfLaneChange()
        listOfVehicle[int(vehicle)].add_new_speed(traci.vehicle.getSpeed(vehicle))

for simulation in listOfSimulation:
    traci.start(simulation)
    vehID = '0'
    listOfVehicle = []
    print(traci.simulation.getTime())
    while traci.simulation.getMinExpectedNumber() > 0:
        keepTrackOfNewVehicle()
        traci.simulationStep()
        updateVehicleData()
        checkIfCarFinished()

    displayResults()
    traci.close(False)
