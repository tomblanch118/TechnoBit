from microbit import *
import utime
import radio

myAddress = 10


i2c.init(freq=1000000, sda=pin20, scl=pin19)

radio.on()

# Store previous RFID card in case we want to do some debounce type stuff
lastRfidCard = ""

def writeToLCDScreen(line, text):

    if line >= 2:
        text = b'\x02'+bytes(text[:16], 'utf-8')
    if line <= 1:
        text = b'\x01'+bytes(text[:16], 'utf-8')

    i2c.write(8, text)

def sendPacket(rfid):
    radio.send(str(myAddress)+",i,"+rfid)

    # Wait up to 1.5 seconds for response
    startTime = utime.ticks_ms()

    data = False

    while (utime.ticks_diff(utime.ticks_ms(), startTime)) < 1500:

        incoming = radio.receive()

        # if we have received something, check if it is for us
        if incoming is not None:

            address = incoming.split(",")[0]
            if str(address) == str(myAddress):
                # print(address+" is me!")
                data = True
                break

    # first check for status codes
    if data is True:
        return incoming.split(',')[1:]
    else:
        return [408]

while True:

    # Try to talk to the RFID
    try:
        rfidCard = str(i2c.read(8, 8), 'utf-8')

        if rfidCard != "00000000" and lastRfidCard != rfidCard:

            # Print out the card ID we just read
            print("card id = "+rfidCard)

            writeToLCDScreen(1, "ID:"+rfidCard)

            # Now make a packet
            response = sendPacket(rfidCard)

            if str(response[0]) == '200':
                if len(response) > 1:
                    writeToLCDScreen(2,str(response[1]))
                    # Set the LED color
                    i2c.write(8, b'\x03\x00\x55\x00')
            else:
                writeToLCDScreen(2, "Error: "+str(response[0]))
                # Set the LED color
                i2c.write(8, b'\x03\x55\x00\x00')




    # RFID reader can't be reached, oh no!
    except OSError:
        print("cant reach rfid reader")

    utime.sleep_ms(1000)