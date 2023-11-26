int BTN_PIN = 8;
int SAFETY = 9;
int lastButtonState = HIGH;

void setup() {

  //start serial connection

  Serial.begin(9600);

  //configure pin 2 as an input and enable the internal pull-up resistor

  pinMode(BTN_PIN, INPUT_PULLUP);
  pinMode(SAFETY, INPUT_PULLUP);
  

  pinMode(13, OUTPUT);

}

void dostuff(){
  Serial.println("bruh");
}

void loop() {
  int dorun = digitalRead(SAFETY);
  if (dorun){
    return;
  }
  
  

  int buttonState = digitalRead(BTN_PIN);
  if (buttonState != lastButtonState) {
    if (buttonState == HIGH) {
      dostuff();
  } }
  lastButtonState =buttonState;
}
