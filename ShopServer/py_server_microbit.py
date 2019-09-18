import radio
from microbit import uart, sleep
radio.on()

uart.init(115200)

while True:
    incoming = radio.receive()

    if incoming is not None:
        uart.write(str(incoming) + "\n")

        address = incoming.split(',')[0]

        try:
            int(address)
            sleep(10)

            details = uart.readline()

            if details is None:
                # send HTTP timeout code
                radio.send(address+",408")
            else:
                radio.send(address+","+str(details,"utf-8") )
        except ValueError:
            sleep(1)



    sleep(1)