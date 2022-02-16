/*********************************************************************
 This is an example for our nRF51822 based Bluefruit LE modules

 Pick one up today in the adafruit shop!

 Adafruit invests time and resources providing this open source code,
 please support Adafruit and open-source hardware by purchasing
 products from Adafruit!

 MIT license, check LICENSE for more information
 All text above, and the splash screen below must be included in
 any redistribution
*********************************************************************/

#include <Arduino.h>
#include <SPI.h>
#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"

#include "BluefruitConfig.h"

#if SOFTWARE_SERIAL_AVAILABLE
  #include <SoftwareSerial.h>
#endif

/*=========================================================================
    APPLICATION SETTINGS

    FACTORYRESET_ENABLE       Perform a factory reset when running this sketch
   
                              Enabling this will put your Bluefruit LE module
                              in a 'known good' state and clear any config
                              data set in previous sketches or projects, so
                              running this at least once is a good idea.
   
                              When deploying your project, however, you will
                              want to disable factory reset by setting this
                              value to 0.  If you are making changes to your
                              Bluefruit LE device via AT commands, and those
                              changes aren't persisting across resets, this
                              is the reason why.  Factory reset will erase
                              the non-volatile memory where config data is
                              stored, setting it back to factory default
                              values.
       
                              Some sketches that require you to bond to a
                              central device (HID mouse, keyboard, etc.)
                              won't work at all with this feature enabled
                              since the factory reset will clear all of the
                              bonding data stored on the chip, meaning the
                              central device won't be able to reconnect.
    MINIMUM_FIRMWARE_VERSION  Minimum firmware version to have some new features
    MODE_LED_BEHAVIOUR        LED activity, valid options are
                              "DISABLE" or "MODE" or "BLEUART" or
                              "HWUART"  or "SPI"  or "MANUAL"
    -----------------------------------------------------------------------*/
    #define FACTORYRESET_ENABLE         1
    #define MINIMUM_FIRMWARE_VERSION    "0.6.6"
    #define MODE_LED_BEHAVIOUR          "MODE"
    #define LED 13
    int i = 0;
/*=========================================================================*/

// Create the bluefruit object, either software serial...uncomment these lines
/*
SoftwareSerial bluefruitSS = SoftwareSerial(BLUEFRUIT_SWUART_TXD_PIN, BLUEFRUIT_SWUART_RXD_PIN);

Adafruit_BluefruitLE_UART ble(bluefruitSS, BLUEFRUIT_UART_MODE_PIN,
                      BLUEFRUIT_UART_CTS_PIN, BLUEFRUIT_UART_RTS_PIN);
*/

/* ...or hardware serial, which does not need the RTS/CTS pins. Uncomment this line */
// Adafruit_BluefruitLE_UART ble(Serial1, BLUEFRUIT_UART_MODE_PIN);

/* ...software SPI, using SCK/MOSI/MISO user-defined SPI pins and then user selected CS/IRQ/RST */
//Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_SCK, BLUEFRUIT_SPI_MISO,
//                             BLUEFRUIT_SPI_MOSI, BLUEFRUIT_SPI_CS,
//                             BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

#include <Adafruit_BluefruitLE_SPI.h>
#include <Adafruit_BLEBattery.h>

// These are the pins for an Arduino UNO board. Change as needed
#define BLUEFRUIT_SPI_CS               8
#define BLUEFRUIT_SPI_IRQ              7
#define BLUEFRUIT_SPI_RST              4
#define BLUEFRUIT_SPI_SCK              13
#define BLUEFRUIT_SPI_MISO             12
#define BLUEFRUIT_SPI_MOSI             11

// SETUP ADAFRUIT BLUEFRUITLE SPI FRIEND
Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

// A couple global variables to keep track of time
unsigned long StartTime;
unsigned long TimeReference;

int count = 0;

/* ACCELEROMETER SERVICE ITEMS
 * ----------------- */
int32_t accServiceId;
int32_t xAccCharId;
int32_t yAccCharId;
int32_t zAccCharId;
int32_t xGyroCharId;
int32_t yGyroCharId;
int32_t zGyroCharId;
int32_t accTimeCharId;

/*  These are just some fake values I created so you can get some values over 
 *  the connection. In reality you would setup the AGM and get data from the 
 *  AGM to send via BLE
 */
float AccX = 0;
int AccY = 0;
int AccZ = 0;
int GyroX = 0;
int GyroY = 0;
int GyroZ = 0;
float data[460];

/* BATTERY SERVICE ITEMS
 * ----------------- */
int BatteryLevel = 100;

/*  This sets up the battery service for us. 
 *  You could also set it up using the UUID 
 *  like I do acceleromter service. Check out the 
 *  bluefruit documentation for examples on 
 *  how to do this as setting up a standardized  
 *  service is slightly different than
 *  a custom 128 bit UUID.
 */
Adafruit_BLEBattery battery(ble);


/* Function: error
 * ---------------------------------
 * small helper function
 * 
 * returns: n/a - void. Error message is printed serially
 */
void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}


/* Function: updateIntCharacteristic
 * ---------------------------------
 * This function updates given integer characteristics and emitts
 * the updated values via the BLE module
 * 
 * nameOfChar = the name of the characteristic to be emitted as a String
 * characteristic = the value of the characteristic - must be an integer
 * serviceId = the id that this characteristic belongs to
 * 
 * returns: n/a - void
 */
void updateIntCharacteristic(String nameOfChar, int counter, float characteristic, int32_t charId) {

  Serial.print("Byte size of ");
  Serial.print(nameOfChar);
  Serial.print(" : ");
  Serial.println(sizeof(characteristic));

  String msg = String(characteristic) + "," + String(counter);
  
  ble.print( F("AT+GATTCHAR=") );
  ble.print( charId );
  ble.print( F(",") );
  ble.println(characteristic);

  Serial.print("Actual value of ");
  Serial.print(nameOfChar);
  Serial.print(" : ");
  Serial.println(characteristic);
  if ( !ble.waitForOK() ) Serial.println(F("Failed to get response!"));
  Serial.println("");
  Serial.println("");
}


/* Function: emittAccelerometerData
 * ---------------------------------
 * prepares accelerometer data and passes it along to 
 * be emitted by the BLE module
 * 
 * xAcc = the x axis accelerometer reading
 * yAcc = the y axis accelerometer reading
 * zAcc = the z axis accelerometer reading
 * xGyro = the x axis gyroscope reading
 * yGyro = the y axis gyroscope reading
 * zGyro = the z axis gyroscope reading
 * accTimeReference = the time reference for this accelerometer reading
 * 
 * returns: n/a - void
 */
void emittAccelerometerData(int xAcc, int yAcc, float zAcc, int xGyro, int yGyro, int zGyro, unsigned long accTimeReference, int counter) {
  updateIntCharacteristic("x acceleration", counter, xAcc, xAccCharId);
}


void setup() {
  // SETUP BLE
  #define VBATPIN A7
  
  // initialize the serial communication:
  pinMode(10, INPUT); // Setup for leads off detection LO +
  pinMode(11, INPUT); // Setup for leads off detection LO -

  delay(500);
  boolean success;
  Serial.begin(115200);
  if ( !ble.begin(false) ) error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?")); // Set to false for silent and true for debug
  if (! ble.factoryReset() ) error(F("Couldn't factory reset"));
  ble.echo(false);
  ble.info();
  if (! ble.sendCommandCheckOK(F("AT+GAPDEVNAME=BLE Arduino Hardware")) ) error(F("Could not set device name?"));
  
  // SETUP ACCELEROMETER SERVICE & CHARACTERISTICS
  success = ble.sendCommandWithIntReply( F("AT+GATTADDSERVICE=UUID128=00-00-00-01-62-7E-47-E5-A3-fC-DD-AB-D9-7A-A9-66"), &accServiceId);
  if (! success) error(F("Could not add accelerometer service"));
  success = ble.sendCommandWithIntReply( F("AT+GATTADDCHAR=UUID128=00-00-00-02-62-7E-47-E5-A3-fC-DD-AB-D9-7A-A9-66, PROPERTIES=0x2, MIN_LEN=1, MAX_LEN=20,VALUE=5,DATATYPE=1"), &xAccCharId);
  if (! success) error(F("Could not add x acc characteristic"));

  // SETUP BATTERY SERVICE & CHARACTERISTICS
  battery.begin(true); // Note: this executes a ble.reset() automatically. If you don't use the battery.begin(true); command, you will need to use the ble.reset() command at the end. See the bluefruit documentation
  
  Serial.println();
}


void loop() {
  // Update the battery level measurement
  battery.update(BatteryLevel);

  StartTime = millis();
  TimeReference = millis();
  // Imaginary BIS Sweep here...
  for ( int i = 0; i < 460; i++) {
    float measuredvbat = analogRead(VBATPIN);
    measuredvbat *= 2;    // we divided by 2, so multiply back
    measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
    measuredvbat /= 1024; // convert to voltage
    Serial.print("VBat: " ); Serial.println(measuredvbat);
    ble.print("AT+BLEUARTTX=");
    ble.println(measuredvbat);
    data[i] = measuredvbat;
  }
  
  for ( int i =0; i < 460; i++) {
    AccX=data[i];
    emittAccelerometerData(AccX,AccY,AccZ,GyroX,GyroY,GyroZ, (TimeReference - StartTime),count);
  }
  if((digitalRead(10) == 1)||(digitalRead(11) == 1)){
    Serial.println('!');
  }
  else{
    // send the value of analog input 0:
      Serial.println(analogRead(A0));
      Serial.write(analogRead(A0));
  }
  
//  emittAccelerometerData(AccX,AccY,AccZ,GyroX,GyroY,GyroZ, (TimeReference - StartTime),count);
  
  count++;
  Serial.println(count);
  
  // Imaginary battery drain...
  
  if (BatteryLevel == 0) {
    BatteryLevel = 100;
  }
}
