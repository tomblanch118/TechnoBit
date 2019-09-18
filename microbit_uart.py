# Write your code here :-)

from microbit import *

print("Hello Tom")
uart.init(9600,tx=pin0,rx=pin1)

while True:
    uart.write('hello world')
    sleep(500)
"""
# NOT CHECKED
def NFC_write_registers(register, values):
    bregister = bytearray([register])

    CS_PIN.write_digital(0)
    spi.write(bregister)
    for val in values:
        bvalue = bytearray([val])
        spi.write(bvalue)
    CS_PIN.write_digital(1)

# NOT CHECKED
def NFC_IsNewCardPresent():
    bufferATQA = []
    bufferSize = 2

    # Reset baud rates
    NFC_write_register(TxModeRegister, 0x00)
    NFC_write_register(RxModeRegister, 0x00)
    # Reset ModWidthReg
    NFC_write_register(ModWidthRegister, 0x26)

    result = PICC_REQA_or_WUPA(PICC_CMD_REQA, bufferATQA, bufferSize)

    if result == STATUS_OK or result == STATUS_COLLISION:
        return True
    return False

def NFC_TransceiveData(sendData, sendLen, backData, backLen,
                       validBits, rxAlign, checkCRC):
    waitIRq = 0x30
    return NFC_CommunicateWithPICC(PCD_Transceive, waitIRq, sendData,
                                   sendLen, backData, backLen, validBits,
                                   rxAlign, checkCRC)


def NFC_SetRegisterBitMask(reg,  mask):
    tmp = NFC_read_register(reg)
    NFC_write_register(reg, tmp | mask)

def NFC_CommunicateWithPICC(command, waitIRq, sendData, sendLen, backData,
                            backLen, validBits, rxAlign, checkCRC):
    # Prepare values for BitFramingReg
    txLastBits = validBits
    # RxAlign = BitFramingReg[6..4]. TxLastBits = BitFramingReg[2..0]
    bitFraming = (rxAlign << 4) + txLastBits

    # Stop any active command.
    NFC_write_register(CommandRegister, PCD_Idle)
    # Clear all seven interrupt request bits
    NFC_write_register(ComIrqRegister, 0x7F)
    # FlushBuffer = 1, FIFO initialization
    NFC_write_register(FIFOLevelRegister, 0x80)
    #  Write sendData to the FIFO
    NFC_write_registers(FIFODataRegister, sendData)
    # Bit adjustments
    NFC_write_register(BitFramingRegister, bitFraming)
    # Execute the command
    NFC_write_register(CommandRegister, command)
    if (command == PCD_Transceive):
        # StartSend=1, transmission of data starts
        NFC_SetRegisterBitMask(BitFramingRegister, 0x80)

        # Wait for the command to complete.
        # In PCD_Init() we set the TAuto flag in TModeReg. This means
        # the timer automatically starts when the PCD stops transmitting.
        # Each iteration of the do-while-loop takes 17.86μs.
        # TODO check/modify for other architectures than Arduino Uno 16bit
        start = utime.ticks_us()
        i = 0
        while utime.ticks_diff(utime.ticks_us(), start) < 35700:
            n = NFC_read_register(ComIrqRegister)
            # One of the interrupts that signal success has been set.
            if n & waitIRq:
                i = 1
                break

            # Timer interrupt - nothing received in 25ms
            if n & 0x01:
                return STATUS_TIMEOUT

            utime.sleep_us(10)

        # 35.7ms and nothing happend. Communication with
        # the MFRC522 might be down.
        if i == 0:
            return STATUS_TIMEOUT

        # Stop now if any errors except collisions were detected.
        errorRegValue = NFC_read_register(ErrorRegister)
        # ErrorReg[7..0] bits are: WrErr TempErr reserved BufferOvfl
        # CollErr CRCErr ParityErr ProtocolErr
        # BufferOvfl ParityErr ProtocolErr
        if errorRegValue & 0x13:
            return STATUS_ERROR

        _validBits = 0

        # If the caller wants data back, get it from the MFRC522.
        if backData and backLen:
            # Number of bytes in the FIFO
            n = NFC_read_register(FIFOLevelRegister)
            if n > backLen:
                return STATUS_NO_ROOM

                backLen = n
                NFC_read_register(FIFODataRegister, n, backData, rxAlign)
                _validBits = NFC_read_register(ControlRegister) & 0x07
                if (validBits):
                    validBits = _validBits

        # Tell about collisions
        if errorRegValue & 0x08:
            return STATUS_COLLISION

        # Perform CRC_A validation if requested.
        if backData and backLen and checkCRC:
            # In this case a MIFARE Classic NAK is not OK.
            if backLen == 1 and _validBits == 4:
                return STATUS_MIFARE_NACK

            # We need at least the CRC_A value and all 8 bits of
            # the last byte must be received.
            if backLen < 2 or _validBits != 0:
                return STATUS_CRC_WRONG

            # Verify CRC_A - do our own calculation and store the
            # control in controlBuffer.
            controlBuffer = []
            status = NFC_CalculateCRC(backData[0], backLen - 2, controlBuffer[0])
            if status != STATUS_OK:
                return status

            if (backData[backLen - 2] != controlBuffer[0]) or (backData[backLen - 1] != controlBuffer[1]):
                return STATUS_CRC_WRONG
    # All ok
    return STATUS_OK


# return byte
# def PICC_RequestA(byte *bufferATQA,byte *bufferSize) {
#         return PICC_REQA_or_WUPA(PICC_CMD_REQA, bufferATQA, bufferSize);
# }

def NFC_CalculateCRC(data, length, result):
    NFC_write_register(CommandRegister, PCD_Idle)
    NFC_write_register(DivIrqRegister, 0x04)
    NFC_write_register(FIFOLevelRegister, 0x80)
    NFC_write_register(FIFODataRegister, length, data)
    NFC_write_register(CommandRegister, PCD_CalcCRC)

    # Wait for the CRC calculation to complete. Each iteration of the
    # while-loop takes 17.73μs.
    # TODO check/modify for other architectures than Arduino Uno 16bit

    # Wait for the CRC calculation to complete. Each iteration of theloop
    # takes 17.73us.
    start = utime.ticks_us()

    while utime.ticks_diff(utime.ticks_us(), start) < 89000:
        # DivIrqReg[7..0] bits are: Set2 reserved reserved MfinActIRq reserved
        # CRCIRq reserved reserved
        n = NFC_read_register(DivIrqRegister)
        if n & 0x04:
            NFC_write_register(CommandRegister, PCD_Idle)
            # Transfer the result from the registers to the result buffer
            result[0] = NFC_read_register(CRCResultRegisterL)
            result[1] = NFC_read_register(CRCResultRegisterH)
            return STATUS_OK
        utime.sleep_us(10)

        # 89ms passed and nothing happend. Communication with the MFRC522 might be down.
    return STATUS_TIMEOUT

# NEED RETURN  buffersize (actual) and validBits (actual)
# return byte
def PICC_REQA_or_WUPA(command, bufferATQA, bufferSize):

    # ValuesAfterColl=1 => Bits received after collision are cleared.
    NFC_ClearRegisterBitMask(CollRegister, 0x80)

    validBits = 7
    # For REQA and WUPA we need the short frame format - transmit only
    # 7 bits of the last (and only) byte. TxLastBits = BitFramingReg[2..0]
    status = NFC_TransceiveData(command, 1, bufferATQA, bufferSize, validBits)
    if status != STATUS_OK:
        return status

    # ATQA must be exactly 16 bits.
    if bufferSize != 2 or validBits != 0:
        return STATUS_ERROR

    return STATUS_OK

def NFC_ClearRegisterBitMask(reg, mask):
    tmp = NFC_read_register(reg)
    NFC_write_register(reg, tmp & (~mask))
"""