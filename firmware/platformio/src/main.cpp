// Firmware of the I2C Adapter implementation using a Raspberry Pico.

#include <Arduino.h>
#include <Wire.h>

#include "board.h"

using board::i2c;
using board::led;

static uint8_t aux_pins[] = {
    0,  // Aux 0 = GP0
    1,  // Aux 0 = GP1
    2,  // Aux 0 = GP2
    3,  // Aux 0 = GP3
    4,  // Aux 0 = GP4
    5,  // Aux 0 = GP5
    6,  // Aux 0 = GP6
    7,  // Aux 0 = GP7
};

static constexpr uint8_t kNumAuxPins = sizeof(aux_pins) / sizeof(*aux_pins);
static_assert(kNumAuxPins == 8);

static constexpr uint8_t kApiVersion = 1;
static constexpr uint16_t kFirmwareVersion = 1;

// Arduino libraries seems to be limited to 256 bytes per read or write
// operation so we limit it here.
static constexpr uint16_t kMaxReadWriteBytes = 256;

// TODO: Add support for debug info using an auxilary UART.

// NOTE: Arduino Wire API documentation is here
// https://www.arduino.cc/reference/en/language/functions/communication/wire/

// All command bytes must arrive within this time period.
static constexpr uint32_t kCommandTimeoutMillis = 250;

// Since LED updates may involved neopixel communication, we minimize
// it by filtering the 'no-change' updates.
static bool last_led_state;

// A buffer for reading data from the serial port.
static uint8_t data_buffer[kMaxReadWriteBytes];
// The number of valid bytes in data_buffer.
static uint16_t data_size = 0;

// A simple timer.
// Cveate: overflows 50 days after last reset().
class Timer {
 public:
  Timer() { reset(millis()); }
  void reset(uint32_t millis_now) { _start_millis = millis_now; }
  uint32_t elapsed_millis(uint32_t millis_now) {
    return millis_now - _start_millis;
  }

 private:
  uint32_t _start_millis;
};

// Time since the start of last cmd.
static Timer cmd_timer;

// Fill data_buffer with n bytes. Done in chunks. data_size tracks the 
// num of bytes read so far.
static bool read_serial_bytes(uint16_t n) {
  // Handle the case where not enough chars.
  const uint16_t avail = Serial.available();
  const uint16_t required = n - data_size;
  const uint16_t requested = std::min(avail, required);
  
  if (requested) {
    size_t actual_read = Serial.readBytes((char*)(&data_buffer[data_size]), requested);
    data_size += actual_read;
  }

  return data_size >= n;
}

// Abstract base of all command handlers.
class CommandHandler {
 public:
  CommandHandler(const char* name) : _name(name) {}
  const char* cmd_name() const { return _name; }
  // Called each time the command starts to allow initialization.
  virtual void on_cmd_entered() {}
  // Returns true if command completed.
  virtual bool on_cmd_loop() = 0;
  // Call if the command is aborted due to timeout.
  virtual void on_cmd_aborted() {}

 private:
  const char* _name;
};

// ECHO command. Recieves a byte and echoes it back as a response. Used
// to test connectivity with the driver.
//
// Command:
// - byte 0:  'e'
// - byte 1:  Bhar to echo, 0x00 to 0xff
//
// Response:
// - byte 0:  Byte 1 from the command.
//
static class EchoCommandHandler : public CommandHandler {
 public:
  EchoCommandHandler() : CommandHandler("ECHO") {}
  virtual bool on_cmd_loop() override {
    static_assert(sizeof(data_buffer) >= 1);
    if (!read_serial_bytes(1)) {
      return false;
    }
    Serial.write(data_buffer[0]);
    return true;
  }
} echo_cmd_handler;

// INFO command. Provides information about this driver. Currently
// it's a skeleton for future values that will be returned.
//
// Command:
// - byte 0:  'i'
//
// Response:
// - byte 0:  'K' for OK.
// - byte 1:  Magic number MSB
// - byte 2:  Magic number LSB
// - byte 3:  Number of bytes to follow (3).
// - byte 4:  Version of wire format API.
// - byte 5:  MSB of firmware version.
// - byte 6:  LSB of firmware version.
static class InfoCommandHandler : public CommandHandler {
 public:
  InfoCommandHandler() : CommandHandler("INFO") {}
  virtual bool on_cmd_loop() override {
    Serial.write('K');                      // OK.
    Serial.write(0x45);                     // Magic number MSB.
    Serial.write(0x67);                     // Magic number LSB.
    Serial.write(0x03);                     // Number of bytes to follow.
    Serial.write(kApiVersion);              // API version.
    Serial.write(kFirmwareVersion >> 8);    // Firmware version MSB.
    Serial.write(kFirmwareVersion & 0x08);  // Firmware version LSB.
    return true;
  }
} info_cmd_handler;

// WRITE command. Writes N bytes to an I2C device.
//
// Command:
// - byte 0:    'w'
// - byte 1:    Device's I2C address in the range 0-127.
// - byte 2,3:  Number bytes to write. Big endian. Should be in the
//              range 0 to kMaxReadWriteBytes.
// - Byte 4...  The data bytes to write.
//
// Error response:
// - byte 0:    'E' for error.
// - byte 1:    Error code. See list below.
//
// OK response
// - byte 0:    'K' for 'OK'.
//
// Error codes:
//  1 : Data too long
//  2 : NACK on transmit of address
//  3 : NACK on transmit of data
//  4 : Other error
//  5 : Timeout
//  8 : Device address out of range..
//  9 : Count out of range.
//
static class WriteCommandHandler : public CommandHandler {
 public:
  WriteCommandHandler() : CommandHandler("WRITE") {}
  virtual void on_cmd_entered() override {
    _got_cmd_header = false;
    _device_addr = 0;
    _count = 0;
  }
  virtual bool on_cmd_loop() override {
    // Read command header.
    if (!_got_cmd_header) {
      static_assert(sizeof(data_buffer) >= 3);
      if (!read_serial_bytes(3)) {
        return false;
      }
      _device_addr = data_buffer[0];
      _count = (((uint16_t)data_buffer[1]) << 8) + data_buffer[2];
      _got_cmd_header = true;
      data_size = 0;
    }

    // Validate the command header.
    uint8_t status = (_device_addr > 127)            ? 0x08
                     : (_count > kMaxReadWriteBytes) ? 0x09
                                                     : 0x00;
    if (status != 0x00) {
      Serial.write('E');
      Serial.write(status);
      return true;
    }

    // Read the data bytes
    static_assert(sizeof(data_buffer) >= kMaxReadWriteBytes);
    if (!read_serial_bytes(_count)) {
      return false;
    }

    // Device address is 7 bits LSB.
    i2c.beginTransmission(_device_addr);
    i2c.write(data_buffer, _count);
    status = i2c.endTransmission(true);

    // TODO: Should do here if i2c_chan.getTimeout() is true?

    // All done
    if (status == 0x00) {
      Serial.write('K');
    } else {
      Serial.write('E');
      Serial.write(status);
    }
    return true;
  }

 private:
  bool _got_cmd_header = false;
  uint8_t _device_addr = 0;
  uint16_t _count = 0;

} write_cmd_handler;

// READ command. Read N bytes from an I2C device.
//
// Command:
// - byte 0:    'r'
// - byte 1:    Device's I2C address in the range 0-127.
// - byte 2,3:  Number bytes to read. Big endian. Should be in the
//              range 0 to kMaxReadWriteBytes.
//
// Error  Response:
// - byte 0:    'E' for 'error'.
// - byte 1:    Error code. See list below.
//
// OK Response:
// - byte 0:    'K' for 'OK'.
// - byte 1,2:  Number bytes to follow. Big endian. Identical to the
//              count in the command.
// - byte 3...  The bytes read.
//
// Error codes:
//  1 : Byte count mismatch while reading.
//  2 : Bytes not available for reading.
//  8 : Device address out of range..
//  9 : Count out of range.
static class ReadCommandHandler : public CommandHandler {
 public:
  ReadCommandHandler() : CommandHandler("READ") {}

  virtual bool on_cmd_loop() override {
    // Get the command address and the count.

    static_assert(sizeof(data_buffer) >= 3);
    if (!read_serial_bytes(3)) {
      return false;  // try later
    }

    // Sanity check the command
    const uint8_t device_addr = data_buffer[0];
    const uint16_t count = (((uint16_t)data_buffer[1]) << 8) + data_buffer[2];
    uint8_t status = (device_addr > 127)            ? 0x08
                     : (count > kMaxReadWriteBytes) ? 0x09
                                                    : 0x00;
    if (status != 0x00) {
      Serial.write('E');
      Serial.write(status);
      return true;
    }

    // Read the bytes from the I2C devcie.
    const size_t actual_count = i2c.requestFrom(device_addr, count, true);

    // Sanity check the response.
    status = (actual_count != count)      ? 0x01
             : (i2c.available() != count) ? 0x02
                                          : 0x00;
    if (status != 0x00) {
      Serial.write('E');
      Serial.write(status);
      return true;
    }

    // Here when OK, send status, count, and data.
    Serial.write('K');
    Serial.write(count >> 8);
    Serial.write(count & 0x00ff);
    for (uint16_t i = 0; i < count; i++) {
      Serial.write(i2c.read());
    }
    return true;
  }

} read_cmd_handler;

// SET AUXILARY PIN MODE command.
//
// Command:
// - byte 0:    'm'
// - byte 1:    pin index, 0 - 7
// - byte 2:    pin mode
//
// Error response:
// - byte 0:    'E' for error.
// - byte 1:    Error code, per the list below, providing more information about
// the error.
//
// OK response
// - byte 0:    'K' for 'OK'.

// Error codes:
//  1 : Pin index out of range.
//  2 : Mode value out of range.
static class AuxPinModeCommandHandler : public CommandHandler {
 public:
  AuxPinModeCommandHandler() : CommandHandler("AUX_MODE") {}

  virtual bool on_cmd_loop() override {
    // Read command header.
    // if (!_got_cmd_header) {
    static_assert(sizeof(data_buffer) >= 2);
    if (!read_serial_bytes(data_buffer, 2)) {
      return false;
    }
    // Parse the command header
    const uint8_t aux_pin_index = data_buffer[0];
    const uint8_t aux_pin_mode = data_buffer[1];

    // Check aux pin index range.
    if (aux_pin_index >= kNumAuxPins) {
      Serial.write('E');
      Serial.write(0x01);
      return true;
    }

    // Map to underlying gpio pin.
    const uint8_t gpio_pin = aux_pins[aux_pin_index];

    // Dispatch by pin mode:
    switch (aux_pin_mode) {
      // Input pulldown
      case 1:
        pinMode(gpio_pin, INPUT_PULLDOWN);
        break;

      // Input pullup
      case 2:
        pinMode(gpio_pin, INPUT_PULLUP);
        break;

      // Output.
      case 3:
        pinMode(gpio_pin, OUTPUT);
        break;

      default:
        Serial.write('E');
        Serial.write(0x02);
        return true;
    }

    // All done Ok
    Serial.write('K');
    return true;
  }

} aux_mode_cmd_handler;

// READ AUXILARY PINS command.
//
// Command:
// - byte 0:    'a'
//
// Error response:
// - byte 0:    'E' for error.
// - byte 1:    Reserved. Always 0.
//
// OK response
// - byte 0:    'K' for 'OK'.
// - byte 1:    Auxilary pins values
static class AuxPinsReadCommandHandler : public CommandHandler {
 public:
  AuxPinsReadCommandHandler() : CommandHandler("AUX_READ") {}

  virtual bool on_cmd_loop() override {
    uint8_t result = 0;
    static_assert(kNumAuxPins == 8);
    for (int i = 7; i >= 0; i--) {
      const uint8_t gpio_pin = aux_pins[i];
      const PinStatus pin_status = digitalRead(gpio_pin);
      result = result << 1;
      if (pin_status) {
        result |= 0b00000001;
      }
    }

    // All done Ok
    Serial.write('K');
    Serial.write(result);
    return true;
  }

} aux_pins_read_cmd_handler;

// WRITE AUXILARY PINS command.
//
// Command:
// - byte 0:    'b'
// - byte 1:    New pins values
// - byte 2:    Write mask. Only pins with a corresponding '1' are written.
//
// Error response:
// - byte 0:    'E' for error.
// - byte 1:    Reserved. Always 0.
//
// OK response
// - byte 0:    'K' for 'OK'.
static class AuxPinsWriteCommandHandler : public CommandHandler {
 public:
  AuxPinsWriteCommandHandler() : CommandHandler("AUX_WRITE") {}

  virtual bool on_cmd_loop() override {
    static_assert(sizeof(data_buffer) >= 2);
    if (!read_serial_bytes(data_buffer, 2)) {
      return false;
    }
    const uint8_t values = data_buffer[0];
    const uint8_t mask = data_buffer[1];
    static_assert(kNumAuxPins == 8);
    for (int i = 0; i < 8; i++) {
      if (mask & 1 << i) {
        const uint8_t gpio_pin = aux_pins[i];
        // TODO: We write also to input pins. What is the semantic?
        digitalWrite(gpio_pin, values & 1 << i);
      }
    }

    // All done Ok
    Serial.write('K');
    return true;
  }

} aux_pins_write_cmd_handler;

// Given a command char, return a Command pointer or null if invalid command
// char.
static CommandHandler* find_command_handler_by_char(const char cmd_char) {
  switch (cmd_char) {
    case 'e':
      return &echo_cmd_handler;
    case 'i':
      return &info_cmd_handler;
    case 'w':
      return &write_cmd_handler;
    case 'r':
      return &read_cmd_handler;
    case 'm':
      return &aux_mode_cmd_handler;
    case 'a':
      return &aux_pins_read_cmd_handler;
    case 'b':
      return &aux_pins_write_cmd_handler;
    default:
      return nullptr;
  }
}

void setup() {
  // A short delay to let the USB/CDC settle down. Otherwise
  // it messes up with the debugger, in case it's used.
  delay(500);

  board::setup();
  board::led.update(false);
  last_led_state = false;

  // USB serial.
  Serial.begin(115200);

  // Init aux pins as inputs.
  for (uint8_t i = 0; i < kNumAuxPins; i++) {
    auto gp_pin = aux_pins[i];
    pinMode(gp_pin, INPUT_PULLUP);
  }

  // Init I2C.
  i2c.setClock(400000);   // 400Khz.
  i2c.setTimeout(50000);  // 50ms timeout.
  i2c.begin();
}

// If in command, points to the command handler.
static CommandHandler* current_cmd = nullptr;

void loop() {
  Serial.flush();
  const uint32_t millis_now = millis();
  const uint32_t millis_since_cmd_start = cmd_timer.elapsed_millis(millis_now);

  // Update LED state. Solid if active or short blinks if idle.
  {
    const bool is_active = current_cmd || millis_since_cmd_start < 200;
    const bool new_led_state =
        is_active || (millis_since_cmd_start & 0b11111111100) == 0;
    if (new_led_state != last_led_state) {
      led.update(new_led_state);
      last_led_state = new_led_state;
    }
  }

  // If a command is in progress, handle it.
  if (current_cmd) {
    // Handle command timeout.
    if (millis_since_cmd_start > kCommandTimeoutMillis) {
      current_cmd->on_cmd_aborted();
      current_cmd = nullptr;
      return;
    }
    // Invoke command loop.
    const bool cmd_completed = current_cmd->on_cmd_loop();
    if (cmd_completed) {
      current_cmd = nullptr;
    }
    return;
  }

  // Try to read selection char of next command.
  static_assert(sizeof(data_buffer) >= 1);
  data_size = 0;
  if (!read_serial_bytes(1)) {
    return;
  }

  // Dispatch the next command by the selection char.
  current_cmd = find_command_handler_by_char(data_buffer[0]);
  if (current_cmd) {
    cmd_timer.reset(millis_now);
    data_size = 0;
    current_cmd->on_cmd_entered();
    // We call on_cmd_loop() on the next iteration, after updating the LED.
  } else {
    // Unknown command selector. We ignore it silently.
  }
}
