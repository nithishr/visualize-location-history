import json
import datetime

# Get the Location History from Google Takeout
with open("Location History.json", "r") as location_history:
    location_data = json.loads(
        location_history.read(), parse_float=float, parse_int=int
    )

cleaned_location_history = []
count = 0

for location in location_data["locations"]:
    cl_location = {
        "ts": datetime.datetime.fromtimestamp(float(location["timestampMs"]) / 1000.0),
        "geo": {
            "lat": location["latitudeE7"] / 10000000,
            "lon": location["longitudeE7"] / 10000000,
        },
    }
    cleaned_location_history.append(cl_location)

with open("cb_clean_data.json", "w") as out_file:
    out_file.write(json.dumps(cleaned_location_history, default=str))

print("Cleaning completed")
