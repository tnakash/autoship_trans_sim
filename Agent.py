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
        # rewrite afterwards...
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
            # Return Subsidy
            policymaker.sub_used -= policymaker.sub_RandD

        return tech


class ShipOwner:
    def __init__(self, economy=1.0, safety=1.0, current_fleet=None, num_newbuilding=None, estimated_loss=10000000):
        self.economy = economy
        self.safety = safety
        self.fleet = current_fleet
        self.num_newbuiding = num_newbuilding
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

        labour_cost, fuel_cost, capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum                
        select_parameter = annual_cost * self.economy + accident_sum * self.safety * self.accident_loss - spec['subsidy']

        # Consider TRL regulation
        for i in berth_list:
            select_parameter[i] += 99999999 if tech.TRL[0] < TRLreg else 0
        for i in navi1_list:
            select_parameter[i] += 99999999 if tech.TRL[1] + 3 < TRLreg else 0
        for i in navi2_list:
            select_parameter[i] += 99999999 if tech.TRL[1] < TRLreg else 0
        for i in moni_list:
            select_parameter[i] += 99999999 if tech.TRL[2] < TRLreg else 0

        select = select_parameter.idxmin()
        return select

    def purchase_ship(self, select, year):
        self.fleet.loc[len(self.fleet.year)] = 0
        self.fleet.at[len(self.fleet.year)-1, 'year'] = self.fleet.at[len(self.fleet.year)-2, 'year'] + 1
        self.fleet.at[len(self.fleet.year)-1, 'config'+str(select)] = self.num_newbuiding['ship'][year]

    def purchase_ship_with_adoption(self, spec, select, tech, year, TRLreg, PolicyMaker):
        # Rewrite afterwards ... 
        berth_list = [1, 5, 6, 7, 10, 11]
        navi1_list = [2, 5, 8, 10]
        navi2_list = [3, 6, 9, 11]
        moni_list = [4, 7, 8, 9, 10, 11]
        
        # ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        labour_cost, fuel_cost, capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum = self.calculate_assumption(spec)
        annual_cost = opex_sum + capex_sum + voyex_sum + addcost_sum                
        select_parameter = annual_cost * self.economy + accident_sum * self.safety * self.accident_loss - spec['subsidy']
        
        # Consider TRL regulation
        for i in berth_list:
            select_parameter[i] += 99999999 if tech.TRL[0] < TRLreg else 0
        for i in navi1_list:
            select_parameter[i] += 99999999 if tech.TRL[1] + 3 < TRLreg else 0
        for i in navi2_list:
            select_parameter[i] += 99999999 if tech.TRL[1] < TRLreg else 0
        for i in moni_list:
            select_parameter[i] += 99999999 if tech.TRL[2] < TRLreg else 0

        select = select_parameter.idxmin()

        if PolicyMaker.sub_select != select:
            PolicyMaker.sub_per_ship = select_parameter[PolicyMaker.sub_select] - select_parameter[select]
            num_subsidized_ship_possible = PolicyMaker.sub_Adoption // PolicyMaker.sub_per_ship
            num_subsidized_ship = self.num_newbuiding['ship'][year] if self.num_newbuiding['ship'][year]<num_subsidized_ship_possible else num_subsidized_ship_possible
            PolicyMaker.sub_used += num_subsidized_ship * PolicyMaker.sub_per_ship
        else:
            PolicyMaker.sub_per_ship = 0
            num_subsidized_ship = 0

        self.fleet.at[len(self.fleet.year)-1, 'config'+str(PolicyMaker.sub_select)] = num_subsidized_ship
        self.fleet.at[len(self.fleet.year)-1, 'config'+str(select)] = self.num_newbuiding['ship'][year] - num_subsidized_ship


def calculate_assumption(spec):
    # Can be re-categorized
    labour_cost = spec.crew_cost + spec.SCC_Personal
    fuel_cost   = spec.fuel_cost_ME + spec.fuel_cost_AE 
    capex_sum   = spec.material_cost + spec.integrate_cost + spec.add_eq_cost
    opex_sum    = spec.crew_cost + spec.store_cost + spec.maintenance_cost + spec.insurance_cost+ spec.general_cost + spec.dock_cost
    voyex_sum   = spec.port_call + spec.fuel_cost_ME + spec.fuel_cost_AE
    addcost_sum = spec.SCC_Capex + spec.SCC_Opex + spec.SCC_Personal + spec.Mnt_in_port
    accident_sum = spec.accident_berth + spec.accident_navi + spec.accident_moni

    return labour_cost, fuel_cost, capex_sum, opex_sum, voyex_sum, addcost_sum, accident_sum


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