# import hashlib
# backCarID = bytes("245", encoding="utf-8")
# frontCarID = bytes("234", encoding="utf-8")
#
# backCarHash = hashlib.sha256(backCarID).hexdigest()
# frontCarHash = hashlib.sha256(frontCarID).hexdigest()
# bytesTotalHash = bytes(backCarHash + frontCarHash, encoding="utf-8")
# totalHash = hashlib.sha256(bytesTotalHash).hexdigest()
# print(totalHash)

from openSpaceClass import OpenSpace

os1 = OpenSpace(20, 10, '5', '8')
os2 = OpenSpace(30, 20, '4', '9')

listOs = [os1]

if os2 in listOs:
    print("YES")
else:
    print("NO")
