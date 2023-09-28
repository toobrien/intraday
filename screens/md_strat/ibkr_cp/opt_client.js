

class opt_client {


    constructor(
        host = "localhost",
        port = 5000
    ) {

        this.base_client = new base_client(host, port);
        this.l1_fields   = [ mdf.bid, mdf.bid_size, mdf.ask, mdf.ask_size, mdf.last, mdf.last_size ];

    } 


    async get_opt_defs(ul_conid, exp, exchange, lo_str, hi_str, right) {

        exp = String(exp);

        let   exp_month     = exp.slice(0, -2);
        let   opt_defs      = null;
        let   res           = await this.base_client.secdef_info(ul_conid, "OPT", exp_month, exchange, "0", right);
            
        if (res) {

            opt_defs = [];

            for (let i = 0; i < res.length; i++) {

                let opt_def = res[i];

                if (
                    opt_def.maturityDate    == exp      &&
                    opt_def.strike          >= lo_str   &&
                    opt_def.strike          <= hi_str
                )

                    opt_defs.push(
                        {
                            conid:  opt_def.conid,
                            strike: opt_def.strike,
                            right:  opt_def.right,
                            class:  opt_def.tradingClass
                        }
                    );

            }

            opt_defs.sort((a, b) => a.strike - b.strike);

        }

        return opt_defs;

    }


    async get_defs(
        type,           // "FUT", "IND", or "STK"
        ul_sym,         // underlying symbol, e.g. "ZC" or "SPX"
        ul_exp = null,  // futures only; integer: YYYYMMDD
        opt_exp,        // integer: YYYYMMDD
        lo_str,         // lowest strike in range
        hi_str,         // highest strike in range
        right           // "C" or "P"
    ) {

        let res         = null;
        let ul_conid    = null;

        if (type == "FUT") {

            const futs = await this.base_client.futures(ul_sym);

            if (futs) {
                
                const fut = futs[ul_sym].find(o => o.expirationDate == ul_exp);

                if (fut)

                    ul_conid = fut["conid"];

            }

        } else {

            // type == "IND" or "STK"

            const uls = await this.base_client.search(ul_sym, true, type);

            if (uls)

                // assumes first search result is a match... probably refactor

                ul_conid = uls[0].conid

        }
        
        if (ul_conid) {

            const opt_defs = await this.get_opt_defs(ul_conid, opt_exp, "SMART", lo_str, hi_str, right);

            if (opt_defs)

                res = {
                    "ul_conid": ul_conid,
                    "defs":     defs
                };

        }

        return res

    }

    async get_call_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side);
    async get_call_vertical_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side, params);
    async get_iron_fly_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side, params);

    // US options only
    // leg_defs: asc sorted opt defs from get_*_defs
    // side: "+" for long, "-" for short
    // width: distance, in strikes, between legs

    async get_fly_defs(
        ul_type,
        ul_sym,
        ul_exps,
        opt_exps,
        lo_str,
        hi_str,
        side,
        params
    ) {

        const   leg_defs    = await this.get_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, "C");
        const   width       = params[0];
        let     defs        = [];
        const   signs       = side == "-" ? [ "-", "", "-" ] : [ "", "-", "" ];

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

    
    async get_put_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side);
    async get_call_vertical_defs(ul_type, ul_syms, ul_exps, opt_exp, lo_str, hi_str, side, parmas);
    async get_put_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side);
    async get_put_vertical_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side, params);
    async get_straddle_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side);
    async get_calendar_defs(ul_type, ul_sym, ul_expss, opt_expss, lo_str, hi_str, side);


    async set_ws_handlers(
        msg_handler = null,
        err_handler = null, 
        opn_handler = null, 
        cls_handler = null
    ) {

        await this.base_client.set_ws_handlers(
            msg_handler = msg_handler,
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