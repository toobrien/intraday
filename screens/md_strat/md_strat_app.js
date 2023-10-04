
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

const   INTERVAL    = 100;


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


async function update() {

    // update model -- quotes updated in quote_handler()

    if (!UL_LAST)

        return;

    let rounded = Math.round(UL_LAST / CONFIG["model_inc"]) * UL_LAST;

    for (let i = 0; i < OFFSETS.length; i++)

        X_MODEL[i] = rounded + OFFESTS[i];
    
    Y_MODEL = MODEL[IDX_IT];

    // update view

    Plotly.update(
        "chart_div",
        {
            x: [ X_STRAT, X_STRAT, X_STRAT, X_MODEL ],
            y: [
                Y_BID,
                Y_ASK,
                Y_LAST,
                Y_MODEL
            ]
        },
        [ 0, 1, 2, 3 ]
    )

    // update label

    UL_LBL.innerHTML = `    ${UL_LAST}`;

}


async function init() {

    // model, strategy, quotes

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

    // view

    const view = document.getElementById("view");
    
    CHART_DIV       = document.createElement("div");
    CHART_DIV.id    = "chart_div";
    CHART_DIV.style = "height: 800px";

    view.appendChild(CHART_DIV);

    let trace_cfgs = [
        // X       Y        color      name
        [ X_STRAT, Y_BID,   "#0000FF", "bid"    ],
        [ X_STRAT, Y_ASK,   "#FF0000", "ask"    ],
        [ X_STRAT, Y_LAST,  "#cccccc", "last"   ],
        [ X_MODEL, Y_MODEL, "#D9027D", "model"  ]
    ]

    for (let i = 0; i < trace_cfgs.length; i++) {

        let cfg = trace_cfgs[i];

        TRACES[i] = {
            x:      cfg[0],
            y:      cfg[1],
            type:   "scatter",
            marker: { color: cfg[2] },
            mode:   "markers",
            name:   cfg[3]
        }

    }

    layout = {
        xaxis: {
            tickmode: "array",
            tickvals: X_STRAT
        }
    }

    Plotly.newPlot("chart_div", TRACES, layout);

    // controls

    L_BTN               = document.createElement("button");
    L_BTN.innerHTML     = "<";
    L_BTN.id            = "l_btn";
    L_BTN.onclick       = (evt) => {
                            IDX_IT              = Math.max(0, IDX_IT - 1);
                            IDX_LBL.innerHTML   = `    ${INDEX[IDX_IT]}`;
                        };

    R_BTN               = document.createElement("button");
    R_BTN.innerHTML     = "<";
    R_BTN.id            = "l_btn";
    R_BTN.onclick       = (evt) => {
                            IDX_IT              = Math.min(INDEX.length - 1, IDX_IT + 1);
                            IDX_LBL.innerHTML   = `    ${INDEX[IDX_IT]}`;
                        };
    
    IDX_LBL             = document.createElement("text");
    IDX_LBL.innerHTML   = `${INDEX[IDX_IT]}`;

    IDX_TXT             = document.createElement("input");
    IDX_TXT.id          = "idx_txt";
    IDX_TXT.type        = "text";
    IDX_TXT.length      = 30;
    IDX_TXT.value       = INDEX[0];                        

    IDX_TXT.addEventListener(
        "keydown",
        (evt) => {

            if (evt.key === "Enter") {

                let i = INDEX.indexOf(IDX_TXT.value);

                if (i != -1) {

                    IDX_IT              = i;
                    IDX_LBL.innerHTML   = INDEX[IDX_IT];

                }

            }

        }
    );

    view.appendChild(IDX_TXT);
    view.appendChild(L_BTN);
    view.appendChild(R_BTN);
    view.appendChild(IDX_LBL);
    view.appendChild(UL_LBL);

}


init();