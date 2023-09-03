

const   SERVER    = "localhost";
const   PORT      = 8080;
const   L1_DATA   = {};
let     REF_DATA  = null;


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

    let handler = null;

    client.set_ws_handlers(msg_handler = handler);

}


async function update_view() {}


async function init() {

    const config    = await (await fetch(`http://${SERVER}:${PORT}/config`)).json();
    const client    = new opt_client();
    const opt_defs  = await client.get_defs_ind(config.ul_sym, config.expiry, config.lo_strike, config.hi_strike, "C");
    const ul_conid  = opt_defs.ul_conid; 
    const fly_defs  = client.get_butterfly_defs(opt_defs.defs, "-", 1);
    const conids    = fly_defs.map(def => def.conid);
    REF_DATA        = config.rows;

    conids.push(ul_conid);

    // set_ws_handlers(client);

    client.sub_l1(conids);
    
    // setInterval(update_view, 10);

}


init();