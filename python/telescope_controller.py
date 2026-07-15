import serial
import time
from datetime import datetime

class TelescopeController:
    """
    Handles serial communication between Python and Arduino
    for telescope positioning
    """
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        Initialize serial connection
        
        Args:
            port (str): Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baud_rate (int): Communication speed (default 9600)
            timeout (int): Read timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.connected = False
        
    def connect(self):
        """Establish serial connection with Arduino"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE
            )
            time.sleep(2)  # Wait for Arduino to initialize
            self.connected = True
            print(f"✓ Connected to Arduino on {self.port} at {self.baud_rate} baud")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print("✓ Disconnected from Arduino")
    
    def point_telescope(self, azimuth, altitude):
        """
        Send positioning command to telescope
        
        Args:
            azimuth (float): Azimuth angle in degrees (0-360)
            altitude (float): Altitude angle in degrees (-90 to +90)
            
        Returns:
            bool: True if command succeeded, False otherwise
        """
        if not self.connected:
            print("✗ Arduino not connected")
            return False
        
        # Validate inputs
        if not (0 <= azimuth <= 360):
            print(f"✗ Invalid azimuth: {azimuth}° (must be 0-360°)")
            return False
        
        if not (-90 <= altitude <= 90):
            print(f"✗ Invalid altitude: {altitude}° (must be -90 to +90°)")
            return False
        
        # Format command: AZ:value,AL:value\n
        command = f"AZ:{azimuth:.1f},AL:{altitude:.1f}\n"
        
        try:
            # Send command
            self.ser.write(command.encode())
            print(f"→ Sent: {command.strip()}")
            
            # Read response
            response = self.ser.readline().decode().strip()
            print(f"← Received: {response}")
            
            if response == "OK":
                print(f"✓ Telescope pointing to AZ:{azimuth:.1f}°, AL:{altitude:.1f}°")
                return True
            elif "ERROR" in response:
                print(f"✗ Arduino error: {response}")
                return False
            else:
                print(f"✗ Unexpected response: {response}")
                return False
                
        except Exception as e:
            print(f"✗ Communication error: {e}")
            return False
    
    def get_status(self):
        """Get current telescope status"""
        if self.connected:
            print("✓ Telescope is connected and ready")
            return True
        else:
            print("✗ Telescope is not connected")
            return False
    
    def emergency_stop(self):
        """Emergency stop - point telescope to safe position"""
        print("⚠ EMERGENCY STOP - Moving to safe position...")
        return self.point_telescope(azimuth=0, altitude=0)


# Example usage
if __name__ == "__main__":
    # Initialize controller
    telescope = TelescopeController(port="COM3", baud_rate=9600)
    
    # Connect to Arduino
    if telescope.connect():
        # Point to a location (Azimuth: 245.5°, Altitude: 35.2°)
        telescope.point_telescope(azimuth=245.5, altitude=35.2)
        
        # Wait a bit
        time.sleep(2)
        
        # Point to another location
        telescope.point_telescope(azimuth=90, altitude=45)
        
        # Disconnect
        time.sleep(1)
        telescope.disconnect()
    else:
        print("Failed to connect to telescope")
