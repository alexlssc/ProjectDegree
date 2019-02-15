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
import asyncio
from random import randint
from vehicleClass import Vehicle
from openSpaceClass import OpenSpace
from oneLaneClass import oneLaneObject
from allLanesClass import AllLanes
from datetime import datetime

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


listOfSimulation = []
numberOfSimulation = 1

sumoBinary = "/Users/alexandrelissac/Documents/SUMO/bin/sumo-gui"
for i in range(numberOfSimulation):
    randomSeed = str(randint(0,900))
    sumoCmd = [sumoBinary, "-c", "/Users/alexandrelissac/Desktop/Project/Simulation/Resources/FiveLanes/100v.sumocfg", "--lanechange-output", "lanechange.xml" ,"--seed", randomSeed , "--output-prefix", str(i),"--quit-on-end"]
    listOfSimulation.append(sumoCmd)

import traci
import traci.constants as tc

showGraph = False

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

def main():
    for idx, simulation in enumerate(listOfSimulation):
        traci.start(simulation)
        allLanes = AllLanes()
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            allLanes.updateAllLanes()
            print(traci.simulation.getCurrentTime())
            print(allLanes.get_vehicleOnLaneForSpecificLane(0))
            print(allLanes.get_openSpaceForSpecificLane(0))
            # updateVehicleData()
        traci.close(True)
    dirName = convertXMLintoCSV() # Convert and get directory of new folder
    time.sleep(3) # Wait for computer to save converted csv file
    analyseResults(dirName)

if __name__ == '__main__':
    main()
