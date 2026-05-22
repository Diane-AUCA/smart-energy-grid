import paho.mqtt.client as mqtt
import psycopg2
import json
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="energy_db",
    user="postgres",
    password="password"
)
cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS energy_readings (
        meter_id VARCHAR(10),
        timestamp TIMESTAMPTZ NOT NULL,
        power DOUBLE PRECISION,
        voltage DOUBLE PRECISION,
        current DOUBLE PRECISION,
        frequency DOUBLE PRECISION,
        energy DOUBLE PRECISION
    );
""")
conn.commit()
print("Table created successfully!")

# When connected to EMQX
def on_connect(client, userdata, flags, rc):
    print("Connected to EMQX broker!")
    client.subscribe("energy/meters/#")
    print("Subscribed to energy/meters/#")

# When a message arrives
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        cur.execute("""
            INSERT INTO energy_readings 
            (meter_id, timestamp, power, voltage, current, frequency, energy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['meter_id'],
            data['timestamp'],
            data['power'],
            data['voltage'],
            data['current'],
            data['frequency'],
            data['energy']
        ))
        conn.commit()
        print(f"Saved reading from meter {data['meter_id']}")
    except Exception as e:
        print(f"Error: {e}")

# Start MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
print("Starting subscriber... Press Ctrl+C to stop")
client.loop_forever()