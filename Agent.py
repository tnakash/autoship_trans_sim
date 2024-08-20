import math
import pandas as pd
import warnings

warnings.simplefilter('ignore', FutureWarning)
semi_auto_TRLgap = 3

class Investor():
    def __init__(self, name):
        self.name = name
        self.invest_tech = 'None'
        self.invest_amount = 0
        return

    def reset(self, invest, amount):
        self.invest_tech = invest
        self.invest_amount = amount
        self.invest_used = 0

    def invest(self, tech, policymaker):
        self.invest_used = self.invest_amount
        tech_name_list = tech['tech_name'].tolist()
        tech_indices = {name: index for index, name in enumerate(tech_name_list)} # {'Berth': 0, 'Navi': 1, 'Moni': 2}
        selected_tech_index = tech_indices.get(self.invest_tech)

        # List of indices of non-complete technologies (TRL < 9)
        incomplete_tech_indices = [i for i, trl in enumerate(tech.TRL) if trl < 9]

        if selected_tech_index is not None and selected_tech_index in incomplete_tech_indices:
            # Invest only in the selected technology if it is not complete
            tech.loc[selected_tech_index, "Rexp"] += self.invest_amount
        elif len(incomplete_tech_indices) >= 1:
            # Evenly distribute investment among all incomplete technologies
            amount_per_tech = self.invest_amount / len(incomplete_tech_indices)
            for i in incomplete_tech_indices:
                tech.loc[i, "Rexp"] += amount_per_tech
        else:
            # No investment made if all technologies are completed
            self.invest_used = 0
            policymaker.sub_used -= policymaker.sub_RandD

        return tech


class ShipOwner:
    def __init__(self, name, economy=1.0, safety=1.0, current_fleet=None, num_newbuilding=None, estimated_loss=25):
        self.name = name
        self.economy = economy
        self.safety = safety
        self.fleet = current_fleet
        self.num_newbuilding = num_newbuilding
        self.accident_loss = estimated_loss # compared to annual capex

    def reset(self, economy, safety, current_fleet):
        self.economy = economy
        self.safety = safety
        self.fleet = current_fleet

    def one_step(self, year):
        filtered_data = self.fleet[(self.fleet['year'] == year - 1) & (self.fleet['is_operational'] == True)].copy()
        filtered_data['year'] = year
        self.fleet = pd.concat([self.fleet, filtered_data], ignore_index=True)

    def select_ship(self, spec, tech, TRLreg):
        capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum
        select_parameter = annual_cost * self.economy + accident_sum * self.safety * capex_sum * self.accident_loss - spec['subsidy']
        select_parameter = consider_TRL_regulation(select_parameter, tech.TRL, TRLreg)
        select = select_parameter.idxmin()
        if math.isnan(select):
            select = 0

        return select

    def purchase_ship(self, config_list, select, year, start_year, ship_size, ship_type):
        berth, navi, moni = config_to_tech(select)
    # def purchase_ship(self, ship_spec, config_list, select, year, start_year, ship_size, ship_type):
    #     berth, navi, moni = ship_spec.get(select, tuple(None for _ in next(iter(ship_spec.values())).keys() if _ != 'index'))
        for i in range(self.num_newbuilding.loc[(self.num_newbuilding['year'] == start_year + year) & (self.num_newbuilding['DWT'] == ship_size),'ship'].values[0]):
            new_row = pd.Series({'year': start_year+year, 
                                 'ship_id': self.fleet['ship_id'].max() + 1, 
                                 'year_built': start_year+year, 
                                 'ship_type': ship_type,
                                 'DWT': ship_size, 
                                 'berthing': berth, 
                                 'navigation': navi, 
                                 'monitoring': moni, 
                                 'config': config_list[select], 
                                 'is_operational': True, 
                                 'misc': 'newbuilt', 
                                 'owner': self.name
                                 })
            self.fleet.loc[len(self.fleet)] = new_row

    # def purchase_ship_with_adoption(self, ship_spec, spec, config_list, select, tech, year, TRLreg, PolicyMaker, start_year, ship_size):
    def purchase_ship_with_adoption(self, spec, config_list, select, tech, year, TRLreg, PolicyMaker, start_year, ship_size):
        capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum                
        select_parameter = annual_cost * self.economy + accident_sum * self.safety * capex_sum * self.accident_loss - spec['subsidy']
        # select_parameter = consider_TRL_regulation(ship_spec, select_parameter, tech.TRL, TRLreg)
        select_parameter = consider_TRL_regulation(select_parameter, tech.TRL, TRLreg)
        select = select_parameter.idxmin()
        if math.isnan(select):
            select = 0

        if PolicyMaker.sub_select != select and select_parameter[PolicyMaker.sub_select] != float('inf'):
            PolicyMaker.sub_per_ship = select_parameter[PolicyMaker.sub_select] - select_parameter[select]
            num_subsidized_ship_possible = PolicyMaker.sub_Adoption // PolicyMaker.sub_per_ship
            newbuilding_ship = self.num_newbuilding.loc[(self.num_newbuilding['year'] == start_year + year) & (self.num_newbuilding['DWT'] == ship_size),'ship'].values[0]
            num_subsidized_ship = newbuilding_ship if newbuilding_ship < num_subsidized_ship_possible else num_subsidized_ship_possible
            PolicyMaker.sub_used += num_subsidized_ship * PolicyMaker.sub_per_ship
        else:
            PolicyMaker.sub_per_ship = 0
            num_subsidized_ship = 0

        berth, navi, moni = config_to_tech(PolicyMaker.sub_select)
        # berth, navi, moni = ship_spec.get(PolicyMaker.sub_select, tuple(None for _ in next(iter(ship_spec.values())).keys() if _ != 'index'))

        list = self.fleet.loc[(self.fleet['year_built'] == start_year + year) & (self.fleet['DWT'] == ship_size)]
        self.fleet = self.fleet.drop(self.fleet.loc[(self.fleet['year_built'] == start_year + year) & (self.fleet['DWT'] == ship_size)].index)
        for i in range(int(num_subsidized_ship)):
            list.iloc[i]['config'] = config_list[PolicyMaker.sub_select]
            list.iloc[i]['berthing'] = berth
            list.iloc[i]['navigation'] = navi
            list.iloc[i]['monitoring'] = moni
            list.iloc[i]['misc'] = 'newbuilt_subsidized'
            
        self.fleet = pd.concat([self.fleet, list], ignore_index= True)


    def scrap_ship(self, ship_age, year, start_year):
        filtered_fleet = self.fleet[(self.fleet['year'] == start_year + year) & (start_year + year - self.fleet['year_built'] >= ship_age)].copy()
        filtered_fleet['is_operational'] = False
        self.fleet.update(filtered_fleet)
    
    
    # def select_retrofit_ship(self, ship_spec, spec, tech, TRLreg, ship_age, retrofit_cost_rate, config_list, year, start_year, retrofit_limit, ship_size):
    def select_retrofit_ship(self, spec, tech, TRLreg, ship_age, retrofit_cost_rate, config_list, year, start_year, retrofit_limit, ship_size):
        capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption_for_retrofit(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum
        retrofit_cost = annual_cost[0] * retrofit_cost_rate
        retrofitted_ship = 0
        filtered_fleet = self.fleet[(self.fleet['year'] == start_year + year) & (self.fleet['DWT'] == ship_size)]
        for i in reversed(filtered_fleet.index.values):
            if (self.fleet.at[i, 'is_operational'] == False) or (self.fleet.at[i, 'year'] == self.fleet.at[i, 'year_built']):
                continue
            else:
                years_in_use = self.fleet.at[i, 'year'] - self.fleet.at[i, 'year_built']
                select_parameter = (annual_cost * self.economy + accident_sum * self.safety * capex_sum * self.accident_loss) * (ship_age - years_in_use) + retrofit_cost
                select_parameter[config_list.index(self.fleet.at[i, 'config'])] -= retrofit_cost 
                # select_parameter = consider_TRL_regulation(ship_spec, select_parameter, tech.TRL, TRLreg)
                select_parameter = consider_TRL_regulation(select_parameter, tech.TRL, TRLreg)
                select = select_parameter.idxmin()
                if math.isnan(select):
                    select = 0
                
                # retrofit if the technology can be upgraded
                berth, navi, moni = config_to_tech(select)
                # berth, navi, moni = ship_spec.get(select, tuple(None for _ in next(iter(ship_spec.values())).keys() if _ != 'index'))
                
                if self.fleet.at[i, 'config'] == config_list[select] or self.fleet.at[i, 'berthing'] > berth or self.fleet.at[i, 'navigation'] > navi or self.fleet.at[i, 'monitoring'] > moni:
                    continue
                else:
                    new_row = pd.Series({'year': start_year+year, 
                                         'ship_id': self.fleet.at[i, 'ship_id'], 
                                         'year_built': self.fleet.at[i, 'year_built'], 
                                         'ship_type': self.fleet.at[i, 'ship_type'],
                                         'DWT': self.fleet.at[i, 'DWT'], 
                                         'berthing': berth, 
                                         'navigation': navi, 
                                         'monitoring': moni, 
                                         'config': config_list[select], 
                                         'is_operational': True, 
                                         'misc': 'retrofitted', 
                                         'owner': self.name
                                         })
                    retrofitted_ship += 1
                    if(retrofitted_ship > retrofit_limit):
                        break
                    else:
                        self.fleet.loc[i] = new_row


def calculate_assumption(spec):
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


def consider_TRL_regulation(select_parameter, TRL, TRLreg):
    berth_list = [1, 5, 6, 7, 10, 11]
    navi1_list = [2, 5, 8, 10]
    navi2_list = [3, 6, 9, 11]
    moni_list = [4, 7, 8, 9, 10, 11]
    
    for i in berth_list:
        select_parameter[i] += float('inf') if TRL[0] < TRLreg else 0
    for i in navi1_list:
        select_parameter[i] += float('inf') if TRL[1] + semi_auto_TRLgap < TRLreg else 0
    for i in navi2_list:
        select_parameter[i] += float('inf') if TRL[1] < TRLreg else 0
    for i in moni_list:
        select_parameter[i] += float('inf') if TRL[2] < TRLreg else 0    

# def consider_TRL_regulation(ship_spec, select_parameter, TRL, TRLreg):
    # for config, tech_levels in ship_spec.items():
    #     if tech_levels['Berth'] and TRL[0] < TRLreg:
    #         select_parameter[config] += float('inf')
    #     if tech_levels['Navi'] == 1 and TRL[1] + 3 < TRLreg:
    #         select_parameter[config] += float('inf')
    #     if tech_levels['Navi'] == 2 and TRL[1] < TRLreg:
    #         select_parameter[config] += float('inf')
    #     if tech_levels['Moni'] and TRL[2] < TRLreg:
    #         select_parameter[config] += float('inf')

    return select_parameter

class PolicyMaker():
    def __init__(self, name, TRLreg):
        self.name = name
        self.sub_RandD = 0
        self.sub_Adoption = 0
        self.sub_Experience = 0
        self.sub_select = 0
        self.sub_used = 0
        self.sub_per_ship = 0
        self.TRLreg = TRLreg

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
    
    # Need to be rewritten
    def select_for_sub_adoption(self, spec, tech):
        for i in range(len(spec)-1, 0, -1):
            if (tech.TRL[0] >= self.TRLreg or spec.Berth[i] == 0) and ((tech.TRL[1] >= self.TRLreg or spec.Navi[i] == 0) or (tech.TRL[1] >= self.TRLreg - semi_auto_TRLgap and spec.Navi[i] == 1)) and (tech.TRL[2] >= self.TRLreg or spec.Moni[i] == 0):
                self.sub_select = i
                break
    
    def subsidize_experience(self, tech):
        for i in range(len(tech.TRL)):
            if tech.TRL[i] < self.TRLreg:
                tech.loc[i, ["Mexp"]] += self.sub_Experience / (tech.tech_cost[i] * self.trial_times) / len(tech.TRL)
                tech.loc[i, ["Oexp"]] += self.sub_Experience / (tech.tech_cost[i] * self.trial_times) / len(tech.TRL)
                self.sub_used += self.sub_Experience