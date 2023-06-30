/*******************************************************************************
* Copyright 2016 ROBOTIS CO., LTD.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

#include <Dynamixel2Arduino.h>

// Please modify it to suit your hardware.

#define DXL_SERIAL   Serial3 //OpenCM9.04 EXP Board's DXL port Serial. (Serial1 for the DXL port on the OpenCM 9.04 board)
#define DEBUG_SERIAL Serial
const int DXL_DIR_PIN = 22; //OpenCM9.04 EXP Board's DIR PIN. (28 for the DXL port on the OpenCM 9.04 board)


Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

int id_scanned = 0;

//This namespace is required to use Control table item names
using namespace ControlTableItem;

void setup() {
  // put your setup code here, to run once:

  pinMode(18, OUTPUT);
  pinMode(19, OUTPUT);
  pinMode(20, OUTPUT);

  pinMode(16, INPUT);
  pinMode(17, INPUT);

  for(int i = 0; i < 1; i++){
    digitalWriteFast(18, LOW);
    digitalWriteFast(19, LOW);
    digitalWriteFast(20, LOW);
    delay(1000);
    digitalWriteFast(18, HIGH);
    digitalWriteFast(19, HIGH);
    digitalWriteFast(20, HIGH);
    delay(1000);
  }

  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);   //set debugging port baudrate to 115200bps
  //while(!DEBUG_SERIAL);         //Wait until the serial port is opened

    // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
      

      // Set Port baudrate.
      dxl.begin(1000000);

      for(int protocol = 1; protocol <= 3; protocol++){

        digitalWrite(protocol + 17, LOW);
        dxl.setPortProtocolVersion(float(protocol));

        for(int id = 0; id < DXL_BROADCAST_ID; id++) {
              
          //iterate until all ID in each buadrate is scanned.
          if(dxl.writeControlTableItem(LED, id, 1)) {

            delay(500);
            digitalWriteFast(19, HIGH);
            digitalWriteFast(20, HIGH);
            
            int new_id = 0;

            digitalWriteFast(18, LOW);

            Serial.println("Current id is " + String(id));

            while(!digitalRead(16)){

              if(digitalRead(17)){
                
                if(new_id < 254){
                  new_id++;
                  digitalWriteFast(19, LOW);
                  while(digitalRead(17));
                  digitalWriteFast(19, HIGH);
                  delay(250);
                }

              }

              if(Serial.available()){
                dxl.writeControlTableItem(ID, id, String(Serial.read()).toInt());
                Serial.println("help");
                break;

              }

            }

            while(digitalRead(16));

            digitalWriteFast(18, HIGH);

            if(!dxl.writeControlTableItem(ID, id, new_id)){
              digitalWrite(18, LOW);
              digitalWrite(19, LOW);
              digitalWrite(20, LOW);
              continue;
            }

            DEBUG_SERIAL.println("Changed id to " + String(new_id));


            dxl.setOperatingMode(new_id, OP_POSITION);
            dxl.writeControlTableItem(TORQUE_ENABLE, new_id, 1);
            dxl.writeControlTableItem(GOAL_POSITION, new_id, 0);

            
            digitalWrite(20, LOW);

            for(int i = 0; i < new_id; i++){
              digitalWrite(19, LOW);
              delay(500);
              digitalWrite(19, HIGH);
              delay(500);


            }

            while(!digitalRead(16)){

              if(digitalRead(17)){

                dxl.setOperatingMode(new_id, OP_VELOCITY);
                dxl.writeControlTableItem(MOVING_SPEED, new_id, 1023);

              }

            }

            dxl.writeControlTableItem(TORQUE_ENABLE, new_id, 0);
            dxl.writeControlTableItem(LED, new_id, 0);

            delay(1000);
            digitalWriteFast(18, HIGH);
            digitalWriteFast(19, HIGH);
            digitalWriteFast(20, HIGH);

            return;

          }
          
        }
      }

      delay(1000);
      digitalWriteFast(18, HIGH);
      digitalWriteFast(19, HIGH);
      digitalWriteFast(20, HIGH);
    
  
  
}

void loop() {
  // put your main code here, to run repeatedly:
}