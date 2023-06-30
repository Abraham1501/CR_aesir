
// Include libraries
#include <Dynamixel2Arduino.h>
//Time controlled prepositions
//Improve the speed at which servo go when disconnected and not detected

#define DXL_SERIAL   Serial3 //OpenCM9.04 EXP Board's DXL port Serial. (Serial1 for the DXL port on the OpenCM 9.04 board) Serial3
const int DXL_DIR_PIN = 22; //OpenCM9.04 EXP Board's DIR PIN. (28 for the DXL port on the OpenCM 9.04 board) Pin 22


Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

// Set a timer for servos
long last = micros();

// Set a timer for the sensor data upload
long sent_last = micros();

long wave = micros();

long wavetime = 1000000;

int dir = 1;

// Set the wait of the servos
long set_wait = 15000;

int actSpeed = 132;

int send = 66;

int motors[10] = {false, false, false, false, false, false, false, false, false, false};

int CW_limit[10]  = {0, 0, 0, 0, 149, 197, 213, 198, 260, 0};
int CCW_limit[10] = {0, 0, 0, 0, 852, 817, 833, 777, 820, 1023}; // last is 820

bool waving = false;

// The string used to store serial information from the raspberry pi
String read = "";

// 4 = release
// 2 = backward
// 1 = forward

using namespace ControlTableItem;

// The setup function
void setup ()
{

  // Beginning of the Serial communication
  Serial.begin(9600);

  // Setting the serial delay
  Serial.setTimeout(6);

  // Prints a comment for the rasp to get when activating the program

  
  dxl.setPortProtocolVersion(1.0);

  dxl.begin(1000000);



  delay(1000);

  for( int i = 0; i < 9; i++){
    writeServo(LED, i, 1);
  }


  
  flicker(9);
  delay(500);
  writeServo(GOAL_POSITION, 8, 260); //489
  writeServo(GOAL_POSITION, 7, 198);
  writeServo(GOAL_POSITION, 6, 213);
  writeServo(GOAL_POSITION, 5, 817);
  writeServo(GOAL_POSITION, 4, 512);

}

// The loop function
void loop() {

  // Function to send information of the sensors to the rasp
  readSensor();   

  // Check if there is any information available
  if(Serial.available()){

    // Reads the information of the serial and sets it to a string it also eliminates the last character which is a \n
    read = Serial.readString();


    //Serial.println(read);
    int servo_id = -1;
    int speed;
    int pos;

    String temp;

    bool com = true;
    
    // If read is empty, exit the function
    if(read == ""){
      return;
    }

    //Set up the portions that are going to be read
    String to, from;

    //Do it until if has read all the message
    while(read != ""){

      //Serial.println(read);

      // Sets string 'to' to a cut version of read, it will havethe section until the first space, read is cut too
      to = cmds(read, ' ');

      // If the message is a ping message send information about the servos
      if(to[0] == 'P'){
        
        Serial.println("Pinged");
        pingMotors();
        
        return;
      }

      //Checks the first character of the segmented message
      switch (to[0]){
          case 'I':
            to.remove(0, 1);
            send = to.toInt();

          case 'W':
            to.remove(0, 1);
            waving = true;

            temp = to.substring(0, 4); 
            to.remove(0, 4); 

            speed = temp.toInt();
            com = writeServo(MOVING_SPEED, 8, speed);

            temp = to.substring(0, 4); 
            to.remove(0, 4); 

            wavetime = long((float(temp.toInt()) / float(speed)) * 435435);

            Serial.println(wavetime);
            Serial.println(temp.toInt()); 
            Serial.println(speed);


                

          break;
          //M is for motor information
          case 'M':
            to.remove(0, 1);
            com = motor_handler(to);
            

          break;

          // S is for servo information
          case 'S':

          to.remove(0, 1);

          
          //Serial.println(servo_id);


          switch (to[0]){

            // S is for servo speed information
            case 'S':
              to.remove(0, 1);
                speed = to.toInt();
                actSpeed = speed;
                for(int i = 4; i <= 8; i++){
                  com = writeServo(MOVING_SPEED, i, speed);
                }

                //Serial.println("Servo speed " + String(speed));
              

            break;

            // P is for servo position information
            case 'P':
              to.remove(0, 1);
              servo_id = hex(to);

              if(waving && servo_id == 8){
                waving = false;
                dir = 1;
                
              }

              checkSpeed(servo_id);

              if(!dxl.ping(servo_id)){
                continue;

              }

                  pos = to.toInt();
                  
                  if(pos < CW_limit[servo_id]){
                    pos = CW_limit[servo_id];
                  }

                  if(pos > CCW_limit[servo_id]){
                    pos = CCW_limit[servo_id];
                  }

                  com = writeServo(GOAL_POSITION, servo_id, pos);

                  //Serial.println(pos);

            break;

            // If it is default servo information
            default:
              servo_id = hex(to);

              //if(!dxl.ping(servo_id)){
                //continue;

              //}

                //Serial.println("Servos changed");
                  if(waving && servo_id == 8){
                    waving = false;
                    dir = 1;
                  }

                  checkSpeed(servo_id);

                  if(to[0] == '1' || to[0] == '2'){

                    if(to[0] == '1')
                      com = writeServo(GOAL_POSITION, servo_id, CCW_limit[servo_id]);

                    if(to[0] == '2')
                      com = writeServo(GOAL_POSITION, servo_id, CW_limit[servo_id]);

                    //Serial.println("Servo " + String(servo_id) + " changed");
                    
                  }else{

                    if(readServo(GOAL_POSITION, servo_id) == CW_limit[servo_id] || readServo(GOAL_POSITION, servo_id) == CCW_limit[servo_id]){
                      
                      com = writeServo(GOAL_POSITION, servo_id, readServo(PRESENT_POSITION, servo_id));
                    }

                  }
                
              

            break;
          }

        break;
        
        default:

          //Serial.println("No useful message");

        break;
      }

    }
      
    if(com){
      //Serial.println("Command success");
    }

    

  }
}


void readSensor(){
  // If 1 second has passed since last uploaded information
  if(micros() - sent_last > 1000000){
    
    //Resets timer
    sent_last = micros();

    // Reads the sendor and sends it as the Co2 sensor
    /*
    for(int i = 0; i < 9; i++){

      if(readServo(ALARM_LED, i)){

        int alarm = readServo(ALARM_LED, i);

        //Serial.println(alarm);

        if((alarm & 1) == 1){
          Serial.println("Over voltage on servo " + String(i));
        }

        if((alarm & 4) == 4){
          Serial.println("Over heating on servo " + String(i));
        }

        if((alarm & 32) == 32){
          Serial.println("Over load on servo  " + String(i));
        }
        

      }

    }//*/

    String id = "";

    switch(send){
      case 66:
        id = "p: ";
      break;
      case 69:
        id = "t: ";
      break;
      case 68:
        id = "v: ";
      break;
      case 63:
        id = "l: ";
      break;
      default:
        id = "Unidentified: ";

    }

    //I hate this line of code :/
    //I'll do it better when i implement logic in rasp (hopefully)
    Serial.println(id +
      String(bitrem(readServo(send, 0), 10)) + " " + 
      String(bitrem(readServo(send, 1), 10)) + " " + 
      String(bitrem(readServo(send, 2), 10)) + " " + 
      String(bitrem(readServo(send, 3), 10)) + " " + 
      String(bitrem(readServo(send, 4), 10)) + " " + 
      String(bitrem(readServo(send, 5), 10)) + " " + 
      String(bitrem(readServo(send, 6), 10)) + " " + 
      String(bitrem(readServo(send, 7), 10)) + " " + 
      String(bitrem(readServo(send, 8), 10)) + " " +
      String(bitrem(readServo(send, 9), 10)) + " "
    );//*/
    

  }

  if(waving && ((micros() - wave) > wavetime)){
    wave = micros();
    
    if(dir == 1){
      writeServo(GOAL_POSITION, 8, CW_limit[8]);

      dir = 2;
    }else if(dir == 2){
      writeServo(GOAL_POSITION, 8, CCW_limit[8]);
      dir = 1;
    }
    //Serial.println("Servo " + String(servo_id) + " changed");
                    
    

  }


}

void checkSpeed(int id){
  if(motors[id] && (readServo(MOVING_SPEED, id) != actSpeed )){
    writeServo(MOVING_SPEED, id, actSpeed);
  }

}

int bitrem(int num, int bit){

  if((num & (1 << bit)) == (1 << bit)){
    
    return num -= (1 << bit);

  }

  return num;


}

// Handles the motor
bool motor_handler(String to){
  
  // The variables for the speed
  int speed1 = 0, speed2 = 0;

  bool com = true;

  String temp;

  temp = to.substring(0, 4); 
  to.remove(0, 4); 

  // Gets the number in decimal of the hexadecimal (just the last 2 digits of the string)
  speed1 = temp.toInt();

  // If it has the last bit active it goes backwards otherwise it goes forward
  com = writeServo(MOVING_SPEED, 0, speed1);

  com = writeServo(MOVING_SPEED, 1, speed1);


  temp = to.substring(0, 4); 
  to.remove(0, 4); 
  
  // Sets the speed 2
  speed2 = temp.toInt();

  

  if(!(speed2 & 1024)){
    speed2 += 1024;

  }else{
    speed2 -= 1024;
    

  }



  // Same procedure as the above but with the second side of the motor
  
  com = writeServo(MOVING_SPEED, 2, speed2);

  com = writeServo(MOVING_SPEED, 3, speed2);

  // Prints the speed for the rasp to read
  //Serial.println(String(speed1) + " " + String(speed2));

  return com;

}

bool writeServo(uint8_t cont, uint8_t id, int32_t data){

  long time = micros();

  if(!motors[id]){
    if(dxl.ping(id)){
      //Serial.println("Motor detected");
      motors[id] = true;
      servoSetup(id);
    

    }else{

      Serial.println("e: Servo " + String(id));
      //Serial.println("Motor disconnected");
      motors[id] = false;

      return false;

    }


  }

  dxl.writeControlTableItem(cont, id, data);
  
  if(id == 8){

    
    if(cont == 58){

      Serial.println("Setting");
      Serial.println(data);

      data = (CCW_limit[8] - data) + CW_limit[8] - 52;

    }
    //Serial.println(data);
    writeServo(cont, 9, data);

  }

  if(id == 9){
    Serial.println(data);

  }

  return true;

}

int32_t readServo(uint8_t cont, uint8_t id){
  if(motors[id]){
    int very = dxl.readControlTableItem(cont, id);

    if(!very){
      if(!dxl.ping(id)){
        motors[id] = false;
        //println("Motor disconnected from read");
        Serial.println("e: Servo " + String(id));
      }

    }

    return very;

  }else{
    return 0;
  }

}

void servoSetup(uint8_t id){

  switch(id){
    case 0:
      dxl.setOperatingMode(id, OP_VELOCITY);
      writeServo(TORQUE_ENABLE, id, 1);
    break;
    case 1:
      dxl.setOperatingMode(id, OP_VELOCITY);
      writeServo(TORQUE_ENABLE, id, 1);
    break;
    case 2:
      dxl.setOperatingMode(id, OP_VELOCITY);
      writeServo(TORQUE_ENABLE, id, 1);
    break;
    case 3:
      dxl.setOperatingMode(id, OP_VELOCITY);
      writeServo(TORQUE_ENABLE, id, 1);
    break;
    case 4:
      dxl.setOperatingMode(id, OP_POSITION);
      writeServo(TORQUE_ENABLE, id, 1);
      writeServo(MOVING_SPEED, id, 132);

      writeServo(CCW_ANGLE_LIMIT, id, CCW_limit[id]);
      writeServo(CW_ANGLE_LIMIT, id, CW_limit[id]);

      //writeServo(GOAL_POSITION, 7, 507);
    break;
    case 5:
      dxl.setOperatingMode(id, OP_POSITION);
      writeServo(TORQUE_ENABLE, id, 1);
      writeServo(MOVING_SPEED, id, 132);

     
      writeServo(CCW_ANGLE_LIMIT, id, CCW_limit[id]);
      writeServo(CW_ANGLE_LIMIT, id, CW_limit[id]);

    break;
    case 6:
      dxl.setOperatingMode(id, OP_POSITION);
      writeServo(TORQUE_ENABLE, id, 1);
      writeServo(MOVING_SPEED, id, 132);

      
      writeServo(CCW_ANGLE_LIMIT, id, CCW_limit[id]);
      writeServo(CW_ANGLE_LIMIT, id, CW_limit[id]);

    break;
    case 7:
      dxl.setOperatingMode(id, OP_POSITION);
      writeServo(TORQUE_ENABLE, id, 1);
      writeServo(MOVING_SPEED, id, 132);

      writeServo(CCW_ANGLE_LIMIT, id, CCW_limit[id]);
      writeServo(CW_ANGLE_LIMIT, id, CW_limit[id]);

    break;
    case 8:
      dxl.setOperatingMode(id, OP_POSITION);
      writeServo(TORQUE_ENABLE, id, 1);
      writeServo(MOVING_SPEED, id, 132);

      //writeServo(CCW_ANGLE_LIMIT, id, CCW_limit[id]);
      //writeServo(CW_ANGLE_LIMIT, id, CW_limit[id]);

    break;
    case 9:
      Serial.println("limits:");
      Serial.println(CCW_limit[id]);
      Serial.println(CW_limit[id]);
      dxl.setOperatingMode(id, OP_POSITION);
      writeServo(TORQUE_ENABLE, id, 1);
      writeServo(MOVING_SPEED, id, 132);

      //writeServo(CCW_ANGLE_LIMIT, id, CCW_limit[id]);
      //writeServo(CW_ANGLE_LIMIT, id, CW_limit[id]);

    break;

    


  }

}

// Overload
String cmds(String& cmd){
  return cmds(cmd, ';');
}

// Gets a string through reference and chops it until it finds the character given, it also returns the chopped version
String cmds(String& cmd, char cut){
  int a = cmd.indexOf(cut);
  String temp;

  if(a != -1){
    temp = cmd.substring(0, a); 
    cmd.remove(0, a+1); 

  }else{
    temp = cmd.substring(0, cmd.length()); 
    cmd.remove(0, cmd.length()); 
  }
  //Serial1.println(cmd.length());
  return temp;

}

// Overload
int hex(String& num){
  return hex(num, 2);

}

// Transform a number in hexadecimal into a decimal
int hex(String& num, int size){
  if(num.length() >= size){
    String temp = num.substring(0, 2); 
    num.remove(0, 2); 
    

    int ret = 0;

    for(int i = 0; i < size; i++){
          
      if(temp[temp.length()-(i+1)] >= '0' && temp[temp.length()-(i+1)] <= '9'){

        ret += ((temp[temp.length()-(i+1)] - 48) << (4*i));

      }else if(temp[temp.length()-(i+1)] >= 'A' && temp[temp.length()-(i+1)] <= 'F'){
        //Serial1.println(temp[temp.length()-(i+1)]);
        ret += ((temp[temp.length()-(i+1)] - 55) << (4*i));
      }
      
    }
 
    return ret;

  }

  return 0;

}

void pingMotors(){

  for(int i = 0; i < 9; i++){

    writeServo(LED, i, 1);

    writeServo(LED, i, 0);

  }


}

void flicker(int motors){

  for(int i = 0; i < motors; i++){

    writeServo(LED, i, !readServo);

  }

}