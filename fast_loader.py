import psycopg2
import random
from datetime import datetime, timedelta
import io

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="energy_db",
    user="postgres",
    password="password"
)
cur = conn.cursor()

# Generate 1000 meter IDs once
random.seed(42)
meters = [str(random.randint(1000000000, 9999999999)) for _ in range(1000)]

# Realistic power pattern
def get_power_by_hour(hour):
    if 6 <= hour <= 9:
        return random.uniform(3.0, 5.0)
    elif 17 <= hour <= 21:
        return random.uniform(4.0, 6.0)
    elif 22 <= hour <= 23:
        return random.uniform(0.5, 1.5)
    elif 0 <= hour <= 5:
        return random.uniform(0.3, 1.0)
    else:
        return random.uniform(1.5, 3.0)

# Generate 4 weeks of data
start_date = datetime.utcnow() - timedelta(weeks=4)
end_date = datetime.utcnow()
current_time = start_date

print("Starting fast data load...")
print("Clearing old data...")
cur.execute("TRUNCATE energy_readings;")
conn.commit()

total = 0
# Process one day at a time to save memory
one_day = timedelta(days=1)
day_start = start_date

while day_start <= end_date:
    day_end = min(day_start + one_day, end_date)
    current_time = day_start
    
    # Build CSV buffer for this day
    buffer = io.StringIO()
    
    while current_time <= day_end:
        for meter_id in meters:
            power = get_power_by_hour(current_time.hour)
            voltage = random.uniform(218.0, 242.0)
            current_val = power / (voltage / 1000)
            frequency = random.uniform(49.8, 50.2)
            energy = power * (5/60)

            buffer.write(
                f"{meter_id}\t"
                f"{current_time.isoformat()}\t"
                f"{round(power, 3)}\t"
                f"{round(voltage, 3)}\t"
                f"{round(current_val, 3)}\t"
                f"{round(frequency, 3)}\t"
                f"{round(energy, 6)}\n"
            )
        current_time += timedelta(minutes=5)

    # Use COPY for fast insert
    buffer.seek(0)
    cur.copy_from(
        buffer,
        'energy_readings',
        columns=('meter_id', 'timestamp', 'power', 'voltage', 'current', 'frequency', 'energy')
    )
    conn.commit()
    buffer.close()

    # Count and report
    day_rows = 1000 * int((day_end - day_start).total_seconds() / 300)
    total += day_rows
    print(f"Loaded day {day_start.strftime('%Y-%m-%d')} — Total so far: ~{total} rows")

    day_start += one_day

print(f"\nDone! Verifying final count...")
cur.execute("SELECT COUNT(*) FROM energy_readings;")
print(f"Total rows in database: {cur.fetchone()[0]}")
cur.close()
conn.close()