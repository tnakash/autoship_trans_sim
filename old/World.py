import pandas as pd

class Tech_list():
    def __ini__(self, tech_yml):
        self.tech_list = ['Berth', 'Navi', 'Moni'] # ideally from yml
        column = ['tech_name', 'tech_cost', 'integ_factor', 'TRL', 'Rexp', 'Mexp', 'Oexp', 'tech_cost_min', 'accident_ratio', 'accident_ratio_base', 'accident_ratio_ini']

        self.tech_cost = [0] * len(self.tech_list)
        self.tech_cost_min = [0] * len(self.tech_list)

        self.integ_factor_ini = [0] * len(self.tech_list)
        self.rd_need_TRL = [0] * len(self.tech_list)
        self.ope_max = [0] * len(self.tech_list)
        self.manu_max = [0] * len(self.tech_list)

        self.integ_factor = [0] * len(self.tech_list)
        self.TRL = [0] * len(self.tech_list) #  May change to TECH
        self.Rexp = [0] * len(self.tech_list)
        self.Mexp = [0] * len(self.tech_list)
        self.Oexp = [0] * len(self.tech_list)
        self.accident_ratio_ini = [0] * len(self.tech_list)
        self.accident_ratio_base = [0] * len(self.tech_list)
        self.accident_ratio = [0] * len(self.tech_list)

        for i in range(len(self.tech_list)):
            s = self.tech_list[i]
            self.tech_cost_min[i] = tech_yml[s]['min_cost']
            
            self.integ_factor_ini[i] = tech_yml['Others']['tech_integ_factor'] # sごとに決めることも可能
            self.rd_need_TRL[i] = tech_yml['Others']['rd_need_TRL']
            self.ope_max[i] = tech_yml['Others']['ope_max']
            self.manu_max[i] = tech_yml['Others']['manu_max']
            
            self.integ_factor[i] = self.integ_factor_ini[i]
            self.TRL[i] = tech_yml[s]['TRL_ini']
            self.Rexp[i] = tech_yml[s]['R&D_exp']
            self.Mexp[i] = tech_yml[s]['Man_exp']
            self.Oexp[i] = tech_yml[s]['Ope_exp']
            self.tech_cost[i] = self.tech_cost_min[i] * (10 - self.TRL[i])
            self.accident_ratio_ini[i] = tech_yml[s]['accident']
            self.accident_ratio_base[i] = self.accident_ratio_ini[i]
            self.accident_ratio[i] = self.accident_ratio_base[i]

        self.acc_reduction_full = tech_yml['Others']['acc_reduction_full']
        self.ope_TRL_factor = tech_yml['Others']['ope_TRL_factor']
        self.ope_safety_b = tech_yml['Others']['ope_safety_b']
        self.randd_base = tech_yml['Others']['randd_base']
        self.rd_TRL_factor = tech_yml['Others']['rd_TRL_factor']
        
        self.trl_reduction = [0] * len(tech_yml['Others']['trl_reduction'])
        list = tech_yml['Others']['trl_reduction']
        for j in range(len(self.trl_reduction)):
            self.trl_reduction[j] = tech_yml['Others']['trl_reduction'][list[j]] # We'll see...
                
        self.tech_df = pd.DataFrame(zip(self.tech_list, self.tech_cost, self.integ_factor, self.TRL, self.Rexp, self.Mexp, self.Oexp,
                                   self.tech_cost_min, self.accident_ratio, self.accident_ratio_base, self.accident_ratio_ini),
                               columns = column)

    def calculate_tech(self, ship_fleet, ship_age):
        ship_working = ship_fleet[-ship_age:]
        
        # Rewrite afterwards ...
        berth_list = ['config1', 'config5', 'config6', 'config7', 'config10', 'config11']
        navi1_list = ['config2', 'config5', 'config8', 'config10']
        navi2_list = ['config3', 'config6', 'config9', 'config11']
        moni_list = ['config4', 'config7', 'config8', 'config9', 'config10', 'config11']

        for i in berth_list:
            self.Oexp[0] += ship_working[i].sum()
            self.Mexp[0] += ship_working.iloc[-1][i]
        for i in navi1_list:
            self.Oexp[1] += ship_working[i].sum() * 0.5
            self.Mexp[1] += ship_working.iloc[-1][i] * 0.5
        for i in navi2_list:
            self.Oexp[1] += ship_working[i].sum()
            self.Mexp[1] += ship_working.iloc[-1][i]
        for i in moni_list:
            self.Oexp[2] += ship_working[i].sum() 
            self.Mexp[2] += ship_working.iloc[-1][i]
            
        for i in range(len(self.Oexp)):
            self.Oexp[i] = self.ope_max[i] if self.Oexp[i] > self.ope_max[i] else self.Oexp[i]
            self.Mexp[i] = self.manu_max[i] if self.Mexp[i] > self.manu_max[i] else self.Mexp[i]

    def calculate_TRL_cost(self):
        TRL_need = [0] * 3
        
        for i in range(len(self.tech_list)):
            TRL_need[i] = self.rd_need_TRL # * self.TRL[i]
            if (self.Oexp[i] * self.ope_TRL_factor + self.Rexp[i] * self.rd_TRL_factor) - TRL_need[i] > 0 and self.TRL[i] < 9:
                self.TRL[i] += 1
                self.accident_ratio_base[i] -= self.acc_reduction_full * self.trl_reduction(self.TRL[i])
                self.Rexp[i] = self.Rexp[i] - self.rd_need_TRL[i] if self.Rexp[i] - self.rd_need_TRL[i] > 0 else 0

            self.Rexp[i] += self.randd_base # Base investment (TBD)    
            self.tech_cost[i] = (10 - self.TRL[i]) * self.tech_cost_min[i]
            self.integ_factor[i] = 1+(self.integ_factor[i]-1)*(self.manu_max[i]-self.Mexp[i])/self.manu_max[i] if self.manu_max[i] > self.Mexp[i] else 1
            self.accident_ratio[i] = self.accident_ratio_base[i] * (self.Oexp[i]+1) ** (-self.ope_safety_b)

    def reset_fromdf(self, df):
        # change unconstant parameters only
        self.tech_cost = df['tech_cost'].to_list()
        self.integ_factor = df['integ_factor'].to_list()
        self.TRL = df['TRL'].to_list()
        self.Rexp = df['Rexp'].to_list()
        self.Mexp = df['Mexp'].to_list()
        self.Oexp = df['Oexp'].to_list()
        self.accident_ratio = df['self.accident_ratio'].to_list()
        self.accident_ratio_base = df['self.accident_ratio_base'].to_list()

class Ship_list():
    def __ini__(self, cost, ship_spec):
        self.navi_crew_factor = cost['Others']['navi_crew_factor']
        self.moni_crew_factor = cost['Others']['moni_crew_factor']
        self.cook_crew_factor = cost['Others']['cook_crew_factor']
        self.mainte_amount = cost['Others']['mainte_amount']
        self.capex_material_ratio = cost['Others']['capex_material_ratio']
        self.accom_reduce_navi = cost['Others']['accom_reduce_navi']
        self.accom_reduce_moni = cost['Others']['accom_reduce_moni']
        
        self.num_crew_navi = cost['Others']['num_crew_navi']
        self.num_crew_moni = cost['Others']['num_crew_moni']
        self.num_crew_cook = cost['Others']['num_crew_cook']
        self.num_crew_all = self.num_crew_navi + self.num_crew_moni + self.num_crew_cook
        
        self.berth_pilot_save = cost['Others']['berth_pilot_save']
        self.integ_a = cost['Others']['integ_a']
        self.integ_b = cost['Others']['integ_b']
        
        self.config = [''] * len(ship_spec)
        self.Berth = [0] * len(ship_spec) #  May change to TECH
        self.Navi = [0] * len(ship_spec)
        self.Moni = [0] * len(ship_spec)

        self.num_navi = [0] * len(ship_spec)       
        self.num_engi = [0] * len(ship_spec)
        self.num_cook = [0] * len(ship_spec)
            
        self.crew_cost = [0] * len(ship_spec)
        self.store_cost = [0] * len(ship_spec)
        self.maintenance_cost = [0] * len(ship_spec)
        self.insurance_cost = [0] * len(ship_spec)
        self.general_cost = [0] * len(ship_spec)
        self.dock_cost = [0] * len(ship_spec)

        self.material_cost = [0] * len(ship_spec)
        self.integrate_cost = [0] * len(ship_spec)
        self.add_eq_cost = [0] * len(ship_spec)

        self.port_call = [0] * len(ship_spec)
        self.fuel_cost_ME = [0] * len(ship_spec)
        self.fuel_cost_AE = [0] * len(ship_spec)
        
        self.SCC_Capex = [0] * len(ship_spec)
        self.SCC_Opex = [0] * len(ship_spec)
        self.SCC_Personal = [0] * len(ship_spec)
        self.Mnt_in_port = [0] * len(ship_spec)
        
        self.subsidy = [0] * len(ship_spec)

        self.Capex = [0] * len(ship_spec)
        self.Opex = [0] * len(ship_spec)
        self.Voyex = [0] * len(ship_spec)
        self.AddCost = [0] * len(ship_spec)

        self.acc_ratio_berth = [0] * len(ship_spec)
        self.acc_ratio_navi = [0] * len(ship_spec)
        self.acc_ratio_moni = [0] * len(ship_spec)

        for i in range(len(ship_spec)):
            self.config[i] = 'Config'+str(i)
            self.Berth[i] = ship_spec[self.config[i]]['Berth'] #  May change to TECH
            self.Navi[i] = ship_spec[self.config[i]]['Navi']
            self.Moni[i] = ship_spec[self.config[i]]['Moni']
            
            self.num_navi[i] = 0 if self.Navi == 2 else self.num_crew_navi * 0.5 if self.Navi == 1 else self.num_crew_navi
            self.num_engi[i] = 0 if self.Moni == 1 else self.num_crew_moni
            self.num_cook[i] = 0 if self.Navi == 2 and self.Moni == 1 else self.num_crew_cook
            
            self.crew_cost[i] = cost['OPEX']['crew_cost'] # May change based on the number
            self.store_cost[i] = cost['OPEX']['store_cost']
            self.maintenance_cost[i] = cost['OPEX']['store_cost']
            self.insurance_cost[i] = cost['OPEX']['store_cost']
            self.general_cost[i] = cost['OPEX']['store_cost']
            self.dock_cost[i] = cost['OPEX']['store_cost']
            self.port_call[i] = cost['VOYEX']['port_call']
            self.fuel_cost_ME[i] = cost['VOYEX']['fuel_cost_ME']
            self.fuel_cost_AE[i] = cost['VOYEX']['fuel_cost_AE']
            self.material_cost[i] = cost['CAPEX']['material_cost']
            
            self.SCC_Capex[i] = 0
            self.SCC_Opex[i] = 0
            self.SCC_Personal[i] = 0
            self.Mnt_in_port[i] = 0

        
    def calculate_cost(self, ship_spec, cost, year, tech):

        tech_list = ['Berth', 'Navi', 'Moni']
        crew_list = ['NaviCrew', 'EngiCrew', 'Cook']
        cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
        opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_cost', 'dock_cost']
        capex_list = ['material_cost', 'integrate_cost', 'add_eq_cost']
        voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
        addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
        accident_list = ['accident_berth', 'accident_navi', 'accident_moni']

        column = ['year', 'config'] + tech_list + crew_list + opex_list + capex_list + voyex_list + addcost_list + ['subsidy'] + cost_list + accident_list

        self.years = [year] * len(ship_spec)        
        for i in range(len(ship_spec)):
            self.config[i] = 'Config'+str(i)
            self.Berth[i] = ship_spec[self.config[i]]['Berth'] #  May change to TECH
            self.Navi[i] = ship_spec[self.config[i]]['Navi']
            self.Moni[i] = ship_spec[self.config[i]]['Moni']
            
            self.integrate_cost[i] = cost['CAPEX']['integrate_cost']*(1 + self.Berth[i] * (tech.integ_factor[0]-1)
                                                                      + self.Navi[i] * (tech.integ_factor[1]-1)
                                                                      + self.Moni[i] * (tech.integ_factor[2]-1))
            self.add_eq_cost[i] = tech.tech_cost[0] * self.Berth[i] + tech.tech_cost[1] * self.Navi[i] + tech.tech_cost[2] * self.Moni[i]
            
            # Rewrite afterwards... too dirty ...
            self.acc_ratio_berth[i] = tech.accident_ratio_ini[0]
            self.acc_ratio_navi[i] = tech.accident_ratio_ini[1]
            self.acc_ratio_moni[i] = tech.accident_ratio_ini[2]
            
            if self.Berth[i] == 1:
                self.port_call[i] -= self.berth_pilot_save * tech.trl_reduction(tech.TRL[0])
                self.acc_ratio_berth[i] = tech.accident_ratio[0]

            if self.Navi[i] == 1:
                TRL_semiauto = tech.TRL[1]+tech.TRLgap_semi if tech.TRL[1]+tech.TRLgap_semi < 9 else 9
                self.crew_cost[i] -= cost['OPEX']['crew_cost'] * self.navi_crew_factor * 0.5 * tech.trl_reduction(TRL_semiauto)
                self.maintenance_cost[i] -= self.mainte_amount * self.num_crew_navi/self.num_crew_all * 0.5 * tech.trl_reduction(TRL_semiauto)
                self.material_cost[i] -= cost['CAPEX']['material_cost'] * self.accom_reduce_navi * 0.5 * tech.trl_reduction(TRL_semiauto)
                self.integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * self.accom_reduce_navi * 0.5 * tech.trl_reduction(TRL_semiauto)
                self.SCC_Capex[i] += cost['AddCost']['SCC_Capex']*0.5
                self.SCC_Opex[i] += cost['AddCost']['SCC_Opex']*0.5
                self.SCC_Personal[i] += cost['AddCost']['SCC_Personal']*0.5
                self.acc_ratio_navi[i] = (tech.accident_ratio_base[1]+tech.accident_ratio[1]) * 0.5  # Need to Change
            elif self.Navi[i] == 2:
                self.crew_cost[i] -= cost['OPEX']['crew_cost'] * self.navi_crew_factor * tech.trl_reduction(tech.TRL[1])
                self.maintenance_cost[i] -= self.mainte_amount * self.num_crew_navi/self.num_crew_all * tech.trl_reduction(tech.TRL[1])
                self.material_cost[i] -= cost['CAPEX']['material_cost'] * self.accom_reduce_navi * tech.trl_reduction(tech.TRL[1])
                self.integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * self.accom_reduce_navi * tech.trl_reduction(tech.TRL[1])
                self.SCC_Capex[i] += cost['AddCost']['SCC_Capex']
                self.SCC_Opex[i] += cost['AddCost']['SCC_Opex']
                self.SCC_Personal[i] += cost['AddCost']['SCC_Personal']
                self.acc_ratio_navi[i] = tech.accident_ratio[1]
            
            if self.Moni[i] == 1:
                self.crew_cost[i] -= cost['OPEX']['crew_cost'] * self.moni_crew_factor
                self.maintenance_cost[i] -= self.mainte_amount * self.num_crew_moni/self.num_crew_all * tech.trl_reduction(tech.TRL[2])
                self.material_cost[i] -= cost['CAPEX']['material_cost'] * self.accom_reduce_moni * tech.trl_reduction(tech.TRL[2])
                self.integrate_cost[i] -= cost['CAPEX']['integrate_cost'] * self.accom_reduce_moni * tech.trl_reduction(tech.TRL[2])
                self.Mnt_in_port[i] += cost['AddCost']['Mnt_in_port']
                self.SCC_Capex[i] += cost['AddCost']['SCC_Capex']
                self.SCC_Opex[i] += cost['AddCost']['SCC_Opex']
                self.SCC_Personal[i] += cost['AddCost']['SCC_Personal']
                self.acc_ratio_moni[i] = tech.accident_ratio[2]
            
            # No cook if fully unmanned
            if self.Navi[i] == 2 and self.Moni[i] == 1: # Do not consider Berth
                self.crew_cost[i] -= cost['OPEX']['crew_cost'] * self.cook_crew_factor
        
            self.Opex[i] = self.crew_cost[i] + self.store_cost[i] + self.maintenance_cost[i] + self.insurance_cost[i] + self.general_cost[i] + self.dock_cost[i] 
            self.Capex[i] = self.material_cost[i] + self.integrate_cost[i] + self.add_eq_cost[i]
            self.Voyex[i] = self.port_call[i] + self.fuel_cost_ME[i] + self.fuel_cost_AE[i] 
            self.AddCost[i] = self.SCC_Capex[i] + self.SCC_Opex[i] + self.SCC_Personal[i] + self.Mnt_in_port[i]
        
        self.spec = pd.DataFrame(zip(self.years, self.config, self.Berth, self.Navi, self.Moni, self.num_navi, self.num_engi, self.num_cook, 
                                self.crew_cost, self.store_cost, self.maintenance_cost, self.insurance_cost, self.general_cost, self.dock_cost, 
                                self.material_cost, self.integrate_cost, self.add_eq_cost,
                                self.port_call, self.fuel_cost_ME, self.fuel_cost_AE, 
                                self.SCC_Capex, self.SCC_Opex, self.SCC_Personal, self.Mnt_in_port, self.subsidy,
                                self.Opex, self.Capex, self.Voyex, self.AddCost,
                                self.acc_ratio_berth, self.acc_ratio_navi, self.acc_ratio_moni), columns = column)