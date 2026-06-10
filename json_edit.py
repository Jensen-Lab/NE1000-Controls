import json

with open(".exp_metadata.json", "r") as f:
    data = json.load(f)

nozzle_specs = {
    85: {"length": 24, "radius": 25}
}

for measurement in data.values():
    nozzle = measurement.get("nozzle")

    if nozzle in nozzle_specs:
        measurement.update(nozzle_specs[nozzle])

with open(".exp_metadata.json", "w") as f:
    json.dump(data, f, indent=4)