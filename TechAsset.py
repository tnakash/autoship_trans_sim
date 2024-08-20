import math
import pandas as pd
import warnings

class Technology():
    def __init__(self):
        return

    # Need to be rewritten: Assuming three technologies
    def get_tech_ini(self, tech_yml, uncertainty, trl_b = 0, trl_n = 0, trl_m = 0):
        tech_list = list(tech_yml)[:-1] # Without "Others"
        column = ['tech_name', 'tech_cost', 'integ_factor', 'integ_factor_ini', 'TRL', 'Rexp', 'Mexp', 'Oexp', 'tech_cost_min', 'accident_ratio', 'accident_ratio_base', 'accident_ratio_ini']

        tech_cost = [0] * len(tech_list)
        tech_cost_min = [0] * len(tech_list)
        integ_factor = [0] * len(tech_list)
        integ_factor_ini = [0] * len(tech_list)
        TRL = [0] * len(tech_list)
        Rexp = [0] * len(tech_list)
        Mexp = [0] * len(tech_list)
        Oexp = [0] * len(tech_list)
        accident_ratio_ini = [0] * len(tech_list)
        accident_ratio_base = [0] * len(tech_list)
        accident_ratio = [0] * len(tech_list)
        
        ope_max = tech_yml['Others']['ope_max']
        manu_max = tech_yml['Others']['manu_max']
        acc_reduction_full = tech_yml['Others']['acc_reduction_full']
        ope_TRL_factor = tech_yml['Others']['ope_TRL_factor']
        ope_safety_b = tech_yml['Others']['ope_safety_b']
        randd_base = tech_yml['Others']['randd_base']
        rd_TRL_factor = tech_yml['Others']['rd_TRL_factor']

        rd_need_TRL = [0] * len(tech_list)
        # Introduce Uncertainty
        if uncertainty:
            rd_need_TRL[0] = trl_b
            rd_need_TRL[1] = trl_n
            rd_need_TRL[2] = trl_m
            # for i in range(3):
            #     rd_need_TRL[i] = np.random.normal(tech_yml['Others']['rd_need_TRL'], tech_yml['Others']['rd_need_TRL']/3)
            #     rd_need_TRL[i] = 0 if rd_need_TRL[i] < 0 else rd_need_TRL[i] 
        else:
            for i in range(len(tech_list)):
                rd_need_TRL[i] = tech_yml['Others']['rd_need_TRL']

        integ_b = tech_yml['Others']['integ_b']
        # Rewrite afterwards... 
        param = pd.Series({
            'ope_max': ope_max,
            'manu_max': manu_max,
            'acc_reduction_full': acc_reduction_full,
            'ope_TRL_factor': ope_TRL_factor,
            'ope_safety_b': ope_safety_b,
            'randd_base': randd_base,
            'rd_TRL_factor': rd_TRL_factor,
            'rd_need_TRL': rd_need_TRL,
            'integ_b': integ_b
            }, index = [
                'ope_max',
                'manu_max',
                'acc_reduction_full',
                'ope_TRL_factor',
                'ope_safety_b',
                'randd_base',
                'rd_TRL_factor',
                'rd_need_TRL',
                'integ_b'
                ]
            )

        for i in range(len(tech_list)):
            s = tech_list[i]
            tech_cost_min[i] = tech_yml[s]['min_cost']
            integ_factor_ini[i] = tech_yml['Others']['tech_integ_factor']
            integ_factor[i] = integ_factor_ini[i]
            TRL[i] = tech_yml[s]['TRL_ini']
            tech_cost[i] = tech_cost_min[i] # * (10 - TRL[i])
            accident_ratio_ini[i] = tech_yml[s]['accident']
            accident_ratio_base[i] = accident_ratio_ini[i]
            accident_ratio[i] = accident_ratio_base[i]
        
        self.tech = pd.DataFrame(zip(tech_list, tech_cost, integ_factor, integ_factor_ini, TRL, Rexp, Mexp, Oexp, tech_cost_min, accident_ratio, accident_ratio_base, accident_ratio_ini), columns = column)
        self.param = param

class Vehicle():
    def __init__(self, fleet_yml):
        self.ship_types = list(fleet_yml)
        self.cost_types = [f'cost_{fleet_yml[ship]["ship_size"]}' for ship in fleet_yml]
        return

    def initiate_spec(self):
        self.spec_current = [''] * len(self.cost_types)
        self.spec_each = [''] * len(self.ship_types)    
