def select_ship(spec, cost, year, ship_age, economy, environment, safety, labour):
    labour_cost = spec.num_sf * cost.Seafarer[year] \
                + spec.num_so * cost.ShoreOperator[year]
    fuel_cost   = spec.foc * cost.Fuel[year]
    com_sec_cost= spec.sec_cost * cost.CS[year] \
                + spec.com_cost * cost.Comm[year]
    opex_sum    = labour_cost + fuel_cost + com_sec_cost
    capex_sum   = spec.sa_cost * cost.Situ[year] \
                + spec.pl_cost * cost.Plan[year] \
                + spec.ex_cost * cost.Exec[year] \
                + spec.ro_cost * cost.RemOpe[year] \
                + spec.rm_cost * cost.RemMon[year]
    ac_loss     = spec.acc_ratio * cost.ExpLoss[year]
    annual_cost = opex_sum + capex_sum/ship_age + ac_loss
    sf_sum      = spec.num_sf + spec.num_so

    select_parameter = annual_cost * economy \
                     + fuel_cost * environment \
                     + ac_loss * safety \
                     + labour_cost * labour #要正規化 
    select      = select_parameter.idxmin()   
    # seafarerの増減率をながらかにするようなファクター → TBD

    return select, annual_cost, opex_sum, capex_sum, ac_loss, sf_sum, fuel_cost