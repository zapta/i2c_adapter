// #include <Adafruit_TinyUSB.h>
#include <Arduino.h>
#include <Wire.h>

// TODO: Add static asserts about the buffer size.
// TODO: Clear i2c available buffer before i2c read operation.
// TODO: Determine optimal led blinking policy.
// TODO: Investigate if we get a better resolution or failure errors.
// TODO: Add a RESET command.
// TODO: Add an INFO command, with version, etc.
// TODO: Add support for pullup control.

// NOTE: Arduino Wire API documentation is here
// https://www.arduino.cc/reference/en/language/functions/communication/wire/

// All command bytes must arrive within this time period.
static constexpr uint32_t kCommandTimeoutMillis = 250;
// static constexpr uint32_t kCommandTimeoutMillis = 0xffffffff;

// static uint8_t cmd_buffer[20];
static uint8_t data_buffer[512];

static uint32_t last_command_start_millis = 0;

// Read exactly n chanrs to data buffer. If not enough bytes, none is read
// and the function returns false.
static bool read_input_bytes(uint8_t* bfr, uint16_t n) {
  // Handle the case where not enough chars.
  const int avail = Serial.available();
  if (avail < (int)n) {
    return false;
  }

  // TODO: Verify actual read == n;
  size_t actual_read = Serial.readBytes(bfr, n);
  (void)actual_read;
  return true;
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
    if (!read_input_bytes(data_buffer, 1)) {
      return false;
    }
    Serial.write(data_buffer[0]);
    return true;
  }
} echo_cmd_handler;

// RESET command. Clears pending errors. Used for the Greenpack
// erase errata.
//
// Command:
// - byte 0:  't'
//
// Response:
// - byte 0:  'K' to indicate OK. This command doesn't fail.
//
static class ResetCommandHandler : public CommandHandler {
 public:
  ResetCommandHandler() : CommandHandler("RESET") {}
  virtual bool on_cmd_loop() override {
    Wire.end();
    Wire.begin();
    // static_assert(sizeof(data_buffer) >= 1);
    // if (!read_input_bytes(data_buffer, 1)) {
    //   return false;
    // }
    Serial.write('K');
    return true;
  }
} reset_cmd_handler;

// INFO command. Provides information about this driver. Currently
// it's a skeleton for future values that will be returned.
//
// Command:
// - byte 0:  'i'
//
// Response:
// - byte 0:  Number of bytes to follow. Equals 1.
// - byte 1:  API version of this driver. Equals 1.
static class InfoCommandHandler : public CommandHandler {
 public:
  InfoCommandHandler() : CommandHandler("INFO") {}
  virtual bool on_cmd_loop() override {
    Serial.write(0x01);  // Number of bytes to follow.
    Serial.write(0x01);  // API version.
    return true;
  }
} info_cmd_handler;

// WRITE command. Writes N bytes to an I2C device.
//
// Command:
// - byte 0:    'w'
// - byte 1:    Device's I2C address in the range 0-127.
// - byte 2,3:  Number bytes to write. Big endian. Should be in the
//              range 1 to 512.
// - Byte 4...  The data bytes to write.
//
// Error response:
// - byte 0:    'E' for error.
// - byte 1:    Additional device specific internal error info per the list
// below.
//
// OK response
// - byte 0:    'K' for 'OK'.
//
// Additional error info:
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
    // Temp, testing the errata workaround
    // Wire.end();
    // Wire.begin();
  }
  virtual bool on_cmd_loop() override {
    // Read command header.
    if (!_got_cmd_header) {
      static_assert(sizeof(data_buffer) >= 3);
      if (!read_input_bytes(data_buffer, 3)) {
        return false;
      }
      _device_addr = data_buffer[0];
      _count = (((uint16_t)data_buffer[1]) << 8) + data_buffer[2];
      _got_cmd_header = true;
    }

    // Validate the command header.
    uint8_t status = (_device_addr > 127) ? 0x08 : (_count > 512) ? 0x09 : 0x00;
    if (status != 0x00) {
      Serial.write('E');
      Serial.write(status);
      return true;
    }

    // Read the data bytes
    static_assert(sizeof(data_buffer) >= 512);
    if (!read_input_bytes(data_buffer, _count)) {
      return false;
    }

    // Clear previous write errors.
    //
    // Serial.print("["); Serial.print(_device_addr); Serial.print("]");
    // Serial.print("["); Serial.print(_count); Serial.print("]");
    // Serial.print("["); Serial.print(data_buffer[0]); Serial.print("]");
    // Serial.print("["); Serial.print(data_buffer[1]); Serial.print("]");

    // Device address is 7 bits LSB.
    // const uint8_t device_addr = data_buffer[0];
    // Wire.clearTimeoutFlag();
    Wire.beginTransmission(_device_addr);
    Wire.write(data_buffer, _count);
    status = Wire.endTransmission(true);

    // NOTE: Due to this Erata, some GreenPacks may not nack when we write
    // to the erase byte. We want to let the user to ignore this error as a 
    // woraround.
    // TODO: What do we want to do here with Wire.getTimeout()?
    
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
//              range 1 to 512.
//
// Error  Response:
// - byte 0:    'E' for 'error'.
// - byte 1:    Additional device specific internal error info per the list
// below.
//
// OK Response:
// - byte 0:    'K' for 'OK'.
// - byte 1,2:  Number bytes to follow. Big endian. Identical to the
//              count in the command.
// - byte 3...  The bytes read.
//
// Additional error info:
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
    if (!read_input_bytes(data_buffer, 3)) {
      return false; // try later
    }

    // Sanity check the command
    const uint8_t device_addr = data_buffer[0];
    const uint16_t count = (((uint16_t)data_buffer[1]) << 8) + data_buffer[2];
    uint8_t status = (device_addr > 127) ? 0x08 : (count > 512) ? 0x09 : 0x00;
    if (status != 0x00) {
      Serial.write('E');
      Serial.write(status);
      return true;
    }

    // Read the bytes from the I2C devcie.
    const size_t actual_count = Wire.requestFrom(device_addr, count, true);

    // Sanity check the response.
    status = (actual_count != count)       ? 0x01
             : (Wire.available() != count) ? 0x02
                                           : 0x00;
    if (status != 0x00) {
      Serial.write('E');
      Serial.write(status);
      return true;
    }

    // Here when OK, send status, count, and data.
    Serial.write('K');
    // Serial.print("["); Serial.print(count); Serial.print("]");
    Serial.write(count >> 8);
    Serial.write(count & 0x00ff);
    for (uint16_t i = 0; i < count; i++) {
      Serial.write(Wire.read());
    }
    return true;
  }

} read_cmd_handler;

// Given a command char, return a Command pointer or null if invalid command
// char.
static CommandHandler* find_command_handler_by_char(const char cmd_char) {
  switch (cmd_char) {
    case 'e':
      return &echo_cmd_handler;
    case 't':
      return &reset_cmd_handler;
    case 'i':
      return &info_cmd_handler;
    case 'w':
      return &write_cmd_handler;
    case 'r':
      return &read_cmd_handler;
    default:
      return nullptr;
  }
}

void setup() {
  // SerialUSB.begin(19200);
  pinMode(LED_BUILTIN, OUTPUT);

  // USB serial.
  // Per https://arduino-pico.readthedocs.io/en/latest/serial.html
  Serial.begin(115200);

  // Pins are SD=4, SCL=5
  Wire.setClock(100000);   // 100Khz.
  Wire.setTimeout(50000);  // 50ms timeout.
  Wire.begin();
}

// If in command, points to the command handler.
static CommandHandler* current_cmd = nullptr;

void loop() {
  // Serial.printf("Loop %s\n", current_cmd? current_cmd->name() : "-");
  // delay(300);

  Serial.flush();
  const uint32_t millis_now = millis();
  const bool blink =
      current_cmd || (millis_now - last_command_start_millis) < 200;
  // millis_now & 0x0040 : millis_now & 0x0100;
  // const bool blink = current_cmd;
  digitalWrite(LED_BUILTIN, blink);

  // If a command is in progress, handle it.
  if (current_cmd) {
    bool cmd_completed = current_cmd->on_cmd_loop();
    if (!cmd_completed && (millis() - last_command_start_millis > kCommandTimeoutMillis)) {
      current_cmd->on_cmd_aborted();
      cmd_completed = true;
    }
    if (cmd_completed) {
      current_cmd = nullptr;
    }
    return;
  }

  // Not in a command. Try to read selection char of next command.
  static_assert(sizeof(data_buffer) >= 1);
  if (!read_input_bytes(data_buffer, 1)) {
    return;
  }

  // Dispatch the next command.
  // const char cmd_char = Serial.read();
  current_cmd = find_command_handler_by_char(data_buffer[0]);
  if (current_cmd) {
    // Clear potential I2C errors.
    // Wire.clearWriteError();
    // Started a new command.
    last_command_start_millis = millis_now;
    current_cmd->on_cmd_entered();
  } else {
    // Unknown command selector. We ignore it silently.
  }
}
