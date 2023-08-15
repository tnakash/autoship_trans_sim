import math
import pandas as pd
import warnings

warnings.simplefilter('ignore', FutureWarning)

class Investor():
    def __init__(self):
        self.invest_tech = 'None'
        self.invest_amount = 0
        return

    def reset(self, invest, amount):
        self.invest_tech = invest
        self.invest_amount = amount
        self.invest_used = 0

    # def investment(self, cost, TRL, year, delay, invest, budget):
    def invest(self, tech, policymaker):
        self.invest_used = self.invest_amount
        if (self.invest_tech == 'Berth' or (tech.TRL[1] == 9 and tech.TRL[2] == 9)) and tech.TRL[0] < 9:
            tech.loc[0, ["Rexp"]] += self.invest_amount
        elif (self.invest_tech == 'Navi' or (tech.TRL[0] == 9 and tech.TRL[2] == 9)) and tech.TRL[1] < 9:
            tech.loc[1, ["Rexp"]] += self.invest_amount
        elif (self.invest_tech == 'Moni' or (tech.TRL[0] == 9 and tech.TRL[1] == 9)) and tech.TRL[2] < 9:
            tech.loc[2, ["Rexp"]] += self.invest_amount
        elif tech.TRL[0] < 9 and tech.TRL[1] < 9 and tech.TRL[2] == 9:
            tech.loc[0, ["Rexp"]] += self.invest_amount / 2
            tech.loc[1, ["Rexp"]] += self.invest_amount / 2
        elif tech.TRL[0] < 9 and tech.TRL[1] == 9 and tech.TRL[2] < 9:
            tech.loc[0, ["Rexp"]] += self.invest_amount / 2
            tech.loc[2, ["Rexp"]] += self.invest_amount / 2
        elif tech.TRL[0] == 9 and tech.TRL[1] < 9 and tech.TRL[2] < 9:
            tech.loc[1, ["Rexp"]] += self.invest_amount / 2
            tech.loc[2, ["Rexp"]] += self.invest_amount / 2            
        elif tech.TRL[0] < 9 and tech.TRL[1] < 9 and tech.TRL[2] < 9:
            tech.loc[0, ["Rexp"]] += self.invest_amount / 3
            tech.loc[1, ["Rexp"]] += self.invest_amount / 3
            tech.loc[2, ["Rexp"]] += self.invest_amount / 3
        else:
            self.invest_used = 0
            policymaker.sub_used -= policymaker.sub_RandD

        return tech


class ShipOwner:
    def __init__(self, name, economy=1.0, safety=1.0, current_fleet=None, num_newbuilding=None, estimated_loss=10000000):
        self.name = name
        self.economy = economy
        self.safety = safety
        self.fleet = current_fleet
        self.num_newbuilding = num_newbuilding
        self.accident_loss = estimated_loss

    def reset(self, economy, safety, current_fleet):
        self.economy = economy
        self.safety = safety
        self.fleet = current_fleet

    def select_ship(self, spec, tech, TRLreg):
        # Rewrite afterwards ... 
        berth_list = [1, 5, 6, 7, 10, 11]
        navi1_list = [2, 5, 8, 10]
        navi2_list = [3, 6, 9, 11]
        moni_list = [4, 7, 8, 9, 10, 11]

        capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum
        select_parameter = annual_cost * self.economy + accident_sum * self.safety * self.accident_loss - spec['subsidy']

        # Consider TRL regulation
        for i in berth_list:
            select_parameter[i] += float('inf') if tech.TRL[0] < TRLreg else 0
        for i in navi1_list:
            select_parameter[i] += float('inf') if tech.TRL[1] + 3 < TRLreg else 0
        for i in navi2_list:
            select_parameter[i] += float('inf') if tech.TRL[1] < TRLreg else 0
        for i in moni_list:
            select_parameter[i] += float('inf') if tech.TRL[2] < TRLreg else 0

        select = select_parameter.idxmin()
        if math.isnan(select):
            select = 0

        return select


    def purchase_ship(self, config_list, select, year, start_year):
        # self.fleet.loc[len(self.fleet.year)] = 0
        # self.fleet.at[len(self.fleet.year)-1, 'year'] = self.fleet.at[len(self.fleet.year)-2, 'year'] + 1
        # self.fleet.at[len(self.fleet.year)-1, config_list[select]] = self.num_newbuilding['ship'][year]
        # # self.fleet.at[len(self.fleet.year)-1, 'config'+str(select)] = self.num_newbuilding['ship'][year]        
        berth, navi, moni = config_to_tech(select)
        ship_size = 499 # to be an input
        for i in range(self.num_newbuilding['ship'][year]):
            new_row = pd.Series({'year': start_year+year, 'ship_id': self.fleet['ship_id'].max() + 1, 'year_built': start_year+year, 'DWT': ship_size, 'berthing': berth, 'navigation': navi, 'monitoring': moni, 'config': config_list[select], 'is_operational': True, 'misc': 'newbuilt', 'owner': self})
            # self.fleet = pd.concat([self.fleet, new_row], ignore_index=True)
            self.fleet.loc[len(self.fleet)] = new_row


    def purchase_ship_with_adoption(self, spec, config_list, select, tech, year, TRLreg, PolicyMaker, start_year):
        # Rewrite afterwards ... 
        berth_list = [1, 5, 6, 7, 10, 11]
        navi1_list = [2, 5, 8, 10]
        navi2_list = [3, 6, 9, 11]
        moni_list = [4, 7, 8, 9, 10, 11]
        
        # 同じ計算をあちこちでやっているが，ここはあえて色々な選好パターンを作る目的で．
        capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum                
        select_parameter = annual_cost * self.economy + accident_sum * self.safety * self.accident_loss - spec['subsidy']
        
        # Consider TRL regulation
        for i in berth_list:
            select_parameter[i] += float('inf') if tech.TRL[0] < TRLreg else 0
        for i in navi1_list:
            select_parameter[i] += float('inf') if tech.TRL[1] + 3 < TRLreg else 0
        for i in navi2_list:
            select_parameter[i] += float('inf') if tech.TRL[1] < TRLreg else 0
        for i in moni_list:
            select_parameter[i] += float('inf') if tech.TRL[2] < TRLreg else 0

        select = select_parameter.idxmin()
        if math.isnan(select):
            select = 0

        if PolicyMaker.sub_select != select:
            PolicyMaker.sub_per_ship = select_parameter[PolicyMaker.sub_select] - select_parameter[select]
            num_subsidized_ship_possible = PolicyMaker.sub_Adoption // PolicyMaker.sub_per_ship
            num_subsidized_ship = self.num_newbuilding['ship'][year] if self.num_newbuilding['ship'][year] < num_subsidized_ship_possible else num_subsidized_ship_possible
            PolicyMaker.sub_used += num_subsidized_ship * PolicyMaker.sub_per_ship
        else:
            PolicyMaker.sub_per_ship = 0
            num_subsidized_ship = 0

        # # self.fleet.at[len(self.fleet.year)-1, 'config'+str(PolicyMaker.sub_select)] = num_subsidized_ship
        # # self.fleet.at[len(self.fleet.year)-1, 'config'+str(select)] = self.num_newbuilding['ship'][year] - num_subsidized_ship
        # self.fleet.at[len(self.fleet.year)-1, config_list[PolicyMaker.sub_select]] = num_subsidized_ship
        # self.fleet.at[len(self.fleet.year)-1, config_list[select]] = self.num_newbuilding['ship'][year] - num_subsidized_ship

        berth, navi, moni = config_to_tech(PolicyMaker.sub_select)
        list = self.fleet.loc[self.fleet['year_built'] == start_year+year]
        self.fleet = self.fleet.drop(self.fleet.loc[self.fleet['year_built'] == start_year+year].index)
        for i in range(int(num_subsidized_ship)):
            list.iloc[i]['config'] = config_list[PolicyMaker.sub_select]
            list.iloc[i]['berthing'] = berth
            list.iloc[i]['navigation'] = navi
            list.iloc[i]['monitoring'] = moni
            list.iloc[i]['misc'] = 'newbuilt_subsidized'
            
        self.fleet = pd.concat([self.fleet, list], ignore_index= True)


    # def retrofit_ship(self, config_list, select_retrofit, year):
    #     self.fleet.loc[len(self.fleet.year)] = 0
    #     self.fleet.at[len(self.fleet.year)-1, 'year'] = self.fleet.at[len(self.fleet.year)-2, 'year'] + 1
    #     self.fleet.at[len(self.fleet.year)-1, config_list[select]] = self.num_newbuilding['ship'][year]
    #     # self.fleet.at[len(self.fleet.year)-1, 'config'+str(select)] = self.num_newbuilding['ship'][year]


    def scrap_ship(self, ship_age, year, start_year):
         for i in self.fleet.index.values: #range(len(self.fleet)):
            if (self.fleet.at[i, 'is_operational'] == True) and ((start_year + year) - self.fleet.at[i, 'year_built'] > ship_age):
                self.fleet.at[i, 'is_operational'] = False
        

    def select_retrofit_ship(self, spec, tech, TRLreg, ship_age, retrofit_cost, config_list, year, start_year, retrofit_limit):
        # Rewrite afterwards ... 
        berth_list = [1, 5, 6, 7, 10, 11]
        navi1_list = [2, 5, 8, 10]
        navi2_list = [3, 6, 9, 11]
        moni_list = [4, 7, 8, 9, 10, 11]

        capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption_for_retrofit(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum

        retrofitted_ship = 0
        for i in reversed(self.fleet.index.values):
            if (self.fleet.at[i, 'is_operational'] == False) or (self.fleet.at[i, 'year'] == self.fleet.at[i, 'year_built']):
                continue
            else:
                years_in_use = self.fleet.at[i, 'year'] - self.fleet.at[i, 'year_built']
                select_parameter = (annual_cost * self.economy + accident_sum * self.safety * self.accident_loss) * (ship_age - years_in_use) + retrofit_cost
                select_parameter[config_list.index(self.fleet.at[i, 'config'])] -= retrofit_cost
            
                # Consider TRL regulation
                for j in berth_list:
                    select_parameter[j] += float('inf') if tech.TRL[0] < TRLreg else 0
                for j in navi1_list:
                    select_parameter[j] += float('inf') if tech.TRL[1] + 3 < TRLreg else 0
                for j in navi2_list:
                    select_parameter[j] += float('inf') if tech.TRL[1] < TRLreg else 0
                for j in moni_list:
                    select_parameter[j] += float('inf') if tech.TRL[2] < TRLreg else 0
                
                select = select_parameter.idxmin()
                if math.isnan(select):
                    select = 0
                
                # retrofit if the technology can be upgraded
                berth, navi, moni = config_to_tech(select)
                if self.fleet.at[i, 'config'] == config_list[select] or self.fleet.at[i, 'berthing'] > berth or self.fleet.at[i, 'navigation'] > navi or self.fleet.at[i, 'monitoring'] > moni:
                    continue
                else:
                    self.fleet.at[i, 'is_operational'] = False
                    new_row = pd.Series({'year': start_year+year, 'ship_id': self.fleet.at[i, 'ship_id'], 'year_built': self.fleet.at[i, 'year_built'], 'DWT': self.fleet.at[i, 'DWT'], 'berthing': berth, 'navigation': navi, 'monitoring': moni, 'config': config_list[select], 'is_operational': True, 'misc': 'retrofitted', 'owner': self})
                    retrofitted_ship += 1
                    if(retrofitted_ship > retrofit_limit):
                        self.fleet.at[i, 'is_operational'] = True
                        break
                    self.fleet.loc[len(self.fleet)] = new_row


def calculate_assumption(spec):
    # Can be re-categorized
    # labour_cost = spec.crew_cost + spec.SCC_Personal
    # fuel_cost   = spec.fuel_cost_ME + spec.fuel_cost_AE 
    capex_sum   = spec.material_cost + spec.integrate_cost + spec.add_eq_cost
    opex_sum    = spec.crew_cost + spec.store_cost + spec.maintenance_cost + spec.insurance_cost+ spec.general_cost + spec.dock_cost
    voyex_sum   = spec.port_call + spec.fuel_cost_ME + spec.fuel_cost_AE
    addcost_sum = spec.SCC_Capex + spec.SCC_Opex + spec.SCC_Personal + spec.Mnt_in_port
    accident_sum = spec.accident_berth + spec.accident_navi + spec.accident_moni

    return capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum


def calculate_assumption_for_retrofit(spec):
    # Not considering fuel_cost_ME reduction (because of the superstructure)
    capex_sum   = spec.material_cost + spec.integrate_cost + spec.add_eq_cost
    opex_sum    = spec.crew_cost + spec.store_cost + spec.maintenance_cost + spec.insurance_cost+ spec.general_cost + spec.dock_cost
    voyex_sum   = spec.port_call + spec.fuel_cost_AE # + spec.fuel_cost_ME
    addcost_sum = spec.SCC_Capex + spec.SCC_Opex + spec.SCC_Personal + spec.Mnt_in_port
    accident_sum = spec.accident_berth + spec.accident_navi + spec.accident_moni

    return capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum


def config_to_tech(config_number):
    berth_list = [1, 5, 6, 7, 10, 11]
    navi1_list = [2, 5, 8, 10]
    navi2_list = [3, 6, 9, 11]
    moni_list = [4, 7, 8, 9, 10, 11]
    
    tech_berth, tech_navi, tech_moni = 0, 0, 0
    
    if config_number in berth_list:
        tech_berth = 1
    
    if config_number in navi1_list:
        tech_navi = 1
    elif config_number in navi2_list:
        tech_navi = 2

    if config_number in moni_list:
        tech_moni = 1
    
    return tech_berth, tech_navi, tech_moni


class PolicyMaker():
    def __init__(self):
        self.sub_RandD = 0
        self.sub_Adoption = 0
        self.sub_Experience = 0
        self.sub_select = 0
        self.sub_used = 0
        self.sub_per_ship = 0

    def reset(self, sub_RandD, sub_Adoption, sub_Experience, trial_times):
        self.sub_RandD = sub_RandD
        self.sub_Adoption = sub_Adoption
        self.sub_select = 0
        self.sub_used = 0
        self.sub_per_ship = 0
        self.sub_Experience = sub_Experience
        self.trial_times = trial_times

    def subsidize_investment(self, investor):
        investor.invest_amount += self.sub_RandD
        self.sub_used += self.sub_RandD
    
    def select_for_sub_adoption(self, spec, tech, TRLreg):
        for i in range(11, 0, -1):
            if (tech.TRL[0] >= TRLreg or spec.Berth[i] == 0) and ((tech.TRL[1] >= TRLreg or spec.Navi[i] == 0) or (tech.TRL[1] >= TRLreg-3 and spec.Navi[i] == 1)) and (tech.TRL[2] >= TRLreg or spec.Moni[i] == 0):
                self.sub_select = i
                break
    
    def subsidize_experience(self, tech, TRLreg):
        for i in range(3):
            if tech.TRL[i] < TRLreg:
                tech.loc[i, ["Mexp"]] += self.sub_Experience / (tech.tech_cost[i] * self.trial_times)
                tech.loc[i, ["Oexp"]] += self.sub_Experience / (tech.tech_cost[i] * self.trial_times)
                self.sub_used += self.sub_Experience