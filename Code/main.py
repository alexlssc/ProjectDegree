import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

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
        for car in finishedVehicle:
            timeFinishedVehicle.update({car : (traci.simulation.getTime() - startingVehicle[car])})

def keepTrackOfNewVehicle():
    listOfNewVehicle = traci.simulation.getDepartedIDList()
    for vehicle in listOfNewVehicle:
        startingVehicle.update({vehicle : traci.simulation.getTime()})

def displayResultsTimeTravelled():
    listOfTime = []
    for time in timeFinishedVehicle.values():
        listOfTime.append(time)
    fit = stats.norm.pdf(sorted(listOfTime), np.mean(listOfTime), np.std(listOfTime))  #this is a fitting indeed
    plt.plot(sorted(listOfTime),fit,'-o')
    plt.hist(sorted(listOfTime), density=True)
    plt.ylabel('Probability')
    plt.xlabel('Time travelled in tic')
    plt.title('Time travelled per vehicle in tic')
    plt.show()

traci.start(sumoCmd)
vehID = '0'
traci.vehicle.setColor(vehID, (255, 0, 0))
traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_LANE_ID))
startingVehicle = {}
timeFinishedVehicle = {}
finishedVehicle = []
print(traci.simulation.getTime())
while traci.simulation.getMinExpectedNumber() > 0:
    keepTrackOfNewVehicle()
    traci.simulationStep()
    checkIfCarFinished()
print(timeFinishedVehicle)
displayResultsTimeTravelled()
traci.close(False)
