

class opt_client {


    constructor(
        host = "localhost",
        port = 5000
    ) {

        this.base_client = new base_client(host, port);
        this.l1_fields   = [ mdf.bid, mdf.bid_size, mdf.ask, mdf.ask_size, mdf.last, mdf.last_size ];

    } 


    async get_defs_ind(ul_sym, exp, lo_str, hi_str, right) {

        exp             = String(exp);
        let exp_month   = exp.slice(0, -2);
        let ul_conid    = null;
        let defs        = [];
        let res         = await this.base_client.search(ul_sym, true, "IND");

        if (!res)

            defs = null;
            
        else {
            
            ul_conid    = res[0].conid;
            res         = await this.base_client.secdef_info(ul_conid, "OPT", exp_month, "SMART", "0", right);

            if (!res)

                defs = null;
            
            else {

                for (let i = 0; i < res.length; i++) {

                    let opt_def = res[i];

                    if (
                            opt_def.maturityDate == exp &&
                            opt_def.strike >= lo_str    && 
                            opt_def.strike <= hi_str
                        )

                        defs.push(
                            {
                                conid:  opt_def.conid,
                                strike: opt_def.strike,
                                right:  opt_def.right,
                                class:  opt_def.tradingClass
                            }
                        );

                }

                defs.sort((a, b) => a.strike - b.strike);

            }
        
        }

        return {
            "ul_conid": ul_conid,
            "defs":     defs
        };

    }


    // US options only
    // leg_defs: asc sorted opt defs from get_*_defs
    // side: "+" for long, "-" for short
    // width: distance, in strikes, between legs

    get_butterfly_defs(leg_defs, side, width) {

        let     defs    = [];
        const   signs   = side == "-" ? [ "-", "", "-" ] : [ "", "-", "" ];

        for (let i = 0; i < leg_defs.length - 2 * width; i++) {

            let lo_id = leg_defs[i].conid;
            let md_id = leg_defs[i + width].conid;
            let hi_id = leg_defs[i + 2 * width].conid;

            defs.push(
                {
                    conid:  `28812380;;;${lo_id}/${signs[0]}1,${md_id}/${signs[1]}2,${hi_id}/${signs[2]}1`,
                    lo:     leg_defs[i].strike,
                    md:     leg_defs[i + width].strike,
                    hi:     leg_defs[i + 2 * width].strike
                }
            );

        }

        return defs;

    }


    async get_defs_stock(ul_sym, exp, lo_str, hi_str, right) {}
    async get_defs_fut(ul_sym, ul_month, exp, lo_str, hi_str, right) {}


    async set_handlers(msg_handler, err_handler, opn_handler, cls_handler) {

        this.base_client.set_ws_handlers(
            msg_handler = handler,
            err_handler = err_handler,
            opn_handler = opn_handler,
            cls_handler = cls_handler
        );

    }


    async sub_l1(conids) {

        for (let i = 0; i < conids.length; i++)

            await this.base_client.sub_market_data(conids[i], this.l1_fields);

    }


    async unsub_l1(conids) {

        for (let i = 0; i < conids; i++)

            this.base_client.unsub_market_data(conids[i]);

    }


}