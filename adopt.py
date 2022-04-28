import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt

class ShipOwner:
    # def __init__(self, economy, environment, safety, labour, learning):
    def __init__(self, economy=1.0, environment=0.0, safety=0.0, labour=0.0):
        self.economy = economy
        self.environment = environment
        self.safety = safety
        self.labour = labour
        # self.learning = learning

    def reset(self, economy, environment, safety, labour):
        self.economy = economy
        self.environment = environment
        self.safety = safety
        self.labour = labour
 
    def select_ship(self, spec, cost, year, ship_age):
        labour_cost = spec.num_sf * cost.Seafarer[year] \
                    + spec.num_so * cost.ShoreOperator[year]
        fuel_cost   = spec.foc * cost.Fuel[year]
        com_sec_cost= spec.sec_cost * cost.CS[year] \
                    + spec.com_cost * cost.Comm[year]
        opex_sum    = labour_cost + fuel_cost + com_sec_cost
        capex_sum   = spec.sa_cost * cost.Situ[year] \
                    + spec.pl_cost * cost.Plan[year] \
                    + spec.ex_cost * cost.Exec[year] \
                    + spec.ro_cost * cost.RemOpe[year] \
                    + spec.rm_cost * cost.RemMon[year]
        ac_loss     = spec.acc_ratio * cost.ExpLoss[year]
        annual_cost = opex_sum + capex_sum/ship_age + ac_loss
        sf_sum      = spec.num_sf + spec.num_so

        select_parameter = annual_cost * self.economy \
                        + fuel_cost * self.environment \
                        + ac_loss * self.safety \
                        + labour_cost * self.labour #要正規化 
        select      = select_parameter.idxmin()   
        # seafarerの増減率をながらかにするようなファクター → TBD

        return select, annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost