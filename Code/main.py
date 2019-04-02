import os
import sys
#import matplotlib.pyplot as plt
import numpy as np
#import scipy.stats as stats
import xlwt
import subprocess
import pathlib
import pandas as pd
import time
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
numberOfSimulation = 2
listOfSeed = []
useRandomValue = True

sumoBinary = "/Users/alexandrelissac/Documents/SUMO/bin/sumo"
for i in range(numberOfSimulation):
    if useRandomValue is False:
        sumoCmd = [sumoBinary, "-c", "../Resources/FiveLanes/1000v.sumocfg", "--lanechange-output", "lanechange.xml", "--tripinfo-output", "tripinfos.xml" ,"--seed", str(listOfSeed[i]) , "--output-prefix", str(i),"--start","--quit-on-end"]
        listOfSimulation.append(sumoCmd)
    else:
        randomSeed = str(randint(0,100000))
        #randomSeed = "511"
        listOfSeed.append(randomSeed)
        sumoCmd = [sumoBinary, "-c", "../Resources/FiveLanes/1000v.sumocfg", "--lanechange-output", "lanechange.xml", "--tripinfo-output", "tripinfos.xml" ,"--seed", randomSeed , "--output-prefix", str(i),"--start","--quit-on-end"]
        listOfSimulation.append(sumoCmd)

import traci
import traci.constants as tc

showGraph = False

def convertXMLintoCSV():
    dirName = "/Users/alexandrelissac/Desktop/Project/Simulation/Results/" + datetime.now().strftime('%d-%m-%Y_%H.%M.%S')
    pathlib.Path(dirName).mkdir(parents=True, exist_ok=True)
    for sim in range(numberOfSimulation):
        fileTargetLaneChange = str(sim) + "lanechange.xml"
        fileOutputLaneChange = str(sim) + "_lanechange.csv"
        fileTargetTripInfo = str(sim) + "tripinfos.xml"
        fileOutputTripInfo = str(sim) + "_tripinfos.csv"
        # subprocess.Popen(["xml2csv", "--input", "/Users/alexandrelissac/Desktop/Project/Simulation/Code/" + fileTargetTripInfo, "--output", dirName + "/" + fileOutputTripInfo, "--tag", "item"])
        subprocess.Popen(["python", "/Users/alexandrelissac/Documents/SUMO/tools/xml/xml2csv.py", "/Users/alexandrelissac/Desktop/Project/Simulation/Code/" + fileTargetLaneChange, "--output", dirName + "/" + fileOutputLaneChange])
        subprocess.Popen(["python", "/Users/alexandrelissac/Documents/SUMO/tools/xml/xml2csv.py", "/Users/alexandrelissac/Desktop/Project/Simulation/Code/" + fileTargetTripInfo, "--output", dirName + "/" + fileOutputTripInfo])
    return dirName

def analyseResults(dirName):
    count = 0
    file_exist = True
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Result Simulation')
    ws.write(0,0, "Simulation Number")
    ws.write(0,1, "Average Duration Trip")
    ws.write(0,2, "Std Average Duration Trip")
    ws.write(0,3, "Number of Lane Change")
    ws.write(0,4, "Average Duration Trip LCC")
    ws.write(0,5, "Average Duration Trip No LCC")
    ws.write(0,6, "TimeLoss LCC")
    ws.write(0,7, "TimeLoss No LCC")
    ws.write(0,8, "Seed")


    listOfAverageDurationTrip = []
    listOfLaneChange = []
    listAverageTimeLCC = []
    listAverageTimeNoLCC = []
    listAverageTimeLossLCC = []
    listAverageTimeLossNoLCC = []
    keepTrackAverageLCC = []
    keepTrackAverageNoLCC = []
    keepTrackAverageTimeLossLCC = []
    keepTrackAverageTimeLossNoLCC = []

    while(file_exist):
        fileDir = dirName + "/" + str(count) + "_tripinfos.csv"
        lcDir = dirName + "/" + str(count) + "_lanechange.csv"
        if not os.path.exists(fileDir):
            break
        try:
            #Average duration trip
            tripCsv = pd.read_csv(fileDir, delimiter=';')
            currentAverageDurationTrip = np.mean(tripCsv['tripinfo_duration'])
            stdDurationTrip = np.std(tripCsv['tripinfo_duration'])
            listOfAverageDurationTrip.append(currentAverageDurationTrip)
            # Number of lane change
            lcCsv = pd.read_csv(lcDir, delimiter=';')
            numberOfLaneChange = len(lcCsv['change_id'])
            listOfLaneChange.append(numberOfLaneChange)

            #Average duration for LCC and non-LCC
            allLCID = lcCsv.change_id.unique()
            for idx,row in tripCsv.iterrows():
                if tripCsv.loc[idx, 'tripinfo_id'] in allLCID:
                    listAverageTimeLCC.append(tripCsv.loc[idx,'tripinfo_duration'])
                    listAverageTimeLossLCC.append(tripCsv.loc[idx,'tripinfo_timeLoss'])
                else:
                    listAverageTimeNoLCC.append(tripCsv.loc[idx,'tripinfo_duration'])
                    listAverageTimeLossNoLCC.append(tripCsv.loc[idx,'tripinfo_timeLoss'])

            averageDurationLCC = np.mean(listAverageTimeLCC)
            averageDurationNoLCC = np.mean(listAverageTimeNoLCC)
            keepTrackAverageLCC.append(averageDurationLCC)
            keepTrackAverageNoLCC.append(averageDurationNoLCC)
            averageTimeLossLCC = np.mean(listAverageTimeLossLCC)
            averageTimeLossNoLCC = np.mean(listAverageTimeLossNoLCC)
            keepTrackAverageTimeLossLCC.append(averageTimeLossLCC)
            keepTrackAverageTimeLossNoLCC.append(averageTimeLossNoLCC)

            ws.write(count + 1, 0, str(count))
            ws.write(count + 1, 1, str(currentAverageDurationTrip))
            ws.write(count + 1, 2, str(stdDurationTrip))
            ws.write(count + 1, 3, str(numberOfLaneChange))
            ws.write(count + 1, 4, str(averageDurationLCC))
            ws.write(count + 1, 5, str(averageDurationNoLCC))
            ws.write(count + 1, 6, str(averageTimeLossLCC))
            ws.write(count + 1, 7, str(averageTimeLossNoLCC))
            ws.write(count + 1, 8, str(listOfSeed[count]))


            count += 1
        except:
            print("ERROR: " + str(count))
            file_exist = False
            break

    ws.write(count + 1, 0, "Total Average")
    ws.write(count + 1, 1, str(np.mean(listOfAverageDurationTrip)))
    ws.write(count + 1, 3, str(np.mean(listOfLaneChange)))
    ws.write(count + 1, 4, str(np.mean(keepTrackAverageLCC)))
    ws.write(count + 1, 5, str(np.mean(keepTrackAverageNoLCC)))
    ws.write(count + 1, 6, str(np.mean(keepTrackAverageTimeLossLCC)))
    ws.write(count + 1, 7, str(np.mean(keepTrackAverageTimeLossNoLCC)))
    wb.save(dirName + '/results.xls')

def main():
    for idx, simulation in enumerate(listOfSimulation):
        traci.start(simulation)
        allLanes = AllLanes()
        print("SIMULATION " + str(idx) + " / SEED: " + str(listOfSeed[idx]))
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            allLanes.handlesAllManoeuvres()
            if traci.simulation.getCurrentTime() > 10000:
                allLanes.checkCarDesiringLaneChange()
        traci.close()
    dirName = convertXMLintoCSV() # Convert and get directory of new folder
    print(dirName)
    time.sleep(3) # Wait for computer to save converted csv file
    analyseResults(dirName)

if __name__ == '__main__':
    main()
