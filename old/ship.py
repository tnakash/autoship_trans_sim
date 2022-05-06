import pandas as pd

class Ship():
    def __init__(self, i, ship_spec):
        self.config = 'Config'+str(i)
        self.Berth = ship_spec[self.config]['Berth'] #  May change to TECH
        self.Navi = ship_spec[self.config]['Navi']
        self.Moni = ship_spec[self.config]['Moni']

    def get_cost(self, year, cost): # , tech
        self.year = year
        
        self.cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
        self.opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_costs', 'dock_cost']
        self.capex_list = ['material_cost', 'integrate_cost']
        self.voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
        self.addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']

        self.num_navi = 0 if self.Navi == 2 else 2 if self.Navi == 1 else 4       
        self.num_engi = 0 if self.Moni == 1 else 14
        self.num_cook = 0 if self.Navi == 2 and self.Moni == 1 else 2
        
        self.crew_cost = cost['OPEX']['crew_cost'] # May change based on the number
        self.store_cost = cost['OPEX']['store_cost']
        self.maintenance_cost = cost['OPEX']['store_cost']
        self.insurance_cost = cost['OPEX']['store_cost']
        self.general_cost = cost['OPEX']['store_cost']
        self.dock_cost = cost['OPEX']['store_cost']

        self.material_cost = cost['CAPEX']['material_cost']
        self.integrate_cost = cost['CAPEX']['integrate_cost']

        self.port_call = cost['VOYEX']['port_call']
        self.fuel_cost_ME = cost['VOYEX']['fuel_cost_ME']
        self.fuel_cost_AE = cost['VOYEX']['fuel_cost_AE']
    
        self.SCC_Capex = 0
        self.SCC_Opex = 0
        self.SCC_Personal = 0
        self.Mnt_in_port = 0
        
        if self.Navi == 1:
            self.SCC_Capex = cost['AddCost']['SCC_Capex']*0.5
            self.SCC_Opecx = cost['AddCost']['SCC_Opex']*0.5
            self.SCC_Personal = cost['AddCost']['SCC_Personal']*0.5
        elif self.Navi == 2:
            self.SCC_Capex = cost['AddCost']['SCC_Capex']
            self.SCC_Opex = cost['AddCost']['SCC_Opex']
            self.SCC_Personal = cost['AddCost']['SCC_Personal']            
        
        if self.Moni == 1:            
            self.Mnt_in_port = cost['AddCost']['Mnt_in_port']
        
        # cost_alllist = opex_list + capex_list + voyex_list + addcost_list
        # df_cost = pd.DataFrame(zip('crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_costs', 'dock_cost', 'material_cost', 'integrate_cost', 'port_call', 'fuel_cost_ME', 'fuel_cost_AE', 'SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port'), columns = cost_alllist)
        # return df_cost
        
    #     # Set cost time series by yaml
    # def get_cost_df(Year, cost, ship_spec):
    #     cost_list = ['OPEX', 'CAPEX', 'VOYEX', 'AddCost']
    #     opex_list = ['crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_costs', 'dock_cost']

    #     crew_cost = cost['OPEX']['crew_cost']
    #     store_cost = cost['OPEX']['store_cost']
    #     maintenance_cost = cost['OPEX']['store_cost']
    #     insurance_cost = cost['OPEX']['store_cost']
    #     general_cost = cost['OPEX']['store_cost']
    #     dock_cost = cost['OPEX']['store_cost']

    #     capex_list = ['material_cost', 'integrate_cost']
    #     material_cost = cost['CAPEX']['material_cost']
    #     integrate_cost = cost['CAPEX']['integrate_cost']

    #     voyex_list = ['port_call', 'fuel_cost_ME', 'fuel_cost_AE']
    #     port_call = cost['VOYEX']['port_call']
    #     fuel_cost_ME = cost['VOYEX']['fuel_cost_ME']
    #     fuel_cost_AE = cost['VOYEX']['fuel_cost_AE']

    #     addcost_list = ['SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port']
    #     SCC_Capex = cost['AddCost']['SCC_Capex']
    #     SCC_Opex = cost['AddCost']['SCC_Opex']
    #     SCC_Personal = cost['AddCost']['SCC_Personal']
    #     Mnt_in_port = cost['AddCost']['Mnt_in_port']
            
    #     sim_years = len(Year)
    #     # = [0] * sim_years   
    #     # for i in range (sim_years):
    #     #     ExpLoss[i] = int(ExpLoss[i-1] * loss_growth) if i>0 else loss_initial
    #     #     CS[i] = int(CS[i-1] * cs_growth) if i>0 else cs_initial
    #     #     Comm[i] = int(Comm[i-1] * com_growth) if i>0 else com_initial
    #     #     Situ[i] = int(Situ[i-1] * sa_growth) if i>0 else sa_initial
    #     #     Plan[i] = int(Plan[i-1] * pl_growth) if i>0 else pl_initial
    #     #     Exec[i] = int(Exec[i-1] * ex_growth) if i>0 else ex_initial
    #     #     RemOpe[i] = int(RemOpe[i-1] * ro_growth) if i>0 else ro_initial
    #     #     RemMon[i] = int(RemMon[i-1] * rm_growth) if i>0 else rm_initial
    #     #     Fuel[i] = int(Fuel[i-1] * fc_growth) * random.gauss(1,0.1) if i>0 else fc_initial

    #     # df_cost = pd.DataFrame(zip(Year, Seafarer, ShoreOperator, ExpLoss, CS, Comm, Situ, Plan, Exec, RemOpe, RemMon,Fuel), columns = column)
    #     cost_alllist = opex_list + capex_list + voyex_list + addcost_list
    #     df_cost = pd.DataFrame(zip('crew_cost', 'store_cost', 'maintenance_cost', 'insurance_cost', 'general_costs', 'dock_cost', 'material_cost', 'integrate_cost', 'port_call', 'fuel_cost_ME', 'fuel_cost_AE', 'SCC_Capex', 'SCC_Opex', 'SCC_Personal', 'Mnt_in_port'), columns = cost_alllist)
            
    #     return df_cost

    #     # Set spec of each ship by yaml
    # def get_spec(spec='spec_1'):
    #     check = True
    #     # folder_pass = 'yml/spec/' 
    #     folder_pass = homedir + 'yml/spec/' # Google Colab用に変更
    #     while check:
    #         try:
    #             with open(folder_pass + spec + ".yml") as yml:
    #                 spec = yaml.load(yml,Loader = yaml.SafeLoader)
    #             check = False
    #         except:
    #             print(FILE_ERROR_MESSAGE)

    #     options = len(spec['SituationAwareness']) * len(spec['Control']) * len(spec['Control']) * len(spec['Remote'])
    #     column = ['ship_type', 'Control', 'Planning', 'SituationAwareness', 'Remote', 'sec_cost', 'com_cost', 'acc_ratio', 'sa_cost', 'pl_cost', 'ex_cost', 'ro_cost', 'rm_cost', 'num_sf', 'num_so', 'foc']

    #     ship_type = [''] * options
    #     Control = [''] * options
    #     Planning = [''] * options
    #     SituationAwareness = [''] * options
    #     Remote = [''] * options
    #     sec_cost = [0] * options
    #     com_cost = [0] * options
    #     acc_ratio = [0] * options
    #     sa_cost = [0] * options
    #     pl_cost = [0] * options
    #     ex_cost = [0] * options
    #     ro_cost = [0] * options
    #     rm_cost = [0] * options
    #     num_sf = [0] * options
    #     num_so = [0] * options
    #     foc = [0] * options

    #     CPSR = list(itertools.product(spec['Control'], spec['Planning'], spec['SituationAwareness'],spec['Remote']))
    #     Control, Planning, SituationAwareness, Remote = [r[0] for r in CPSR], [r[1] for r in CPSR], [r[2] for r in CPSR], [r[3] for r in CPSR]
    
        # for i in range(options):
        #     ship_type[i] = 'ship_' + str(i+1) 
        #     sec_cost[i] = spec['Control'][Control[i]]['sec_cost']+spec['Planning'][Planning[i]]['sec_cost']+spec['SituationAwareness'][SituationAwareness[i]]['sec_cost']+spec['Remote'][Remote[i]]['sec_cost']-4
        #     com_cost[i] = spec['Control'][Control[i]]['com_cost']+spec['Planning'][Planning[i]]['com_cost']+spec['SituationAwareness'][SituationAwareness[i]]['com_cost']+spec['Remote'][Remote[i]]['com_cost']-4
        #     acc_ratio[i] = spec['Control'][Control[i]]['acc_ratio']*spec['Planning'][Planning[i]]['acc_ratio']*spec['SituationAwareness'][SituationAwareness[i]]['acc_ratio']
        #     sa_cost[i] = spec['SituationAwareness'][SituationAwareness[i]]['sa_cost']
        #     pl_cost[i] = spec['Planning'][Planning[i]]['pl_cost']
        #     ex_cost[i] = spec['Control'][Control[i]]['ex_cost']
        #     ro_cost[i] = spec['Remote'][Remote[i]]['ro_cost']
        #     rm_cost[i] = spec['Remote'][Remote[i]]['rm_cost']
        #     num_sf_tmp = spec['Control'][Control[i]]['num_sf']+spec['Planning'][Planning[i]]['num_sf']+spec['SituationAwareness'][SituationAwareness[i]]['num_sf']
        #     num_so[i] = int(num_sf_tmp*spec['Remote'][Remote[i]]['num_so_ratio'])
        #     num_sf[i] = num_sf_tmp - num_so[i]
        #     foc[i] = (1 - (8 - num_sf[i])/200) if num_sf[i] >0 else 0.9 # Assume max seafarer = 8

        # spec = pd.DataFrame(zip(ship_type, Control, Planning, SituationAwareness, Remote, sec_cost, com_cost, acc_ratio, sa_cost, pl_cost, ex_cost, ro_cost, rm_cost, num_sf, num_so, foc), columns = column)
        # return spec