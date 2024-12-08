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
MOVEMENT_THRESHOLD = 1.0  # Adjust based on your accelerometer sensitivity

# Function to process accelerometer data and detect movement
def process_accelerometer_data(x, y, z):
    """
    Function to process accelerometer data (X, Y, Z) and detect movement.
    """
    # Calculate the magnitude of the acceleration vector (Euclidean norm)
    magnitude = math.sqrt(x**2 + y**2 + z**2)

    # Check if movement is detected (based on threshold)
    movement_status = "Moving" if magnitude > MOVEMENT_THRESHOLD else "Stationary"

    # Print the accelerometer data and the movement status
    print(f"Accelerometer Data (m/s²) -> X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}, Magnitude: {magnitude:.2f} m/s² -> Movement Status: {movement_status}")

    return movement_status

# Function to parse accelerometer data from raw BLE packets
def parse_accelerometer_data(raw_packet):
    """
    Parse accelerometer data from a raw BLE advertisement packet.
    """
    try:
        if len(raw_packet) >= 12:  # Ensure packet has enough data for accelerometer values
            # Extract accelerometer section (6 bytes starting from offset 6)
            accel_data = raw_packet[6:12]
            
            # Unpack 6 bytes into three 16-bit signed integers (X, Y, Z)
            x, y, z = struct.unpack('<hhh', accel_data)  # little-endian format
            # Scale the raw data to m/s² (adjust SCALE_FACTOR based on your sensor)
            SCALE_FACTOR = 1.0  # Update as per your sensor's documentation
            x = x * SCALE_FACTOR
            y = y * SCALE_FACTOR
            z = z * SCALE_FACTOR
            return x, y, z
        else:
            print("Invalid raw packet: Not enough data for accelerometer readings.")
            return None
    except Exception as e:
        print(f"Error parsing accelerometer data: {e}")
        return None

# Callback function to process each discovered device
async def detection_callback(device, advertisement_data):
    """
    Callback for handling detected BLE devices and processing accelerometer data.
    """
    print("=" * 50)
    print(f"Device Address: {device.address}")
    print(f"RSSI: {device.rssi} dBm")
    
    if advertisement_data.service_data:
        for service_uuid, service_data in advertisement_data.service_data.items():
            print(f"Service UUID: {service_uuid}, Data (hex): {service_data.hex()}")

            # Check if the packet contains accelerometer data
            parsed_data = parse_accelerometer_data(service_data)
            if parsed_data:
                x, y, z = parsed_data
                process_accelerometer_data(x, y, z)

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
