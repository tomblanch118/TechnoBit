from microbit import *

uart.init(9600, tx=pin8, rx=pin16)

while True:

    while pin0.read_digital() != 1:
        continue

    sleep(50)
    data = uart.readline().strip()
    uart.init(115200)
    print(data)
    uart.init(9600, tx=pin8, rx=pin16)
    sleep(50)