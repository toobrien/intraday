from json           import loads
from util.parsers   import tas_rec
from util.tas_tools import get_tas
from sys            import argv

# example usage:

# NG                            symbol
# 0.001                         price multiplier
# J23:12                        12 consecutive terms, starting at J23
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


# example usage: python term_chg.py NG 0.001 J23:12 2023-03-27T00:00:00 2023-03-28T00:00:00 0


if __name__ == "__main__":

    symbol                  = argv[1]
    multiplier              = argv[2]
    precision               = len(multiplier.split(".")[1]) if "." in multiplier else len(multiplier)
    first_term, n_months    = argv[3].split(":")
    start                   = argv[4]
    end                     = argv[5]
    print_recs              = int(argv[6])

    multiplier  = float(multiplier)
    first_month = first_term[0]
    year        = int(first_term[1:])
    n_months    = int(n_months)
    
    results = []
    
    i = MONTHS.index(first_month)

    while n_months > 0:

        try:

            contract_id = f"{symbol}{MONTHS[i]}{year}"
            recs        = get_tas(f"{contract_id}_FUT_CME", FMT, multiplier, start, end)

            if recs:

                results.append(
                        process_records(
                            recs,
                            contract_id,
                            precision,
                            print_recs
                        )
                    )

            year    =  year if i != 11 else year + 1
            i       =  (i + 1) % 12

        except Exception as e:

            # print exception and keep going on file not found
            # (for non-serial contracts)

            print(e)

        n_months -= 1
    
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
        
            delta_pct = f"{delta / count: 0.2f}" 
        
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