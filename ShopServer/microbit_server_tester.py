import radio
import utime
from microbit import uart, sleep

myAddress = "15"

radio.on()

uart.init(115200)
uart.write("Sending data\n")


uart.write("TEST\n")
while True:
    uart.write("Sending... \n")
    radio.send(myAddress+",i,bbabaf21")
    startTime = utime.ticks_ms()
    incoming = None
    while (utime.ticks_diff(utime.ticks_ms(), startTime)) < 1000:
        incoming = radio.receive()

        if incoming is not None and incoming.split(',')[0] == myAddress:
            # incoming.split(',')[0] == myAddress:
            break
    if incoming is None:
        print("error")
    else:
        print(incoming.split(',')[1])
    sleep(1000)
    # radio.send(myAddress+",a,fd15f3ea,1")
    # sleep(1000)