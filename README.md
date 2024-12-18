# iBeacon-and-Accelerometer-broadcasts-

Requirements :- 
Python 3.8 or above
A laptop with a Bluetooth adapter (Linux or macOS)
The following Python packages:
bleak
nest-asyncio

Installation :- 

Clone the repository:

bash
git clone  https://github.com/bubainayak1/iBeacon-and-Accelerometer-broadcasts-.git
cd repository-name
Install the required dependencies:

bash
pip install -r requirements.txt
Running the Code
Run the BLE scanner:

bash
python main.py (becon_test.py)

The program will scan for BLE devices, extract accelerometer data, and determine if the beacon is moving or stationary.
If a BLE device with accelerometer data is detected, the accelerometer readings and movement status will be printed.
