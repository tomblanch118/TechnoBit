# TechnoBit
This project aims to allow easy interaction between a BBC Microbit and an RFID card reader. A custom PCB has been created that uses an Atmega 328p to interface between the Microbit and an MFRC522 RFID reader. Communication between the Microbit and the Atmega is over an 3.3 V i2c bus and communication between the RFID reader and the Atmega is via SPI. Details of the PCB (including eagle schematic/board layout) and the firmware / bootloader for the Atmega are in the boards directory.

Also included on the board is a header for a 2 row 16 character LCD display, a footprint for an RGB LED and a breakout of all of the Microbits pins.

The design allows the Microbit to still use all of its:
- Buttons
- Sensors
- Radio
- The LED matrix
- The serial port.

An example micropython program is provided to communicate with the RGB LED, LCD screen and RFID reader.

There is also a more comprehensive "shop" example, see the shopServer directory. In this example a Python program runs as a 'database server' on a PC and connects to a Microbit to allow wireless communication. A TechnoBit can send RFID card ids to this 'database server' wirelessly and either increment/decrement the amount held in the database or receive Price, Stock and Name information. 
