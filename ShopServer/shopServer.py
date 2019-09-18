from __future__ import print_function
import serial
import sys


#TODO Watch db file for changes and reload if necessary
shopDatabase = "ShopDatabase.txt"

items = {}
db = open(shopDatabase)

serialPort = None
if len(sys.argv) >= 2:
    serialPort = sys.argv[1]

for line in db:
    item = []

    if len(line.strip().split(',')) < 4:
        continue
        # print(line)
    for field in line.strip().split(','):
        item.append(field)

    items[item[0]] = [item[1],int(item[2]),int(item[3]) ] # {item[1],int(item[2]),int(item[3])}

print("Database...")
for key in items:
    print(items[key])

if serialPort is None:
    sys.exit()

ser = serial.Serial(serialPort,115200)


# TODO add addresses and message format
# Message format 
# i,id = info on id - resp = name,cost,quantity
# m,id,quantity = modify quantity of id, 

while True:
    original = ser.readline().strip()
    request = original.split(',')
    address = request[0]
    
    requestType = request[1]
    
    if requestType == 'i':
        if len(request) < 3:
            result = "400"
            print("Bad request \""+original+"\"")
        else:
            request = request[2]
            print("Info Request: "+request+" ==> ",end='')

            # Look up card id in 'database' and return HTTP 204 if nothing found
            result = items.get(request, None)
            
            if result == None:
                result = "204"
                print("Couldn't locate item")
            else:
                result = ', '.join(str(x) for x in result)
                print("Found: " + str(result))

        ser.write(str(result))

    elif requestType == 'm':
        if len(request) < 3:
            result = "400"

            print("Bad request \""+original+"\"")
        else:
            rfid = request[2]
            quantity = 0
            try: 
                quantity = int(request[3])
            except IndexError:
                quantity = 1

            print("Add Request: "+rfid+", "+str(quantity) + " ==> ",end='') 

            itm = items.get(rfid, None)

            if itm is not None:
                result = "200"
                itm[2] += quantity
                items[rfid] = itm
                print("Updated entry: "+str(itm )) 
            else:
                result = "204"
                print("Can't find item: "+rfid)

        ser.write(result)

    else:

        ser.write("400")
#open serial port
#respond to resquests
