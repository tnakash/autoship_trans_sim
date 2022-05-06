import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt
class ShipOwner:
    # def __init__(self, economy, environment, safety, labour, learning):
    def __init__(self, economy=1.0, environment=0.0, safety=0.0, labour=0.0, current_fleet=None, num_newbuilding=None):
        self.economy = economy
        self.environment = environment
        self.safety = safety
        self.labour = labour
        # ship number with config and built year
        self.fleet = current_fleet
        self.num_newbuiding = num_newbuilding

    def reset(self, economy, environment, safety, labour):
        self.economy = economy
        self.environment = environment
        self.safety = safety
        self.labour = labour

    def select_ship(self, spec):
        labour_cost, fuel_cost, capex_sum, opex_sum, voyex_sum, addcost_sum = self.calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum

        select_parameter = annual_cost * self.economy \
                        + fuel_cost * self.environment \
                        + addcost_sum * self.safety \
                        + labour_cost * self.labour #要修正
        select = select_parameter.idxmin()   

        return select

    def purchase_ship(self, select, year):
        # new = pd.DataFrame([[self.num_newbuiding['year'][year]], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0]])
        # print(year, select, self.num_newbuiding['year'][year], self.num_newbuiding['ship'][year])
        # new[select+1]=self.num_newbuiding['ship'][year]
        self.fleet.loc[len(self.fleet.year)] = 0
        self.fleet.at[len(self.fleet.year)-1, 'year'] = self.fleet.at[len(self.fleet.year)-2, 'year'] + 1
        self.fleet.at[len(self.fleet.year)-1, 'config'+str(select)] = self.num_newbuiding['ship'][year]
        print(self.fleet)

    def calculate_assumption(self, spec):
        labour_cost = spec.crew_cost + spec.SCC_Personal
        fuel_cost   = spec.fuel_cost_ME + spec.fuel_cost_AE 
        capex_sum   = spec.material_cost + spec.integrate_cost
        opex_sum    = spec.crew_cost + spec.store_cost + spec.maintenance_cost + spec.insurance_cost+ spec.general_cost + spec.dock_cost
        voyex_sum   = spec.port_call + spec.fuel_cost_ME + spec.fuel_cost_AE
        addcost_sum = spec.SCC_Capex + spec.SCC_Opex + spec.SCC_Personal + spec.Mnt_in_port
        
        return labour_cost, fuel_cost, capex_sum, opex_sum, voyex_sum, addcost_sum
    

    # def select_ship(self, spec, cost, year, ship_age):
    #     labour_cost, fuel_cost, com_sec_cost, capex_sum, ac_loss, sf_sum = self.calculate_assumption(spec, cost, year)
    #     opex_sum    = labour_cost + fuel_cost + com_sec_cost
    #     annual_cost = opex_sum + capex_sum/ship_age + ac_loss

    #     select_parameter = annual_cost * self.economy \
    #                     + fuel_cost * self.environment \
    #                     + ac_loss * self.safety \
    #                     + labour_cost * self.labour #要正規化 
    #     select      = select_parameter.idxmin()   
    #     # seafarerの増減率をながらかにするようなファクター → TBD
    #     return select, annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost
    
    # def calculate_assumption(self, spec, cost, year):
    #     labour_cost = spec.num_sf * cost.Seafarer[year] \
    #                 + spec.num_so * cost.ShoreOperator[year]
    #     fuel_cost   = spec.foc * cost.Fuel[year]
    #     com_sec_cost= spec.sec_cost * cost.CS[year] \
    #                 + spec.com_cost * cost.Comm[year]
    #     capex_sum   = spec.sa_cost * cost.Situ[year] \
    #                 + spec.pl_cost * cost.Plan[year] \
    #                 + spec.ex_cost * cost.Exec[year] \
    #                 + spec.ro_cost * cost.RemOpe[year] \
    #                 + spec.rm_cost * cost.RemMon[year]
    #     ac_loss     = spec.acc_ratio * cost.ExpLoss[year]
    #     sf_sum      = spec.num_sf + spec.num_so
        
    #     return labour_cost, fuel_cost, com_sec_cost, capex_sum, ac_loss, sf_sum
