import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt

class PolicyMaker():
    def __init__(self, filename, info=None):
        with open(src_path + default_input, 'r') as yml:
            data = yaml.safe_load(yml)
        data = data['PolicyMaker']
        if info is None:
            self.name = data['name']
            self.sa_growth = data['sa_growth']['Medium']
            self.pl_growth = data['pl_growth']['Medium']
            self.ex_growth = data['ex_growth']['Medium']
            self.ro_growth = data['re_growth']['Medium']
            self.rm_growth = data['re_growth']['Medium']
            self.fuel_growth = data['fuel_growth']['Medium']
        else:
            self.name = info['name']
            self.sa_growth = data['sa_growth'][info['sa_growth']]
            self.pl_growth = data['pl_growth'][info['pl_growth']]
            self.ex_growth = data['ex_growth'][info['ex_growth']]
            self.ro_growth = data['re_growth'][info['re_growth']]
            self.rm_growth = data['re_growth'][info['re_growth']]
            self.fuel_growth = data['fuel_growth'][info['fuel_growth']]
    
        with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                  f"case{filename['simulation_case']:03}.yml", 'a') as yml:
            save_yaml(self, yml)
