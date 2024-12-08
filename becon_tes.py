# The device address (so you know which device the data belongs to).
# The service UUID (to confirm which service is providing the data).
# The raw accelerometer data (for debugging).
# The movement status based on the accelerometer data.

import nest_asyncio
import struct
import math
import signal
import sys
import asyncio
from bleak import BleakScanner

# Apply nest_asyncio to allow asyncio in Jupyter environments
nest_asyncio.apply()

# Threshold to detect movement (in m/s²)
MOVEMENT_THRESHOLD = 1.0  # You can adjust this based on your accelerometer sensitivity
ACCELEROMETER_SERVICE_UUID = "0000fe2c-0000-1000-8000-00805f9b34fb"  # Replace with actual UUID if available

# Function to process accelerometer data and detect movement
def process_accelerometer_data(data):
    """
    Function to process accelerometer data (XYZ values) and detect movement.
    """
    if len(data) >= 6:  # Assuming 6 bytes of data for X, Y, Z accelerometer readings (2 bytes each)
        # Unpack the 6 bytes of data into three 16-bit signed integers (X, Y, Z)
        x, y, z = struct.unpack('<hhh', data[:6])  # little-endian 16-bit signed integers
        
        # Convert from raw data to acceleration in m/s² (assuming raw data is in some scaled unit)
        # You may need to adjust these scaling factors based on your sensor's calibration.
        SCALE_FACTOR = 1.0  # Adjust this scaling factor according to your sensor's documentation
        x_acc = x * SCALE_FACTOR
        y_acc = y * SCALE_FACTOR
        z_acc = z * SCALE_FACTOR

        # Calculate the magnitude of the acceleration vector (Euclidean norm)
        magnitude = math.sqrt(x_acc**2 + y_acc**2 + z_acc**2)

        # Check if movement is detected (based on threshold)
        movement_status = "Moving" if magnitude > MOVEMENT_THRESHOLD else "Stationary"

        # Print the accelerometer data and the movement status in a readable way
        print(f"Accelerometer Data (m/s²) -> X: {x_acc:.2f}, Y: {y_acc:.2f}, Z: {z_acc:.2f}, Magnitude: {magnitude:.2f} m/s² -> Movement Status: {movement_status}")

        return movement_status
    else:
        return "Invalid data"

# Callback function to process each discovered device
async def detection_callback(device, advertisement_data):
    """
    Callback for handling detected BLE devices and processing accelerometer data.
    """
    print("=" * 50)
    print(f"Scanning... Device found: {device.address}")
    print(f"RSSI: {device.rssi} dBm")
    
    if advertisement_data.service_data:
        # Iterate through all service data found in the advertisement
        for service_uuid, service_data in advertisement_data.service_data.items():
            print(f"Service UUID: {service_uuid}, Data (hex): {service_data.hex()}")
            
            if service_uuid == ACCELEROMETER_SERVICE_UUID:  # If it's an accelerometer service
                print("Accelerometer data found!")
                movement_status = process_accelerometer_data(service_data)
                print(f"Device: {device.address}, Accelerometer Data: {service_data.hex()} -> Movement Status: {movement_status}")
            else:
                print(f"Service UUID {service_uuid} does not match accelerometer service UUID.")

# Function to scan BLE packets from nearby devices
async def scan_ble_packets():
    """
    Scan for BLE devices and process their service data.
    """
    scanner = BleakScanner(detection_callback)
    print("Starting BLE scan...")

    try:
        await scanner.start()
        await asyncio.sleep(60)  # Scan for 60 seconds
    finally:
        await scanner.stop()
        print("Scan completed.")

# Function to handle graceful exit on KeyboardInterrupt
def handle_exit_signal(signal, frame):
    print("\nExiting program...")
    sys.exit(0)

# Set up the keyboard interrupt handler (Ctrl+C)
signal.signal(signal.SIGINT, handle_exit_signal)

# Run the BLE scan in the asyncio event loop
if __name__ == "__main__":
    try:
        asyncio.run(scan_ble_packets())
    except KeyboardInterrupt:
        print("\nScan interrupted by user. Exiting...")
