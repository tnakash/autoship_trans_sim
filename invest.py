import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt
class Investor():
    def __init__(self):
        return

    # def investment(self, cost, TRL, year, delay, invest, budget):
    def investment(self, cost, year, delay, invest):
        if invest == 'Comm':
            cost.Comm[year+delay:] *= 0.8
            # TRL.Comm[year+delay:] *= 1.1 * budget
        elif invest == 'Situ':
            cost.Situ[year+delay:] *= 0.8
            # TRL.Comm[year+delay:] *= 1.1 * budget
        elif invest == 'Plan':
            cost.Plan[year+delay:] *= 0.8
            # TRL.Plan[year+delay:] *= 1.1 * budget
        elif invest == 'Exec':
            cost.Exec[year+delay:] *= 0.8
            # TRL.Plan[year+delay:] *= 1.1 * budget