from json           import loads
from util.parsers   import bulk_parse_tas, parse_tas_header, tas_rec, transform_tas
from util.sc_dt     import ts_to_ds
from sys            import argv

# example usage:

# NG                            symbol
# 0.001                         price multiplier
# J23:12                        12 consecutive terms, starting at J23
# "2023-03-22 06:00:00.000000"  start ts
# "2023-03-22 07:00:00.000000"  end ts
# 1                             print tas records


SC_ROOT     = loads(open("./config.json").read())["sc_root"]
MONTHS      = [ "F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
FMT         = "%Y-%m-%d %H:%M:%S.%f"
FIELD_WIDTH = 10

def process_records(
    fd,
    contract_id,
    multiplier,
    precision,
    start,
    end,
    print_recs
):

    if print_recs:

        print(f"{contract_id}\n")

    _       = parse_tas_header(fd)
    recs    = bulk_parse_tas(fd, 0)
    recs    = transform_tas(recs, multiplier)

    start_price = None
    end_price   = None
    count       = 0
    at_bid      = 0
    at_ask      = 0

    for i in range(len(recs)):

        r   = recs[i]
        ds  = ts_to_ds(r[tas_rec.timestamp], FMT)

        if start <= ds < end:

            start_price = r[tas_rec.price] if not start_price else start_price
            price       = f"{r[tas_rec.price]: {FIELD_WIDTH}.{precision}f}"
            qty         = f"{r[tas_rec.qty]: {FIELD_WIDTH}d}"
            side        = None

            if r[tas_rec.side] == 0:

                at_bid  += 1
                side    =  "bid".rjust(FIELD_WIDTH)
            
            else:

                at_ask  += 1
                side    =  "ask".rjust(FIELD_WIDTH)

            count += 1

            if print_recs:

                print(ds, price, qty, side)

        elif ds >= end:

            end_price = recs[i - 1][tas_rec.price]

            break

    if print_recs:
    
        print("\n")

    return ( contract_id, start_price, end_price, count, at_bid, at_ask )



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
            fn          = f"{SC_ROOT}/Data/{contract_id}_FUT_CME.scid"

            with open(fn, "rb") as fd:

                results.append(
                    process_records(
                        fd,
                        contract_id,
                        multiplier,
                        precision, 
                        start,
                        end,
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