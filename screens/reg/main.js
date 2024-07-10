const fs                    = require("node:fs");
const { format }            = require("date-fns");
const { base_client, mdf }  = require("./ibkr/base_client");
const CONFIG                = JSON.parse(fs.readFileSync("./config.json"));
const CLIENT                = new base_client(host = CONFIG.host);
const DATA                  = {};
const DATE_FMT              = "yyyy-MM-dd";
const TS_FMT                = `${DATE_FMT}'T'HH:mm:ss`;


// node ./screens/reg/main.js


function ws_handler(evt) {

    if (!evt.data) return;
    
    let msg = JSON.parse(evt.data);

    if (CONFIG.debug)

        console.log(JSON.stringify(msg, null, 2));

    if (msg.topic.includes('smd+')) {

        let conid = msg.conid;

        if (conid in DATA) {

            let data = DATA[conid];

            msg[mdf.bid] ? data[mdf.bid] = parseFloat(msg[mdf.bid]) : null;
            msg[mdf.ask] ? data[mdf.ask] = parseFloat(msg[mdf.ask]) : null;

            data["mid"] = (data[mdf.bid] + data[mdf.ask]) / 2;

        }

    }

}


async function init() {

    await CLIENT.set_ws_handlers(msg_handler = ws_handler);

    for (let conid of Object.keys(CONFIG.symbols)) {

        DATA[conid]             = {};
        DATA[conid][mdf.bid]    = null;
        DATA[conid][mdf.ask]    = null;
        DATA[conid]["mid"]      = null;

        CLIENT.sub_market_data(conid, [ mdf.bid, mdf.ask ]);

    }

    setInterval(write_csv, CONFIG.interval)

}


async function write_csv() {

    let conids  = Object.keys(CONFIG.symbols);
    let syms    = Object.values(CONFIG.symbols);
    let vals    = [];
    let date    = Date.now();
    let day     = format(date, DATE_FMT)
    let ts      = format(Date.now(), TS_FMT);
    let fn      = `./csvs/${day}.csv`;

    if (syms.length == 0)

        return;

    if (!fs.existsSync(fn)) {

        let header = `ts,${syms.join(",")}\n`;
        
        fs.writeFileSync(fn, header, 'utf8');

    }

    for (let conid of conids) {

        let data = DATA[conid];

        if (!data.mid)
            
            return;

        vals.push(data.mid);
    
    }

    let row = `${ts},${vals.join(",")}\n`;

    fs.appendFileSync(fn, row, "utf8");

}

init();
