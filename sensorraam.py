import adafruit_dht
import board
import csv
import time
from datetime import datetime

# Initialize the DHT22 sensor (connected to GPIO"")
dht_device = adafruit_dht.DHT22(board.D17)

# CSV file path
csv_file = "sensorraam.csv"

time.sleep(200)

# Write CSV header if the file doesn't exist
try:
    with open(csv_file, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperature_C", "humidity_percent"])
except FileExistsError:
    pass  # File already exists

# Continuous loop
try:
    while True:
        try:
            # Read values
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            if temperature is not None and humidity is not None:
                # Format timestamp as day-month-year hour:minute
                timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
                print(f"{timestamp} | Temp: {temperature:.1f}°C | Humidity: {humidity:.1f}%")

                # Append to CSV
                with open(csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, temperature, humidity])

            else:
                print("Failed to retrieve data from sensor")

        except RuntimeError as e:
            # Sensor read errors are normal sometimes
            print(f"Sensor error: {e.args[0]}")
            time.sleep(2.0)
            continue

        time.sleep(300)  # Wait 5 minute between reads

except KeyboardInterrupt:
    print("Stopping humidity logger")

finally:
    dht_device.exit()
