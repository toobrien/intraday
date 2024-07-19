const   ROOT            = "http://localhost:8081";
const   L1              = {};
const   DATE_FMT        = "yyyy-MM-dd'T'HH:mm:ss";
let     top_chart       = null;
let     bot_chart       = null;
let     CLIENT          = null;
let     TS              = null;
let     DEBUG           = null;
let     x_id            = null;
let     y_id            = null;
let     X               = null;
let     Y               = null;
let     residuals       = null;
let     debug           = null;


async function update_chart() {}


async function update_model() {

    let body = {
                x: L1[x_id]["mids"],
                y: L1[y_id]["mids"]
            };

    let res = await (await fetch(
                `${ROOT}/get_model`,
                {
                    method:     "POST",
                    headers:    { "Content-Type": "application/json" },
                    body:       JSON.stringify(body)
                }
            )).json();
        
    X           = res.x;
    Y           = res.y;
    residuals   = res.residuals;

}


function update_data() {

    let quotes = Object.values(L1);

    for (let quote of quotes)
    
        if (!quote[mdf.bid] || !quote[mdf.ask])

            return;

    for ( let quote of quotes)

        quote.mids.push(quote.mid);

    TS.push(dateFns.format(new Date(), DATE_FMT));

}


async function m_handler(evt) {

    if (!evt.data) return;
    
    let msg = JSON.parse(await evt.data.text());

    if (debug)

        console.log(JSON.stringify(msg, null, 2));

    if (msg.topic.includes('smd+')) {

        let conid = msg.conid;

        if (conid in L1) {

            let quote = L1[conid];

            msg[mdf.bid] ? quote[mdf.bid] = parseFloat(msg[mdf.bid]) : null;
            msg[mdf.ask] ? quote[mdf.ask] = parseFloat(msg[mdf.ask]) : null;

            quote["mid"] = (quote[mdf.bid] + quote[mdf.ask]) / 2;

        }

    }

}

function init_charts() {

    

}


async function init() {

    const config    = await (await fetch(`${ROOT}/get_config`)).json();
    debug           = config["debug"];
    TS              = config["ts"];
    x_sym           = config["x_sym"];
    x_id            = parseInt(config["x_id"]);
    let x           = config["x"];
    y_sym           = config["y_sym"];
    y_id            = parseInt(config["y_id"]);
    let y           = config["y"];

    for (let cfg of [ [ x_id, x_sym, x ], [ y_id, y_sym, y] ]) {

        let id          = cfg[0];
        let sym         = cfg[1]
        let mids        = cfg[2];
        L1[id]          = {};
        L1[id][sym]     = sym;
        L1[id][mdf.bid] = null;
        L1[id][mdf.ask] = null;
        L1[id]["mid"]   = null;
        L1[id]["mids"]  = mids;

    }

    CLIENT  = new base_client(config["host"]);

    await CLIENT.set_ws_handlers(msg_handler = m_handler);
    
    CLIENT.sub_market_data(x_id, [ mdf.bid, mdf.ask ]);
    CLIENT.sub_market_data(y_id, [ mdf.bid, mdf.ask ]);

    init_charts();

    setInterval(update_data,  config["quote_interval"]);
    setInterval(update_model, config["model_interval"]);

}

init();