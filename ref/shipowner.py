import os
import csv
import yaml
import pandas as pd
import itertools
import matplotlib.pyplot as plt

class ShipOwner():
    def __init__(self, filename, info=None):
        if info is None:
            with open(src_path + default_input, 'r') as yml:
                data = yaml.safe_load(yml)
            data = data['ShipOwner']
            self.name = data['name']
            self.economy = data['economy']
            self.environment = data['environment']
            self.safety = data['safety']
            self.labour = data['labour']
        else:
            self.name = info['name']
            self.economy = info['economy']
            self.environment = info['environment']
            self.safety = info['safety']
            self.labour = info['labour']
    
        with open(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                  f"case{filename['simulation_case']:03}.yml", 'a') as yml:
            save_yaml(self, yml)
    
    def select_ship(self, filename, scenarios, costs, specs, show=False):
        spec = specs.data
        selected_ship = []
        for scenario, cost in zip(scenarios.data.to_dict(orient='records'),
                                  costs.data.to_dict(orient='records')):
            labour_cost = spec['num_sf'] * cost['Seafarer'] \
                          + spec['num_so'] * cost['Shore Operator']

            fuel_cost = spec['foc'] * cost['Fuel']
            fuel_cost = fuel_cost.round(0).astype(int)

            sec_cost = spec['sec_cost'] * cost['OPEX of Cyber Security']
            sec_cost = sec_cost.round(0).astype(int)
            com_cost = spec['com_cost'] * cost['OPEX of Communication']
            com_cost = com_cost.round(0).astype(int)

            sa_cost = spec['sa_cost'] * cost['CAPEX of Situation Awareness']
            sa_cost = sa_cost.round(0).astype(int)
            pl_cost = spec['pl_cost'] * cost['CAPEX of Planning']
            pl_cost = pl_cost.round(0).astype(int)
            ex_cost = spec['ex_cost'] * cost['CAPEX of Execution']
            ex_cost = ex_cost.round(0).astype(int)
            ro_cost = spec['ro_cost'] * cost['CAPEX of Remote Operation']
            ro_cost = ro_cost.round(0).astype(int)
            rm_cost = spec['rm_cost'] * cost['CAPEX of Remote Monitoring']
            rm_cost = rm_cost.round(0).astype(int)

            opex_sum = labour_cost + fuel_cost + sec_cost + com_cost
            capex_sum = sa_cost + pl_cost + ex_cost + ro_cost + rm_cost

            ac_loss = spec['acc_ratio'] * cost['Exp Loss']
            ac_loss = ac_loss.round(0).astype(int)

            annual_cost = opex_sum + capex_sum/scenarios.ship_age + ac_loss
            annual_cost = annual_cost.round(0).astype(int)

            sf_sum = spec['num_sf'] + spec['num_so']

            select_parameter = annual_cost * self.economy \
                               + fuel_cost * self.environment \
                               + ac_loss * self.safety \
                               + labour_cost * self.labour
            
            total_cost = sec_cost + com_cost + capex_sum/scenarios.ship_age \
                         + fuel_cost + ac_loss + labour_cost

            selected_index = select_parameter.idxmin() # NOT normalized
            selected_ship.append('ship_' + str(selected_index+1))

            if show and scenario["Year"]%show == 0:
                year = str(scenario["Year"])
                fig = plt.figure(figsize=(18,5))
                ax1 = fig.add_subplot(1, 3, 1)
                ax2 = fig.add_subplot(1, 3, 2)
                ax3 = fig.add_subplot(1, 3, 3)

                ax1.scatter(x=annual_cost, y=ac_loss, label='All candidates')
                ax1.scatter(x=annual_cost[selected_index], y=ac_loss[selected_index],
                            label=f'Selected ({selected_ship[-1]})',
                            marker='*', c='yellow', edgecolor='k', s=150)
                ax1.set_title("Economy vs Safety in " + year)
                ax1.set_xlabel("Annual Cost (USD)")
                ax1.set_ylabel("Expected Accident Loss (USD)")
                ax1.legend(loc='best')

                ax2.scatter(x=annual_cost, y=sf_sum, label='All candidates')
                ax2.scatter(x=annual_cost[selected_index], y=sf_sum[selected_index],
                            label=f'Selected ({selected_ship[-1]})',
                            marker='*', c='yellow', edgecolor='k', s=150)
                ax2.set_title("Economy vs Labour in " + year)
                ax2.set_xlabel("Annual Cost (USD)")
                ax2.set_ylabel("Number of Seafarer (person)")
                ax2.legend(loc='best')

                ax3.scatter(x=annual_cost, y=fuel_cost, label='All candidates')
                ax3.scatter(x=annual_cost[selected_index], y=fuel_cost[selected_index],
                            label=f'Selected ({selected_ship[-1]})',
                            marker='*', c='yellow', edgecolor='k', s=150)
                ax3.set_title("Economy vs Environment in " + year)
                ax3.set_xlabel("Annual Cost (USD)")
                ax3.set_ylabel("Fuel Cost (USD)")
                ax3.legend(loc='best')
                
                plt.savefig(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                            f"case{filename['simulation_case']:03}_trade_space_in_{year}.png",
                            format="png", dpi=300, bbox_inches="tight")
                plt.show()

                _out = pd.DataFrame({'annual_cost': annual_cost,
                                    'ac_loss': ac_loss,
                                    'sf_sum': sf_sum,
                                    'fuel_cost': fuel_cost,
                                    'labour_cost': labour_cost,
                                    'sec_cost': sec_cost,
                                    'com_cost': com_cost,
                                    'sa_cost': (sa_cost/scenarios.ship_age).round(0).astype(int),
                                    'pl_cost': (pl_cost/scenarios.ship_age).round(0).astype(int),
                                    'ex_cost': (ex_cost/scenarios.ship_age).round(0).astype(int),
                                    'ro_cost': (ro_cost/scenarios.ship_age).round(0).astype(int),
                                    'rm_cost': (rm_cost/scenarios.ship_age).round(0).astype(int),
                                    'total_cost': total_cost})
                _out.to_csv(f"{out_path}/team_{filename['team']}/case{filename['simulation_case']:03}/"
                            f"case{filename['simulation_case']:03}_trade_space_in_{year}.csv")

        output = pd.DataFrame(zip(scenarios.data["Year"], selected_ship),
                              columns=['Year', 'Selected Ship type'])
        return output
