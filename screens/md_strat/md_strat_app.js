
const   SERVER      = "localhost";
const   PORT        = 8080;
const   CONFIG      = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();
const   CLIENT      = new opt_client();
const   INDEX       = CONFIG["index"];
const   MODEL       = CONFIG["rows"];
const   STRAT       = null;
const   STRAT_DEFS  = null;
const   OFFSETS     = null;

let Y_BID           = null;
let Y_ASK           = null;
let Y_LAST          = null;
let Y_MODEL         = null;
let X_MODEL         = null;
let X_STRAT         = null;
let X_IDX           = null;

let UL_CONID       = null;
let UL_LAST        = null;
let UL_LBL         = null;

let IDX_L_BTN       = null;
let IDX_R_BTN       = null;
let IDX_TXT         = null;
let IDX_LBL         = null;
let IDX_IT          = 0;

let     CHART_DIV   = null;
const   TRACES      = [ null, null, null, null ];

const INTERVAL      = 100;


async function quote_handler(evt) {

    if (evt.data) {

        let msg = JSON.parse(await evt.data.text());

        if (msg.conidEx && X_IDX[msg.conidEx]) {

            let i = X_IDX[msg.conidEx];

            if (msg[mdf.ask])   Y_ASK[i]    = msg[mdf.ask];
            if (msg[mdf.bid])   Y_BID[i]    = msg[mdf.bid];
            if (msg[mdf.last])  Y_LAST[i]   = msg[mdf.last];

        } else if (msg.conid && msg.conid == UL_CONID) {

            if (msg[mdf.last]) {

                const last = msg[mdf.last];

                UL_LAST = typeof last === "string" && last[0] == "C" ? parseFloat(last.substring(1)) : parseFloat(last);  

            }

        }

    }
    
};


async function get_strategy(strat) {

    let     res         = null;
    const   ul_type     = CONFIG.ul_type;
    const   ul_sym      = CONFIG.ul_sym;
    const   ul_exps     = CONFIG.ul_exps.map(exp => exp == "-" ? null : exp);
    const   opt_exps    = CONFIG.opt_exps;
    const   lo_str      = CONFIG.lo_str;
    const   hi_str      = CONFIG.hi_str;
    const   side        = CONFIG.side;
    const   params      = CONFIG.params;
    const   strike_inc  = CONFIG.true_inc;

    if (strat == "calendar")

        res = await CLIENT.get_calendar_defs(ul_type, ul_sym, ul_exps, opt_exps, lo_str, hi_str, params[0] ? "C" : "P");

    else if (strat == "call")

        res = await CLIENT.get_call_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str);
    
    else if (strat == "call_vertical")

        res = await CLIENT.get_call_vertical_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));

    else if (strat == "fly")

        res = await CLIENT.get_fly_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));
    
    else if (strat == "iron_fly")

        res = await CLIENT.get_iron_fly_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));

    else if (strat == "put")

        res = await CLIENT.get_put_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str);
    
    else if (strat == "put_vertical")

        res = await CLIENT.get_put_vertical_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side, width = parseInt(params[0] / strike_inc));

    else if (strat == "straddle")

        res = await CLIENT.get_straddle_defs(ul_type, ul_sym, ul_exps[0], opt_exps[0], lo_str, hi_str, side);

    return res;

}


async function init() {

    OFFSETS = Array.from(
        { length: (CONFIG.offsets[1] - CONFIG.offsets[2]) / CONFIG.strike_inc },
        (_, i) => CONFIG.offsets[0] + i * CONFIG.strike_inc
    );
    
    const res   = await get_strategy(CONFIG["strat"]);
    UL_CONID    = res["ul_conid"];
    STRAT_DEFS  = res["defs"];

    Y_BID   = new Float32Array(STRAT_DEFS.length);
    Y_ASK   = new Float32Array(STRAT_DEFS.length);
    Y_LAST  = new Float32Array(STRAT_DEFS.length);
    Y_MODEL = MODEL[IDX_IT];
    X_MODEL = new Float32Array(OFFSETS.length);
    X_STRAT = new Float32Array(STRAT_DEFS.length);
    X_IDX   = {};

    for (let i = 0; i < STRAT_DEFS.length; i++) {

        X_IDX[STRAT_DEFS[i].conid]  = STRAT_DEFS[i].repr;
        X_STRAT[i]                  = STRAT_DEFS[i].repr;

    }

    


        

}


init();