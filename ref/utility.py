import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt

def clean(filename):
    TEAM_CASE_PATH = f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}"
    if not os.path.exists(TEAM_CASE_PATH):
        os.makedirs(TEAM_CASE_PATH)
    with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
              f"case{filename['simulation_case']:03}.yml", 'w') as yml:
        yaml.safe_dump(None)


def save_yaml(data, filename):
    yaml.safe_dump({data.__class__.__name__: vars(data)},
                   filename,
                   sort_keys=False, # require "!pip install PyYAML==5.4.1"
                   default_flow_style=False)


def save_dict(data, filename):
    with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
              f"case{filename['simulation_case']:03}_input.csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "Fuel & GHG cost growth", "Investment in Situation Awareness",
            "Investment in Planning", "Investment in Execution",
            "Investment in Remote"
        ])
        writer.writeheader()
        writer.writerows([data])