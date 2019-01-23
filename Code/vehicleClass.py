class Vehicle:
    def __init__(self,id):
        self.id = id
        self.listSpeed = []
        self.startTime = None
        self.endTime = None

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def add_new_speed(self, new_speed):
        self.listSpeed.append(new_speed)

    def get_average_speed(self):
        return sum(self.listSpeed) / len(self.listSpeed)

    def get_listSpeed(self):
        return self.listSpeed

    def set_startTime(self, startTime):
        self.startTime = startTime

    def set_endTime(self, endTime):
        self.endTime = endTime

    def get_timeTravelled(self):
        return self.endTime - self.startTime
