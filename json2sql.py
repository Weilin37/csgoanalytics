import pandas as pd
import json

with open("json/demo.json", "r") as read_file:
    data = json.load(read_file)

data = json.loads(data)

data[]