

const   SERVER      = "localhost";
const   PORT        = 8080;

const   FLY_I       = {};
const   L1_DATA     = {};

let     FLY_STRIKES = null;
let     MODEL_DATA  = null;
let     MODEL_INC   = null;
let     MODEL_TXT   = null;
let     MODEL_X     = null;
let     MODEL_Y     = null;
let     OFFSETS     = null;
let     TIME_I      = null;
let     TIME_IDX    = null;
let     UL_CONID    = null;
let     UL_LAST     = null;

let     SLIDER      = null;
let     SLIDER_LBL  = null;
let     CHART_DIV   = null;
const   TRACES      = [ null, null, null, null ];
let     UL_LBL      = null;

const   INTERVAL    = 100;


function round(val, increment) { return Math.round(val / increment) * increment; }


async function set_ws_handlers(client) {

    let handler = async (evt) => {

        if (evt.data) {
            
            let msg = JSON.parse(await evt.data.text());

            if (msg.conidEx && FLY_I[msg.conidEx]) {

                let i = FLY_I[msg.conidEx];

                if (msg[mdf.ask])   L1_DATA[mdf.ask][i]     = msg[mdf.ask];
                if (msg[mdf.bid])   L1_DATA[mdf.bid][i]     = msg[mdf.bid];
                if (msg[mdf.last])  L1_DATA[mdf.last][i]    = msg[mdf.ask];

            } else if (msg.conid && msg.conid == UL_CONID) {

                if (msg[mdf.last]) {

                    const last  = msg[mdf.last];
                    UL_LAST     =   typeof last === "string" && last[0] == "C" ? 
                                    parseFloat(last.substring(1)) : parseFloat(last);
                
                }

            }
        
        }

    };

    await client.set_ws_handlers(msg_handler = handler);

}


function update_model_vals() {

    if (!UL_LAST) 

        // not ready

        return;

    const lo = FLY_STRIKES[0];
    const hi = FLY_STRIKES[FLY_STRIKES.length - 1];

    for (let i = 0; i < OFFSETS.length; i++) {

        let model   = MODEL_DATA[TIME_I];
        let offset  = OFFSETS[i];
        let x       = round(offset + UL_LAST, MODEL_INC);

        if (lo <= x && x < hi) {
        
            MODEL_X[i]      = x;
            MODEL_Y[i]      = -model[i];
            MODEL_TXT[i]    = offset;

        } else {

            MODEL_X[i]      = null;
            MODEL_Y[i]      = null;
            MODEL_TXT[i]    = null;
            
        }

    }

}


async function update_view() {

    Plotly.update(
        "chart_div",
        {
            x : [ null, null, null, MODEL_X ],
            y: [
                L1_DATA[mdf.bid],
                L1_DATA[mdf.ask],
                L1_DATA[mdf.last],
                MODEL_Y
            ],
            text: [ null, null, null, MODEL_TXT ]
        },
        [ 0, 1, 2, 3 ]
    );

    UL_LBL.innerHTML = UL_LAST;

}


async function update() {

    update_model_vals();
    update_view();

}

async function init_view(config) {

    const view = document.getElementById("view");

    // chart

    CHART_DIV       = document.createElement("div");
    CHART_DIV.id    = "chart_div";
    CHART_DIV.style = "height: 800px"; 

    TRACES[0] = {
        x:      FLY_STRIKES,
        y:      L1_DATA[mdf.bid],
        type:   "scatter",
        marker: { color: "#0000FF" },
        mode:   "markers",
        name:   "bid"
    };

    TRACES[1] = {
        x:      FLY_STRIKES,
        y:      L1_DATA[mdf.ask],
        type:   "scatter",
        marker: { color: "#FF0000" },
        mode:   "markers",
        name:   "ask"
    };

    TRACES[2] = {
        x:      FLY_STRIKES,
        y:      L1_DATA[mdf.last],
        type:   "scatter",
        marker: { color: "#cccccc" },
        mode:   "markers",
        name:   "last"
    };

    TRACES[3] = {
        x:      FLY_STRIKES,
        y:      MODEL_VALS,
        text:   MODEL_TXT,
        type:   "scatter",
        marker: { color: "#D9027D" },
        mode:   "markers",
        name:   "model"
    };

    layout = {
                xaxis: {         
                    tickmode: "array",
                    tickvals: FLY_STRIKES
                },
                yaxis: {
                    range: [ -config.width, 0 ]
                }
            };

    view.appendChild(CHART_DIV);

    Plotly.newPlot("chart_div", TRACES, layout);

    // ul

    UL_LBL = document.createElement("text");
    
    UL_LBL.innerHTML = UL_LAST;

    view.appendChild(UL_LBL);
    view.appendChild(document.createElement("br"));

    // slider

    SLIDER                  = document.createElement("input");
    SLIDER.id               = "slider";
    SLIDER.type             = "range";
    SLIDER.min              = 0;
    SLIDER.value            = 0;
    SLIDER.max              = TIME_IDX.length - 1;

    SLIDER_LBL              = document.createElement("text");
    SLIDER_LBL.innerHTML    = `${TIME_IDX[TIME_I]}`;

    const update_slider = (evt) => {

        TIME_I                  = parseInt(evt.target.value);
        SLIDER_LBL.innerHTML    = `${TIME_IDX[TIME_I]}`;

    };

    SLIDER.onchange = update_slider;

    view.appendChild(SLIDER_LBL);
    view.appendChild(SLIDER);

}


async function init() {

    const config    = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();
    const client    = new opt_client();
    const opt_defs  = await client.get_defs_ind(config.ul_sym, config.expiry, config.lo_strike, config.hi_strike, "C");
    const ul_conid  = opt_defs.ul_conid; 
    const fly_defs  = client.get_butterfly_defs(opt_defs.defs, "-", 1);
    const conids    = fly_defs.map(def => def.conid);

    MODEL_INC       = config.increment;
    OFFSETS         = config.offsets;
    MODEL_DATA      = config.rows;

    for (let i = 0; i < conids.length; i++)

        FLY_I[conids[i]] = i;

    L1_DATA[mdf.bid]    = new Float32Array(conids.length);
    L1_DATA[mdf.ask]    = new Float32Array(conids.length);
    L1_DATA[mdf.last]   = new Float32Array(conids.length);

    FLY_STRIKES = fly_defs.map((def) => { return def.md; });
    MODEL_X     = new Float32Array(OFFSETS.length);
    MODEL_Y     = new Float32Array(OFFSETS.length)
    MODEL_TXT   = new Float32Array(OFFSETS.length);
    TIME_I      = 0;
    TIME_IDX    = Object.keys(MODEL_DATA);
    MODEL_DATA  = Object.values(MODEL_DATA);
    UL_CONID    = ul_conid;

    await set_ws_handlers(client);

    client.sub_l1([ ul_conid ]);
    client.sub_l1(conids);
    
    init_view(config);
    setInterval(update, INTERVAL);

}


init();