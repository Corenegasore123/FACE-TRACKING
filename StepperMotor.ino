#include <Stepper.h>

const int stepsPerRevolution = 2048; // 28BYJ-48 with 64:1 reduction

// Define the pins connected to the ULN2003 driver inputs
const int in1Pin = 8;
const int in2Pin = 9;
const int in3Pin = 10;
const int in4Pin = 11;
// Create a Stepper object
Stepper myStepper(stepsPerRevolution, in1Pin, in3Pin, in2Pin, in4Pin);

// Convert degrees to steps
int angleToSteps(float angle) {
  return (int)((angle / 360.0) * stepsPerRevolution);
}

// Rotate motor by angle
void stepByAngle(float angle) {
  int steps = angleToSteps(angle);
  myStepper.step(steps);
}

void setup() {
  Serial.begin(9600);
  Serial.println("Stepper Motor Control Ready!");
  Serial.println("Type commands like:");
  Serial.println("rotate 180 degrees");
  Serial.println("rotate -90 degrees");

  myStepper.setSpeed(10); // RPM
}

void loop() {
  // Check if a full command has arrived
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // read full line
    command.trim();  // remove spaces & newlines

    // Check if command starts with "rotate"
    if (command.startsWith("rotate")) {
      // Remove "rotate" word
      command.replace("rotate", "");
      command.replace("degrees", "");  // remove word "degrees"
      command.trim();

      // Convert remaining text to number
      float angle = command.toFloat();

      if (angle != 0) {
        Serial.print("Rotating by ");
        Serial.print(angle);
        Serial.println(" degrees...");

        stepByAngle(angle);

        Serial.println("Done!");
      } else {
        Serial.println("Invalid angle input!");
      }
    } else {
      Serial.println("Unknown command. Use: rotate <angle> degrees");
    }
  }
}
