const { base_client, mdf }  = require("./ibkr/base_client");
const { format }            = require("date-fns");
const fs                    = require("node:fs");;
const CONFIG                = JSON.parse(process.argv[2]);
const CLIENT                = new base_client(host = CONFIG.host)
const DATA                  = { ts: [] };


// node main.js '{ "conids": [ 568550526, 637533542 ], "tickers": [ "ES", "EMD" ], "interval": 1000, "host": "localhost" }'


function ws_handler(evt) {

    if (!evt.data) return;
    
    let msg = JSON.parse(evt.data);

    if (msg.topic.includes('smd')) {

        console.log(JSON.stringify(msg, null, 2));

    }

}


async function init() {

    await CLIENT.set_ws_handlers(msg_handler = ws_handler);

    for (let conid of CONFIG.conids) {

        DATA[conid] = [];

        CLIENT.sub_market_data(conid, [ mdf.bid, mdf.ask ]);

    }

}


async function write_csv() {

    //fs.writeFile();

}


setInterval(write_csv, CONFIG.interval)

init();