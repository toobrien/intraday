from json                   import loads
from util.contract_settings import  get_settings
from util.parsers           import tas_rec
from util.rec_tools         import get_precision
from util.term_structure    import get_terms
from sys                    import argv

# usage: python term_chg_table.py NGM23 2023-03-27T00:00:00 2023-03-28T00:00:00 0

# NGJ23                         starting symbol
# 12                            12 consecutive terms, starting at J23
# "2023-03-22T06:00:00.000000"  start ts
# "2023-03-22T07:00:00.000000"  end ts
# 1                             print tas records


SC_ROOT     = loads(open("./config.json").read())["sc_root"]
MONTHS      = [ "F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
FMT         = "%Y-%m-%dT%H:%M:%S.%f"
FIELD_WIDTH = 10

def process_records(
    recs,
    contract_id,
    precision,
    print_recs
):

    if print_recs:

        print(f"{contract_id}\n")


    start_price = recs[0][tas_rec.price]
    end_price   = recs[-1][tas_rec.price]
    count       = 0
    at_bid      = 0
    at_ask      = 0

    for rec in recs:

        price       = f"{rec[tas_rec.price]: {FIELD_WIDTH}.{precision}f}"
        qty         = f"{rec[tas_rec.qty]: {FIELD_WIDTH}d}"
        side        = None

        if rec[tas_rec.side] == 0:

            at_bid  += 1
            side    =  "bid".rjust(FIELD_WIDTH)
        
        else:

            at_ask  += 1
            side    =  "ask".rjust(FIELD_WIDTH)

        count += 1

        if print_recs:

            print(rec[tas_rec.timestamp].ljust(20), price, qty, side)

    if print_recs:
    
        print("\n")

    return ( contract_id, start_price, end_price, count, at_bid, at_ask )


if __name__ == "__main__":

    init_symbol     = argv[1]
    multiplier, _   = get_settings(init_symbol)
    precision       = get_precision(float(multiplier))
    multiplier      = float(multiplier)
    n_months        = int(argv[2])
    start           = argv[3]
    end             = argv[4]
    print_recs      = int(argv[5])
    
    terms   = get_terms(
                init_symbol,
                multiplier,
                n_months,
                FMT,
                start,
                end
            )
            
    results = []

    for contract_id, recs in terms.items():

        results.append(
            process_records(
                recs,
                contract_id,
                precision,
                print_recs
            )
        )

    print(start, "\t", end, "\n")

    print(
        "contract_id".ljust(FIELD_WIDTH),
        "chg".ljust(FIELD_WIDTH),
        "chg %".ljust(FIELD_WIDTH),
        "count".ljust(FIELD_WIDTH),
        "at_bid".ljust(FIELD_WIDTH),
        "at_ask".ljust(FIELD_WIDTH),
        "delta".ljust(FIELD_WIDTH),
        "delta_pct"
        "\n"
    )

    for res in results:

        contract_id, start_price, end_price, count, at_bid, at_ask = res
        
        chg         = f"{end_price - start_price: 0.{precision}f}"
        chg_pct     = f"{((end_price / start_price - 1) * 100): 0.2f}%"
        delta       = -at_bid + at_ask
        delta_pct   = None

        try:
        
            delta_pct = f"{delta / count * 100: 0.2f}%" 
        
        except:

            # divide by zero

            pass

        print(
            contract_id.ljust(FIELD_WIDTH),
            chg.ljust(FIELD_WIDTH),
            chg_pct.ljust(FIELD_WIDTH),
            str(count).ljust(FIELD_WIDTH),
            str(at_bid).ljust(FIELD_WIDTH),
            str(at_ask).ljust(FIELD_WIDTH),
            str(delta).ljust(FIELD_WIDTH),
            delta_pct.ljust(FIELD_WIDTH)
        )