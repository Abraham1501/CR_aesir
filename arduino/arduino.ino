
// Include libraries
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>


// Pins of the right motors
int En1A = 7; 
int in5 = 26;  
int in6 = 27;  
int En1B = 6; 
int in7 = 28; 
int in8 = 29; 

// Pins of the left motors

int En2A = 3; 
int in1 = 38;  
int in2 = 39;  
int En2B = 2;
int in3 = 40;  
int in4 = 41;  

// Variable for the servos
Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver (0x40);

//Positions of the servos
unsigned int Pos0 = 204; 
unsigned int Pos180 = 409; 

// Current movement of the servos
int rotate[5] = {0, 0, 0, 0, 0};

// Current position of the servos
int positions[5] = {90,30, 0, 90, 180};

// Set a timer for servos
long last = micros();

// Set the timer time
long waiting = 1000000;

// Set a timer for the sensor data upload
long sent_last = micros();

// Set the wait of the servos
long set_wait = 15000;

// The string used to store serial information from the raspberry pi
String read = "";

// 4 = release
// 2 = backward
// 1 = forward

// The setup function
void setup ()
{

  // Beginning of the Serial communication
  Serial.begin(9600);

  // Setting the serial delay
  Serial.setTimeout(10);
 
  // Setting up the pins of the motors
  pinMode(in1, OUTPUT);    
  pinMode(in2, OUTPUT);
  //pinMode(EnA, OUTPUT);
  pinMode(in3, OUTPUT);    
  pinMode(in4, OUTPUT);

  pinMode(in5, OUTPUT);    
  pinMode(in6, OUTPUT);
  
  
  pinMode(in7, OUTPUT);   
  pinMode(in8, OUTPUT);

  pinMode(En1A, OUTPUT);
  pinMode(En1B, OUTPUT);
  pinMode(En2A, OUTPUT);
  pinMode(En2B, OUTPUT);

  // Prints a comment for the rasp to get when activating the program
  Serial.println("started");

  //Begins the servos and sets them to their position
  servos.begin();
  servos.setPWMFreq(50);
  servosUpdate();
  

}

// The loop function
void loop() {

  // Function to update the servo movement 
  servoMovement();

  // Function to send information of the sensors to the rasp
  readSensor();   

  // Check if there is any information available
  if(Serial.available()){

    // Reads the information of the serial and sets it to a string it also eliminates the last character which is a \n
    read = Serial.readString();
    read[read.length()-1] = 0;
    //Serial.println(read);
    
    
    // If read is empty, exit the function
    if(read == ""){
      return;
    }

    //Set up the portions that are going to be read
    String to, from;

    //Do it until if has read all the message
    while(read != ""){

      // Sets string 'to' to a cut version of read, it will havethe section until the first space, read is cut too
      to = cmds(read, ' ');

      // If the message is a ping message send information about the servos
      if(to == "ping"){
        Serial.println("A:S1: " + String(positions[0]) + " S2: " + String(positions[1])  + " S3: " + String(positions[2])  + " S4: " + String(positions[3])  + " S5: " + String(positions[4]));
        return;
      }

      //Checks the first character of the segmented message
      switch (to[0]){
          //M is for motor information
          case 'M':
            to.remove(0, 1);

            if(to.length() == 4){
              //Serial.println(to);
              motor_handler(to);
            }

          break;

          // S is for servo information
          case 'S':

          to.remove(0, 1);
          switch (to[0]){

            // S is for servo speed information
            case 'S':
              to.remove(0, 1);
              
              if(to.length() == 2){
                set_wait = long(hex(to)) * 1000;
                Serial.println("Speed is: " + String(set_wait));
              }

            break;

            // P is for servo position information
            case 'P':
              to.remove(0, 1);
              waiting = 1000000;
              if(to.length() == 8){
                for(int i = 0; i < 4; i++){
                                    
                  positions[i] = hex(to);
                }
                                
              }

            break;

            // If it is default servo information
            default:
              if(to.length() == 5){
                //Serial.println("Servos changed");
                for (int i = 0; i < 5; i++){
                  if(to[i] == '1' || to[i] == '2'){
                    rotate[i] = (to[i] - 48 )*2 - 3;
                    
                  }else{
                    rotate[i] = 0;

                  }
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
  }
}

// Set the servo to the desired angle
void setServo(uint8_t n_servo, int angulo, bool update) {

  // If th angle is in range 
  if(angulo > 180)
    angulo = 180;
  
  if(angulo < 0)
    angulo = 0;

  //Update the position of the servo
  if(update)
    positions[n_servo] = angulo;

  
  angulo *= 2;

  // Sends the information to the servo driver to move the servo
  int duty;
  duty = map (angulo, 0, 180, Pos0, Pos180);
  servos.setPWM(n_servo, 0, duty);
  
}


void readSensor(){
  // If 1 second has passed since last uploaded information
  if(micros() - sent_last > 1000000){
    
    //Resets timer
    sent_last = micros();

    // Reads the sendor and sends it as the Co2 sensor
    int Co2 = analogRead(A0);
    Serial.println("C:" + String(Co2));

  }


}

// Sets all the servo positions to the stored positions
void servosUpdate(){

  //Loops through all the stored positions
  for(int i = 0; i < sizeof(positions) / sizeof(int); i++){
    setServo(i, positions[i], true);
  }

}

// Ensures to move the servos at a certain speed
void servoMovement() {

  // If the timer has run out
  if(micros() - last > waiting){

    // Reset timer
    last = micros();

    // If the timer it waited has changed, update the servos
    if(waiting != set_wait){
      waiting = set_wait;
      servosUpdate();
    }

    // Loop through the positions
    for(int i = 0; i < sizeof(positions) / sizeof(int); i++){ 

      // Check if the specific servo is moving
      if(rotate[i] != 0){

        // Checks if the servo con move, although nothing would happen if i get rid of this check
        if((positions[i] < 180 && rotate[i] > 0) || (positions[i] > 0 && rotate[i] < 0)){

          // Add the position
          positions[i] += rotate[i];

          //Set the position
          setServo(i, positions[i], true);

        }

      }

    }

  }

}

// Handles the motor
void motor_handler(String to){
  
  // The variables for the speed
  int speed1 = 0, speed2 = 0;

  // Gets the number in decimal of the hexadecimal (just the last 2 digits of the string)
  speed1 = hex(to);

  // If it has the last bit active it goes backwards otherwise it goes forward
  if(!(speed1 & 128)){
    speed1 *= 2;
    ford(false, speed1);


  }else{
    speed1 -= 128;
    speed1 *= 2;
    back(false, speed1);

    // This multiplication is for setting the speed for printing
    speed1 *= -1;

  }
  
  // Sets the speed 2
  speed2 = hex(to);

  // Same procedure as the above but with the second side of the motor
  if(!(speed2 & 128)){
    speed2 *= 2;
    ford(true, speed2);


  }else{
    speed2 -= 128;
    speed2 *= 2;
    back(true, speed2);
    
    // This multiplication is for setting the speed for printing
    speed2 *= -1;

  }

  // Prints the speed for the rasp to read
  Serial.println(String(speed1) + " " + String(speed2));

}

// Stops the car
void parar(bool right){
  
  if(right){
    analogWrite(En1A,0);
    analogWrite(En1B,0);

    return;
  }

  analogWrite(En2A,0);
  analogWrite(En2B,0);

}

// Makes one side of the car go fordward
void ford(bool right, int sped){

  parar(right);
  
   
  if(right){
    analogWrite(En1A,sped);      //Velocidad del  Motor A
    digitalWrite(in1, HIGH);  
    digitalWrite(in2, LOW);

    analogWrite(En1B,sped);      //Velocidad del  Motor A
    digitalWrite(in3, HIGH);  
    digitalWrite(in4, LOW);
    return;
  }

  analogWrite(En2A,sped);      //Velocidad del  Motor A
  digitalWrite(in5, HIGH);  
  digitalWrite(in6, LOW);

  analogWrite(En2B,sped);      //Velocidad del  Motor A
  digitalWrite(in7, HIGH);  
  digitalWrite(in8, LOW);

}

//  Makes one side of the car go backward
void back(bool right, int sped){

  parar(right); 

  if(right){
    analogWrite(En1A,sped);      //Velocidad del  Motor A
    digitalWrite(in1, LOW);  
    digitalWrite(in2, HIGH);

    analogWrite(En1B,sped);      //Velocidad del  Motor A
    digitalWrite(in3, LOW);  
    digitalWrite(in4, HIGH);
    return;
  }

  analogWrite(En2A,sped);      //Velocidad del  Motor A
  digitalWrite(in5, LOW);  
  digitalWrite(in6, HIGH);

  analogWrite(En2B,sped);      //Velocidad del  Motor A
  digitalWrite(in7, LOW);  
  digitalWrite(in8, HIGH);

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
    String temp = num.substring(num.length() - size, num.length()); 
    num.remove(num.length() - size, num.length()); 
    

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

}


// Code that was not used, it was to have a better structure using classes for the motor instead of letting them be free
class Pair{

  private:

    int EnA;
    int EnB;
    int in1;
    int in2;
    int in3;
    int in4;
  
  public:
    Pair(int a, int b, int c, int d, int e, int f){
      EnA = a;
      EnB = b;
      in1 = c;
      in2 = d;
      in3 = e;
      in4 = f;        
                    
      pinMode(in1, OUTPUT);    // Configura  los pines como salida
      pinMode(in2, OUTPUT);
      //pinMode(EnA, OUTPUT);
      pinMode(in3, OUTPUT);    // Configura  los pines como salida
      pinMode(in4, OUTPUT);

      pinMode(EnA, OUTPUT);    // Configura  los pines como salida
      pinMode(EnB, OUTPUT);

      
      
    }
        
    void stop(){
      digitalWrite(in1, LOW);  
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);  
      digitalWrite(in4, LOW);
      
    }

    void forward(int8_t speed){
      analogWrite(EnA, speed);
      analogWrite(EnB, speed);
      digitalWrite(in1, HIGH);  
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);  
      digitalWrite(in4, LOW);
      
    }

    void backward(int8_t speed){
      analogWrite(EnA, speed);
      analogWrite(EnB, speed);
      digitalWrite(in1, LOW);  
      digitalWrite(in2, HIGH);
      digitalWrite(in3, LOW);  
      digitalWrite(in4, HIGH);
      
    }
  
};

class Motors{

  private:
    Pair* left = new Pair(2, 3, 38, 39, 40, 41); 
    Pair* right = new Pair(6, 7, 22, 23, 24, 25);

      
  public:

  ~Motors(){
    delete left;
    delete right;

  }

  void forward(){
    left -> stop();

  }
    
            
};
/*
Motor mot1(true, false);
Motor mot2(false, true);
Motor mot3(false, true);
Motor mot4(false, false);
//*///primer digito es polaridad, segundo es lado (derecha izquierda)
