
const   SERVER      = "localhost";
const   PORT        = 8080;
const   CONFIG      = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();
const   CLIENT      = new opt_client();
const   INDEX       = CONFIG["index"];
const   MODEL       = CONFIG["rows"];
const   STRAT       = null;
const   STRAT_DEFS  = null;
const   OFFSETS     = null;


function get_strategy(strat) {

    let     res         = null;
    const   ul_type     = CONFIG.ul_type;
    const   ul_sym      = CONFIG.ul_sym;
    const   ul_exps     = CONFIG.ul_exps;
    const   opt_exps    = CONFIG.opt_exps;
    const   lo_str      = CONFIG.lo_str;
    const   hi_str      = CONFIG.hi_str;
    const   side        = CONFIG.side;
    const   params      = CONFIG.params;
    const   strike_inc  = CONFIG.true_inc;

    if (strat == "calendar")

        res = CLIENT.get_calendar_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str);

    else if (strat == "call")

        res = CLIENT.get_call_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str);
    
    else if (strat == "call_vertical")

        res = CLIENT.get_call_vertical_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));

    else if (strat == "fly")

        res = CLIENT.get_fly_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));
    
    else if (strat == "iron_fly")

        res = CLIENT.get_iron_fly_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));

    else if (strat == "put")

        res = CLIENT.get_put_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str);
    
    else if (strat == "put_vertical")

        res = CLIENT.get_put_vertical_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));

    else if (strat == "straddle")

        res = CLIENT.get_straddle_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side);

    return res;

}


async function init() {

    STRAT_DEFS  = get_strategy(CONFIG["strat"]);
    OFFSETS     = Array.from(
                    { length: (CONFIG.offsets[1] - CONFIG.offsets[2]) / CONFIG.strike_inc },
                    (_, i) => CONFIG.offsets[0] + i * CONFIG.strike_inc
                );
    

}


init();