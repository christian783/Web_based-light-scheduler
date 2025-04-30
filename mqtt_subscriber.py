import subprocess
import json
import serial
import time
from datetime import datetime

# Serial connection to Arduino (adjust port as needed, e.g., COM3 on Windows or /dev/ttyUSB0 on Linux)
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for serial connection to establish

# MQTT topic to subscribe to
topic = "light/schedule"

# Function to send command to Arduino
def send_to_arduino(command):
    ser.write(command.encode())
    print(f"Sent to Arduino: {command}")

# Process MQTT messages
def process_schedule():
    # Start mosquitto_sub process to listen for messages
    process = subprocess.Popen(
        ["mosquitto_sub", "-h", "localhost", "-t", topic],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    last_on_time = None
    last_off_time = None

    while True:
        message = process.stdout.readline().strip()
        if message:
            try:
                # Parse the MQTT message
                schedule = json.loads(message)
                on_time = schedule['onTime']
                off_time = schedule['offTime']
                print(f"Received schedule - On: {on_time}, Off: {off_time}")

                last_on_time = on_time
                last_off_time = off_time
            except json.JSONDecodeError:
                print("Failed to decode MQTT message")
                continue

        # Check current time against schedule
        if last_on_time and last_off_time:
            current_time = datetime.now().strftime("%H:%M")
            on_hour, on_minute = map(int, last_on_time.split(":"))
            off_hour, off_minute = map(int, last_off_time.split(":"))
            current_hour, current_minute = map(int, current_time.split(":"))

            on_minutes = on_hour * 60 + on_minute
            off_minutes = off_hour * 60 + off_minute
            current_minutes = current_hour * 60 + current_minute

            # Determine if the light should be on or off
            if on_minutes <= current_minutes < off_minutes:
                send_to_arduino('1')  # Turn on
            else:
                send_to_arduino('0')  # Turn off

        time.sleep(1)  # Avoid excessive CPU usage

try:
    process_schedule()
except KeyboardInterrupt:
    print("Stopping subscriber...")
    ser.close()