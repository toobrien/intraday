

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
            
            if (right == "P")

                opt_defs.reverse();

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


    // US options only
    // *_defs: asc sorted opt defs from get_*_defs
    // side: "+" for long, "-" for short
    // width: distance, in strikes, between legs


    async get_call_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str) {

        const   call_defs   = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "C");
        let     defs        = [];

        for (let i = 0; i < call_defs.length; i++) {

            defs.push(
                {
                    conid: call_defs[i].conid,
                    repr:  call_defs[i].strike
                }
            );

        }

        return defs;

    };


    async get_call_vertical_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, side, width) {

        const leg_defs  = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "C");
        const signs     = side == "-" ? [ "", "-" ] : [ "-", "" ];
        const defs      = [];

        for (let i = 0; i < leg_defs.length - width; i++) {

            let lo = leg_defs[i];
            let hi = leg_defs[i + width];

            defs.push(
                {
                    conid:  `28812380;;;${lo.conid}/${signs[0]}1,${hi.conid}/${signs[1]}1`,
                    lo_str: lo.strike,
                    hi_str: hi.strike,
                    repr:   lo.strike
                }
            );

        }

        return defs;

    };


    async get_iron_fly_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, side, width) {

        const call_leg_defs = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "C");
        const put_leg_defs  = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "P");
        const signs         = side == "-" ? [ "-", "", "", "-" ] : [ "", "-", "-", "" ];
        const defs          = [];

        for (let i = 0; i < call_leg_defs.length - 2 * width; i++) {

            let hi_c = call_leg_defs[i];
            let md_c = call_leg_defs[i + width];
            let md_p = put_leg_defs[i + width];
            let lo_p = put_leg_defs[ i + 2 * width];

            defs.push(
                {
                    conid:      `28812380;;;${hi_c.conid}/${signs[0]}1,${md_c.conid}/${signs[1]}1,${md_p.conid}/${signs[2]}1,${lo_p.conid}/${signs[3]}1`,
                    hi_c_str:   hi_c.strike,
                    md_c_str:   md_c.strike,
                    md_p_str:   md_p.strike,
                    lo_p_str:   lo_p.strike,
                    repr:       md_c.strike
                }
            );

        }

        return defs;

    };


    async get_fly_defs(
        ul_type,
        ul_sym,
        ul_exp,
        opt_exp,
        lo_str,
        hi_str,
        side,
        width
    ) {

        // assume call fly

        const leg_defs  = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "C");
        const signs     = side == "-" ? [ "-", "", "-" ] : [ "", "-", "" ];
        const defs      = [];

        for (let i = 0; i < leg_defs.length - 2 * width; i++) {

            let lo = leg_defs[i];
            let md = leg_defs[i + width];
            let hi = leg_defs[i + 2 * width];

            defs.push(
                {
                    conid:  `28812380;;;${lo.conid}/${signs[0]}1,${md.conid}/${signs[1]}2,${hi.conid}/${signs[2]}1`,
                    lo_str: lo.strike,
                    md_str: md.strike,
                    hi_str: hi.strike,
                    repr:   md.strike,
                }
            );

        }

        return defs;

    }

    
    async get_put_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str) {

        const put_defs  = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "P");
        const defs      = [];
        
        for (let i = 0; i < put_defs.length; i++) {

            defs.push(
                {
                    conid:  put_defs[i].conid,
                    repr:   put_defs[i].strike
                }
            );

        }

        return defs;

    };


    async get_put_vertical_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, side, width) {

        const leg_defs  = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "P");
        const signs     = side == "-" ? [ "-", "" ] : [ "", "-" ];
        const defs      = [];

        for (let i = 0; i < leg_defs.length - width; i++) {

            let lo = leg_defs[i];
            let hi = leg_defs[i + width];

            defs.push(
                {
                    conid:  `28812380;;;${lo.conid}/${signs[0]}1,${hi.conid}/${signs[1]}1`,
                    lo_str: lo.strike,
                    hi_str: hi.strike,
                    repr:   hi.strike
                }
            );

        }

        return defs;       

    };


    async get_straddle_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, side) {

        const call_leg_defs = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "C");
        const put_leg_defs  = await this.get_defs(ul_type, ul_sym, ul_exp, opt_exp, lo_str, hi_str, "P");
        const signs         = side == "-" ? [ "-", "-" ] : [ "", "" ];
        const defs          = [];
    
        for (let i = 0; i < call_leg_defs.length; i++) {

            let c = call_leg_defs[i];
            let p = put_leg_defs[i];

            defs.push(
                {
                    conid:  `28812380;;;${c.conid}/${signs[0]}1,${p.conid}/${signs[1]}1`,
                    c_str:  c.strike,
                    p_str:  p.strike,
                    repr:   c.strike
                }
            );

        }

        return defs;

    };


    async get_calendar_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, side) {

        // assume call calendar

        const leg_defs_0    = await this.get_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, "C");
        const leg_defs_1    = await this.get_defs(ul_type, ul_sym, ul_exps[1], opt_exps[1], lo_str, hi_str, "C");
        const signs         = side == "-" ? [ "", "-" ] : [ "-", "" ];
        const defs          = [];

        for (let i = 0; i < leg_defs_0.length; i++) {

            let c_0 = leg_defs_0[i];
            let c_1 = leg_defs_1[i];

            defs.push(
                {
                    conid:  `28812380;;;${c_0.conid}/${signs[0]}1,${c_1.conid}/${signs[1]}1`,
                    str:    c_0.strike,
                    repr:   c_0.strike
                }
            );

        }

        return defs;

    };


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