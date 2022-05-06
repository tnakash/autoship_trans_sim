import os
import csv
from re import S
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt
class Investor():
    def __init__(self):
        self.invest_tech = 'None'
        self.invest_amount = 0
        return

    def reset(self, invest, amount):
        self.invest_tech = invest
        self.invest_amount = amount

    # def investment(self, cost, TRL, year, delay, invest, budget):
    def invest(self, tech):
        if self.invest_tech == 'Berth':
            # tech[self.invest_tech].Rexp += self.invest_amount
            tech.Rexp[0] += self.invest_amount
        elif self.invest_tech == 'Navi':
            # tech.navi_exp += self.invest_amount
            tech.Rexp[1] += self.invest_amount
        elif self.invest_tech == 'Moni':
            # tech.moni_exp += self.invest_amount
            tech.Rexp[2] += self.invest_amount

        return tech

    # def invest(self, tech, year, delay):
    #     if self.invest_tech == 'Comm':
    #         tech.Comm[year+delay:] *= 0.8
    #         # TRL.Comm[year+delay:] *= 1.1 * budget
    #     elif self.invest_tech == 'Situ':
    #         tech.Situ[year+delay:] *= 0.8
    #         # TRL.Comm[year+delay:] *= 1.1 * budget
    #     elif self.invest_tech == 'Plan':
    #         cost.Plan[year+delay:] *= 0.8
    #         # TRL.Plan[year+delay:] *= 1.1 * budget
    #     elif self.invest_tech == 'Exec':
    #         cost.Exec[year+delay:] *= 0.8
    #         # TRL.Plan[year+delay:] *= 1.1 * budget