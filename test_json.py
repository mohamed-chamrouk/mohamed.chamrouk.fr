import json

with open('data.json', 'r') as f:
    data_json = json.load(f)

for track in data_json.json():
    print(track.track.name)
