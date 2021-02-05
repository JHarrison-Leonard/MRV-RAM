//https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/#Raspberry_Pi_Software_setup
//https://www.youtube.com/watch?v=ub82Xb1C8os

int LED = 8; //the pin we connect the LED
int LED_2 = 10;// the pin for LED2 when voltage goes high on MDM

void powerOffAllLEDs()
{
    digitalWrite(LED, LOW);
    digitalWrite(LED_2, LOW);
}

void setup() {
  Serial.begin(19200);
  pinMode(LED, OUTPUT); //set the LED pin as OUTPUT
  pinMode(LED_2, OUTPUT); //set the LED pin as OUTPUT
}

void loop() 
{
  int sensorValue = analogRead(A0); //Read input from Analog pin o
  float voltage = sensorValue * (5.0 / 1023.0);
  bool LEDval = HIGH;
  
  if (Serial.available() > 0) 
  {
    
    String data = Serial.readStringUntil('\n');
    
    if (data == "Module?") 
    {
      Serial.print("MDM");
    }    
    
    else if (data == "Recognized")
    {
      digitalWrite(LED, HIGH); //write 1 or HIGH to led pin //Hand Shake completed Green LED Should be on in the module
      Serial.print("Ready");
    }
    
    else if (data == "Metal?") //Metal Detection
      {
        if(voltage > 2.3)//Voltage limit for metal detection
        {
          digitalWrite(LED_2, HIGH);//LED on for Metal Detection - This LED is not Needed
          Serial.print("Detected");
        }
        else if (voltage <= 2.3)//Metal not detected
        {
          digitalWrite(LED_2, LOW);//LED off for Metal Detection - This LED is not Needed
          Serial.print("None");
        }
      }
    
   
  }
}
