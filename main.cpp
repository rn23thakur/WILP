#include <Arduino.h>

// --- CONFIGURATION ---
#define MAX_PASS_LEN 16
#define TRIGGER_PIN 2      // Connect Scope Channel 1 (Trigger) here
#define LED_PIN LED_BUILTIN

// A small delay inside the loop makes the power/timing "steps" 
// visible to the human eye on a scope.
// For advanced/realistic attacks, you would remove this.
#define ARTIFICIAL_DELAY_US 50 

char storedPassword[MAX_PASS_LEN + 1] = "3456";
char serialBuffer[MAX_PASS_LEN + 1];

void setup() {
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(TRIGGER_PIN, LOW);
  
  Serial.begin(115200);
  while(!Serial);
  
  Serial.println("\n--- OSCILLOSCOPE SCA LAB ---");
  Serial.println("Send a password to trigger the trace.");
}

// The Vulnerable Comparison Function
// Returns: true if match, false if fail
// Side Effect: Leaks timing/power info via execution duration
bool vulnerableCheck(const char* guess) {
  for (int i = 0; i < MAX_PASS_LEN; i++) {
    // 1. Check if we reached end of stored password
    if (storedPassword[i] == '\0') {
      // If we reached the end, check if the guess also ended
      if (guess[i] == '\0') return true; 
      else return false;
    }

    // 2. The Vulnerability: Early Exit
    // If characters don't match, we return IMMEDIATELY.
    // This cuts the power trace short.
    if (guess[i] != storedPassword[i]) {
      return false; 
    }
    
    // 3. The "Leak" Amplifier
    // This creates a distinct "shelf" in the power trace
    // and extends the Trigger High duration.
    delayMicroseconds(ARTIFICIAL_DELAY_US); 
  }
  return true;
}

void loop() {
  if (Serial.available() > 0) {
    // 1. Read Input
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > MAX_PASS_LEN) input = input.substring(0, MAX_PASS_LEN);
    
    // Clear buffer and copy
    memset(serialBuffer, 0, sizeof(serialBuffer));
    strncpy(serialBuffer, input.c_str(), MAX_PASS_LEN);

    // 2. Prepare System for Clean Capture
    Serial.flush(); // Ensure UART is idle
    delay(10);      // Let power rails stabilize

    // --- CRITICAL SECTION START ---
    
    // Disable interrupts to prevent OS jitter (millis, serial interrupts)
    // This ensures every clock cycle is dedicated to our code.
    noInterrupts(); 
    
    // RISE Trigger: Tell Scope to start capturing NOW
    digitalWrite(TRIGGER_PIN, HIGH); 
    
    // Run the check exactly ONCE
    bool result = vulnerableCheck(serialBuffer);
    
    // FALL Trigger: Tell Scope capture is done
    digitalWrite(TRIGGER_PIN, LOW);
    
    interrupts(); // Re-enable interrupts
    
    // --- CRITICAL SECTION END ---

    // 3. User Feedback (Outside the measured window)
    if (result) {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("Result: [ACCESS GRANTED]");
    } else {
      digitalWrite(LED_PIN, LOW);
      Serial.println("Result: [DENIED]");
    }
  }
}