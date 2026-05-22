import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# Generate 1000 meter IDs
meters = [str(random.randint(1000000000, 9999999999)) for _ in range(1000)]

# Realistic power pattern based on hour of day
def get_power_by_hour(hour):
    if 6 <= hour <= 9:      # Morning peak
        return random.uniform(3.0, 5.0)
    elif 17 <= hour <= 21:  # Evening peak
        return random.uniform(4.0, 6.0)
    elif 22 <= hour <= 23:  # Night
        return random.uniform(0.5, 1.5)
    elif 0 <= hour <= 5:    # Late night
        return random.uniform(0.3, 1.0)
    else:                   # Normal day
        return random.uniform(1.5, 3.0)

# Connect to EMQX
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

print(f"Starting data generation for {len(meters)} meters...")
print("Press Ctrl+C to stop")

count = 0
while True:
    hour = datetime.now().hour
    for meter_id in meters:
        power = get_power_by_hour(hour)
        voltage = random.uniform(218.0, 242.0)
        current = power / (voltage / 1000)
        frequency = random.uniform(49.8, 50.2)
        energy = power * (5/60)

        message = {
            "meter_id": meter_id,
            "timestamp": datetime.utcnow().isoformat(),
            "power": round(power, 3),
            "voltage": round(voltage, 3),
            "current": round(current, 3),
            "frequency": round(frequency, 3),
            "energy": round(energy, 6)
        }

        client.publish(f"energy/meters/{meter_id}", json.dumps(message))
        count += 1

    print(f"Published {count} messages so far...")
    time.sleep(300)  # Wait 5 minutes