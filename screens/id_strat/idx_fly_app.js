

const   SERVER      = "localhost";
const   PORT        = 8080;
const   FLY_IDS     = {};
let     FLY_STRIKES = null;
const   L1_DATA     = {};
let     MODEL_INC   = null;
let     MODEL_VALS  = null;
let     OFFSET_BASE = null;
let     MODEL_DATA  = null;
let     TIME_IDX    = null;
let     UL_CONID    = null;
let     UL_LAST     = null;


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

            if (msg.conidEx && FLY_IDS[msg.conidEx]) {

                let i = FLY_IDS[msg.conidEx];

                if (msg[mdf.ask])   L1_DATA[mdf.ask][i]     = msg[mdf.ask];
                if (msg[mdf.bid])   L1_DATA[mdf.bid][i]     = msg[mdf.bid];
                if (msg[mdf.last])  L1_DATA[mdf.last][i]    = msg[mdf.ask];

            } else if (msg.conid && msg.conid == UL_CONID)

                if (msg[mdf.last]) UL_LAST = msg[mdf.last];
        
        }

    };

    client.set_ws_handlers(msg_handler = handler);

}


function update_model_vals() {

    if (!UL_LAST) 

        // not ready

        return;

    for (let i = 0; i < FLY_IDS.length; i++) {

        let strike  = FLY_STRIKES[i];
        let offset  = round(strike - UL_LAST, MODEL_INC);
        let j       = offset + OFFSET_BASE;

        MODEL_VALS[FLY_IDS[i]] = MODEL_DATA[TIME_IDX][j];

    }

}


async function update_view() {}


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

        FLY_IDS[conids[i].conid] = i;

    L1_DATA[mdf.bid]    = new Float32Array(conids.length);
    L1_DATA[mdf.ask]    = new Float32Array(conids.length);
    L1_DATA[mdf.last]   = new Float32Array(conids.length);

    FLY_STRIKES = fly_defs.map((def) => { def.strike });
    MODEL_VALS  = new Float32Array(conids.length);
    UL_CONID    = ul_conid;

    set_ws_handlers(client);

    client.sub_l1([ ul_conid ]);
    client.sub_l1(conids);
    
    // setInterval(update_view, 10);

}


init();