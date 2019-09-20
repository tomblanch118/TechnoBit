#include <Wire.h> //i2c library
#include <SPI.h> //spi library
#include <MFRC522.h> // rfid library
#include <LiquidCrystal.h> // lcd library
#include <Adafruit_NeoPixel.h> // rgb led library

#define RST_PIN         9           //rfid reset pin
#define SS_PIN          10           //rfid chip select pin
#define IRQ_PIN         2           //rfid interrupt pin

#define LCD_RS          8
#define LCD_EN          7
#define LCD_D4          3
#define LCD_D5          4
#define LCD_D6          5
#define LCD_D7          6

#define RGB_LED_PIN     A0

//RFID reader instance
MFRC522 mfrc522(SS_PIN, RST_PIN);

//LCD screen instance
LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

//RGB led instance
Adafruit_NeoPixel strip = Adafruit_NeoPixel(1, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);

//Variables used in interrupts
volatile uint8_t card = 0;
volatile bool bNewInt = false;
volatile uint8_t cRed = 0;
volatile uint8_t cBlue = 0;
volatile uint8_t cGreen = 0;

byte regVal = 0x7F;
void activateRec(MFRC522 mfrc522);
void clearInt(MFRC522 mfrc522);


void setup() {
  // join i2c bus with address #8 (how we communicate with the microbit)
  Wire.begin(8);

  //Register event callbacks for receiveing i2c data and receiving requests for data
  Wire.onRequest(requestEvent);
  Wire.onReceive(receiveEvent);

  //Start the serial port at 115200 baud, mainly used for debug
  Serial.begin(115200); // Initialize serial communications with the PC
  while (!Serial);

  Serial.println("Technocamps i2c RFID adapter v0.1");
  Serial.flush();

  //Initialise the RGB LED to off
  strip.begin();
  strip.setPixelColor(0, strip.Color(cRed, cGreen, cBlue));
  strip.show();

  // Set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print(" -=TechnoBit=- ");
  lcd.setCursor(0, 1);
  lcd.print("    -=V0.2=-   ");

  //Initialise the SPI bus
  SPI.begin();

  //Initialise the MFRC522 rfid card reader
  mfrc522.PCD_Init();

  // Read and printout the MFRC522 version (valid values 0x91 & 0x92)
  Serial.print(F("MFRC522 Ver: 0x"));
  byte readReg = mfrc522.PCD_ReadRegister(mfrc522.VersionReg);
  Serial.println(readReg, HEX);

  //Set up the interrupt pin so the card reader can notify us when there is a card present
  pinMode(IRQ_PIN, INPUT_PULLUP);

  /*
     Allow the ... irq to be propagated to the IRQ pin
     For test purposes propagate the IdleIrq and loAlert
  */
  regVal = 0xA0; //rx irq
  mfrc522.PCD_WriteRegister(mfrc522.ComIEnReg, regVal);

  //Set the interrupt flag to false
  bNewInt = false;
  
  //Connect the interrupt event with the handler function
  attachInterrupt(digitalPinToInterrupt(IRQ_PIN), readCard, FALLING);

  //Catch any spurious interrupts that happen during start up
  unsigned long start = millis();
  do {
    ;
  } while (!bNewInt && (millis() - start < 1500) );
  bNewInt = false;

  Serial.println(F("Setup complete"));
  rainbow(5);
}

/**
   Main loop.
*/
char cardID[8] = "00000000";

const char * blankLine = "               ";
char lcdLine0[16] = "               ";
char lcdLine1[16] = "               ";

void loop() {
  if (bNewInt) { //new read interrupt
    card = 1;
    mfrc522.PICC_ReadCardSerial(); //read the tag data
    // Show some details of the PICC (that is: the tag/card)
    mfrc522.PICC_HaltA();
    clearInt(mfrc522);
    // maybe use bigger id (use mfrc522.uid.size)
    for (int i = 0; i < 4; i++)
    {
      sprintf(&cardID[i * 2], "%02x", *(mfrc522.uid.uidByte  + i));
    }
    Serial.println(cardID);
    // lcd.setCursor(0, 1);

    //lcd.print(cardID);


    bNewInt = false;
  }

  lcd.setCursor(0, 0);
  lcd.print(lcdLine0);
  lcd.setCursor(0, 1);
  lcd.print(lcdLine1);

  //Serial.println(lcdLine0);
  //Serial.println(lcdLine1);
  // The receiving block needs regular retriggering (tell the tag it should transmit??)
  // (mfrc522.PCD_WriteRegister(mfrc522.FIFODataReg,mfrc522.PICC_CMD_REQA);)
  activateRec(mfrc522);
  strip.setPixelColor(0, strip.Color(cRed, cGreen, cBlue));
  strip.show();
  delay(100);
} //loop()

/**
   Helper routine to dump a byte array as hex values to Serial.
*/
void dump_byte_array(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? "0" : "");
    Serial.print(buffer[i], HEX);
  }
}
/**
   MFRC522 interrupt serving routine
*/
void readCard() {
  bNewInt = true;
}

/*
   The function sending to the MFRC522 the needed commands to activate the reception
*/
void activateRec(MFRC522 mfrc522) {
  mfrc522.PCD_WriteRegister(mfrc522.FIFODataReg, mfrc522.PICC_CMD_REQA);
  mfrc522.PCD_WriteRegister(mfrc522.CommandReg, mfrc522.PCD_Transceive);
  mfrc522.PCD_WriteRegister(mfrc522.BitFramingReg, 0x87);
}

/*
   The function to clear the pending interrupt bits after interrupt serving routine
*/
void clearInt(MFRC522 mfrc522) {
  mfrc522.PCD_WriteRegister(mfrc522.ComIrqReg, 0x7F);
}


void receiveEvent(int num)
{
  uint8_t reg = 0x00;
  if (1 < Wire.available() ) {
    reg = Wire.read();
  }
  //TODO: check if amount of data correct
  if (reg == 0x03) {
    cRed = Wire.read();
    cGreen = Wire.read();
    cBlue = Wire.read();
  }
  else if (reg == 0x02 || reg == 0x01)
  {
    int i = 0;
    if (reg == 0x01)
    {
      sprintf(lcdLine0, "%s", blankLine);
    }
    else
    {
      sprintf(lcdLine1, "%s", blankLine);
    }

    while (0 < Wire.available()) { // loop through all but the last
      char c = Wire.read(); // receive byte as a character
      //Only space for 16 characters so read but ignore the others
      if (i < 16) {
        if (reg == 0x02) {
          lcdLine1[i] = c;
        }
        else {
          lcdLine0[i] = c;
        }
      }
      i++;
    }
  }
  else
  {
    while (0 < Wire.available()) { // loop through all but the last
      char c = Wire.read(); // receive byte as a character
    }
  }
}

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {
  if (card == 0)
  {

    Wire.write("00000000"); // respond with message of 6 bytes
  }
  else
  {
    for (int i = 0; i < 8; i++)
    {
      Wire.write(cardID[i]);
    }
    card = 0;
  }
  // as expected by master
  //  Serial.println("Got request");
}

void rainbow(uint8_t wait) {
  uint16_t i, j;

  for(j=0; j<256; j++) {
    for(i=0; i<strip.numPixels(); i++) {
      strip.setPixelColor(i, Wheel((i+j) & 255));
    }
    strip.show();
    delay(wait);
  }
}
// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}
