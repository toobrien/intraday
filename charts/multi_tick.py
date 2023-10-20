from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.contract_settings  import  get_settings
from    util.parsers            import  tas_rec
from    util.plotting           import  get_title
from    util.aggregations       import  tick_series, vbp
from    util.rec_tools          import  get_tas, get_precision
from    util.sc_dt              import  ts_to_ds


# python charts/multi_tick.py HOZ23_FUT_CME:HOZ24_FUT_CME 2023-10-19


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    title                   = f"{'    '.join(contract_ids)}    {start} - {end}"
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    recs = [
        [ list(rec) for rec in recs[i] ]
        for i in range(len(recs))
    ]

    for i in range(len(recs)):

        series      = recs[i]
        contract_id = contract_ids[i]

        for j in range(len(series)):

            series[j].append(contract_id)

    recs = [
        rec
        for series in recs
        for rec in series
    ]

    prev_m1 = recs[0][tas_rec.price]

    recs = sorted(recs, key = lambda r: r[tas_rec.timestamp])

    agg_recs = []
    tick     = recs[0][tas_rec.qty]
    prev_rec = [ val for val in recs[0] ]
    prev_rec.append(tick)

    for next_rec in recs[1:]:

        if  next_rec[tas_rec.price] == prev_rec[tas_rec.price]  and \
            next_rec[tas_rec.side]  == prev_rec[tas_rec.side]    and \
            next_rec[-1]            == prev_rec[-2]:

            prev_rec[tas_rec.qty]   += next_rec[tas_rec.qty]
        
        else:

            agg_recs.append(prev_rec)

            prev_rec = [ val for val in next_rec ]
            
            prev_rec.append(tick)
            
        tick            += next_rec[tas_rec.qty]
        prev_rec[-1]    =  tick

    prev_rec[-1] = tick

    agg_recs.append(prev_rec)

    for rec in agg_recs:
    
        if rec[-2] == contract_ids[0]:

            prev_m1 = rec[tas_rec.price]

        else:

            rec.append(log(rec[tas_rec.price] / prev_m1))

    recs = [
        [ 
            rec
            for rec in agg_recs
            if contract_id in rec
        ]
        for contract_id in contract_ids
    ]

    pass