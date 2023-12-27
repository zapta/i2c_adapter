
// Board abstraction. Allow to retarget to different boards.

#pragma once

#include <Wire.h>

// Abstract LED states.
enum LedState {
  // LED is off.
  LED_OFF,
  // LED is on during idle blinking.
  LED_IDLE_BLINK_ON,
  // LED is on while adapter is active.
  LED_ACTIVE_ON
};

// An abstrat LED.
class Led {
 public:
  virtual void update(LedState led_state) = 0;
};

namespace board {

extern void setup();
extern Led& led;
extern TwoWire i2c;

}  // namespace board
