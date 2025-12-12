import requests
import random
import time
import math

API_URL = "https://angelofdeath.pythonanywhere.com/api/update-location"

# Mina center (same as backend)
CENTER_LAT = 21.4167
CENTER_LNG = 39.9000

# number of simulated pilgrims
NUM_PILGRIMS = 100

# movement step size (degrees)
STEP = 0.00025  # ~20–25 meters per update

# store all simulated pilgrims
pilgrims = {}

# random starting point around Mina
def random_start():
    lat = CENTER_LAT + (random.random() - 0.5) * 0.004  # ±0.002
    lng = CENTER_LNG + (random.random() - 0.5) * 0.004
    return lat, lng

# initialize pilgrims
for i in range(1, NUM_PILGRIMS + 1):
    pid = f"P{i:03d}"  # P001, P002, ...
    lat, lng = random_start()
    pilgrims[pid] = {"lat": lat, "lng": lng}

print(f"🚀 Simulating {NUM_PILGRIMS} pilgrims...")

# main loop
while True:
    for pid, p in pilgrims.items():

        # random movement
        p["lat"] += random.uniform(-STEP, STEP)
        p["lng"] += random.uniform(-STEP, STEP)

        # send to backend
        try:
            requests.post(
                API_URL,
                json={"id": pid, "lat": p["lat"], "lng": p["lng"]},
                timeout=2
            )
        except Exception as e:
            print(f"Error updating {pid}: {e}")

    print("✓ Tick update sent.")
    time.sleep(1)  # update every 1 second
