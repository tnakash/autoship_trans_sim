import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt

class Tech():
    def __ini__(self, tech_list):
        self.Tech = [Berth, Navi, Moni]

                self.Tech = [Berth, Navi, Moni]
        self.Tech = ['Berth', 'Navi', 'Moni']
        for s in self.Tech:
            self.s.exp = 0
            self.s.TRL_ini = aaa.TRL_init
            self.s.cost = (10-self.s.TRL_ini)*s.min_cost
        
    def get_tech(self, invest_matrix, Year):
        for s in self.Tech:
            self.s.exp += invest_matrix.s
            self.s.TRL = self.s.TRL_ini + Berth.exp//Berth.TRLfactor
            self.s.cost = (10-self.s.TRL) * s.min_cost


    def get_tech_df_ini(self, tech_yml):
        tech_list = ['Berth', 'Navi', 'Moni'] # 本来はymlから
        self.tech_list = ['cost', 'TRL', 'Rexp', 'Mexp', 'Oexp']

        for s in tech_list:
            self[s].cost = [s]['min_cost']
            self[s].TRL = [s]['TRL_ini']
            self[s].Rexp = [s]['R&D_exp']
            self[s].Mexp = [s]['Man_exp']
            self[s].Oexp = [s]['Ope_exp']
            
            self.s.TRL_ini = aaa.TRL_init
            self.s.cost = (10-self.s.TRL_ini)*s.min_cost
        
    def get_tech(self, invest_matrix, Year):
        for s in self.Tech:
            self.s.exp += invest_matrix.s
            self.s.TRL = self.s.TRL_ini + Berth.exp//Berth.TRLfactor
            self.s.cost = (10-self.s.TRL) * s.min_cost
        
        return tech

# class Ship():
#     def __ini__(self, config_list):
#         self.Config = config_list # ship.Tech
        
#     def get_tech(self, invest_matrix, Year):
#         for s in self.Config:
#             self.s.exp += invest_matrix.s
#             self.s.TRL = self.s.TRL_ini + Berth.exp//Berth.TRLfactor
#             self.s.cost = (10-self.s.TRL) * s.min_cost