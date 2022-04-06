def investment(cost, year, delay, invest):
    if invest == 'Comm':
        cost.Comm[year+delay:] *= 0.8
    elif invest == 'Situ':
        cost.Situ[year+delay:] *= 0.8
    elif invest == 'Plan':
        cost.Plan[year+delay:] *= 0.8
    elif invest == 'Exec':
        cost.Exec[year+delay:] *= 0.8