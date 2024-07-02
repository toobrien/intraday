const { base_client, mdf }  = require("./ibkr/base_client");
const { format }            = require("date-fns");
const fs                    = require("node:fs");
const CONFIG                = JSON.parse(process.argv[2]);
const CLIENT                = new base_client(host = CONFIG.host)
let   TS                    = null;
const DATA                  = {};
const SYM_MAP               = {};


// node main.js '{ "conids": [ 568550526, 637533542 ], "symbols": [ "ES", "EMD" ], "interval": 1000, "host": "localhost" }'


function ws_handler(evt) {

    if (!evt.data) return;
    
    let msg = JSON.parse(evt.data);

    if (msg.topic.includes('smd+')) {

        console.log(JSON.stringify(msg, null, 2));

        let conid = msg.conid;

        if (conid in DATA) {

            let data = DATA[conid];

            msg[mdf.bid] ? data[mdf.bid] = msg[mdf.bid] : null;
            msg[mdf.ask] ? data[mdf.ask] = msg[mdf.ask] : null;

            data["mid"] = (data[mdf.bid] + data[mdf.ask]) / 2;

        }

    }

}


async function init() {

    await CLIENT.set_ws_handlers(msg_handler = ws_handler);

    for (let i = 0; i < CONFIG.conids.length; i++) {

        let conid               = CONFIG.conids[i];
        let sym                 = CONFIG.symbols[i];
        DATA[conid]             = {};
        DATA[conid][mdf.bid]    = null;
        DATA[conid][mdf.ask]    = null;
        DATA[conid]["mid"]      = null;
        SYM_MAP[conid]          = sym;

        CLIENT.sub_market_data(conid, [ mdf.bid, mdf.ask ]);

    }

}


async function write_csv() {

    //fs.writeFile();

}


setInterval(write_csv, CONFIG.interval)

init();