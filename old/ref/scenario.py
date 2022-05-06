import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt

class Scenario():
    def __init__(self, filename, info=None):
        if info is None:
            with open(src_path + default_input, 'r') as yml:
                data = yaml.safe_load(yml)
            data = data['Scenario']
            self.ship_age = data['ship_age']
            self.ship_demand = data['ship_demand']
            self.sim_setting = data['sim_setting']
        else:
            self.ship_age = info[0]
            self.ship_demand = info[1]
            self.sim_setting = info[2]
    
        with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                  f"case{filename['simulation_case']:03}.yml", 'a') as yml:
            save_yaml(self, yml)
    
    def create(self, filename):
        years = list(range(self.sim_setting['start_year'], 
                          self.sim_setting['end_year']+1))
        num_of_ship, scrap, new_building = [], [], []
        for elapsed_years, year in enumerate(years):
            if elapsed_years == 0:
                numship_year = self.ship_demand['initial_number']
                scrap_year = int(self.ship_demand['initial_number'] / self.ship_age)
                nbld_year = int(self.ship_demand['initial_number'] / self.ship_age)
            elif 1 <= elapsed_years < self.ship_age:
                numship_year = int(num_of_ship[-1] * self.ship_demand['annual_growth']) 
                scrap_year = int(self.ship_demand['initial_number'] / self.ship_age)
                nbld_year = numship_year + scrap_year - num_of_ship[-1]
            else:
                numship_year = int(num_of_ship[-1] * self.ship_demand['annual_growth']) 
                scrap_year = new_building[elapsed_years - self.ship_age]
                nbld_year = numship_year + scrap_year - num_of_ship[-1]

            num_of_ship.append(numship_year)
            scrap.append(scrap_year)
            new_building.append(nbld_year)

        self.data = pd.DataFrame(zip(years, num_of_ship, new_building, scrap),
                                 columns=['Year',
                                          'Number of Ship',
                                          'New Building',
                                          'Scrap'])
    
        self.data.to_csv(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                         f"case{filename['simulation_case']:03}_scenario.csv")
    
    def update(self, filename, ships, costs, specs, target):
        scenario = self.data
        spec = specs.data
        cost = costs.data
        ship_list = sorted(set(ships['Selected Ship type']),
                               key=list(ships['Selected Ship type']).index)
        conventional_ship = spec['Ship type'].iloc[-1]
        ship_list.insert(0, conventional_ship)
        elapsed_years = 0
        selected_ship_for_output = []

        for year, ship in zip(ships['Year'], ships['Selected Ship type']):
            _ship = spec['Ship type']==ship
            print(f"in {year}, {ship} is selected. ("
                  f"Situation Awareness: {spec.loc[_ship, 'Situation Awareness'].iloc[0]:>8}, "
                  f"Planning: {spec.loc[_ship, 'Planning'].iloc[0]:>8}, "
                  f"Control: {spec.loc[_ship, 'Control'].iloc[0]:>8}, "
                  f"Remote: {spec.loc[_ship, 'Remote'].iloc[0]:>7})")
            selected_ship_for_output.append({
                "Year": year,
                "Selected ship": ship,
                "Situation Awareness": spec.loc[_ship, 'Situation Awareness'].iloc[0],
                "Planning": spec.loc[_ship, 'Planning'].iloc[0],
                "Control": spec.loc[_ship, 'Control'].iloc[0],
                "Remote": spec.loc[_ship, 'Remote'].iloc[0]
            })
            this_year = scenario['Year']==year
            last_year = scenario['Year']==year-1

            number_of_ship = int(scenario.loc[this_year, 'Number of Ship'])
            scrap_number = int(scenario.loc[this_year, 'Scrap'])
            new_building_number = int(scenario.loc[this_year, 'New Building'])
            scenario['Selected Ship type'] = ships['Selected Ship type']
            for _ship in ship_list:
                if elapsed_years == 0:
                    scenario[_ship] = 0
                else:
                    scenario.loc[this_year, _ship] = int(scenario.loc[last_year, _ship])

            if elapsed_years == 0:
                scenario.loc[this_year, conventional_ship] = number_of_ship
                scenario.loc[this_year, conventional_ship] -= scrap_number
                scenario.loc[this_year, ship] += new_building_number
            elif 1 <= elapsed_years < self.ship_age:
                scenario.loc[this_year, conventional_ship] -= scrap_number
                scenario.loc[this_year, ship] += new_building_number
            else:
                ship_ages_ago = ships['Year']==year-20
                scrap_ship = str(ships[ship_ages_ago]['Selected Ship type'].iloc[0])
                scenario.loc[this_year, scrap_ship] -= scrap_number
                scenario.loc[this_year, ship] += new_building_number

            elapsed_years += 1

        with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                f"case{filename['simulation_case']:03}_selected_ship.csv", 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                "Year", "Selected ship", "Situation Awareness",
                "Planning", "Control", "Remote"
            ])
            writer.writeheader()
            writer.writerows(selected_ship_for_output)

        evaluation_items = ['Labour Cost', 'Operation Cost', 'Fuel Cost',
                            'Onboard Asset', 'Shore Asset', 'Loss Damage',
                            'Seafarer', 'Shore Operator', 
                            'Total Loss Damage', 'Total Cost']
        for evaluation_item in evaluation_items:
            scenario[evaluation_item] = 0

        for ship in ship_list:
            _ship = spec['Ship type']==ship
            number_of_ship = scenario[ship]

            number_of_seafarer = int(spec.loc[_ship, 'num_sf'])
            number_of_shore_operator = int(spec.loc[_ship, 'num_so'])
            seafarer_cost = number_of_seafarer * cost['Seafarer']
            shore_operator_cost = number_of_shore_operator * cost['Shore Operator']
            scenario['Labour Cost'] += ((seafarer_cost + shore_operator_cost) 
                                        * number_of_ship).astype(int)

            cyber_security_cost = float(spec.loc[_ship, 'sec_cost']) * cost['OPEX of Cyber Security']
            communication_cost = float(spec.loc[_ship, 'com_cost']) * cost['OPEX of Communication']
            scenario['Operation Cost'] += ((cyber_security_cost + communication_cost) 
                                           * number_of_ship).astype(int)

            fuel_cost = float(spec.loc[_ship, 'foc']) * cost['Fuel']
            scenario['Fuel Cost'] += (fuel_cost * number_of_ship).astype(int)

            situation_awareness_cost = float(spec.loc[_ship, 'sa_cost']) * cost['CAPEX of Situation Awareness']
            planning_cost = float(spec.loc[_ship, 'pl_cost']) * cost['CAPEX of Planning']
            execution_cost = float(spec.loc[_ship, 'ex_cost']) * cost['CAPEX of Execution']
            scenario['Onboard Asset'] += ((situation_awareness_cost + planning_cost 
                                           + execution_cost) / self.ship_age * number_of_ship).astype(int)

            remote_operation_cost = float(spec.loc[_ship, 'ro_cost']) * cost['CAPEX of Remote Operation']
            remote_monitoring_cost = float(spec.loc[_ship, 'rm_cost']) * cost['CAPEX of Remote Monitoring']
            scenario['Shore Asset'] += ((remote_operation_cost + remote_monitoring_cost)
                                        / self.ship_age * number_of_ship).astype(int)

            accident_cost = float(spec.loc[_ship, 'acc_ratio']) * cost['Exp Loss']
            scenario['Loss Damage'] += (accident_cost * number_of_ship).astype(int)

            scenario['Seafarer'] += (number_of_seafarer * number_of_ship).astype(int)
            scenario['Shore Operator'] += (number_of_shore_operator * number_of_ship).astype(int)

        scenario['Labour Cost'] = (scenario['Labour Cost'] / scenario['Number of Ship']).astype(int)
        scenario['Loss Damage'] = (scenario['Loss Damage'] / scenario['Number of Ship']).astype(int)
        scenario['Fuel Cost'] = (scenario['Fuel Cost'] / scenario['Number of Ship']).astype(int)
        scenario['Operation Cost'] = (scenario['Operation Cost'] / scenario['Number of Ship']).astype(int)
        scenario['Onboard Asset'] = (scenario['Onboard Asset'] / scenario['Number of Ship']).astype(int)
        scenario['Shore Asset'] = (scenario['Shore Asset'] / scenario['Number of Ship']).astype(int)
        scenario['Total Loss Damage'] = (scenario['Loss Damage'] * scenario['Number of Ship']).astype(int)
        scenario['Total Cost'] += (scenario['Labour Cost']
                                    + scenario['Loss Damage']
                                    + scenario['Fuel Cost']
                                    + scenario['Operation Cost']
                                    + scenario['Onboard Asset']
                                    + scenario['Shore Asset'])
    
        self.data.to_csv(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                         f"case{filename['simulation_case']:03}_scenario.csv")

        fig = plt.figure(figsize=(18,10))
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        years = scenario['Year']
        target_seafarer_upper, target_seafarer_lower, target_cost = [], [], []
        for i, year in enumerate(years):
            if i == 0:
                _seafarer_upper = scenario['Seafarer'].iloc[i]
                _seafarer_lower = scenario['Seafarer'].iloc[i]
                _cost = scenario['Total Cost'].iloc[i]
            else:
                _seafarer_upper = target_seafarer_upper[-1] * (1.0-target['seafarer_upper']*0.01)
                _seafarer_lower = target_seafarer_lower[-1] * (1.0-target['seafarer_lower']*0.01)
                _cost = target_cost[-1] * (1.0-target['cost']*0.01)
            target_seafarer_upper.append(_seafarer_upper)
            target_seafarer_lower.append(_seafarer_lower)
            target_cost.append(_cost)

        ax1.stackplot(years, [scenario[ship] for ship in ship_list],
                      labels=[ship for ship in ship_list])
        ax1.set_title("Number of ships for each autonomous level")
        ax1.set_ylabel("Number of ships (vessel)")
        ax1.legend(loc="best")

        ax2.stackplot(years, scenario['Total Loss Damage'])
        ax2.set_title("Number of Expected Accidents")
        ax2.set_ylabel("Total Loss Damage (USD)")

        items = ['Seafarer', 'Shore Operator']
        ax3.stackplot(years,[scenario[item] for item in items], labels=items)
        ax3.plot(years, target_seafarer_upper,
                 label='Target', c='k', linestyle="dashed", alpha = 1.0)
        ax3.plot(years, target_seafarer_lower,
                 c='k', linestyle="dashed", alpha = 1.0)
        ax3.set_title("Number of Workers")
        ax3.set_xlabel("year (yyyy)")
        ax3.set_ylabel("Number of Workers (person)")
        ax3.legend(loc="best")

        items = ['Labour Cost', 'Loss Damage', 'Fuel Cost', 'Operation Cost',
                 'Onboard Asset', 'Shore Asset']
        ax4.stackplot(years,[scenario[item] for item in items], labels=items)
        ax4.plot(years, target_cost,
                 label='Target', c='k', linestyle="dashed", alpha = 1.0)
        ax4.set_title(f"Total Cost from {scenario['Year'].iloc[0]} "
                      f"to {scenario['Year'].iloc[-1]} is "
                      f"{scenario['Total Cost'].sum():,}USD")
        ax4.set_xlabel("year (yyyy)")
        ax4.set_ylabel("Cost for each vessel (USD)")
        ax4.legend(loc='best')
        
        plt.savefig(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                    f"case{filename['simulation_case']:03}_scenario.png",
                    format="png", dpi=300, bbox_inches="tight")
        plt.show()

class Cost():
    def __init__(self, filename, info=None):
        if info is None:
            with open(src_path + default_input, 'r') as yml:
                data = yaml.safe_load(yml)
            data = data['Cost']
            self.seafarer_cost = data['seafarer_cost'] # sf
            self.shore_operator_cost = data['shore_operator_cost'] # so
            self.exp_loss = data['exp_loss'] # el
            self.opex_cyber_security = data['opex_cyber_security'] # cs
            self.opex_communication = data['opex_communication'] # cm
            self.capex_situation_awareness = data['capex_situation_awareness'] # sa
            self.capex_planning = data['capex_planning'] # pl
            self.capex_execution = data['capex_execution'] # ex
            self.capex_remote_operation = data['capex_remote_operation'] # ro
            self.capex_remote_monitoring = data['capex_remote_monitoring'] # rm
            self.fuel_cost = data['fuel_cost'] # fc
        else:
            self.seafarer_cost = info[0]
            self.shore_operator_cost = info[1]
            self.exp_loss = info[2]
            self.opex_cyber_security = info[3]
            self.opex_communication = info[4]
            self.capex_situation_awareness = info[5]
            self.capex_planning = info[6]
            self.capex_execution = info[7]
            self.capex_remote_operation = info[8]
            self.capex_remote_monitoring = info[9]
            self.fuel_cost = info[10]
    
        with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                  f"case{filename['simulation_case']:03}.yml", 'a') as yml:
            save_yaml(self, yml)
    
    def calculate(self, filename, scenario, policymaker):
        sf, so, el, cs, cm, sa = [], [], [], [], [], []
        pl, ex, ro, rm, fc = [], [], [], [], []
        for i, year in enumerate(scenario.data["Year"]):
            if i == 0:
                sf_year = self.seafarer_cost['initial_number']
                so_year = self.shore_operator_cost['initial_number']
                el_year = self.exp_loss['initial_number']
                cs_year = self.opex_cyber_security['initial_number']
                cm_year = self.opex_communication['initial_number']
                sa_year = self.capex_situation_awareness['initial_number']
                pl_year = self.capex_planning['initial_number']
                ex_year = self.capex_execution['initial_number']
                ro_year = self.capex_remote_operation['initial_number']
                rm_year = self.capex_remote_monitoring['initial_number']
                fc_year = self.fuel_cost['initial_number']
            else:
                sf_year = int(sf[-1] * self.seafarer_cost['annual_growth'])
                so_year = int(so[-1] * self.shore_operator_cost['annual_growth'])
                el_year = int(el[-1] * self.exp_loss['annual_growth'])
                cs_year = int(cs[-1] * self.opex_cyber_security['annual_growth'])
                cm_year = int(cm[-1] * self.opex_communication['annual_growth'])
                sa_year = int(sa[-1] * (policymaker.sa_growth + policymaker.rm_growth*0.1))
                pl_year = int(pl[-1] * policymaker.pl_growth)
                ex_year = int(ex[-1] * policymaker.ex_growth)
                ro_year = int(ro[-1] * policymaker.ro_growth)
                rm_year = int(rm[-1] * (policymaker.rm_growth + policymaker.sa_growth*0.1))
                fc_year = int(fc[-1] * policymaker.fuel_growth)

            sf.append(sf_year)
            so.append(so_year)
            el.append(el_year)
            cs.append(cs_year)
            cm.append(cm_year)
            sa.append(sa_year)
            pl.append(pl_year)
            ex.append(ex_year)
            ro.append(ro_year)
            rm.append(rm_year)
            fc.append(fc_year)

        self.data = pd.DataFrame(zip(scenario.data["Year"],
                                     sf, so, el, cs, cm, sa, pl, ex, ro, rm, fc),
                                 columns=['Year',
                                          'Seafarer',
                                          'Shore Operator',
                                          'Exp Loss',
                                          'OPEX of Cyber Security',
                                          'OPEX of Communication',
                                          'CAPEX of Situation Awareness',
                                          'CAPEX of Planning',
                                          'CAPEX of Execution',
                                          'CAPEX of Remote Operation',
                                          'CAPEX of Remote Monitoring',
                                          'Fuel'])
    
        self.data.to_csv(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                         f"case{filename['simulation_case']:03}_cost.csv")
    

class Spec():
    def __init__(self, filename, info=None):
        if info is None:
            with open(src_path + default_input, 'r') as yml:
                data = yaml.safe_load(yml)
            data = data['Spec']
            self.situation_awareness = data['SituationAwareness'] # sa
            self.planning = data['Planning'] # pl
            self.control = data['Control'] # co
            self.remote = data['Remote'] # re
        else:
            self.situation_awareness = info[0]
            self.planning = info[1]
            self.control = info[2]
            self.remote = info[3]
    
        with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                  f"case{filename['simulation_case']:03}.yml", 'a') as yml:
            save_yaml(self, yml)

    def get(self, filename):
        st, co, pl, sa, re = [], [], [], [], []
        sec_cost, com_cost, acc_ratio, sa_cost = [], [], [], []
        pl_cost, ex_cost, ro_cost, rm_cost = [], [], [], []
        num_sf, num_so, foc = [], [], []
        i = 1
        for choice in itertools.product(self.control, # choice[0]
                                        self.planning, # choice[1]
                                        self.situation_awareness, # choice[2]
                                        self.remote): # choice[3]
            st_ship = 'ship_' + str(i)
            sec_ship = self.control[choice[0]]['sec_cost'] \
                       + self.planning[choice[1]]['sec_cost'] \
                       + self.situation_awareness[choice[2]]['sec_cost'] \
                       + self.remote[choice[3]]['sec_cost'] \
                       - 4
            com_ship = self.control[choice[0]]['com_cost'] \
                       + self.planning[choice[1]]['com_cost'] \
                       + self.situation_awareness[choice[2]]['com_cost'] \
                       + self.remote[choice[3]]['com_cost'] \
                       - 4
            acc_ship = self.control[choice[0]]['acc_ratio'] \
                       * self.planning[choice[1]]['acc_ratio'] \
                       * self.situation_awareness[choice[2]]['acc_ratio']
            sa_ship = self.situation_awareness[choice[2]]['sa_cost']
            pl_ship = self.planning[choice[1]]['pl_cost']
            ex_ship = self.control[choice[0]]['ex_cost']
            ro_ship = self.remote[choice[3]]['ro_cost']
            rm_ship = self.remote[choice[3]]['rm_cost']
            sf_total = self.control[choice[0]]['num_sf'] \
                       + self.planning[choice[1]]['num_sf'] \
                       + self.situation_awareness[choice[2]]['num_sf']
            so_ship = int(sf_total * self.remote[choice[3]]['num_so_ratio'])
            sf_ship = sf_total - so_ship
            max_seafarer = 8 # assume max seafarer: 8
            if sf_ship > 0:
                foc_ship = (1 - (max_seafarer - sf_ship) / 200)
            else:
                foc_ship = 0.9

            st.append(st_ship)
            co.append(choice[0])
            pl.append(choice[1])
            sa.append(choice[2])
            re.append(choice[3])
            sec_cost.append(sec_ship)
            com_cost.append(com_ship)
            acc_ratio.append(acc_ship)
            sa_cost.append(sa_ship)
            pl_cost.append(pl_ship)
            ex_cost.append(ex_ship)
            ro_cost.append(ro_ship)
            rm_cost.append(rm_ship)
            num_so.append(so_ship)
            num_sf.append(sf_ship)
            foc.append(foc_ship)
            i += 1

        self.data = pd.DataFrame(zip(st, co, pl, sa, re, sec_cost, com_cost,
                                     acc_ratio, sa_cost, pl_cost, ex_cost,
                                     ro_cost, rm_cost, num_sf, num_so, foc),
                                 columns=['Ship type',
                                          'Control',
                                          'Planning',
                                          'Situation Awareness',
                                          'Remote',
                                          'sec_cost',
                                          'com_cost',
                                          'acc_ratio',
                                          'sa_cost',
                                          'pl_cost',
                                          'ex_cost',
                                          'ro_cost',
                                          'rm_cost',
                                          'num_sf',
                                          'num_so',
                                          'foc'])
    
        self.data.to_csv(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                         f"case{filename['simulation_case']:03}_spec.csv")
    

