# import hashlib
# backCarID = bytes("245", encoding="utf-8")
# frontCarID = bytes("234", encoding="utf-8")
#
# backCarHash = hashlib.sha256(backCarID).hexdigest()
# frontCarHash = hashlib.sha256(frontCarID).hexdigest()
# bytesTotalHash = bytes(backCarHash + frontCarHash, encoding="utf-8")
# totalHash = hashlib.sha256(bytesTotalHash).hexdigest()
# print(totalHash)

def predictLockedSpaceLength(self):
    backCarPosition = 5
    frontCarPosition = 20
    backCarSpeed = 23
    frontCarSpeed = 20
    carDecel = 4.5
    carAccel = 2.5
