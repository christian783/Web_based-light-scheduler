import asyncio
import websockets
import json
import subprocess

async def handle_schedule(websocket, path):
    try:
        async for message in websocket:
            # Parse the incoming schedule
            schedule = json.loads(message)
            on_time = schedule['onTime']
            off_time = schedule['offTime']
            print(f"Received schedule - On: {on_time}, Off: {off_time}")

            # Forward the schedule to MQTT topic using mosquitto_pub
            topic = "light/schedule"
            payload = json.dumps({"onTime": on_time, "offTime": off_time})
            subprocess.run([
                "mosquitto_pub",
                "-h", "localhost",  # MQTT broker host
                "-t", topic,        # MQTT topic
                "-m", payload       # Message payload
            ])
            print(f"Published to MQTT topic {topic}: {payload}")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

# Start the WebSocket server
start_server = websockets.serve(handle_schedule, "localhost", 8765)

# Run the server
asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server running on ws://localhost:8765")
asyncio.get_event_loop().run_forever()