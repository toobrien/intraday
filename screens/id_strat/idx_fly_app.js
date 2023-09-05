

const   SERVER      = "localhost";
const   PORT        = 8080;
const   FLY_I       = {};
let     FLY_STRIKES = null;
const   L1_DATA     = {};
let     MODEL_INC   = null;
let     MODEL_VALS  = null;
let     OFFSET_BASE = null;
let     MODEL_DATA  = null;
let     TIME_I      = null;
let     TIME_IDX    = null;
let     UL_CONID    = null;
let     UL_LAST     = null;
const   INTERVAL    = 2000;


function round(val, increment) { return Math.round(val / increment) * increment; }


async function set_ws_handlers(client) {

    /*
        {
            "31": "4514.95",
            "6119": "q28",
            "6509": "Z",
            "server_id": "q28",
            "conidEx": "416904",
            "conid": 416904,
            "_updated": 1693723535040,
            "topic": "smd+416904"
        }
        {
            "_updated": 1693723590349,
            "topic": "smd+28812380;;;646629987/-1,646629993/2,646630013/-1"
        }
    */

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
                    UL_LAST     = typeof last === "string" ? parseFloat(last.substring(1)) : last;
                
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

    for (let i = 0; i < FLY_STRIKES.length; i++) {

        let model   = MODEL_DATA[TIME_I];
        let strike  = FLY_STRIKES[i];
        let offset  = round(strike - UL_LAST, MODEL_INC);
        let j       = offset - OFFSET_BASE;

        if (0 <= j && j < model.length)
        
            MODEL_VALS[i] = model[j];

    }

}


async function update_view() {}


async function update() {

    update_model_vals();
    update_view();

}

async function init_view() {}


async function init() {

    const config    = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();
    const client    = new opt_client();
    const opt_defs  = await client.get_defs_ind(config.ul_sym, config.expiry, config.lo_strike, config.hi_strike, "C");
    const ul_conid  = opt_defs.ul_conid; 
    const fly_defs  = client.get_butterfly_defs(opt_defs.defs, "-", 1);
    const conids    = fly_defs.map(def => def.conid);

    MODEL_INC       = config.increment;
    OFFSET_BASE     = config.offsets[0];
    MODEL_DATA      = config.rows;

    for (let i = 0; i < conids.length; i++)

        FLY_I[conids[i]] = i;

    L1_DATA[mdf.bid]    = new Float32Array(conids.length);
    L1_DATA[mdf.ask]    = new Float32Array(conids.length);
    L1_DATA[mdf.last]   = new Float32Array(conids.length);

    FLY_STRIKES = fly_defs.map((def) => { return def.md; });
    MODEL_VALS  = new Float32Array(conids.length);
    TIME_I      = 0;
    TIME_IDX    = Object.keys(MODEL_DATA);
    MODEL_DATA  = Object.values(MODEL_DATA);
    UL_CONID    = ul_conid;

    await set_ws_handlers(client);

    client.sub_l1([ ul_conid ]);
    client.sub_l1(conids);
    
    init_view();
    setInterval(update, INTERVAL);

}


init();