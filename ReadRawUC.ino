void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); 
  // 11520 bytes/s --> 2880 floats/s -- > 347us delay
}

void loop() {
  while(true){
    // put your main code here, to run repeatedly:
    float f = analogRead(A1);
    int us = 347;
    //Serial.print(" ");
    Serial.println(f);
    delayMicroseconds(us);;
  }
}