# import hashlib
# backCarID = bytes("245", encoding="utf-8")
# frontCarID = bytes("234", encoding="utf-8")
#
# backCarHash = hashlib.sha256(backCarID).hexdigest()
# frontCarHash = hashlib.sha256(frontCarID).hexdigest()
# bytesTotalHash = bytes(backCarHash + frontCarHash, encoding="utf-8")
# totalHash = hashlib.sha256(bytesTotalHash).hexdigest()
# print(totalHash)

test = "gneE0_4"
character = test[len(test) - 1]
print(character)
