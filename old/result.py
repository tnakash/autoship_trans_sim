import pandas as pd

def initiate_result(demand,spec,cost,select,ship_age):
    result = pd.DataFrame(demand.Year)
    for s in list(set(spec.ship_type[select])):
        result[s] = 0

    # Add conventional ship
    conv_ship = len(spec)-1
    result[spec.ship_type[conv_ship]] = 0

    # Calculate number of ships
    result[spec.ship_type[conv_ship]][0] = demand.NumofShip[0] # Initial num of ship
    for i in range(len(cost.Year)):
        for s in list(set(spec.ship_type[select])):
            result.at[i,s] = result.at[i-1,s] if i >= 1 else 0
        result[spec.ship_type[select[i]]][i] += demand.Newbuilding[i]
        if i-ship_age > 0:
            result[spec.ship_type[select[i-ship_age-1]]][i] -= demand.Newbuilding[i-ship_age-1]
        if i >= 1 and i <= ship_age:
            result[spec.ship_type[conv_ship]][i] = result[spec.ship_type[conv_ship]][i-1] - demand.Scrap[i]
            
    return result, conv_ship

def selected_ship_label(spec,select,conv_ship):
    labels = list(set(spec.ship_type[select]))
    labels.append(spec.ship_type[conv_ship])
    labels = sorted(labels, reverse=True)
    return labels

def result_addrow(result):
    result['LabourCost'] = 0
    result['OpeCost'] = 0
    result['FuelCost'] = 0
    result['OnboardAsset'] = 0
    result['ShoreAsset'] = 0
    result['LossDamage'] = 0
    result['Seafarer'] = 0
    result['ShoreOperator'] = 0
    result['LossDamagePerVessel'] = 0

# Calculate Other Parameters
def calculate_result(result,spec,cost,demand,ship_age,labels1):
    for i in range(len(cost.Year)):
        a = [0] * 8
        for s in labels1:
            new = list(result_calc(s, spec, cost, i, result.at[i,s], ship_age))
            a = [x + y for (x, y) in zip(a, new)]
        
        result.LabourCost[i], result.OpeCost[i], result.FuelCost[i], result.OnboardAsset[i], result.ShoreAsset[i], result.LossDamage[i], result.Seafarer[i], result.ShoreOperator[i] = a

    result.LossDamagePerVessel = [a/b for (a,b) in zip(result.LossDamage, demand.NumofShip)]

def result_calc(s, spec, cost, year, num, ship_age):
    i = spec.index[spec.ship_type == s].tolist()[0]
    LabourCost = (spec.num_sf[i] * cost.Seafarer[year] + spec.num_so[i] * cost.ShoreOperator[year]) * num
    OpeCost = (spec.sec_cost[i] * cost.CS[year] + spec.com_cost[i] * cost.Comm[year]) * num
    FuelCost = spec.foc[i] * cost.Fuel[year] * num
    OnboardAsset = (spec.sa_cost[i] * cost.Situ[year] + spec.pl_cost[i] * cost.Plan[year] + spec.ex_cost[i] * cost.Exec[year])/ship_age * num
    ShoreAsset = (spec.ro_cost[i] * cost.RemOpe[year] + spec.rm_cost[i] * cost.RemMon[year])/ship_age * num 
    LossDamage = (spec.acc_ratio[i] * cost.ExpLoss[year]) * num
    Seafarer = spec.num_sf[i] * num
    ShoreOperator = spec.num_so[i] * num
    
    return LabourCost, OpeCost, FuelCost, OnboardAsset, ShoreAsset, LossDamage, Seafarer, ShoreOperator