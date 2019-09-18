from microbit import spi
from microbit import pin16
from microbit import pin8
from microbit import pin13
from microbit import pin14
from microbit import pin15
import utime


RST_PIN = pin16
CS_PIN = pin8
# IRQ_PIN = 2

CommandRegister = 0x01 << 1
ComIEnRegister = 0x02 << 1
DivIEnRegister = 0x03 << 1
ComIrqRegister = 0x04 << 1
DivIrqRegister = 0x05 << 1
ErrorRegister = 0x06 << 1
Status1Register = 0x07 << 1
Status2Register = 0x08 << 1
FIFODataRegister = 0x09 << 1
FIFOLevelRegister = 0x0A << 1
WaterLevelRegister = 0x0B << 1
ControlRegister = 0x0C << 1
BitFramingRegister = 0x0D << 1
TxModeRegister = 0x12 << 1
RxModeRegister = 0x13 << 1
ModWidthRegister = 0x24 << 1
TModeRegister = 0x2A << 1
TPrescalarRegister = 0x2B << 1
TReloadRegisterH = 0x2C << 1
TReloadRegisterL = 0x2D << 1
TxASKRegister = 0x15 << 1
ModeRegister = 0x11 << 1
TxControlRegister = 0x14 << 1
VersionRegister = 0x37 << 1
CollRegister = 0x0E << 1
CRCResultRegisterH = 0x21 << 1
CRCResultRegisterL = 0x22 << 1

STATUS_OK = 0
STATUS_ERROR = 1
STATUS_COLLISION = 2
STATUS_TIMEOUT = 3
STATUS_NO_ROOM = 4
STATUS_INTERNAL_ERROR = 5
STATUS_INVALID = 6
STATUS_CRC_WRONG = 7
STATUS_MIFARE_NACK = 8

PICC_CMD_REQA = 0x26

PCD_Transceive = 0x0C
PCD_Idle = 0x00
PCD_CalcCRC = 0x03


def NFC_read_register(register):
    CS_PIN.write_digital(0)
    data = bytearray([0x80 | register])
    spi.write(data)
    # spi.write(0x00)#maybe?
    value = 0xff
    value = spi.read(1)
    CS_PIN.write_digital(1)
    return int(value[0])


def NFC_write_register(register, value):
    bregister = bytearray([register])
    bvalue = bytearray([value])
    CS_PIN.write_digital(0)
    spi.write(bregister)
    # need to think about writing a loop for multi byte write
    spi.write(bvalue)
    CS_PIN.write_digital(1)


def NFC_antenna_on():
    value = NFC_read_register(TxControlRegister)
    # value = int(value[0])
    if ((value & 0x03) != 0x03):
        NFC_write_register(TxControlRegister, value | 0x03)

    value = NFC_read_register(TxControlRegister)

def NFC_dump_version():
    version = NFC_read_register(VersionRegister)
    # version = int(version[0])

    print("Firmware Version: "+(str(hex(version))))
    if version == 0x88:
        print("clone")
    elif version == 0x90:
        print("v0.0")
    elif version == 0x91:
        print("v1.0")
    elif version == 0x92:
        print("v2.0")
    elif version == 0x12:
        print("counterfeit chip")
    else:
        print("unknown")

def NFC_setup():

    # display.off()
    spi.init(baudrate=1000000, bits=8, mode=0, sclk=pin13, mosi=pin15,
             miso=pin14)

    print("SPI Init")
    CS_PIN.write_digital(1)

    if RST_PIN.read_digital() == 0:
        RST_PIN.write_digital(0)
        # give a few microseconds for nfc to reset
        utime.sleep_us(2)
        RST_PIN.write_digital(1)
        utime.sleep_us(50000)

    print("version:")
    byt = NFC_read_register(0x37 << 1)
    print(byt)

    NFC_write_register(TxModeRegister, 0x00)
    NFC_write_register(RxModeRegister, 0x00)
    # Reset ModWidthReg
    NFC_write_register(ModWidthRegister, 0x26)
    # TAuto=1; timer starts automatically at the end of the transmission
    # in all communication modes at all speeds
    NFC_write_register(TModeRegister, 0x80)
    # TPreScaler = TModeReg[3..0]:TPrescalerReg, ie 0x0A9 = 169 =>
    # f_timer=40kHz,ie a timer period of 25μs.
    NFC_write_register(TPrescalarRegister, 0xA9)
    # Reload timer with 0x3E8 = 1000, ie 25ms before timeout.
    NFC_write_register(TReloadRegisterH, 0x03)

    NFC_write_register(TReloadRegisterL, 0xE8)
    # Default 0x00. Force a 100 % ASK modulation independent of
    # the ModGsPReg register setting
    NFC_write_register(TxASKRegister, 0x40)
    # Default 0x3F. Set the preset value for the CRC coprocessor
    # for the CalcCRC command to 0x6363 (ISO 14443-3 part 6.2.4)
    NFC_write_register(ModeRegister, 0x3D)
    NFC_antenna_on()

if __name__ == "__main__":
    print("Start")

    NFC_setup()
    print("NFC Initialised")

    NFC_dump_version()

    """while True:
        blah = NFC_IsNewCardPresent()
        print(blah)
        utime.sleep(100)
    """