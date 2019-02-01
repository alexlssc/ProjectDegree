import os
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc

class OpenSpace:
    def __init__(id, length, middlePosition):
        self.id = id
        self.length = length
        self.middlePosition = middlePosition
        self.lockedSpace = False

    def get_id(self):
        return self.id

    def get_length(self):
        return self.length

    def set_length(self, double: new_length):
        self.get_length = new_length

    def get_middlePosition(self):
        return self.middlePosition

    def set_middlePosition(self, double: new_middlePosition):
        self.middlePosition = new_middlePosition

    def get_locked_state(self):
        return self.lockedSpace

    def set_locked_state(self, boolean: new_locked_state):
        self.lockedSpace = new_locked_state
