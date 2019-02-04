import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import xlwt
import subprocess
import pathlib
import pandas as pd
import time
from random import randint
from vehicleClass import Vehicle
from datetime import datetime

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


listOfSimulation = []
numberOfSimulation = 5

sumoBinary = "/Users/alexandrelissac/Documents/SUMO/bin/sumo-gui"
for i in range(numberOfSimulation):
    randomSeed = str(randint(0,900))
    sumoCmd = [sumoBinary, "-c", "/Users/alexandrelissac/Desktop/Project/Simulation/Resources/FiveLanes/100v.sumocfg", "--lanechange-output", "lanechange.xml" ,"--seed", randomSeed , "--output-prefix", str(i), "--start", "--quit-on-end"]
    listOfSimulation.append(sumoCmd)

import traci
import traci.constants as tc

showGraph = False

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

    # Keep track of all departing vehicle
    listOfNewVehicleDeparted = traci.simulation.getDepartedIDList()
    for vehicle in listOfNewVehicleDeparted:
        listOfVehicle[int(vehicle)].set_startTime(traci.simulation.getTime())

def displayResultsTimeTravelled(idx):
    listOfTime = []
    for vehicle in listOfVehicle:
        listOfTime.append(vehicle.get_timeTravelled())
    ws.write(idx, 0, np.median(listOfTime))
    fit = stats.norm.pdf(sorted(listOfTime), np.mean(listOfTime), np.std(listOfTime))  #this is a fitting indeed
    timeTravelledPlot = plt.figure(1)
    plt.plot(sorted(listOfTime),fit,'-o')
    plt.hist(sorted(listOfTime), density=True)
    plt.ylabel('Percentage of cars')
    plt.xlabel('Time travelled in second')
    plt.title('Time travelled per vehicle in second')

def displayAverageSpeedPerCar(idx):
    listOfSpeedAverage = []
    for vehicle in listOfVehicle:
        listOfSpeedAverage.append(vehicle.get_average_speed())
    ws.write(idx, 1, np.median(listOfSpeedAverage))
    fit = stats.norm.pdf(sorted(listOfSpeedAverage), np.mean(listOfSpeedAverage), np.std(listOfSpeedAverage))  #this is a fitting indeed
    averageSpeedPlot = plt.figure(2)
    plt.plot(sorted(listOfSpeedAverage),fit,'-o')
    plt.hist(sorted(listOfSpeedAverage), density=True)
    plt.ylabel('Percentage of cars')
    plt.xlabel('Average speed in m/s')
    plt.title('Average speed per vehicle in m/s')

def displayChangeLaneCount(idx):
    listOfChangeLaneCount = []
    for vehicle in listOfVehicle:
        listOfChangeLaneCount.append(vehicle.get_changeLaneCount())
    ws.write(idx, 2, np.median(listOfChangeLaneCount))
    changeLaneCountPlot = plt.figure(3)
    plt.hist(sorted(listOfChangeLaneCount), density=True)
    plt.ylabel('Percentage of cars')
    plt.xlabel('Amount of lane change')
    plt.title('Amount of lane change per vehicle')

def displayResults(idx):
    displayResultsTimeTravelled(idx)
    displayAverageSpeedPerCar(idx)
    displayChangeLaneCount(idx)
    if showGraph:
        plt.show()

def updateVehicleData():
    listOfVehicleOnNetwork = traci.vehicle.getIDList()
    for vehicle in listOfVehicleOnNetwork:
        listOfVehicle[int(vehicle)].keepTrackOfLaneChange()
        listOfVehicle[int(vehicle)].add_new_speed(traci.vehicle.getSpeed(vehicle))

def keepTrackOfOpenSpace(numberOfLane):
    ListOfLanes = []
    for i in range(numberOfLane - 1):
        listOfPosition = {}
        listOfOpenSpace = {}
        laneToCheck = "gneE0_" + str(i)
        lengthLane = traci.lane.getLength(laneToCheck)
        vehicleOnLane = traci.lane.getLastStepVehicleIDs(laneToCheck)
        for vehicle in vehicleOnLane:
            listOfPosition.update({vehicle : listOfVehicle[int(vehicle)].get_positionOnLane()})

        previousId = None
        previousPosition = None
        count = 0
        for id, position in listOfPosition.items():
            lengthVehicle = listOfVehicle[int(id)].get_lengthVehicle()
            if len(listOfPosition) == 1:
                distanceBeforeCar = position - (lengthVehicle / 2)
                distanceAfterCar = lengthLane - (position + ( lengthVehicle / 2 ))
                middlePositionDistanceBeforeCar = distanceBeforeCar / 2
                middlePositionDistanceAfterCar = lengthLane - (distanceAfterCar / 2)
                listOfOpenSpace.update({middlePositionDistanceBeforeCar : distanceBeforeCar})
                listOfOpenSpace.update({middlePositionDistanceAfterCar : distanceAfterCar})
            else:
                if count == 0:
                    distance = position - (lengthVehicle / 2)
                    middlePosition = distance / 2
                elif count == len(listOfPosition) - 1:
                    distance = lengthLane - (position + ( lengthVehicle / 2 ) )
                    middlePosition = lengthLane - (distance / 2)
                else:
                    distance = (position - (lengthVehicle / 2)) - (previousPosition + (listOfVehicle[int(previousId)].get_lengthVehicle() / 2))
                    middlePosition = position - ((distance / 2) + (lengthVehicle / 2))
                listOfOpenSpace.update({middlePosition : distance})

            previousId = id
            previousPosition = position
            count += 1
        ListOfLanes.append(listOfOpenSpace)

def convertXMLintoCSV():
    dirName = "/Users/alexandrelissac/Desktop/Project/Simulation/Results/" + datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
    pathlib.Path(dirName).mkdir(parents=True, exist_ok=True)
    for sim in range(numberOfSimulation):
        fileTargetLaneChange = str(sim) + "lanechange.xml"
        fileOutputLaneChnage = str(sim) + "_lanechange.csv"
        fileTargetTripInfo = str(sim) + "tripinfos.xml"
        fileOutputTripInfo = str(sim) + "_tripinfos.csv"
        subprocess.Popen(["python", "/Users/alexandrelissac/Documents/SUMO/tools/xml/xml2csv.py", "/Users/alexandrelissac/Desktop/Project/Simulation/Code/" + fileTargetLaneChange, "--output", dirName + "/" + fileOutputLaneChnage])
        subprocess.Popen(["python", "/Users/alexandrelissac/Documents/SUMO/tools/xml/xml2csv.py", "/Users/alexandrelissac/Desktop/Project/Simulation/Resources/FiveLanes/" + fileTargetTripInfo, "--output", dirName + "/" + fileOutputTripInfo])
    return dirName

def analyseResults(dirName):
    count = 0
    file_exist = True
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Result Simulation')
    ws.write(0,0, "Simulation Number")
    ws.write(0,1, "Average Duration Trip")
    listOfAverageDurationTrip = []

    while(file_exist):
        fileDir = dirName + "/" + str(count) + "_tripinfos.csv"
        if not os.path.exists(fileDir):
            break
        try:
            currentCsv = pd.read_csv(fileDir, delimiter=';')
            currentAverageDurationTrip = np.mean(currentCsv['tripinfo_duration'])
            listOfAverageDurationTrip.append(currentAverageDurationTrip)
            ws.write(count + 1, 0, str(count))
            ws.write(count + 1, 1, str(currentAverageDurationTrip))
            count += 1
        except:
            print("ERROR: " + str(count))
            file_exist = False
            break

    ws.write(count + 1, 0, "Total Average")
    ws.write(count + 1, 1, str(np.mean(listOfAverageDurationTrip)))
    wb.save(dirName + '/results.xls')

for idx, simulation in enumerate(listOfSimulation):
    traci.start(simulation)
    listOfVehicle = []
    numberOfLane = traci.lane.getIDCount()
    while traci.simulation.getMinExpectedNumber() > 0:
        keepTrackOfNewVehicle()
        traci.simulationStep()
        keepTrackOfOpenSpace(numberOfLane)
        updateVehicleData()
        checkIfCarFinished()

    #displayResults(idx)
    traci.close(True)
dirName = convertXMLintoCSV()
time.sleep(5) # Wait for computer to save converted csv file
analyseResults(dirName)
