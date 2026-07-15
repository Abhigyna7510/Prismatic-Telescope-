# Serial Communication Protocol 📡

## Overview

The Python application communicates with the Arduino microcontroller via USB serial connection to send telescope positioning commands.

## Connection Parameters

```
Baud Rate:    9600
Data Bits:    8
Stop Bits:    1
Parity:       None
Flow Control: None
Port:         COM3 (Windows) / /dev/ttyUSB0 (Linux) / /dev/ttyACM0 (Mac)
```

## Communication Format

### Command Structure

**Python → Arduino:**
```
AZ:{azimuth_value},AL:{altitude_value}\n
```

### Parameters

| Parameter | Range | Unit | Description |
|-----------|-------|------|-------------|
| `azimuth` | 0-360 | Degrees | Horizontal position (0° = North, 90° = East, 180° = South, 270° = West) |
| `altitude` | -90 to +90 | Degrees | Vertical position (-90° = Down, 0° = Horizon, +90° = Zenith) |

### Examples

```
Command: AZ:245.5,AL:35.2\n
Meaning: Point telescope to Azimuth 245.5°, Altitude 35.2°

Command: AZ:0,AL:90\n
Meaning: Point telescope straight up (Zenith)

Command: AZ:180,AL:0\n
Meaning: Point telescope South at horizon level
```

---

## Response Structure

**Arduino → Python:**
```
OK\n
```

The Arduino confirms receipt and execution of the command by responding with `OK\n`.

---

## Error Handling

### Invalid Commands

If the Arduino receives a malformed command:
```
ERROR:INVALID\n
```

### Out of Range Values

If values are outside acceptable range:
```
ERROR:RANGE\n
```

### Timeout

If no valid command received for 30 seconds:
```
READY\n
```

---

## Communication Sequence Diagram

```
Python Application
    │
    ├─→ "AZ:245.5,AL:35.2\n"  (Calculate and send)
    │
    │   ╔═══════════════════════╗
    │   ║   Arduino UNO         ║
    │   ║  - Parse command      ║
    │   ║  - Calculate PWM      ║
    │   ║  - Move servos        ║
    │   ║  - Wait for movement  ║
    │   ╚═══════════════════════╝
    │
    ←─ "OK\n"  (Command executed, ready for next)
    │
    └─→ [Wait ~500ms for servo movement]
```

---

## Conversion: Degrees to PWM Microseconds

The Arduino internally converts degrees to PWM pulse width:

### Formula
```
Pulse Width (µs) = 1500 + (Degrees * 5.555)

Where:
- 1500 µs = 90° (neutral/center position)
- Each degree = 5.555 µs
```

### Examples
```
0°   → 1500 + (0 * 5.555)   = 1500 µs
45°  → 1500 + (45 * 5.555)  = 1750 µs
90°  → 1500 + (90 * 5.555)  = 2000 µs
-45° → 1500 + (-45 * 5.555) = 1250 µs
```

---

## Command Timing

| Action | Timing |
|--------|--------|
| Command Send | Instant |
| Arduino Parse | < 10ms |
| Servo Movement | 200-500ms (depends on angle) |
| Arduino Response | < 5ms after movement complete |
| Next Command Ready | 500ms after last command |

---

## Buffer Management

- **Receive Buffer**: 64 bytes (Arduino)
- **Maximum Command Length**: 30 bytes
- **Input Queue**: Commands processed sequentially
- **Timeout**: 30 seconds of inactivity → Arduino sends "READY\n"

---

## Python Serial Example

```python
import serial
import time

# Open serial connection
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to initialize

# Send command
command = "AZ:245.5,AL:35.2\n"
ser.write(command.encode())

# Read response
response = ser.readline().decode().strip()
print(f"Response: {response}")

# Close connection
ser.close()
```

---

## Arduino Serial Example

```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    
    // Parse command: AZ:245.5,AL:35.2
    float azimuth = parseValue(command, "AZ:");
    float altitude = parseValue(command, "AL:");
    
    // Move servos
    moveServos(azimuth, altitude);
    
    // Send confirmation
    Serial.println("OK");
  }
}
```

---

## Debugging Commands

For testing, you can send these directly via Serial Monitor:

```
AZ:0,AL:0         → Point to North at Horizon
AZ:90,AL:0        → Point to East at Horizon
AZ:180,AL:0       → Point to South at Horizon
AZ:270,AL:0       → Point to West at Horizon
AZ:0,AL:90        → Point straight up (Zenith)
AZ:0,AL:-90       → Point straight down (Nadir)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No response from Arduino | Check serial port & baud rate |
| "ERROR:INVALID" | Check command format (AZ:value,AL:value\n) |
| "ERROR:RANGE" | Check values are within ±90 for altitude, 0-360 for azimuth |
| Servo moves wrong direction | Check servo calibration in Arduino code |
| Servo doesn't reach target | Increase wait time or check power supply |

---

## Next Steps

1. Upload the Arduino firmware (see `arduino/servo_controller.ino`)
2. Test with Arduino Serial Monitor
3. Run Python control script (see `python/main.py`)
