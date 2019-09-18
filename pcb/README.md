Fuses are the same as the default Uno fuses as we are using a 16Mhz resonator at 3.3v.

Fuses L:FF H:DE E:FD

avrdude -B 200 -C ../etc/avrdude.conf -c dragon_isp -p m328p -U lfuse:w:0xff:m -U hfuse:w:0xde:m -U efuse:w:0xfd:m

Then write the bootloader that is in this directory. You should then be able to program via an FTDI adapter as normal from the IDE.

Charge pump?
https://www.edn.com/design/integrated-circuit-design/4368224/Voltage-inverter-employs-PWM
